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

from rameau.core import Parameter, OverflowParameters, TransferReservoir

class TestTransferReservoir(unittest.TestCase):
    def setUp(self):
        ref = Parameter(value=0.3, lower=0.1, upper=0.5, opti=True, sameas=1)
        overflow = OverflowParameters(threshold=ref, halflife=ref)
        self.refs = {
            "h":0.2,
            "halflife":ref, 
            "runsee": ref,
            "overflow":overflow
        }

    def test_is_instance(self):
        foo = TransferReservoir()
        self.assertIsInstance(foo, TransferReservoir)

    def test_properties_instances(self):
        instances = {
            "h":float,
            "halflife":Parameter, 
            "runsee": Parameter,
            "overflow": OverflowParameters
        }
        for key in TransferReservoir._computed_attributes:
            with self.subTest(key):
                foo = TransferReservoir(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])
    
    def test_properties_values(self):
        foo = TransferReservoir(**self.refs)
        for key in TransferReservoir._computed_attributes:
            if type(self.refs[key]) is float:
                self.assertAlmostEqual(foo[key], self.refs[key])
            else:
                self.assertEqual(foo[key], self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in TransferReservoir._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    TransferReservoir(**{key:DummyType()})
    
    def test_pickle(self):
        import pickle
        foo = TransferReservoir(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)

    def test_transfer(self):
        res = TransferReservoir(
            halflife=Parameter(10),
            runsee=Parameter(150),
            h=120,
        )
        toto = res.transfer(200)
        self.assertEqual(
            toto,
            {
                'runoff':1.5449810028076172,
                'seepage':0.7267780303955078,
                'overflow':0.0
            }
        )
        self.assertAlmostEqual(res.h, 317.728, places=3)