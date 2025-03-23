from .read_restart import read_restart
from .write_pdb import write_pdb
import numpy as np

def single_locate_position_restart(FileNamePdb, ComplexSize, FileNameRestart='restart.dat'):
    """ Reads a restart.dat file and a PDB file, identifies protein complexes of a certain size, creates a new PDB file
    containing only the proteins corresponding to those complexes, and writes the new PDB file.

    Args:
        FileNamePdb (str): the name of the input PDB file
        ComplexSize (int): the size of protein complexes to be located
        FileNameRestart (str, optional): the name of the input restart.dat file (default is 'restart.dat')

    Returns:
        output_file.pdb: holds all of the proteins that were in a complex of a certain size

    """

    #read restart file
    print('Reading restart.dat...')
    complex_lst = read_restart(FileNameRestart)
    print('Reading files complete!')
    
    #find which complexes have the correct size
    protein_remain = []
    for complex in complex_lst:
        if len(complex) == ComplexSize:
            print(complex)
            print(len(complex))
            protein_remain.append(complex)
    
    #flatten list as it is a list of lists (list of complexes)
    protein_remain_flat = np.array(protein_remain).flatten()
    
    #write new PDB
    write_pdb(FileNamePdb, protein_remain_flat)
    print('PDB writing complete!(named as output_file.pdb)')
    return 0