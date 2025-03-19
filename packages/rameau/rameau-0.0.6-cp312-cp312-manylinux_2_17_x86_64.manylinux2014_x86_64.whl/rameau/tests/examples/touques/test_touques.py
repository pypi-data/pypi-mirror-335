# Copyright 2025, BRGM
# 
# This file is part of Rameau.
# 
# Rameau is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# Rameau is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# Rameau. If not, see <https://www.gnu.org/licenses/>.
#
import rameau.core as rm
import numpy as np
import unittest
import datetime
import os

class TestToTomlTouques(unittest.TestCase):
    def setUp(self):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)
        self.model = rm.Model.from_toml("touques.toml")
    
    def test_to_toml(self):
        # Test for writing correctly regression parameters
        vals = [0.0, 0.0, 1.0]
        optis = [False, True, False]
        for iwat, wat in enumerate(self.model.tree.watersheds):
            wat.groundwater.base_level.value = vals[iwat]
            wat.groundwater.base_level.opti = optis[iwat]
        self.model.to_toml("tmp.toml")
        try:
            self.model.from_toml("tmp.toml")
        except RuntimeError as msg:
            self.fail(str(msg))
    
    def tearDown(self):
        if os.path.exists("tmp.toml"):
            os.remove("tmp.toml")
        os.chdir(os.path.dirname(__file__))

class TestOptimizationTouques(unittest.TestCase):
    def setUp(self):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)
        self.model = rm.Model.from_toml("touques.toml")

    def test_is_confluence(self):
        self.model.tree.watersheds[2].is_confluence = True
        sim = self.model.run_simulation()
        riverflow = sim.get_output()
        pump = self.model.get_input("riverpumping")
        data = riverflow.iloc[:, [0, 1]].sum(axis=1) + pump.iloc[:,2].values
        np.testing.assert_array_equal(data.values, riverflow.iloc[:, 2].values)
    
    def test_is_confluence_no_pumping(self):
        self.model.tree.watersheds[2].is_confluence = True
        for wat in self.model.tree.watersheds:
            wat.pumping.river.coefficient.value = 0.0
        sim = self.model.run_simulation()
        riverflow = sim.get_output()
        data = riverflow.iloc[:, [0, 1]].sum(axis=1)
        np.testing.assert_array_equal(data.values, riverflow.iloc[:, 2].values)

    def test_opti_strahler(self):
        sim = self.model.run_optimization(
            method="strahler",
            maxit=5,
            river_objective_function='nse'
        )
        scores = sim.get_opti_metrics()
        self.assertGreater(scores.loc['nse', :].mean(), 0.62)
    
    def test_opti_all(self):
        sim = self.model.run_optimization(
            method="all",
            maxit=25,
            river_objective_function='nse'
        )
        scores = sim.get_opti_metrics()
        self.assertGreater(scores.loc['nse', :].mean(), 0.62)

    def test_opti_is_confluence_all(self):
        self.model.tree.watersheds[2].is_confluence = True
        sim = self.model.run_optimization(
            method="all",
            maxit=25,
            river_objective_function='nse'
        )
        val1 = self.model.tree.watersheds[2].transfer_reservoir.runsee.value
        val2 = sim.tree.watersheds[2].transfer_reservoir.runsee.value
        self.assertEqual(val1, val2)

    def test_opti_selected_watersheds(self):
        for l in [[1, 2], [3]]:
            sim = self.model.run_optimization(
                method="all",
                maxit=5,
                river_objective_function='nse',
                selected_watersheds=l
            )
            self.model.tree = sim.tree
        scores = sim.get_opti_metrics()
        self.assertGreater(scores.loc['nse', :].mean(), 0.62)
    
    def tearDown(self):
        os.chdir(os.path.dirname(__file__))

