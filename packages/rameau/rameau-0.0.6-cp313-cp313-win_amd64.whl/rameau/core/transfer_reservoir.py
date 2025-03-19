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
Transfer reservoir.
"""

from typing import Union, Optional

from rameau.wrapper import CTransferReservoir

from rameau.core.parameter import Parameter
from rameau.core import OverflowParameters
from rameau.core._abstract_wrapper import AbstractWrapper

from rameau._typing import ParameterType
from rameau.core._utils import _build_parameter, _build_type, wrap_property

class TransferReservoir(AbstractWrapper):
    """Transfer reservoir.
    
    Parameters
    ----------
    halflife : `dict` or `Parameter`, optional
        Half-life characterizing the exponential decay of the transfer
        reservoir water level (month).

    runsee : `dict` or `Parameter`, optional
        Water level value defining the partition between surface
        runoff and seepage (mm).

    overflow : `dict` or `OverflowParameters`, optional
        Overflow parameters.

    h : `float`
        Transfer reservoir water level (mm).

    Returns
    -------
    `TransferReservoir`

    Examples
    --------
    >>> s = rm.TransferReservoir(
    ...     halflife=15, runsee=200, overflow=dict(threshold=300, halflife=20)
    ...     h=100
    ... )
    >>> s.h
    100.0
    >>> s.transfer(250)
    {'runoff': 0.9268571138381958,
     'seepage': 0.5307539701461792,
     'overflow': 1.70318603515625}
    >>> s.h
    348.5423889160156
    """

    _computed_attributes = "halflife", "runsee", "overflow", "h"
    _c_class = CTransferReservoir

    def __init__(
        self,
        halflife: ParameterType = None,
        runsee: ParameterType = None,
        overflow: Optional[Union[dict, OverflowParameters]] = None,
        h: float = 0
    ) -> None: 
        self._init_c()

        if halflife is not None:
            self.halflife = _build_parameter(halflife)
        if runsee is not None:
            self.runsee = _build_parameter(runsee)
        if overflow is not None:
            self.overflow = _build_type(overflow, OverflowParameters)
        
        self.h = h
    
    @property
    @wrap_property(Parameter)
    def halflife(self) -> Parameter:
        """Half-life characterizing the exponential decay of the transfer
        reservoir water level (month).

        Returns
        -------
        `Parameter`
        """
        return self._m.getHalflife()

    @halflife.setter
    def halflife(self, v: Parameter) -> None:
        self._m.setHalflife(v._m)

    @property
    @wrap_property(Parameter)
    def runsee(self) -> Parameter:
        """Water level value defining the partition between surface
        runoff and seepage (mm).

        Returns
        -------
        `Parameter`
        """
        return self._m.getRunsee()

    @runsee.setter
    def runsee(self, v: Parameter) -> None:
        self._m.setRunsee(v._m)

    @property
    @wrap_property(OverflowParameters)
    def overflow(self) -> OverflowParameters:
        """Overflow parameters.
        
        Returns
        -------
        `OverflowParameters`
        """
        return self._m.getOverflow()

    @overflow.setter
    def overflow(self, v) -> None:
        self._m.setOverflow(v._m)

    @property
    def h(self) -> float:
        """Transfer reservoir water level (mm).

        Returns
        -------
        `float`
        """
        return self._m.getH()

    @h.setter
    def h(self, v: float) -> None:
        self._m.setH(v)

    def transfer(
            self,
            effective_rainfall: float,
            deltat: float = 86400.
        ) -> dict:
        r"""Transfer function.

        Parameters
        ----------
        effective_rainfall : `float`
            Effective rainfall (mm).
        
        deltat : `float`, optional
            Time step duration (s).

        Returns
        -------
        `dict`
            Output fluxes with keys:

            ``'runoff'``
                Runoff (mm).
            ``'seepage'``
                Seepage to groundwater (mm).
            ``'overflow'``
                Overflow (mm).
        
        Notes
        -----
        """
        return self._m.transfer(effective_rainfall, int(deltat))