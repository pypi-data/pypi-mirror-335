import numpy as np
import matplotlib.pyplot as plt
from .read_multi_hist import read_multi_hist
from ...file_managment.save_vars_to_file import save_vars_to_file

def multi_stack_hist_complex_count(FullHist: list, FileNum: int, InitialTime: float, FinalTime: float,
                       SpeciesList: list, xAxis: str, DivideSpecies: str, DivideSize: int,
                       BarSize: int = 1, ExcludeSize: int = 0, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
    """Creates a stacked histogram from histogram.dat (multi-species) that shows the average number of each type of 
    complex species (based on protein composition) over the whole sim. 

    Args:
        FullHist (list): Holds all of the information from the .dat file
        FileNum (int): Number of the total input files (file names should be [fileName]_1,[fileName]_2,...)
        InitialTime (float): The starting time. Must not be smaller / larger then times in file.
        FinalTime (float): The ending time. Must not be smaller / larger then times in file.
        xAxis (str): Species shown on X-axis.
        DivideSpecies (str): The name of the species that will be seperated by size.
        DivideSize (int): The value that separates the size of dissociate complexes. (only changes color of graph)
        SpeciesList (list): The names of the species you want to examine. Should be in the .dat file.
        BarSize (int, optional): The size of each data bar in the X-dimension. Defaults to 1.
        ExcludeSize (int, optional): Monomers in the complex that are smaller or equal to this number will not be included. 
        ShowFig (bool, optional): If the plot is shown. Defaults to True.
        SaveFig (bool, optional): If the plot is saved. Defaults to False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    Returns:
        Histogram. X-axis = size of selected species, Y-axis = average number of each corresponds.
    """

    above_list = []
    equal_list = []
    below_list = []
    max_size = 0 # largest complex size

    #get index of the xAxis and divide species
    x_species_index = SpeciesList.index(xAxis)
    divide_species_index = SpeciesList.index(DivideSpecies)

    #for each file
    for hist_list in FullHist:

        total_above_dict = {}
        total_equal_dict = {}
        total_below_dict = {}

        data_count = 0

        #for every time step
        for time_step in hist_list:
            if time_step != []:
                time = time_step[0]
                if InitialTime <= time <= FinalTime:
                    data_count += 1

                    #for every protein complex
                    for protein_complex in time_step[1:]:
                        
                        #if number of selected proteisn in the complex
                        if xAxis == 'tot' and DivideSpecies in SpeciesList:
                            total_size = sum(protein_complex[0:-1])
                        elif xAxis in SpeciesList and DivideSpecies in SpeciesList:
                            total_size = protein_complex[x_species_index]
                        
                        if total_size >= ExcludeSize:
                            divide_spe_size = protein_complex[divide_species_index]
                                
                            #check if there is already a key for a protein of this size. If there isn't add it
                            if not total_size in total_above_dict:
                                total_above_dict[total_size] = 0
                                total_equal_dict[total_size] = 0
                                total_below_dict[total_size] = 0

                            #if complex size not included, initlize this size, and add the total number of this kind of complex to lists of above/below
                            if divide_spe_size > DivideSize:
                                total_above_dict[total_size] += (protein_complex[-1])
                            elif divide_spe_size == DivideSize:
                                total_equal_dict[total_size] += (protein_complex[-1])
                            else:
                                total_below_dict[total_size] += (protein_complex[-1])
                            
        #find max size and devide each protein by # of timesteps to get average
        for key in total_above_dict:
            total_above_dict[key] = total_above_dict[key] / data_count
            if max_size < int(key):
                max_size = int(key)
            n_list = list(range(1,int(max_size+1)))
        
        for key in total_equal_dict:
            total_equal_dict[key] = total_equal_dict[key] / data_count
            if max_size < int(key):
                max_size = int(key)
            n_list = list(range(1,int(max_size+1)))
        
        for key in total_below_dict:
            total_below_dict[key] = total_below_dict[key] / data_count
            if max_size < int(key):
                max_size = int(key)
            n_list = list(range(1,int(max_size+1)))

        #add dictionaries to main lists
        above_list.append(total_above_dict)
        equal_list.append(total_equal_dict)
        below_list.append(total_below_dict)


    #add dictionary values to filled lists and transposes them for prep for mean
    above_list_filled = np.zeros([max_size,FileNum])
    for indexX,dict in enumerate(above_list):
        for key in dict:
            above_list_filled[int(key)-1][indexX] += dict[key]

    equal_list_filled = np.zeros([max_size,FileNum])
    for indexX,dict in enumerate(equal_list):
        for key in dict:
            equal_list_filled[int(key)-1][indexX] += dict[key]
    
    below_list_filled = np.zeros([max_size,FileNum])
    for indexX,dict in enumerate(below_list):
        for key in dict:
            below_list_filled[int(key)-1][indexX] += dict[key]
    
    #is it mean time?
    mean_above = []
    std_above = []
    mean_equal = []
    std_equal = []
    mean_below = []
    std_below = []
    for protein_size in above_list_filled:
        mean_above.append(np.nanmean(protein_size))
        std_above.append(np.nanstd(protein_size))
    for protein_size in equal_list_filled:
        mean_equal.append(np.nanmean(protein_size))
        std_equal.append(np.nanstd(protein_size))
    for protein_size in below_list_filled:
        mean_below.append(np.nanmean(protein_size))
        std_below.append(np.nanstd(protein_size))
    

    
    #will combine means together if bar size is too small
    mean_above_ = []
    mean_equal_ = []
    mean_below_ = []
    std_above_ = []
    std_equal_ = []
    std_below_ = []
    n_list_ = []
    temp_mean_above = 0
    temp_mean_equal = 0
    temp_mean_below = 0
    temp_std_above = 0
    temp_std_equal = 0
    temp_std_below = 0
    bar_size_count = 0
    for i in range(len(mean_above)):
        temp_mean_above += mean_above[i]
        temp_mean_equal += mean_equal[i]
        temp_mean_below += mean_below[i]
        temp_std_above += std_above[i]
        temp_std_equal += std_equal[i]
        temp_std_below += std_below[i]
        bar_size_count += 1
        if bar_size_count >= BarSize and i != len(mean_above) - 1:
            mean_above_.append(temp_mean_above)
            mean_equal_.append(temp_mean_equal)
            mean_below_.append(temp_mean_below)
            std_above_.append(temp_std_above)
            std_equal_.append(temp_std_equal)
            std_below_.append(temp_std_below)
            n_list_.append(n_list[i])
            temp_mean_above = 0
            temp_mean_equal = 0
            temp_mean_below = 0
            temp_std_above = 0
            temp_std_equal = 0
            temp_std_below = 0
            bar_size_count = 0
    
    mean_above_.append(temp_mean_above)
    mean_equal_.append(temp_mean_equal)
    mean_below_.append(temp_mean_below)
    std_above_.append(temp_std_above)
    std_equal_.append(temp_std_equal)
    std_below_.append(temp_std_below)
    n_list_.append(n_list[i])
    mean_above_ = np.array(mean_above_)
    mean_equal_ = np.array(mean_equal_)
    mean_below_ = np.array(mean_below_)
    std_above_ = np.array(std_above_)
    std_equal_ = np.array(std_equal_)
    std_below_ = np.array(std_below_)
    n_list_ = np.array(n_list_)
    
    #output variables
    if SaveVars:
        save_vars_to_file({"x_mono_count":n_list_, "cmplx_count":[mean_below_, mean_equal_, mean_above_], "std":[std_below_, std_equal_, std_above_]})
    #show figure!
    if ShowFig:
        if DivideSize != 0:
            below_label = DivideSpecies + '<' + str(DivideSize)
            equal_label = DivideSpecies + '=' + str(DivideSize)
            above_label = DivideSpecies + '>' + str(DivideSize)
        else:
            above_label = 'With ' + DivideSpecies
            equal_label = 'Without ' + DivideSpecies
        if FileNum != 1:
            if DivideSize != 0:
                plt.bar(n_list_, mean_below_, width=BarSize, color='C0',
                        yerr=std_below_, label=below_label, ecolor='C3', capsize=2)
            plt.bar(n_list_, mean_equal_, width=BarSize, color='C1', yerr=std_equal_,
                    bottom=mean_below_, label=equal_label, ecolor='C3', capsize=2)
            plt.bar(n_list_, mean_above_, width=BarSize, color='C2', yerr=std_above_,
                    bottom=mean_below_+mean_equal_, label=above_label, ecolor='C3', capsize=2)
        else:
            if DivideSize != 0:
                plt.bar(n_list_, mean_below_, width=BarSize,
                        color='C0', label=below_label, capsize=2)
            plt.bar(n_list_, mean_equal_, width=BarSize, color='C1',
                    bottom=mean_below_, label=equal_label, capsize=2)
            plt.bar(n_list_, mean_above_, width=BarSize, color='C2',
                    bottom=mean_below_+mean_equal_, label=above_label, capsize=2)
        if xAxis == 'tot':
            x_label_name = 'total monomers'
        else:
            x_label_name = xAxis
        plt.xlabel('Number of ' + x_label_name + ' in single complex')
        plt.ylabel('Count')
        plt.legend()
        plt.title('Histogram of Multi-component Assemblies')
        fig_name = 'stacked_histogram_of_' + xAxis + '_divided_by_' + DivideSpecies
        if SaveFig:
            plt.savefig(fig_name, dpi=500)
        plt.show()
    return n_list_, [mean_below_, mean_equal_, mean_above_], [std_below_, std_equal_, std_above_]


