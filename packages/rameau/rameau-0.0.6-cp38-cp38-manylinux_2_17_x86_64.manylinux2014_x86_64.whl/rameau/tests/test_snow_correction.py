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

from rameau.core.snow import SnowCorrectionParameters
from rameau.core import Parameter

class TestDegreedayParameters(unittest.TestCase):
    def setUp(self):
        self.ref = Parameter(value=0.3, lower=0.1, upper=0.5, opti=True, sameas=1)

    def test_is_instance(self):
        foo = SnowCorrectionParameters()
        self.assertIsInstance(foo, SnowCorrectionParameters)

    def test_properties_instances(self):
        for key in SnowCorrectionParameters._computed_attributes:
            with self.subTest(key):
                foo = SnowCorrectionParameters(**{key:dict(value=0.3)})
                self.assertIsInstance(getattr(foo, key), Parameter)
    
    def test_properties_values(self):
        foo = SnowCorrectionParameters(**{
            i:self.ref for i in SnowCorrectionParameters._computed_attributes}
        )
        for key in SnowCorrectionParameters._computed_attributes:
            self.assertAlmostEqual(foo[key], self.ref)
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in SnowCorrectionParameters._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    SnowCorrectionParameters(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = SnowCorrectionParameters(
            **{
                key:self.ref
                for key in SnowCorrectionParameters._computed_attributes
            }
        )
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)