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
from rameau.core import Parameter

class TestParameter(unittest.TestCase):
    def test_instance(self):
        foo = Parameter()
        self.assertIsInstance(foo, Parameter)
    
    def test_default_keywords(self):
        default_values = {
            'value':0, 'opti':False, 'lower':0, 'upper':0
        }
        foo = Parameter()
        for key, value in default_values.items():
            with self.subTest(key):
                self.assertEqual(getattr(foo, key), value)
    
    def test_keyvalues(self):
        keyvalues = {
            'value':1.2, 'opti':True, 'lower':0.2, 'upper':15
        }
        foo = Parameter(**keyvalues)
        for key, value in keyvalues.items():
            with self.subTest(key):
                self.assertAlmostEqual(getattr(foo, key), value)

    def test_mixedkeywords(self):
        foo = Parameter(1.4, True, upper=1.2)
        self.assertAlmostEqual(foo.value, 1.4)
        self.assertEqual(foo.opti, True)
        self.assertAlmostEqual(foo.upper, 1.2)

    def test_toomanyargs(self):
        with self.assertRaises(TypeError):
            Parameter(1, False, 2, 5, 0, 5)

    def test_wrongkeyword(self):
        with self.assertRaises(TypeError):
            Parameter(truc=4)
    
    def test_type_error(self):
        keys = ['value', 'opti', 'lower', 'upper', 'sameas']
        for key in keys:
            with self.subTest(key):
                with self.assertRaises((TypeError, ValueError)):
                    Parameter(**{key:'foo'})
    
    def test_pickle(self):
        import pickle
        keyvalues = {
            'value':1.2, 'opti':True, 'lower':0.2, 'upper':15
        }
        p = Parameter(**keyvalues)
        p_data = pickle.dumps(p)
        p_new = pickle.loads(p_data)
        self.assertEqual(p, p_new)

    def test_assign_value(self):
        p = Parameter(value=0.2)
        p.value = 0.3
        self.assertAlmostEqual(p.value, 0.3)
