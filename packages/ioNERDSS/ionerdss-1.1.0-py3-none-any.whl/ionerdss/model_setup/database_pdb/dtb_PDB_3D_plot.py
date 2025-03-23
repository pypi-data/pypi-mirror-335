import matplotlib.pyplot as plt


def dtb_PDB_3D_plot(Result: tuple):
    """
    Generate a 3D plot to display the spatial geometry of each simplified chain.

    Parameters:
        Result (5 length tuple): The output result of function(s): 'read','filter','sigma', or first five of function(s): 'angle','COM'

    Returns:
        3D Plot.The plot will show solid lines of different colors that connect the COM with interfaces within each chain. It will also show black dotted lines that connect each pair of interfaces, and the COMs will be represented as solid points with their names above.
    
    Note:
        To interact with the plot, other IDEs rather than Jupyter Notebook (such as VSCode) are recommended.
    """

    reaction_chain, int_site, int_site_distance, unique_chain, COM = Result
    coord_list = []
    for i in range(len(unique_chain)):
        coord_list_temp = []
        coord_list_temp.append(COM[i])
        for j in range(len(reaction_chain)):
            if unique_chain[i] in reaction_chain[j]:
                if unique_chain[i] == reaction_chain[j][0]:
                    coord_list_temp.append(int_site[j][0])
                else:
                    coord_list_temp.append(int_site[j][1])
        coord_list.append(coord_list_temp)
    fig = plt.figure(1)
    color_list = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
    ax = plt.axes(projection="3d")
    for i in range(len(coord_list)):
        ax.scatter(coord_list[i][0][0], coord_list[i][0][1],
                   coord_list[i][0][2], color=color_list[i % 9])
        ax.text(coord_list[i][0][0], coord_list[i][0][1],
                coord_list[i][0][2], unique_chain[i], color='k')
        for j in range(1, len(coord_list[i])):
            figure = ax.plot([coord_list[i][0][0], coord_list[i][j][0]],
                             [coord_list[i][0][1], coord_list[i][j][1]],
                             [coord_list[i][0][2], coord_list[i][j][2]], color=color_list[i % 9])
    for i in range(len(int_site)):
        figure = ax.plot([int_site[i][0][0], int_site[i][1][0]],
                         [int_site[i][0][1], int_site[i][1][1]],
                         [int_site[i][0][2], int_site[i][1][2]], linestyle=':', color='k')
    ax.set_xlabel('x (nm)')
    ax.set_ylabel('y (nm)')
    ax.set_zlabel('z (nm)')
    plt.show()
    return 0
