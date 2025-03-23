import os
import numpy as np

def save_variable_to_file(variable, file_name=None, file_path=None):
    """Save a list or NumPy array of numbers to a .dat file, one number per line.

    This function takes a list or NumPy array of numbers as input, saves it to a .dat file
    with each number on a new line, and allows for customization of the file name and file
    path. If no file name is provided, the default name is "my_var". If no file path is
    provided, the default path is the current folder.

    Parameters
    ----------
    variable : list or numpy.array
        The list or NumPy array of numbers to be saved.
    file_name : str, optional
        The name of the file, by default "my_var".
    file_path : str, optional
        The abs path of the file, by default the current folder.

    Returns
    -------
    None
    """
    if not isinstance(variable, (list, np.ndarray)):
        raise ValueError("The input variable must be a list or a NumPy array of numbers.")
    
    if isinstance(variable, np.ndarray):
        variable = variable.tolist()
    
    if not all(isinstance(item, (int, float)) for item in variable):
        raise ValueError("All elements in the list or array must be numbers (integers or floats).")
    
    if file_name is None:
        file_name = "my_var" + '.dat'
    else:
        file_name = file_name + '.dat'

    if file_path is None:
        file_path = os.getcwd()
    else:
        file_path = os.path.abspath(file_path)

    file_full_path = os.path.join(file_path, file_name)

    with open(file_full_path, 'w') as f:
        for number in variable:
            f.write(f'{number}\n')
