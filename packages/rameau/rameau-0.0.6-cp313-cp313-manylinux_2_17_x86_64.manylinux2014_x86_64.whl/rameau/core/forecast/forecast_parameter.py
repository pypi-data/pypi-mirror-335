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
Forecast correction parameters.
"""
import datetime

from rameau.wrapper import CForecastParameter

from rameau.core._abstract_wrapper import AbstractWrapper
from rameau.core._utils import _set_datetime, _get_datetime

class ForecastParameter(AbstractWrapper):
    """Forecast correction parameters.
    
    Parameters
    ----------
    halflife : `float`, optional
        Halflife value (time step).

    Returns
    -------
    `ForecastParameter`
    """

    _computed_attributes = 'halflife', #'kalman_date'
    _c_class = CForecastParameter

    def __init__(
            self,
            halflife: float = 0.0,
            #kalman_date: datetime.datetime = None
        ) -> None: 
        self._init_c()

        self.halflife = float(halflife)

        #if kalman_date is not None:
        #    self.kalman_date = kalman_date
        #else:
        #    self.kalman_date = datetime.datetime(9999, 12, 31)
    
    @property
    def halflife(self) -> float:
        """
        Halflife value (time step).

        Returns
        -------
        `float`
        """
        return self._m.getHalflife()
    
    @halflife.setter
    def halflife(self, v: float) -> None:
        self._m.setHalflife(v)

    #@property
    #@_get_datetime
    #def kalman_date(self) -> datetime.datetime:
    #    """
    #    Starting date for the ensemble kalman filter (experimental).

    #    Returns
    #    -------
    #    `datetime`
    #    """
    #    return self._m.getKalmanDate()

    #@kalman_date.setter
    #@_set_datetime
    #def kalman_date(self, v: datetime.datetime) -> None:
    #    self._m.setKalmanDate(v)


    
