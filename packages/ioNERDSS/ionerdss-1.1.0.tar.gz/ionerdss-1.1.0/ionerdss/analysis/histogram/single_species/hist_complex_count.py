import numpy as np
import matplotlib.pyplot as plt
from ...file_managment.save_vars_to_file import save_vars_to_file

def hist_complex_count(
    full_hist: list, 
    file_num: int, 
    initial_time: float, 
    final_time: float, 
    species_name: str,
    bar_size: int = 1, 
    show_fig: bool = True, 
    save_fig: bool = False, 
    save_vars: bool = False
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generates a histogram of the average number of complex species that contain a specific number of species.

    This function analyzes complex species over a given time period and plots a histogram
    showing the relative count of each complex species.

    Args:
        full_hist (list): 
            A list containing all time-series data from `histogram.dat`.
        file_num (int): 
            Number of input files used for data collection.
        initial_time (float): 
            The starting time for analysis.
        final_time (float): 
            The ending time for analysis.
        species_name (str): 
            The name of the species to analyze.
        bar_size (int, optional): 
            The bin size for histogram bars. Defaults to `1`.
        show_fig (bool, optional): 
            Whether to display the histogram. Defaults to `True`.
        save_fig (bool, optional): 
            Whether to save the histogram as an image file. Defaults to `False`.
        save_vars (bool, optional): 
            Whether to save computed variables to a file. Defaults to `False`.

    Returns:
        tuple: 
            - np.ndarray: Complex sizes. If binned, this is the start of each bin.
            - np.ndarray: Mean occurrence of each complex size.
            - np.ndarray: Standard deviation of occurrence.

    Raises:
        ValueError: If `bar_size` is not positive.
        ValueError: If `file_num` is less than 1.

    Example:
        >>> hist_complex_count(full_hist, 3, 0.0, 100.0, "ProteinX")
        (array([1, 2, 3]), array([0.4, 0.6, 0.8]), array([0.1, 0.2, 0.3]))
    """

    if bar_size < 1:
        raise ValueError("`bar_size` must be at least 1.")
    
    if file_num < 1:
        raise ValueError("`file_num` must be at least 1.")

    # Initialize storage lists
    count_list, size_list = [], []

    # Process each file
    for hist in full_hist:
        size_counts = {}  # Dictionary to track counts per complex size
        data_count = 0  # Number of valid time steps

        for timestamp in hist:
            if initial_time <= timestamp[0] <= final_time:
                data_count += 1

                # Iterate through each complex type at this timestamp
                for complex_size, complex_count in zip(timestamp[2], timestamp[1]):
                    size_counts[complex_size] = size_counts.get(complex_size, 0) + complex_count

        # Normalize counts by the number of valid time steps
        if data_count > 0:
            for size in size_counts:
                size_counts[size] /= data_count
        
        # Convert dictionary to sorted lists
        sorted_sizes = np.array(sorted(size_counts.keys()))
        sorted_counts = np.array([size_counts[size] for size in sorted_sizes])

        # Append to main lists
        size_list.append(sorted_sizes)
        count_list.append(sorted_counts)

    # Determine the largest complex size across all files
    max_size = max((max(sizes) for sizes in size_list), default=0)
    if max_size == 0:
        return np.array([]), np.array([]), np.array([])  # No valid data

    # Initialize zero-padded count array
    count_list_filled = np.zeros((max_size, file_num))

    # Populate the zero-padded array
    for i, counts in enumerate(count_list):
        for j, count in enumerate(counts):
            count_list_filled[size_list[i][j] - 1, i] = count

    # **Binning Calculation**: Aggregate counts into bins of `bar_size`
    num_bins = (max_size // bar_size) + (1 if max_size % bar_size else 0)
    count_list_filled_binned = np.zeros((num_bins, file_num))

    for i in range(num_bins):
        start_idx = i * bar_size
        end_idx = min((i + 1) * bar_size, max_size)
        count_list_filled_binned[i] = np.sum(count_list_filled[start_idx:end_idx], axis=0)

    # Compute mean and standard deviation across files
    mean_values = np.nanmean(count_list_filled_binned, axis=1)
    std_values = np.nanstd(count_list_filled_binned, axis=1) if file_num > 1 else np.zeros_like(mean_values)
    binned_sizes = np.arange(1, num_bins * bar_size + 1, bar_size)

    # Save variables if requested
    if save_vars:
        save_vars_to_file({
            "complex_sizes": binned_sizes, 
            "mean": mean_values, 
            "std_dev": std_values
        })

    # Display the histogram if requested
    if show_fig:
        plt.bar(binned_sizes, mean_values, width=bar_size, yerr=std_values if file_num > 1 else None, capsize=2, color="C0")
        plt.title(f"Histogram of {species_name}")
        plt.xlabel(f"Number of {species_name} in a Single Complex")
        plt.ylabel("Count")

        if save_fig:
            plt.savefig("histogram.png", dpi=600)
        plt.show()

    return binned_sizes, mean_values, std_values
