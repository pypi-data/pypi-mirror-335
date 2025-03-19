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
import unittest
from unittest.mock import patch
from rameau.utils import ErosReader, create_model_from_eros
import os
import datetime
import rameau.core as rm
import numpy as np

#def fake_read_arbros(*args, **kwargs):
#    ref_con = {
#        1:2, 2:3, 3:4, 4:6, 5:6, 6:8, 7:8, 8:9,
#        9:11, 10:11, 11:0
#    }
#    ref_name = {
#        1:"Marnay",
#        2:"Mussey",
#        3:"Chamouilley",
#        4:"St_Dizier",
#        5:"Blaise_Louvem",
#        6:"Compl_Frignic",
#        7:"Saulx_Vitry",
#        8:"Compl_Chalons",
#        9:"Compl_Ferté",
#        10:"Grand_Morin",
#        11:"Compl_Gournay"
#    }
#    ref_is_confl = {i:0 for i in range(1, 12)}
#    return ref_con, ref_name, ref_is_confl
#
#def fake_from_files(*args, **kwargs):
#    inputs = rm.InputControl(
#        rainfall = np.arange(11),
#        pet = np.arange(11)
#    )
#    return inputs
#
#def fake_read_parameter(*args, **kwargs):
#    watersheds = [rm.Watershed(), rm.Watershed()]
#    opt = rm.Optimization()
#    input_fmt = rm.InputFormat()
#    return opt, input_fmt, watersheds
#
#class TestConvertEros(unittest.TestCase):
#    @patch.object(ErosReader, 'read_arbros', fake_read_arbros)
#    @patch.object(ErosReader, 'read_parameter', fake_read_parameter)
#    @patch.object(rm.InputControl, 'from_files', fake_from_files)
#    def test_is_instance(self):
#        eros_file = os.path.join(os.path.dirname(__file__),
#            "helpers/data/eros_marne_v73a.eros")
#        model = create_model_from_eros(eros_file)
#        self.assertIsInstance(model, rm.Model)

class TestErosReader(unittest.TestCase):
    def test_is_instance(self):
        eros = ErosReader()
        self.assertIsInstance(eros, ErosReader)
    
    def test_read_project(self):
        eros = ErosReader()
        files_ref = {
            "arbros":"Eros_Marne.arbros",
            "ros":"Eros_Marne.ros",
            "rainfall":"Pluie_Marne_2022.txt",
            "pet":"ETP_Marne_2022.txt",
            "riverobs":"Debits_Marne_2022.txt",
            "groundwaterobs":"Piezos_Marne_2022.txt",
            "riverpumping":"Prelev_Marne_sansrest_2022.txt",
        }
        eros_file = os.path.join(os.path.dirname(__file__),
            "data/eros_marne_v73a.eros")
        files = eros.read_project(eros_file)
        for label in files_ref:
            with self.subTest(label):
                self.assertEqual(files[label], files_ref[label])
    
    def test_read_arbros(self):
        eros = ErosReader()
        eros_file = os.path.join(os.path.dirname(__file__),
            "data/eros_marne_v73.arbros")
        ref_con = {
            1:2, 2:3, 3:4, 4:6, 5:6, 6:8, 7:8, 8:9,
            9:11, 10:11, 11:0
        }
        ref_name = {
            1:"Marnay",
            2:"Mussey",
            3:"Chamouilley",
            4:"St_Dizier",
            5:"Blaise_Louvem",
            6:"Compl_Frignic",
            7:"Saulx_Vitry",
            8:"Compl_Chalons",
            9:"Compl_Ferté",
            10:"Grand_Morin",
            11:"Compl_Gournay"
        }
        ref_is_confl = {i:0 for i in range(1, 12)}
        df = eros.read_arbros(eros_file)
        con = {row.iloc[0]:row.iloc[2] for _, row in df.iterrows()}
        is_c = {row.iloc[0]:row.iloc[3] for _, row in df.iterrows()}
        name = {row.iloc[0]:row.iloc[-1] for _, row in df.iterrows()}
        for ref, d in zip(
            [ref_con, ref_name, ref_is_confl],
            [con, name, is_c]
        ):
            self.assertEqual(ref, d)

    def test_read_ros_v73c(self):
        eros = ErosReader()
        eros_file = os.path.join(os.path.dirname(__file__),
            "data/eros_marne_v73c.ros")
        gw_pump = {i:0 for i in range(1, 12)}
        riv_pump = {i:1 for i in range(1, 12)}
        opt, sim_opt, fmt, watersheds = eros.read_parameter(eros_file, gw_pump, riv_pump)
        ref_opt = rm.settings.OptimizationSettings(
            maxit=600,
            starting_date=datetime.datetime(1985, 1, 1),
            transformation='log'
        )
        ref_fmt = rm.inputs.InputFormat()
        ref_sim_opt = rm.settings.SimulationSettings(
            starting_date=datetime.datetime(1985, 1, 1),
            spinup_settings=rm.settings.SpinupSettings(
                ending_date=datetime.datetime(1984, 12, 31),
                cycles=1
            )
        )
        for ref, d in zip(
            [ref_opt, ref_sim_opt, ref_fmt],
            [opt, sim_opt, fmt]
        ):
            self.assertEqual(ref, d)
        self.assertEqual(len(watersheds), 11)
        self.assertEqual(watersheds[2].river.area.value, 384)
        self.assertAlmostEqual(
            watersheds[2].groundwater.base_level.value,
            172.92238, places=2
        )

    def test_read_ros_v73e(self):
        eros = ErosReader()
        eros_file = os.path.join(os.path.dirname(__file__),
            "data/eros_marne_v73e.ros")
        gw_pump = {i:0 for i in range(1, 12)}
        riv_pump = {i:1 for i in range(1, 12)}
        opt, sim_opt, fmt, watersheds = eros.read_parameter(
            eros_file, gw_pump, riv_pump
        )
        ref_opt = rm.settings.OptimizationSettings(
            maxit=600,
            starting_date=datetime.datetime(1985, 1, 1),
            transformation='log'
        )
        ref_fmt = rm.inputs.InputFormat()
        ref_sim_opt = rm.settings.SimulationSettings(
            starting_date=datetime.datetime(1985, 1, 1),
            spinup_settings=rm.settings.SpinupSettings(
                ending_date=datetime.datetime(1984, 12, 31),
                cycles=1
            )
        )
        for ref, d in zip(
            [ref_opt, ref_sim_opt, ref_fmt],
            [opt, sim_opt, fmt]
        ):
            self.assertEqual(ref, d)
        self.assertEqual(len(watersheds), 11)
        self.assertEqual(watersheds[2].river.area.value, 384)
        self.assertAlmostEqual(
            watersheds[2].groundwater.base_level.value,
            172.92238, places=2
        )





