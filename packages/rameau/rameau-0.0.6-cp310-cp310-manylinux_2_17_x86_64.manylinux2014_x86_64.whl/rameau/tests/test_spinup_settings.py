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
from rameau.core.settings import SpinupSettings

class TestSpinupSettings(unittest.TestCase):
    def setUp(self):
        self.refs = {
            "starting_date":datetime.datetime(2000, 1, 1),
            "ending_date":datetime.datetime(2000, 1, 1),
            "cycles":2
        }

    def test_properties_instances(self):
        instances = {
            "cycles":int,
            "starting_date":datetime.datetime,
            "ending_date":datetime.datetime,
        }
        for key in SpinupSettings._computed_attributes:
            with self.subTest(key):
                foo = SpinupSettings(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])

    def test_properties_values(self):
        foo = SpinupSettings(
            **{
                key:self.refs[key]
                for key in SpinupSettings._computed_attributes
            }
        )
        for key, value in foo.items():
            self.assertEqual(value, self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in SpinupSettings._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    SpinupSettings(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = SpinupSettings(
            **{
                key:self.refs[key]
                for key in SpinupSettings._computed_attributes
            }
        )
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)
    