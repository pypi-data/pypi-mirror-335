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
Input collection.
"""
from __future__ import annotations

from typing import Optional, Union

import numpy as np
import pandas as pd

from rameau.wrapper import CInputCollection

from rameau.core import FilePaths
from rameau.core.inputs import Input, InputFormat
from rameau.core._abstract_wrapper import AbstractWrapper
from rameau.core._utils import _build_type, wrap_property

InputType = Optional[Union[np.ndarray, Input, pd.DataFrame]]

class _InputDescriptor():
    """Input descriptor
    """
    def __init__(self, id, doc):
        self._id = id
        self.__doc__ = f"""{doc}

            Returns
            -------
            `Input`
            """

    @wrap_property(Input)
    def __get__(self, instance, type=None) -> Input:
        return instance._m.getInput(self._id)
    
    def __set__(self, instance, value) -> None:
        if np.size(value.data) != 0:
            instance._m.setInput(value._m, self._id)

class InputCollection(AbstractWrapper):
    """Collection of `Input` representing either meteorological, observations,
    or pumping data time series for a given set of watersheds.

    Data are passed to the constructor by keyword arguments whose names refer
    to the data types to store (e.g. rainfall, riverflow observations, etc.).
    Keyword arguments accept `Input`, `numpy.ndarray` or `pandas.DataFrame`.
    In the case of `numpy.ndarray` or `pandas.DataFrame`, data is converted
    into `Input` in the constructor.

    If a `pandas.DataFrame` with a `pandas.DatetimeIndex` as index is passed,
    this index is used to set the input dates.

    Parameters
    ----------
    rainfall: `numpy.ndarray`, `Input` or `pandas.DataFrame`
        Rainfall time series (mm).

    pet: `ndarray`, `Input` or `DataFrame`
        |PET| time series (mm).

    temperature: `numpy.ndarray`, `Input` or `pandas.DataFrame`, optional
        Temperature time series (°C).

    snow: `numpy.ndarray`, `Input` or `pandas.DataFrame`, optional
        Snowfall time series (mm).

    riverobs: `numpy.ndarray`, `Input` or `pandas.DataFrame`, optional
        Observed river flow time series (m3/s).

    groundwaterobs: `numpy.ndarray`, `Input` or `pandas.DataFrame`, optional
        Observed groundwater level time series (m).

    riverpumping: `numpy.ndarray`, `Input` or `pandas.DataFrame`, optional
        River pumping time series (m3/s).

    groundwaterpumping:  `numpy.ndarray`, `Input` or `pandas.DataFrame`, optional
        Groundwater pumping time series (m3/s).

    dates: `pandas.DatetimeIndex`, optional
        If provided, overrides the dates of all the inputs in the collection.
    
    Returns
    -------
    `InputCollection`
    
    Notes
    -----
    The consistency between each input (i.e. shapes of dates and data) is
    checked when setting the collection of inputs to the `Model` either through
    the constructor or by attribute assignment.
    """

    _computed_attributes = (
        "rainfall", "pet", "snow", "temperature",
        "riverobs", "riverpumping", "groundwaterobs",
        "groundwaterpumping",
        "file_paths", "input_format"
    )
    _c_class = CInputCollection
    rainfall: Input = _InputDescriptor(
        0, "Rainfall time series (mm)."
    )
    pet: Input = _InputDescriptor(
        1, "|PET| time series (mm)."
    )
    temperature: Input = _InputDescriptor(
        2, "Temperature time series (°C)"
    )
    snow: Input = _InputDescriptor(
        3, "Snow time series (mm)"
    )
    riverobs: Input = _InputDescriptor(
        4, "Observed river flow time series (m3/s)"
    )
    groundwaterobs: Input = _InputDescriptor(
        5, "Observed groundwater level time series (m)"
    )
    riverpumping: Input = _InputDescriptor(
        6, "River pumping time series (m3/s)"
    )
    groundwaterpumping: Input = _InputDescriptor(
        7, "Groundwater pumping time series (m3/s)"
    )

    def __init__(
            self,
            rainfall: InputType,
            pet: InputType,
            snow: InputType = None,
            temperature: InputType = None,
            riverobs: InputType = None,
            riverpumping: InputType = None,
            groundwaterobs: InputType = None,
            groundwaterpumping: InputType = None,
            dates: Optional[pd.DatetimeIndex] = None,
        ) -> None: 
        self._init_c()

        self.rainfall = self._build_input(rainfall, dates)
        self.pet = self._build_input(pet, dates)

        if snow is not None:
            self.snow = self._build_input(snow, dates)

        if temperature is not None:
            self.temperature = self._build_input(temperature, dates)

        if riverobs is not None:
            self.riverobs = self._build_input(riverobs, dates)

        if groundwaterobs is not None:
            self.groundwaterobs = self._build_input(groundwaterobs, dates)

        if riverpumping is not None:
            self.riverpumping = self._build_input(riverpumping, dates)

        if groundwaterpumping is not None:
            self.groundwaterpumping = self._build_input(groundwaterpumping, dates)
        
        self.input_format = InputFormat()
    
    def _build_input(self, var, dates):
        kwargs = {}
        if dates is not None:
            if not isinstance(dates, pd.DatetimeIndex):
                raise TypeError(f"Type {type(var)} not allowed.")
            kwargs["dates"] = dates

        if isinstance(var, np.ndarray):
            var = Input(data=var, **kwargs)
        elif isinstance(var, pd.DataFrame):
            if isinstance(var.index, pd.DatetimeIndex) and not kwargs:
                var = Input(data=var.to_numpy(), dates=var.index)
            else:
                var = Input(data=var.to_numpy(), **kwargs)
        elif not isinstance(var, Input):
            raise TypeError(f"Type {type(var)} not allowed.")

        return var

    @staticmethod
    def from_files(
            rainfall: str,
            pet: str,
            temperature: str = '',
            snow: str = '',
            riverobs: str = '',
            riverpumping: str = '',
            groundwaterobs: str = '',
            groundwaterpumping: str = '',
            input_format: Optional[Union[dict, InputFormat]] = None
        ) -> InputCollection:
        """Create InputCollection from CSV files.

        Parameters
        ----------
        rainfall: `str`
            Rainfall data file path.

        pet: `str`
            Potential Evapotranspiration data file path.

        temperature: `str`, optional
            Temperature data file path. Default is ab=n empty string.

        snow: `str`, optional
            Snowfall data file path. Default is an empty string.

        riverobs: `str`, optional
            Observed river flow data file path. Default is an empty string.

        groundwaterobs: `str`, optional
            Observed groundwater level data file path. Default is an empty string.

        riverpumping: `str`, optional
            River pumping data file path. Default is an empty string.

        groundwaterpumping: `str`, optional
            Groundwater pumping data file path. Default is an empty string.
        
        input_format: `dict` or `InputFormat`, optional
            Input data file format. Default is None. See `InputFormat`
            for details.

        Returns
        -------
        `InputCollection`
        """

        fake_data = np.ones((1,1))

        ic = InputCollection(fake_data, fake_data)

        ic.file_paths = FilePaths(
            rainfall=rainfall, pet=pet,
            temperature=temperature, snow=snow,
            riverobs=riverobs, riverpumping=riverpumping,
            groundwaterobs=groundwaterobs,
            groundwaterpumping=groundwaterpumping
        )

        if input_format is not None:
            input_format = _build_type(input_format, InputFormat)
            ic.input_format = input_format
        
        e = ic._m.from_files()
        if e.getStat() != 0:
            raise RuntimeError(e.getMessage())
        return ic
    
    @property
    @wrap_property(InputFormat)
    def input_format(self) -> InputFormat:
        """Input data file format.

        Returns
        -------
        `InputFormat`
        """
        return self._m.getInputFormat()

    @input_format.setter
    def input_format(self, v: InputFormat) -> None:
        self._m.setInputFormat(v._m)

    @property
    @wrap_property(FilePaths)
    def file_paths(self) -> FilePaths:
        """Input data file paths.

        Returns
        -------
         `FilePaths`
        """
        return self._m.getFiles()

    @file_paths.setter
    def file_paths(self, v: FilePaths) -> None:
        self._m.setFiles(v._m)
