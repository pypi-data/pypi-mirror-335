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
from rameau.core.settings import OptimizationSettings

class TestOptimizationSettings(unittest.TestCase):
    def setUp(self):
        self.refs = {
            "maxit":25,
            "starting_date":datetime.datetime(1992, 2, 3),
            "ending_date":datetime.datetime(1993, 3, 2),
            "method":"strahler",
            "transformation":"square root",
            "river_objective_function":"kge",
            "selected_watersheds":[1, 2],
            "verbose":True
        }

    def test_properties_instances(self):
        instances = {
            "maxit":int,
            "starting_date":datetime.datetime,
            "ending_date":datetime.datetime,
            "method":str,
            "transformation":str,
            "river_objective_function":str,
            "selected_watersheds":list,
            "verbose":bool
        }
        for key in OptimizationSettings._computed_attributes:
            with self.subTest(key):
                foo = OptimizationSettings(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_assign_maxit(self):
        foo = OptimizationSettings(maxit=4)
        foo.maxit = 5
        self.assertEqual(foo.maxit, 5)
    
    def test_properties_values(self):
        foo = OptimizationSettings(**self.refs)
        for key, value in foo.items():
            self.assertEqual(value, self.refs[key])
    
    def test_bad_literal(self):
        with self.assertRaises(ValueError):
            OptimizationSettings(transformation="toto")
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in OptimizationSettings._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    OptimizationSettings(**{key:DummyType()})
    
    def test_default_starting_date(self):
        opt = OptimizationSettings()
        self.assertEqual(opt.starting_date, None)
    
    def test_pickle(self):
        import pickle
        foo = OptimizationSettings(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)
    