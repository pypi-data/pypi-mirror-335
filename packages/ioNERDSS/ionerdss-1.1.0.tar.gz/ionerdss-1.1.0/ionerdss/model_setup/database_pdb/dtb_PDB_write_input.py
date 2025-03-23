def dtb_PDB_write_input(Result: tuple):
    """
    Writes '.inp' and '.mol' files based on the calculations and modifications performed by the previous functions. Multiple '.mol' files and a single '.inp' file will be created in the same directory as the Jupyter Notebook file once the function finishes running.

    Parameters:
        Result (9 length tuple): The output result of function(s): 'angle','COM'

    Returns:
        File with new inputs for NERDSS.
    """

    (
        reaction_chain,
        new_int_site,
        new_int_site_distance,
        unique_chain,
        COM,
        angle,
        normal_point_lst1,
        normal_point_lst2,
        one_site_chain,
    ) = Result
    f = open("parm.inp", "w")
    f.write(" # Input file\n\n")
    f.write("start parameters\n")
    f.write("    nItr = 10000\n")
    f.write("    timestep = 0.1\n")
    f.write("    timeWrite = 500\n")
    f.write("    trajWrite = 500\n")
    f.write("    pdbWrite = 500\n")
    f.write("    restartWrite = 5000\n")
    f.write("end parameters\n\n")
    f.write("start boundaries\n")
    f.write("    WaterBox = [494,494,494] #nm\n")
    f.write("end boundaries\n\n")
    f.write("start molecules\n")
    for i in range(len(unique_chain)):
        f.write("     %s:10\n" % (unique_chain[i]))
    f.write("end molecules\n\n")
    f.write("start reactions\n")
    for i in range(len(reaction_chain)):
        molecule1_lower = reaction_chain[i][0].lower()
        molecule2_lower = reaction_chain[i][1].lower()
        f.write(
            "    #### %s - %s ####\n" % (reaction_chain[i][0], reaction_chain[i][1])
        )
        f.write(
            "    %s(%s) + %s(%s) <-> %s(%s!1).%s(%s!1)\n"
            % (
                reaction_chain[i][0],
                molecule2_lower,
                reaction_chain[i][1],
                molecule1_lower,
                reaction_chain[i][0],
                molecule2_lower,
                reaction_chain[i][1],
                molecule1_lower,
            )
        )
        f.write("    onRate3Dka = 10\n")
        f.write("    offRatekb = 1\n")
        f.write("    sigma = %f\n" % angle[i][5])
        f.write(
            "    norm1 = [%.6f,%.6f,%.6f]\n"
            % (
                normal_point_lst1[i][0],
                normal_point_lst1[i][1],
                normal_point_lst1[i][2],
            )
        )
        f.write(
            "    norm2 = [%.6f,%.6f,%.6f]\n"
            % (
                normal_point_lst2[i][0],
                normal_point_lst2[i][1],
                normal_point_lst2[i][2],
            )
        )
        if reaction_chain[i][0] in one_site_chain:
            angle[i][2] = "nan"
        if reaction_chain[i][1] in one_site_chain:
            angle[i][3] = "nan"
        f.write(
            "    assocAngles = ["
            + str(angle[i][0])
            + ","
            + str(angle[i][1])
            + ","
            + str(angle[i][2])
            + ","
            + str(angle[i][3])
            + ","
            + str(angle[i][4])
            + "]\n\n"
        )
    f.write("end reactions")
    f.close()

    for i in range(len(unique_chain)):
        mol_file = str(unique_chain[i]) + ".mol"
        f = open(mol_file, "w")
        f.write("##\n# %s molecule information file\n##\n\n" % unique_chain[i])
        f.write("Name    = %s\n" % unique_chain[i])
        f.write("checkOverlap = true\n\n")
        f.write("# translational diffusion constants\n")
        f.write("D       = [12.0,12.0,12.0]\n\n")
        f.write("# rotational diffusion constants\n")
        f.write("Dr      = [0.5,0.5,0.5]\n\n")
        f.write("# Coordinates, with states below, or\n")
        f.write("COM     %.4f    %.4f    %.4f\n" % (COM[i][0], COM[i][1], COM[i][2]))
        reaction_chain_merged = []
        chain_string = []
        bond_counter = 0
        for a in range(len(reaction_chain)):
            for b in range(2):
                reaction_chain_merged.append(reaction_chain[a][b])
        if unique_chain[i] not in reaction_chain_merged:
            break
        if unique_chain[i] in reaction_chain_merged:
            bond_counter = 0
            for m in range(len(reaction_chain)):
                if unique_chain[i] == reaction_chain[m][0]:
                    bond_counter += 1
                    chain_name = str(reaction_chain[m][1])
                    chain_string.append(chain_name.lower())
                    f.write(
                        "%s       %.4f    %.4f    %.4f\n"
                        % (
                            chain_name.lower(),
                            new_int_site[m][0][0],
                            new_int_site[m][0][1],
                            new_int_site[m][0][2],
                        )
                    )
                elif unique_chain[i] == reaction_chain[m][1]:
                    bond_counter += 1
                    chain_name = str(reaction_chain[m][0])
                    f.write(
                        "%s       %.4f    %.4f    %.4f\n"
                        % (
                            chain_name.lower(),
                            new_int_site[m][1][0],
                            new_int_site[m][1][1],
                            new_int_site[m][1][2],
                        )
                    )
                    chain_string.append(chain_name)
        f.write("\nbonds = %d\n" % bond_counter)
        for j in range(bond_counter):
            f.write("COM %s\n" % chain_string[j])
    print("Input files written complete.")
    return 0
