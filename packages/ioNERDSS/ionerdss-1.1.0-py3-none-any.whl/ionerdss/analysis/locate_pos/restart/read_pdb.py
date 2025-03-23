
def read_pdb(file_name_pdb,complex_lst,NumDict):
    """Convert protein information from PDB file to a dictionary

    Args:
        file_name_pdb (str): the name of the PDB file to be read.
        complex_lst (list): a list of lists, where each sub-list represents a complex and contains the IDs of its components.
        NumDict (dictionary): A dictionary that holds the requested number of protein types in a complex

    Returns:
        sorted_complexes (array): holds each complex as a subdictionary. Then each dictionaries key = name of a protein, value = list of protein indexes in that complex

    Examples:
        >>> RESTART_pdb_to_df_alt('protein.pdb')
        {1: 'clat',2: 'clat',3:'dode',....}
    ...
    """
    sorted_complexes = [] #holds each complex as a subdictionary. Then each dictionaries key = name of protein, value = list of protein indexes
    protein_name_list = NumDict.keys()


    for na in range(len(complex_lst)):
        sorted_complexes.append({})
        for protein_name in protein_name_list:
            sorted_complexes[-1][protein_name] = set()


    with open(file_name_pdb, 'r') as file:
        for line in file.readlines():
            
            #if it is an protein site line
            line = line.split(' ')
            if line[0] == 'ATOM':
                
                info = [ele for ele in line if ele != ""] #create a nice clean info
                protein_index = int(info[4]) #index of the current protein
                protein_name = info[3] #name of the current protein
                
                #if this a protein being looked for then:
                if protein_name in protein_name_list:
                    
                    #search through every complex found by restart and:
                    for index,complex in enumerate(complex_lst):
                        
                        #if this protein in found in a complex, add the protein to the new dictionary under this protein's name
                        if protein_index in complex:
                            sorted_complexes[index][protein_name].add(protein_index)
    
    #If any proteins inputted where not found anywhere, raise an exception
    for protein_name in protein_name_list:
        check = True
        for complex in sorted_complexes:
            if len(complex[protein_name]) != 0:
                check = False
        if check:
            raise Exception(f"Protein {protein_name} was not found in any complex. Maybe you misspelled?")


    return sorted_complexes

