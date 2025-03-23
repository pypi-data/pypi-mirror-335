import unittest
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch
from ionerdss.analysis.file_managment.save_vars_to_file import save_vars_to_file
from ionerdss.analysis.histogram.single_species.hist_complex_count import hist_complex_count

class TestHistComplexCount(unittest.TestCase):
    """Unit tests for the `hist_complex_count` function."""

    def setUp(self):
        """Set up test data for histogram calculations."""
        # Simulated full_hist data (list of files, each file contains timestamps)
        self.full_hist_single = [
            [  # Single file
                [0.0, [2, 3], [1, 3]],   # time, counts, sizes
                [50.0, [5, 2], [1, 2]], 
                [100.0, [3, 4], [2, 5]]
            ]
        ]

        self.full_hist_multiple = [
            [  # First file
                [0.0, [2, 3], [1, 2]],   
                [50.0, [5, 2], [3, 1]], 
                [100.0, [3, 4], [2, 3]]
            ],
            [  # Second file
                [0.0, [1, 2], [1, 3]],   
                [50.0, [4, 1], [1, 2]], 
                [100.0, [2, 3], [2, 3]]
            ]
        ]

    def test_valid_single_file(self):
        """Test correct histogram calculation for a single file."""
        sizes, means, stds = hist_complex_count(
            self.full_hist_single, file_num=1, initial_time=0, final_time=100, species_name="Test", show_fig=False
        )
        
        expected_sizes = np.array([1, 2, 3, 4, 5])
        expected_means = np.array([(2+5)/3, (2+3)/3, 3/3, 0/3, 4/3])
        expected_stds = np.array([0, 0, 0, 0, 0])

        self.assertTrue(np.array_equal(sizes, expected_sizes))
        self.assertTrue(np.array_equal(means, expected_means))
        self.assertTrue(np.array_equal(stds, expected_stds))

    def test_valid_single_file_bin_size(self):
        """Test correct histogram calculation for a single file."""
        sizes, means, stds = hist_complex_count(
            self.full_hist_single, file_num=1, initial_time=0, final_time=100, species_name="Test", bar_size=2, show_fig=False
        )
        
        expected_sizes = np.array([1, 3, 5])
        expected_means = np.array([(2+5)/3 + (2+3)/3, 3/3 + 0/3, 4/3])
        expected_stds = np.array([0, 0, 0])

        self.assertTrue(np.array_equal(sizes, expected_sizes))
        self.assertTrue(np.array_equal(means, expected_means))
        self.assertTrue(np.array_equal(stds, expected_stds))

    def test_valid_multiple_files(self):
        """Test correct histogram calculation for multiple files."""
        sizes, means, stds = hist_complex_count(
            self.full_hist_multiple, file_num=2, initial_time=0, final_time=100, species_name="Test", show_fig=False
        )
        
        expected_sizes = np.array([1, 2, 3])
        expected_means = np.array([np.mean([(2+2)/3, (1+4)/3]), np.mean([(3+3)/3, (1+2)/3]), np.mean([(5+4)/3, (2+3)/3])])
        expected_stds = np.array([np.std([(2+2)/3, (1+4)/3]), np.std([(3+3)/3, (1+2)/3]), np.std([(5+4)/3, (2+3)/3])])

        self.assertTrue(np.array_equal(sizes, expected_sizes))
        self.assertTrue(np.array_equal(means, expected_means))
        self.assertTrue(np.array_equal(stds, expected_stds))

    def test_valid_multiple_files_bin_size(self):
        """Test correct histogram calculation for multiple files."""
        sizes, means, stds = hist_complex_count(
            self.full_hist_multiple, file_num=2, initial_time=0, final_time=100, species_name="Test", bar_size=2, show_fig=False
        )
        
        expected_sizes = np.array([1, 3])
        expected_means = np.array([np.mean([(2+2)/3+(3+3)/3, (1+4)/3+(1+2)/3]), np.mean([(5+4)/3, (2+3)/3])])
        expected_stds = np.array([np.std([(2+2)/3+(3+3)/3, (1+4)/3+(1+2)/3]), np.std([(5+4)/3, (2+3)/3])])

        self.assertTrue(np.array_equal(sizes, expected_sizes))
        self.assertTrue(np.array_equal(means, expected_means))
        self.assertTrue(np.array_equal(stds, expected_stds))

if __name__ == "__main__":
    unittest.main()
