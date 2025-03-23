import math
import numpy as np
import matplotlib.pyplot as plt
import warnings
from .read_transition_matrix import read_transition_matrix
from ..file_managment.save_vars_to_file import save_vars_to_file

def free_energy(FileName: str, FileNum: int, InitialTime: float, FinalTime: float,
                SpeciesName: str, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
    """ Plots the change in free energy in selected time period among different sizes of complexes.
    
    Args:
        FileName (str): The path to the '.dat' file containing the histogram data to be analyzed.
        FileNum (int): The number of the total input file. If multiple files are provided, their names should follow the naming rule listed below.
        InitialTime (float): The initial time that users desire to examine in seconds.
        FinalTime (float): The final time that users desire to examine in seconds.
        SpeciesName (str): The name of the species that users want to examine, which should also be identical with the name written in the input (.inp and .mol) files.
        ShowFig (bool, optional): If True, the plot will be shown; if False, the plot will not be shown. Defaults to True.
        SaveFig (bool, optional): If True, the plot will be saved as a '.png' file in the current directory; if False, the figure will not be saved. Defaults to False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    Returns:
        A tuple containing the following:
        - An array of the size of complexes
        - An array of the free energies calculated as -ln(P(N))/kBT, where P(N) is the probability of occurrence of the number of times N-mer is counted (including association and dissociation).
    
    Notes:
        - If multiple input files are given, the output plot will be the average value of all files and an error bar will also be included.
        - If a single file is provided, the input file should be named as its original name ('transition_matrix_time.dat').
        - If multiple files are provided, the name of the input file should also include serial number as 'transition_matrix_time_X.dat' where X = 1,2,3,4,5...
    """
    
    warnings.filterwarnings('ignore')
    
    matrix_list = [] #list of each change in matrix for every file
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    
    for transition_file_number in range(1, FileNum+1):
        #determining file name (if there are multiple or none)
        if FileNum == 1:
            temp_file_name = FileName
        else:
            temp_file_name = file_name_head + '_' + str(transition_file_number) + '.' + file_name_tail
        
        #read matrix to get initial / final readings, and add them to master list
        ti_matrix, tf_matrix = read_transition_matrix(
            temp_file_name, SpeciesName, InitialTime, FinalTime)
        matrix = tf_matrix - ti_matrix
        matrix_list.append(matrix)
    
    #magic
    sum_list_list = []
    for k in range(len(matrix_list)):
        sum_list = np.zeros(len(matrix))
        i = 0
        while i < len(matrix_list[k]):
            j = 0
            while j < len(matrix_list[k][i]):
                if i == j:
                    sum_list[i] += matrix_list[k][i][j]
                elif i > j:
                    if i % 2 == 0:
                        if j <= (i-1)/2:
                            sum_list[i] += matrix_list[k][i][j]
                    else:
                        if j <= i/2:
                            if (i-1)/2 == j:
                                sum_list[i] += matrix_list[k][i][j]/2
                            else:
                                sum_list[i] += matrix_list[k][i][j]
                else:
                    if j % 2 != 0:
                        if i <= j/2:
                            if (j-1)/2 == i:
                                sum_list[i] += matrix_list[k][i][j]/2
                            else:
                                sum_list[i] += matrix_list[k][i][j]
                        else:
                            sum_list[i] += matrix_list[k][i][j]
                    else:
                        sum_list[i] += matrix_list[k][i][j]
                j += 1
            i += 1
        sum_list_list.append(sum_list)
    energy_list_list = []
    
    #more magic
    for i in range(len(sum_list_list)):
        sum_arr = np.array(sum_list_list[i])
        sum_arr = sum_arr/sum_arr.sum()
        energy_list = np.asarray([])
        for i in sum_arr:
            if i > 0:
                energy_list = np.append(energy_list, -math.log(i))
            else:
                energy_list = np.append(energy_list, np.nan)
        energy_list_list.append(energy_list)
    
    n_list = list(range(1, 1 + len(matrix_list[0]))) # list of each size
    
    #transposing
    energy_list_list_rev = []
    for i in range(len(energy_list_list[0])):
        temp = []
        for j in range(len(energy_list_list)):
            temp.append(energy_list_list[j][i])
        energy_list_list_rev.append(temp)
    
    #calculate means and std devs
    mean_energy_list = np.array([])
    std_energy_list = np.array([])
    for energy in energy_list_list_rev:
        mean_energy_list = np.append(mean_energy_list, np.nanmean(energy))
        if FileNum != 1:
            std_energy_list = np.append(std_energy_list, np.nanstd(energy))
    
    #output variables
    if SaveVars:
        save_vars_to_file({"cmplx_size":n_list,"mean_energy":mean_energy_list,"std":std_energy_list})
    
    #show figure
    if ShowFig:
        errorbar_color = '#c9e3f6'
        plt.plot(n_list, mean_energy_list, 'C0')
        if FileNum != 1:
            plt.errorbar(n_list, mean_energy_list, yerr=std_energy_list,
                         ecolor=errorbar_color, capsize=2)
        plt.title('Free Energy')
        plt.xlabel('Number of ' + str(SpeciesName) + ' in Single Complex')
        plt.ylabel('-ln(p(N)) ($k_B$T)')
        plt.xticks(ticks=n_list)
        if SaveFig:
            plt.savefig('free_energy.png', dpi=500)
        plt.show()
    return n_list, mean_energy_list, std_energy_list


