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

from rameau.core import (
    RiverParameters, CorrectionParameters,
    ThornthwaiteReservoir, ProgressiveReservoir,
    TransferReservoir, Meteo, Parameter, Watershed
)
from rameau.core.snow import SnowReservoir, DegreeDayParameters
from rameau.core.pumping import Pumping, PumpingReservoir
from rameau.core.groundwater import GroundwaterParameters, GroundwaterReservoir
from rameau.core.forecast import ForecastCorrection, ForecastParameter

class TestWatershed(unittest.TestCase):
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

    def test_is_instance(self):
        foo = Watershed()
        self.assertIsInstance(foo, Watershed)

    def test_properties_instances(self):
        instances = {
            "name":str,
            "is_confluence":bool,
            "river":RiverParameters,
            "correction":CorrectionParameters,
            "thornthwaite_reservoir":ThornthwaiteReservoir,
            "progressive_reservoir":ProgressiveReservoir,
            "transfer_reservoir":TransferReservoir,
            "snow_reservoir":SnowReservoir,
            "pumping":Pumping,
            "groundwater":GroundwaterParameters,
            "meteo":Meteo,
            "forecast_correction":ForecastCorrection
        }
        for key in Watershed._computed_attributes:
            with self.subTest(key):
                foo = Watershed(**{key:self.refs[key]})
                self.assertIsInstance(getattr(foo, key), instances[key])

    def test_properties_values(self):
        foo = Watershed(
            **{
                key:self.refs[key]
                for key in Watershed._computed_attributes
            }
        )
        for key, value in foo.items():
            with self.subTest(key):
                self.assertEqual(value, self.refs[key])
    
    def test_init_type_error(self):
        class DummyType:
            pass
        for key in Watershed._computed_attributes:
            with self.subTest(key):
                with self.assertRaises(TypeError):
                    Watershed(**{key:DummyType()})

    def test_pickle(self):
        import pickle
        foo = Watershed(
            **{
                key:self.refs[key]
                for key in Watershed._computed_attributes
            }
        )
        foo_data = pickle.dumps(foo)
        foo_new = pickle.loads(foo_data)
        self.assertEqual(foo, foo_new)
    