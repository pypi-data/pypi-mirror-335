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

from rameau.core.forecast import ForecastCorrection, ForecastParameter

class TestForecastCorrection(unittest.TestCase):
    def setUp(self):
        self.ref = ForecastParameter(halflife=1.3)
        self.refs = {
            #'da_priority':'watertable',
            'river':self.ref,
            'groundwater':self.ref
        }

    def test_properties_instances(self):
        instances = {
            #'da_priority':str,
            'river':ForecastParameter,
            'groundwater':ForecastParameter
        }
        foo = ForecastCorrection(**self.refs)
        for key in ForecastCorrection._computed_attributes:
            with self.subTest(key):
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = ForecastCorrection(**self.refs)
        for key in ForecastCorrection._computed_attributes:
            self.assertEqual(foo[key], self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in ForecastCorrection._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    ForecastCorrection(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = ForecastCorrection(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)