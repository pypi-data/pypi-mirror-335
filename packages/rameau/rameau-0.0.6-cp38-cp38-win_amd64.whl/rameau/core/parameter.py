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
Physical parameter.
"""

from rameau.wrapper import CParameter

from rameau.core._abstract_wrapper import AbstractWrapper

class Parameter(AbstractWrapper):
    """Physical parameter.
    
    Parameters
    ----------
    value : `float`, optional
        Parameter value.

    opti : `bool`, optional
        True for optimising the parameter.

    lower : `float`, optional
        Lower bound value in case of bound-constrained optimisation.

    upper : `float`, optional
        Upper bound value in case of bound-constrained optimisation.

    sameas : `int`, optional
        Watershed identifier to which this parameter must be equal when running
        an optimisation. A value of zero means an independent parameter value.
    
    Returns
    -------
    `Parameter`
    
    Examples
    --------
    A minimal working example is shown below:

    >>> p = rm.Parameter(value=2, opti=True, lower=-0.2, upper=0.2)
    >>> p.value
    2.0
    """

    _computed_attributes = 'value', 'opti', 'lower', 'upper', 'sameas'
    _c_class = CParameter

    def __init__(
        self,
        value: float = 0.0,
        opti: bool = False,
        lower: float = 0.0,
        upper: float = 0.0,
        sameas: int = 0
    ) -> None: 
        self._init_c()
        self.value = value
        self.opti = opti
        self.lower = lower
        self.upper = upper
        self.sameas = sameas
    
    @property
    def value(self) -> float:
        return self._m.value
    
    @value.setter
    def value(self, v: float):
        self._m.value = float(v)

    @property
    def lower(self) -> float:
        return self._m.lower
    
    @lower.setter
    def lower(self, v) -> None:
        self._m.lower = float(v)

    @property
    def upper(self) -> float:
        return self._m.upper
    
    @upper.setter
    def upper(self, v) -> None:
        self._m.upper = float(v)

    @property
    def opti(self) -> bool:
        return self._m.opti
    
    @opti.setter
    def opti(self, v) -> None:
        self._m.opti = v

    @property
    def sameas(self) -> int:
        return self._m.sameas
    
    @sameas.setter
    def sameas(self, v) -> None:
        self._m.sameas = int(v)