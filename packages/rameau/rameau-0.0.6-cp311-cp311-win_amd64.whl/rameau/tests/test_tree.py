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

import numpy as np

from rameau.core import (
    RiverParameters, CorrectionParameters,
    ThornthwaiteReservoir, ProgressiveReservoir,
    TransferReservoir, Meteo, Parameter, Watershed, Tree
)
from rameau.core.snow import SnowReservoir, DegreeDayParameters
from rameau.core.pumping import Pumping, PumpingReservoir
from rameau.core.groundwater import GroundwaterParameters, GroundwaterReservoir
from rameau.core.forecast import ForecastCorrection, ForecastParameter

class TestTree(unittest.TestCase):
    def setUp(self):
        ref = Parameter(value=0.3, lower=0.1, upper=0.5, opti=True, sameas=1)
        self.refs= {
            "name":"foé",
            "is_confluence":True,
            "river":RiverParameters(
                area=ref, concentration_time=ref
            ),
            "correction":CorrectionParameters(
                rainfall=ref, pet=ref
            ),
            "thornthwaite_reservoir":ThornthwaiteReservoir(
                capacity=ref
            ),
            "progressive_reservoir":ProgressiveReservoir(
                capacity=ref
            ),
            "transfer_reservoir":TransferReservoir(
                halflife=ref, runsee=ref
            ),
            "snow_reservoir":SnowReservoir(
                melting=ref, retention=ref,
                degree_day=DegreeDayParameters(
                    coefficient=ref
                )
            ),
            "pumping":Pumping(
                river=PumpingReservoir(coefficient=ref),
                groundwater=PumpingReservoir(coefficient=ref)
            ),
            "groundwater":GroundwaterParameters(
                reservoirs=[
                    GroundwaterReservoir(
                        halflife_baseflow=ref,
                        exchanges=ref
                    )
                ],
            ),
            "meteo":Meteo(
                columns=[3, 5],
                weights=[1.2, 1.3]
            ),
            "forecast_correction":ForecastCorrection(
                river=ForecastParameter(halflife=0.2)
            )
        }
        watershed1 = Watershed(**self.refs)
        self.refs = {
            'watersheds':[watershed1],
        }

    def test_is_instance(self):
        foo = Tree(watersheds=[Watershed()])
        self.assertIsInstance(foo, Tree)

    def test_properties_instances(self):
        instances = {
            "watersheds":list,
            "connection":dict
        }
        foo = Tree(**self.refs)
        for key in Tree._computed_attributes:
            with self.subTest(key):
                self.assertIsInstance(getattr(foo, key), instances[key])

    def test_properties_values(self):
        foo = Tree(**self.refs)
        self.assertEqual(foo["watersheds"], self.refs["watersheds"])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in Tree._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    Tree(**{key:DummyType()})

    def test_pickle(self):
        import pickle
        foo = Tree(**self.refs)
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)

    def test_three_watershed(self):
        tree = Tree(
            watersheds=([
                    Watershed(),
                    Watershed(
                        groundwater=GroundwaterParameters(
                            reservoirs=[
                                GroundwaterReservoir(),
                                GroundwaterReservoir()
                            ]
                        )
                    ),
                    Watershed()
                ]
            ),
            connection={
                1:3,
                2:3,
                3:0,
            }
        )
        strahl = [1, 1, 2]
        gw_res = [1, 2, 1]
        for i in range(3):
            self.assertEqual(tree.watersheds[i].strahler_order, strahl[i])
            self.assertEqual(len(tree.watersheds[i].groundwater.reservoirs), gw_res[i])
    
    def test_three_watershed_dict(self):
        tree = Tree(
            watersheds=dict(
                {
                    10:Watershed(),
                    9:Watershed(
                        groundwater=GroundwaterParameters(
                            reservoirs=[
                                GroundwaterReservoir(),
                                GroundwaterReservoir()
                            ]
                        )
                    ),
                    14:Watershed()
                }
            ),
            connection={
                10:14,
                9:14,
                14:0
            }
        )
        strahl = [1, 1, 2]
        gw_res = [1, 2, 1]
        for i in range(3):
            self.assertEqual(tree.watersheds[i].strahler_order, strahl[i])
            self.assertEqual(len(tree.watersheds[i].groundwater.reservoirs), gw_res[i])
    
    def test_to_csv(self):
        tree = Tree(
            watersheds=dict(
                {
                    10:Watershed(name="foo"),
                    9:Watershed(
                        groundwater=GroundwaterParameters(
                            reservoirs=[
                                GroundwaterReservoir(),
                                GroundwaterReservoir()
                            ]
                        )
                    ),
                    14:Watershed(name='hého')
                }
            ),
            connection={
                10:14,
                9:14,
                14:0
            }
        )
        ref = (
            'Watershed Downstream\n'
            '9 14\n'
            '10 14\n'
            '14 0\n'
        )


        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = tmpdirname + '/foo'
            tree.to_csv(fname)
            with open(fname, 'r') as ff:
                self.assertEqual(ff.read(), ref)
    
    def test_from_csv(self):
        ref = (
            'Watershed Downstream\n'
            '10 14\n'
            '9 14\n'
            '14 0'
        )
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = tmpdirname + '/foo'
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(ref)
            tree = Tree.from_csv(
                fname,
                watersheds=dict(
                    {
                        10:Watershed(),
                        9:Watershed(
                            groundwater=GroundwaterParameters(
                                reservoirs=[
                                    GroundwaterReservoir(),
                                    GroundwaterReservoir()
                                ]
                            )
                        ),
                        14:Watershed()
                    }
                )
            )
            strahl = [1, 1, 2]
            gw_res = [1, 2, 1]
            for i in range(3):
                self.assertEqual(tree.watersheds[i].strahler_order, strahl[i])
                self.assertEqual(len(tree.watersheds[i].groundwater.reservoirs), gw_res[i])