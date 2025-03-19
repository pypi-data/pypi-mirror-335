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

from rameau.core import OverflowParameters, Parameter

class TestOverflowParameters(unittest.TestCase):
    def setUp(self):
        self.ref = Parameter(value=0.3, lower=0.1, upper=0.5, opti=True, sameas=1)
        self.refs = {
            'halflife':self.ref,
            'threshold':self.ref,
            'loss':'loss'
        }
        self.instances = {
            'halflife':Parameter,
            'threshold':Parameter,
            'loss':str
        }

    def test_properties_instances(self):
        foo = OverflowParameters(**self.refs)
        for key in OverflowParameters._computed_attributes:
            with self.subTest(key):
                self.assertIsInstance(getattr(foo, key), self.instances[key])
    
    def test_properties_values(self):
        foo = OverflowParameters(**self.refs)
        for key in OverflowParameters._computed_attributes:
            self.assertEqual(foo[key], self.refs[key])

    def test_init_type_error(self):
        class DummyType:
            pass
        for key in OverflowParameters._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    OverflowParameters(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = OverflowParameters(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)