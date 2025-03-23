import os
import numpy as np
import matplotlib.pyplot as plt
import math


def acf_coord(PDBDirectory: str, mol_list: list, sim_num: int = 1, time_step: int = -1, show_fig: bool = True, save_fig: bool = False):
    """
    Calculate the auto correlation function given a serials of .pdb files from a nerdss simulation.
    The acf is calculated based on the coordinates of all molecules in the sytem. acf = <r(0).r(t)>/<r(0).r(0)>
    The pdb files is in the PDB folder of each simulation outputs. Will plot each acf of each simulation 
    and the averaged acf of all simulations.

    Args:
    PDBDirectory: the directory of the pdb files
    mol_list: the list of molecule names to calculate the acf
    sim_num: the number of simulations to calculate the acf
    time_step: the time step of the NERDSS simulation, if not provided, will use the 1 micro seconds as the time step
    show_fig: whether to show the figure
    save_fig: whether to save the figure

    Return:
    the times (unit is simulation steps if timestep is not provided, unit is second otherwise), averaged acfs, and std
    """
    if time_step < 0:
        time_step = 1
    acfs_all_trace = []
    times_all_trace = []
    boxX, boxY, boxZ = 0.0, 0.0, 0.0
    
    columns = math.ceil(math.sqrt(sim_num))
    
    rows = columns
    plt.figure(figsize=(columns*6, rows*6))
    font = {'size': 6}
    plt.rc('font', **font)
    indexFig = 0
    
    
    for i in range(1, sim_num+1):
        pdb_directory = os.path.join(PDBDirectory, str(i), "PDB")
        if(sim_num == 1):
            pdb_directory = PDBDirectory
        print(f"processing directory: {pdb_directory}")
    
        # Get names of all the .pdb files in the folder pdb_directory;
        # each name is a number corresponding to the simulation steps;
        file_names = [f for f in os.listdir(pdb_directory) if f.endswith('.pdb')]

        if(len(file_names)<2):
            raise Exception("Please provide more than 2 pdb files to calculate the acf.")
    
        # Get the simulation step and convert it to an int; sort the ints to get the time serials
        time_serials = sorted([int(f[:-4]) for f in file_names])

        # Remove the first file
        #time_serials = time_serials[1:]

        # Remove the last file
        time_serials = time_serials[:-1]

        # Get the interval length
        interval = time_serials[1] - time_serials[0]

        start_time = time_serials[0]
        end_time = time_serials[-1]
        # figure out all the mol index
        all_mol = []
        file_name = os.path.join(pdb_directory, str(start_time)+'.pdb')
        f = open(file_name)
        line = f.readline()
        while line:
            line = f.readline()
            if len(line) == 0:
                continue
            if line[0] == 'A':  # this is a line with one interface's info
                siteName = line[12:15]
                molName = line[17:20]
                molIndex = int(line[20:26]) + 1
                molName = molName.strip()
                if siteName == 'COM' and molName in mol_list:
                    all_mol.append(molIndex)
        f.close()
        mol_type_num = len(mol_list)
        # all_mol = all_mol[mol_type_num:]
        # record all the coords
        all_x = [[None for _ in range(
            int((end_time-start_time)/interval)+1)] for _ in range(len(all_mol))]
        all_y = [[None for _ in range(
            int((end_time-start_time)/interval)+1)] for _ in range(len(all_mol))]
        all_z = [[None for _ in range(
            int((end_time-start_time)/interval)+1)] for _ in range(len(all_mol))]
        for j in range(start_time, end_time+1, interval):
            count_line = 0
            file_name = os.path.join(pdb_directory, str(j)+'.pdb')
            f = open(file_name)
            line = f.readline()
            count_line += 1
            while line:
                line = f.readline()
                count_line += 1
                count_mol = 0
                if len(line) == 0 or count_line < mol_type_num + 3:
                    if count_line == 3:
                        boxX, boxY, boxZ = float(line[30:38]), float(line[38:46]), float(line[46:54])
                    continue
                if line[0] == 'A':  # this is a line with one interface's info
                    siteName = line[12:15]
                    molName = line[17:20]
                    molName = molName.strip()
                    molIndex = int(line[20:26]) + 1
                    if siteName == 'COM' and molName in mol_list:
                        coordX1 = float(line[30:38])
                        coordY1 = float(line[38:46])
                        coordZ1 = float(line[46:54])
                        all_x[count_mol][int((j-start_time) / interval)] = coordX1 - boxX/2.0
                        all_y[count_mol][int((j-start_time) / interval)] = coordY1 - boxY/2.0
                        all_z[count_mol][int((j-start_time) / interval)] = coordZ1 - boxZ/2.0
                        count_mol += 1
                        
            f.close()
        
        # average the autocorrelation over the whole lattice (all mols)
        all_time = []
        all_rk_mean = []
        for nk in range(0, int(len(all_x[0])), 1):
            all_rk = []
            for one_mol_index in range(len(all_mol)):
                try:
                    all_rk.append((all_x[one_mol_index][0]*all_x[one_mol_index][nk]+all_y[one_mol_index][0]*all_y[one_mol_index][nk]+all_z[one_mol_index][0]*all_z[one_mol_index][nk])/(
                        all_x[one_mol_index][0]*all_x[one_mol_index][0]+all_y[one_mol_index][0]*all_y[one_mol_index][0]+all_z[one_mol_index][0]*all_z[one_mol_index][0]))
                except:
                    pass
            all_time.append(nk*interval*time_step)
            all_rk_mean.append(np.mean(all_rk))

        acfs_all_trace.append(np.array(all_rk_mean))
        times_all_trace.append(np.array(all_time))

        indexFig += 1
        plt.subplot(columns, rows, indexFig)
        plt.plot(np.array(all_time), np.array(all_rk_mean))
        plt.ylim(-1, 1)
        plt.title("Simulation #" + str(i))
        plt.xlabel("time (us)")
        plt.ylabel("ACF")

    plt.show()
    
    # average all traces
    # Find the length of the shortest trace
    min_length = min([len(time_array) for time_array in times_all_trace])

    # Truncate all traces to the shortest length
    truncated_time_arrays = [time_array[:min_length] for time_array in times_all_trace]
    truncated_acf_arrays = [acf_array[:min_length] for acf_array in acfs_all_trace]

    # Stack the truncated arrays
    stacked_time_arrays = np.stack(truncated_time_arrays)
    stacked_acf_arrays = np.stack(truncated_acf_arrays)

    # Compute the average and standard deviation along the first axis
    average_time_array = np.mean(stacked_time_arrays, axis=0)
    average_acf_array = np.mean(stacked_acf_arrays, axis=0)
    std_acf_array = np.std(stacked_acf_arrays, axis=0)

    # Plot the average_acf_array versus average_time_array with an error band
    plt.plot(average_time_array, average_acf_array)
    plt.fill_between(average_time_array, average_acf_array - std_acf_array, average_acf_array + std_acf_array, alpha=0.2)
    plt.xlabel('time (us)')
    plt.ylabel('ACF')
    plt.title('Mean ACF')
    if save_fig:
        plt.SaveFig('acf.png', dpi=300)
    if show_fig:
        plt.show()
    
    return average_time_array, average_acf_array, std_acf_array