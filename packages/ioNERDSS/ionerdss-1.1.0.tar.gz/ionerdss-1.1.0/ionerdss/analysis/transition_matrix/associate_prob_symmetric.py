import numpy as np
import matplotlib.pyplot as plt
import warnings
from .read_transition_matrix import read_transition_matrix
from ..file_managment.save_vars_to_file import save_vars_to_file

def associate_prob_symmetric(FileName: str, FileNum: int, InitialTime: float, FinalTime: float,
                             SpeciesName: str, DivideSize: int = 2, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
    """ Plots the probability of association between complexes of different sizes and other complexes of different sizes.

    Args:
        FileName (str): Path to the histogram data file (usually named as 'transition_matrix_time.dat') to be analyzed.
        FileNum (int): Number of the total input files. If multiple files are provided, their names should obey the naming rule listed below.
        InitialTime (float): The initial time that users desire to examine. The acceptable range should not be smaller than the starting time or exceed the ending time of simulation.
        FinalTime (float): The final time that users desire to examine. The acceptable range should not be smaller than the value of InitialTime or exceed the ending time of simulation.
        SpeciesName (str): The name of the species that users want to examine, which should also be identical to the name written in the input (.inp and .mol) files.
        DivideSize (int, optional): Value that distinguishes the size of the associate complex. Defaults to 2.
        ShowFig (bool, optional): Whether to show the plot. Defaults to True.
        SaveFig (bool, optional): Whether to save the plot as a '.png' file in the current directory. Defaults to False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    Returns:
        A tuple of four lists containing: 
        - the sizes 
        - probabilities of association for complexes of size less than DivideSize
        - probabilities of association for complexes of size equal to DivideSize
        - probabilities of association for complexes of size greater than DivideSize
    
    Notes:
        If multiple input files are given, the output plot will be the average value of all files, and an error bar will also be included.
        Naming rule for input files: If single file is provided, the input file should be named as its original name (‘transition_matrix_time.dat’); if multiple files are provided, the name of input file should also include serial number as ‘transition_matrix_time_X.dat’ where X = 1,2,3,4,5…

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
        
        #read transition matrix (t1_matrix = matrix of proteins at initial, tf...)
        ti_matrix, tf_matrix = read_transition_matrix(
            temp_file_name, SpeciesName, InitialTime, FinalTime)
        
        #get change in matrix
        matrix = tf_matrix - ti_matrix
        matrix_list.append(matrix)
    
    
    above = []
    equal = []
    below = []
    #for each file
    for matrix in matrix_list:
        
        #create lists of zeros, based on the number of columns
        above_temp = np.zeros(len(matrix_list[0][0]))
        equal_temp = np.zeros(len(matrix_list[0][0]))
        below_temp = np.zeros(len(matrix_list[0][0]))
        
        #goes through the matrix, and based on row/column of data it gets assigned to equal/above/below
        row = 0
        while row < len(matrix):
            column = 0
            while column < len(matrix[row]):
                if row > column:
                    if row - column == DivideSize:
                        equal_temp[column] += matrix[row][column]
                    elif row - column > DivideSize:
                        above_temp[column] += matrix[row][column]
                    else:
                        below_temp[column] += matrix[row][column]
                column += 1
            row += 1
        #add to main above/ect. vars
        above.append(above_temp)
        equal.append(equal_temp)
        below.append(below_temp)
    
    #for each column determine probability based on entire count in that column. 
    above_prob = []
    equal_prob = []
    below_prob = []
    for i in range(len(above)):
        above_prob_temp = []
        equal_prob_temp = []
        below_prob_temp =[]
        for j in range(len(above[0])):
            sum = above[i][j] + equal[i][j] + below[i][j]
            if sum != 0:
                above_prob_temp.append(above[i][j]/sum)
                equal_prob_temp.append(equal[i][j]/sum)
                below_prob_temp.append(below[i][j]/sum)
            else:
                above_prob_temp.append(np.nan)
                equal_prob_temp.append(np.nan)
                below_prob_temp.append(np.nan)
        above_prob.append(above_prob_temp)
        equal_prob.append(equal_prob_temp)
        below_prob.append(below_prob_temp)
    
    #TRANSPOSING TIME!!!!!!
    above_prob_rev = np.array(above_prob).transpose()
    equal_prob_rev = np.array(equal_prob).transpose()
    below_prob_rev = np.array(below_prob).transpose()
    
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

        
    n_list = list(range(1, 1 + len(matrix_list[0])))
        
    #output variables
    if SaveVars:
        save_vars_to_file({"cmplx_size":n_list,"mean_associate_probability":[mean_above, mean_equal, mean_below],"std":[std_above, std_equal, std_below]})

    #show figure!
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
        plt.legend(['Associate Size > ' + str(DivideSize), 'Associate Size = ' +
                    str(DivideSize), 'Associate Size < ' + str(DivideSize)])
        plt.xlabel('Number of ' + str(SpeciesName) + ' in Single Complex')
        plt.ylabel('Probability')
        plt.xticks(ticks=n_list)
        plt.title('Symmetric Association Probability')
        if SaveFig:
            plt.savefig('associate_probability_symmetric.png', dpi=500)
        plt.show()
    return n_list, [mean_above, mean_equal, mean_below], [std_above, std_equal, std_below]


