import numpy as np
import os
import matplotlib.pyplot as plt
from ...file_managment.save_vars_to_file import save_vars_to_file

def multi_hist_complex_count(FileName: str = 'histogram_complexes_time.dat', FileNum: int = 1, InitialTime: float = 0, FinalTime: float = 1E10,
               SpeciesList: list = ['all'], BinNums: int = 10, ExcludeSize: int = 0, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False) -> tuple:
    """
    Generate histogram of the size of target species for a multiple species system for the given species 
    and targets from the histogram_complexes_time.dat in the input file within the specified time range.

    Args:
        FileName (str): The name of the input file. Default is 'histogram_complexes_time.dat'
        FileNum (int): The number of files to read. Default is 1.
        InitialTime (float): The start time of the time range (inclusive). Default is 0.
        FinalTime (float): The end time of the time range (exclusive). Default is 1E10.
        SpeciesList (list): The list of targets for whose number will be counted as the size of the complex. Default is all species.
        BinNums (int, optional): The number of bins in the histogram. Default is 10.
        ExcludeSize (int, optional): The minimum value required to include a data point in the histogram. Default is 0.
        ShowFig (bool, optional): Whether to display the generated figures. Default is True.
        SaveFig (bool, optional): Whether to save the generated figures. Default is False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    Returns:
        the np.arrays of normalized counts, means, and standard deviations for the histograms.
    """

    FileName_head, FileName_tail = os.path.splitext(FileName)

    # Create dictionary to store count of one size
    sizeDictList = []
     
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
            temp_FileName = f"{FileName_head}_{i}{FileName_tail}"
            if not os.path.isfile(temp_FileName):
                raise FileNotFoundError(f"File {temp_FileName} does not exist.")

        sizeDict = {}
        # Open file and read line-by-line
        with open(temp_FileName, 'r') as file:
            found_InitialTime = False

            for line in file:
                # Check if line contains time information
                if line.startswith('Time (s):'):
                    time = float(line.split()[-1])   # Extract time value from line
                    if time < InitialTime:
                        continue
                    elif time >= FinalTime:
                        break
                    else:
                        found_InitialTime = True

                else:   # Line contains complex count information
                    if found_InitialTime:
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
                            if SpeciesList[0] == 'all' and len(SpeciesList) == 1:
                                size += num
                            else:
                                if speciesName in SpeciesList:
                                    size += num
                        if size > ExcludeSize:
                            if size not in sizeDict:
                                sizeDict[size] = count
                            else:
                                sizeDict[size] += count
        sizeDictList.append(sizeDict)
        
    # Combine counts of all sizes from all dictionaries
    combined_counts = {}
    for d in sizeDictList:
        for size, count in d.items():
            if size in combined_counts:
                combined_counts[size].append(count)
            else:
                combined_counts[size] = [count]

    # Calculate mean and standard deviation for each size
    mean_std = {}
    for size, counts in combined_counts.items():
        mean = np.mean(counts)
        std = np.std(counts)
        mean_std[size] = (mean, std)

    mean_std = dict(sorted(mean_std.items()))
    size_array = np.array(list(mean_std.keys()))
    mean_array = np.array([value[0] for value in mean_std.values()])
    std_array = np.array([value[1] for value in mean_std.values()])
    
    #output variables
    if SaveVars:
        save_vars_to_file({"cmplx_sizes":size_array, "cmplx_count":mean_array, "std":std_array})

    plt.hist(size_array, bins=BinNums, weights=mean_array, density=True, histtype='bar', alpha=0.75)

    plt.xlabel('Size of complex')
    plt.ylabel('Frequency')
    if SaveFig:
        plt.SaveFig('histgram_size_of_complex.png', dpi=300)
    if ShowFig:
        plt.show()
    return size_array, mean_array, std_array