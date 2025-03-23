import unittest
from ionerdss.analysis.histogram.single_species.single_hist_obj import SingleHistogram
from ionerdss.analysis.histogram.single_species.complex_time_3d import complex_time_3d

class TestSingleHistogram(unittest.TestCase):

    def setUp(self):
        """Set up a test instance of SingleHistogram"""
        self.file_name = "./data/test_single_histogram.dat"
        self.file_num = 1
        self.initial_time = 0.512
        self.final_time = 0.513
        self.species_name = "dode"
        
        # Create an instance of SingleHistogram
        self.histogram = SingleHistogram(self.file_name, self.file_num, self.initial_time, self.final_time, self.species_name)

    def test_initialization(self):
        """Test if SingleHistogram initializes correctly and calls read_file"""
        histogram = SingleHistogram(self.file_name, self.file_num, self.initial_time, self.final_time, self.species_name)

        self.assertEqual(histogram.FileName, self.file_name)
        self.assertEqual(histogram.FileNum, self.file_num)
        self.assertEqual(histogram.InitialTime, self.initial_time)
        self.assertEqual(histogram.FinalTime, self.final_time)
        self.assertEqual(histogram.SpeciesName, self.species_name)
        self.assertEqual(len(histogram.full_hist), self.file_num)

if __name__ == "__main__":
    unittest.main()
