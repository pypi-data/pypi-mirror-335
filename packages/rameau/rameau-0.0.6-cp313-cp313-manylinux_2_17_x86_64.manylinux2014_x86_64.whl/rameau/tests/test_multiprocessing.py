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
import datetime
from functools import partial

import pandas as pd
import numpy as np

import rameau as rm

def task(date, model: rm.Model):
    sim = model.run_forecast(
        emission_date=date,
        scope=datetime.timedelta(days=4)
    )
    res = []
    for data in sim._m.getForecastOutputs().getVariable(0):
        res.append(data.getData())
    return np.array(res)

class TestParallel(unittest.TestCase):
    def setUp(self):
        inputs = rm.inputs.InputCollection(
            rainfall=np.random.random((900, 2)),
            pet=np.random.random((900, 2)),
            dates = pd.date_range(start="2000-1-1", periods=900)
        )
        tree = rm.Tree(
            watersheds=[rm.Watershed(), rm.Watershed()],
            connection={1:2, 2:0}
        )
        self.model = rm.Model(tree, inputs)

    def test_multiprocessing_run_forecast(self):
        import multiprocessing
        dates = pd.date_range("2000-1-1", "2000-1-2")
        refs = [task(date, self.model) for date in dates]
        results = []
        with multiprocessing.Pool(4) as pool:
            for result in pool.map(partial(task, model=self.model), dates):
                results.append(result)
        np.testing.assert_almost_equal(refs, results)

    #def test_joblib_run_forecast(self):
    #    from joblib import Parallel, delayed
    #    dates = pd.date_range("2000-1-1", "2000-1-2")
    #    refs = [task(date, self.model) for date in dates]
    #    results = Parallel(2)(delayed(task)(date, self.model) for date in dates)
    #    np.testing.assert_almost_equal(refs, results)