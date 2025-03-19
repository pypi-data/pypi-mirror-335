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
Rameau simulations
"""
from typing import Literal, List
from collections import defaultdict
import pandas as pd
import numpy as np

from rameau.wrapper import (
    CSimulation, COptiSimulation, CForecastSimulation
)
from rameau.core.settings import (
    SimulationSettings, ForecastSettings, OptimizationSettings
)
from rameau.core import Tree
from rameau.core.states import StatesCollection
from rameau.core.inputs import InputCollection

from rameau.core._utils import wrap_property, _check_literal, _get_datetime

class Simulation():
    """rameau simulations."""
    _c_class = CSimulation
    _metrics_riv_keys_meths = {
        "nse": "getNSE",
        "kge": "getKGE",
        "kge_2012": "getKGE_2012",
        "nse_sqrt": "getNSESqrt",
        "kge_sqrt": "getKGESqrt",
        "kge_2012_sqrt": "getKGE_2012Sqrt",
        "nse_log": "getNSELog",
        "kge_log": "getKGELog",
        "kge_2012_log": "getKGE_2012Log",
        "ratio": "getRatio",
    }
    _metrics_gw_keys_meths = {
        "nse": "getNSE",
    }
    _variables_ids = {
        'output': {
            'riverflow': 0,
            'watertable': 1,
        },
        'budget': {
            'rainfall': 2,
            'snowfall': 3,
            'potential_evapotranspiration': 4,
            'unmet_potential_evapotranspiration': 5,
            'actual_evapotranspiration': 6,
            'effective_rainfall': 7,
            'height_snowpack': 8,
            'retention_snowpack': 9,
            'height_thornthwaite_reservoir': 10,
            'height_progressive_reservoir': 11,
            'runoff': 12,
            'runoff_overflow': 13,
            'seepage': 14,
            'height_soil': 15,
            'baseflow': 16,
            'drainage': 17,
            'exchanges_flow': 18,
            'groundwater_overflow': 19,
            'groundwater_state': 20,
            'riverflow_local': 21,
        }
    }

    def __init__(self) -> None: 
        self._m = self._c_class()

    def _set_columns(self, header_type):
        c = self.tree.connection
        if header_type == 'id':
            columns = list(c.keys())
        elif header_type == 'name':
            columns = [self.tree.watersheds[i].name for i in range(len(c))]
        return columns

    @_get_datetime
    def _get_date(self, date):
        return date

    def _input_to_dataframe(self, data, header_type, nan_nodata=False):
        columns = self._set_columns(header_type)
        if np.size(data.data) == 0:
            return pd.DataFrame()
        df = pd.DataFrame(
            data.data,
            index=data.dates,
            columns=columns
        )
        df.index.name = "dates"
        df.columns.name = "watersheds"
        if nan_nodata:
            df = df.where(df != data.nodata, np.nan)
        return df


    def _output_to_dataframe(self, data, header_type):
        columns = self._set_columns(header_type)
        if np.size(data) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(
            data,
            index=[
                self._get_date(d.getDatetime())
                for d in self._m.getOutputs().getDates()
            ],
            columns=columns
        )
        df.index.name = "dates"
        df.columns.name = "watersheds"
        return df

    def _metrics_to_dataframe(self, scores, columns, header_type):
        if len(scores) > 0:
            data = defaultdict(lambda :[])
            index = self._set_columns(header_type)
            for i in range(len(self.tree.connection)):
                for key, value in columns.items():
                    data[key].append(getattr(scores[i], value)())
            df = pd.DataFrame(data, index=index).T
            df.index.name = "metrics"
            df.columns.name = "watersheds"
            df = df.where(df < 1e+20, np.nan)
            return df
        else:
            return pd.DataFrame()

    def get_input(
        self,
        variable: Literal[
            "rainfall", "pet", "snow", "temperature",
            "riverobs", "groundwaterobs",
            "riverpumping", "groundwaterpumping"
        ] = 'rainfall',
        header_type: Literal["id", "name"] = "name"
    ) -> pd.DataFrame:
        """Get simulation input data.

        Parameters
        ----------

        variable: `str`, optional
            The simulation input variable to retrieve.

            ======================== =======================================
            variable                 description
            ======================== =======================================
            ``'rainfall'``           The simulation input rainfall data.

            ``'pet'``                The simulation input |PET| data.

            ``'snow'``               The simulation input snow data.

            ``'temperature'``        The simulation input temperature data.

            ``'riverobs'``           The river flow observation data.

            ``'groundwaterobs'``     The groundwater level observation data.

            ``'riverpumping'``       The river pumping data.

            ``'groundwaterpumping'`` The groundwater pumping data.
            ======================== =======================================

        header_type: `str`, optional
            The header type of the returned `pandas.DataFrame`.

            ============ ==========================================
            header_type  description
            ============ ==========================================
            ``'id'``     The header corresponds to the watershed
                         identifiers as they were provided to build
                         the `Tree`.

            ``'name'``   The header corresponds to the watershed 
                         names.
            ============ ==========================================

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
        _check_literal(header_type, ["id", "name"])
        return self._input_to_dataframe(
            getattr(self._inputs, variable), header_type, True
        )

    @property
    @wrap_property(InputCollection)
    def _inputs(self):
        return self._m.getInputs()

    def get_output(
        self,
        variable: Literal["riverflow", "watertable"] = 'riverflow',
        header_type: Literal["id", "name"] = "name"
    ) -> pd.DataFrame:
        """Get a given output variable.

        Parameters
        ----------
        variable: `str`, optional
            Which output variable to return as a dataframe. The options
            are *riverflow* or *watertable*. By default, *riverflow* is
            returned.

        header_type: `str`, optional
            Whether to use the watershed identifiers or names as
            dataframe header.

        Returns
        -------
        `pandas.DataFrame`
        """

        _check_literal(variable, ["riverflow", "watertable"])
        _check_literal(header_type, ["id", "name"])

        id_ = self._variables_ids['output'][variable]

        return self._output_to_dataframe(
            self._m.getOutputs().getVariable(id_, 1).getData(), header_type
        )

    def get_budget(
            self,
            variables: List[str] = None,
            header_type: Literal["id", "name"] = "name",
    ) -> pd.DataFrame:
        """Get the water balance.

        Parameters
        ----------
        header_type: `str`, optional
            Whether to use the watershed identifiers or names as
            dataframe header.
        variables: `str`, optional

        Returns
        -------
        `pandas.DataFrame`
        """
        _check_literal(header_type, ["id", "name"])
        if variables is not None:
            variables = {
                key:value for key, value in self._variables_ids["budget"].items() 
                if key in variables
            }
        else:
            variables = self._variables_ids['budget']

        # determine maximum number of groundwater reservoirs
        n_gw_res = 0
        for watershed in self.tree.watersheds:
            n = len(watershed.groundwater.reservoirs)
            if n > n_gw_res:
                n_gw_res = n

        # gather budget variables into a single dataframe
        df = None

        for variable, id_ in variables.items():
            def get_variable(var, res):
                d = self._output_to_dataframe(
                    self._m.getOutputs().getVariable(id_, res).getData(),
                    header_type
                )
                # turn variable dataframe columns into multiindex
                d = pd.concat(
                    [d], keys=[var], names=['variables'], axis=1
                )
                return d

            if variable in [
                    'baseflow', 'drainage', 'exchanges_flow',
                    'groundwater_overflow', 'groundwater_state'
            ]:
                for k in range(1, n_gw_res + 1):
                    df = pd.concat(
                        [df, get_variable(f'{variable}#{k}', k)],
                        axis=1
                    )
            else:
                df = pd.concat(
                    [df, get_variable(variable, 1)],
                    axis=1
                )

        return df.reorder_levels(['watersheds', 'variables'], axis=1)

    def get_metrics(
        self,
        variable: Literal["riverflow", "watertable"] = 'riverflow',
        header_type: Literal["id", "name"] = "name"
    ) -> pd.DataFrame:
        """Get the metrics.

        Parameters
        ----------
        header_type: `str`, optional
            Whether to use the watershed identifiers or names as
            dataframe header.

        Returns
        -------
        `pandas.DataFrame`
        """
        _check_literal(variable, ["riverflow", "watertable"])
        _check_literal(header_type, ["id", "name"])

        if variable == 'riverflow':
            return self._metrics_to_dataframe(
                self._m.getOutputs().getMetricsRiverflow(),
                self._metrics_riv_keys_meths,
                header_type
            )
        elif variable == 'watertable':
            return self._metrics_to_dataframe(
                self._m.getOutputs().getMetricsWatertable(),
                self._metrics_gw_keys_meths,
                header_type
            )
        
    def run(self, start: int, end: int, update_param: bool = False) -> None:
        """Run simulation from `start` to `end` time steps.

        Parameters
        ----------
        start: `int`
            Starting timestep.
        
        end: `int`
            Ending timestep.

        update_param: `bool`.
            Reinitialise the simulation parameters
        """
        self._m.run(start, end, update_param)
    
    @wrap_property(StatesCollection)
    def get_states(self, timestep: int) -> StatesCollection:
        """Get the simulation states for `timestep`.

        Parameters
        ----------
        timestep: `int`
            Timestep for which to get simulation states. 

        Returns
        -------
        `StatesCollection`
        """
        return self._m.getStates(timestep)

    @wrap_property(StatesCollection)
    def set_states(
        self,
        states: StatesCollection,
        timestep: int,
        only_levels: bool = False
    ) -> None:
        """Set the simulation states for `timestep`.

        Parameters
        ----------
        states: `StatesCollection`
            Simulation states to apply.

        timestep: `int`
            Timestep for which to set the simulation states. 
        
        only_levels: `bool`
            Whether to update only reservoir levels.
        """
        self._m.setStates(states._m, timestep, only_levels)

    @property
    @wrap_property(Tree)
    def tree(self) -> Tree:
        return self._m.getTree()

    @property
    @wrap_property(StatesCollection)
    def final_states(self) -> StatesCollection:
        return self._m.getOutputs().getFinalStates()

    @property
    @wrap_property(SimulationSettings)
    def simulation_settings(self) -> SimulationSettings:
        return self._m.getSimulationSettings()


