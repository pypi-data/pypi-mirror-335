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
Parameters for assimilation schemes or output correction methods.
"""

from typing import Union, Optional, Literal

from rameau.wrapper import CForecastCorrection

from rameau.core.forecast import ForecastParameter
from rameau.core._abstract_wrapper import AbstractWrapper
from rameau.core._utils import _build_type, wrap_property

class ForecastCorrection(AbstractWrapper):
    """Parameters for assimilation schemes or output correction methods
    if simulated river flow and/or groundwater level are corrected
    with respect to observations when a forecast is issued.

    Parameters
    ----------
    river : `dict` or `ForecastParameter`, optional
        Forecast correction parameters for river flows.

    groundwater : `dict` or `ForecastParameter`, optional
        Forecast correction parameters for groundwater levels.
    
    Returns
    -------
    `ForecastCorrection`
    """

    _computed_attributes = 'river', 'groundwater'
    _c_class = CForecastCorrection

    def __init__(
            self,
            river: Optional[Union[dict, ForecastParameter]] = None,
            groundwater: Optional[Union[dict, ForecastParameter]] = None,
            #da_priority: Literal["riverflow", "watertable"] = 'riverflow',
        ) -> None: 
        self._init_c()

        #self.da_priority = da_priority

        if river is not None:
            self.river = _build_type(river, ForecastParameter)
        else:
            self.river = ForecastParameter()
        if groundwater is not None:
            self.groundwater = _build_type(groundwater, ForecastParameter)
        else:
            self.groundwater = ForecastParameter()
        
    #@property
    #def da_priority(self) -> str:
    #    """
    #    Priority variable when using ensemble kalman filter (experimental).

    #    Returns
    #    -------
    #    `str`
    #    """
    #    return self._m.getDAPriority()

    #@da_priority.setter
    #def da_priority(self, v: str) -> None:
    #    self._m.setDAPriority(v)

    @property
    @wrap_property(ForecastParameter)
    def river(self) -> ForecastParameter:
        """Forecast correction parameters for river flows.

        Returns
        -------
        `ForecastParameter`
        """
        return self._m.getRiver()

    @river.setter
    def river(self, v: ForecastParameter) -> None:
        self._m.setRiver(v._m)
    
    @property
    @wrap_property(ForecastParameter)
    def groundwater(self) -> ForecastParameter:
        """Forecast correction parameters for groundwater levels.

        Returns
        -------
        `ForecastParameter`
        """
        return self._m.getGroundwater()

    @groundwater.setter
    def groundwater(self, v: ForecastParameter) -> None:
        self._m.setGroundwater(v._m)



    
