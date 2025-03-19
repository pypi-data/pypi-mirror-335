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
import rameau as rm
import unittest
import os

class TestOptimizationDurance(unittest.TestCase):
    def setUp(self):
        rep = os.path.join(os.path.dirname(__file__),
            'data')
        os.chdir(rep)
        self.model = rm.Model.from_toml("durance.toml")

    def test_opti_scores_riverflow(self):
        sim = self.model.run_optimization()
        scores = sim.get_opti_metrics()
        self.assertGreater(scores.loc['nse_sqrt', "Durance"], 0.76)
    
    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
