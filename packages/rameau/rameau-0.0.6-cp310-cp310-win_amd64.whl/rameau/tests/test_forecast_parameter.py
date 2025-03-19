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
import datetime

from rameau.core.forecast import ForecastParameter

class TestForecastParameter(unittest.TestCase):
    def setUp(self):
        self.refs = {
            'halflife':1,
            #'kalman_date':datetime.datetime(2002, 1, 1)
        }

    def test_properties_instances(self):
        instances = {
            'halflife':float,
            #'kalman_date':datetime.datetime,
        }
        foo = ForecastParameter(**self.refs)
        for key in ForecastParameter._computed_attributes:
            with self.subTest(key):
                self.assertIsInstance(getattr(foo, key), instances[key])

    def test_properties_values(self):
        foo = ForecastParameter(**self.refs)
        for key, value in self.refs.items():
            with self.subTest(key):
                self.assertEqual(getattr(foo, key), value)
    
    def test_default_keywords(self):
        foo = ForecastParameter()
        self.assertEqual(foo.halflife, 0.0)
        #self.assertEqual(foo.kalman_date, None)
    
    def test_type_error(self):
        class DummyType:
            pass
        for key in ForecastParameter._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    ForecastParameter(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        p = ForecastParameter(**self.refs)
        p_data = pickle.dumps(p)
        p_new = pickle.loads(p_data)
        self.assertEqual(p, p_new)
