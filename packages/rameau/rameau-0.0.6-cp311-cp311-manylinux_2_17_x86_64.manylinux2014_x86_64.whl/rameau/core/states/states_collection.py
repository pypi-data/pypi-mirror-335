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
States collection.
"""

from __future__ import annotations
from typing import Union

import numpy as np

from rameau.wrapper import CStatesCollection

from rameau.core.states import States
from rameau.core._abstract_wrapper import AbstractWrapper

from rameau.core._utils import wrap_property, _raise_type_error

class StatesCollection(AbstractWrapper):
    """States collection.
    
    Parameters
    ----------
    states : `list`
        List of watershed `States` to store in the `StatesCollection`.

    Returns
    -------
    `StatesCollection`
    """

    _computed_attributes = "states",
    _c_class = CStatesCollection

    def __init__(
            self,
            states: list[Union[States, dict]],
        ) -> None: 
        self._init_c()

        if not bool(states):
            raise ValueError("Empty list not allowed!")
        for i, res in enumerate(states):
            if isinstance(res, dict):
                states[i] = States(**res)
            elif not isinstance(res, States):
                _raise_type_error(res)
        self.states = states

    @staticmethod
    def from_file(path: str) -> StatesCollection:
        """Load `StatesCollection` from the text file.

        Parameters
        ----------
        path: `str`
            Path to the text file to load.
        
        Returns
        -------
        `StatesCollection`
        """
        sc = StatesCollection.__new__(StatesCollection)
        sc._m = CStatesCollection()
        err = sc._m.from_file(path)
        if err.getStat() != 0:
            raise RuntimeError(err.getMessage())
        return sc
    
    def to_file(
            self,
            path: str,
            index: Union[list[int], np.ndarray[int]] = None
        ) -> None:
        """Dump `StatesCollection` to text file.

        Parameters
        ----------
        path: `str`
            Path to the text file.

        index: `list` or `ndarray`
            Integer indexes to associate with each `States` 
            watershed stored in the `StatesCollection`. If `None`,
            default is a range of integers from 1 to the number
            of stored `States`.
        """
        if index is None:
            index = list(range(1, len(self.states) + 1))
        else:
            a = len(index)
            b = len(self.states)
            if a != b:
                raise ValueError(
                    f"Length mismatch: passed index has {a} elements, StatesCollection has {b} elements"
                )
        self._m.to_file(path, index)
    
    @property
    def states(self) -> list[States]:
        """Stored `States` in the `StatesCollection`.

        Returns
        -------
        `list`
        """
        return [self._ctopy_sta(sta) for sta in self._m.getStates()]

    def _ctopy_sta(self, __states):
        b = States.__new__(States)
        b._m = __states
        return b
    
    @states.setter
    def states(self, v: list) -> None:
        self._m.setStates([vv._m for vv in v])