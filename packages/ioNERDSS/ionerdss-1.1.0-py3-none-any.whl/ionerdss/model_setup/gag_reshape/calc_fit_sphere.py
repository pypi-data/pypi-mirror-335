import numpy as np
import pandas as pd
from .restart_pdb_to_df import *

def calc_fit_sphere(PathName: str):

    positions = fake_PDB_pdb_to_df(PathName)

    # convert coordinate unit from angstrom to nm
    positions["x_coord"] = positions["x_coord"]/10.0
    positions["y_coord"] = positions["y_coord"]/10.0
    positions["z_coord"] = positions["z_coord"]/10.0
    COM_positions = positions[positions["Cite_Name"] == "COM"]
    res = []
    for i in range(int((len(COM_positions)/50) **4)):
        # sample four random COMs
        
        rand1 = int(np.random.random()* len(COM_positions))
        rand2 = int(np.random.random()* len(COM_positions))
        while rand1 == rand2:
            rand2 = int(np.random.random()* len(COM_positions))
        rand3 = int(np.random.random()* len(COM_positions))
        while rand3 == rand2 or rand3 == rand1:
            rand3 = int(np.random.random()* len(COM_positions))
        rand4 = int(np.random.random()* len(COM_positions))
        while rand4 == rand3 or rand4 == rand2 or rand4 == rand1:
            rand4 = int(np.random.random()* len(COM_positions))
        
        

        sampled_coordinates = np.zeros([4,3])
        
        sampled_coordinates[0] = np.array([COM_positions.iloc[rand1]["x_coord"], COM_positions.iloc[rand1]["y_coord"], COM_positions.iloc[rand1]["z_coord"]])
        sampled_coordinates[1] = np.array([COM_positions.iloc[rand2]["x_coord"], COM_positions.iloc[rand2]["y_coord"], COM_positions.iloc[rand2]["z_coord"]])
        sampled_coordinates[2] = np.array([COM_positions.iloc[rand3]["x_coord"], COM_positions.iloc[rand3]["y_coord"], COM_positions.iloc[rand3]["z_coord"]])
        sampled_coordinates[3] = np.array([COM_positions.iloc[rand4]["x_coord"], COM_positions.iloc[rand4]["y_coord"], COM_positions.iloc[rand4]["z_coord"]])

        A = 2 * (sampled_coordinates[:-1] - sampled_coordinates[-1])

        # Constant vector B
        B = np.sum(sampled_coordinates[:-1]**2, axis=1) - np.sum(sampled_coordinates[-1]**2)

        # Solve the system of equations Ax = B
        center = np.linalg.solve(A, B)

        # Calculate the radius
        radius = np.linalg.norm(sampled_coordinates[0] - center)
        
        res.append(np.array([COM_positions.iloc[rand1]["Protein_Num"], 
                                                   COM_positions.iloc[rand2]["Protein_Num"], 
                                                   COM_positions.iloc[rand3]["Protein_Num"], center[0], center[1], center[2], radius]))
    res = np.array(res)
    pd.DataFrame(res).to_csv(PathName[:-4]+"_varience.csv", index=False, header=False)
    print(np.mean(res[:, 3:], axis=0))
    return np.mean(res[:, 3:], axis=0)