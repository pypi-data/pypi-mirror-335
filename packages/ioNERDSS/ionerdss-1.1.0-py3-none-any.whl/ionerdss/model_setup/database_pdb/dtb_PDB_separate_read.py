import math
import sys
from .gen.real_PDB_chain_int_simple import real_PDB_chain_int_simple


def dtb_PDB_separate_read(FileName: str,ChainsIncluded: list = [None], MaxBoundLength: float = 0.3, SymmetryApplied: bool = False):
    """
    This function will extract the coordinate information stored inside a real PDB file and calculate 
    the COM of each unique chain, as well as recognize the binding information between each pair of chains 
    (all atoms of different unique chains that are closer that 3.0 angstroms are considered as binded), 
    including whether two chains are binded and the coordinates of each binding interface. All the information 
    will be printed on the screen and the returns will contain all the information for further analysis. 

    Args:
        FileName (str): The full path of the desired PDB file or name of the file if in same directory. 
        ChainIncluded (lst): A list of which chains you want to be included
        max_bound_length(float): atoms that are less than this length apart are seen as bound

    Returns:
        reaction_chain: list of coordinates to each chains COM. Indicies connect with unique chain.
        int_site: holds interaction site data. [i]: each reaction. [0][i]: each chain involved. [0][0][i]: position of that chains int site
        int_site_distance: distance between each interaction. Indice connects with int_site
        unique_chain: Each chain included
        COM: COM of each chain. Indicies connect with unique chain.

    """

    ##  PART 1: CREATING THE MAIN LISTS WITH ALL THE DATA
    
    # these lists have the same length as as total atom numbers in the protein.
    total_atom_count = [] # holds the index of every atom
    total_chain = [] # specific chain the atom belongs to (such as A or B or C, etc).
    total_resi_count = []  # residue number
    total_position = []  # the coordinate of each atom
    total_atom_type = []  # to show whether the atom is a alpha carbon, N, etc.
    total_resi_type = []  # to show the type of residue
    total_resi_position_every_atom = []  # indicate the position of alpha carbon of the residue the atom is in.
    
    # The length of these two lists are the same as total residue numbers in the chain and the length of rest of the lists
    total_resi_position = []  # list of position of all alpha carbon atom position
    total_alphaC_resi_count = []  # indicate which residule the alphaC belongs to
    
    #read in user pdb file, and output data about each atom into different lists.
    with open(FileName, "r") as filename:
        
        #go through each line in the file
        for line in filename:
            #based on the data, import data from that line into lists
            id = line[:4]
            if id != "ATOM":
                continue
            if(not SymmetryApplied):
                chain_name = line[21].strip()
            else:
                chain_name = line[72:76].strip()
            if id == 'ENDMDL':
                break
            elif id == 'ATOM' and (chain_name in ChainsIncluded or ChainsIncluded == [None]):  # find all 'atom' lines. But only add atom if it is in 'chainincluded'
                #check amino acid name, then edit it accordingly
                atom_serial_num = line[6:11].strip()
                atom_name = line[12:16].strip()
                amino_name = line[17:20].strip()
                if(not SymmetryApplied):
                    chain_name = line[21].strip()
                else:
                    chain_name = line[72:76].strip()
                residue_num = line[22:26].strip()
                x_coord = line[30:38].strip()
                y_coord = line[38:46].strip()
                z_coord = line[46:54].strip()

                #add data about the atom's data to the different lists
                total_atom_count.append(atom_serial_num)
                total_chain.append(chain_name)
                total_resi_count.append(residue_num)
                total_atom_type.append(atom_name)
                total_resi_type.append(amino_name)
                
                #change all strings into floats for position values, also converting to nm from angstroms
                position_coords = [float(x_coord)/10, float(y_coord)/10, float(z_coord)/10]
                total_position.append(position_coords)
                
                #create lists of all residuals (residual pos = location of Alpha C)
                if atom_name == "CA":
                    total_resi_position.append(position_coords)
                    total_alphaC_resi_count.append(residue_num)
    print('Finish reading pdb file')
    #go through as each residual, then run through all of the atoms (kinda) and if the atoms are 
    #in the residual set that atoms position to the residual (Creates total_resi_position_every_atom)
    count = 0
    for residualIndex,residual in enumerate(total_alphaC_resi_count):
        
        #once the end of the atom list is reached, break
        if count >= len(total_atom_type):
            break
        
        #go through each atom, and if the current residual = that atom, set that atoms position to this residual
        for j in range(count, len(total_atom_type)):
            if total_resi_count[j] == residual:
                total_resi_position_every_atom.append(total_resi_position[residualIndex])
                count = count + 1
            else: #since all atoms in 1 residual are next to each other, once one in a different one is reached, we know all have been read.
                break

    # determine how many unique chains exist
    unique_chain = []
    for atom_chain in total_chain:
        if atom_chain not in unique_chain :
            unique_chain.append(atom_chain)  
    
    print(str(len(unique_chain)) + ' chain(s) in total: ' + str(unique_chain))

    # exit if there's only one chain.
    if len(unique_chain) == 1:
        sys.exit()
    
    ##  END OF PART 1



    ## PART 2: CREATE NEW LISTS WHERE EACH CHAIN = 1 SUBLIST

    # create lists of lists where each sublist contains the data for different chains.
    split_atom_count = [] #index of each atom (sublisted)
    split_chain = [] #chain of each atom (sublisted?)
    split_resi_count = [] #residual # of each atom (sublisted)
    split_position = [] #position of each atom (sublisted)
    split_atom_type = [] #type (ex: alpha C, N) of each atom (sublisted)
    split_resi_type = [] #the typing of the residual of each atom (sublisted)
    chain_end_atom = [] #???
    split_resi_position_every_atom = [] #position of the alpha carbon of this atom's residual of each atom (sublisted)

    # inner lists are sublists of each list, each of the sublist represents data about a list
    inner_atom_count = []
    inner_chain = []
    inner_resi_count = []
    inner_position = []
    inner_atom_type = []
    inner_resi_type = []
    inner_resi_position_every_atom = []

    # determine number of atoms in each chain
    chain_counter = 0

    #runs through each atom
    for i in range(len(total_atom_count)):

        #if a new chain has been reached append the sublists to the main lists, and reset the temp lists
        if total_chain[i] != unique_chain[chain_counter]:
            split_atom_count.append(inner_atom_count)
            split_chain.append(inner_chain)
            split_resi_count.append(inner_resi_count)
            split_position.append(inner_position)
            split_atom_type.append(inner_atom_type)
            split_resi_type.append(inner_resi_type)
            split_resi_position_every_atom.append(
                inner_resi_position_every_atom)
            inner_atom_count = []
            inner_chain = []
            inner_resi_count = []
            inner_position = []
            inner_atom_type = []
            inner_resi_type = []
            inner_resi_position_every_atom = []
            chain_end_atom.append(len(split_atom_count[chain_counter]))
            chain_counter = chain_counter + 1
            
        if total_chain[i] == unique_chain[chain_counter]:
            inner_atom_count.append(total_atom_count[i])
            inner_chain.append(total_chain[i])
            inner_resi_count.append(total_resi_count[i])
            inner_position.append(total_position[i])
            inner_atom_type.append(total_atom_type[i])
            inner_resi_type.append(total_resi_type[i])
            inner_resi_position_every_atom.append(
                total_resi_position_every_atom[i])
    
        #if all atoms have been iterated through append the sublists to the main lists
        if i == (len(total_atom_count) - 1):
            split_atom_count.append(inner_atom_count)
            split_chain.append(inner_chain)
            split_resi_count.append(inner_resi_count)
            split_position.append(inner_position)
            split_atom_type.append(inner_atom_type)
            split_resi_type.append(inner_resi_type)
            split_resi_position_every_atom.append(
                inner_resi_position_every_atom)
            chain_end_atom.append(len(split_atom_count[chain_counter]))

    print('Each of them has ' + str(chain_end_atom) + ' atoms.')

    ## END PART 2



    ## PART 3:
    ## determine the interaction between each two chains by using function chain_int()
    ## the output is a tuple with 7 list of list including: reaction_chain, reaction_atom, reaction_atom_position,
    ## reaction_atom_distance, reaction_resi_count, reaction_resi_type and  reaction_atom_type

    interaction = real_PDB_chain_int_simple(unique_chain, split_position, split_resi_count, split_atom_count,
                                     split_resi_type, split_atom_type, split_resi_position_every_atom, MaxBoundLength)
    reaction_chain = interaction[0] #[i]: holds each chain interaction. [0][i]: name of each chain in this interaction
    reaction_resi_position = interaction[1] #[i]: holds each different chain interaction. [0][i]: each atomic interaction. [0][0][1-2]: position of both atoms in the interaction

    ##END OF PART 3




    #PART 4: calculating center of mass (COM), and interaction site

    #Calculate COM
    COM = [] # list of coordinates to each chains COM. Indicies connect with unique chain.
    
    #goes through each chain, and calculates the average location of every atom.
    for chain in split_position:
        sumx = 0
        sumy = 0
        sumz = 0
        chain_length =  len(chain)
        for atom_position in chain:
            sumx = sumx + atom_position[0]
            sumy = sumy + atom_position[1]
            sumz = sumz + atom_position[2]
        inner_COM = [sumx / chain_length, sumy /
                     chain_length, sumz / chain_length]
        COM.append(inner_COM)

    for i,chain_com in enumerate(COM):
        print("Center of mass of  " + unique_chain[i] + " is: " +
              "[%.3f, %.3f, %.3f]" % (chain_com[0], chain_com[1], chain_com[2]))

    #Calculate int_site
    int_site = [] #holds interaction site data. [i]: each reaction. [0][i]: each chain involved. [0][0][i]: position of that chains int site
    two_chain_int_site = []

    #goes through reaction, and calculates the average position of each residual.
    for i in range(len(reaction_resi_position)):
        for j in range(0, 2):
            sumx = 0
            sumy = 0
            sumz = 0
            count = 0
            added_position = []
            for k in range(len(reaction_resi_position[i])):
                if reaction_resi_position[i][k][j] not in added_position:
                    sumx = sumx + reaction_resi_position[i][k][j][0]
                    sumy = sumy + reaction_resi_position[i][k][j][1]
                    sumz = sumz + reaction_resi_position[i][k][j][2]
                    added_position.append(reaction_resi_position[i][k][j])
                    count = count + 1
            inner_int_site = [sumx / count, sumy / count, sumz / count]
            two_chain_int_site.append(inner_int_site)
        int_site.append(two_chain_int_site)
        two_chain_int_site = []

    ##END OF PART 4
    
    
    
    ##PART 5: calculate distance between interaction site.
    
    int_site_distance = []
    for reaction in int_site:
        distance = math.sqrt((reaction[0][0] - reaction[1][0]) ** 2 + (reaction[0][1] - reaction[1][1]) ** 2
                             + (reaction[0][2] - reaction[1][2]) ** 2)
        int_site_distance.append(distance)

    for i,reaction in enumerate(int_site):
        print("Interaction site of " + reaction_chain[i][0] + " & " + reaction_chain[i][1] + " is: "
              + "[%.3f, %.3f, %.3f]" % (reaction[0][0],
                                        reaction[0][1], reaction[0][2]) + " and "
              + "[%.3f, %.3f, %.3f]" % (reaction[1][0],
                                        reaction[1][1], reaction[1][2])
              + " distance between interaction sites is: %.3f nm" % (int_site_distance[i]))

    
    # finally ouputs
    return reaction_chain, int_site, int_site_distance, unique_chain, COM


