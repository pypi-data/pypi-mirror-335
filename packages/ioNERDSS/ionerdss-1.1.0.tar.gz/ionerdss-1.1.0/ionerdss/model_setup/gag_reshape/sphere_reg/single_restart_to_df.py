import pandas as pd

def helper_PDB_pdb_to_df(file_name, protein_num):
    """Helper function to read PDB file and return a pandas dataframe

    Args:
        file_name (String): The path and name of the PDB file
        protein_num (int): the protein number intended to be incorporated into the dataframe

    Returns:
        dataframe: the pandas dataframe contains the atom information read from the PDB file
    """
    df = pd.DataFrame(columns=['Protein_Num', 'Protein_Name',
                      'Cite_Name', 'x_coord', 'y_coord', 'z_coord'])
    with open(file_name, 'r') as file:
        index = 0
        for line in file.readlines():
            line = line.split(' ')
            if line[0] == 'ATOM':
                info = []
                for i in line:
                    if i != '':
                        info.append(i)
                if info[2] == 'COM' and int(info[4]) in protein_num:
                    df.loc[index, 'Protein_Num'] = int(info[4])
                    df.loc[index, 'Protein_Name'] = info[3]
                    df.loc[index, 'Cite_Name'] = info[2]
                    df.loc[index, 'x_coord'] = float(info[5])
                    df.loc[index, 'y_coord'] = float(info[6])
                    df.loc[index, 'z_coord'] = float(info[7])
                    index += 1
        df = df.dropna()
        df = df.reset_index(drop=True)
    return df


def helper_RESTART_read_restart(file_name_restart):
    """helper function to read restart file and return a list of the complexes existing at the end of the iteration

    Args:
        file_name_restart (String): The path and name of the RESTART file

    Returns:
        list: a list of the complexes existing at the end of the iteration. For instance, [[1,2,3],[4,5,6]] 
        means there are two complexes, one contains molecule 1,2,3 and the other contains molecule 4,5,6
    """
    with open(file_name_restart, 'r') as file:
        status = False
        count = 0
        complex_lst = []
        for line in file.readlines():
            if line == '#All Complexes and their components \n':
                status = True
            if status:
                if count % 8 == 7:
                    info = line.split()
                    temp_lst = []
                    for i in range(len(info)):
                        if i != 0:
                            temp_lst.append(int(info[i]))
                    complex_lst.append(temp_lst)
                count += 1
            if line == '#Observables \n':
                break
    print('The total number of complexes is', len(complex_lst))
    return complex_lst

def single_restart_to_df(FileNamePdb, ComplexSizeList, FileNameRestart='restart.dat', SerialNum=0):
    """
    Returns a pandas dataframe of protein complex structure data and an updated serial number based on the input parameters.

    Args:
        FileNamePdb (str): file path of the PDB file containing protein complex structure data
        ComplexSizeList (list[int]): a list of integers specifying desired sizes of protein complexes
        FileNameRestart (str): file path of RESTART file containing the protein complex's restart data (default is 'restart.dat')
        SerialNum (int): the starting index of the desired protein complex in the restart file (default is 0)

    Returns:
        tuple: A tuple containing a pandas dataframe of the desired protein complex structure data and an updated serial number. If the desired size is not found, (0,-1) will be returned.
    """
    if SerialNum == -1:
        return 0, -1
    complex_list = helper_RESTART_read_restart(FileNameRestart)
    index = 0
    protein_remain = []
    for i in range(len(ComplexSizeList)):
        for j in range(len(complex_list)):
            if len(complex_list[j]) == ComplexSizeList[i]:
                index += 1
                if SerialNum == index-1:
                    protein_remain = complex_list[j]
                    SerialNum += 1
                    complex_pdb_df = helper_PDB_pdb_to_df(FileNamePdb, protein_remain)
                    # if 0 in complex_pdb_df.index:
                    #     complex_pdb_df = complex_pdb_df.drop(0)
                    return complex_pdb_df, SerialNum
    print('Cannot find more desired size of complex!')
    return 0, -1
