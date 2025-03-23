def read_restart(file_name_restart):
    """Read restart file and extract information about complexes and their components.

    Args:
        file_name_restart (str): the name of the restart file to be read.

    Returns:
        complex_lst (list): a list of lists, where each sub-list represents a complex and contains the IDs of its components.

    Examples:
        >>> RESTART_read_restart('restart.txt')
        The total number of complexes is 10
        [[1, 2, 3], [4, 5, 6], [7, 8, 9, 10], [11, 12], [13, 14, 15], [16, 17, 18], [19, 20], [21, 22], [23, 24], [25, 26, 27]]
    """
    with open(file_name_restart, 'r') as file:
        status = False
        count = 0
        complex_lst = []
        for line in file.readlines():
            if line == '#All Complexes and their components \n':
                status = True
            if status:
                if count % 8 == 7:
                    info = line.split()
                    temp_lst = []
                    for i in range(len(info)):
                        if i != 0:
                            temp_lst.append(int(info[i]))
                    complex_lst.append(temp_lst)
                count += 1
            if line == '#Observables \n':
                break
    print('The total number of complexes is', len(complex_lst))
    return complex_lst


