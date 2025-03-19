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

from rameau.core import FilePaths

class TestFilePaths(unittest.TestCase):
    def setUp(self):
        self.ref = 'foé'

    def test_properties_instances(self):
        for key in FilePaths._computed_attributes:
            with self.subTest(key):
                foo = FilePaths(**{key:self.ref})
                self.assertIsInstance(getattr(foo, key), str)
    
    def test_properties_values(self):
        foo = FilePaths(
            **{
                key:self.ref
                for key in FilePaths._computed_attributes
            }
        )
        for key in FilePaths._computed_attributes:
            with self.subTest(key):
                self.assertEqual(foo[key], self.ref)
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in FilePaths._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    FilePaths(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = FilePaths(
            **{
                key:self.ref
                for key in FilePaths._computed_attributes
            }
        )
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)