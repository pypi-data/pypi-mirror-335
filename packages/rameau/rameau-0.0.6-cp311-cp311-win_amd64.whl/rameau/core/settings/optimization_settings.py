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
Model optimisation settings.
"""

from __future__ import annotations
from typing import Optional
import datetime

from rameau.wrapper import COptimizationSettings

from rameau.core._abstract_wrapper import AbstractWrapper
from rameau.core._utils import _check_literal, _set_datetime, _get_datetime
from rameau._typing import MethodType, TransformationType, ObjFunctionType

class OptimizationSettings(AbstractWrapper):
    """Model optimisation settings.
    
    Parameters
    ----------
    maxit: `int`, optional
        Number of iterations for the Rosenbrock algorithm. If not
        provided, default value is zero, i.e. no optimisation will be
        performed.

    starting_date: `datetime.datetime`, optional
        The date and time defining the start of the period to consider
        in the input data for the optimisation run.

    ending_date: `datetime.datetime`, optional
        The date and time defining the end of the period to consider
        in the input data for the optimisation run.

    method: `str`, optional
        The approach to use when several gauged watersheds need to
        be considered in the optimisation run. This is typically the
        case when several independent watersheds are considered at
        once (i.e. batch of lumped watersheds), or when a watershed is
        considered as a collection of interconnected sub-watersheds
        (i.e. semi-distributed watershed).

        =================  =========================================
        method             description
        =================  =========================================
        ``'all'``          All the gauged watersheds are optimised
                           at once. This method is only recommended
                           for a single lumped watershed or for a
                           semi-distributed watershed. This is the
                           default method.

        ``'independent'``  The gauged watersheds are optimised one
                           after another, based on the order they
                           are provided in the `Tree`. The optimised
                           parameter values are sustained between
                           the optimisation iterations. This method
                           is only recommended for a batch of lumped
                           watersheds.

        ``'strahler'``     All the gauged locations with the same
                           Strahler order are grouped and considered
                           together. The optimisation is performed
                           sequentially for each group based on
                           increasing Strahler order. This method is
                           only recommended for a semi-distributed
                           watershed.
        =================  =========================================

    transformation: `str`, optional
        The function to apply to transform the observed and predicted
        river flow (Q) before computing the objective function.

        =================  =========================================
        transformation     description
        =================  =========================================
        ``'no'``           No transformation is performed. This is
                           the default behaviour.

        ``'square root'``  The square root function f(Q) = √Q is
                           applied.

        ``'inverse'``      The reciprocal function f(Q) = 1/Q is
                           applied.

        ``'fifth root'``   The fifth root function f(Q) = ⁵√Q is
                           applied.

        ``'log'``          The natural logarithm function
                           f(Q) = ln(Q) is applied.
        =================  =========================================

    river_objective_function: `str`, optional
        The objective function to use to compare the observed and
        predicted river flow.

        =========================  ===================================
        river_objective_function   description
        =========================  ===================================
        ``'nse'``                  The Nash-Sutcliffe Efficiency
                                   (NSE) metric is used
                                   :cite:p:`1970:nash_river`.

        ``'kge'``                  The original Kling-Gupta
                                   efficiency (KGE) metric is used
                                   :cite:p:`2009:gupta_decomposition`.

        ``'kge_2012'``             The modified Kling-Gupta
                                   efficiency (KGE\') metric is used
                                   :cite:p:`2012:kling_runoff`.
        =========================  ===================================

    selected_watersheds: `list` or `int`, optional
        The indices of the watersheds to consider in the
        optimisation run. The indices relate to the positions in the
        sequence of watersheds specified in the `Tree`. If not
        provided, all gauged watersheds are considered.
    
    verbose : `bool`, optional
        True if the verbose mode is activated. The verbose mode
        prints the iteration number and the associated objective
        function value.
    
    Returns
    -------
    `OptimizationSettings`
    """

    _computed_attributes = (
        "maxit", "starting_date",
        "ending_date", "method", "transformation",
        "river_objective_function", "selected_watersheds",
        "verbose"
    )
    _c_class = COptimizationSettings

    def __init__(
        self,
        maxit: int = 0,
        starting_date: datetime.datetime = None,
        ending_date: datetime.datetime = None,
        method: MethodType = "all",
        transformation: TransformationType = "no",
        river_objective_function: ObjFunctionType = 'nse',
        selected_watersheds: Optional[list[int]] = None,
        verbose: bool = False
    ) -> None: 
        self._init_c()

        self.maxit = maxit

        if starting_date is not None:
            self.starting_date = starting_date
        else:
            self.starting_date = datetime.datetime(9999, 12, 31)

        if ending_date is not None:
            self.ending_date = ending_date
        else:
            self.ending_date = datetime.datetime(9999, 12, 31)

        _check_literal(
            transformation, ["no", "square root", "inverse", "fifth root", "log"]
        )
        self.transformation = transformation

        _check_literal(
            method, ["all", "strahler", "independent"]
        )
        self.method = method

        _check_literal(
            river_objective_function, ["nse", "kge", "kge_2012"]
        )
        self.river_objective_function = river_objective_function

        if selected_watersheds is not None:
            if isinstance(selected_watersheds, list):
                self.selected_watersheds = selected_watersheds
            else:
                raise TypeError(f"Type {type(selected_watersheds)} not allowed.")
        
        self.verbose = verbose

    @property
    @_get_datetime
    def starting_date(self) -> datetime.datetime:
        """The date and time defining the start of the period to consider
        in the input data for the optimisation run.

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
        """The date and time defining the end of the period to consider
        in the input data for the optimisation run.

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
    def method(self) -> str:
        """The approach to use when several gauged watersheds need to
        be considered in the optimisation run.

        Returns
        -------
        `str`
        """
        return self._m.getMethod()

    @method.setter
    def method(self, v: str) -> None:
        self._m.setMethod(v)

    @property
    def transformation(self) -> str:
        """The function to apply to transform the observed and predicted
        river flow before computing the objective function.

        Returns
        -------
        `str`
        """
        return self._m.getTransformation()

    @transformation.setter
    def transformation(self, v: str) -> None:
        self._m.setTransformation(v)

    @property
    def river_objective_function(self) -> str:
        """The objective function to use to compare the observed and
        predicted river flow.
        
        Returns
        -------
        `str`
        """
        return self._m.getObjectiveFunction()

    @river_objective_function.setter
    def river_objective_function(self, v: str) -> None:
        self._m.setObjectiveFunction(v)

    @property
    def selected_watersheds(self) -> list[int]:
        """The indices of the watersheds to consider in the optimisation
        run.

        Returns
        -------
        `list`
        """
        return self._m.getSelectedWatersheds()

    @selected_watersheds.setter
    def selected_watersheds(self, v) -> None:
        if v:
            self._m.setSelectedWatersheds(v)

    @property
    def maxit(self) -> int:
        """Number of iterations for the Rosenbrock algorithm.

        Returns
        -------
        `int`
        """
        return self._m.getMaxit()

    @maxit.setter
    def maxit(self, v: int) -> None:
        self._m.setMaxit(v)

    @property
    def verbose(self) -> bool:
        """Whether the verbose mode is activated. True when it is.

        Returns
        -------
        `bool`
        """
        return self._m.getVerbose()

    @verbose.setter
    def verbose(self, v: bool) -> None:
        self._m.setVerbose(v)
