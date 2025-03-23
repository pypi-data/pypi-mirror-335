from .read_PDB import read_PDB
from .read_inp import read_inp
from .create_bond_list import create_bond_list
from .create_complex_list import create_complex_list
from .filter_complexes import filter_complexes
from .write_new_PDB import write_new_PDB


def locate_pos_no_restart(FileNamePdb, NumDict, FileNameInp, BufferRatio=0.01, OpName = "output_file"):
    """
    Locates specific complexes of a certain size from a PDB file after simulation and outputs the result as a separated file
    named "output_file.pdb" containing only the desired complex.

    Args:
        FileNamePdb (str): The path to the PDB file, which is usually the last frame of the simulation.
        NumDict (dictionary): A dictionary that holds the requested number of protein types in a complex
            Ex: {'dod':11,'clat':4}
        FileNameInp (str): The path to the '.inp' file, which usually stores the reaction information.
        BufferRatio (float, optional): The buffer ratio used to determine whether two reaction interfaces can be considered as bonded.
            Defaults to 0.01.
        OpName (str, optional = “output_file”): The name of the outputted file. 

    Returns:
        output_file.pdb: A file containing the desired complex.

    Note:
        This function is slightly slower than the one that reads restart, but still runs quite fast.

    Examples:
        >>> locate_position_PDB('/Users/UserName/Documents/999999.pdb', [12], '/Users/UserName/Documents/parms.inp', 0.05)
        "/Users/UserName/Documents/output_file.pdb"
    """

    #reads in the .pdb file
    print('Reading files......')
    site_array,site_dict,num_name_dict,main_pdb_list = read_PDB(FileNamePdb, True)
    print('Reading files complete!')

    #reads in the .inp file
    print('Extracting binding information......')
    binding_array,binding_dict = read_inp(FileNameInp)
    print('Extracting complete!')

    #creates list of every bond
    print('Calculating distance......')
    bonds_lst = create_bond_list(site_array,site_dict,binding_array,binding_dict,BufferRatio)
    print('Calculation complete!')

    #creates list of each complex
    print('Finding complexes......')
    complex_lst = create_complex_list(bonds_lst)
    print('Finding complexes complete!')

    #creates list of each complex that has the correct number of each type
    print('Filtering complexes......')
    complex_filtered = filter_complexes(complex_lst,num_name_dict,NumDict)
    print('Filtering complexes complete!')

    #writes a new PDB file that only includs proteins that are in complexes of the correct size
    print('Writing new PDB files......')
    write_new_PDB(complex_filtered, main_pdb_list, OpName)
    print(f'PDB writing complete! (named as {OpName}.pdb)')
    return 0


