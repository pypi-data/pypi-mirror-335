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
import tomlkit
import unittest
import os
import shutil
import rameau.utils as rmu
from rameau.core import Model


class TestGardeniaParser(unittest.TestCase):

    _versions = ('8.8.1',)
    _piezometers = (
        'buclay',
        'savigne',
        'chateauneuf',
    )

    def test_reading_legacy_gardenia_files(self):
        for vn in self._versions:
            tg = ''.join(vn.split('.'))

            for pz in self._piezometers:
                with self.subTest(version=vn, piezometer=pz):
                    # generate TOML+CSV files from RGA+GAR files
                    rmu.convert_rga_gar_to_toml(
                        rga_file=os.path.join(
                            os.path.dirname(__file__),
                            f"data/gardenia_{pz}_v{tg}.rga"
                        ),
                        gar_file=os.path.join(
                            os.path.dirname(__file__),
                            f"data/gardenia_{pz}_v{tg}.gar"
                        ),
                        toml_file=os.path.join(
                            os.path.dirname(__file__),
                            f"tmp/gardenia_{pz}_v{tg}.toml"
                        ),
                        gardenia_version=vn
                    )

                    # check content of TOML file
                    # (skipping comparison of paths to tree files)
                    tml1 = tomlkit.load(
                        open(os.path.join(
                            os.path.dirname(__file__),
                            f"tmp/gardenia_{pz}_v{tg}.toml"
                        ))
                    )
                    tml2 = tomlkit.load(
                        open(os.path.join(
                            os.path.dirname(__file__),
                            f"data/gardenia_{pz}_v{tg}.toml"
                        ))
                    )

                    self.assertEqual(tml1, tml2)

    def test_creating_model_from_legacy_gardenia_files(self):
        for vn in self._versions:
            tg = ''.join(vn.split('.'))

            for pz in self._piezometers:
                with self.subTest(version=vn, piezometer=pz):
                    root = os.path.dirname(__file__)

                    os.chdir(os.path.join(root, 'data'))

                    model = rmu.create_model_from_rga_gar(
                        rga_file=f"gardenia_{pz}_v{tg}.rga",
                        gar_file=f"gardenia_{pz}_v{tg}.gar",
                        gardenia_version=vn
                    )
                    self.assertIsInstance(model, Model)

                    os.chdir(root)
    
    def tearDown(self):
        path = os.path.join(os.path.dirname(__file__), "tmp")
        if os.path.exists(path):
            shutil.rmtree(path)
