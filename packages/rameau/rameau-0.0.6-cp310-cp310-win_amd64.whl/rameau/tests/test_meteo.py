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
from rameau.core import Meteo

class TestMeteo(unittest.TestCase):
    def setUp(self):
        self.refs = dict(
            columns=[1, 2, 3],
            weights=[1.1, 2.2, 3],
        )

    def test_properties_instances(self):
        instances = {
            "columns":list,
            "weights":list
        }
        foo = Meteo(**{key:self.refs[key] for key in instances})
        for key in Meteo._computed_attributes:
            with self.subTest(key):
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = Meteo(
            **{
                key:self.refs[key]
                for key in Meteo._computed_attributes
            }
        )
        for key, value in foo.items():
            if type(value) is list:
                for i in range(len(value)):
                    self.assertAlmostEqual(value[i], self.refs[key][i])
            else:
                self.assertEqual(value, self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in Meteo._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    Meteo(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = Meteo(
            **{
                key:self.refs[key]
                for key in Meteo._computed_attributes
            }
        )
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)
    