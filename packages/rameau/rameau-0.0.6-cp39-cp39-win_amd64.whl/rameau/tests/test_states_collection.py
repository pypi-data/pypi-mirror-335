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
import tempfile
import pandas as pd

from rameau.core.states import States, StatesCollection

txt_ref_to_file = """                 ID      h_thornthwaite       h_progressive          h_transfer              h_snow              r_snow          h_pump_riv           h_pump_gw         gm_pump_riv          gm_pump_gw     h_groundwater.1     h_groundwater.2           q_local.1           q_local.2          q_outlet.1          q_outlet.2          q_outlet.3
                  1             0.10000             0.00000             0.20000             0.00000             0.00000             0.00000             0.00000             0.00000             0.00000             0.30000             0.40000             0.00000             0.45000             0.60000             0.70000             0.80000
                  2             0.00000             1.10000             1.20000             0.00000             0.00000             0.00000             0.00000             0.00000             0.00000             1.30000             0.00000             0.50000             0.60000             0.00000             0.00000             0.00000
"""

class TestStatesCollection(unittest.TestCase):
    def setUp(self):
        self.refs = {
            "states":[
                States(
                    h_thornthwaite=0.1,
                    h_transfer=0.2,
                    h_groundwater=[0.3, 0.4],
                    q_local=[0.45],
                    q_outlet=[0.6, 0.7, 0.8]
                ),
                States(
                    h_progressive=1.1,
                    h_transfer=1.2,
                    h_groundwater=[1.3],
                    q_local=[0.5, 0.6]
                ),
            ]
        }

    def test_is_instance(self):
        foo = StatesCollection(**self.refs)
        self.assertIsInstance(foo, StatesCollection)

    def test_properties_instances(self):
        instances = { "states":list, }
        foo = StatesCollection(**self.refs)
        for key in StatesCollection._computed_attributes:
            with self.subTest(key):
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = StatesCollection(**self.refs)
        self.assertListEqual(foo["states"], self.refs["states"])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in StatesCollection._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    StatesCollection(**{key:DummyType()})
    
    def test_to_file(self):
        foo = StatesCollection(**self.refs)
        with tempfile.TemporaryDirectory() as tmpdirname:
            name = f"{tmpdirname}/foo"
            foo.to_file(f"{tmpdirname}/foo")
            with open(name) as f:
                txt = f.read()
                self.assertEqual(txt_ref_to_file.strip(), txt.strip())
    
    def test_from_file(self):
        ref = StatesCollection(**self.refs)
        with tempfile.TemporaryDirectory() as tmpdirname:
            name = f"{tmpdirname}/foo"
            with open(name, 'w') as f:
                f.write(txt_ref_to_file)
            foo = StatesCollection.from_file(name)
            keys = ["h_transfer", "q_local"]
            for key in keys:
                with self.subTest(key):
                    for i in range(2):
                        self.assertEqual(
                            getattr(ref.states[i], key),
                            getattr(foo.states[i], key),
                        )

    
    def test_pickle(self):
        import pickle
        foo = StatesCollection(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)