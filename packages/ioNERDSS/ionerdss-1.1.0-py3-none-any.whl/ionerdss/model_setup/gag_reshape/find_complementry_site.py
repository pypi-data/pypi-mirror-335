import numpy as np

def find_complementry_site(p1,positions):
    target_site_name = ""
    p1_index = -1

    # figure out the target site name
    for i in range(len(positions)):
        if positions.iloc[i]["x_coord"] == p1[0] and positions.iloc[i]["y_coord"] == p1[1] and positions.iloc[i]["z_coord"] == p1[2]:
            target_site_name = positions.iloc[i]["Site_Name"]
            p1_index = i
            break
    # find the complementry site to the target site
    site_pair = positions[positions["Site_Name"] == target_site_name]
    if len(site_pair) != 2:
        raise Exception("The target site does not have a pair or has more than one pair.")
    complementary_site = site_pair[site_pair.index != p1_index]
    complementary_site_index = complementary_site.index
    p2 = np.array([complementary_site.iloc[0]["x_coord"],
                    complementary_site.iloc[0]["y_coord"],
                      complementary_site.iloc[0]["z_coord"]])
    # find the COM of the monomer with the complementary site
    complementary_site_COM_index = -1
    for i in range(len(positions)):
        if positions.iloc[i]["Site_Name"] == "COM":
            complementary_site_COM_index = i
        if i >= complementary_site_index:
            break
    complementary_site_COM = positions.iloc[complementary_site_COM_index]
    c2 = np.array([complementary_site_COM["x_coord"], complementary_site_COM["y_coord"], complementary_site_COM["z_coord"]])
    return c2, p2
    