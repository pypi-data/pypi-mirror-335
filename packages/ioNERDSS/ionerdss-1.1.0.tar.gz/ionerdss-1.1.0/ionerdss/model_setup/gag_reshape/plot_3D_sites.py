import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .restart_pdb_to_df import *

def plot_3D_sites(positionsVec, COM_index, from_PDB = False, PathName = "",chains_included = []):
    fig = plt.figure(1)
    color_list = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
    ax = plt.axes(projection="3d")
    if from_PDB:
        if PathName == "":
            raise Exception("Please provide the path to the PDB file")
        
        positions = fake_PDB_pdb_to_df(PathName)
        # convert coordinate unit from angstrom to nm
        positions["x_coord"] = positions["x_coord"]/10.0
        positions["y_coord"] = positions["y_coord"]/10.0
        positions["z_coord"] = positions["z_coord"]/10.0
        
        if len(chains_included) != 0:
            positions = positions[positions["Protein_Name"].isin(chains_included)]
        # get the number of monomers
        monomer_count = 0
        for i in range(len(positions)):
            if(positions.iloc[i]["Site_Name"] == "COM"):
                monomer_count += 1
        
        # get count of interfaces for each monomer
        interfaces_count = []
        count = 0
        for i in range(len(positions)):
            count += 1
            if(positions.iloc[i]["Site_Name"] == "COM"):
                count = 0
            if(i+1 == len(positions) or positions.iloc[i+1]["Site_Name"] == "COM"):
                interfaces_count.append(count)
        interfaces_count = np.array(interfaces_count)

        # get the index of the COM
        COM_index = []
        curr_index = 0
        for i in range(len(interfaces_count)):
            COM_index.append(curr_index)
            curr_index += (interfaces_count[i]+1)

        # get the coordinates of the monomers
        positionsVec = np.zeros([len(positions),3])
        for i in range(len(positions)):
            positionsVec[i,:] = [positions.iloc[i]["x_coord"], positions.iloc[i]["y_coord"], positions.iloc[i]["z_coord"]]
        


    for i in range(len(COM_index)):
        ax.scatter(positionsVec[COM_index[i]][0], positionsVec[COM_index[i]][1],positionsVec[COM_index[i]][2], color=color_list[i % 9])
        if from_PDB:
            ax.text(positionsVec[COM_index[i]][0], positionsVec[COM_index[i]][1],
                    positionsVec[COM_index[i]][2], positions.iloc[COM_index[i]]["Protein_Name"], color='k')
        next_COM_index = COM_index[i+1] if i+1 < len(COM_index) else len(positionsVec)
        for j in range(COM_index[i]+1, next_COM_index):
            figure = ax.plot([positionsVec[COM_index[i]][0], positionsVec[j][0]],
                             [positionsVec[COM_index[i]][1], positionsVec[j][1]],
                             [positionsVec[COM_index[i]][2], positionsVec[j][2]], color=color_list[i % 9])
    ax.set_xlabel('x (nm)')
    ax.set_ylabel('y (nm)')
    ax.set_zlabel('z (nm)')
    plt.show()
    return 0