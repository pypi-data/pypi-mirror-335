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

from rameau.core import ThornthwaiteReservoir, Parameter

class TestThornthwaiteReservoir(unittest.TestCase):
    def setUp(self):
        ref = dict(value=0.3, lower=0.1, upper=0.5, opti=True, sameas=1)
        self.refs = {
            "h":0.1,
            "capacity":ref
        }

    def test_properties_instances(self):
        instances = {
            "h":float,
            "capacity":Parameter
        }
        for key in ThornthwaiteReservoir._computed_attributes:
            with self.subTest(key):
                foo = ThornthwaiteReservoir(**self.refs)
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = ThornthwaiteReservoir(**self.refs)
        for key, value in foo.items():
            if key == "capacity":
                for key_ref in self.refs[key]:
                    self.assertAlmostEqual(
                        value[key_ref], self.refs[key][key_ref]
                    )
            else:
                self.assertAlmostEqual(value, self.refs[key])
                    
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in ThornthwaiteReservoir._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    ThornthwaiteReservoir(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = ThornthwaiteReservoir(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)
    
    def test_production(self):
        res = ThornthwaiteReservoir(
            capacity=dict(value=150),
            h=12,
        )
        toto = res.production(5, 2)
        self.assertEqual(
            toto,
            {
                'effective_rainfall':0.0,
                'aet':2.0,
                'unsatisfied_pet':0.0
            }
        )
        self.assertEqual(res.h, 15)
