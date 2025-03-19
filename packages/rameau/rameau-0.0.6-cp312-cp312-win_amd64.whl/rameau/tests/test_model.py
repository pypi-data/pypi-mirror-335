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
import unittest

import os
import shutil
import datetime
import tempfile

import numpy as np
import pandas as pd

from rameau.core.inputs import InputCollection
from rameau.core import (
    RiverParameters,
    Parameter,
    ThornthwaiteReservoir,
    TransferReservoir,
    Watershed,
    Tree,
    Model,
    ProgressiveReservoir,
    FilePaths
)
from rameau.core.simulation import (
    Simulation,
    OptiSimulation,
    ForecastSimulation
)
from rameau.core.groundwater import (
    GroundwaterParameters,
    GroundwaterReservoir,
    StorageParameters
)
from rameau.core.settings import (
    SimulationSettings,
    OptimizationSettings,
    ForecastSettings
)
from rameau.core.states import StatesCollection

txt_test_from_toml = """[files]
pet = "pet"
rainfall = "rainfall"
tree = "tree"
temperature = " "
[optimization]
maxit = 250
starting_date = 1989-01-01
river_objective_function = "nse"
[forecast]
scope = { days = 6 }
[watershed.all]
river.weight = 5
river.area = {value=524, opti=false}
thornthwaite.capacity = {value=0, opti=true, sameas=0, lower=0.1, upper=350}
progressive.capacity = {value=180, opti=true, sameas=0, lower=0.000, upper=650}
transfer.runsee = {value=600, opti=true, sameas=0, lower=5.0, upper=9999}
transfer.halflife = {value=5, opti=true, sameas=0, lower=0.15, upper=50}
groundwater.observed_reservoir = 1
groundwater.weight = 2
groundwater.base_level = {value=125, opti=true}
groundwater.storage.regression = true
groundwater.storage.coefficient = {value=1, opti=true, lower=0.02, upper=50}
groundwater.1.exchanges = {value=0, opti=false, sameas=0, lower=-50, upper=50}
groundwater.1.halflife_baseflow = {value=20, opti=true, sameas=0, lower=0.1, upper=70}
"""

txt_test_no_tree_file = txt_test_from_toml.replace('"tree"', '""')

