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

from rameau.core import CorrectionParameters, Parameter

class TestCorrectionParameters(unittest.TestCase):
    def setUp(self):
        self.ref = dict(value=0.3, lower=0.1, upper=0.5, opti=True, sameas=1)

    def test_properties_instances(self):
        for key in CorrectionParameters._computed_attributes:
            with self.subTest(key):
                foo = CorrectionParameters(**{key:dict(value=0.3)})
                self.assertIsInstance(getattr(foo, key), Parameter)
    
    def test_properties_values(self):
        foo = CorrectionParameters(
            **{
                key:self.ref
                for key in CorrectionParameters._computed_attributes
            }
        )
        for key in CorrectionParameters._computed_attributes:
            foo2 = foo[key]
            for key_ref in self.ref:
                self.assertAlmostEqual(foo2[key_ref], self.ref[key_ref])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in CorrectionParameters._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    CorrectionParameters(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = CorrectionParameters(
            **{
                key:self.ref
                for key in CorrectionParameters._computed_attributes
            }
        )
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)