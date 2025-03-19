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

from rameau.core import RiverParameters
from rameau.core import Parameter

class TestRiverParameters(unittest.TestCase):
    def setUp(self):
        ref = Parameter(value=0.3, lower=0.1, upper=0.5, opti=True, sameas=1)
        self.refs = {
            "area":ref, 
            "minimum_riverflow": ref,
            "concentration_time": ref,
            "propagation_time": ref,
            "weight": 2,
            "obslim": [0.8, 1.2],
        }

    def test_is_instance(self):
        foo = RiverParameters()
        self.assertIsInstance(foo, RiverParameters)

    def test_properties_instances(self):
        instances = {
            "area":Parameter, 
            "minimum_riverflow": Parameter,
            "concentration_time": Parameter,
            "propagation_time": Parameter,
            "weight": float,
            "obslim": list,
        }
        for key in RiverParameters._computed_attributes:
            with self.subTest(key):
                foo = RiverParameters(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = RiverParameters(**self.refs)
        for key, value in foo.items():
            if key == 'obslim':
                self.assertAlmostEqual(value[0], self.refs[key][0])
                self.assertAlmostEqual(value[1], self.refs[key][1])
            else:
                self.assertEqual(value, self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in RiverParameters._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    RiverParameters(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = RiverParameters(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)

    def test_bad_obslim(self):
        with self.assertRaises(TypeError):
            RiverParameters(obslim=[0.0, 0.0, 0.0])

