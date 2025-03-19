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
Simulation settings.
"""

from typing import Optional, Union
import datetime

from rameau.wrapper import CSimulationSettings

from rameau.core._abstract_wrapper import AbstractWrapper
from rameau.core._utils import _build_type, wrap_property, _get_datetime, _set_datetime
from rameau.core.settings import SpinupSettings

class SimulationSettings(AbstractWrapper):
    """Simulation settings.
    
    Parameters
    ----------
    name: `str`, optional
        Name of the simulation. This name is used to name to the output
        directory. If omitted, default is "simulation".

    starting_date: `datetime.datetime`, optional
        Starting date of the simulation. This date needs to be contained in the
        rainfall input data. If None, default is the starting date of
        the rainfall input data. The simulation run will start from this
        date and will stop at the end of the meteorological input data.

    spinup_settings: `dict` or `SpinupSettings`, optional
        Spinup settings of the simulation. See `SpinupSettings` for details.

    Returns
    -------
    `SimulationSettings`
    """

    _computed_attributes = "name", "starting_date", "spinup_settings"
    _c_class = CSimulationSettings

    def __init__(
            self,
            name: str = 'simulation',
            starting_date: Optional[datetime.datetime] = None,
            spinup_settings: Optional[Union[dict, SpinupSettings]] = None,
        ) -> None: 
        self._init_c()

        self.name = name

        if starting_date is not None:
            self.starting_date = starting_date
        else:
            self.starting_date = datetime.datetime(9999, 12, 31)
        
        if spinup_settings is not None:
            self.spinup_settings = _build_type(spinup_settings, SpinupSettings)
        else:
            self.spinup_settings = SpinupSettings()

    @property
    @_get_datetime
    def starting_date(self) -> datetime.datetime:
        """Starting date of the simulation.

        Returns
        -------
        `datetime.datetime`
        """
        return self._m.getStartingDate()

    @starting_date.setter
    @_set_datetime
    def starting_date(self, v: datetime.datetime) -> None:
        self._m.setStartingDate(v)

    @property
    def name(self) -> str:
        """Name of the simulation.

        Returns
        -------
        `str`
        """
        return self._m.getName()

    @name.setter
    def name(self, v: str) -> None:
        self._m.setName(v)

    @property
    @wrap_property(SpinupSettings)
    def spinup_settings(self) -> SpinupSettings:
        """Spinup settings of the simulation. See `SpinupSettings` for details.

        Returns
        -------
        `SpinupSettings`
        """
        return self._m.getSpinupSettings()

    @spinup_settings.setter
    def spinup_settings(self, v: SpinupSettings) -> None:
        self._m.setSpinupSettings(v._m)