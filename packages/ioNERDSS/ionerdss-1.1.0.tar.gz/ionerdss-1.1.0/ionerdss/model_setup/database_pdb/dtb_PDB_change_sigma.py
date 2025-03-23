import math
import copy
from .gen.real_PDB_mag import real_PDB_mag


def dtb_PDB_change_sigma(Result: tuple, ChangeSigma: bool = False, SiteList: list = [], NewSigma: list = []):
    """
    This function allows users to change the value of sigma (the distance between two binding interfaces). 
    The new sigma value and the corresponding coordinates of interfaces will be shown on the screen and the 
    returns will contain all the information for further analysis. 

    Args:
        Result (5 length tuple): The output result of function(s): 'read','filter', or first five of function(s): 'angle','COM'
        ChangeSigma (bool, optional): If True, the users are capable of changing the sigma value; 
                                      if False, the sigma will remain as the original ones. 
        SiteList (list, optional): It consists of the serial numbers of the pair of interfaces for which 
                                   the user needs to modify the sigma value. The serial number is determined 
                                   by the pairing sequence shown by the function ‘real_PDB_separate_read’. 
                                   The serial number should be no greater than the total number of interface 
                                   pairs and no smaller than 0. If the serial number is 0, it means to change 
                                   all pairs of interfaces into a same sigma value.
        NewSigma (list, optional): It consists of the actual sigma value that users desire to change, according 
                                   to the sequence of input ‘SiteList’. 

    Returns:
        5 length tuple: The tuple contains all the information for further analysis.
    """

    reaction_chain, int_site, int_site_distance, unique_chain, COM = Result
    # user can choose to change the interaction site
    new_int_site_distance = copy.deepcopy(int_site_distance)
    new_int_site = copy.deepcopy(int_site)
    
    if ChangeSigma:
        for i in range(len(SiteList)):
            n = SiteList[i] - 1
            new_distance = NewSigma[i]
            
            if new_distance >= 0:
                if n == -1:
                    for p in range(0, len(reaction_chain)):
                        new_int_site_distance[p] = copy.deepcopy(
                            new_distance)
                        dir_vec1 = (
                            int_site[p][0][0] -
                            int_site[p][1][0], int_site[p][0][1] -
                            int_site[p][1][1],
                            int_site[p][0][2] - int_site[p][1][2])
                        dir_vec2 = (
                            int_site[p][1][0] -
                            int_site[p][0][0], int_site[p][1][1] -
                            int_site[p][0][1],
                            int_site[p][1][2] - int_site[p][0][2])
                        unit_dir_vec1 = [dir_vec1[0] / real_PDB_mag(dir_vec1), dir_vec1[1] / real_PDB_mag(dir_vec1),
                                         dir_vec1[2] / real_PDB_mag(dir_vec1)]
                        unit_dir_vec2 = [dir_vec2[0] / real_PDB_mag(dir_vec2), dir_vec2[1] / real_PDB_mag(dir_vec2),
                                         dir_vec2[2] / real_PDB_mag(dir_vec2)]

                        inner_new_position = []
                        new_coord1 = []
                        new_coord2 = []
                        for i in range(3):
                            new_coord1.append(
                                (new_distance - int_site_distance[p]) / 2 * unit_dir_vec1[i] + int_site[p][0][
                                    i])
                            new_coord2.append(
                                (new_distance - int_site_distance[p]) / 2 * unit_dir_vec2[i] + int_site[p][1][
                                    i])
                        inner_new_position.append(new_coord1)
                        inner_new_position.append(new_coord2)

                        new_int_site[p] = copy.deepcopy(
                            inner_new_position)
                        new_int_site_distance[p] = math.sqrt(
                            (new_int_site[p][0][0] -
                             new_int_site[p][1][0]) ** 2
                            + (new_int_site[p][0][1] -
                               new_int_site[p][1][1]) ** 2
                            + (new_int_site[p][0][2] - new_int_site[p][1][2]) ** 2)
                        # print("New interaction site of " + reaction_chain[p][0] + " & " + reaction_chain[p][
                        #     1] + " is: "
                        #     + "[%.3f, %.3f, %.3f]" % (
                        #     new_int_site[p][0][0], new_int_site[p][0][1], new_int_site[p][0][2]) + " and "
                        #     + "[%.3f, %.3f, %.3f]" % (
                        #     new_int_site[p][1][0], new_int_site[p][1][1], new_int_site[p][1][2])
                        #     + " distance between interaction sites is: %.3f" % (new_int_site_distance[p]))
                
                if n >= 0:
                    new_int_site_distance[n] = copy.deepcopy(
                        new_distance)
                    dir_vec1 = (int_site[n][0][0] - int_site[n][1][0], int_site[n][0]
                                [1] - int_site[n][1][1], int_site[n][0][2] - int_site[n][1][2])
                    dir_vec2 = (int_site[n][1][0] - int_site[n][0][0], int_site[n][1]
                                [1] - int_site[n][0][1], int_site[n][1][2] - int_site[n][0][2])
                    unit_dir_vec1 = [
                        dir_vec1[0] / real_PDB_mag(dir_vec1), dir_vec1[1] / real_PDB_mag(dir_vec1), dir_vec1[2] / real_PDB_mag(dir_vec1)]
                    unit_dir_vec2 = [
                        dir_vec2[0] / real_PDB_mag(dir_vec2), dir_vec2[1] / real_PDB_mag(dir_vec2), dir_vec2[2] / real_PDB_mag(dir_vec2)]

                    inner_new_position = []
                    new_coord1 = []
                    new_coord2 = []
                    for i in range(3):
                        new_coord1.append(
                            (new_distance - int_site_distance[n]) / 2 * unit_dir_vec1[i] + int_site[n][0][i])
                        new_coord2.append(
                            (new_distance - int_site_distance[n]) / 2 * unit_dir_vec2[i] + int_site[n][1][i])
                    inner_new_position.append(new_coord1)
                    inner_new_position.append(new_coord2)

                    new_int_site[n] = copy.deepcopy(inner_new_position)
                    new_int_site_distance[n] = math.sqrt((new_int_site[n][0][0] - new_int_site[n][1][0]) ** 2
                                                         + (new_int_site[n][0][1] - new_int_site[n][1][1]) ** 2
                                                         + (new_int_site[n][0][2] - new_int_site[n][1][2]) ** 2)
                    # print("New interaction site of " + reaction_chain[n][0] + " & " + reaction_chain[n][1] + " is: "
                    #     + "[%.3f, %.3f, %.3f]" % (
                    #         new_int_site[n][0][0], new_int_site[n][0][1], new_int_site[n][0][2]) + " and "
                    #     + "[%.3f, %.3f, %.3f]" % (
                    #     new_int_site[n][1][0], new_int_site[n][1][1], new_int_site[n][1][2])
                    #     + " distance between interaction sites is: %.3f" % (new_int_site_distance[n]) + ' nm')

        for i in range(len(new_int_site)):
            print("New interaction site of " + reaction_chain[i][0] + " & " + reaction_chain[i][1] + " is: "
                  + "[%.3f, %.3f, %.3f]" % (new_int_site[i][0][0],
                                            new_int_site[i][0][1], new_int_site[i][0][2]) + " and "
                  + "[%.3f, %.3f, %.3f]" % (new_int_site[i][1][0],
                                            new_int_site[i][1][1], new_int_site[i][1][2])
                  + " distance between new interaction sites is: %.3f nm" % (new_int_site_distance[i]))

        return reaction_chain, new_int_site, new_int_site_distance, unique_chain, COM

    else:
        return Result


