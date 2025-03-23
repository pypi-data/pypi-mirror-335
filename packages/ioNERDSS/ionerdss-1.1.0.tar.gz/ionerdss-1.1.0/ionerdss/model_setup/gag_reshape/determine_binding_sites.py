import numpy as np
import pandas as pd

def sort_sites(positions, COM_index, interfaces_count):
    '''
    Sort the sites in the order of increasing distance from the COM of each monomer.
    
    '''
   # find the distance from each interface to the COM for each monomer
    distances = []
    for i in range(len(COM_index)):
        COM_coord = [positions.iloc[COM_index[i]]["x_coord"], positions.iloc[COM_index[i]]["y_coord"], positions.iloc[COM_index[i]]["z_coord"]]
        distances.append(0)
        for j in range(interfaces_count[i]):
            interface_coord = [positions.iloc[COM_index[i]+j+1]["x_coord"], positions.iloc[COM_index[i]+j+1]["y_coord"], positions.iloc[COM_index[i]+j+1]["z_coord"]]
            distances.append(np.linalg.norm(np.array(COM_coord)-np.array(interface_coord)))
    positions["Distance"] = distances
    
    # eliminate inconsistent sites (sites that are only present on some monomers)
    # obtain the consistent sites, using distances from interfaces to COM to identify sites
    valid_sites_num = np.min(interfaces_count)
    valid_sites_dist = []
    for i in range(valid_sites_num):
        valid_sites_dist.append(positions.iloc[COM_index[interfaces_count.argmin()]+i+1]["Distance"])
    
    temp_positions = pd.DataFrame({})
    temp_distances = []
    for i in range(len(COM_index)):
        for j in range(valid_sites_num):
            temp_distances = distances[COM_index[i]+1:COM_index[i]+interfaces_count[i]+1]
            temp_distances = np.abs(temp_distances - valid_sites_dist[j])
            closest_site_index = temp_distances.argmin()
            if(j == 0):
                temp_positions = pd.concat([temp_positions, positions.iloc[[COM_index[i]]]], ignore_index = True)
            temp_positions = pd.concat([temp_positions, positions.iloc[[COM_index[i]+closest_site_index+1]]], ignore_index = True)
    positions = temp_positions
    return positions