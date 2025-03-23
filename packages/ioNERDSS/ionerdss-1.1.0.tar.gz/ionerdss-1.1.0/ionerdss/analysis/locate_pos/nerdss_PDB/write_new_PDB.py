def write_new_PDB(protein_remain, main_pdb_list, OpName):
    """Generates a new PDB file with protein information based on a list of remaining protein numbers.

    This function reads a PDB file, extracts protein information for the proteins whose numbers are specified
    in the `protein_remain` list, and writes the extracted information to a new PDB file.

    Args:
        protein_remain (list): A list of protein numbers that had the correct number of sub-proteins.
        main_pdb_list (list): A list of lists of every single line of the original inputted pdb file. info[i][0] = important data from line, info[i][1] = the line string
        OpName (str): The name of the outputted file. 

    Returns:
        .pdb file: holds all of the proteins sites that are in the complexes of the correct sizes
    """

    OpName = f"{OpName}.pdb"
    
    #write new file
    with open(OpName, 'w') as file:
        file.seek(0)
        file.truncate()
        
        #goes through the main_PDB_list which has a setup of [['info','string of line'],[],[],...] with info being the important data in that line (or description of line)
        for line in main_pdb_list:
            if line[0] == "header":
                file.writelines(line[1])
            elif line[0] in protein_remain:
                file.writelines(line[1])
    return 0


