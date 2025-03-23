def write_pdb(file_name_pdb, protein_remain, OpName):
    """Reads a PDB file and creates a new PDB file with only the atoms that correspond to the protein_remain list.

    Args:
        file_name_pdb (str): the name of the input PDB file
        protein_remain (List[int]): a list of integers with the protein numbers to be kept in the new PDB file
        OpName (string): name of the outputted file

    Returns:
        int: 0, indicating that the function has finished executing

    Example:
        >>> RESTART_new_pdb('input_file.pdb', [1, 2, 3, 5])
        0
    """
    
    with open(file_name_pdb, 'r') as file:
        write_lst = []
        for line in file.readlines():
            line_ = line.split(' ')
            if line_[0] == 'TITLE':
                write_lst.append(line)
            elif line_[0] == 'CRYST1':
                write_lst.append(line)
            elif line_[0] == 'ATOM':
                info = []
                for i in line_:
                    i.strip('\n')
                    if i != '':
                        info.append(i)
                info[9] = info[9].strip('\n')
                if int(info[4]) in protein_remain:
                    write_lst.append(line)
    
    OpName = f"{OpName}.pdb"
    
    with open(OpName, 'w') as file_:
        file_.seek(0)
        file_.truncate()
        for i in write_lst:
            file_.writelines(i)
    return 0


