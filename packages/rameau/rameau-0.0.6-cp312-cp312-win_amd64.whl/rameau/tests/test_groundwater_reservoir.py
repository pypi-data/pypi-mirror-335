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


from rameau.core.groundwater import GroundwaterReservoir
from rameau.core import Parameter, OverflowParameters

class TestGroundwaterReservoir(unittest.TestCase):
    def setUp(self):
        ref = Parameter(value=0.3, lower=0.1, upper=0.5, opti=True, sameas=1)
        overflow = OverflowParameters(threshold=ref, halflife=ref)
        self.refs = {
            "h":0.2,
            "halflife_baseflow":ref, 
            "halflife_drainage": ref,
            "exchanges": ref,
            "overflow":overflow
        }

    def test_is_instance(self):
        foo = GroundwaterReservoir()
        self.assertIsInstance(foo, GroundwaterReservoir)

    def test_properties_instances(self):
        instances = {
            "h":float,
            "halflife_baseflow":Parameter, 
            "halflife_drainage": Parameter,
            "exchanges": Parameter,
            "overflow": OverflowParameters
        }
        for key in GroundwaterReservoir._computed_attributes:
            with self.subTest(key):
                foo = GroundwaterReservoir(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = GroundwaterReservoir(**self.refs)
        for key in GroundwaterReservoir._computed_attributes:
            if type(self.refs[key]) is float:
                self.assertAlmostEqual(foo[key], self.refs[key])
            else:
                self.assertEqual(foo[key], self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in GroundwaterReservoir._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    GroundwaterReservoir(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = GroundwaterReservoir(
            **{
                key:self.refs[key]
                for key in GroundwaterReservoir._computed_attributes
            }
        )
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)

    def test_assign_overflow_value(self):
        foo = GroundwaterReservoir(
            overflow=dict(
                threshold=dict(value=0.3)
            )
        )
        foo.overflow.threshold.value = 0.2
        self.assertAlmostEqual(foo.overflow.threshold.value, 0.2)
    
    def test_transfer(self):
        foo = GroundwaterReservoir(
            halflife_baseflow=Parameter(1),
            halflife_drainage=Parameter(2),
            exchanges = Parameter(5),
            overflow=OverflowParameters(
                halflife=Parameter(10),
                threshold=Parameter(100)
            ),
            h=120
        )
        res = foo.transfer(10)
        self.assertIsInstance(res, dict)
        self.assertAlmostEqual(foo.h, 125.572, places=3)
        