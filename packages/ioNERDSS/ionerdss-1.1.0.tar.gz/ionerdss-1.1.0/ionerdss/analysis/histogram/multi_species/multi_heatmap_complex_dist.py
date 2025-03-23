import numpy as np
import matplotlib.pyplot as plt
from .read_multi_hist import read_multi_hist
from ...file_managment.save_vars_to_file import save_vars_to_file

def multi_heatmap_complex_dist(FileName: str, FileNum: int, InitialTime: float, FinalTime: float, xAxis: str, yAxis: str,
                  SpeciesList: list = [], xBarSize: int = 1, yBarSize: int = 1,
                  ShowFig: bool = True, ShowMean: bool = False, ShowStd: bool = False, SaveFig: bool = False, SaveVars: bool = False):
    """ Creates a 3D heatmap from a histogram.dat (multi-species) that shows distrubution of sizes of selected species.

    Args:
        FileName (str): Path to the histogram.dat file
        FileNum (int): Number of the total input files (file names should be [fileName]_1,[fileName]_2,...)
        InitialTime (float): The starting time. Must not be smaller / larger then times in file.
        FinalTime (float): The ending time. Must not be smaller / larger then times in file.
        xAxis (str): Species shown on X-axis.
        yAxis (str): Species shown on Y-axis.
        SpeciesList (list, optional): The names of the species you want to examine. Should be in the .dat file.
        xBarSize (int, optional): The size of each data bar in the X-dimension. Defaults to 1.
        yBarSize (int, optional): The size of each data bar in the Y-dimension. Defaults to 1.
        ShowMean (bool, optional): If means will be shown in each box. Defaults to False.
        ShowStd (bool, optional): If std values will be shown in each box. Defaults to False.
        ShowFig (bool, optional): If the plot is shown. Defaults to True.
        SaveFig (bool, optional): If the plot is saved. Defaults to False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    Returns:
        3D Histogram. X-axis / Y-axis: the distribution of sizes of each specified species. Color: relative occurance of each complex.
    """
    file_name_head = FileName.split('.')[0]
    file_name_tail = FileName.split('.')[1]
    count_list_sum = []

    #create species list 
    SpeciesList = []
    SpeciesList.append(xAxis)
    SpeciesList.append(yAxis)

    #true max X and Y (across all files)
    true_max_x = 0
    true_max_y = 0

    #runs through every file
    for histogram_file_number in range(1, FileNum+1):
        
        #determining file name (if there are multiple or none)
        if FileNum == 1:
            temp_file_name = FileName
        else:
            temp_file_name = file_name_head + '_' + str(histogram_file_number) + '.' + file_name_tail

        max_x_size = 0 #stores the max number of the x protein type in 1 complex (1 file vv)
        max_y_size = 0 #stores the max number of the y protein type in 1 complex
        count_list = [[0]]
        data_count = 0

        #get lists of data from file
        hist_list = read_multi_hist(temp_file_name, SpeciesList=SpeciesList)

        #run through every timestep in the file, to find the max # of Xs and Ys in a single complex
        for time_step in hist_list:
            if time_step != []:
                time = time_step[0]
                if InitialTime <= time <= FinalTime:
                    data_count += 1

                    #run through each protein complex in timestep
                    for protein_complex in time_step[1:]:

                        #find number of each protein type in this complex. Then how many complexes of this type there are
                        x_size = protein_complex[0]
                        x_size = int(x_size / xBarSize)
                        y_size = protein_complex[1]
                        y_size = int(y_size / yBarSize)
                        count = protein_complex[-1]

                        #Expands matrix if it is not big enough
                        if max_y_size < y_size: 
                            for i in range(max_y_size,y_size):
                                count_list.append([])
                                for i in range(max_x_size+1):
                                    count_list[-1].append(0)
                            max_y_size = y_size
                        if max_x_size < x_size: 
                            for column_index in range(len(count_list)):
                                for i in range(max_x_size,x_size):
                                    count_list[column_index].append(0)
                            max_x_size = x_size

                        #goes through each protein, than adds 1 to the main array based on # of Xs and Ys in it
                        count_list[y_size][x_size] += count

        #find max X and Y b/w all files
        if max_y_size > true_max_y:
            true_max_y = max_y_size
        if max_x_size > true_max_x:
            true_max_x = max_x_size
        

        #turns array (# of proteins with specific XY counts) into mean (b/w all timestamps) than adds it to main, multi-file list
        count_list = np.divide(count_list,data_count).tolist()
        count_list_sum.append(count_list)
    

    #makes it so the arrays all go up to max_x and max_y
    true_max_x = true_max_x + 1
    true_max_y = true_max_y + 1
    
    for file_index,array in enumerate(count_list_sum):
        y_size = len(array)
        
        if y_size < true_max_y: 
            for na1 in range(y_size,true_max_y):
                count_list_sum[file_index].append([])
                for na2 in range(true_max_x+1):
                    count_list_sum[file_index][-1].append(0)
        
        for column_index in range(len(array)):
            x_size = len(array[column_index])
            if x_size < true_max_x: 
                for i in range(x_size,true_max_x):
                    count_list_sum[file_index][column_index].append(0)
    
    #find mean and std
    count_list_mean = np.zeros([true_max_y, true_max_x])
    count_list_std = np.zeros([true_max_y, true_max_x])
    for y in range(len(count_list_sum[0])):
        for x in range(len(count_list_sum[0][0])):
            temp_list = []
            for file in count_list_sum:
                temp_list.append(file[y][x])
            count_list_mean[y][x] += np.mean(temp_list)
            count_list_std[y][x] += np.std(temp_list)
    x_list = np.arange(0, true_max_x) * xBarSize
    y_list = np.arange(0, true_max_y) * yBarSize
    
    #output variables
    if SaveVars:
        save_vars_to_file({"x_mono_count":x_list, "y_mono_count":y_list, "cmplx_count":count_list_mean, "std":count_list_std})


    #create figure
    if ShowFig:
        fig, ax = plt.subplots()
        im = ax.imshow(count_list_mean)
        ax.set_xticks(np.arange(len(x_list)))
        ax.set_yticks(np.arange(len(y_list)))
        ax.set_xticklabels(x_list)
        ax.set_yticklabels(y_list)
        if ShowMean and ShowStd:
            print('Cannot show both mean and std!')
            return 0
        if ShowMean:
            fig_name = 'Complex_Distribution_of_' + xAxis + '_and_' + yAxis + '_with_mean'
            for i in range(len(y_list)):
                for j in range(len(x_list)):
                    text = ax.text(j, i, round(
                        count_list_mean[i, j], 1), ha='center', va='center', color='w')
        elif ShowStd and FileNum != 1:
            fig_name = 'Complex_Distribution_of_' + xAxis + '_and_' + yAxis + '_with_std'
            for i in range(len(y_list)):
                for j in range(len(x_list)):
                    text = ax.text(j, i, round(
                        count_list_std[i, j], 1), ha='center', va='center', color='w')
        else:
            fig_name = 'Complex_Distribution_of_' + xAxis + '_and_' + yAxis
        ax.set_title('Complex Distribution of ' + xAxis + ' and ' + yAxis)
        fig.tight_layout()
        plt.colorbar(im)
        plt.xlabel('Count of ' + xAxis)
        plt.ylabel('Count of ' + yAxis)
        if SaveFig:
            plt.savefig(fig_name, dpi=500,  bbox_inches='tight')
        plt.show()
    return x_list, y_list, count_list_mean, count_list_std

