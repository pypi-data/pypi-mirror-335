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
Pumping reservoir.
"""

from rameau.wrapper import CPumpingReservoir

from rameau.core.parameter import Parameter
from rameau.core._abstract_wrapper import AbstractWrapper

from rameau._typing import ParameterType
from rameau.core._utils import _build_parameter, wrap_property

class PumpingReservoir(AbstractWrapper):
    """Pumping reservoir.
    
    Parameters
    ----------
    coefficient: `dict` or `Parameter`, optional
        Fraction of the pumping rate that will be applied (-).

    halflife_rise: `dict` or `Parameter`, optional
        Halflife time of the falling pumping (time step).

    halflife_fall: `dict` or `Parameter`, optional
        Halflife time of the rising pumping (time step).

    Returns
    -------
    `PumpingReservoir`
    """

    _computed_attributes = "coefficient", "halflife_fall", "halflife_rise"
    _c_class = CPumpingReservoir

    def __init__(
            self,
            coefficient: ParameterType = None,
            halflife_rise: ParameterType = None,
            halflife_fall: ParameterType = None
        ) -> None: 
        self._init_c()

        if coefficient is not None:
            self.coefficient = _build_parameter(coefficient)
        if halflife_fall is not None:
            self.halflife_fall = _build_parameter(halflife_fall)
        if halflife_rise is not None:
            self.halflife_rise = _build_parameter(halflife_rise)
    
    @property
    @wrap_property(Parameter)
    def coefficient(self) -> Parameter:
        """Fraction of the pumping rate that will be applied (-).

        Returns
        -------
        `Parameter`
        """
        return self._m.getCoefficient()

    @coefficient.setter
    def coefficient(self, v: Parameter) -> None:
        self._m.setCoefficient(v._m)

    @property
    @wrap_property(Parameter)
    def halflife_fall(self) -> Parameter:
        return self._m.getHalflifeFall()

    @halflife_fall.setter
    def halflife_fall(self, v: Parameter) -> None:
        self._m.setHalflifeFall(v._m)

    @property
    @wrap_property(Parameter)
    def halflife_rise(self) -> Parameter:
        return self._m.getHalflifeRise()

    @halflife_rise.setter
    def halflife_rise(self, v: Parameter) -> None:
        self._m.setHalflifeRise(v._m)