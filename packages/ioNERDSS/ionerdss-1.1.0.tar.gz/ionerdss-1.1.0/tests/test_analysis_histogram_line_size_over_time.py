import unittest
import numpy as np
from ionerdss.analysis.histogram.line_size_over_time import line_size_over_time


class TestLineSizeOverTime(unittest.TestCase):
    """Unit tests for the `line_size_over_time` function."""

    def setUp(self):
        """Set up sample histogram data for testing."""
        self.full_hist = [
            [[0.0, [1, 2], [10, 20]], [50.0, [3, 1], [30, 5]], [100.0, [2, 4], [15, 25]]],
            [[0.0, [2, 1], [12, 18]], [50.0, [4, 2], [28, 6]], [100.0, [3, 5], [18, 22]]]
        ]
        self.file_count = 2
        self.initial_time = 0.0
        self.final_time = 100.0
        self.species_list = ["A", "B"]

    def test_valid_mean_calculation(self):
        """Test correct mean calculation for species in a single complex."""
        times, means, stds = line_size_over_time(
            data_type=1, full_hist=self.full_hist, file_count=self.file_count,
            initial_time=self.initial_time, final_time=self.final_time, show_fig=False
        )
        expected_times = [0.0, 50.0, 100.0]
        expected_means = [np.mean([(1*10+2*20)/3,(2*12+1*18)/3]), np.mean([(3*30+1*5)/4,(4*28+2*6)/6]), np.mean([(2*15+4*25)/6,(3*18+5*22)/8])]
        expected_stds = [np.std([(1*10+2*20)/3,(2*12+1*18)/3]), np.std([(3*30+1*5)/4,(4*28+2*6)/6]), np.std([(2*15+4*25)/6,(3*18+5*22)/8])]
        self.assertEqual(times, expected_times)
        self.assertEqual(means, expected_means)
        self.assertEqual(stds, expected_stds)

    def test_valid_mean_calculation_exclude_size(self):
        """Test correct mean calculation for species in a single complex."""
        times, means, stds = line_size_over_time(
            data_type=1, full_hist=self.full_hist, file_count=self.file_count,
            initial_time=self.initial_time, final_time=self.final_time, exclude_size=10, show_fig=False
        )
        expected_times = [0.0, 50.0, 100.0]
        expected_means = [np.mean([(2*20)/2,(2*12+1*18)/3]), np.mean([(3*30)/3,(4*28)/4]), np.mean([(2*15+4*25)/6,(3*18+5*22)/8])]
        expected_stds = [np.std([(2*20)/2,(2*12+1*18)/3]), np.std([(3*30)/3,(4*28)/4]), np.std([(2*15+4*25)/6,(3*18+5*22)/8])]
        self.assertEqual(times, expected_times)
        self.assertEqual(means, expected_means)
        self.assertEqual(stds, expected_stds)

    def test_valid_max_calculation(self):
        """Test correct maximum calculation for species in a single complex."""
        times, max_values, stds = line_size_over_time(
            data_type=2, full_hist=self.full_hist, file_count=self.file_count,
            initial_time=self.initial_time, final_time=self.final_time, show_fig=False
        )
        expected_times = [0.0, 50.0, 100.0]
        expected_max_values = [np.mean([20, 18]), np.mean([30, 28]), np.mean([25, 22])]
        expected_stds = [np.std([20, 18]), np.std([30, 28]), np.std([25, 22])]
        self.assertEqual(times, expected_times)
        self.assertEqual(max_values, expected_max_values)
        self.assertEqual(stds, expected_stds)

    # TODO: Add test cases for multi-species histograms


if __name__ == "__main__":
    unittest.main()
