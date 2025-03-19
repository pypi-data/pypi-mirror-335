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
import datetime
import unittest
import pandas as pd
import os
import rameau.core as rm

class TestOptimizationPerpignan(unittest.TestCase):
    def setUp(self):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)
        self.model = rm.Model.from_toml("perpignan.toml")
        self.sim = self.model.run_optimization()

    def test_opti_scores_watertable(self):
        scores = self.sim.get_opti_metrics("watertable", header_type='id')
        self.assertGreater(scores.loc["nse", 1], 0.92)
    
    def tearDown(self):
        os.chdir(os.path.dirname(__file__))

class TestForecastPerpignan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)
        cls.model = rm.Model.from_toml("perpignan.toml")
        sim = cls.model.run_optimization()
        cls.model.tree = sim.tree
        gw1 = cls.model.get_input("groundwaterpumping")
        gw1 = gw1.squeeze()
        gw2 = pd.Series(
            [1, 2],
            index = pd.date_range("2006-8-1", "2006-8-2")
        )
        gw1 = pd.concat([gw1, gw2], axis=0)
        gw1 = pd.DataFrame(gw1)
        cls.model.inputs.groundwaterpumping = rm.inputs.Input(
            data=gw1.values, dates=gw1.index, nodata=0.0
        )

    def test_forecast(self):
        sim = self.model.run_forecast(
            scope=datetime.timedelta(days=1),
            year_members=[1970],
            emission_date=datetime.datetime(1970, 8, 3),
        )
        self.assertAlmostEqual(sim.get_forecast_output("watertable").iloc[1, 0], 51.205, places=2)

    def test_forecast_pumping(self):
        sim = self.model.run_forecast(
            scope=datetime.timedelta(days=3),
            year_members=[1970],
            pumping_date=datetime.datetime(2002, 1, 1),
            emission_date=datetime.datetime(1970, 8, 3),
        )
        self.assertAlmostEqual(sim.get_forecast_output("watertable").iloc[1, 0], 51.215, places=2)
    
    @classmethod
    def tearDown(cls):
        os.chdir(os.path.dirname(__file__))