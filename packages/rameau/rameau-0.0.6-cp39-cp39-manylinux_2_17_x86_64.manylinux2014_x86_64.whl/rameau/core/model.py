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
rameau model.
"""
from __future__ import annotations

from typing import Union, Optional, Literal
import datetime

import pandas as pd
import numpy as np

from rameau.wrapper import CModel

from rameau.core.settings import (
    SimulationSettings,
    ForecastSettings,
    OptimizationSettings
)
from rameau.core.inputs import InputCollection
from rameau.core.states import StatesCollection, States
from rameau.core.tree import Tree
from rameau.core.simulation import (
    Simulation,
    OptiSimulation,
    ForecastSimulation
)

from rameau.core._utils import _check_literal
from rameau.core._abstract_wrapper import AbstractWrapper
from rameau.core._utils import _build_type, wrap_property

from rameau._typing import MethodType, TransformationType, ObjFunctionType

class Model(AbstractWrapper):
    """Define a rameau model.
    
    Parameters
    ----------
    tree: `dict` or `Tree`
        Watershed connection tree.

    inputs: `dict` or `InputCollection`
        Model input data.

    init_states: `dict` or `StatesCollection`, optional
        Model initial states.

    simulation_settings: `dict` or `SimulationSettings`, optional
        Settings related to a simulation run.
        See `SimulationSettings` for details.

    optimization_settings: `dict` or `OptimizationSettings`, optional
        Settings related to an optimisation run.
        See `OptimizationSettings` for details.

    forecast_settings: `dict` or `ForecastSettings`, optional
        Settings related to a forecast run.
        See `ForecastSettings` for details.
    
    Returns
    -------
    `Model`

    Examples
    --------
    Constructing model from `Tree` and `InputCollection`.

    >>> data = np.array([0.1, 0.2, 0.3])
    >>> model = rm.Model(
    ...     tree=rm.Tree(watersheds=[{}]),
    ...     inputs=rm.inputs.InputCollection(rainfall=data, pet=data)
    ... )
    >>> model.inputs.rainfall.data
    array([[0.1],
           [0.2],
           [0.3]], dtype=float32)

    Constructing model from `dict`.

    >>> model = rm.Model(
    ...     tree=dict(watersheds=[{}]),
    ...     inputs=dict(rainfall=data, pet=data)
    ... )
    >>> model.inputs.rainfall.data
    array([[0.1],
           [0.2],
           [0.3]], dtype=float32)
    """

    _computed_attributes = (
        "tree", "inputs", "init_states", "simulation_settings",
        "optimization_settings", "forecast_settings"
    )
    _c_class = CModel

    def __init__(
        self,
        tree: Union[dict, Tree],
        inputs: Union[dict, InputCollection],
        init_states: Optional[
            Union[list[Union[dict, States]], Union[dict, StatesCollection]]
        ] = None,
        simulation_settings: Optional[Union[dict, SimulationSettings]] = None,
        optimization_settings: Optional[Union[dict, OptimizationSettings]] = None,
        forecast_settings: Optional[Union[dict, ForecastSettings]] = None
    ) -> None: 
        self._init_c()

        self.tree = _build_type(tree, Tree)
        self.inputs = _build_type(inputs, InputCollection)
        if init_states is not None:
            if isinstance(init_states, list):
                self.init_states = StatesCollection(states=init_states)
            else:
                self.init_states = _build_type(init_states, StatesCollection)
        else:
            self._m.set_default_init_states()

        if simulation_settings is not None:
            self.simulation_settings = _build_type(
                simulation_settings, SimulationSettings
            )
        else:
            self.simulation_settings = SimulationSettings()

        if optimization_settings is not None:
            self.optimization_settings = _build_type(
                optimization_settings, OptimizationSettings
            )
        else:
            self.optimization_settings = OptimizationSettings()

        if forecast_settings is not None:
            self.forecast_settings = _build_type(
                forecast_settings, ForecastSettings
            )
        else:
            self.forecast_settings = ForecastSettings()

    @wrap_property(Simulation)
    def create_simulation(self) -> Simulation:
        """Start a simulation run.

        Returns
        -------
        `Simulation`
        """
        sim, err = self._m.create_simulation()
        if err.getStat() != 0:
            raise RuntimeError(err.getMessage())
        return sim
    
    @wrap_property(Simulation)
    def run_simulation(self) -> Simulation:
        """Start a simulation run.

        Returns
        -------
        `Simulation`
        """
        sim, err = self._m.run_simulation()
        if err.getStat() != 0:
            raise RuntimeError(err.getMessage())
        return sim

    @wrap_property(OptiSimulation)
    def run_optimization(
        self,
        maxit: Optional[int] = None,
        starting_date: Optional[datetime.datetime] = None,
        ending_date: Optional[datetime.datetime] = None,
        method: MethodType = None,
        transformation: TransformationType = None,
        river_objective_function: ObjFunctionType = None,
        selected_watersheds: Optional[list[int]] = None,
        verbose = None
    ) -> OptiSimulation:
        """Start an optimisation run.

        Parameters
        ----------
        maxit: `int`, optional
            Number of iterations for the optimisation algorithm.

        starting_date: `datetime.datetime`, optional
            The date and time defining the start of the period to consider
            in the input data for the optimisation run.

        ending_date: `datetime.datetime`, optional
            The date and time defining the end of the period to consider
            in the input data for the optimisation run.

        method: `str`, optional
            The approach to use when several gauged watersheds need to
            be considered in the optimisation run.
            See `OptimizationSettings.method` for details.

        transformation: `str`, optional
            The function to apply to transform the observed and predicted river
            flow (Q) before computing the objective function.
            See `OptimizationSettings.transformation` for details.

        river_objective_function: `str`, optional
            The objective function to use to compare the observed and
            predicted river flow.
            See `OptimizationSettings.objective_function` for details.

        selected_watersheds: `list` or `int`, optional
            The indices of the watersheds to consider in the
            optimisation run. The indices relate to those in the
            sequence of watersheds specified in the `Tree`. If not
            provided, all gauged watersheds are considered.

        verbose: `bool`, optional
            Whether to display information for each step of the
            optimisation process. If not provided, no information is
            displayed.

        Returns
        -------
        `OptiSimulation`
        """
        attrs = {
            "maxit":maxit, "starting_date":starting_date,
            "ending_date":ending_date, "method":method,
            "transformation":transformation,
            "river_objective_function":river_objective_function,
            "selected_watersheds":selected_watersheds,
            "verbose":verbose
        }
        kwargs = {}
        for key, value in attrs.items():
            if value is not None:
                kwargs[key] = value
            else:
                kwargs[key] = getattr(self.optimization_settings, key)
        opt = OptimizationSettings(**kwargs)
        
        if opt.maxit > 0:
            sim, err = self._m.run_optimization(opt._m)
            if err.getStat() != 0:
                raise RuntimeError(err.getMessage())
            return sim
        else:
            raise RuntimeError("0 iterations defined (maxit=0).")

    @wrap_property(ForecastSimulation)
    def run_forecast(
        self,
        emission_date: Optional[datetime.datetime] = None,
        scope: Optional[datetime.timedelta] = None,
        year_members: Optional[list[int]] = None,
        correction: Optional[Literal["no", "halflife", "enkf"]] = None,
        pumping_date: Optional[datetime.datetime] = None,
        quantiles_output: bool = None,
        quantiles: Optional[list[int]] = None,
        norain: bool = None
    ) -> ForecastSimulation:
        """Start a forecast run.

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
            before issuing a forecast. See `ForecastSettings` for details.

        pumping_date: `datetime.datetime`, optional

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
        `ForecastSimulation`
        """
        attrs = {
            "emission_date":emission_date, "scope":scope,
            "year_members":year_members,
            "correction":correction, "pumping_date":pumping_date,
            "quantiles_output":quantiles_output, "quantiles":quantiles,
            "norain":norain
        }
        kwargs = {}
        for key, value in attrs.items():
            if value is not None:
                kwargs[key] = value
            else:
                kwargs[key] = getattr(self.forecast_settings, key)
        fcast = ForecastSettings(**kwargs)
        sim, err = self._m.run_forecast(fcast._m)
        if err.getStat() != 0:
            raise RuntimeError(err.getMessage())
        return sim

    def get_input(
        self,
        variable: Literal[
            "rainfall", "pet", "snow", "temperature",
            "riverobs", "groundwaterobs",
            "riverpumping", "groundwaterpumping"
        ] = 'rainfall'
    ) -> pd.DataFrame:
        """Get model input data.

        Parameters
        ----------

        variable: `str`, optional
            The model input variable to retrieve.

            ======================== =======================================
            variable                 description
            ======================== =======================================
            ``'rainfall'``           The model input rainfall data.

            ``'pet'``                The model input |PET| data.

            ``'snow'``               The model input snow data.

            ``'temperature'``        The model input temperature data.

            ``'riverobs'``           The river flow observation data.

            ``'groundwaterobs'``     The groundwater level observation data.

            ``'riverpumping'``       The river pumping data.

            ``'groundwaterpumping'`` The Groundwater pumping data.
            ======================== =======================================

        Returns
        -------
        `pandas.DataFrame`
        """
        _check_literal(
            variable,
            [
                "rainfall", "pet", "snow", "temperature",
                "riverobs", "groundwaterobs",
                "riverpumping", "groundwaterpumping"
            ]
        )
        return self._input_to_dataframe(
            getattr(self.inputs, variable), True
        )

    @classmethod
    def from_toml(cls, path: str) -> Model:
        """Load a model from a TOML file.

        Parameters
        ----------

        path: `str`
            TOML file path.
        """
        model = cls.__new__(cls)
        model._m = CModel()
        err = model._m.from_toml(path)
        if err.getStat() != 0:
            raise RuntimeError(err.getMessage())
        return model

    def to_toml(
        self,
        path: str,
        tree: Optional[Tree] = None,
    ) -> None:
        """
        Dump the model to a TOML file.

        Parameters
        ----------
        path: `str`
            TOML file path.

        tree: `Tree`, optional
            The `Tree` object to write in the TOML file. If None, write the
            `Tree` object associated with the `tree` model attribute.
        """
        if tree is None:
            tree = self.tree
        err = self._m.to_toml(path, tree._m)
        if err.getStat() != 0:
            raise RuntimeError(err.getMessage())

    def _input_to_dataframe(self, data, nan_nodata=False):
        d = data.data
        if np.size(d) == 0:
            return pd.DataFrame()
        df = pd.DataFrame(
            data=d, index=data.dates,
            columns=range(1, d.shape[1] + 1)
        )
        df.index.name = "dates"
        df.columns.name = "zones"
        if nan_nodata:
            df = df.where(df != data.nodata, np.nan)
        return df

    @property
    @wrap_property(Tree)
    def tree(self) -> Tree:
        """Watershed connection tree of the model.

        Returns
        -------
        `Tree`
        """
        return self._m.getTree()
    
    @tree.setter
    def tree(self, v: Tree) -> None:
        self._m.setTree(v._m)

    @property
    @wrap_property(InputCollection)
    def inputs(self) -> InputCollection:
        """Model input data.

        Returns
        -------
        `InputCollection`
        """
        return self._m.getInputs()
    
    @inputs.setter
    def inputs(self, v: InputCollection) -> None:
        e = self._m.setInputs(v._m)
        if e.getStat() != 0:
            raise RuntimeError(e.getMessage())

    @property
    @wrap_property(StatesCollection)
    def init_states(self) -> StatesCollection:
        """Model initial states.

        Returns
        -------
        `StatesCollection`
        """
        return self._m.getInitStates()
    
    @init_states.setter
    def init_states(self, v: StatesCollection) -> None:
        self._m.setInitStates(v._m)

    @property
    @wrap_property(SimulationSettings)
    def simulation_settings(self) -> SimulationSettings:
        """Settings related to a simulation run.

        Returns
        -------
        `SimulationSettings`
        """
        return self._m.getSimulationSettings()
    
    @simulation_settings.setter
    def simulation_settings(self, v: SimulationSettings) -> None:
        self._m.setSimulationSettings(v._m)

    @property
    @wrap_property(OptimizationSettings)
    def optimization_settings(self) -> OptimizationSettings:
        """Settings related to an optimisation run.

        Returns
        -------
        `OptimizationSettings`
        """
        return self._m.getOptimizationSettings()
    
    @optimization_settings.setter
    def optimization_settings(self, v: OptimizationSettings) -> None:
        self._m.setOptimizationSettings(v._m)

    @property
    @wrap_property(ForecastSettings)
    def forecast_settings(self) -> ForecastSettings:
        """Settings related to a forecast run.

        Returns
        -------
        `ForecastSettings`
        """
        return self._m.getForecastSettings()
    
    @forecast_settings.setter
    def forecast_settings(self, v: ForecastSettings) -> None:
        self._m.setForecastSettings(v._m)
