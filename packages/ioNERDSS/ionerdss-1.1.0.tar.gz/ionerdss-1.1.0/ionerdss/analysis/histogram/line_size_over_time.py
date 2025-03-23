import numpy as np
import matplotlib.pyplot as plt
from ..file_managment.save_vars_to_file import save_vars_to_file


def line_size_over_time(
    data_type: int, 
    full_hist: list, 
    file_count: int, 
    initial_time: float, 
    final_time: float,
    species_name: str = "tot", 
    exclude_size: int = 0, 
    species_list: list = None, 
    show_fig: bool = True, 
    save_fig: bool = False, 
    save_vars: bool = False
) -> tuple[list[float], list[float], list[float]]:
    """Generates a graph showing the count of a specific protein species in a complex over time.

    This function plots the mean or maximum number of a protein species in a complex molecule 
    across a specified time period.

    Args:
        data_type (int): 
            Type of graph to generate:
            - `1`: Mean number of species in a complex.
            - `2`: Maximum number of species in a complex.
        full_hist (list): 
            List containing all time-series data from `histogram.dat`.
        file_count (int): 
            Number of input files used for data collection.
        initial_time (float): 
            The starting time for data analysis.
        final_time (float): 
            The ending time for data analysis.
        species_name (str, optional): 
            The target species to analyze. Defaults to `"tot"` (all species).
        exclude_size (int, optional): 
            Excludes complexes of size ≤ `exclude_size` from the analysis. Defaults to `0`.
        species_list (list, optional): 
            List of species in the dataset (for multi-species histograms). Defaults to `None`.
        show_fig (bool, optional): 
            Whether to display the generated plot. Defaults to `True`.
        save_fig (bool, optional): 
            Whether to save the generated plot as a file. Defaults to `False`.
        save_vars (bool, optional): 
            Whether to save computed data variables to a file. Defaults to `False`.

    Returns:
        tuple: 
            - list[float]: Time points.
            - list[float]: Mean or max species count at each time point.
            - list[float]: Standard deviation of species count at each time point.

    Raises:
        ValueError: If `data_type` is not 1 or 2.
        ValueError: If `exclude_size` is negative.

    Example:
        >>> line_size_over_time(1, full_hist, 3, 0.0, 100.0)
        ([0.0, 50.0, 100.0], [5.2, 7.1, 4.9], [0.8, 1.2, 0.7])
    """

    if data_type not in [1, 2]:
        raise ValueError("Invalid `data_type`. Choose 1 (mean) or 2 (max).")
    
    if exclude_size < 0:
        raise ValueError("`exclude_size` cannot be negative.")

    # Define graph title and y-axis label
    graph_title = f"{'Average' if data_type == 1 else 'Maximum'} Number of {species_name} in a Single Complex"
    y_label = f"{'Average' if data_type == 1 else 'Maximum'} Number of {species_name}"

    time_list, size_list = [], []
    max_size, max_index = 0, -1

    for index, hist in enumerate(full_hist):
        time_steps, size_values = [], []

        for timestamp in hist:
            if initial_time <= timestamp[0] <= final_time:
                time_steps.append(timestamp[0])

                # Extract species data
                if species_list:
                    if species_name != "tot":
                        if species_name in species_list:
                            species_idx = species_list.index(species_name)
                            species_data = [complex_[species_idx] for complex_ in timestamp[1:]]
                            species_count = [complex_[-1] for complex_ in timestamp[1:]]  # Last column stores count
                        else:
                            species_data = []
                            species_count = []
                    else:
                        species_data = [sum(complex_[:-1]) for complex_ in timestamp[1:]]
                        species_count = [complex_[-1] for complex_ in timestamp[1:]]
                else:
                    species_data = timestamp[2]
                    species_count = timestamp[1]

                # Compute mean or max species count
                total_count = 0
                total_size = 0
                max_species_size = 0  # Track the largest complex size for max calculation

                for i, species_size in enumerate(species_data):
                    if species_size > exclude_size:
                        total_count += species_count[i]
                        total_size += species_size * species_count[i]
                        max_species_size = max(max_species_size, species_size)

                # Store mean or max value
                if total_count > 0:
                    size_values.append(total_size / total_count if data_type == 1 else max_species_size)
                else:
                    size_values.append(0)

        # Update max size index for longest `size_values`
        if len(size_values) > max_size:
            max_size, max_index = len(size_values), index

        time_list.append(time_steps)
        size_list.append(size_values)

    # Normalize sizes for consistency across files
    for i, size_data in enumerate(size_list):
        if len(size_data) != max_size:
            zero_padded = np.zeros(max_size)
            zero_padded[:len(size_data)] = size_data
            size_list[i] = zero_padded

    # Compute mean and standard deviation
    size_list_transposed = np.transpose(size_list)
    mean_values = [np.nanmean(timestep) for timestep in size_list_transposed]
    std_values = [np.nanstd(timestep) if file_count > 1 else 0 for timestep in size_list_transposed]

    # Save variables if requested
    if save_vars:
        save_vars_to_file({
            "time_stamp": time_list[max_index] if max_index >= 0 else [], 
            "mean_cmplx_size" if data_type == 1 else "max_cmplx_size": mean_values, 
            "std": std_values
        })

    # Plot the figure if requested
    if show_fig and max_index >= 0:
        plt.plot(time_list[max_index], mean_values, color='C0')
        if file_count > 1:
            plt.errorbar(time_list[max_index], mean_values, yerr=std_values, ecolor='#c9e3f6', color='C0')
        plt.title(graph_title)
        plt.xlabel("Time (s)")
        plt.ylabel(y_label)
        if save_fig:
            plt.savefig(f"{'mean' if data_type == 1 else 'max'}_complex.png", dpi=600)
        plt.show()

    return time_list[max_index] if max_index >= 0 else [], mean_values, std_values
