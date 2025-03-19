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
import datetime
import unittest
from rameau.core.settings import SpinupSettings, SimulationSettings

class TestSimulationSettings(unittest.TestCase):
    def setUp(self):
        self.refs = {
            "name": "foo",
            "starting_date":datetime.datetime(2000, 1, 1),
            "spinup_settings":SpinupSettings(
                cycles=1,
                starting_date=datetime.datetime(2001, 1, 1),
                ending_date=datetime.datetime(2001, 1, 1)
            )
        }

    def test_properties_instances(self):
        instances = {
            "name":str,
            "starting_date":datetime.datetime,
            "spinup_settings":SpinupSettings,
        }
        for key in SimulationSettings._computed_attributes:
            with self.subTest(key):
                foo = SimulationSettings(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])

    def test_properties_values(self):
        foo = SimulationSettings(
            **{
                key:self.refs[key]
                for key in SimulationSettings._computed_attributes
            }
        )
        for key, value in foo.items():
            self.assertEqual(value, self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in SimulationSettings._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    SimulationSettings(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = SimulationSettings(
            **{
                key:self.refs[key]
                for key in SimulationSettings._computed_attributes
            }
        )
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)
    