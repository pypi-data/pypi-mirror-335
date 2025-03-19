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

from rameau.core.groundwater import GroundwaterParameters, StorageParameters, GroundwaterReservoir
from rameau.core import Parameter

class TestGroundwaterParameters(unittest.TestCase):
    def setUp(self):
        ref = Parameter(value=0.3, lower=0.1, upper=0.5, opti=True, sameas=1)
        storage = StorageParameters(coefficient=ref, regression=True)
        reservoir = GroundwaterReservoir(
            halflife_baseflow=ref, halflife_drainage=ref, exchanges=ref
        )
        self.refs = {
            "storage":storage, 
            "base_level": ref,
            "weight": 2,
            "obslim": [0.8, 1.2],
            "observed_reservoir": 2,
            "reservoirs":[reservoir, reservoir]
        }

    def test_is_instance(self):
        foo = GroundwaterParameters()
        self.assertIsInstance(foo, GroundwaterParameters)

    def test_properties_instances(self):
        instances = {
            "storage":StorageParameters, 
            "base_level": Parameter,
            "weight": float,
            "obslim": list,
            "observed_reservoir": int,
            "reservoirs":list
        }
        for key in GroundwaterParameters._computed_attributes:
            with self.subTest(key):
                foo = GroundwaterParameters(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = GroundwaterParameters(**self.refs)
        for i in range(2):
            self.assertAlmostEqual(foo["obslim"][i], self.refs["obslim"][i])
        self.assertEqual(foo["weight"], self.refs["weight"])
        self.assertAlmostEqual(foo["base_level"], self.refs["base_level"])
        self.assertAlmostEqual(foo["storage"], self.refs["storage"])
        for res1, res2 in zip(foo["reservoirs"], self.refs["reservoirs"]):
            self.assertAlmostEqual(res1, res2)
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in GroundwaterParameters._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    GroundwaterParameters(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = GroundwaterParameters(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)