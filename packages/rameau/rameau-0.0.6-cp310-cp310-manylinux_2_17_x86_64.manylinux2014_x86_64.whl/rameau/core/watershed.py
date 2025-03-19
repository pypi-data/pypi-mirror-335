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
"""
Watershed.
"""
from typing import Union, Optional

from rameau.wrapper import CWatershed

from rameau.core import (
    RiverParameters, CorrectionParameters,
    ThornthwaiteReservoir, ProgressiveReservoir,
    TransferReservoir, Meteo
)
from rameau.core.snow import SnowReservoir
from rameau.core.pumping import Pumping
from rameau.core.groundwater import GroundwaterParameters
from rameau.core.forecast import ForecastCorrection
from rameau.core._abstract_wrapper import AbstractWrapper
from rameau.core._utils import _build_type, wrap_property

class _IntDescriptor():
    """Integer descriptor."""
    def __init__(self, id):
        self._id = id

    def __get__(self, instance, type=None) -> float:
        return instance._m.getInt(self._id)

class Watershed(AbstractWrapper):
    """Watershed.
    
    Parameters
    ----------
    name: `str`, optional
        Watershed name.

    correction: `dict` or `CorrectionParameters`, optional
        Correction terms used when running a simulation.
        See `CorrectionParameters` for details.

    thornthwaite_reservoir: `dict` or `ThornthwaiteReservoir`, optional
        Soil reservoir using the Thornthwaite soil approach.
        See `ThornthwaiteReservoir` for details.

    progressive_reservoir: `dict` or `ProgressiveReservoir`, optional
        Soil reservoir using the GR3 soil approach.
        See `ProgressiveReservoir` for details.

    transfer_reservoir: `dict` or `TransferReservoir`, optional
        Transfer reservoir. See `TransferReservoir` for details.

    snow_reservoir: `dict` or `SnowReservoir`, optional
        Snow reservoir. See `SnowReservoir` for details.

    river: `dict` or `River`, optional
        River parameters. See `RiverParameters` for details.

    groundwater: `dict` or `GroundwaterParameters`, optional
        Groundwater parameters. See `GroundwaterParameters` for details.

    pumping: `dict` or `Pumping`, optional
        Pumping parameters. See `Pumping` for details.

    meteo: dict or `Meteo`, optional
        Parameters related to the meteorological inputs.
        See `Meteo` for details.

    forecast_correction: dict or `ForecastCorrection`, optional
        Forecast corrections. See `ForecastCorrection` for details.

    is_confluence: bool, optional
        True if the watershed is a confluence.
    
    Returns
    -------
    `Watershed`
    """

    _computed_attributes = (
        "name", "is_confluence", "river",
        "correction", "thornthwaite_reservoir",
        "progressive_reservoir", "transfer_reservoir",
        "snow_reservoir", "pumping", "groundwater",
        "meteo", "forecast_correction"
    )
    _c_class = CWatershed
    id: int = _IntDescriptor(0)
    strahler_order: int = _IntDescriptor(1)

    def __init__(
            self,
            name: str = '',
            correction: Optional[Union[dict, CorrectionParameters]] = None,
            thornthwaite_reservoir: Optional[Union[dict, ThornthwaiteReservoir]] = None,
            progressive_reservoir: Optional[Union[dict, ProgressiveReservoir]] = None,
            transfer_reservoir: Optional[Union[dict, TransferReservoir]] = None,
            snow_reservoir: Optional[Union[dict, SnowReservoir]] = None,
            river: Optional[Union[dict, RiverParameters]] = None,
            groundwater: Optional[Union[dict, GroundwaterParameters]] = None,
            pumping: Optional[Union[dict, Pumping]] = None,
            meteo: Optional[Union[dict, Meteo]] = None,
            forecast_correction: Optional[Union[dict, ForecastCorrection]] = None,
            is_confluence: bool = False,
        ) -> None: 
        self._init_c()

        self.name = name
        self.is_confluence = is_confluence

        if river is not None:
            self.river = _build_type(river, RiverParameters)
        if correction is not None:
            self.correction = _build_type(correction, CorrectionParameters)
        if thornthwaite_reservoir is not None:
            self.thornthwaite_reservoir = _build_type(
                thornthwaite_reservoir, ThornthwaiteReservoir
            )
        if progressive_reservoir is not None:
            self.progressive_reservoir = _build_type(
                progressive_reservoir, ProgressiveReservoir
            )
        if transfer_reservoir is not None:
            self.transfer_reservoir = _build_type(
                transfer_reservoir, TransferReservoir
            )
        if snow_reservoir is not None:
            self.snow_reservoir = _build_type(
                snow_reservoir, SnowReservoir
            )
        if pumping is not None:
            self.pumping = _build_type(
                pumping, Pumping
            )
        if groundwater is not None:
            self.groundwater = _build_type(
                groundwater, GroundwaterParameters
            )
        else:
            self.groundwater = GroundwaterParameters()
        if meteo is not None:
            self.meteo = _build_type(
                meteo, Meteo
            )
        if forecast_correction is not None:
            self.forecast_correction = _build_type(
                forecast_correction, ForecastCorrection
            )
        else:
            self.forecast_correction = ForecastCorrection()
    
    @property
    def name(self) -> str:
        return self._m.getName()

    @name.setter
    def name(self, v: str) -> None:
        self._m.setName(v)

    @property
    @wrap_property(RiverParameters)
    def river(self) -> RiverParameters:
        return self._m.getRiver()

    @river.setter
    def river(self, v: RiverParameters) -> None:
        self._m.setRiver(v._m)

    @property
    @wrap_property(CorrectionParameters)
    def correction(self) -> CorrectionParameters:
        return self._m.getCorrection()

    @correction.setter
    def correction(self, v: CorrectionParameters) -> None:
        self._m.setCorrection(v._m)

    @property
    @wrap_property(ThornthwaiteReservoir)
    def thornthwaite_reservoir(self) -> ThornthwaiteReservoir:
        return self._m.getThornthwaiteReservoir()

    @thornthwaite_reservoir.setter
    def thornthwaite_reservoir(self, v: ThornthwaiteReservoir) -> None:
        self._m.setThornthwaiteReservoir(v._m)

    @property
    @wrap_property(ProgressiveReservoir)
    def progressive_reservoir(self) -> ProgressiveReservoir:
        return self._m.getProgressiveReservoir()

    @progressive_reservoir.setter
    def progressive_reservoir(self, v: ProgressiveReservoir) -> None:
        self._m.setProgressiveReservoir(v._m)

    @property
    @wrap_property(TransferReservoir)
    def transfer_reservoir(self) -> TransferReservoir:
        return self._m.getTransferReservoir()

    @transfer_reservoir.setter
    def transfer_reservoir(self, v: TransferReservoir) -> None:
        self._m.setTransferReservoir(v._m)

    @property
    @wrap_property(SnowReservoir)
    def snow_reservoir(self) -> SnowReservoir:
        return self._m.getSnowReservoir()

    @snow_reservoir.setter
    def snow_reservoir(self, v: SnowReservoir) -> None:
        self._m.setSnowReservoir(v._m)

    @property
    @wrap_property(Pumping)
    def pumping(self) -> Pumping:
        return self._m.getPumping()

    @pumping.setter
    def pumping(self, v: Pumping) -> None:
        self._m.setPumping(v._m)

    @property
    @wrap_property(GroundwaterParameters)
    def groundwater(self) -> GroundwaterParameters:
        return self._m.getGroundwater()

    @groundwater.setter
    def groundwater(self, v: GroundwaterParameters) -> None:
        self._m.setGroundwater(v._m)

    @property
    @wrap_property(Meteo)
    def meteo(self) -> Meteo:
        return self._m.getMeteo()

    @meteo.setter
    def meteo(self, v: Meteo) -> None:
        self._m.setMeteo(v._m)

    @property
    @wrap_property(ForecastCorrection)
    def forecast_correction(self) -> ForecastCorrection:
        return self._m.getForecastCorrection()

    @forecast_correction.setter
    def forecast_correction(self, v: ForecastCorrection) -> None:
        self._m.setForecastCorrection(v._m)

    @property
    def is_confluence(self) -> bool:
        return self._m.getIsConfluence()

    @is_confluence.setter
    def is_confluence(self, v: bool) -> None:
        self._m.setIsConfluence(v)
