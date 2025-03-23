import pandas as pd
import os
from .xyz_to_csv import xyz_to_csv


def xyz_to_df(FileName: str, LitNum: int, SaveCsv: bool = True):
    """Converts a .xyz file to a pandas.DataFrame for a specific or entire time frame.

    Args:
        FileName (str): The path to the input .xyz file, usually named 'trajectory.xyz'.
        LitNum (int): The number of iterations to examine. If -1, the entire iteration will be extracted.
        SaveCsv (bool): Whether to save the corresponding .csv file (default: True).

    Returns:
        A pandas.DataFrame containing 5 columns: number of iteration, species name, x, y, and z coordinates.

    Description:
        This function enables users to convert the output .xyz file by NERDSS simulation into a pandas.DataFrame of a specific or entire time frame. The generated DataFrame will contain 5 columns: number of iteration, species name, x, y, and z coordinates.

    Sample:
        df = xyz_to_df('/Users/UserName/Documents/trajectory.xyz', 100000000, True) # Extracts iteration 100000000 and saves the corresponding .csv file
        df = xyz_to_df('/Users/UserName/Documents/trajectory.xyz', -1, False) # Extracts the entire iteration and deletes the generated .csv file
    """
    xyz_to_csv(FileName, LitNum)
    if LitNum != -1:
        write_file_name = 'trajectory_' + str(LitNum) + '.csv'
    else:
        write_file_name = 'trajectory_full.csv'
    df = pd.read_csv(write_file_name)
    if not SaveCsv:
        os.remove(write_file_name)
    return df


