def xyz_to_csv(FileName: str, LitNum: int = -1, OpName: str = "output_file"):
    """Converts a .xyz file to a .csv file for a specific or entire time frame.

    Args:
        FileName (str): The path to the input .xyz file, usually named 'trajectory.xyz'.
        LitNum (int, optional = -1): The number of iterations to examine. If -1, the entire iteration will be extracted.
        OpName (str, optional = “output_file”): The name of the outputted file. 

    Returns:
        A .csv file.

    Description:
        This function enables users to convert the output .xyz file by NERDSS simulation into a .csv file of a specific or entire time frame. The generated csv file will contain 5 columns, including number of iteration, species name, x, y, and z coordinates.

    Sample:
        xyz_to_csv('/Users/UserName/Documents/trajectory.xyz', 100000000) # Extracts iteration 100000000
        xyz_to_csv('/Users/UserName/Documents/trajectory.xyz', -1) # Extracts the entire iteration
    """
    
    #determines which iterations will be included
    write_file_name = f"{OpName}.csv"

    if LitNum != -1:
        lit_switch = False
    else:
        lit_switch = True
    
    #open read and write file
    with open(FileName, 'r') as read_file, open(write_file_name, 'w') as write_file:
        
        #creates header
        head = 'literation,name,x,y,z\n'
        write_file.write(head)
        
        #reads each line
        for line in read_file.readlines():
            
            #determines whether this iteration will be read or not
            if LitNum != -1:
                if line[0:11] == 'iteration: ':
                    if int(line.split(' ')[1]) == LitNum:
                        lit_switch = True
                    else:
                        lit_switch = False
                    literation = LitNum
            else:
                if line[0:11] == 'iteration: ':
                    literation = int(line.split(' ')[1])

            #if reading is enabled
            if lit_switch:
                
                #if it has the correct length
                info = line.strip(' ').strip('\n').split()
                if len(info) == 4:
                    
                    #write the row name
                    write_info = str(literation) + ','
                    
                    for word in info:
                        write_info += word

                        #if it is not last add ',' else \n
                        if word != info[-1]:
                            write_info += ','
                        else:
                            write_info += '\n'
                    write_file.write(write_info)
    return 0


