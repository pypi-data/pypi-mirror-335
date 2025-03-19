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
Overflow parameters.
"""

from typing import Literal

from rameau.wrapper import COverflow

from rameau.core import Parameter
from rameau.core._abstract_wrapper import AbstractWrapper

from rameau._typing import ParameterType
from rameau.core._utils import _build_parameter, wrap_property, _check_literal

class OverflowParameters(AbstractWrapper):
    """Overflow parameters.
    
    Parameters
    ----------
    halflife : `dict` or `Parameter`, optional
        Half-life parameter (time step).

    threshold : `dict` or `Parameter`, optional
        Overflow threshold (mm).

    loss : `str`, optional
        Fate of overflow (only for transfer reservoir).

            =================  =========================================
            loss               description
            =================  =========================================
            ``'no'``           Overflow is directly added to the river
                               flow.
            ``'loss'``         Overflow leaves the system.

            ``'groundwater'``  Overflow is added to the baseflow
                               component of the river flow.
            =================  =========================================
    
    Returns
    -------
    `OverflowParameters`
    """

    _computed_attributes = "halflife", "threshold", "loss"
    _c_class = COverflow

    def __init__(
        self,
        halflife: ParameterType = None,
        threshold: ParameterType = None,
        loss: Literal['no', 'groundwater', 'loss'] = 'no',
    ) -> None: 
        self._init_c()

        if halflife is not None:
            self.halflife = _build_parameter(halflife)
        if threshold is not None:
            self.threshold = _build_parameter(threshold)
        
        _check_literal(loss, ["no", "groundwater", "loss"])
        self.loss = loss
    
    @property
    @wrap_property(Parameter)
    def halflife(self) -> Parameter:
        """Half-life parameter (time step).

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
    def threshold(self) -> Parameter:
        """Overflow threshold (mm).

        Returns
        -------
        `Parameter`
        """
        return self._m.getThreshold()

    @threshold.setter
    def threshold(self, v: Parameter) -> None:
        self._m.setThreshold(v._m)

    @property
    def loss(self) -> str:
        """Fate of overflow (only for transfer reservoir).

        Returns
        -------
        `str`
        """
        return self._m.getLoss()

    @loss.setter
    def loss(self, v: str) -> None:
        self._m.setLoss(v)