def real_PDB_norm_input(normal_point_lst, chain_name, chain_pair1, chain_pair2):
    """
    Takes user input for normal vector of a chain in a pair of chains and adds it to a list.

    Args:
        normal_point_lst (list): A list to which the normal vector will be appended.
        chain_name (str): The name of the chain for which the normal vector is being input.
        chain_pair1 (str): The name of the first pair for which the normal vector is being input.
        chain_pair2 (str): The name of the other pair for which the normal vector is being input.

    Returns:
        list: A list containing the updated normal vector list after appending the new normal vector input by the user.
    """

    normal_point_1_temp = input('Please input normal vector for ' +
                                chain_name + ' in chain ' + chain_pair1 + " & " + chain_pair2 + ' : ')
    normal_point_1_temp = normal_point_1_temp.strip('[').strip(']').split(',')
    normal_point_1_temp_ = []
    for j in normal_point_1_temp:
        normal_point_1_temp_.append(float(j))
    normal_point_lst.append(normal_point_1_temp_)
    return normal_point_lst


