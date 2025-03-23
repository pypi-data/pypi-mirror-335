import unittest
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch
from ionerdss.analysis.histogram.single_species.hist_temp import hist_temp
from ionerdss.analysis.file_managment.save_vars_to_file import save_vars_to_file
from ionerdss.analysis.histogram.single_species.complex_time_3d import complex_time_3d


class TestComplexTime3D(unittest.TestCase):
    """Unit tests for the complex_time_3d function."""

    def setUp(self):
        """Initialize test data for complex_time_3d."""
        self.graph_type = 1  # Heatmap
        self.graphed_data = 1  # Complex count
        self.file_num = 1
        self.initial_time = 0.0
        self.final_time = 100.01
        self.species_name = "A"
        self.time_bins = 5
        self.x_bar_size = 1

        # Sample histogram data: [time, complex_count, complex_sizes]
        self.full_hist = [
            [
                [0.0, [10, 5, 4], [1, 2, 3]],
                [20.0, [15, 8, 3], [1, 2, 3]],
                [40.0, [15, 8], [1, 2]],
                [60.0, [20, 10, 4], [1, 2, 5]],
                [80.0, [20, 10, 1], [1, 2, 6]],
                [100.0, [20, 10, 2], [1, 2, 7]]
            ]
        ]

        self.full_hist_2 = [
            [
                [0.0, [10, 5, 4], [1, 2, 3]],
                [20.0, [15, 8, 3], [1, 2, 3]],
                [40.0, [15, 8], [1, 2]],
                [60.0, [20, 10, 4], [1, 2, 5]],
                [80.0, [20, 10, 1], [1, 2, 6]],
                [100.0, [20, 10, 2], [1, 2, 7]]
            ],
            [
                [0.0, [20, 10, 8], [1, 2, 3]],
                [20.0, [30, 16, 6], [1, 2, 3]],
                [40.0, [30, 16], [1, 2]],
                [60.0, [40, 20, 8], [1, 2, 5]],
                [80.0, [40, 20, 2], [1, 2, 6]],
                [100.0, [40, 20, 4], [1, 2, 7]]
            ]
        ]

    def test_valid_execution(self):
        """Test execution with valid inputs and return values."""
        x_list, t_list, count_mean, count_std = complex_time_3d(
            self.graph_type, self.graphed_data, self.full_hist, self.file_num,
            self.initial_time, self.final_time, self.species_name, self.time_bins, show_fig=False
        )

        self.assertIsInstance(x_list, np.ndarray)
        self.assertIsInstance(t_list, np.ndarray)
        self.assertIsInstance(count_mean, np.ndarray)
        self.assertIsInstance(count_std, np.ndarray)
        self.assertEqual(len(t_list), self.time_bins + 1)

    def test_invalid_graph_type(self):
        """Test for ValueError when invalid graph_type is provided."""
        with self.assertRaises(ValueError):
            complex_time_3d(
                3, self.graphed_data, self.full_hist, self.file_num,
                self.initial_time, self.final_time, self.species_name, self.time_bins, show_fig=False
            )

    def test_invalid_graphed_data(self):
        """Test for ValueError when invalid graphed_data is provided."""
        with self.assertRaises(ValueError):
            complex_time_3d(
                self.graph_type, 4, self.full_hist, self.file_num,
                self.initial_time, self.final_time, self.species_name, self.time_bins, show_fig=False
            )

    def test_calculation(self):
        """Test correct calculation."""
        complex_size, time_bins, count_mean, count_std = complex_time_3d(
            self.graph_type, self.graphed_data, self.full_hist, self.file_num,
            self.initial_time, self.final_time, self.species_name, self.time_bins, show_fig=False
        )

        expected_complex_size = np.array([1, 2, 3, 4, 5, 6, 7])

        expected_time_bins = np.array([0.,     20.002,  40.004,  60.006,  80.008, 100.01])

        expected_mean = np.array([[12.5,  6.5,  3.5,  0.,   0.,   0.,   0. ],
                                  [15.,   8.,   0.,   0.,   0.,   0.,   0. ],
                                  [20.,  10.,   0.,   0.,   4.,   0.,   0. ],
                                  [20.,  10.,   0.,   0.,   0.,   1.,   0. ],
                                  [20.,  10.,   0.,   0.,   0.,   0.,   2. ]])

        expected_std = np.array([[0., 0., 0., 0., 0., 0., 0.],
                                 [0., 0., 0., 0., 0., 0., 0.],
                                 [0., 0., 0., 0., 0., 0., 0.],
                                 [0., 0., 0., 0., 0., 0., 0.],
                                 [0., 0., 0., 0., 0., 0., 0.]])

        np.testing.assert_array_almost_equal(complex_size, expected_complex_size, decimal=2)

        np.testing.assert_array_almost_equal(time_bins, expected_time_bins, decimal=2)

        np.testing.assert_array_almost_equal(count_mean, expected_mean, decimal=2)

        np.testing.assert_array_almost_equal(count_std, expected_std, decimal=2)

    def test_calculation_2(self):
        """Test correct calculation."""
        complex_size, time_bins, count_mean, count_std = complex_time_3d(
            self.graph_type, self.graphed_data, self.full_hist_2, self.file_num,
            self.initial_time, self.final_time, self.species_name, self.time_bins, show_fig=False
        )

        expected_complex_size = np.array([1, 2, 3, 4, 5, 6, 7])

        expected_time_bins = np.array([0.,     20.002,  40.004,  60.006,  80.008, 100.01])

        expected_mean = np.array([[np.mean([25/2,50/2]), np.mean([13/2,26/2]), np.mean([7/2,14/2]), 0., 0., 0., 0.],
                                  [np.mean([15,30]), np.mean([8,16]), 0., 0., 0., 0., 0.],
                                  [np.mean([20,40]), np.mean([10,20]), 0., 0., np.mean([4,8]), 0., 0.],
                                  [np.mean([20,40]), np.mean([10,20]), 0., 0., 0., np.mean([1,2]), 0.],
                                  [np.mean([20,40]), np.mean([10,20]), 0., 0., 0., 0., np.mean([2,4])]])

        expected_std = np.array([[np.std([25/2,50/2]), np.std([13/2,26/2]), np.std([7/2,14/2]), 0., 0., 0., 0.],
                                 [np.std([15,30]), np.std([8,16]), 0., 0., 0., 0., 0.],
                                 [np.std([20,40]), np.std([10,20]), 0., 0., np.std([4,8]), 0., 0.],
                                 [np.std([20,40]), np.std([10,20]), 0., 0., 0., np.std([1,2]), 0.],
                                 [np.std([20,40]), np.std([10,20]), 0., 0., 0., 0., np.std([2,4])]])

        np.testing.assert_array_almost_equal(complex_size, expected_complex_size, decimal=2)

        np.testing.assert_array_almost_equal(time_bins, expected_time_bins, decimal=2)

        np.testing.assert_array_almost_equal(count_mean, expected_mean, decimal=2)

        np.testing.assert_array_almost_equal(count_std, expected_std, decimal=2)


if __name__ == "__main__":
    unittest.main()
