import numpy as np
import pandas as pd
from .restart_pdb_to_df import *

def calc_rmsError(PathName: str, fitted_sphere_params: list):
    
    # positions = fake_PDB_pdb_to_df("show_structure.pdb")
    positions = fake_PDB_pdb_to_df(PathName)
    # convert coordinate unit from angstrom to nm
    positions["x_coord"] = positions["x_coord"]/10.0
    positions["y_coord"] = positions["y_coord"]/10.0
    positions["z_coord"] = positions["z_coord"]/10.0

    # get the number of monomers
    monomer_count = 0
    for i in range(len(positions)):
        if(positions.iloc[i]["Cite_Name"] == "COM"):
            monomer_count += 1
    
    # get count of interfaces for each monomer
    interfaces_count = []
    count = 0
    for i in range(len(positions)):
        count += 1
        if(positions.iloc[i]["Cite_Name"] == "COM"):
            count = 0
        if(i+1 == len(positions) or positions.iloc[i+1]["Cite_Name"] == "COM"):
            interfaces_count.append(count)
    interfaces_count = np.array(interfaces_count)

    # get the index of the COM
    COM_index = []
    curr_index = 0
    for i in range(len(interfaces_count)):
        COM_index.append(curr_index)
        curr_index += (interfaces_count[i]+1)

    # get the distance from the sphere center
    distance_r = []
    for i in range(len(COM_index)):
        COM_coord = [positions.iloc[COM_index[i]]["x_coord"], positions.iloc[COM_index[i]]["y_coord"], positions.iloc[COM_index[i]]["z_coord"]]
        distance_from_sphere_center = np.linalg.norm(np.array(COM_coord) - np.array(fitted_sphere_params[:3]))
        distance_r.append(distance_from_sphere_center)
    distance_r = np.array(distance_r)
    distance_r_std = np.std(distance_r)
    # print(distance_r)
    print("std from sphere center: ", distance_r_std)
    return 0
    