txt_test_to_toml = """name = "foo"
starting_date = 2000-01-01 00:00:00.000
[files]
pet = ""
rainfall = "foo/f o o/féo"
snow = ""
temperature = ""
tree = ""
riverobs = ""
riverpumping = ""
groundwaterobs = ""
groundwaterpumping = ""
states = ""
[input_format]
meteo_files = false
starting_date = 1900-01-01 00:00:00.000
[outputs]
budget = false
metrics = true
parameters = true
toml = true
states = true
[spinup]
starting_date = 2000-01-01 00:00:00.000
ending_date = 2000-01-01 00:00:00.000
cycles = 0
[forecast]
forecast = false
emission_date = 2000-01-01 00:00:00.000
correction = "no"
quantiles_output = false
quantiles = [ 10, 20, 50, 80, 90 ]
norain = false
scope = { seconds = 691200 }
[optimization]
maxit = 5
starting_date = 2000-01-01 00:00:00.000
transformation = "no"
method = "all"
river_objective_function = "nse"
verbose = false
[watershed.all]
name = ""
is_confluence = false
meteo.weights = [ 1.00000 ]
forecast.river.halflife = 0.00000
forecast.groundwater.halflife = 0.00000
correction.area = { value = 1.00000, lower = 0.00100, upper = 7.00000, opti = false, sameas = 0 }
correction.rainfall = { value = 0.00000, lower = -10.00000, upper = 10.00000, opti = false, sameas = 0 }
correction.pet = { value = 0.00000, lower = -15.00000, upper = 15.00000, opti = false, sameas = 0 }
river.weight = 1.00000
river.obslim = [ 0.00000, 0.00000 ]
river.area = { opti = true }
river.minimum_riverflow = { value = 0.00000, opti = false }
river.concentration_time = { value = 0.00000, lower = 0.00000, upper = 10.00000, opti = false, sameas = 0 }
river.propagation_time = { value = 0.00000, lower = 0.00000, upper = 45.00000, opti = false, sameas = 0 }
thornthwaite.capacity = { value = 0.30000, lower = 0.10000, upper = 0.30000, opti = false, sameas = 0 }
progressive.pet_decrease = false
progressive.capacity = { value = 150.00000, lower = 0.00000, upper = 650.00000, opti = false, sameas = 0 }
transfer.runsee = { value = 100.00000, lower = 1.00000, upper = 9.9990000000000000E+3, opti = false, sameas = 0 }
transfer.halflife = { value = 0.20000, lower = 0.10000, upper = 0.30000, opti = true, sameas = 0 }
transfer.overflow.loss = "no"
transfer.overflow.threshold = { value = 0.00000, lower = 0.00000, upper = 9.9990000000000000E+3, opti = false, sameas = 0 }
transfer.overflow.halflife = { value = 0.00000, lower = 0.00100, upper = 20.00000, opti = false, sameas = 0 }
groundwater.weight = 0.00000
groundwater.obslim = [ 0.00000, 0.00000 ]
groundwater.observed_reservoir = 1
groundwater.base_level = { value = 0.00000, opti = false }
groundwater.storage.regression = false
groundwater.storage.coefficient = { value = 0.20000, lower = 0.10000, upper = 0.30000, opti = true, sameas = 0 }
groundwater.1.halflife_baseflow = { value = 0.30000, lower = 0.10000, upper = 0.30000, opti = false, sameas = 0 }
groundwater.1.halflife_drainage = { value = 0.00000, lower = 0.05000, upper = 50.00000, opti = false, sameas = 0 }
groundwater.1.exchanges = { value = 0.00000, lower = -20.00000, upper = 20.00000, opti = false, sameas = 0 }
groundwater.1.overflow.threshold = { value = 0.00000, lower = 0.00000, upper = 9.9990000000000000E+3, opti = false, sameas = 0 }
groundwater.1.overflow.halflife = { value = 0.00000, lower = 0.00100, upper = 20.00000, opti = false, sameas = 0 }
snow.correction.temperature = { value = 0.00000, lower = -20.00000, upper = 20.00000, opti = false, sameas = 0 }
snow.correction.pet = { value = 0.00000, lower = -20.00000, upper = 20.00000, opti = false, sameas = 0 }
snow.correction.rainfall = { value = 0.00000, lower = 0.00100, upper = 20.00000, opti = false, sameas = 0 }
snow.degree_day.coefficient = { value = 0.00000, lower = 0.00100, upper = 7.00000, opti = false, sameas = 0 }
snow.degree_day.temperature = { value = 0.00000, lower = -2.00000, upper = 2.00000, opti = false, sameas = 0 }
snow.retention = { value = 0.00000, lower = 0.00000, upper = 0.00000, opti = false, sameas = 0 }
snow.melting = { value = 0.00000, lower = 0.00000, upper = 0.00000, opti = false, sameas = 0 }
pumping.river.coefficient = { value = 1.00000, opti = false }
pumping.river.halflife_rise = { value = 0.00000, lower = 0.05000, upper = 10.00000, opti = false, sameas = 0 }
pumping.river.halflife_fall = { value = 0.00000, lower = 0.05000, upper = 15.00000, opti = false, sameas = 0 }
pumping.groundwater.coefficient = { value = 1.00000, opti = false }
pumping.groundwater.halflife_rise = { value = 0.00000, lower = 0.05000, upper = 10.00000, opti = false, sameas = 0 }
pumping.groundwater.halflife_fall = { value = 0.00000, lower = 0.05000, upper = 15.00000, opti = false, sameas = 0 }
[watershed.1]
meteo.columns = [ 1 ]
river.area = { value = 0.10000 }
[watershed.2]
meteo.columns = [ 2 ]
river.area = { value = 0.20000 }
"""

