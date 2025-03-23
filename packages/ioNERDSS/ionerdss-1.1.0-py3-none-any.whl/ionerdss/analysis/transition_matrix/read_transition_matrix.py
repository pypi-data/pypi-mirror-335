import numpy as np


def read_transition_matrix(FileName: str, SpeciesName: str, InitialTime: float, FinalTime: float):
    """
    Parses transition_matrix_time.dat, and returns the matrices at two given time points.

    Args:
        FileName (str): The name of the file to be read.
        SpeciesName (str): The name of the species to be analyzed.
        InitialTime (float): The initial time point of interest.
        FinalTime (float): The final time point of interest.

    Returns:
          A tuple that contains:
           - NumPy array of the transition matrix at the initial time point
           - NumPy array of the transition matrix at the final time point
    """
    ti_matrix = []
    tf_matrix = []
    speciesDistance = 0

    #read the file (slowest part I promise)
    with open(FileName, 'r') as file:
        lines = file.readlines()

    #determine distance between times/speciesname
    for index,line in enumerate(lines[1:]):

        #distance b/w time line and the correct species name line
        if speciesDistance == 0 and line[0:4] == SpeciesName:
            speciesDistance = index + 1

        #distance between 2 different time slines
        if line[0:5] == 'time:': 
            distance = index + 1
            break
    
    #if no species was found, raise error
    if speciesDistance == 0:
        raise Exception("No species name found")


    #go through each 'time' line
    for index,line in enumerate(lines[::distance]):
            
        #checks if it equal to the initial time
        if float(line.split(' ')[1]) == InitialTime:
            index_real = (distance*index) + 1
            index_start_read = index_real + speciesDistance

            #get data from this time's matrix, and put it into an array (reads until it hits lifetime)
            for data in lines[index_start_read:-1]:
                if data[0:8] != 'lifetime':
                    info = data.strip(' ').strip('\n').split(' ')
                    temp_list = []
                    for value in info:
                        temp_list.append(int(value))
                    ti_matrix.append(temp_list)
                else:
                    break


        #checks if it equal to the final time
        if float(line.split(' ')[1]) == FinalTime:
            index_real = (distance*index) + 1
            index_start_read = index_real + 2
            
            #get data from this time's matrix, and put it into an array (reads until it hits lifetime
            for data in lines[index_start_read:-1]:
                if data[0:8] != 'lifetime':
                    info = data.strip(' ').strip('\n').split(' ')
                    temp_list = []
                    for value in info:
                        temp_list.append(int(value))
                    tf_matrix.append(temp_list)
                else:
                    break
            
    #if no matrices found
    if ti_matrix == []:
        raise Exception('Time initial not found')
    if tf_matrix == []:
        raise Exception('Time final not found')        
    
    #output
    ti_matrix = np.array(ti_matrix)
    tf_matrix = np.array(tf_matrix)
    return ti_matrix, tf_matrix