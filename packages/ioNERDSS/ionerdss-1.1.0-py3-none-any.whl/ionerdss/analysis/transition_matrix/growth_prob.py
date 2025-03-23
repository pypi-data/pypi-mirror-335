import numpy as np
import matplotlib.pyplot as plt
import warnings
from .read_transition_matrix import read_transition_matrix
from ..file_managment.save_vars_to_file import save_vars_to_file

def growth_prob(FileName: str, FileNum: int, InitialTime: float, FinalTime: float,
                SpeciesName: str, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
    """
    This function generates a line plot indicating the probability of growth in size for different sizes of complexes.

    Args:
        FileName (str): Path to the ‘.dat’ file, which is usually named as ‘histogram_complexes_time.dat’, representing the histogram data to be analyzed.
        FileNum (int): Number of the total input file. If multiple files are provided, their names should obey the naming rule listed below.
        InitialTime (float): Initial time that users desire to examine. The acceptable range should not smaller than the starting time or exceed the ending time of simulation.
        FinalTime (float): Final time that users desire to examine. The acceptable range should not smaller than the value of InitialTime or exceed the ending time of simulation.
        SpeciesName (str): Name of species that users want to examine, which should also be identical with the name written in the input (.inp and .mol) files.
        ShowFig (bool, optional): If True, the plot will be shown; if False, the plot will not be shown. Defaults to True.
        SaveFig (bool, optional): If True, the plot will be saved as a ‘.png’ file in the current directory; if False, the figure will not be saved. Defaults to False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    Returns:
        Line plot. X-axis = size of complexes. Y-axis = growth probability.
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
    growth_list_list = []
    tot_list_list = []
    for k in range(len(matrix_list)):
        growth_list = []
        tot_list = []
        i = 0
        while i < len(matrix_list[k][0]):
            j = 0
            growth_sum = 0
            tot_sum = 0
            while j < len(matrix_list[k][i]):
                if i != j:
                    tot_sum += matrix_list[k][j][i]
                    if i < j:
                        growth_sum += matrix_list[k][j][i]
                j += 1
            growth_list.append(growth_sum)
            tot_list.append(tot_sum)
            i += 1
        growth_list_list.append(growth_list)
        tot_list_list.append(tot_list)
   
    #more magic
    growth_prob = []
    for i in range(len(growth_list_list)):
        growth_prob_temp = []
        for j in range(len(growth_list_list[i])):
            if tot_list_list[i][j] != 0:
                growth_prob_temp.append(
                    growth_list_list[i][j]/tot_list_list[i][j])
            else:
                growth_prob_temp.append(0.0)
        growth_prob.append(growth_prob_temp)
    
    #transpose
    growth_prob_rev = []
    for i in range(len(growth_prob[0])):
        temp = []
        for j in range(len(growth_prob)):
            temp.append(growth_prob[j][i])
        growth_prob_rev.append(temp)
   
   #determine mean / std
    mean = []
    std = []
    for i in growth_prob_rev:
        mean.append(np.nanmean(i))
        std.append(np.nanstd(i))
    
    #list of each complex size
    n_list = list(range(1, 1 + len(matrix_list[0])))
    
    #output variables
    if SaveVars:
        save_vars_to_file({"cmplx_size":n_list,"prob_of_growth":mean,"std":std})
    
    #show figure
    if ShowFig:
        errorbar_color = '#c9e3f6'
        plt.plot(n_list, mean, color='C0')
        if FileNum != 1:
            plt.errorbar(n_list, mean, yerr=std,
                         ecolor=errorbar_color, capsize=2)
        plt.axhline(y=1/2, c='black', lw=1.0)
        plt.xlabel('Number of ' + str(SpeciesName) + ' in Single Complex')
        plt.ylabel('$P_{growth}$')
        plt.xticks(ticks=n_list)
        plt.yticks((0, 0.25, 0.5, 0.75, 1))
        plt.title('Growth Probability')
        if SaveFig:
            plt.savefig('growth_probability.png', dpi=500)
        plt.show()
    return n_list, mean, std


