import os
import unittest
from tempfile import NamedTemporaryFile
from ionerdss.analysis.histogram.single_species.read_file import read_file


class TestReadFile(unittest.TestCase):
    """Unit tests for the `read_file` function."""

    def setUp(self):
        """Create a temporary file before each test."""
        self.test_file = NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
        self.test_file_path = self.test_file.name

    def tearDown(self):
        """Remove the temporary file after each test."""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_valid_file_parsing(self):
        """Test that the function correctly parses a valid histogram.dat file."""
        self.test_file.write(
"""Time (s): 0.453
1	dode: 3. 
4	dode: 10. 
3	dode: 7. 
4	dode: 8. 
2	dode: 6. 
4	dode: 11. 
4	dode: 9. 
1	dode: 12. 
Time (s): 0.454
1	dode: 3. 
5	dode: 10. 
3	dode: 7. 
4	dode: 8. 
2	dode: 6. 
4	dode: 11. 
4	dode: 9. 
1	dode: 15. 
Time (s): 0.455
1	dode: 3. 
6	dode: 10. 
3	dode: 7. 
4	dode: 8. 
2	dode: 6. 
4	dode: 11. 
4	dode: 9. 
1	dode: 14. 
Time (s): 0.456
1	dode: 3. 
7	dode: 10. 
3	dode: 7. 
4	dode: 8. 
2	dode: 6. 
4	dode: 11. 
4	dode: 9. 
1	dode: 13. 
""")
        self.test_file.close()

        expected_output = [
            [0.453, [1, 4, 3, 4, 2, 4, 4, 1], [3, 10, 7, 8, 6, 11, 9, 12]],
            [0.454, [1, 5, 3, 4, 2, 4, 4, 1], [3, 10, 7, 8, 6, 11, 9, 15]],
            [0.455, [1, 6, 3, 4, 2, 4, 4, 1], [3, 10, 7, 8, 6, 11, 9, 14]],
            [0.456, [1, 7, 3, 4, 2, 4, 4, 1], [3, 10, 7, 8, 6, 11, 9, 13]],
        ]

        self.assertEqual(read_file(self.test_file_path, "dode"), expected_output)

    def test_missing_file_error(self):
        """Test that the function raises FileNotFoundError when the file does not exist."""
        with self.assertRaises(FileNotFoundError):
            read_file("non_existent_file.dat", "dode")

    def test_missing_species_error(self):
        """Test that the function raises ValueError when the species is not found in the file."""
        self.test_file.write(
"""Time (s): 0.453
1	dode: 3. 
4	dode: 10. 
3	dode: 7. 
4	dode: 8. 
2	dode: 6. 
4	dode: 11. 
4	dode: 9. 
1	dode: 12. 
Time (s): 0.454
1	dode: 3. 
4	dode: 10. 
3	dode: 7. 
4	dode: 8. 
2	dode: 6. 
4	dode: 11. 
4	dode: 9. 
1	dode: 12. 
Time (s): 0.455
1	dode: 3. 
4	dode: 10. 
3	dode: 7. 
4	dode: 8. 
2	dode: 6. 
4	dode: 11. 
4	dode: 9. 
1	dode: 12. 
Time (s): 0.456
1	dode: 3. 
4	dode: 10. 
3	dode: 7. 
4	dode: 8. 
2	dode: 6. 
4	dode: 11. 
4	dode: 9. 
1	dode: 12. 
""")
        self.test_file.close()

        with self.assertRaises(ValueError):
            read_file(self.test_file_path, "SpeciesA")

if __name__ == "__main__":
    unittest.main()