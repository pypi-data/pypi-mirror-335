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

from rameau.core.snow import (
    SnowReservoir, DegreeDayParameters, SnowCorrectionParameters
)
from rameau.core import Parameter

class TestSnowReservoir(unittest.TestCase):
    def setUp(self):
        ref = Parameter(value=0.3, lower=0.1, upper=0.5, opti=True, sameas=1)
        degree_day = DegreeDayParameters(
            temperature=ref, coefficient=ref
        )
        snow_correction = SnowCorrectionParameters(
            temperature=ref,
            pet=ref,
            rainfall=ref
        )
        self.refs = {
            "swe": 0.1,
            "r": 0.2,
            "melting":ref, 
            "retention": ref,
            "degree_day": degree_day,
            "snow_correction":snow_correction
        }

    def test_is_instance(self):
        foo = SnowReservoir()
        self.assertIsInstance(foo, SnowReservoir)

    def test_properties_instances(self):
        instances = {
            "swe": float,
            "r": float,
            "melting":Parameter, 
            "retention": Parameter,
            "degree_day": DegreeDayParameters,
            "snow_correction":SnowCorrectionParameters
        }
        for key in SnowReservoir._computed_attributes:
            with self.subTest(key):
                foo = SnowReservoir(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = SnowReservoir(**self.refs)
        for key in SnowReservoir._computed_attributes:
            if type(foo[key]) is float:
                self.assertAlmostEqual(foo[key], self.refs[key])
            else:
                self.assertEqual(foo[key], self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in SnowReservoir._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    SnowReservoir(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = SnowReservoir(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)

    def test_production(self):
        res = SnowReservoir(
            melting=Parameter(value=2),
            retention=Parameter(value=50),
            degree_day=DegreeDayParameters(
                coefficient=Parameter(2),
                temperature=Parameter(1)
            ),
            swe=3,
            r=0.5
        )
        toto = res.production(0, 0, -1, 1)
        self.assertAlmostEqual(toto["snow_melt_to_soil"], 0.2)
        self.assertAlmostEqual(res.swe, 3.79999, places=3)