class OptiSimulation(Simulation):
    """rameau optimization simulation."""
    _c_class = COptiSimulation

    def __init__(self) -> None: 
        super.__init__()
        self.optimization_settings: OptimizationSettings

    def get_opti_metrics(
        self,
        variable: Literal["riverflow", "watertable"] = 'riverflow',
        header_type: Literal["id", "name"] = "name"
    ) -> pd.DataFrame:

        _check_literal(variable, ["riverflow", "watertable"])
        _check_literal(header_type, ["id", "name"])

        if variable == 'riverflow':
            return self._metrics_to_dataframe(
                self._m.getOutputs().getMetricsOptiRiverflow(),
                self._metrics_riv_keys_meths,
                header_type
            )
        elif variable == 'watertable':
            return self._metrics_to_dataframe(
                self._m.getOutputs().getMetricsOptiWatertable(),
                self._metrics_gw_keys_meths,
                header_type
            )


    @property
    @wrap_property(OptimizationSettings)
    def optimization_settings(self) -> OptimizationSettings:
        return self._m.getOptimizationSettings()

class ForecastSimulation(OptiSimulation):
    """rameau forecast simulation."""
    _c_class = CForecastSimulation

    _forecast_variables_ids = {
        'output': {
            'riverflow': 0,
            'watertable': 1,
        }
    }

    def __init__(self) -> None: 
        self._m = CForecastSimulation()

    @property
    @wrap_property(ForecastSettings)
    def forecast_settings(self) -> ForecastSettings:
        return self._m.getForecastSettings()

    def get_forecast_output(
        self,
        variable: Literal["riverflow", "watertable"] = 'riverflow',
        header_type: Literal["id", "name"] = "name"
    ) -> pd.DataFrame:

        _check_literal(variable, ["riverflow", "watertable"])
        _check_literal(header_type, ["id", "name"])

        columns = self._set_columns(header_type)
        df2 = {}
        j = 0

        outputs = self._m.getForecastOutputs().getVariable(
            self._forecast_variables_ids['output'][variable]
        )

        for i, output in enumerate(outputs):
            df = pd.DataFrame(
                output.getData(),
                index=[
                    self._get_date(d.getDatetime())
                    for d in self._m.getForecastOutputs().getDates()
                ],
                columns=columns
            )
            df.index.name = "dates"
            df.columns.name = "watersheds"
            if self.forecast_settings.norain and i == 0:
                df2['norain'] = df
            else:
                if self.forecast_settings.quantiles_output:
                    df2[f'{self.forecast_settings.quantiles[j]}%'] = df
                else:
                    df2[self.forecast_settings.year_members[j]] = df
                j = j + 1
        if df2:
            df2 = pd.concat(df2, axis=1, names=['member'])
            return df2
        else:
            return pd.DataFrame()

    def get_output(
            self,
            variable: Literal["riverflow", "watertable"] = 'riverflow',
            header_type: Literal["id", "name"] = "name"
        ) -> pd.DataFrame:

        _check_literal(variable, ["riverflow", "watertable"])
        _check_literal(header_type, ["id", "name"])

        emission_date = self.forecast_settings.emission_date

        data = self._output_to_dataframe(
            self._m.getOutputs()
                .getVariable(self._variables_ids['output'][variable], 1)
                .getData(),
            header_type
        )
        return data.loc[:emission_date]
