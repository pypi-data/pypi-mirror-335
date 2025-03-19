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
from rameau.core.inputs import InputFormat

class TestInputFormat(unittest.TestCase):
    def setUp(self):
        self.refs = {
            "starting_date":datetime.datetime(1992, 2, 3),
            "time_step":datetime.timedelta(30),
            "meteo_files":True,
        }

    def test_properties_instances(self):
        instances = {
            "starting_date":datetime.datetime,
            "time_step":datetime.timedelta,
            "meteo_files":bool,
        }
        for key in InputFormat._computed_attributes:
            with self.subTest(key):
                foo = InputFormat(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = InputFormat(
            **{
                key:self.refs[key]
                for key in InputFormat._computed_attributes
            }
        )
        for key, value in foo.items():
            self.assertEqual(value, self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in InputFormat._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    InputFormat(**{key:DummyType()})
    
    def test_default_starting_date(self):
        foo = InputFormat()
        self.assertEqual(foo.starting_date, datetime.datetime(1900, 1, 1))
    
    def test_pickle(self):
        import pickle
        foo = InputFormat(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)
    