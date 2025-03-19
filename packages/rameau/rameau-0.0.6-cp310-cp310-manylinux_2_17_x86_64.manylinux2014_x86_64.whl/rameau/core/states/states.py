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
Model states.
"""

from __future__ import annotations
from rameau.wrapper import CStates
from rameau.core._utils import _FloatDescriptor

from rameau.core._abstract_wrapper import AbstractWrapper

class States(AbstractWrapper):
    """Model states.

    Parameters
    ----------
    h_thornthwaite: `float`, optional
        Water level (mm) in the soil reservoir using the Thornthwaite method.
        See `ThornthwaiteReservoir` for details.

    h_progressive: `float`, optional
        Water level (mm) in the soil reservoir using the GR3J method.
        See `ProgressiveReservoir` for details.

    h_transfer: `float`, optional
        Water level (mm) in the transfer reservoir.
        See `TransferReservoir` for details.

    h_snow: `float`, optional
        Snow water equivalent (mm) of the snow pack.
        See `SnowReservoir` for details.

    h_pump_riv: `float`, optional

    h_pump_gw: `float`, optional

    gm_pump_riv: `float`, optional

    gm_pump_gw: `float`, optional

    r_snow: `float`, optional
        Water retention (-) in the snow pack.
        See `SnowReservoir` for details.

    h_groundwater: `list`, optional
        Water level (mm) in the groundwater reservoirs.
        See `Groundwater` for details.
    
    q_local: `list`, optional
        Total water level (mm) produced locally. 

    q_outlet: `list`, optional
        Historical riverflow (:math:`m^{3}.s^{-1}`) produced at the
        watershed outlet.
    
    Returns
    -------
    `States`
    """
    _computed_attributes = (
        "h_thornthwaite", "h_progressive", "h_transfer",
        "h_snow", "r_snow", "h_groundwater",
        "h_pump_riv", "h_pump_gw", "gm_pump_riv", "gm_pump_gw",
        "q_local", "q_outlet"
    )
    _c_class = CStates
    h_thornthwaite: float = _FloatDescriptor(0)
    h_progressive: float  = _FloatDescriptor(1)
    h_transfer: float  = _FloatDescriptor(2)
    h_snow: float  = _FloatDescriptor(3)
    r_snow: float  = _FloatDescriptor(4)
    h_pump_riv: float  = _FloatDescriptor(5)
    h_pump_gw: float  = _FloatDescriptor(6)
    gm_pump_riv: float  = _FloatDescriptor(7)
    gm_pump_gw: float  = _FloatDescriptor(8)

    def __init__(
            self,
            h_thornthwaite: float = 0.0,
            h_progressive: float = 0.0,
            h_transfer: float = 0.0,
            h_snow: float = 0.0,
            r_snow: float = 0.0,
            h_pump_riv: float = 0.0,
            h_pump_gw: float = 0.0,
            gm_pump_riv: float = 0.0,
            gm_pump_gw: float = 0.0,
            h_groundwater: list[float] = [0.0],
            q_local: list[float] = [0.0, 0.0],
            q_outlet: list[float] = [0.0, 0.0]
        ) -> None: 
        self._init_c()

        self.h_thornthwaite = h_thornthwaite
        self.h_progressive = h_progressive
        self.h_transfer = h_transfer
        self.h_snow = h_snow
        self.r_snow = r_snow
        self.h_pump_riv = h_pump_riv
        self.h_pump_gw = h_pump_gw
        self.gm_pump_riv = gm_pump_riv
        self.gm_pump_gw = gm_pump_gw
        self.h_groundwater = h_groundwater
        self.q_local = q_local
        self.q_outlet = q_outlet
    
    @property
    def h_groundwater(self) -> list[float]:
        return self._m.getArray(0)

    @h_groundwater.setter
    def h_groundwater(self, v: list[float]) -> None:
        if v:
            self._m.setArray(v, 0)

    @property
    def q_local(self) -> list[float]:
        return self._m.getArray(1)

    @q_local.setter
    def q_local(self, v: list[float]) -> None:
        if v:
            if len(v) < 2:
                v = [0 for i in range(2 - len(v))] + v
            self._m.setArray(v, 1)

    @property
    def q_outlet(self) -> list[float]:
        return self._m.getArray(2)

    @q_outlet.setter
    def q_outlet(self, v: list[float]) -> None:
        if v:
            if len(v) < 2:
                v = [0 for i in range(2 - len(v))] + v
            self._m.setArray(v, 2)