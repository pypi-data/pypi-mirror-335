from .determine_bind import determine_bind


def create_bond_list(site_array,site_dict,binding_array,binding_dict,BufferRatio):
    """Generates a list of every bond.

    Args:
        site_array (list of lists): holds information about each bonding site on every protein
        site_dict (dictionary): turns column name (from df) into list index for site_array
        binding_array (list of lists): holds information about each iteraction
        binding_dict (dictionary): turns column name (from df) into list index for binding_array
        BufferRatio (float): The buffer ratio used to determine whether two reaction interfaces can be considered as bonded.

    Returns:
        List: every protein-protein bond pairs in the format ([protein_num_1, protein_num_2]_    
    """
    count = 1

    bond_lst = []

    #for every reaction type, check all possible interactions b/w interaction sites. Then add to main list
    for bind_type in binding_array:
        
        #create a list of each possible interaction site for this interaction
        protein_1_sites = [] #list of first interaction site
        protein_2_sites = [] #list of second interaction site

        for site in site_array: #for every site, check if it can be included in 1 of the lists
            if site[site_dict['Protein_Name']] == bind_type[binding_dict['Protein_Name_1']]:
                if site[site_dict['Site_Name']] == bind_type[binding_dict['Site_Name_1']]:
                    protein_1_sites.append(site)
            if site[site_dict['Protein_Name']] == bind_type[binding_dict['Protein_Name_2']]:
                if site[site_dict['Site_Name']] == bind_type[binding_dict['Site_Name_2']]:
                    protein_2_sites.append(site)


        print('Calculating distance for reaction #', count, '...')
        count += 1
        
        #create list of each actual interaction
        for site_1 in protein_1_sites:
            for site_2 in protein_2_sites:

                #determine if these two sites are bonded
                storeBoolean = determine_bind(site_1,site_2,BufferRatio,site_dict,bind_type[binding_dict["sigma"]])
                if storeBoolean:

                    temp_bond_lst = [site_1[site_dict["Protein_Num"]],site_2[site_dict["Protein_Num"]]]
                    if temp_bond_lst not in bond_lst:
                        temp_bond_lst.sort()
                        bond_lst.append(temp_bond_lst)

    

    return bond_lst