class TestMiscellaneousModel(unittest.TestCase):
    def test_input_one_dimension(self):
        data = np.random.rand(3)
        w = Watershed()
        t = Tree(watersheds=[w])
        inputs = InputCollection(rainfall=data, pet=data)
        model = Model(tree=t, inputs=inputs)
        self.assertIsInstance(model, Model)

class TestModel(unittest.TestCase):
    def setUp(self):
        self.data = np.array([[1.2, 4], [2.2, 5], [3, 6.3]])
        self.dates=pd.date_range("2000-1-1", "2000-1-3")
        self.ref = Parameter(value=0.2, lower=0.1, upper=0.3)
        inputs = InputCollection(
            rainfall=self.data, pet=self.data,
            riverobs=self.data, dates=self.dates,
        )
        watershed_keys = {
            "river":RiverParameters(area=self.ref),
            "thornthwaite_reservoir":ThornthwaiteReservoir(capacity=self.ref),
            "transfer_reservoir":TransferReservoir(halflife=self.ref),
            "groundwater":GroundwaterParameters(
                reservoirs=[GroundwaterReservoir(halflife_baseflow=self.ref)],
                storage=StorageParameters(coefficient=self.ref)
            ),
        }
        watershed1 = Watershed(**watershed_keys)
        watershed2 = Watershed(**watershed_keys)
        tree = Tree(watersheds=[watershed1, watershed2], connection={1:2, 2:0})
        sim_set = SimulationSettings(
            name='foo',
            starting_date=datetime.datetime(2000, 1, 1),
            spinup_settings=dict(
                starting_date=datetime.datetime(2000, 1, 1),
                ending_date=datetime.datetime(2000, 1, 1),
            )
        )
        opt_set = OptimizationSettings(
            maxit=5, starting_date=datetime.datetime(2000, 1, 1)
        )
        fcast_set = ForecastSettings(
            emission_date=datetime.datetime(2000, 1, 1),
            scope=datetime.timedelta(days=8)
        )
        self.refs = {
            'tree':tree,
            'inputs':inputs,
            'simulation_settings':sim_set,
            'optimization_settings':opt_set,
            'forecast_settings':fcast_set
        }

    def test_properties_instances(self):
        instances = {
            'tree': Tree,
            'inputs': InputCollection,
            'simulation_settings': SimulationSettings,
            'optimization_settings': OptimizationSettings,
            'forecast_settings': ForecastSettings,
            'init_states': StatesCollection
        }
        foo = Model(**self.refs)
        for key in instances.keys():
            with self.subTest(key):
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = Model(**self.refs)
        keys = [
            "simulation_settings", "optimization_settings",
            "forecast_settings", "tree"
        ]
        for key in keys:
            with self.subTest(key):
                self.assertEqual(foo[key], self.refs[key])
        for key in InputCollection._computed_attributes[:-2]:
            np.testing.assert_almost_equal(
                foo["inputs"][key].data, self.refs["inputs"][key].data)
            pd.testing.assert_index_equal(
                foo["inputs"][key].dates, self.refs["inputs"][key].dates)
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in Model._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    Model(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = Model(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        keys = [
            "simulation_settings", "optimization_settings",
            "forecast_settings", "tree", "init_states"
        ]
        for key in keys:
            with self.subTest(key):
                self.assertEqual(foo[key], foo_new[key])
        for key in InputCollection._computed_attributes[:-2]:
            np.testing.assert_almost_equal(
                foo["inputs"][key].data, foo_new["inputs"][key].data)
            pd.testing.assert_index_equal(
                foo["inputs"][key].dates, foo_new["inputs"][key].dates)
    
    def test_run_simulation(self):
        model = Model(**self.refs)
        sim = model.run_simulation()
        self.assertIsInstance(sim, Simulation)

    def test_create_simulation(self):
        model = Model(**self.refs)
        sim = model.create_simulation()
        self.assertIsInstance(sim, Simulation)

    def test_create_two_simulation(self):
        model = Model(**self.refs)
        sim = model.create_simulation()
        sim = model.create_simulation()
        self.assertIsInstance(sim, Simulation)

    def test_two_run_simulation(self):
        model = Model(**self.refs)
        sim = model.run_simulation()
        sim = model.run_simulation()
        self.assertIsInstance(sim, Simulation)

class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.data = np.array([[1.2, 4], [2.2, 5], [3, 6.3]])
        self.dates = pd.date_range("2000-1-1", "2000-1-3")
        self.ref = Parameter(value=0.2, lower=0.1, upper=0.3, opti=True)
        self.ref2 = Parameter(value=0.3, lower=0.1, upper=0.3)
        inputs = InputCollection(
            rainfall=self.data, pet=self.data,
            riverobs=self.data, dates=self.dates,
        )
        inputs.file_paths.rainfall = 'foo/f o o/féo'
        watershed_keys = {
            "river": RiverParameters(area=self.ref),
            "thornthwaite_reservoir": ThornthwaiteReservoir(capacity=self.ref2),
            "transfer_reservoir": TransferReservoir(halflife=self.ref),
            "groundwater": GroundwaterParameters(
                reservoirs=[GroundwaterReservoir(halflife_baseflow=self.ref2)],
                storage=StorageParameters(coefficient=self.ref)
            ),
        }
        watershed1 = Watershed(**watershed_keys)
        watershed1.river.area.value = 0.1
        watershed2 = Watershed(**watershed_keys)
        tree = Tree(
            watersheds=[watershed1, watershed2],
            connection={1: 2, 2: 0}
        )
        sim_set = SimulationSettings(
            name='foo',
            starting_date=datetime.datetime(2000, 1, 1),
            spinup_settings=dict(
                starting_date=datetime.datetime(2000, 1, 1),
                ending_date=datetime.datetime(2000, 1, 1),
            )
        )
        opt_set = OptimizationSettings(
            maxit=5, starting_date=datetime.datetime(2000, 1, 1)
        )
        fcast_set = ForecastSettings(
            emission_date=datetime.datetime(2000, 1, 1),
            scope=datetime.timedelta(days=8)
        )
        refs = {
            'tree': tree,
            'inputs': inputs,
            'simulation_settings': sim_set,
            'optimization_settings': opt_set,
            'forecast_settings': fcast_set
        }
        self.model = Model(**refs)
    
    def test_properties_instances(self):
        sim = self.model.run_simulation()
        self.assertIsInstance(sim.simulation_settings, SimulationSettings)
        self.assertIsInstance(sim.tree, Tree)
    
    def test_get_output_riverflow(self):
        sim = self.model.run_simulation()
        data = sim.get_output()
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(data.shape, (3, 2))

    def test_get_output_watertable(self):
        sim = self.model.run_simulation()
        data = sim.get_output("watertable")
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(data.shape, (3, 2))

    def test_get_budget(self):
        sim = self.model.run_simulation()
        data = sim.get_budget()
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(data.shape, (3, 20 * 2))

    def test_get_metrics_riverflow(self):
        sim = self.model.run_simulation()
        data = sim.get_metrics()
        self.assertIsInstance(data, pd.DataFrame)
    
    def test_get_metrics_watertable(self):
        sim = self.model.run_simulation()
        data = sim.get_metrics("watertable")
        self.assertIsInstance(data, pd.DataFrame)

    def test_run_optimization(self):
        sim = self.model.run_optimization(
            maxit=2,
            starting_date=datetime.datetime(2000, 1, 1),
            ending_date=datetime.datetime(2000, 1, 2)
        )
        opt = OptimizationSettings(
            maxit=2,
            starting_date=datetime.datetime(2000, 1, 1),
            ending_date=datetime.datetime(2000, 1, 2)
        )
        self.assertIsInstance(sim, Simulation)
        self.assertIsInstance(sim, OptiSimulation)
        self.assertIsInstance(sim.optimization_settings, OptimizationSettings)
        self.assertEqual(sim.optimization_settings, opt)

    def test_two_run_optimization(self):
        sim = self.model.run_optimization(
            maxit=1,
            starting_date=datetime.datetime(2000, 1, 1),
            ending_date=datetime.datetime(2000, 1, 2)
        )
        sim = self.model.run_optimization(
            maxit=1,
            starting_date=datetime.datetime(2000, 1, 1),
            ending_date=datetime.datetime(2000, 1, 2)
        )
        self.assertIsInstance(sim, Simulation)

    def test_run_forecast(self):
        sim = self.model.run_forecast(
            emission_date=datetime.datetime(2000, 1, 1),
            scope=datetime.timedelta(days=2),
            quantiles_output=True,
            norain=True,
        )
        self.assertIsInstance(sim, Simulation)
        self.assertIsInstance(sim, ForecastSimulation)

    def test_get_forecast_output_riverflow(self):
        sim = self.model.run_forecast(
            emission_date=datetime.datetime(2000, 1, 1),
            scope=datetime.timedelta(days=2),
            quantiles_output=True,
            norain=True,
        )
        data = sim.get_forecast_output()
        self.assertIsInstance(data, pd.DataFrame)
        self.assertIsInstance(data.index[0], datetime.datetime)

    def test_1_scope_forecast(self):
        sim = self.model.run_forecast(
            emission_date=datetime.datetime(2000, 1, 1),
            scope=datetime.timedelta(days=1),
            quantiles_output=True,
            norain=True,
        )
        self.assertIsInstance(sim, Simulation)
        self.assertIsInstance(sim, ForecastSimulation)

    def test_two_run_forecast(self):
        sim = self.model.run_forecast(
            emission_date=datetime.datetime(2000, 1, 1),
            scope=datetime.timedelta(days=2),
            quantiles_output=True,
            norain=True,
        )
        sim = self.model.run_forecast(
            emission_date=datetime.datetime(2000, 1, 1),
            scope=datetime.timedelta(days=2),
            quantiles_output=True,
            norain=True,
        )
        self.assertIsInstance(sim, ForecastSimulation)
    
    def test_get_input(self):
        sim = self.model.run_simulation()
        df = sim.get_input("rainfall")
        np.testing.assert_almost_equal(df.values, self.data.data, decimal=6)
        np.testing.assert_equal(df.index.values, self.dates.values)

    def test_get_input_rainfall(self):
        df = self.model.get_input()
        np.testing.assert_almost_equal(df.values, self.data.data, decimal=6)
        np.testing.assert_equal(df.index.values, self.dates.values)

    def test_get_input_pet(self):
        df = self.model.get_input("pet")
        np.testing.assert_almost_equal(df.values, self.data.data, decimal=6)
        np.testing.assert_equal(df.index.values, self.dates.values)

    def test_get_input_snow(self):
        df = self.model.get_input("snow")
        self.assertIsInstance(df, pd.DataFrame)

    def test_to_toml(self):
        self.maxDiff = None
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = tmpdirname + '/foo'
            self.model.to_toml(fname)
            with open(fname, encoding="utf-8") as ff:
                self.assertEqual(ff.read(), txt_test_to_toml)

class TestModelFromToml(unittest.TestCase):
    def setUp(self):
        self.tmpdirname = tempfile.mkdtemp()
        river = RiverParameters(
            area=dict(value=524, opti=False),
            weight=5
        )
        thorn = ThornthwaiteReservoir(
            capacity=dict(value=0, opti=True, lower=0.1, upper=350)
        )
        prog = ProgressiveReservoir(
            capacity=dict(value=180, opti=True, lower=0.0, upper=650)
        )
        transfer = TransferReservoir(
            runsee=dict(value=600, opti=True, lower=5, upper=9999),
            halflife=dict(value=5, opti=True, lower=0.15, upper=50)
        )
        gw = GroundwaterParameters(
            weight=2,
            observed_reservoir=1,
            base_level=dict(value=125, opti=True),
            storage=StorageParameters(
                regression=True,
                coefficient=dict(value=1, opti=True, lower=0.02, upper=50)
            ),
            reservoirs=[
                GroundwaterReservoir(
                    halflife_baseflow=dict(value=20, opti=True, lower=0.1, upper=70),
                    exchanges=dict(value=0, opti=False, lower=-50, upper=50)
                )
            ]
        )
        watershed = Watershed(
            name="Watershed 1",
            river=river,
            thornthwaite_reservoir=thorn,
            progressive_reservoir=prog,
            transfer_reservoir=transfer,
            groundwater=gw
        )
        opt = OptimizationSettings(
            maxit=250,
            starting_date=datetime.datetime(1989, 1, 1),
        )
        self.data = np.random.random((5000, 1))
        inputs = InputCollection(
            rainfall=self.data, pet=self.data
        )
        inputs.file_paths = FilePaths(
            rainfall='rainfall', pet='pet', tree='tree'
        )
        self.model_ref = Model(
            tree=Tree(
                watersheds=[watershed]
            ),
            inputs=inputs,
            optimization_settings=opt,
            forecast_settings=ForecastSettings(
                scope = datetime.timedelta(days=6)
            )
        )
        fname = self.tmpdirname + '/rainfall'
        with open(fname , 'w') as f:
            f.write("Header\n")
            np.savetxt(f, self.data)
        fname = self.tmpdirname + '/pet'
        with open(fname , 'w') as f:
            f.write("Header\n")
            np.savetxt(f, self.data)
        fname = self.tmpdirname + '/tree'
        self.model_ref.tree.to_csv(fname)
        os.chdir(self.tmpdirname)

    def test_from_toml(self):
        fname = 'toml_ref.toml'
        with open(fname , 'w') as f:
            f.write(txt_test_from_toml)
        model = Model.from_toml('toml_ref.toml')

        self.assertEqual(model.optimization_settings,  self.model_ref.optimization_settings)
        self.assertEqual(model.forecast_settings,  self.model_ref.forecast_settings)
        self.assertEqual(model.simulation_settings,  self.model_ref.simulation_settings)
        self.assertEqual(model.init_states,  self.model_ref.init_states)
        self.assertEqual(model.inputs.file_paths,  self.model_ref.inputs.file_paths)
        np.testing.assert_almost_equal(model.inputs.rainfall.data,  self.model_ref.inputs.rainfall.data, decimal=6)
        for key in Watershed._computed_attributes:
            with self.subTest(key):
                self.assertEqual(model.tree.watersheds[0][key], self.model_ref.tree.watersheds[0][key])


    def test_no_tree_file(self):
        self.model_ref.inputs.file_paths.tree = ""
        fname = 'toml_ref.toml'
        with open(fname , 'w') as f:
            f.write(txt_test_no_tree_file)
        model = Model.from_toml('toml_ref.toml')

        self.assertEqual(model.inputs.file_paths,  self.model_ref.inputs.file_paths)
        for key in Watershed._computed_attributes:
            with self.subTest(key):
                self.assertEqual(model.tree.watersheds[0][key], self.model_ref.tree.watersheds[0][key])
    
    def tearDown(self):
        shutil.rmtree(self.tmpdirname, ignore_errors=True)
        os.chdir(os.path.dirname(__file__))

class TestModelBadKey(unittest.TestCase):
    def setUp(self):
        self.tmpdirname = tempfile.mkdtemp()

        data = np.random.random((3, 1))

        fname = self.tmpdirname + '/rainfall'
        with open(fname , 'w') as f:
            f.write("Header\n")
            np.savetxt(f, data)
        fname = self.tmpdirname + '/pet'
        with open(fname , 'w') as f:
            f.write("Header\n")
            np.savetxt(f, data)

        os.chdir(self.tmpdirname)

    def test_bad_key(self):
        fname = 'toml_ref.toml'
        a = txt_test_from_toml.replace('"tree"', "''")
        b = a.replace("maxit", "toto")
        with open(fname , 'w') as f:
            f.write(b)
        with self.assertRaises(RuntimeError):
            _ = Model.from_toml('toml_ref.toml')

    def tearDown(self):
        shutil.rmtree(self.tmpdirname, ignore_errors=True)
        os.chdir(os.path.dirname(__file__))
