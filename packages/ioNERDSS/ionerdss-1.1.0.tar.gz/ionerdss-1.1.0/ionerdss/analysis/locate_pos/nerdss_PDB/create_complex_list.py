def create_complex_list(bond_list):
    """Finds protein complexes based on a list of protein-protein bond pairs.

    Args:
        bond_lst (list): A list of protein-protein bond pairs in the format ([protein_num_1, protein_num_2]_.

    Returns:
        list: A list of protein complex lists, where each complex list contains protein numbers that are part of
        the same complex.
    """
    
    complex_lst = []
    
    #if the bond list is not empty, keep going through it
    while bond_list != []:
        temp_complex_lst = bond_list[0]

        #go through each the temp protein complex list. For each protein, check through the enitre bond_list to see if it is bonded with anything. If yes, add it and remove it from main list
        for protein in temp_complex_lst:
            for bond in bond_list:
                if protein == bond[0]:
                    temp_complex_lst.append(bond[1])
                    bond_list.remove(bond)
                elif protein == bond[1]:
                    temp_complex_lst.append(bond[0])
                    bond_list.remove(bond)

        
        temp_complex_lst.sort()
        complex_lst.append(list(set(temp_complex_lst)))


    
    
    return complex_lst