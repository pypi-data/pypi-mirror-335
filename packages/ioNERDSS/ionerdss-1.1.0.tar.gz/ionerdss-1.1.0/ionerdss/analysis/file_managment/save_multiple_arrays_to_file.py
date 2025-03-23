import os
import numpy as np

def save_multiple_arrays_to_file(arrays, file_name=None, file_path=None):
    """
    Save multiple NumPy arrays of numbers to a .dat file. Each array is stored on one column

    This function takes a list of arrays as input, saves it to a .dat file
    with each array on a column, and allows for customization of the file name and file
    path. If no file name is provided, the default name is "my_arrays". If no file path is
    provided, the default path is the current folder.

    Parameters
    ----------
    arrays : list of numpy.arrays
        The list of arrays to be saved.
    file_name : str, optional
        The name of the file, by default "my_arrays".
    file_path : str, optional
        The abs path of the file, by default the current folder.

    Returns
    -------
    None
    """
    if not isinstance(arrays, (list, np.ndarray)):
        raise ValueError("The input variable must be a list or a NumPy array of numbers.")
    
    if isinstance(arrays, np.ndarray):
        arrays = arrays.tolist()
    
    if not all(isinstance(item, np.ndarray) for item in arrays):
        raise ValueError("All elements in the list or array must be np.array.")
    
    if file_name is None:
        file_name = "my_arrays" + '.dat'
    else:
        file_name = file_name + '.dat'

    if file_path is None:
        file_path = os.getcwd()
    else:
        file_path = os.path.abspath(file_path)

    file_full_path = os.path.join(file_path, file_name)

    # combine the arrays in the list arrays vertically to create a 2D array
    data = np.vstack(arrays).T

    # save the data to a data file named file_full_path
    np.savetxt(file_full_path, data, delimiter=',')
