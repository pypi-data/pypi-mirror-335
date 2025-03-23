import numpy as np
import matplotlib.pyplot as plt
import warnings
from .read_transition_matrix import read_transition_matrix
from ..file_managment.save_vars_to_file import save_vars_to_file

def dissociate_prob_asymmetric(FileName: str, FileNum: int, InitialTime: float, FinalTime: float,
                               SpeciesName: str, DivideSize: int = 2, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
    """
    Create a line plot representing the probability of dissociation of complexes of different sizes into other complexes of different sizes.

    Args:
        FileName (str): The path to the '.dat' file containing the histogram data to be analyzed.
        FileNum (int): The number of the total input file. If multiple files are provided, their names should follow the naming rule listed below.
        InitialTime (float): The initial time that users desire to examine.
        FinalTime (float): The final time that users desire to examine.
        SpeciesName (str): The name of the species that users want to examine, which should also be identical with the name written in the input (.inp and .mol) files.
        DivideSize (int, optional): The value that separates the size of the dissociate complex. Defaults to 2.
        ShowFig (bool, optional): If True, the plot will be shown; if False, the plot will not be shown. Defaults to True.
        SaveFig (bool, optional): If True, the plot will be saved as a '.png' file in the current directory; if False, the figure will not be saved. Defaults to False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    Returns:
        A tuple containing the following:
        - np.ndarray: an array of the size of complexes
        - np.ndarray: an array of the dissociate probabilities when complexes dissociate into smaller complexes
        - np.ndarray: an array of the dissociate probabilities when complexes dissociate into larger complexes

    Notes:
        - If multiple input files are given, the output plot will be the average value of all files and an error bar will also be included.
        - 'Asymmetric' in the function name means that for the dissociate reaction, only the complexes of smaller size dissociating from the original one is counted as dissociate event asymmetrically.
        - For example, if a heptamer dissociates into a tetramer and a trimer, then this event is counted only once, which is heptamer dissociates to trimer.
        - If multiple input files are given, their names should follow the naming rule listed below.
        - If a single file is provided, the input file should be named as its original name ('transition_matrix_time.dat').
        - If multiple files are provided, the name of the input file should also include serial number as 'transition_matrix_time_X.dat' where X = 1,2,3,4,5...
    """
    
    warnings.filterwarnings('ignore')
    
    matrix_list = []
 
    #create name head/tail
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    
    #for each transition matrix file input
    for matrix_file_number in range(1, FileNum+1):
        
        #determining file name (if there are multiple or none)
        if FileNum == 1:
            temp_file_name = FileName
        else:
            temp_file_name = file_name_head + '_' + str(matrix_file_number) + '.' + file_name_tail
        
        #reads file and determines difference
        ti_matrix, tf_matrix = read_transition_matrix(
            temp_file_name, SpeciesName, InitialTime, FinalTime)
        matrix = tf_matrix - ti_matrix
        matrix_list.append(matrix)
    
    #magic
    above = []
    equal = []
    below = []
    for k in range(len(matrix_list)):
        above_temp = np.zeros(len(matrix_list[0][0]))
        equal_temp = np.zeros(len(matrix_list[0][0]))
        below_temp = np.zeros(len(matrix_list[0][0]))
        i = 0
        while i < len(matrix_list[k][0]):
            j = 0
            while j < len(matrix_list[k][i]):
                if i > j:
                    if i % 2 == 0:
                        if j <= (i-1)/2:
                            if j + 1 == DivideSize:
                                equal_temp[i] += matrix_list[k][j][i]
                            elif j + 1 > DivideSize:
                                above_temp[i] += matrix_list[k][j][i]
                            else:
                                below_temp[i] += matrix_list[k][j][i]
                    else:
                        if j <= int(i/2):
                            if (i-1)/2 == j:
                                if j + 1 == DivideSize:
                                    equal_temp[i] += matrix_list[k][j][i]/2
                                elif j + 1 > DivideSize:
                                    above_temp[i] += matrix_list[k][j][i]/2
                                else:
                                    below_temp[i] += matrix_list[k][j][i]/2
                            else:
                                if j + 1 == DivideSize:
                                    equal_temp[i] += matrix_list[k][j][i]
                                elif j + 1 > DivideSize:
                                    above_temp[i] += matrix_list[k][j][i]
                                else:
                                    below_temp[i] += matrix_list[k][j][i]
                j += 1
            i += 1
        above.append(above_temp)
        equal.append(equal_temp)
        below.append(below_temp)
    
    #more magic
    above_prob = []
    equal_prob = []
    below_prob = []
    for i in range(len(above)):
        above_prob_temp = np.array([])
        equal_prob_temp = np.array([])
        below_prob_temp = np.array([])
        for j in range(len(above[0])):
            sum = above[i][j] + equal[i][j] + below[i][j]
            if sum != 0:
                above_prob_temp = np.append(above_prob_temp, above[i][j]/sum)
                equal_prob_temp = np.append(equal_prob_temp, equal[i][j]/sum)
                below_prob_temp = np.append(below_prob_temp, below[i][j]/sum)
            else:
                above_prob_temp = np.append(above_prob_temp, np.nan)
                equal_prob_temp = np.append(equal_prob_temp, np.nan)
                below_prob_temp = np.append(below_prob_temp, np.nan)
        above_prob.append(above_prob_temp)
        equal_prob.append(equal_prob_temp)
        below_prob.append(below_prob_temp)
    
    #transpose
    above_prob_rev = []
    for i in range(len(above_prob[0])):
        temp = []
        for j in range(len(above_prob)):
            temp.append(above_prob[j][i])
        above_prob_rev.append(temp)
    equal_prob_rev = []
    for i in range(len(equal_prob[0])):
        temp = []
        for j in range(len(equal_prob)):
            temp.append(equal_prob[j][i])
        equal_prob_rev.append(temp)
    below_prob_rev = []
    for i in range(len(below_prob[0])):
        temp = []
        for j in range(len(below_prob)):
            temp.append(below_prob[j][i])
        below_prob_rev.append(temp)
    
    #calculate means and stds devss
    mean_above = []
    mean_equal = []
    mean_below = []
    std_above = []
    std_equal = []
    std_below = []
   
   #for every column (across all files) determine mean / std
    if FileNum != 1: 
        for i in range(len(above_prob_rev)):
            if np.any(above_prob_rev[i] != above_prob_rev[i-1]) or i == 0:
                mean_above.append(np.nanmean(above_prob_rev[i]))
                std_above.append(np.nanstd(above_prob_rev[i]))
            else:
                mean_above.append(mean_above[i-1])
                std_above.append(std_above[i-1])
            
            if np.any(equal_prob_rev[i] != equal_prob_rev[i-1]) or i == 0:
                mean_equal.append(np.nanmean(equal_prob_rev[i]))
                std_equal.append(np.nanstd(equal_prob_rev[i]))
            else:
                mean_equal.append(mean_equal[i-1])
                std_equal.append(std_equal[i-1])

            if np.any(below_prob_rev[i] != below_prob_rev[i-1]) or i == 0:
                mean_below.append(np.nanmean(below_prob_rev[i]))
                std_below.append(np.nanstd(below_prob_rev[i]))
            else:
                mean_below.append(mean_below[i-1])        
                std_below.append(std_below[i-1])
    else:
        for i in range(len(above_prob_rev)):
            mean_above.append(above_prob_rev[i])
            mean_equal.append(equal_prob_rev[i])
            mean_below.append(below_prob_rev[i])

    mean_above = np.nan_to_num(mean_above)
    mean_equal = np.nan_to_num(mean_equal)
    mean_below = np.nan_to_num(mean_below)
    
    #create list of complex sizes
    n_list = list(range(1, 1 + len(matrix_list[0])))

    #output variables
    if SaveVars:
        save_vars_to_file({"cmplx_size":n_list,"mean_dissociate_probability":[mean_above, mean_equal, mean_below],"std":[std_above, std_equal, std_below]})
    
    #show figure
    if ShowFig:
        errorbar_color_1 = '#c9e3f6'
        errorbar_color_2 = '#ffe7d2'
        errorbar_color_3 = '#d7f4d7'
        plt.plot(n_list, mean_above, 'C0')
        plt.plot(n_list, mean_equal, 'C1')
        plt.plot(n_list, mean_below, 'C2')
        if FileNum != 1:
            plt.errorbar(n_list, mean_above, yerr=std_above,
                         ecolor=errorbar_color_1, capsize=2)
            plt.errorbar(n_list, mean_equal, yerr=std_equal,
                         ecolor=errorbar_color_2, capsize=2)
            plt.errorbar(n_list, mean_below, yerr=std_below,
                         ecolor=errorbar_color_3, capsize=2)
        plt.legend(['Dissociate Size > ' + str(DivideSize), 'Dissociate Size = ' +
                    str(DivideSize), 'Dissociate Size < ' + str(DivideSize)])
        plt.xlabel('Number of ' + str(SpeciesName) + ' in Single Complex')
        plt.ylabel('Probability')
        plt.xticks(ticks=n_list)
        plt.title('Asymmetric Dissociation Probability')
        if SaveFig:
            plt.savefig('dissociate_probability_asymmetric.png', dpi=500)
        plt.show()
    return n_list, [mean_above, mean_equal, mean_below], [std_above, std_equal, std_below]


