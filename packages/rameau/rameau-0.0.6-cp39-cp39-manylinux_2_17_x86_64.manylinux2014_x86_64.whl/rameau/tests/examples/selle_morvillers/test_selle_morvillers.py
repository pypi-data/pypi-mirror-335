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
import rameau as rm
from rameau.core.simulation import ForecastSimulation
import pandas as pd
import numpy as np
import unittest
import os
import datetime

class TestMultipleSimulationSelleMorvillers(unittest.TestCase):
    def setUp(self):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)

    def test_update_param(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        model.optimization_settings.maxit = 0
        model.simulation_settings.spinup_settings.cycles = 0
        model.tree.watersheds[0].river.concentration_time.value = 2
        sim = model.create_simulation()
        states = sim.get_states(1)
        istart = 5000
        iend = 5005
        sim.run(istart, iend)
        riv1 = sim.get_output()
        sim.tree.watersheds[0].river.concentration_time.value = 3
        sim.set_states(states, istart - 1)
        sim.run(istart, iend, update_param=True)
        riv2 = sim.get_output()
        np.testing.assert_array_equal(
            riv1.iloc[istart:iend-1].values,
            riv2.iloc[istart+1:iend].values
        )
    
    def test_run(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        model.optimization_settings.maxit = 0
        model.simulation_settings.spinup_settings.cycles = 0
        model.tree.watersheds[0].river.concentration_time.value = 2.5
        rainfall = model.get_input("rainfall")
        sim_ref = model.run_simulation()
        sim = model.create_simulation()
        sim.run(1, len(rainfall))
        riv = sim.get_output()
        riv_ref = sim_ref.get_output()
        pd.testing.assert_frame_equal(riv_ref, riv)
    
    def test_run_with_states(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        model.optimization_settings.maxit = 0
        model.simulation_settings.spinup_settings.cycles = 0
        model.tree.watersheds[0].river.concentration_time.value = 3.5
        rainfall = model.get_input("rainfall")
        sim_ref = model.run_simulation()
        sim = model.create_simulation()
        for i in range(1, len(rainfall) + 1):
            if i > 1:
                sim.set_states(states, i - 1)
            sim.run(i, i)
            states = sim.get_states(i)
        riv = sim.get_output()
        riv_ref = sim_ref.get_output()
        pd.testing.assert_frame_equal(riv_ref, riv)

    def test_get_states(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        model.tree.watersheds[0].river.concentration_time.value = 2.5
        rainfall = model.get_input("rainfall")
        sim = model.run_simulation()
        toto = sim.get_states(len(rainfall))
        self.assertEqual(
            sim.final_states.states[0].h_progressive,
            toto.states[0].h_progressive
        )

    def test_set_states(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        model.tree.watersheds[0].river.concentration_time.value = 2.5
        sim = model.create_simulation()
        states_ref = rm.states.StatesCollection(
                states=[
                    rm.states.States(
                        h_progressive=0.5,
                        q_local=[1, 2, 3]
                    )
                ],
            )
        sim.set_states(states_ref, 0)
        states = sim.get_states(1)
        self.assertEqual(
            states_ref.states[0].h_progressive,
            states.states[0].h_progressive,
        )
        self.assertListEqual(
            [2.0, 3.0, 0.0], states.states[0].q_local
        )

    def test_multiple_singlestep_simulation(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        model.optimization_settings.maxit = 0
        model.simulation_settings.spinup_settings.cycles = 0
        model.tree.watersheds[0].river.concentration_time.value = 2.5
        sim_ref = model.run_simulation()
        riv_ref = sim_ref.get_output()
        rainfall = model.get_input("rainfall")
        pet = model.get_input("pet")
        riv = []
        for date in rainfall.index[:365]:
            inputs = rm.inputs.InputCollection(
                rainfall=rainfall.loc[date, :].to_frame(),
                pet=pet.loc[date, :].to_frame(),
                dates=pd.date_range(date, date)
            )
            model.inputs = inputs
            sim = model.run_simulation()
            riv.append(sim.get_output())
            model.init_states = sim.final_states
        riv = pd.concat(riv, axis=0)
        pd.testing.assert_frame_equal(riv_ref.iloc[:365], riv)

    def test_multiple_simulation(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        model.optimization_settings.maxit = 0
        model.simulation_settings.spinup_settings.cycles = 0
        model.tree.watersheds[0].river.concentration_time.value = 2.5
        sim_ref = model.run_simulation()
        riv_ref = sim_ref.get_output()
        rainfall = sim_ref.get_input("rainfall")
        pet = model.get_input("pet")
        riv = []
        limit = 365
        for date in rainfall.index[:limit]:
            index = pd.date_range(date - pd.Timedelta(1, 'D'), date)
            r = pd.DataFrame(
                data=[0, rainfall.loc[date, :].values[0]],
                index=index
            )
            p = pd.DataFrame(
                data=[0, pet.loc[date, :].values[0]],
                index=index
            )
            inputs = rm.inputs.InputCollection(rainfall=r, pet=p)
            model.inputs = inputs
            model.simulation_settings.starting_date = date
            sim = model.run_simulation()
            riv.append(sim.get_output().loc[date, :].values[0])
            model.init_states = sim.final_states
        riv = pd.DataFrame(data=riv, index=rainfall.index[:limit])
        riv.columns = rainfall.columns
        pd.testing.assert_frame_equal(riv_ref.iloc[:limit], riv)

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))


class TestOptimizationSelleMorvillers(unittest.TestCase):
    def setUp(self):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)

    def test_opti_scores_watertable(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        sim = model.run_optimization()
        scores = sim.get_opti_metrics(variable='watertable')
        self.assertGreater(scores.loc['nse', "Selle à Plachy"], 0.9)

    def test_opti_scores_riverflow(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        sim = model.run_optimization()
        scores = sim.get_opti_metrics()
        self.assertGreater(scores.loc['nse', "Selle à Plachy"], 0.8)

    def test_storage_bounds(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        model.tree.watersheds[0].groundwater.storage.regression = False
        sim = model.run_optimization()
        scores = sim.get_opti_metrics("watertable")
        self.assertGreater(scores.loc['nse', "Selle à Plachy"], 0.9)
    
    def tearDown(self):
        os.chdir(os.path.dirname(__file__))

class TestSimulationSelleMorvillers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)
        cls.model = rm.Model.from_toml("selle_morvillers.toml")
        cls.sim = cls.model.run_simulation()

    def test_scores_riverflow(self):
        scores = self.sim.get_metrics(header_type="id")
        self.assertGreater(scores.loc['nse', 1], 0.5)

    def test_scores_watertable(self):
        scores = self.sim.get_metrics("watertable", header_type="id")
        self.assertLess(scores.loc['nse', 1], -0.3)
    
    def test_output_riverflow(self):
        data = self.sim.get_output("riverflow")
        self.assertIsInstance(data, pd.DataFrame)

    def test_output_watertable(self):
        data = self.sim.get_output('watertable')
        self.assertIsInstance(data, pd.DataFrame)
    
    def test_area_corr(self):
        r = self.sim.tree.watersheds[0].river
        self.assertEqual(r.area_corr, r.area.value)
        self.assertEqual(r.area_cum, r.area.value)

    @classmethod
    def tearDown(cls):
        os.chdir(os.path.dirname(__file__))
    
class TestAreaSelleMorvillers(unittest.TestCase):
    def setUp(self):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)
    
    def test_area_corr(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        sim = model.run_simulation()
        r = sim.tree.watersheds[0].river
        self.assertEqual(r.area_corr, r.area.value)
        self.assertEqual(r.area_cum, r.area.value)

    def test_area_corr_modified(self):
        model = rm.Model.from_toml("selle_morvillers.toml")
        model.tree.watersheds[0].correction.area.value = 0.5
        sim = model.run_simulation()
        r = sim.tree.watersheds[0].river
        self.assertEqual(r.area_corr, r.area.value * 0.5)
        self.assertEqual(r.area_cum, r.area.value * 0.5)

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))

class TestForecastSelleMorvillers(unittest.TestCase):
    def setUp(self):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)
        self.model = rm.Model.from_toml("selle_morvillers.toml")
        bas = self.model.tree.watersheds[0]
        bas.forecast_correction.river = rm.forecast.ForecastParameter(halflife=2)
        self.sim = self.model.run_forecast(
            scope=datetime.timedelta(days=90),
            norain=True,
            quantiles_output=True,
            correction='halflife'
        )

    def test_get_forecast_output_watertable(self):
        data = self.sim.get_forecast_output(variable='watertable')
        self.assertEqual(len(data.columns), 6)
        self.assertGreater(data.iloc[0, 0], 194)

    def test_get_output_watertable(self):
        data = self.sim.get_output(variable='watertable')
        self.assertEqual(data.mean().values, 178.249313)

    def test_halflife_same_init_value(self):
        edate = datetime.datetime(2000, 1, 1)
        sim = self.model.run_forecast(
            emission_date=edate,
            scope=datetime.timedelta(days=2),
            norain=True,
            quantiles_output=True,
            correction='halflife'
        )
        data = sim.get_forecast_output(variable='riverflow')
        obs = sim.get_input("riverobs", header_type="id")
        self.assertEqual(data.iloc[0, 0], obs.loc[edate, 1])

    def test_get_forecast_output_riverflow(self):
        data = self.sim.get_forecast_output()
        self.assertEqual(len(data.columns), 6)
        self.assertGreater(data.iloc[0, 0], 0.4)
    
    def test_same_forecast(self):
        sim1 = self.model.run_forecast(
            emission_date=datetime.datetime(2000, 1, 1),
            scope=datetime.timedelta(days=90),
            year_members=[2000]
        )
        data1 = sim1.get_forecast_output().xs(key=2000, level='member', axis=1)
        sim = self.model.run_simulation()
        data2 = sim.get_output().loc[data1.index, :]
        pd.testing.assert_frame_equal(data1, data2)
    
    def tearDown(self):
        os.chdir(os.path.dirname(__file__))

#class TestForecastKalmanSelleMorvillers(unittest.TestCase):
#    def setUp(self):
#        rep = os.path.join(os.path.dirname(__file__),
#            'data')
#        os.chdir(rep)
#        self.model = rm.Model.from_toml("selle_morvillers.toml")
#
#    def test_kalman_simulation(self):
#        #import pylab as plt
#        kalman_date = datetime.datetime(1998, 1, 1)
#        emit_date = datetime.datetime(1998, 8, 1)
#        scope = datetime.timedelta(days=180)
#        #end_date = emit_date + scope
#        bas = self.model.tree.watersheds[0]
#        bas.forecast_correction.da_priority = 'watertable'
#        #bas.forecast_correction.river = rm.forecast.ForecastParameter(
#        #    kalman_date=kalman_date
#        #)
#        bas.forecast_correction.groundwater = rm.forecast.ForecastParameter(
#            kalman_date=kalman_date
#        )
#        #sim1 = self.model.run_optimization()
#        #self.model.tree = sim1.tree
#        sim2 = self.model.run_forecast(
#            scope=scope,
#            year_members=[emit_date.year],
#            emission_date = emit_date,
#            correction='enkf'
#        )
#        self.assertIsInstance(sim2, ForecastSimulation)
#        #fig, ax = plt.subplots()
#        #obs = self.model.get_input("groundwaterobs").loc[kalman_date:end_date, :]
#        #res1 = sim1.get_output("watertable").loc[kalman_date:end_date, :]
#        #resk = sim2.get_output("watertable").loc[kalman_date:end_date, :]
#        #resk2 = sim2.get_forecast_output("watertable")
#        #print(resk)
#        #ax.plot(obs.index, obs.interpolate(), label="obs", ls='--')
#        #ax.plot(res1.index, res1, label='sim')
#        #ax.plot(resk.index, resk, label='kalman')
#        #ax.plot(resk2.index, resk2, label='kalman-forecast')
#        #ax.legend()
#        #ax.grid()
#        #plt.show()
#
#        #fig, ax = plt.subplots()
#        #obs = self.model.get_input("riverobs").loc[kalman_date:end_date, :]
#        #res1 = sim1.get_output().loc[kalman_date:end_date, :]
#        #resk = sim2.get_output().loc[kalman_date:end_date, :]
#        #resk2 = sim2.get_forecast_output()
#        #print(resk)
#        #ax.plot(obs.index, obs.interpolate(), label="obs", ls='--')
#        #ax.plot(res1.index, res1, label='sim')
#        #ax.plot(resk.index, resk, label='kalman')
#        #ax.plot(resk2.index, resk2, label='kalman-forecast')
#        #ax.legend()
#        #ax.grid()
#        #plt.show()
#
#    
#    def tearDown(self):
#        os.chdir(os.path.dirname(__file__))
#