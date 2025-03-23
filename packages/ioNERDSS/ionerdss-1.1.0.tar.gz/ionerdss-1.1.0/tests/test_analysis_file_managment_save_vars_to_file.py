import unittest
import os
import numpy as np
from ionerdss.analysis.file_managment.save_vars_to_file import *


class TestAddEmptyLists(unittest.TestCase):
    """Tests for the `add_empty_lists` function."""

    def test_empty_list(self):
        """Test handling of an empty list."""
        self.assertEqual(add_empty_lists([]), ["Empty List"])

    def test_nested_empty_lists(self):
        """Test handling of nested empty lists."""
        self.assertEqual(add_empty_lists([[], [1, 2], []]), [["Empty List"], [1, 2], ["Empty List"]])

    def test_list_with_numpy_array(self):
        """Test handling of lists containing NumPy arrays."""
        np_array = np.array([])
        result = add_empty_lists([[], np_array, [1, 2, 3]])
        self.assertEqual(result, [["Empty List"], ["Empty List"], [1, 2, 3]])

    def test_list_with_non_empty_values(self):
        """Ensure non-list values remain unchanged."""
        input_data = [1, "text", [2, 3, []]]
        expected_output = [1, "text", [2, 3, ["Empty List"]]]
        self.assertEqual(add_empty_lists(input_data), expected_output)


class TestSaveVarsToFile(unittest.TestCase):
    """Tests for the `save_vars_to_file` function."""

    def setUp(self):
        """Create a temporary test directory before each test."""
        self.test_dir = "test_vars"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Remove test files and directory after each test."""
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def test_save_number(self):
        """Test saving an integer and float to text files."""
        save_vars_to_file({"num": 42, "pi": 3.14}, self.test_dir)
        
        with open(os.path.join(self.test_dir, "num_number.txt"), "r") as f:
            self.assertEqual(f.read(), "42")
        
        with open(os.path.join(self.test_dir, "pi_number.txt"), "r") as f:
            self.assertEqual(f.read(), "3.14")

    def test_save_string(self):
        """Test saving a string to a text file."""
        save_vars_to_file({"message": "Hello, world!"}, self.test_dir)

        with open(os.path.join(self.test_dir, "message_string.txt"), "r") as f:
            self.assertEqual(f.read(), "Hello, world!")

    def test_save_1d_list(self):
        """Test saving a 1D list to a CSV file."""
        save_vars_to_file({"numbers": [1, 2, 3]}, self.test_dir)

        with open(os.path.join(self.test_dir, "numbers_list.csv"), "r") as f:
            self.assertEqual(f.read(), "1,2,3")

    def test_save_2d_list(self):
        """Test saving a 2D list to a CSV file."""
        save_vars_to_file({"matrix": [[1, 2, 3], [4, 5, 6]]}, self.test_dir)

        with open(os.path.join(self.test_dir, "matrix_list.csv"), "r") as f:
            self.assertEqual(f.read(), "1,2,3\n4,5,6\n")

    def test_save_empty_list(self):
        """Test saving an empty list."""
        save_vars_to_file({"empty": []}, self.test_dir)

        with open(os.path.join(self.test_dir, "empty_list.csv"), "r") as f:
            self.assertEqual(f.read(), "Empty List")

    def test_directory_creation(self):
        """Test that the directory is created if it doesn't exist."""
        temp_dir = "temp_test_dir"
        save_vars_to_file({"temp": 123}, temp_dir)
        self.assertTrue(os.path.exists(temp_dir))

        # Cleanup
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)


if __name__ == "__main__":
    unittest.main()