class TestAreaTouques(unittest.TestCase):
    def setUp(self):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)
    
    def test_area_corr(self):
        model = rm.Model.from_toml("touques.toml")
        sim = model.run_simulation()
        area_corr = [w.river.area_corr for w in sim.tree.watersheds]
        area_cum = [w.river.area_cum for w in sim.tree.watersheds]
        self.assertEqual(area_cum[0], area_corr[0])
        self.assertEqual(area_cum[1], area_corr[1])
        self.assertEqual(area_cum[2], np.sum(area_corr))

    def test_area_corr_modified(self):
        model = rm.Model.from_toml("touques.toml")
        model.tree.watersheds[1].correction.area.value = 0.5
        sim = model.run_simulation()
        area_corr = [w.river.area_corr for w in sim.tree.watersheds]
        area_cum = [w.river.area_cum for w in sim.tree.watersheds]
        self.assertEqual(area_cum[0], area_corr[0])
        self.assertEqual(area_cum[1], area_corr[1])
        self.assertEqual(area_cum[2], np.sum(area_corr))

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))



class TestForecastTouques(unittest.TestCase):
    def setUp(self):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)
        self.model = rm.Model.from_toml("touques.toml")
    
    def test_halflife_same_init_value(self):
        edate = datetime.datetime(2000, 1, 1)
        sim_ref = self.model.run_simulation()
        riv_ref = sim_ref.get_output(header_type="id")
        sim = self.model.run_forecast(
            emission_date=edate,
            scope=datetime.timedelta(days=2),
            correction='halflife'
        )
        data = sim.get_forecast_output(variable='riverflow', header_type="id")
        obs = sim.get_input("riverobs", header_type="id")
        self.assertAlmostEqual(data.iloc[0, 0], obs.loc[edate, 1], places=2)
        self.assertEqual(data.iloc[0, 1], riv_ref.loc[edate, 2])

    def test_halflife_same_init_value_no_rain(self):
        edate = datetime.datetime(2000, 1, 1)
        sim_ref = self.model.run_simulation()
        riv_ref = sim_ref.get_output(header_type="id")
        sim = self.model.run_forecast(
            emission_date=edate,
            scope=datetime.timedelta(days=2),
            correction='halflife',
            norain=True
        )
        data = sim.get_forecast_output(variable='riverflow', header_type="id")
        obs = sim.get_input("riverobs", header_type="id")
        self.assertAlmostEqual(data.iloc[0, 0], obs.loc[edate, 1], places=2)
        self.assertEqual(data.iloc[0, 1], riv_ref.loc[edate, 2])

#    def test_kalman(self):
#        import datetime
#        import pylab as plt
#        sim = self.model.run_optimization(
#            method="all",
#            maxit=650,
#            river_objective_function='nse'
#        )
#        self.model.tree = sim.tree
#        # Run a forecast
#        for w in self.model.tree.watersheds:
#            w.forecast_correction.da_priority = 'watertable'
#            w.forecast_correction.river.kalman_date = datetime.datetime(2021, 1, 1)
#            w.forecast_correction.groundwater.kalman_date = datetime.datetime(2021, 1, 1)
#        edate = datetime.datetime(2021, 12, 31)
#        sim_for = self.model.run_forecast(
#            scope=datetime.timedelta(days=90),
#            emission_date=edate,
#            year_members=[2021],
#            #correction='enkf'
#        )
#        sim_for2 = self.model.run_forecast(
#            scope=datetime.timedelta(days=90),
#            emission_date=edate,
#            year_members=[2021],
#            correction='enkf'
#        )
#        riv_obs = self.model.get_input("groundwaterobs")
#        hist = sim_for2.get_output("watertable")
#
#        # Get forecast groundwater flow
#        fore = sim_for.get_forecast_output("watertable")
#        fore2 = sim_for2.get_forecast_output("watertable")
#
#        # Plot the spaghettis
#        s = datetime.datetime(2021, 11, 1)
#        e = hist.index[-1] + sim_for.forecast_settings.scope
#
#        fig, ax = plt.subplots(3, 1, figsize=(10, 8))
#        for i, obs in enumerate(hist.columns):
#            riv_obs.loc[s:e, obs].plot(ax=ax[i])
#            hist.loc[s:e, obs].plot(ax=ax[i])
#            fore.loc[s:e, (slice(None), slice(obs, obs, None))].plot(ax=ax[i], legend=False)
#            fore2.loc[s:e, (slice(None), slice(obs, obs, None))].plot(ax=ax[i], legend=False)
#            ax[i].grid()
#        fig.tight_layout()
#        plt.show()
#
    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
