from ..file_managment.save_vars_to_file import save_vars_to_file

def traj_track(FileName: str, SiteNum: int, MolIndex: list, SaveVars: bool = False):
    """Tracks the center of mass (COM) coordinate changing of one or more molecules.

    Args:
        FileName: A string specifying the path to the input .xyz file, usually named 'trajectory.xyz'.
        SiteNum: An integer specifying the total number of COM and interfaces of a single molecule.
        MolIndex: A list of integers specifying the index of molecules users desire to track.

    Returns:
        A 2D matrix with the size of the number of literation times the number of desired molecules.

    Example:
        traj_track('/Users/UserName/Documents/trajectory.xyz', 6, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
         [0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
         [0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
         [0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
         [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]
    """ """"""
    array = [] #an array that stores the trajectory
    
    #an array with a sublist for each tracked molecule
    for na in range(len(MolIndex)):
        array.append([])
    
    with open(FileName, 'r') as file:
        for line in file.readlines():
            
            #if there is a new iteration, reset index
            if line[0:11] == 'iteration: ':
                index = 0
            
            info = line.strip(' ').strip('\n').split()
            
            #if line is a trajectory line
            if len(info) == 4:
                
                #if the correct molecule is found and it's the first site (COM) of that molecule. Add data to array
                if (index//SiteNum)+1 in MolIndex and index % SiteNum == 0:
                    x = float(info[1])
                    y = float(info[2])
                    z = float(info[3])
                    coord = [x, y, z]
                    list_index = MolIndex.index((index//SiteNum)+1)
                    array[list_index].append(coord)
                index += 1
    
    
    if SaveVars:
        save_vars_to_file({"trajectory":array})

    return array