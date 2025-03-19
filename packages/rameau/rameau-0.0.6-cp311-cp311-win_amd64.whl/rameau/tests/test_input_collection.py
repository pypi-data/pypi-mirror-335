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
import tempfile
from rameau.core import FilePaths
from rameau.core.inputs import Input, InputFormat, InputCollection
import datetime

class TestInputCollection(unittest.TestCase):
    def setUp(self):
        self.data = np.array([[1.2, 4], [2.2, 5], [3, 6.3]])
        self.dates=pd.date_range("2000-1-1", "2000-1-3")
        self.refs = {
            'rainfall': self.data,
            'pet': self.data,
            'snow': self.data,
            'temperature': self.data,
            'riverobs': self.data,
            'riverpumping': self.data,
            'groundwaterobs': self.data,
            'groundwaterpumping': self.data,
        }

    def test_properties_instances(self):
        instances = {
            'rainfall': Input,
            'pet': Input,
            'snow': Input,
            'temperature': Input,
            'riverobs': Input,
            'riverpumping': Input,
            'groundwaterobs': Input,
            'groundwaterpumping': Input,
            'file_paths':FilePaths,
            'input_format':InputFormat
        }
        foo = InputCollection(**{key:self.refs[key] for key in self.refs})
        for key in InputCollection._computed_attributes:
            with self.subTest(key):
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = InputCollection(**self.refs)
        for key in self.refs:
            with self.subTest(key):
                np.testing.assert_almost_equal(self.refs[key], foo[key].data, decimal=6)
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in InputCollection._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    InputCollection(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = InputCollection(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        keys = [
            'rainfall', 'pet', 'snow', 'temperature', 'riverobs', 'riverpumping',
            'groundwaterobs', 'groundwaterpumping'
        ]
        for key in keys:
            with self.subTest(key):
                np.testing.assert_almost_equal(foo[key].data, foo_new[key].data)
        self.assertEqual(foo["file_paths"], foo_new["file_paths"])
        self.assertEqual(foo.input_format, foo_new.input_format)
    
    def test_from_files(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = tmpdirname + '/foo'
            data = Input(
                data=np.array([[1.2, 4], [2.2, 5], [3, 6.3]]),
                dates=self.dates
            )
            with open(fname , 'w') as f:
                f.write("Header\n")
                np.savetxt(f, data.data)
            foo = InputCollection.from_files(
                rainfall=fname, pet=fname,
                input_format=InputFormat(
                    starting_date=datetime.datetime(2000, 1, 1)
                )
            )
            np.testing.assert_almost_equal(data.data, foo.rainfall.data, decimal=6)

    def test_ndarray_dates(self):
        foo = InputCollection(
            rainfall=self.data, pet=self.data, dates=self.dates
        )
        np.testing.assert_almost_equal(foo.rainfall.data, self.data, decimal=6)
        pd.testing.assert_index_equal(foo.rainfall.dates, self.dates)

    def test_dataframe(self):
        rainfall = pd.DataFrame(self.data)
        foo = InputCollection(
            rainfall=rainfall, pet=self.data, dates=self.dates
        )
        np.testing.assert_almost_equal(foo.rainfall.data, self.data, decimal=6)
        pd.testing.assert_index_equal(foo.rainfall.dates, self.dates)

    def test_dataframe_with_dates(self):
        rainfall = pd.DataFrame(self.data, index=self.dates)
        foo = InputCollection(
            rainfall=rainfall, pet=self.data, dates=self.dates
        )
        np.testing.assert_almost_equal(foo.rainfall.data, self.data, decimal=6)
        pd.testing.assert_index_equal(foo.rainfall.dates, self.dates)

    def test_groundwater_nan(self):
        data_in = np.array([[0.2, 0.4], [np.nan, 5], [3, 3]])
        fake_data = np.ones(data_in.shape)
        foo = InputCollection(
            fake_data, fake_data,
            groundwaterobs=data_in
        )
        data_in2 = np.array([[0.2, 0.4], [1e+20, 5], [3, 3]], dtype=np.float32)
        np.testing.assert_almost_equal(foo.groundwaterobs.data, data_in2)

    def test_river_nan(self):
        data_in = np.array([[0.2, 0.4], [np.nan, 5], [3, 3]])
        fake_data = np.ones(data_in.shape)
        foo = InputCollection(
            fake_data, fake_data,
            riverobs=data_in
        )
        data_in2 = np.array([[0.2, 0.4], [1e+20, 5], [3, 3]], dtype=np.float32)
        np.testing.assert_almost_equal(foo.riverobs.data, data_in2)
