import numpy as np
from .gen.real_PDB_angles import real_PDB_angles
from .gen.real_PDB_norm_check import real_PDB_norm_check
# This function will calculate five necessary angles: theta_one, theta_two, phi_one, phi_two and omega
# Input variables: four coordinates indicating COM and interaction site of two chains
# First created by Yian Qian
# Modified by Mankun Sang on 04/13/2022
#   1) unit of zero vector and length-one vector
#   2) error messages when v // n
#   3) test scripts
# Modified by Yian Qian & Mankun Sang on 04/16/2022
#   0) correct omega calculation when n // sigma
#   1) generalize the sign determination of phi and omega
#   2) created a function for phi cacluation

def dtb_PDB_calc_angle(Result: tuple, NormVector: list = [0.,0.,1.]):
    """
    This function calculates the 5 associating angles of each pair of interfaces.
    The default normal vector will be assigned as (0, 0, 1). If the co-linear issue occurs, 
    the system will use (0, 1, 0) instead to resolve co-linear issue. The calculated 5 angles 
    will be shown on the screen automatically. If user intends to manually input the normal vector, 
    please refer to function ‘real_PDB_UI’, the separated function does not support manual inputs.
    
    Args:
        Result (5 length tuple): The output result of function(s): 'read','filter','sigma', or first five of function(s): 'COM'
        NormVector (list, optional): The normal vector used to calculate the angles
        ThrowError(bool, optional = True): If a co-linear or syntax error occurs, whether 
        it will continue or stop the program. Recommended to keep as True.
    
    Returns:
        9 length Tuple: All the information for further analysis, including the 5 associating angles of each pair of interfaces.
    """

    reaction_chain, new_int_site, new_int_site_distance, unique_chain, COM = Result
    angle = []
    normal_point_lst1 = []
    normal_point_lst2 = []
    for i in range(len(reaction_chain)):
        chain1 = 0
        chain2 = 0
        for j in range(len(unique_chain)):
            if reaction_chain[i][0] == unique_chain[j]:
                chain1 = j
            if reaction_chain[i][1] == unique_chain[j]:
                chain2 = j
            if reaction_chain[i][0] == unique_chain[chain1] and reaction_chain[i][1] == unique_chain[chain2]:
                break
        
        if NormVector == [0.,0.,1.]:
            normal_point_lst1.append([0., 0., 1.])
            if real_PDB_norm_check(normal_point_lst1[-1], COM[chain1], new_int_site[i][0]) == False:
                pass
            else:
                normal_point_lst1.remove(normal_point_lst1[-1])
                normal_point_lst1.append([0., 1., 0.])

            normal_point_lst2.append([0., 0., 1.])
            if real_PDB_norm_check(normal_point_lst2[-1], COM[chain2], new_int_site[i][1]) == False:
                pass
            else:
                normal_point_lst2.remove(normal_point_lst2[-1])
                normal_point_lst2.append([0., 1., 0.])
        else:
            normal_point_lst1.append(NormVector)
            if real_PDB_norm_check(normal_point_lst1[-1], COM[chain1], new_int_site[i][0]) == False:
                pass
            else:
                raise Exception("Value inputted is invalid because of co-linear or syntax issues")

            normal_point_lst2.append(NormVector)
            if real_PDB_norm_check(normal_point_lst2[-1], COM[chain2], new_int_site[i][1]) == False:
                pass
            else:
                raise Exception("Value inputted is invalid because of co-linear or syntax issues")

        inner_angle = real_PDB_angles(COM[chain1], COM[chain2], new_int_site[i][0], new_int_site[i][1], np.array(
            COM[chain1]) + np.array(normal_point_lst1[-1]), np.array(COM[chain2]) + np.array(normal_point_lst2[-1]))
        angle.append([inner_angle[0], inner_angle[1], inner_angle[2],
                      inner_angle[3], inner_angle[4], inner_angle[5]])
        print("Angles for chain " +
              str(unique_chain[chain1]) + " & " + str(unique_chain[chain2]))
        print("Theta1: %.3f, Theta2: %.3f, Phi1: %.3f, Phi2: %.3f, Omega: %.3f" % (
            inner_angle[0], inner_angle[1], inner_angle[2], inner_angle[3], inner_angle[4]))

    # looking for chains possess only 1 inferface.
    reaction_chain_1d = []
    one_site_chain = []
    for i in reaction_chain:
        for j in i:
            reaction_chain_1d.append(j)
    for i in unique_chain:
        if reaction_chain_1d.count(i) == 1:
            one_site_chain.append(i)
    return reaction_chain, new_int_site, new_int_site_distance, unique_chain, COM, angle, normal_point_lst1, normal_point_lst2, one_site_chain


