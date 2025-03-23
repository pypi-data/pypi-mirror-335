import numpy as np


def read_cluster_lifetime(FileName: str, SpeciesName: str, InitialTime: float, FinalTime: float):
    """Reads and extracts the lifetimes of clusters of a specific species from a transition_matrix_time.dat file.

    Args:
        FileName (str): The name of the file to read the cluster lifetimes from.
        SpeciesName (str): The name of the species to extract cluster lifetimes for.
        InitialTime (float): The initial time at which to extract cluster lifetimes.
        FinalTime (float): The final time at which to extract cluster lifetimes.

    Returns:
        A tuple containing three elements:
        - A list of numpy arrays representing the lifetimes of the species clusters
        at the initial time.
        - A list of numpy arrays representing the lifetimes of the species clusters
        at the final time.
        - A list of integers representing the sizes of the species clusters.
    """
    size_list = []
    ti_lifetime = []
    tf_lifetime = []
    
    ##This file initiall had everything in the with open() meaning it would go through each line, and check it. Now it will check only the start, than only will check lines. This gave it 
    ##A slight boost in speed for higher timestep data

    #read the file (slowest part I promise)
    with open(FileName, 'r') as file:
        lines = file.readlines()

    #determine distance between times
    for index,line in enumerate(lines[1:]):
        
        #distance b/w time line and the correct species name line
        if line[0:4] == SpeciesName:
            speciesDistance = index + 1

        #distance between 2 different time slimes
        if line[0:5] == 'time:': 
            distance = index + 1
            break     

        
    #for every time line
    for index,line in enumerate(lines[::distance]):
        
        #checks if it equal to the initial time
        if float(line.split(' ')[1]) == InitialTime:
            index_real = (distance*index) + 1
            index_start_read = index_real + speciesDistance   
            for data in lines[index_start_read:]:
                
                #if time is reached
                if data[0:5] == 'time:':
                    break

                #cluster size line
                if data[0:20] == 'size of the cluster:':
                    size_list.append(int(data.split(':')[1].strip('\n')))
                        
                #the lifetimes of that size??
                else:
                    str_list = data.strip('\n').strip(' ').split(' ')
                    temp = []
                    for i in str_list:
                        if i != '':
                            temp.append(float(i))
                    ti_lifetime.append(np.array(temp))

        
        #checks if it equal to the final time
        if float(line.split(' ')[1]) == FinalTime:
            index_real = (distance*index) + 1
            index_start_read = index_real + speciesDistance   

            for data in lines[index_start_read:]:
                
                #if time is reached
                if data[0:5] == 'time:':
                    break
                
                #the lifetimes of that size??
                if data[0:20] != 'size of the cluster:':
                    str_list = data.strip('\n').strip(' ').split(' ')
                    temp = np.array([])
                    for i in str_list:
                        if i != '':
                            temp = np.append(temp, float(i))
                    tf_lifetime.append(temp)
    
    return ti_lifetime, tf_lifetime, size_list


