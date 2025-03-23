def dtb_PDB_write_PDB(Result: bool):
    """
    Generates a PDB file containing the calculated COMs and reaction interfaces for visualization and comparison with the 
    original PDB file. The input must be the output result of the 'real_PDB_separate_read' function. Note that the unit for 
    the coordinates in the PDB file is Angstrom, not nm, so the values will be 10 times larger than those in NERDSS input 
    files.

    Parameters:
        Result (5 length tuple): The output result of function(s): 'read','filter','sigma', or first five of function(s): 'angle','COM'

    Returns:
        .pdb file.
    """
        
    reaction_chain, int_site, int_site_distance, unique_chain, COM = Result
    f = open('show_structure.pdb', 'w')
    f.write('TITLE  PDB\n')
    f.write('REMARK   0 THE COORDINATES IN PDB FILE IS IN UNIT OF ANGSTROM, \n')
    f.write('REMARK   0 SO THE VALUE WILL BE 10 TIMES LARGER THAN NERDSS INPUTS.\n')
    tot_count = 0
    for i in range(len(unique_chain)):
        f.write('ATOM' + ' '*(7-len(str(tot_count))) + str(tot_count)[:7] + '  COM' +
                ' '*(4-len(unique_chain[i])) + unique_chain[i][:4] + ' '*(5-len(str(i))) + str(i)[:5] +
                ' '*(13-len(str(round(COM[i][0]*10, 3)))) + str(round(COM[i][0]*10, 3)) +
                ' '*(8-len(str(round(COM[i][1]*10, 3)))) + str(round(COM[i][1]*10, 3)) +
                ' '*(8-len(str(round(COM[i][2]*10, 3)))) + str(round(COM[i][2]*10, 3)) +
                '     0     0CL\n')
        tot_count += 1
        for j in range(len(reaction_chain)):
            if unique_chain[i] in reaction_chain[j]:
                if unique_chain[i] == reaction_chain[j][0]:
                    # react_site = reaction_chain[j][1].lower()
                    react_coord = int_site[j][0]
                else:
                    # react_site = reaction_chain[j][0].lower()
                    react_coord = int_site[j][1]
                react_site = reaction_chain[j][0] + reaction_chain[j][1]
                f.write('ATOM' + ' '*(7-len(str(tot_count))) + str(tot_count)[:7] +
                        ' '*(5-len(str(react_site))) + str(react_site)[:5] +
                        ' '*(4-len(unique_chain[i])) + unique_chain[i][:4] + ' '*(5-len(str(i))) + str(i)[:5] +
                        ' '*(13-len(str(round(react_coord[0]*10, 3)))) + str(round(react_coord[0]*10, 3)) +
                        ' '*(8-len(str(round(react_coord[1]*10, 3)))) + str(round(react_coord[1]*10, 3)) +
                        ' '*(8-len(str(round(react_coord[2]*10, 3)))) + str(round(react_coord[2]*10, 3)) +
                        '     0     0CL\n')
                tot_count += 1
    print('PDB writing complete! (named as show_structure.pdb)')
    return 0


