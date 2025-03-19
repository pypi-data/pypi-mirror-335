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
Forecast settings.
"""

from __future__ import annotations
from typing import Union, Optional, Literal
import datetime

from rameau.wrapper import CForecastSettings

from rameau.core._abstract_wrapper import AbstractWrapper
from rameau.core._utils import _check_literal, _set_datetime, _get_datetime

class ForecastSettings(AbstractWrapper):
    """
    Forecast settings.
    
    Parameters
    ----------
    emission_date: `datetime.datetime`, optional
        The date and time on which to issue a forecast.

    scope: `datetime.timedelta`, optional
        The duration for which to run the forecast. If not provided,
        set to one day.

    year_members: `list` or `ìnt`, optional
        The years to consider to form the forecast ensemble members.
        If not provided, all years in record are considered.

    correction: `str`, optional
        The approach to use to correct the initial conditions
        before issuing the forecast.

        =================  =========================================
        correction         description
        =================  =========================================
        ``'no'``           No correction is performed. This is
                           the default behaviour.

        ``'halflife'``     A correction using the observation
                           of the forecast variable on the issue
                           date is applied and then the correction
                           is gradually dampened overtime based on
                           a half-life parameter.

        ``'enkf'``         A correction using an ensemble Kalman
                           filter approach is used (experimental).
        =================  =========================================

    pumping_date: `datetime.datetime`, optional
        The date and time on which to start pumping.

    quantiles_output: `bool`, optional
        Whether to reduce the forecast ensemble members to specific
        climatology quantiles. If not provided, all years in record
        or years specified via the ``year_members`` parameter are
        considered. The quantiles can be chosen via the ``quantiles``
        parameter.

    quantiles: `list` or `int`, optional
        The climatology percentiles to include in the forecast ensemble
        members. Only considered if ``quantiles_output`` is set to
        `True`. By default, the percentiles computed are 10, 20, 50,
        80, and 90.

    norain: `bool`, optional
        Whether to include an extra ensemble member corresponding to
        a completely rain-free year. By default, this member is not
        included in the forecast output.
    
    Returns
    -------
    `ForecastSettings`
    """

    _computed_attributes = (
        "emission_date", "scope", "year_members", "correction", "pumping_date",
        "quantiles_output", "quantiles", "norain"
    )
    _c_class = CForecastSettings

    def __init__(
            self,
            emission_date: Optional[datetime.datetime] = None,
            scope: Optional[datetime.timedelta] = datetime.timedelta(1),
            year_members: Optional[list[int]] = None,
            correction: Optional[Literal["no", "halflife", "enkf"]] = None,
            pumping_date: Optional[datetime.datetime] = None,
            quantiles_output: bool = False,
            quantiles: Optional[list[int]] = [10, 20, 50, 80, 90],
            norain: bool = False
        ) -> None: 
        self._init_c()

        if emission_date is not None:
            self.emission_date = emission_date
        else:
            self.emission_date = datetime.datetime(9999, 12, 31)

        if pumping_date is not None:
            self.pumping_date = pumping_date
        else:
            self.pumping_date = datetime.datetime(9999, 12, 31)

        self.scope = scope

        if correction is None:
            correction = "no"
        _check_literal(
            correction, ["no", "halflife", "enkf"]
        )
        self.correction = correction

        if year_members is not None:
            if isinstance(year_members, list):
                self.year_members = year_members
            else:
                raise TypeError(f"Type {type(year_members)} not allowed.")

        self.quantiles_output = quantiles_output

        if isinstance(quantiles, list):
            self.quantiles = quantiles
        else:
            raise TypeError(f"Type {type(quantiles)} not allowed.")
        
        self.norain = norain

    @property
    @_get_datetime
    def emission_date(self) -> datetime.datetime:
        """The date and time on which to issue a forecast.

        Returns
        -------
        `datetime.datetime`
        """
        return self._m.getEmissionDate()

    @emission_date.setter
    @_set_datetime
    def emission_date(self, v: datetime.datetime) -> None:
        self._m.setEmissionDate(v)

    @property
    @_get_datetime
    def pumping_date(self) -> datetime.datetime:
        """The date and time on which to start pumping.

        Returns
        -------
        `datetime.datetime`
        """
        return self._m.getPumpingDate()

    @pumping_date.setter
    @_set_datetime
    def pumping_date(self, v: datetime.datetime) -> None:
        self._m.setPumpingDate(v)

    @property
    def scope(self) -> datetime.timedelta:
        """The duration for which to run the forecast.

        Returns
        -------
        `datetime.timedelta`
        """
        return self._m.getScope()

    @scope.setter
    def scope(self, v: datetime.timedelta) -> None:
        self._m.setScope(v)

    @property
    def year_members(self) -> list[int]:
        """The years to consider to form the forecast ensemble members.

        Returns
        -------
        `list`
        """
        return self._m.getYearMembers()

    @year_members.setter
    def year_members(self, v) -> None:
        if v:
            self._m.setYearMembers(v)

    @property
    def quantiles(self) -> list[float]:
        """The climatology percentiles to include in the forecast ensemble
        members.

        Returns
        -------
        `list`
        """
        return self._m.getQuantiles()

    @quantiles.setter
    def quantiles(self, v) -> None:
        if v:
            self._m.setQuantiles(v)

    @property
    def quantiles_output(self) -> bool:
        """Whether to reduce the forecast ensemble members to specific
        climatology quantiles.

        Returns
        -------
        `bool`
        """
        return self._m.getQuantilesOutput()

    @quantiles_output.setter
    def quantiles_output(self, v) -> None:
        self._m.setQuantilesOutput(v)

    @property
    def norain(self) -> bool:
        """Whether to include an extra ensemble member corresponding to
        a completely rain-free year.
        
        Returns
        -------
        `bool`
        """
        return self._m.getNoRain()

    @norain.setter
    def norain(self, v) -> None:
        self._m.setNoRain(v)

    @property
    def correction(self) -> str:
        """The approach to use to correct the initial conditions
        before issuing a forecast.

        Returns
        -------
        `str`
        """
        return self._m.getCorrection()

    @correction.setter
    def correction(self, v) -> None:
        self._m.setCorrection(v)