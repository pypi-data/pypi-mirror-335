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

from rameau.core.states import States

class TestStates(unittest.TestCase):
    def setUp(self):
        self.refs = {
            "h_thornthwaite":0.2,
            "h_progressive":4,
            "h_transfer":3.2,
            "h_snow":3.1,
            "r_snow":3.1,
            "h_pump_riv":2.0,
            "h_pump_gw":2.1,
            "gm_pump_riv":2.2,
            "gm_pump_gw":2.3,
            "h_groundwater":[1, 2],
            "q_local":[3, 4],
            "q_outlet":[5, 6],
        }
    
    def test_is_instance(self):
        foo = States()
        self.assertIsInstance(foo, States)

    def test_properties_instances(self):
        instances = {
            "h_thornthwaite":float,
            "h_progressive":float,
            "h_transfer":float,
            "h_snow":float,
            "r_snow":float,
            "h_pump_riv":float,
            "h_pump_gw":float,
            "gm_pump_riv":float,
            "gm_pump_gw":float,
            "h_groundwater":list,
            "q_local":list,
            "q_outlet":list
        }
        foo = States(**self.refs)
        for key in States._computed_attributes:
            with self.subTest(key):
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = States(**self.refs)
        flist = [
            "h_thornthwaite", "h_progressive",
            "h_transfer", "h_snow", "r_snow",
            "h_pump_riv", "h_pump_gw",
            "gm_pump_riv", "gm_pump_gw",
        ]
        for key in flist:
            self.assertAlmostEqual(foo[key], self.refs[key], places=6)
        flist = [ "h_groundwater", "q_local", "q_outlet" ]
        for key in flist:
            self.assertListEqual(foo[key], self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in States._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    States(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = States(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)