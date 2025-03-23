import unittest
from ionerdss.analysis.histogram.single_species.hist_temp import hist_temp  # Adjust import path if needed


class TestHistTemp(unittest.TestCase):

    def setUp(self):
        """Set up sample histogram data for testing."""
        self.histogram_data = [
            [0.0, [10, 5], [1, 2]],  # Time: 0s, Complex counts: [10, 5] for sizes [1, 2]
            [50.0, [15, 8], [1, 2]],  # Time: 50s, Complex counts: [15, 8] for sizes [1, 2]
            [100.0, [20, 10], [1, 2]],  # Time: 100s, Complex counts: [20, 10] for sizes [1, 2]
        ]

    def test_valid_time_range(self):
        """Test correct output for a valid time range covering the entire dataset."""
        sizes, averages = hist_temp(self.histogram_data, 0, 100.01)

        self.assertEqual(sizes, [1, 2])
        self.assertAlmostEqual(averages[0], (10 + 15 + 20) / 3, places=2)
        self.assertAlmostEqual(averages[1], (5 + 8 + 10) / 3, places=2)

    def test_partial_time_range(self):
        """Test correct output for a time range covering part of the dataset."""
        sizes, averages = hist_temp(self.histogram_data, 0, 50.01)

        self.assertEqual(sizes, [1, 2])
        self.assertAlmostEqual(averages[0], (10 + 15) / 2, places=2)
        self.assertAlmostEqual(averages[1], (5 + 8) / 2, places=2)

    def test_single_time_point(self):
        """Test correct output for a time range covering a single time step."""
        sizes, averages = hist_temp(self.histogram_data, 50, 50.01)

        self.assertEqual(sizes, [1, 2])
        self.assertEqual(averages, [15, 8])

    def test_no_matching_time_steps(self):
        """Test function behavior when no time steps match the given range."""
        sizes, averages = hist_temp(self.histogram_data, 200, 300)

        self.assertEqual(sizes, [])
        self.assertEqual(averages, [])

    def test_time_bin_out_of_bounds(self):
        """Test function handles time bins outside available data range correctly."""
        sizes, averages = hist_temp(self.histogram_data, -50, 200)

        self.assertEqual(sizes, [1, 2])
        self.assertAlmostEqual(averages[0], (10 + 15 + 20) / 3, places=2)
        self.assertAlmostEqual(averages[1], (5 + 8 + 10) / 3, places=2)

    def test_unsorted_time_data(self):
        """Test function works correctly even if time steps are unordered."""
        unsorted_hist_data = [
            [50.0, [15, 8], [1, 2]],
            [0.0, [10, 5], [1, 2]],
            [100.0, [20, 10], [1, 2]],
        ]

        sizes, averages = hist_temp(unsorted_hist_data, 0, 100.01)

        self.assertEqual(sizes, [1, 2])
        self.assertAlmostEqual(averages[0], (10 + 15 + 20) / 3, places=2)
        self.assertAlmostEqual(averages[1], (5 + 8 + 10) / 3, places=2)

if __name__ == "__main__":
    unittest.main()