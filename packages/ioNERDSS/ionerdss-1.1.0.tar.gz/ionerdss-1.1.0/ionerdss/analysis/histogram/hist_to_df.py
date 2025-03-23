import pandas as pd
import os
from .hist_to_csv import hist_to_csv


def hist_to_df(FullHist: list, SpeciesList: list, OpName: str, SaveCsv: bool = True, Single: bool = False):
    """Creates a pandas dataframe from a histogram.dat (multi-species)

    Args:
        FullHist (list): holds all of the histogram data
        SpeciesList (list): list of each included species type
        OpName (str): name of the outputted .csv file
        SaveCsv (bool, optional): If a .csv file is saved as well. Defaults to True.

    Returns:
       pandas.df: Each row is a different time stamp (all times listed in column A). Each column is a different size of complex molecule (all sizes listed in row 1). Each box 
        is the number of that complex molecule at that time stamp.
    """
    hist_to_csv(FullHist, SpeciesList, OpName, Single)
    
    
    df = pd.read_csv(f'{OpName}.csv')
    if not SaveCsv:
        os.remove(f'{OpName}.csv')
    return df


