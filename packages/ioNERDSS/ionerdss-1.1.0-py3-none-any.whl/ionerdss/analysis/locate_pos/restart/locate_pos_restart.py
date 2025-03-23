from .read_restart import read_restart
from .read_pdb import read_pdb
from .find_complexes import find_complexes
from .write_pdb import write_pdb


def locate_pos_restart(FileNamePdb, NumDict, FileNameRestart='restart.dat', OpName = "output_file"):
    """
    Locates specific complexes of a certain size from a PDB file along with 'restart.dat' file after simulation and outputs the result
    as a separated file named "output_file.pdb" containing only the desired complex.

    Args:
        FileNamePdb (str): The path to the PDB file, which is usually the last frame of simulation.
        NumDict (dictionary): A dictionary that holds the requested number of protein types in a complex
            Ex: {'dod':11,'clat':4}       
        FileNameRestart (str): The path to the 'restart.dat' file. Defaults to 'restart.dat'.
        OpName (string, Optional = "output_file"): the name of the outputted file

    Returns:
        output_file.pdb: seperate file containing only the desired complex(es)
    
    Note:
        The advantage of reading the 'restart.dat' file is that the file directly stores the binding information of each complex
        in the system and can be used directly, so the function runs faster; however, the function is not universal, if the
        'restart.dat ' file's write logic changes, then this function will no longer work.

    Raises:
        FileNotFoundError: If the specified PDB file or 'restart.dat' file cannot be found.
        TypeError: If the specified NumList is not a list of integers.

    Examples:
        >>> filter_PDB_op_restart('/Users/UserName/Documents/999999.pdb', [12], '/Users/UserName/Documents/restart.dat')
        "/Users/UserName/Documents/output_file.pdb"
    """

    #Reads restart.dat file to find which proteins are in complexes together
    print('Reading restart.dat......')
    complex_lst = read_restart(FileNameRestart)
    print('Reading files complete!')

    #Reads .pdb file and finds the name / number of each protein data point
    print('Reading PDB files......')
    sorted_complexes = read_pdb(FileNamePdb,complex_lst,NumDict)
    print('Reading files complete!')
    
    #Find all complexes that have the correct number of proteins
    print('Finding complexes......')
    protein_remain = find_complexes(sorted_complexes, NumDict)

    #Writes the new PDB file
    print('Writing new PDB files......')
    write_pdb(FileNamePdb, protein_remain, OpName)
    print(f'PDB writing complete! (named as {OpName}.pdb)')
    
    return 0
