import math


def real_PDB_chain_int(unique_chain, split_position, split_resi_count, split_atom_count, split_resi_type, split_atom_type, split_resi_position):
    """
    This function takes a complex protein structure and determines which chains and residues are interacting
    with each other based on the distance between atoms. The output is a tuple that includes the following lists:

    Args:
        unique_chain (list): Unique chains within the protein structure
        split_position (list of list): Each sublist contains the positions of atoms in a specific chain
        split_resi_count (list of list): Each sublist contains the residue count of atoms in a specific chain
        split_atom_count (list of list): Each sublist contains the atom count in a specific chain
        split_resi_type (list of list): aEach sublist contains the residue type of atoms in a specific chain
        split_atom_type (list of list): Each sublist contains the atom type of atoms in a specific chain
        split_resi_position (list of list): Each sublist contains the residue position of atoms in a specific chain
    
    Returns:
        reaction_chain (list of list): Each sublist contains the chain IDs of two chains that are interacting with each other
        reaction_resi_count (list of list of list): Each sub-sublist contains pairs of residue counts that are interacting
        reaction_resi_type (list of list of list): Each sub-sublist contains pairs of residue types that are interacting
        reaction_resi_position (list of list of list): Each sub-sublist contains pairs of residue positions that are interacting
        reaction_atom (list of list): Each sublist contains pairs of atom counts that are interacting
        reaction_atom_position (list of list): Each sublist contains pairs of atom positions that are interacting
        reaction_atom_distance (list): a list of distances between interacting atoms
        reaction_atom_type (list of list): Each sublist contains pairs of atom types that are interacting
    """

    distance = 0
    # list of lists (each sublist will include two letters indicating these two chains have
    reaction_chain = []
    # interaction) eg: in this protein, only chain A&B, A&D and C&D are interacting, then the list will look like
    # [[A,B],[A,D],[C,D]]
    # list of lists of lists(each sub-sublist will include a bunch of lists of residue pairs
    reaction_resi_type = []
    # (without repeats)) eg: [[[resia,resib],[resic,resid]],[[resie,resif],[resig,resih]],[[resii,resij],[resik,resil]]]
    # ----reaction residues of chain-------- A&B------------------------A&D-------------------------C&D -------------
    reaction_resi_count = []
    reaction_atom = []
    reaction_atom_position = []
    reaction_atom_distance = []
    reaction_atom_type = []
    reaction_resi_position = []
    for i in range(len(unique_chain) - 1):
        for j in range(i+1, len(unique_chain)):
            inner_atom_position = []
            inner_atom_distance = []
            inner_atom = []
            inner_reaction_resi_count = []
            inner_reaction_resi_type = []
            inner_reaction_atom_type = []
            inner_reaction_resi_position = []
            for m in range(len(split_position[i])):
                for n in range(len(split_position[j])):
                    distance = math.sqrt((split_position[i][m][0]-split_position[j][n][0])**2
                                         + (split_position[i][m][1]-split_position[j][n][1])**2
                                         + (split_position[i][m][2]-split_position[j][n][2])**2)
                    if distance <= 0.3:
                        inner_atom.append(
                            [split_atom_count[i][m], split_atom_count[j][n]])
                        inner_atom_distance.append(distance)
                        inner_atom_position.append(
                            [split_position[i][m], split_position[j][n]])
                        inner_reaction_atom_type.append(
                            [split_atom_type[i][m], split_atom_type[j][n]])
                        if [split_resi_count[i][m], split_resi_count[j][n]] not in inner_reaction_resi_count:
                            inner_reaction_resi_count.append(
                                [split_resi_count[i][m], split_resi_count[j][n]])
                            inner_reaction_resi_position.append(
                                [split_resi_position[i][m], split_resi_position[j][n]])
                            inner_reaction_resi_type.append(
                                [split_resi_type[i][m], split_resi_type[j][n]])
            if len(inner_reaction_resi_count) > 0:
                reaction_chain.append([unique_chain[i], unique_chain[j]])
                reaction_resi_count.append(inner_reaction_resi_count)
                reaction_resi_type.append(inner_reaction_resi_type)
                reaction_atom.append(inner_atom)
                reaction_atom_position.append(inner_atom_position)
                reaction_atom_distance.append(inner_atom_distance)
                reaction_atom_type.append(inner_reaction_atom_type)
                reaction_resi_position.append(inner_reaction_resi_position)
    return reaction_chain, reaction_atom, reaction_atom_position, reaction_atom_distance, reaction_resi_count, \
        reaction_resi_type, reaction_atom_type, reaction_resi_position


