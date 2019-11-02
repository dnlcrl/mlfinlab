"""
Test structural break tests: Chow-type, CUSUM, SADF
"""

import unittest
import os
import numpy as np
import pandas as pd

from mlfinlab.structural_breaks import get_chow_type_stat, get_sadf, get_chu_stinchcombe_white_statistics


class TesStructuralBreaks(unittest.TestCase):
    """
    Test Chow-type, CUSUM, SADF tests
    """

    def setUp(self):
        """
        Set the file path for the sample dollar bars data.
        """
        project_path = os.path.dirname(__file__)
        self.path = project_path + '/test_data/dollar_bar_sample.csv'
        self.data = pd.read_csv(self.path, index_col='date_time', parse_dates=[0])

    def test_chow_test(self):
        """
        Test get_chow_type_stat function
        """
        min_length = 10
        log_prices = np.log(self.data.close)
        stats = get_chow_type_stat(log_prices, min_length=min_length)

        # We drop first and last # of min_length values
        self.assertEqual(log_prices.shape[0] - min_length * 2, stats.shape[0])
        self.assertAlmostEqual(stats.max(), 0.179, delta=1e-3)
        self.assertAlmostEqual(stats.mean(), -0.653, delta=1e-3)
        self.assertAlmostEqual(stats[3], -0.6649, delta=1e-3)

    def test_chu_stinchcombe_white_test(self):
        log_prices = np.log(self.data.close)
        one_sided_test = get_chu_stinchcombe_white_statistics(log_prices, test_type='one_sided')
        two_sided_test = get_chu_stinchcombe_white_statistics(log_prices, test_type='two_sided')

        # For the first two values we don't have enough info
        self.assertEqual(log_prices.shape[0] - 2, one_sided_test.shape[0])
        self.assertEqual(log_prices.shape[0] - 2, two_sided_test.shape[0])

        self.assertAlmostEqual(one_sided_test.critical_value.max(), 3.265, delta=1e-3)
        self.assertAlmostEqual(one_sided_test.critical_value.mean(), 2.7809, delta=1e-3)
        self.assertAlmostEqual(one_sided_test.critical_value[20], 2.4466, delta=1e-3)

        self.assertAlmostEqual(one_sided_test.stat.max(), 3729.001, delta=1e-3)
        self.assertAlmostEqual(one_sided_test.stat.mean(), 836.509, delta=1e-3)
        self.assertAlmostEqual(one_sided_test.stat[20], 380.137, delta=1e-3)

        self.assertAlmostEqual(two_sided_test.critical_value.max(), 3.235, delta=1e-3)
        self.assertAlmostEqual(two_sided_test.critical_value.mean(), 2.769, delta=1e-3)
        self.assertAlmostEqual(two_sided_test.critical_value[20], 2.715, delta=1e-3)

        self.assertAlmostEqual(two_sided_test.stat.max(), 5518.519, delta=1e-3)
        self.assertAlmostEqual(two_sided_test.stat.mean(), 1264.582, delta=1e-3)
        self.assertAlmostEqual(two_sided_test.stat[20], 921.2979, delta=1e-3)

        with self.assertRaises(ValueError):
            one_sided_test += get_chu_stinchcombe_white_statistics(log_prices, test_type='abs')

    def test_asdf_test(self):
        log_prices = np.log(self.data.close)
        lags_int = 5
        lags_array = [1, 2, 5, 7]
        min_length = 20

        sm_power_sadf = get_sadf(log_prices, model='sm_power', add_const=True, min_length=min_length, lags=lags_int)

        linear_sadf = get_sadf(log_prices, model='linear', add_const=True, min_length=min_length, lags=lags_int)
        linear_sadf_no_const_lags_arr = get_sadf(log_prices, model='linear', add_const=False, min_length=min_length,
                                                 lags=lags_array)

        quandratic_sadf = get_sadf(log_prices, model='quadratic', add_const=True, min_length=min_length, lags=lags_int)
        sm_poly_1_sadf = get_sadf(log_prices, model='sm_poly_1', add_const=True, min_length=min_length, lags=lags_int)
        sm_poly_2_sadf = get_sadf(log_prices, model='sm_poly_2', add_const=True, min_length=min_length, lags=lags_int)
        sm_exp_sadf = get_sadf(log_prices, model='sm_exp', add_const=True, min_length=min_length, lags=lags_int)

        with self.assertRaises(ValueError):
            linear_sadf += get_sadf(log_prices, model='cubic', add_const=True, min_length=min_length, lags=lags_int)