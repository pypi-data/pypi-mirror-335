import numpy as np
import copy

def hist_to_csv(FullHist: list, SpeciesList: list, OpName: str, Single: bool = False):
    """Creates a .csv (spreadsheet) file from a histogram.dat file (multi-species). If given multiple histograms, it will calculate the average between them.

    Args:
        FullHist (list): holds all of the histogram data
        SpeciesList (list): list of each included species type
        OpName (str): name of the outputted .csv file
        Single (bool): whether or not it is a single histogram

    Returns:
        histogram.csv file: Each row is a different time stamp (all times listed in column A). Each column is a different size of complex molecule (all sizes listed in row 1). Each box 
        is the number of that complex molecule at that time stamp.

    wow this is inefficient, but.... i dont care :D
    """
    
    column_list = [] #holds the name of each column (Time + each complex name)
    time_list = [] #holds each time. Index corresponds to a sublist in name_count_dict_List
    name_count_dict_list = [] #holds each name/count. Index corresponds with size_list
    FakeHist = copy.deepcopy(FullHist)

    #turn single histogram file format into multi histogram
    if Single:
        for file_index,file in enumerate(FakeHist):
            for time_index,time in enumerate(file):
                temp_list = []
                for count_index,count in enumerate(time[1]):
                    sub_temp_list = []
                    sub_temp_list.append(time[2][count_index])
                    sub_temp_list.append(count)
                    temp_list.append(sub_temp_list)
                FakeHist[file_index][time_index] = [FakeHist[file_index][time_index][0]] + temp_list


    #determine longest file
    length = 0
    for file_index,file in enumerate(FakeHist):
        if len(file) > length:
            length = len(file)
            length_index = file_index 
    

    #create list with dictionaries for each timestep
    for na in range(0,length+1):
        name_count_dict_list.append({})

    #goes through every timestep (usese the longest file for this)
    for time_index,time in enumerate(FakeHist[file_index]):

        #create list of every timestep
        time_list.append(time[0])

        #go through every file
        counter = 0
        for file_index,file in enumerate(FakeHist):

            #go through every complex in this file if this timestep exists
            if len(file) > time_index:
                counter = counter + 1
                for complexes in file[time_index][1:]:

                    #get name
                    name = ""
                    for index_sp,species in enumerate(complexes[:-1]):
                        name = f"{name}{SpeciesList[index_sp]}: {species}.  "
                        if name not in name_count_dict_list[time_index].keys():
                            name_count_dict_list[time_index][name] = []
                    
                    #get count
                    name_count_dict_list[time_index][name].append(complexes[-1])

                    #creates a list of every 'name'
                    if name not in column_list:
                        column_list.append(name)

        #determine the average
        for key,value in name_count_dict_list[time_index].items():
            #ensure the list has all of the included histograms
            if len(value) < counter:
                for na in range(len(value), counter):
                    value.append(0)

            #takes mean of list
            name_count_dict_list[time_index][key] = np.mean(value)


    #write the file!
    with open(f'{OpName}.csv', 'w') as write_file:
        
        #create column names
        head = 'Time(s):'
        for column in column_list:
            head += ','
            head += column
        head += '\n'
        write_file.write(head)

        #write the bulk of the file
        for index,timestep in enumerate(time_list):
            
            #initilize writing
            write = ''

            #write time to string
            write += f"{str(timestep)}"

            #write data to string
            for column in column_list:
                write += ','
                if column in name_count_dict_list[index].keys():
                    write += str(name_count_dict_list[index][column])
                else:
                    write += '0'
            
            #commit to file
            write += '\n'
            write_file.write(write)



