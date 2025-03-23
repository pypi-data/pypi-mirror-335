def read_inp(inp_name):
    """Generates an array containing binding information from an input file.

    Args:
        inp_name (str): the name of the input file to read binding information from

    Returns:
        numpy array: array that stores all of the binding info
            - [i] = each row, each different possible bind
            - [i][i] = each column (in a specific row). Has specific info about bind. find the index of the correct colum with the dictionary
                - Ex: binding_dict['Protein_Name_1'] >> 0
        dictionary: dictionary that stores the index of each column    
    """
    status = False

    binding_array = []
    binding_dict = {'Protein_Name_1':0,'Site_Name_1':1,'Protein_Name_2':2,'Site_Name_2':3,'sigma':4}


    with open(inp_name, 'r') as file:
        for line in file.readlines():
            
            #checks when to start/stop reading
            if line == 'end reactions\n':
                status = False
                break
            if line == 'start reactions\n':
                status = True
            
            if status:
                
                #gets reaction info
                if '<->' in line:
                    binding_array.append([])
                    index = len(binding_array) - 1
                    
                    #extracts info from parms.inp (its ugly but im scared to change it)
                    line1 = line.split('+')
                    element1 = line1[0].strip(' ')
                    line2 = line1[1].split('<->')
                    element2 = line2[0].strip(' ')
                    element1_ = element1.strip(')').split('(')
                    element2_ = element2.strip(')').split('(')
                    
                    binding_array[index].append(element1_[0][0:3])
                    binding_array[index].append(element1_[1][0:3])
                    binding_array[index].append(element2_[0][0:3])
                    binding_array[index].append(element2_[1][0:3])
                
                #gets sigma
                if 'sigma' in line:
                    sigma = float(line.split(' = ')[-1].strip('\n'))
                    binding_array[index].append(sigma)

    return binding_array,binding_dict


