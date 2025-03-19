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
import numpy as np
import pandas as pd
from rameau.core.inputs import Input

class TestInput(unittest.TestCase):
    def setUp(self):
        self.refs = {
            'data': np.array([[1, 4], [2, 5.2], [3, 6]]),
            'dates': pd.date_range("2000-1-1", "2000-1-3"),
            'nodata': 3
        }

    def test_input_nan(self):
        foo = Input(data=np.array([[np.nan, 2]]))
        np.testing.assert_array_equal(foo.data, np.array([[1e+20, 2]], dtype=np.float32))

    def test_properties_instances(self):
        instances = {
            "data": np.ndarray,
            "dates": pd.DatetimeIndex,
            "nodata": float
        }
        foo = Input(**{key:self.refs[key] for key in instances})
        for key in Input._computed_attributes:
            with self.subTest(key):
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = Input(**self.refs)
        np.testing.assert_array_almost_equal(
            self.refs["data"], foo["data"]
        )
        pd.testing.assert_index_equal(
            self.refs["dates"], foo["dates"]
        )
        self.assertEqual(self.refs["nodata"], foo["nodata"])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in Input._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    Input(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = Input(
            **{
                key:self.refs[key]
                for key in Input._computed_attributes
            }
        )
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        np.testing.assert_almost_equal(foo["data"], foo_new["data"])
        pd.testing.assert_index_equal(foo["dates"], foo_new["dates"])
        self.assertEqual(foo["nodata"], foo_new["nodata"])
    