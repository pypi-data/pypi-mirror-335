from .read_file import read_file
from .complex_time_3d import complex_time_3d
from ..line_size_over_time import line_size_over_time
from .hist_complex_count import hist_complex_count
from ..hist_to_csv import hist_to_csv
from ..hist_to_df import hist_to_df

class SingleHistogram ():
    """Single Histogram object that holds all data from a histogram.dat to be interpreting in many different ways
    """

    def __init__(self,FileName: str, FileNum: int, InitialTime: float, FinalTime: float, SpeciesName: str):
        """Will initilize the object by reading through the inputted file(s)

        Args:
            FileName (str): file location (relative) histogram.dat that will be read
            FileNum (int): Number of the total input files (file names should be [fileName]_1,[fileName]_2,...)
            InitialTime (float): The starting time. Must not be smaller / larger then times in file.
            FinalTime (float): The ending time. Must not be smaller / larger then times in file.
            SpeciesName (str): The name of the species you want to examine. Should be in the .dat file.        
        """


        #Initilize variables
        self.full_hist = []
        self.FileName = FileName
        self.FileNum = FileNum
        self.InitialTime = InitialTime
        self.FinalTime = FinalTime
        self.SpeciesName = SpeciesName
        
        #setup file naming
        file_name_head = FileName.split('.')[0]
        file_name_tail = FileName.split('.')[1]

        for histogram_file_number in range(1, FileNum+1):
            
            #determining file name (if there are multiple or none)
            if FileNum == 1:
                temp_file_name = FileName
            else:
                temp_file_name = file_name_head + '_' + str(histogram_file_number) + '.' + file_name_tail
            
            #load in the file
            temp_hist = read_file(temp_file_name,SpeciesName)
            self.full_hist.append(temp_hist)
    

    ##Count of monomers in each type / complexes of each type over time (3d)
    def heatmap_complex_count(self, TimeBins: int, xBarSize: int = 1, ShowFig: bool = True,
                        ShowMean: bool = False, ShowStd: bool = False, SaveFig: bool = False, SaveVars: bool = False):
        """Creates a 2D Heatmap from a histogram.dat file that represents the average number of each complex size, over time.

        Args:
            TimeBins (int): The number of bins that the selected time period is divided into.
            xBarSize (int, optional): The size of each data bar in the x-dimension. Defaults to 1.
            ShowFig (bool, optional): If the plot is shown. Defaults to True.
            ShowMean (bool, optional): If means will be shown in each box. Defaults to False.
            ShowStd (bool, optional): If std values will be shown in each box. Defaults to False.
            SaveFig (bool, optional): If the plot is saved. Defaults to False.
            SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.


        Returns:
            2D heatmap. X-axis: size of complex species. Y-axis = time 'bins'. Color = relative number of each species.
        """
        
        return complex_time_3d(1,1,self.full_hist, self.FileNum, self.InitialTime, self.FinalTime,
                self.SpeciesName, TimeBins, xBarSize, ShowFig,
                ShowMean, ShowStd, SaveFig, SaveVars)


    def heatmap_monomer_count(self,TimeBins: int, xBarSize: int = 1, ShowFig: bool = True,
                                    ShowMean: bool = False, ShowStd: bool = False, SaveFig: bool = False, SaveVars: bool = False):
        """Creates a 2D Heatmap from a histogram.dat file that shows average number of monomers in each complex size over time.

        Args:
            TimeBins (int): The number of bins that the selected time period is divided into.
            xBarSize (int, optional): The size of each data bar in the x-dimension. Defaults to 1.
            ShowFig (bool, optional): If the plot is shown. Defaults to True.
            ShowMean (bool, optional): If means will be shown in each box. Defaults to False.
            ShowStd (bool, optional): If std values will be shown in each box. Defaults to False.
            SaveFig (bool, optional): If the plot is saved. Defaults to False.
            SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.


        Returns:
            2D heatmap. X-axis = size of complex species. Y-axis = time. Color = total number of corresponding monomers in N-mers.
        """

        return complex_time_3d(1,2,self.full_hist, self.FileNum, self.InitialTime, self.FinalTime,
                self.SpeciesName, TimeBins, xBarSize, ShowFig,
                ShowMean, ShowStd, SaveFig, SaveVars)      


    def heatmap_monomer_fraction(self,TimeBins: int, xBarSize: int = 1, ShowFig: bool = True,
                                ShowMean: bool = False, ShowStd: bool = False, SaveFig: bool = False, SaveVars: bool = False):
        """Generates a 2D histogram from histogram.dat of the % of the original monomers forming into different complex sizes over time

        Args:
            TimeBins (int): The number of bins that the selected time period is divided into.
            xBarSize (int, optional): The size of each data bar in the x-dimension. Defaults to 1.
            ShowFig (bool, optional): If the plot is shown. Defaults to True.
            ShowMean (bool, optional): If means will be shown in each box. Defaults to False.
            ShowStd (bool, optional): If std values will be shown in each box. Defaults to False.
            SaveFig (bool, optional): If the plot is saved. Defaults to False.
            SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.


        Returns:
            2D heatnao. X-axis = complex species size. Y-axis = time. Color = fraction of monomers forming into that complex at that time
        """
        
        return complex_time_3d(1,3,self.full_hist, self.FileNum, self.InitialTime, self.FinalTime,
                self.SpeciesName, TimeBins, xBarSize, ShowFig,
                ShowMean, ShowStd, SaveFig, SaveVars)
        

    def hist_3d_complex_count(self,TimeBins: int, xBarSize: int = 1, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
        """Takes in a histogram.dat file from NERDSS, and creates a 3D histogram that represents the average count each complex size, over time.

        Args:
            TimeBins (int): The number of bins that the selected time period is divided into.
            xBarSize (int, optional): The size of each data bar in the x-dimension. Defaults to 1.
            ShowFig (bool, optional): If the plot is shown. Defaults to True.
            SaveFig (bool, optional): If the plot is saved. Defaults to False.
            SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.


        Returns:
            Returns a 3D histogram representing the aver count of each complex over time. X-axis = species type/size. Y-axis = averaged time. Z-axis = relative occurance.
        """

        return complex_time_3d(2,1,self.full_hist, self.FileNum, self.InitialTime, self.FinalTime,
                self.SpeciesName, TimeBins, xBarSize, ShowFig,
                False, False, SaveFig, SaveVars)


    def hist_3d_monomer_count(self,TimeBins: int, xBarSize: int = 1, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
        """Takes in a histogram.dat file from NERDSS, and creates a 3D histogram that shows average number of monomers in each complex size over time.

        Args:
            TimeBins (int): The number of bins that the selected time period is divided into.
            xBarSize (int, optional): The size of each data bar in the x-dimension. Defaults to 1.
            ShowFig (bool, optional): If the plot is shown. Defaults to True.
            SaveFig (bool, optional): If the plot is saved. Defaults to False.
            SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.


        Returns:
            Returns a 3D histogram representing the aver count of each complex over time. X-axis = species type/size. Y-axis = averaged time. Z-axis = relative occurance.
        """

        return complex_time_3d(2,2,self.full_hist, self.FileNum, self.InitialTime, self.FinalTime,
                self.SpeciesName, TimeBins, xBarSize, ShowFig,
                False, False, SaveFig, SaveVars)


    def hist_3d_monomer_fraction(self,TimeBins: int, xBarSize: int = 1, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
        """Takes in a histogram.dat file from NERDSS, and creates a 3D histogram that shows % of monomers in each complex size over time.

        Args:
            TimeBins (int): The number of bins that the selected time period is divided into.
            xBarSize (int, optional): The size of each data bar in the x-dimension. Defaults to 1.
            ShowFig (bool, optional): If the plot is shown. Defaults to True.
            SaveFig (bool, optional): If the plot is saved. Defaults to False.
            SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.


        Returns:
            Returns a 3D histogram representing the aver count of each complex over time. X-axis = species type/size. Y-axis = averaged time. Z-axis = relative occurance.
        """

        return complex_time_3d(2,3,self.full_hist, self.FileNum, self.InitialTime, self.FinalTime,
                self.SpeciesName, TimeBins, xBarSize, ShowFig,
                False, False, SaveFig, SaveVars)


    ##Number of complexes over time (2d)
    def line_mean_complex_size(self, ExcludeSize: int = 0, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
        """Creates graph of the mean number of species in a single complex molecule over a time period.

        Args:
            ExcludeSize (int): Monomers in the complex that are smaller or equal to this number will not be included. 
            ShowFig (bool, optional): If the plot is shown. Defaults to True.
            SaveFig (bool, optional): If the plot is saved. Defaults to False.
            SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

        Returns:
            graph. X-axis = time. Y-axis = mean number of species in a single complex molecule.
        """
        return line_size_over_time(Data = 1, full_hist = self.full_hist, FileNum = self.FileNum, InitialTime = self.InitialTime, FinalTime = self.FinalTime,
                SpeciesName = self.SpeciesName, ExcludeSize = ExcludeSize, ShowFig = ShowFig, SaveFig = SaveFig, SaveVars = SaveVars)


    def line_max_complex_size(self, ExcludeSize: int = 0, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
        """Creates graph of the max number of species in a single complex molecule over a time period.

        Args:
            ExcludeSize (int, optional): Monomers in the complex that are smaller or equal to this number will not be included. 
            ShowFig (bool, optional): If the plot is shown. Defaults to True.
            SaveFig (bool, optional): If the plot is saved. Defaults to False.
            SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

        Returns:
            graph. X-axis = time. Y-axis = max number of species in a single complex molecule.
        """  
        return line_size_over_time(Data = 2, full_hist = self.full_hist, FileNum = self.FileNum, InitialTime = self.InitialTime, FinalTime = self.FinalTime,
                SpeciesName = self.SpeciesName, ExcludeSize = ExcludeSize, ShowFig = ShowFig, SaveFig = SaveFig, SaveVars=SaveVars)


    ##Baby Basic Histogram
    def hist_complex_count(self, BarSize: int = 1, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
        """Creates histogram of the average number of complex species that have a certain number of species.

        Args:
            ExcludeSize (int, optional): Monomers in the complex that are smaller or equal to this number will not be included. 
            ShowFig (bool, optional): If the plot is shown. Defaults to True.
            SaveFig (bool, optional): If the plot is saved. Defaults to False.
            SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.


        Returns:
            Histogram. X-axis = # of species in a complexes. Y-axis = relative count of each complex over the whole timeframe
        """
        return hist_complex_count(full_hist=self.full_hist, FileNum=self.FileNum,InitialTime= self.InitialTime, FinalTime= self.FinalTime, 
                           SpeciesName=self.SpeciesName, BarSize=BarSize, ShowFig=ShowFig, SaveFig=SaveFig, SaveVars=SaveVars)


    ##general histogram functions
    def hist_to_csv(self,OpName: int = "histogram"):
        """Creates a .csv (spreadsheet) file from a histogram.dat file (multi-species)

        Args:
            OpName (str, Optional = "histogram"): what the outputted .csv file will be named

        Returns:
            histogram.csv file: Each row is a different time stamp (all times listed in column A). Each column is a different size of complex molecule (all sizes listed in row 1). Each box 
            is the number of that complex molecule at that time stamp.
        """  
        return hist_to_csv(self.full_hist, [self.SpeciesName], OpName, True)

    def hist_to_df(self, OpName: int = "histogram", SaveCsv: bool = True):
        """Creates a pandas dataframe from a histogram.dat (multi-species)

        Args:
            OpName (str, Optional = "histogram"): what the outputted .csv file will be named
            SaveCsv (bool, optional): If a .csv file is saved as well. Defaults to True.

        Returns:
            pandas.df: Each row is a different time stamp (all times listed in column A). Each column is a different size of complex molecule (all sizes listed in row 1). Each box 
                is the number of that complex molecule at that time stamp.
        """
        return hist_to_df(self.full_hist, [self.SpeciesName], OpName, SaveCsv, True)
