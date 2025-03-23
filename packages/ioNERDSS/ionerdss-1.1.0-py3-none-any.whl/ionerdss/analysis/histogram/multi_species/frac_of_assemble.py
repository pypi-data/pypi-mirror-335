import numpy as np
import os
import matplotlib.pyplot as plt
from ...file_managment.save_vars_to_file import save_vars_to_file


def frac_of_assemble(FileName: str = 'histogram_complexes_time.dat', FileNum: int = 1, 
               Mol: str = '', Threshold: int = 2, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False) -> tuple:
    """
    Generate time dependence of the fraction of asssembled molecules from the histogram_complexes_time.dat in the input file within the specified size threshold.

    Args:
        FileName (str): The name of the input file. Default is 'histogram_complexes_time.dat'
        FileNum (int): The number of files to read. Default is 1.
        Mol (str): The name of the molecule. Default is empty string.
        Threshold (int, optional): The minimum size considered to be assembled. Default is 2.
        ShowFig (bool, optional): Whether to display the generated figures. Default is True.
        SaveFig (bool, optional): Whether to save the generated figures. Default is False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    Returns:
        the np.arrays of time, means, and standard deviations for the fraction.
    """

    FileName_head, FileName_tail = os.path.splitext(FileName)

    time_arrays = []
    frac_arrays = []
     
    for i in range(1, FileNum+1):
        # check if there is a folder named '1' in the current folder, if there is, set the temp_FileName to ./i/FileName, then check if ./i/FileName exited. if not exited, throw out a file not exit error.
        # else if FileNum is 1, check if there is file named FileName in the current folder, if there is, set the temp_FileName to FileName; if FileNum > 1, check if there is afile name FileName_head + '_' + str(i) + '.' + FileName_tail, if it is, set as the temp_FileName
        # else throw a file not found error
        temp_FileName = ""
        if os.path.isdir(str(i)):
            temp_FileName = os.path.join(str(i), FileName)
            if not os.path.isfile(temp_FileName):
                raise FileNotFoundError(f"File {temp_FileName} does not exist.")
        elif FileNum == 1:
            if os.path.isfile(FileName):
                temp_FileName = FileName
            else:
                raise FileNotFoundError(f"File {FileName} does not exist.")
        else:
            temp_FileName = f"{FileName_head}_{i}.{FileName_tail}"
            if not os.path.isfile(temp_FileName):
                raise FileNotFoundError(f"File {temp_FileName} does not exist.")

        time_list = []
        frac_list = []
        assembled_num = 0
        non_assembled_num = 0
        # Open file and read line-by-line
        with open(temp_FileName, 'r') as file:
            found_startTime = False

            for line in file:
                # Check if line contains time information
                if line.startswith('Time (s):'):
                    if found_startTime:
                        # store the previous step result
                        frac = assembled_num / (assembled_num + non_assembled_num)
                        time_list.append(time)
                        frac_list.append(frac)
                        assembled_num = 0
                        non_assembled_num = 0

                    time = float(line.split()[-1])   # Extract time value from line
                    found_startTime = True

                else:   # Line contains complex count information
                    # Extract count and complex information
                    count, complexInfoStr = line.strip().split('\t')
                    count = int(count)
                    # Split complex information into individual items
                    complexItems = complexInfoStr.rstrip('.').split('. ')
                    size = 0
                    for item in complexItems:
                        # Extract species name and count from complex information
                        speciesName, numStr = item.split(': ')
                        num = int(numStr)
                        if speciesName == Mol and num >= Threshold:
                            assembled_num = assembled_num + num * count
                        elif speciesName == Mol and num < Threshold:
                            non_assembled_num = non_assembled_num + num * count
            frac = assembled_num / (assembled_num + non_assembled_num)
            time_list.append(time)
            frac_list.append(frac)
        time_array = np.array(time_list)
        frac_array = np.array(frac_list)
        time_arrays.append(time_array)
        frac_arrays.append(frac_array)

    # Find the length of the shortest time_array and frac_array
    min_length = min([len(time_array) for time_array in time_arrays])

    # Truncate all time_arrays and frac_arrays to the shortest length
    truncated_time_arrays = [time_array[:min_length] for time_array in time_arrays]
    truncated_frac_arrays = [frac_array[:min_length] for frac_array in frac_arrays]

    # Stack the truncated time_arrays and frac_arrays
    stacked_time_arrays = np.stack(truncated_time_arrays)
    stacked_frac_arrays = np.stack(truncated_frac_arrays)

    # Compute the average and standard deviation along the first axis
    average_time_array = np.mean(stacked_time_arrays, axis=0)
    average_frac_array = np.mean(stacked_frac_arrays, axis=0)
    std_frac_array = np.std(stacked_frac_arrays, axis=0)

    #output variables
    if SaveVars:
        save_vars_to_file({"time_stamp":average_time_array, "frac_assembled_monos":average_frac_array, "std":std_frac_array})

    # Plot the average_frac_array versus average_time_array with an error band
    plt.plot(average_time_array, average_frac_array)
    plt.fill_between(average_time_array, average_frac_array - std_frac_array, average_frac_array + std_frac_array, alpha=0.2)
    plt.xlabel('Time (s)')
    plt.ylabel('Average Frac of Assembly')
    if SaveFig:
        plt.SaveFig('FracofAssembly.png', dpi=300)
    if ShowFig:
        plt.show()
    
    return average_time_array, average_frac_array, std_frac_array