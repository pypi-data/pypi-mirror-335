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
from rameau.core.settings import ForecastSettings
import numpy as np

class TestForecastSettings(unittest.TestCase):
    def setUp(self):
        self.refs = {
            "emission_date":datetime.datetime(1992, 2, 3),
            "scope":datetime.timedelta(30),
            "year_members":[1992, 1993, 1994],
            "correction":'halflife',
            "pumping_date":datetime.datetime(1992, 2, 3),
            "quantiles_output":True,
            "quantiles":[10, 50, 90],
            "norain":True
        }

    def test_properties_instances(self):
        instances = {
            "emission_date":datetime.datetime,
            "scope":datetime.timedelta,
            "year_members":list,
            "correction":str,
            "pumping_date":datetime.datetime,
            "quantiles_output":bool,
            "quantiles":list,
            "norain":bool
        }
        for key in ForecastSettings._computed_attributes:
            with self.subTest(key):
                foo = ForecastSettings(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = ForecastSettings(
            **{
                key:self.refs[key]
                for key in ForecastSettings._computed_attributes
            }
        )
        for key, value in foo.items():
            self.assertEqual(value, self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in ForecastSettings._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    ForecastSettings(**{key:DummyType()})
    
    def test_empty_list(self):
        foo = ForecastSettings(year_members=[])
        self.assertEqual(foo.year_members, [])
    
    def test_pickle(self):
        import pickle
        foo = ForecastSettings(
            **{
                key:self.refs[key]
                for key in ForecastSettings._computed_attributes
            }
        )
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)
    