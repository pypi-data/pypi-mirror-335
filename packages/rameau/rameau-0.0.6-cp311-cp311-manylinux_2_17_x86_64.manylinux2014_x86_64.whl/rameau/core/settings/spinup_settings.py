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
Spinup settings.
"""

from typing import Optional
import datetime

from rameau.wrapper import CSpinupSettings

from rameau.core._abstract_wrapper import AbstractWrapper
from rameau.core._utils import _get_datetime, _set_datetime

class SpinupSettings(AbstractWrapper):
    """Spinup settings.
    
    Parameters
    ----------
    cycles: `int`, optional
        Number of initialisation period cycles. Default is 0.

    starting_date: `datetime.datetime`, optional
        Starting date of the initialisation period. Default is the
        starting date of the rainfall input data.

    ending_date: `datetime.datetime`, optional
        Ending date of the initialisation period. An error will be returned if
        the provided date is sooner than the spinup starting date. Default is
        the date preceding the `SimulationSettings.starting_date`.

    Returns
    -------
    `SpinupSettings`

    Examples
    --------
    Just a dummy example.

    >>> data = pd.DataFrame(np.random.rand(25))
    >>> model = rm.Model(
    ...     tree=dict(watersheds=[{}]),
    ...     inputs=dict(
                rainfall=data,
                pet=data,
                date=pd.date_range("2000-01-01", "2000-01-25")),
            simulation_settings=dict(
                starting_date=datetime.datetime(2000, 1, 4)
                spinup_settings=dict(
                    starting_date=datetime.datetime(2000, 1, 1)
                    ending_date=datetime.datetime(2000, 1, 3),
                    cycles=2
                )
            )
    ... )
    >>> for key, val in model.simulation_setttings.spinup_settings.item():
    ...     print(key, ":", val)
    cycles = 2
    starting_date = 2000-01-01 00:00:00
    ending_date = 2000-01-03 00:00:00
    
    Let's define a new model but without simulation settings.

    >>> model = rm.Model(
    ...     tree=dict(watersheds=[{}]),
    ...     inputs=dict(
                rainfall=data,
                pet=data,
                date=pd.date_range("2000-01-01", "2000-01-25")),
    ... )
    >>> for key, val in model.simulation_setttings.spinup_settings.item():
    ...     print(key, ":", val)
    cycles = 0
    starting_date = None
    ending_date = None

    The starting date and ending date of the spinup settings attached to the
    model are not defined. If we run a simulation, these dates should be
    initialised.

    >>> sim = model.run_simulation()
    >>> for key, val in sim.simulation_setttings.spinup_settings.item():
    ...     print(key, ":", val)
    cycles = 0
    starting_date = None
    ending_date = None
    
    What's wrong? Spinup dates are initiliased only when cycles > 0. Let's
    change that:

    >>> model.simulation_settings.spinup_settings.cycles = 1
    >>> sim = model.run_simulation()
    Traceback (most recent call last):
    ...
    RuntimeError: Spinup ending date older than spinup starting date
    >>> print(sim.simulation_settings.starting_date)
        2000-01-01 00:00:00
    
    The method throws an error. Try defining a simulation starting date
    one day later.

    >>> model.simulation_settings.starting_date = datetime.datetime(2000, 1, 2)
    >>> sim = model.run_simulation()
    >>> for key, val in sim.simulation_setttings.spinup_settings.item():
    ...     print(key, ":", val)
    cycles = 1
    starting_date = 2000-01-01 00:00:00
    ending_date = 2000-01-01 00:00:00
    
    Now it works. Default value for spinup starting date is 2000-01-01 (first
    date of rainfall data). If the simulation starting date is also equal to
    2000-01-01, then the spinup ending date is 1999-12-31, which is sooner than
    the default spinup starting date. So we need to change the simulation
    starting date to 2000-01-02 for a working initialisation period of 1 day.
    """

    _computed_attributes = "cycles", "starting_date", "ending_date"
    _c_class = CSpinupSettings

    def __init__(
            self,
            cycles: int = 0,
            starting_date: Optional[datetime.datetime] = None,
            ending_date: Optional[datetime.datetime] = None
        ) -> None: 
        self._init_c()

        self.cycles = cycles

        if starting_date is not None:
            self.starting_date = starting_date
        else:
            self.starting_date = datetime.datetime(9999, 12, 31)

        if ending_date is not None:
            self.ending_date = ending_date
        else:
            self.ending_date = datetime.datetime(9999, 12, 31)

    @property
    @_get_datetime
    def starting_date(self) -> datetime.datetime:
        """Starting date of the initialisation period.

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
    @_get_datetime
    def ending_date(self) -> datetime.datetime:
        """Ending date of the initialisation period.

        Returns
        -------
        `datetime.datetime`
        """
        return self._m.getEndingDate()

    @ending_date.setter
    @_set_datetime
    def ending_date(self, v: datetime.datetime) -> None:
        self._m.setEndingDate(v)

    @property
    def cycles(self) -> int:
        """Number of spinup cycles.

        Returns
        -------
        `int`
        """
        return self._m.getCycles()

    @cycles.setter
    def cycles(self, v: int) -> None:
        self._m.setCycles(v)