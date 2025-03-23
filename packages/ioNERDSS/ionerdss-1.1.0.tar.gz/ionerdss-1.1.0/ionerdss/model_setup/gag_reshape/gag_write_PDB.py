import numpy as np


def gag_write_PDB(sites_coord: list):
    
    
    read_file = open('show_structure.pdb', 'r')
    write_file = open("regularized_structure.pdb", "w")

    lines = read_file.readlines()
    sites_coord_index = 0
    interface_serial = 6
    for i in range(len(lines)):
        if(lines[i][0:4] != "ATOM"):
            write_file.write(lines[i])
        else:
            if(lines[i][13:17].strip() == "COM"):
                if(interface_serial < 6):
                    for j in range(6- interface_serial):
                        
                        write_line = "extra line\n"
                        write_file.write(str(sites_coord_index) + write_line)
                        sites_coord_index +=1 
                    
                    write_line = lines[i]
                    write_file.write(str(sites_coord_index) + write_line)
                    sites_coord_index += 1
                    interface_serial = 1
                else:
                    
                    write_line = lines[i]
                    write_file.write(str(sites_coord_index) + write_line)
                    sites_coord_index += 1
                    interface_serial = 1
            else:
                
                write_line = lines[i][:7] + format() + sites_coord[sites_coord_index] + lines[i][:54]
                write_file.write(str(sites_coord_index) + write_line)
                sites_coord_index += 1
                interface_serial += 1
        

            

    read_file.close
    write_file.close


    return 0