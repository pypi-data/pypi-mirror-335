def read_PDB(file_name, drop_COM):
    """Converts a PDB file to an array.

    Args:
        file_name (str): Name of the PDB file to be read.
        drop_COM (bool): Whether to drop lines with 'COM' as the 'Cite_Name' value.

    Returns:
        numpy array: array that stores all of the proteins info
            - [i] = each row, different protein site
            - [i][i] = each column (in a specific row) find the index of the correct colum with the dictionary
                - Ex: site_dict['Protein_Num'] >> 0
        dictionary: dictionary that stores the index of each column
        dictionary: stores the protein type for each protein number
        array: stores each line, and the important parts of it for use in writing    
    
    """

    site_array = []
    site_dict = {'Protein_Num':0,'Protein_Name':1,'Site_Name':2,'x_coord':3,'y_coord':4,'z_coord':5}
    num_name_dict = {}
    main_pdb_lst = []

    #opens the file, goes through each line, and stores it into the array. Also, creates list of each line for use later.
    with open(file_name, 'r') as file:
        
        for line in file.readlines():
            line_lst = line.split(' ')
            
            #if the line discribes a site, take info from it and put it into site_array
            if line_lst[0] == 'ATOM':
                info = []
                info = [element.strip('\n') for element in line_lst if element !=""] #removes white space from line
                    
                if (drop_COM and info[2] != 'COM') or not drop_COM: #if drop_COM is true, dont include COM. if it is false, include everything.

                    site_array.append([])
                    index = len(site_array) - 1

                    site_array[index].append(int(info[4]))
                    site_array[index].append(info[3])
                    site_array[index].append(info[2])
                    site_array[index].append(float(info[5]))
                    site_array[index].append(float(info[6]))
                    site_array[index].append(float(info[7]))
                    
                    num_name_dict[info[4]] = info[3]

            #Creates list of every line
                main_pdb_lst.append([int(info[4]),line])
            else:
                main_pdb_lst.append(['header',line])
                    

                        

    return site_array,site_dict,num_name_dict,main_pdb_lst


