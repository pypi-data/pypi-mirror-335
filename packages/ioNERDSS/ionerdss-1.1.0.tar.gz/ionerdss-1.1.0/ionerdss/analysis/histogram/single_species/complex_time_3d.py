import numpy as np
import matplotlib.pyplot as plt
from .hist_temp import hist_temp
from ...file_managment.save_vars_to_file import save_vars_to_file

def complex_time_3d(
    graph_type: int, 
    graphed_data: int, 
    full_hist: list, 
    file_num: int, 
    initial_time: float, 
    final_time: float,
    species_name: str, 
    time_bins: int, 
    x_bar_size: int = 1, 
    show_fig: bool = True,
    show_mean: bool = False, 
    show_std: bool = False, 
    save_fig: bool = False, 
    save_vars: bool = False
):
    """Generates various 3D time-based plots from histogram data.

    This function creates different types of 3D time graphs, such as heatmaps and histograms, 
    to visualize species' size distribution over time.

    Args:
        graph_type (int): 
            Type of graph to display. 
            - 1: Heatmap 
            - 2: 3D Histogram
        graphed_data (int): 
            Type of data to visualize. 
            - 1: Complex count
            - 2: Monomer count
            - 3: Monomer fraction
        full_hist (list): 
            List containing all histogram data from `histogram.dat`.
        file_num (int): 
            Number of input files. File names should follow `[filename]_1, [filename]_2, ...` format.
        initial_time (float): 
            Starting time for analysis. Must be within the range of recorded times. Initial time inclusive.
        final_time (float): 
            Ending time for analysis. Must be within the range of recorded times. Final time exclusive.
        species_name (str): 
            Name of the species to analyze. Should be present in the `.dat` file.
        time_bins (int): 
            Number of time bins to divide the selected time period.
        x_bar_size (int, optional): 
            Width of each data bar in the x-dimension. Defaults to 1.
        show_fig (bool, optional): 
            Whether to display the generated figure. Defaults to True.
        show_mean (bool, optional): 
            Whether to overlay mean values on the figure. Defaults to False.
        show_std (bool, optional): 
            Whether to overlay standard deviation values on the figure. Defaults to False.
        save_fig (bool, optional): 
            Whether to save the generated figure. Defaults to False.
        save_vars (bool, optional): 
            Whether to save calculated variables to a file. Defaults to False.

    Returns:
        tuple: 
            - np.ndarray: Complex sizes (`n_list`)
            - np.ndarray: Time bins (`t_list`)
            - np.ndarray: Mean count of species in complexes over time (`count_list_mean`)
            - np.ndarray: Standard deviation (`count_list_std`)

    Raises:
        ValueError: If an invalid `graph_type` or `graphed_data` is provided.
    """

    if not full_hist:
        return ([], [], np.array([]), np.array([]))
    
    # Create time bins
    t_list = np.linspace(initial_time, final_time, time_bins + 1)

    # Define graph titles and labels
    graph_titles = {
        1: "Size Distribution Over Time",
        2: "Total Monomers in Complexes Over Time",
        3: "Fraction of Monomers in Complexes Over Time"
    }
    
    z_labels = {
        1: "Number of Complexes",
        2: "Number of Monomers",
        3: "Fraction of Monomers"
    }

    if graphed_data not in graph_titles:
        raise ValueError("Invalid `graphed_data` value. Choose 1 (complex count), 2 (monomer count), or 3 (monomer fraction).")

    graph_title = graph_titles[graphed_data]
    z_label = z_labels[graphed_data]

    x_list_tot, z_list_tot = [], []
    
    for hist in full_hist:
        n_tot = hist[0][1][0] if graphed_data == 3 else 1

        max_species_size = 0
        x_list, z_list = [], []

        for i in range(len(t_list) - 1):
            # Format time labels differently for each graph type
            if graph_type == 1:
                time_label = f"{t_list[i]:.2f}s ~ {t_list[i+1]:.2f}s"
            elif graph_type == 2:
                time_label = (t_list[i] + t_list[i+1]) / 2
            else:
                raise ValueError("Invalid `graph_type` value. Choose 1 (heatmap) or 2 (3D histogram).")

            x, z = hist_temp(hist, t_list[i], t_list[i+1])
            x_list.append(x)
            z_list.append(z)
            max_species_size = max(max_species_size, max(x))

        # Initialize data storage arrays
        z_array = np.zeros((max_species_size, time_bins))

        # Populate z_array with values
        for t_idx, x_vals in enumerate(x_list):
            for x_idx, x_val in enumerate(x_vals):
                z_array[x_val - 1, t_idx] = z_list[t_idx][x_idx]

        # Adjust for monomer count or fraction if needed
        if graphed_data >= 2:
            z_array = np.array([
                [(z_val * (idx + 1) / n_tot) for z_val in row]
                for idx, row in enumerate(z_array)
            ])

        z_array = z_array.T

        # Aggregate results
        x_list_tot.append(np.arange(1, max_species_size + 1, x_bar_size))
        z_list_tot.append(z_array.tolist())

    # Compute mean and standard deviation across files
    count_list_mean = np.mean(z_list_tot, axis=0)
    count_list_std = np.std(z_list_tot, axis=0)

    # Save variables if required
    if save_vars:
        var_data = {"complex_sizes": x_list_tot[0], "time_bins": t_list, "data": count_list_mean, "std_dev": count_list_std}
        save_vars_to_file(var_data)

    # Generate plot
    if show_fig:
        fig, ax = plt.subplots()
        
        if graph_type == 1:
            im = ax.imshow(count_list_mean, aspect='auto')
            ax.set_xticks(np.arange(len(x_list_tot[0])))
            ax.set_yticks(np.arange(len(t_list)))
            ax.set_xticklabels(x_list_tot[0])
            ax.set_yticklabels([f"{t:.2f}s" for t in t_list])

            if show_mean and show_std:
                raise ValueError("Cannot display both mean and standard deviation at the same time.")

            if show_mean:
                for i in range(len(t_list)):
                    for j in range(len(x_list_tot[0])):
                        ax.text(j, i, f"{count_list_mean[i, j]:.1f}", ha='center', va='center', color='w')
            elif show_std and file_num > 1:
                for i in range(len(t_list)):
                    for j in range(len(x_list_tot[0])):
                        ax.text(j, i, f"{count_list_std[i, j]:.1f}", ha='center', va='center', color='w')

            plt.colorbar(im)
            plt.xlabel("Size of Complex")
            plt.ylabel("Time (s)")
        
        ax.set_title(graph_title)
        if save_fig:
            plt.savefig(f"{graph_title.replace(' ', '_').lower()}.png", dpi=600)

        plt.show()

    return x_list_tot[0], t_list, count_list_mean, count_list_std
