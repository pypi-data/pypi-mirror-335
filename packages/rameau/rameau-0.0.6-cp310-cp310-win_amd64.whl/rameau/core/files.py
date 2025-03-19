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
File paths.
"""

from rameau.wrapper import CFiles

from rameau.core._abstract_wrapper import AbstractWrapper

class FilePaths(AbstractWrapper):
    """File paths.
    
    Parameters
    ----------
    rainfall : `str`, optional
        Path to rainfall data file.

    pet : `str`, optional
        Path to |PET| data file.

    temperature : `str`, optional
        Path to temperature data file.

    snow : `str`, optional
        Path to snow data file.

    riverobs : `str`, optional
        Path to river flow observation data file.

    groundwaterobs : `str`, optional
        Path to groundwater level observation data file.

    riverpumping : `str`, optional
        path to river pumping data file.

    groundwaterpumping : `str`, optional
        path to groundwater pumping data file.

    tree : `str`, optional
        Path to tree connection CSV file.

    states : str, optional
        Path to model states file.

    Returns
    -------
    `FilePaths`
    """

    _computed_attributes = (
        "rainfall", "pet", "temperature",
        "snow", "riverobs", "riverpumping",
        "groundwaterobs", "groundwaterpumping",
        "tree", "states"
    )
    _c_class = CFiles

    def __init__(
            self,
            rainfall: str = '',
            pet: str = '',
            temperature: str = '',
            snow: str = '',
            riverobs: str = '',
            riverpumping: str = '',
            groundwaterobs: str ='',
            groundwaterpumping: str = '',
            tree: str = '',
            states: str =''
        ) -> None: 
        self._init_c()

        self.rainfall = rainfall
        self.pet = pet
        self.snow = snow
        self.temperature = temperature
        self.tree = tree
        self.riverobs = riverobs
        self.riverpumping = riverpumping
        self.groundwaterobs = groundwaterobs
        self.groundwaterpumping = groundwaterpumping
        self.states = states
    
    @property
    def rainfall(self):
        return self._m.getRainfall()
    
    @rainfall.setter
    def rainfall(self, v: str):
        self._m.setRainfall(v)

    @property
    def pet(self):
        return self._m.getPet()
    
    @pet.setter
    def pet(self, v: str):
        self._m.setPet(v)

    @property
    def snow(self):
        return self._m.getSnow()
    
    @snow.setter
    def snow(self, v: str):
        self._m.setSnow(v)

    @property
    def temperature(self):
        return self._m.getTemperature()
    
    @temperature.setter
    def temperature(self, v: str):
        self._m.setTemperature(v)

    @property
    def riverobs(self):
        return self._m.getRiverobs()
    
    @riverobs.setter
    def riverobs(self, v: str):
        self._m.setRiverobs(v)

    @property
    def riverpumping(self):
        return self._m.getRiverpumping()
    
    @riverpumping.setter
    def riverpumping(self, v: str):
        self._m.setRiverpumping(v)

    @property
    def groundwaterobs(self):
        return self._m.getGroundwaterobs()
    
    @groundwaterobs.setter
    def groundwaterobs(self, v: str):
        self._m.setGroundwaterobs(v)

    @property
    def groundwaterpumping(self):
        return self._m.getGroundwaterpumping()
    
    @groundwaterpumping.setter
    def groundwaterpumping(self, v: str):
        self._m.setGroundwaterpumping(v)

    @property
    def tree(self):
        return self._m.getTree()
    
    @tree.setter
    def tree(self, v: str):
        self._m.setTree(v)

    @property
    def states(self):
        return self._m.getStates()
    
    @states.setter
    def states(self, v: str):
        self._m.setStates(v)