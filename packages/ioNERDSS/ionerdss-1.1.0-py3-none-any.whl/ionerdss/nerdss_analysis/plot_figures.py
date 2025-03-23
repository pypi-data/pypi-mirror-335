import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import defaultdict
from typing import Optional, Tuple
from mpl_toolkits.mplot3d import Axes3D

def plot_line_speciescopy_vs_time(
    save_dir: str,
    simulations_index: list,
    legend: list,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    Plot species copy number vs. time for selected simulations.

    Parameters:
        save_dir (str): The base directory where simulations are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Species or groups of species to plot.
            - [['A(A1!1).A(A1!1)']] → plot 'A(A1!1).A(A1!1)'
            - [['A(A1!1).A(A1!1)'], ['A(A2!1).A(A2!1)']] → plot two species separately
            - [['A(A1!1).A(A1!1)', 'A(A2!1).A(A2!1)']] → plot their sum
        show_type (str): Display mode, "both", "individuals", or "average".
        simulations_dir (list, optional): List of directories for each simulation.
        figure_size (tuple): Size of the plot figure.
    """
    # Ensure the save path for processed data exists
    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)

    # Initialize lists to store data
    all_sim_data = []

    # Load and preprocess data
    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "copy_numbers_time.dat")

        if not os.path.exists(data_file):
            print(f"Warning: {data_file} not found, skipping simulation {idx}.")
            continue

        df = pd.read_csv(data_file)
        df.rename(columns=lambda x: x.strip(), inplace=True)  # Strip spaces from column names

        # Store time and species data
        all_sim_data.append(df)

    if not all_sim_data:
        print("No valid simulation data found.")
        return
    
    # Align data to the shortest time series
    min_length = min(len(df) for df in all_sim_data)
    all_sim_data = [df.iloc[:min_length] for df in all_sim_data]

    # Compute average and standard deviation
    time_values = all_sim_data[0]["Time (s)"].values
    species_data = {}

    for species_list in legend:
        species_key = "+".join(species_list)
        values = np.array([df[species_list].sum(axis=1).values for df in all_sim_data])

        species_data[species_key] = {
            "mean": values.mean(axis=0),
            "std": values.std(axis=0),
            "raw": values
        }

    # Save processed data
    for species, data in species_data.items():
        save_path = os.path.join(plot_data_dir, f"{species.replace('+', '_')}.csv")
        df_to_save = pd.DataFrame({
            "Time (s)": time_values,
            "Mean": data["mean"],
            "Std": data["std"]
        })
        df_to_save.to_csv(save_path, index=False)
        print(f"Processed data for {species} saved to {save_path}")
    
    # Plot results
    plt.figure(figsize=(10, 6))
    sns.set_style("ticks")
    
    for species, data in species_data.items():
        if show_type in {"individuals", "both"}:
            for i, sim_values in enumerate(data["raw"]):
                plt.plot(time_values, sim_values, alpha=0.3, linestyle="dashed", label=f"{species} (simulation {i})" if show_type == "both" else None)

        if show_type in {"average", "both"}:
            plt.plot(time_values, data["mean"], label=f"{species} (average)", linewidth=2)
            plt.fill_between(time_values, data["mean"] - data["std"], data["mean"] + data["std"], alpha=0.2)

    plt.xlabel("Time (s)")
    plt.ylabel("Copy Number")
    plt.legend()
    plt.tight_layout()
    
    # Save plot
    plot_path = os.path.join(plot_data_dir, "species_vs_time_plot.svg")
    plt.savefig(plot_path, format="svg")
    print(f"Plot saved to {plot_path}")
    plt.show()

    print(f"Plot saved to {plot_path}")

def plot_line_maximum_assembly_size_vs_time(
    save_dir: str,
    simulations_index: list,
    legend: list,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    Plot the maximum assembly size vs. time based on species composition in complexes.

    Parameters:
        save_dir (str): The base directory where simulations are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Species to consider in assembly size calculation.
        show_type (str): Display mode, "both", "individuals", or "average".
        simulations_dir (list): List of simulation directories.
        figure_size (tuple): Size of the figure.
    """

    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)

    all_sim_data = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")

        if not os.path.exists(data_file):
            print(f"Warning: {data_file} not found, skipping simulation {idx}.")
            continue

        time_series = []
        max_assembly_sizes = []

        with open(data_file, "r") as f:
            lines = f.readlines()

        current_time = None
        current_complexes = []

        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                if current_time is not None:
                    # Process previous time block
                    max_size = max([sum(complex_dict.values()) for complex_dict in current_complexes], default=0)
                    time_series.append(current_time)
                    max_assembly_sizes.append(max_size)
                    current_complexes = []

                current_time = float(time_match.group(1))
            else:
                match = re.match(r"(\d+)\s+([\w\.\s:]+)", line)
                if match:
                    count = int(match.group(1))
                    species_data = match.group(2).split()
                    species_dict = {}

                    for i in range(0, len(species_data), 2):
                        species_name = species_data[i].strip(":")
                        species_count = float(species_data[i + 1].strip("."))

                        if species_name in legend:
                            species_dict[species_name] = species_dict.get(species_name, 0) + species_count

                    if species_dict:
                        total_size = sum(species_dict.values())
                        current_complexes.extend([species_dict] * count)

        if current_time is not None:
            max_size = max([sum(complex_dict.values()) for complex_dict in current_complexes], default=0)
            time_series.append(current_time)
            max_assembly_sizes.append(max_size)

        if time_series and max_assembly_sizes:
            df = pd.DataFrame({"Time (s)": time_series, "Max Assembly Size": max_assembly_sizes})
            all_sim_data.append(df)

    if not all_sim_data:
        print("No valid simulation data found.")
        return

    min_length = min(len(df) for df in all_sim_data)
    all_sim_data = [df.iloc[:min_length] for df in all_sim_data]

    time_values = all_sim_data[0]["Time (s)"].values
    max_sizes = np.array([df["Max Assembly Size"].values for df in all_sim_data])

    avg_max_size = max_sizes.mean(axis=0)
    std_max_size = max_sizes.std(axis=0)

    save_path = os.path.join(plot_data_dir, "max_assembly_size_vs_time.csv")
    df_to_save = pd.DataFrame({
        "Time (s)": time_values,
        "Mean Max Assembly Size": avg_max_size,
        "Std Max Assembly Size": std_max_size
    })
    df_to_save.to_csv(save_path, index=False)

    print(f"Processed data saved to {save_path}")

    plt.figure(figsize=figure_size)

    if show_type in {"individuals", "both"}:
        for i, sim_values in enumerate(max_sizes):
            plt.plot(time_values, sim_values, alpha=0.3, linestyle="dashed", label=f"Individual run {i}" if show_type == "both" else None)

    if show_type in {"average", "both"}:
        plt.plot(time_values, avg_max_size, label="Average", linewidth=2)
        plt.fill_between(time_values, avg_max_size - std_max_size, avg_max_size + std_max_size, alpha=0.2)

    plt.xlabel("Time (s)")
    plt.ylabel("Max Assembly Size")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "max_assembly_size_vs_time.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()

    print(f"Plot saved to {plot_path}")

def parse_complex_line(line):
    """Parse a single complex line and return a dictionary with species and counts."""
    match = re.match(r"(\d+)\s+([\w\.\s:]+)", line)
    if not match:
        return None, None

    count = int(match.group(1))  # Number of such complexes
    species_data = match.group(2).split()  # Split species and counts
    species_dict = {}

    for i in range(0, len(species_data), 2):
        species_name = species_data[i].strip(":")
        species_count = float(species_data[i + 1].strip("."))

        species_dict[species_name] = species_dict.get(species_name, 0) + species_count

    return count, species_dict

def compute_average_assembly_size(complexes, conditions):
    """
    Compute the average assembly size for given conditions.

    Parameters:
        complexes (list): List of tuples (count, species_dict) representing each complex.
        conditions (list): List of conditions, e.g., ["A>=2", "A+B>=4"].

    Returns:
        dict: Condition -> average assembly size mapping.
    """
    results = {}

    for condition in conditions:
        species_conditions = condition.split(", ")  # Handle multiple species constraints
        numerator, denominator = 0, 0

        for count, species_dict in complexes:
            valid = True
            total_size = 0

            for cond in species_conditions:
                species_match = re.match(r"(\w+)([>=<]=?|==)(\d+)", cond)
                if not species_match:
                    continue  # Skip invalid conditions

                species, operator, threshold = species_match.groups()
                threshold = int(threshold)
                species_count = species_dict.get(species, 0)

                if operator == ">=" and species_count < threshold:
                    valid = False
                elif operator == ">" and species_count <= threshold:
                    valid = False
                elif operator == "<=" and species_count > threshold:
                    valid = False
                elif operator == "<" and species_count >= threshold:
                    valid = False
                elif operator == "==" and species_count != threshold:
                    valid = False

                total_size += species_count  # Sum the species count

            if valid:
                numerator += count * total_size
                denominator += count

        results[condition] = numerator / denominator if denominator > 0 else 0

    return results

def plot_line_average_assembly_size_vs_time(
    save_dir: str,
    simulations_index: list,
    legend: list,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    Plot the average assembly size vs. time based on species composition in complexes.

    Parameters:
        save_dir (str): The base directory where simulations are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Conditions for computing average assembly size.
        show_type (str): Display mode, "both", "individuals", or "average".
        simulations_dir (list): List of simulation directories.
        figure_size (tuple): Size of the figure.
    """

    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)

    all_sim_data = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")

        if not os.path.exists(data_file):
            print(f"Warning: {data_file} not found, skipping simulation {idx}.")
            continue

        time_series = []
        condition_results = {condition: [] for condition in legend}

        with open(data_file, "r") as f:
            lines = f.readlines()

        current_time = None
        current_complexes = []

        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                if current_time is not None:
                    # Compute average size for the previous time step
                    avg_sizes = compute_average_assembly_size(current_complexes, legend)
                    for cond in legend:
                        condition_results[cond].append(avg_sizes.get(cond, 0))

                    time_series.append(current_time)
                    current_complexes = []

                current_time = float(time_match.group(1))
            else:
                count, species_dict = parse_complex_line(line)
                if species_dict:
                    current_complexes.append((count, species_dict))

        if current_time is not None:
            avg_sizes = compute_average_assembly_size(current_complexes, legend)
            for cond in legend:
                condition_results[cond].append(avg_sizes.get(cond, 0))
            time_series.append(current_time)

        if time_series:
            df = pd.DataFrame({"Time (s)": time_series, **condition_results})
            all_sim_data.append(df)

    if not all_sim_data:
        print("No valid simulation data found.")
        return

    # Align data to the shortest time series
    min_length = min(len(df) for df in all_sim_data)
    all_sim_data = [df.iloc[:min_length] for df in all_sim_data]

    time_values = all_sim_data[0]["Time (s)"].values
    avg_data = {cond: np.array([df[cond].values for df in all_sim_data]) for cond in legend}

    # Compute mean and standard deviation
    mean_values = {cond: data.mean(axis=0) for cond, data in avg_data.items()}
    std_values = {cond: data.std(axis=0) for cond, data in avg_data.items()}

    # Save processed data
    save_path = os.path.join(plot_data_dir, "average_assembly_size_vs_time.csv")
    df_to_save = pd.DataFrame({"Time (s)": time_values, **{f"Mean {cond}": mean_values[cond] for cond in legend},
                               **{f"Std {cond}": std_values[cond] for cond in legend}})
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")

    # Plot the data
    plt.figure(figsize=figure_size)
    sns.set_style("ticks")

    for cond in legend:
        if show_type in {"individuals", "both"}:
            for i, sim_values in enumerate(avg_data[cond]):
                plt.plot(time_values, sim_values, alpha=0.3, linestyle="dashed",
                         label=f"Individual run {i} ({cond})" if show_type == "both" else None)

        if show_type in {"average", "both"}:
            plt.plot(time_values, mean_values[cond], label=f"Average ({cond})", linewidth=2)
            plt.fill_between(time_values, mean_values[cond] - std_values[cond], mean_values[cond] + std_values[cond], alpha=0.2)

    plt.xlabel("Time (s)")
    plt.ylabel("Average Assembly Size")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "average_assembly_size_vs_time.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()

    print(f"Plot saved to {plot_path}")

def plot_line_fraction_of_monomers_assembled_vs_time(
    save_dir: str,
    simulations_index: list,
    legend: list,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    Plot the fraction of monomers assembled in complex vs. time based on species composition in complexes.
    
    Parameters:
        save_dir (str): The base directory where simulations are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Conditions for computing assembly fractions (e.g., ["A>=2"]).
        show_type (str): Display mode, "both", "individuals", or "average".
        simulations_dir (list): List of simulation directories.
        figure_size (tuple): Size of the figure.
    """
    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)
    
    all_sim_data = []
    
    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")
        
        if not os.path.exists(data_file):
            print(f"Warning: {data_file} not found, skipping simulation {idx}.")
            continue
        
        time_series = []
        fraction_results = {condition: [] for condition in legend}
        
        with open(data_file, "r") as f:
            lines = f.readlines()
        
        current_time = None
        current_complexes = []
        
        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                if current_time is not None:
                    for cond in legend:
                        selected_counts = 0
                        total_counts = 0

                        for count, complex_dict in current_complexes:
                            matches, target_species = eval_condition(complex_dict, cond)

                            if matches:
                                selected_counts += count * complex_dict.get(target_species, 0)  # Sum only the target species count

                            if target_species in complex_dict:
                                total_counts += count * complex_dict[target_species]  # Sum only in complexes where species exists

                        fraction = selected_counts / total_counts if total_counts > 0 else 0
                        fraction_results[cond].append(fraction)

                    time_series.append(current_time)
                    current_complexes = []

                current_time = float(time_match.group(1))
            else:
                count, species_dict = parse_complex_line(line)
                if species_dict:
                    current_complexes.append((count, species_dict))

        if current_time is not None:
            for cond in legend:
                selected_counts = 0
                total_counts = 0

                for count, complex_dict in current_complexes:
                    matches, target_species = eval_condition(complex_dict, cond)

                    if matches:
                        selected_counts += count * complex_dict.get(target_species, 0)  # Sum only the target species count

                    if target_species in complex_dict:
                        total_counts += count * complex_dict[target_species]  # Sum only in complexes where species exists

                fraction = selected_counts / total_counts if total_counts > 0 else 0
                fraction_results[cond].append(fraction)

            time_series.append(current_time)

        if time_series:
            df = pd.DataFrame({"Time (s)": time_series, **fraction_results})
            all_sim_data.append(df)
    
    if not all_sim_data:
        print("No valid simulation data found.")
        return
    
    min_length = min(len(df) for df in all_sim_data)
    all_sim_data = [df.iloc[:min_length] for df in all_sim_data]
    
    time_values = all_sim_data[0]["Time (s)"].values
    fraction_data = {cond: np.array([df[cond].values for df in all_sim_data]) for cond in legend}
    
    mean_values = {cond: data.mean(axis=0) for cond, data in fraction_data.items()}
    std_values = {cond: data.std(axis=0) for cond, data in fraction_data.items()}
    
    save_path = os.path.join(plot_data_dir, "fraction_of_monomers_assembled_vs_time.csv")
    df_to_save = pd.DataFrame({"Time (s)": time_values, **{f"Mean {cond}": mean_values[cond] for cond in legend},
                               **{f"Std {cond}": std_values[cond] for cond in legend}})
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")
    
    plt.figure(figsize=figure_size)
    sns.set_style("ticks")
    
    for cond in legend:
        if show_type in {"individuals", "both"}:
            for i, sim_values in enumerate(fraction_data[cond]):
                plt.plot(time_values, sim_values, alpha=0.3, linestyle="dashed",
                         label=f"Individual run {i} ({cond})" if show_type == "both" else None)
        
        if show_type in {"average", "both"}:
            plt.plot(time_values, mean_values[cond], label=f"Average ({cond})", linewidth=2)
            plt.fill_between(time_values, mean_values[cond] - std_values[cond], mean_values[cond] + std_values[cond], alpha=0.2)
    
    plt.xlabel("Time (s)")
    plt.ylabel("Fraction of Monomers Assembled")
    plt.legend()
    plt.tight_layout()
    
    plot_path = os.path.join(plot_data_dir, "fraction_of_monomers_assembled_vs_time.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()
    
    print(f"Plot saved to {plot_path}")

def eval_condition(species_dict, condition):
    """
    Evaluates whether a complex meets a condition based on species count.
    
    Parameters:
        species_dict (dict): Dictionary containing species counts in one complex.
        condition (str): A condition string like "B>=3".
    
    Returns:
        bool: True if the complex satisfies the condition, otherwise False.
    """
    species_match = re.match(r"(\w+)([>=<]=?|==)(\d+)", condition)
    if not species_match:
        return False

    species, operator, threshold = species_match.groups()
    threshold = int(threshold)
    
    species_count = species_dict.get(species, 0)  # Get count for the species
    return eval(f"{species_count} {operator} {threshold}"), species

def plot_hist_complex_species_size(
    save_dir: str,
    simulations_index: list,
    legend: list,
    bins: int = 10,
    time_frame: tuple = None,
    frequency: bool = False,
    normalize: bool = False,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    Plot a histogram of the average number or frequency of different complex species sizes over a time frame.
    The X-axis represents complex species size (only considering species in the legend), and the Y-axis 
    represents the average count or frequency, optionally normalized.

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Species to be counted in determining complex sizes.
        bins (int): Number of bins for the histogram.
        time_frame (tuple, optional): Time range (start, end) to consider for averaging.
        frequency (bool): Whether to plot frequency instead of absolute count.
        normalize (bool): Whether to normalize the histogram (ensuring total area = 1).
        show_type (str): Display mode - "both", "individuals", or "average".
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)
    
    all_sizes_per_sim = []
    all_sizes_combined = []

    # Step 1: Collect all sizes across simulations
    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")
        
        if not os.path.exists(data_file):
            print(f"Warning: {data_file} not found, skipping simulation {idx}.")
            continue
        
        with open(data_file, "r") as f:
            lines = f.readlines()
        
        current_time = None
        sim_sizes = []

        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                current_time = float(time_match.group(1))
                if time_frame and (current_time <= time_frame[0] or current_time >= time_frame[1]):
                    continue
            else:
                count, species_dict = parse_complex_line(line)
                if species_dict:
                    complex_size = sum(species_dict[species] for species in legend if species in species_dict)
                    sim_sizes.extend([complex_size] * count)

        if sim_sizes:
            all_sizes_per_sim.append(sim_sizes)
            all_sizes_combined.extend(sim_sizes)  # Accumulate sizes for global binning

    if not all_sizes_per_sim:
        print("No valid simulation data found.")
        return
    
    # Step 2: Determine global bin edges
    global_hist, bin_edges = np.histogram(all_sizes_combined, bins=bins)  # Global bin edges
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]

    # print out bin edges and bin centers for debugging
    print(f"Bin edges: {bin_edges}")
    print(f"Bin centers: {bin_centers}")
    
    # Step 3: Compute histograms for each simulation using the same bin edges
    hist_values_all = []

    for sizes in all_sizes_per_sim:
        hist_values, _ = np.histogram(sizes, bins=bin_edges)  # Use fixed bin_edges
        hist_values_all.append(hist_values)

    hist_values_all = np.array(hist_values_all)

    # Step 4: Compute mean and standard deviation
    mean_values = np.mean(hist_values_all, axis=0)
    std_values = np.std(hist_values_all, axis=0)

    total = np.sum(mean_values)
    
    if frequency and total > 0:
        mean_values = mean_values / total
        std_values = std_values / total
    
    if normalize and total > 0:
        mean_values = mean_values / bin_width
        std_values = std_values / bin_width

    # Save data
    df_to_save = pd.DataFrame({
        "Bin Center": bin_centers,
        "Mean Count": mean_values,
        "Std Dev": std_values
    })
    save_path = os.path.join(plot_data_dir, "hist_average_number_vs_size.csv")
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")

    # Step 5: Plot with error bars
    plt.figure(figsize=figure_size)
    plt.bar(bin_centers, mean_values, width=bin_width * 0.9, alpha=0.7, label="Mean")
    plt.errorbar(bin_centers, mean_values, yerr=std_values, fmt='o', color='black', capsize=5, label="Std Dev")

    species_all = "+".join(legend)
    plt.xlabel(f"Number of {species_all} in Complexes")
    plt.ylabel("Normalized Frequency" if normalize else ("Frequency" if frequency else "Complex Count"))
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "hist_average_number_vs_size.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()
    
    print(f"Plot saved to {plot_path}")

def plot_hist_monomer_counts_vs_complex_size(
    save_dir: str,
    simulations_index: list,
    legend: list,
    bins: int = 10,
    time_frame: tuple = None,
    frequency: bool = False,
    normalize: bool = False,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6),
):
    """
    Plot a histogram of the total number of monomers as a function of complex size over a time frame.

    The X-axis represents complex species size (only considering species in the legend), 
    and the Y-axis represents the total number of monomers found in those complexes.

    Parameters:
        save_dir (str): Directory to save output plots.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Species to be counted in determining complex sizes.
        bins (int): Number of bins for the histogram.
        time_frame (tuple, optional): Time range (start, end) to consider for averaging.
        frequency (bool): Whether to plot frequency instead of absolute count.
        normalize (bool): Whether to normalize the histogram.
        show_type (str): Display mode - "both", "individuals", or "average".
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)
    
    all_sizes_per_sim = []
    all_sizes_combined = []

    # Step 1: Collect data from simulations
    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")
        
        if not os.path.exists(data_file):
            print(f"Warning: {data_file} not found, skipping simulation {idx}.")
            continue
        
        with open(data_file, "r") as f:
            lines = f.readlines()
        
        current_time = None
        sim_sizes = []

        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                current_time = float(time_match.group(1))
                if time_frame and (current_time <= time_frame[0] or current_time >= time_frame[1]):
                    continue
            else:
                count, species_dict = parse_complex_line(line)
                if species_dict:
                    complex_size = sum(species_dict[species] for species in legend if species in species_dict)
                    sim_sizes.extend([complex_size] * count)  # Repeat complex size `count` times

        if sim_sizes:
            all_sizes_per_sim.append(sim_sizes)
            all_sizes_combined.extend(sim_sizes)

    if not all_sizes_per_sim:
        print("No valid simulation data found.")
        return
    
    # Step 2: Determine global bin edges
    _, bin_edges = np.histogram(all_sizes_combined, bins=bins)  # Compute fixed bin edges
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]

    # Step 3: Compute histograms for monomer counts using the same bin edges
    monomer_values_all = []

    for sizes in all_sizes_per_sim:
        monomer_values, _ = np.histogram(sizes, bins=bin_edges, weights=sizes)  # Weight = complex size
        monomer_values_all.append(monomer_values)

    monomer_values_all = np.array(monomer_values_all)

    # Step 4: Compute mean and standard deviation
    mean_values = np.mean(monomer_values_all, axis=0)
    std_values = np.std(monomer_values_all, axis=0)

    total = np.sum(mean_values)
    
    if frequency and total > 0:
        mean_values = mean_values / total
        std_values = std_values / total
    
    if normalize and total > 0:
        mean_values = mean_values / bin_width
        std_values = std_values / bin_width

    # Save data
    df_to_save = pd.DataFrame({
        "Bin Center": bin_centers,
        "Mean Monomer Count": mean_values,
        "Std Dev": std_values
    })
    save_path = os.path.join(plot_data_dir, "hist_monomer_count_vs_size.csv")
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")

    # Step 5: Plot with error bars
    plt.figure(figsize=figure_size)
    plt.bar(bin_centers, mean_values, width=bin_width * 0.9, alpha=0.7, label="Mean")
    plt.errorbar(bin_centers, mean_values, yerr=std_values, fmt='o', color='black', capsize=5, label="Std Dev")

    species_all = "+".join(legend)
    plt.xlabel(f"Number of {species_all} in Complexes")
    plt.ylabel("Normalized Frequency" if normalize else ("Frequency" if frequency else "Total Monomers in Complexes"))
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "hist_monomer_count_vs_size.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()
    
    print(f"Plot saved to {plot_path}")

def get_time_bins(all_times, time_bins):
    min_t, max_t = min(all_times), max(all_times)
    return np.linspace(min_t, max_t, time_bins + 1)

def plot_hist_complex_species_size_3d(
    save_dir: str,
    simulations_index: list,
    legend: list,
    bins: int = 10,
    time_bins: int = 10,
    frequency: bool = False,
    normalize: bool = False,
    simulations_dir: list = None,
    figure_size: tuple = (10, 8)
):
    """
    Plot a 3D histogram of complex species size over time.

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Species to be counted in determining complex sizes.
        bins (int): Number of bins for the histogram.
        time_bins (int): Number of time bins for the histogram.
        frequency (bool): Whether to plot frequency instead of absolute count.
        normalize (bool): Whether to normalize the histogram.
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    os.makedirs(os.path.join(save_dir, "figure_plot_data"), exist_ok=True)
    all_data = []

    # First pass to collect all sizes and times
    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")
        if not os.path.exists(data_file):
            continue
        
        with open(data_file, "r") as f:
            lines = f.readlines()

        current_time, sim_data = None, []
        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                current_time = float(time_match.group(1))
            else:
                count, species_dict = parse_complex_line(line)
                if species_dict:
                    size = sum(species_dict[s] for s in legend if s in species_dict)
                    sim_data.extend([(current_time, size)] * count)
        all_data.extend(sim_data)

    if not all_data:
        print("No valid data found.")
        return

    # Organize into time bins
    times, sizes = zip(*all_data)
    time_edges = np.linspace(min(times), max(times), time_bins + 1)
    size_edges = np.histogram_bin_edges(sizes, bins=bins)
    size_centers = (size_edges[:-1] + size_edges[1:]) / 2
    time_centers = (time_edges[:-1] + time_edges[1:]) / 2

    print(f"Time edges: {time_edges}")
    print(f"Time centers: {time_centers}")
    print(f"Size edges: {size_edges}")
    print(f"Size centers: {size_centers}")

    # Prepare 2D histogram: rows=time bins, cols=size bins
    hist2d = np.zeros((time_bins, bins))
    for t, s in all_data:
        t_idx = min(np.searchsorted(time_edges, t, side='right') - 1, time_bins - 1)
        s_idx = min(np.searchsorted(size_edges, s, side='right') - 1, bins - 1)
        if 0 <= t_idx < time_bins and 0 <= s_idx < bins:
            hist2d[t_idx, s_idx] += 1

    hist2d /= len(simulations_index)

    if frequency:
        hist2d = hist2d / hist2d.sum(axis=1, keepdims=True)
    if normalize:
        bin_width = size_edges[1] - size_edges[0]
        hist2d = hist2d / bin_width

    # 3D bar plot
    fig = plt.figure(figsize=figure_size)
    ax = fig.add_subplot(111, projection='3d')

    xpos, ypos = np.meshgrid(size_centers, time_centers)
    xpos = xpos.flatten()
    ypos = ypos.flatten()
    zpos = np.zeros_like(xpos)
    dx = (size_edges[1] - size_edges[0]) * 0.9
    dy = (time_edges[1] - time_edges[0]) * 0.9
    dz = hist2d.flatten()

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, shade=True)
    ax.set_xlabel("Complex Size")
    ax.set_ylabel("Time (s)")
    ax.set_zlabel("Normalized Frequency" if normalize else ("Frequency" if frequency else "Complex Count"))
    plt.tight_layout()

    plot_path = os.path.join(save_dir, "figure_plot_data", "3D_hist_complex_species.svg")
    plt.savefig(plot_path)
    plt.show()
    print(f"3D plot saved to {plot_path}")
    # save the data for further analysis
    hist_data = pd.DataFrame(hist2d, index=time_centers, columns=size_centers)
    hist_data.to_csv(os.path.join(save_dir, "figure_plot_data", "hist_complex_species_size_3d.csv"))
    print(f"Histogram data saved to {os.path.join(save_dir, 'figure_plot_data', 'hist_complex_species_size_3d.csv')}")

def plot_hist_monomer_counts_vs_complex_size_3d(
    save_dir: str,
    simulations_index: list,
    legend: list,
    bins: int = 10,
    time_bins: int = 10,
    frequency: bool = False,
    normalize: bool = False,
    simulations_dir: list = None,
    figure_size: tuple = (10, 8)
):
    """
    Plot a 3D histogram of the total number of monomers as a function of complex size over time.
    The X-axis represents complex species size (only considering species in the legend),
    the Y-axis represents time intervals (in seconds),
    and the Z-axis represents the total number of monomers found in those complexes.

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Species to be counted in determining complex sizes.
        bins (int): Number of bins for the histogram.
        time_bins (int): Number of time bins for the histogram.
        frequency (bool): Whether to plot frequency instead of absolute count.
        normalize (bool): Whether to normalize the histogram.
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    os.makedirs(os.path.join(save_dir, "figure_plot_data"), exist_ok=True)
    all_data = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")
        if not os.path.exists(data_file):
            continue

        with open(data_file, "r") as f:
            lines = f.readlines()

        current_time, sim_data = None, []
        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                current_time = float(time_match.group(1))
            else:
                count, species_dict = parse_complex_line(line)
                if species_dict:
                    size = sum(species_dict[s] for s in legend if s in species_dict)
                    sim_data.append((current_time, size, count * size))  # weight = count × size
        all_data.extend(sim_data)

    if not all_data:
        print("No valid data found.")
        return

    times, sizes, weights = zip(*all_data)
    time_edges = np.linspace(min(times), max(times), time_bins + 1)
    size_edges = np.histogram_bin_edges(sizes, bins=bins)
    size_centers = (size_edges[:-1] + size_edges[1:]) / 2
    time_centers = (time_edges[:-1] + time_edges[1:]) / 2

    print(f"Time edges: {time_edges}")
    print(f"Time centers: {time_centers}")
    print(f"Size edges: {size_edges}")
    print(f"Size centers: {size_centers}")

    hist2d = np.zeros((time_bins, bins))
    for t, s, w in all_data:
        t_idx = min(np.searchsorted(time_edges, t, side='right') - 1, time_bins - 1)
        s_idx = min(np.searchsorted(size_edges, s, side='right') - 1, bins - 1)
        if 0 <= t_idx < time_bins and 0 <= s_idx < bins:
            hist2d[t_idx, s_idx] += w

    hist2d /= len(simulations_index)

    if frequency:
        hist2d = hist2d / hist2d.sum(axis=1, keepdims=True)
    if normalize:
        bin_width = size_edges[1] - size_edges[0]
        hist2d = hist2d / bin_width

    # 3D bar plot
    fig = plt.figure(figsize=figure_size)
    ax = fig.add_subplot(111, projection='3d')

    xpos, ypos = np.meshgrid(size_centers, time_centers)
    xpos = xpos.flatten()
    ypos = ypos.flatten()
    zpos = np.zeros_like(xpos)
    dx = (size_edges[1] - size_edges[0]) * 0.9
    dy = (time_edges[1] - time_edges[0]) * 0.9
    dz = hist2d.flatten()

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, shade=True)
    ax.set_xlabel("Complex Size")
    ax.set_ylabel("Time (s)")
    ax.set_zlabel("Monomer Count" if not frequency else "Frequency")
    plt.tight_layout()

    plot_path = os.path.join(save_dir, "figure_plot_data", "3D_hist_monomer_species.svg")
    plt.savefig(plot_path)
    plt.show()
    print(f"3D plot saved to {plot_path}")

    # Save the data for further analysis
    hist_data = pd.DataFrame(hist2d, index=time_centers, columns=size_centers)
    hist_data.to_csv(os.path.join(save_dir, "figure_plot_data", "hist_monomer_count_vs_size_3d.csv"))
    print(f"Histogram data saved to {os.path.join(save_dir, 'figure_plot_data', 'hist_monomer_count_vs_size_3d.csv')}")

def format_sig(x, sig=3):
    return f"{x:.{sig}g}"

def plot_heatmap_complex_species_size(
    save_dir: str,
    simulations_index: list,
    legend: list,
    bins: int = 10,
    time_bins: int = 10,
    frequency: bool = False,
    normalize: bool = False,
    simulations_dir: list = None,
    figure_size: tuple = (10, 8)
):
    """
    Plot a 2D heatmap of the average number of different complex species sizes over time.
    The X-axis represents complex species size (only considering species in the legend),
    the Y-axis represents time intervals (in seconds),
    and the color in each box indicates the average number of corresponding complexes at each time interval.

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Species to be counted in determining complex sizes.
        bins (int): Number of bins for the histogram.
        time_bins (int): Number of time bins for the histogram.
        frequency (bool): Whether to plot frequency instead of absolute count.
        normalize (bool): Whether to normalize the histogram.
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    os.makedirs(os.path.join(save_dir, "figure_plot_data"), exist_ok=True)
    all_data = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")
        if not os.path.exists(data_file):
            continue

        with open(data_file, "r") as f:
            lines = f.readlines()

        current_time = None
        sim_data = []
        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                current_time = float(time_match.group(1))
            else:
                count, species_dict = parse_complex_line(line)
                if species_dict:
                    size = sum(species_dict[s] for s in legend if s in species_dict)
                    sim_data.extend([(current_time, size)] * count)
        all_data.extend(sim_data)

    if not all_data:
        print("No valid data found.")
        return

    times, sizes = zip(*all_data)
    time_edges = np.linspace(min(times), max(times), time_bins + 1)
    size_edges = np.histogram_bin_edges(sizes, bins=bins)

    hist2d, _, _ = np.histogram2d(times, sizes, bins=[time_edges, size_edges])
    hist2d /= len(simulations_index)

    if frequency:
        hist2d = hist2d / hist2d.sum(axis=1, keepdims=True)
    if normalize:
        bin_width = size_edges[1] - size_edges[0]
        hist2d = hist2d / bin_width

    df = pd.DataFrame(hist2d, index=(time_edges[:-1] + time_edges[1:]) / 2,
                      columns=(size_edges[:-1] + size_edges[1:]) / 2)

    save_path = os.path.join(save_dir, "figure_plot_data", "heatmap_complex_species_size.csv")
    df.to_csv(save_path)
    print(f"Heatmap data saved to {save_path}")

    plt.figure(figsize=figure_size)
    heatmap = sns.heatmap(df, cmap="viridis", cbar_kws={"label": "Normalized Frequency" if normalize else ("Frequency" if frequency else "Complex Count")})
    plt.xlabel("Complex Size")
    plt.ylabel("Time (s)")
    heatmap.set_xticklabels([format_sig(x, 3) for x in df.columns])
    heatmap.set_yticklabels([format_sig(y, 3) for y in df.index])
    plt.tight_layout()

    plot_path = os.path.join(save_dir, "figure_plot_data", "heatmap_complex_species_size.svg")
    plt.savefig(plot_path)
    plt.show()
    print(f"Heatmap plot saved to {plot_path}")

def plot_heatmap_monomer_counts_vs_complex_size(
    save_dir: str,
    simulations_index: list,
    legend: list,
    bins: int = 10,
    time_bins: int = 10,
    frequency: bool = False,
    normalize: bool = False,
    simulations_dir: list = None,
    figure_size: tuple = (10, 8)
):
    """
    Plot a 2D heatmap of the average number of monomers as a function of complex size over time.
    The X-axis represents complex species size (only considering species in the legend),
    the Y-axis represents time intervals (in seconds),
    and the color in each box indicates the average number of monomers found in those complexes.

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Species to be counted in determining complex sizes.
        bins (int): Number of bins for the histogram.
        time_bins (int): Number of time bins for the histogram.
        frequency (bool): Whether to plot frequency instead of absolute count.
        normalize (bool): Whether to normalize the histogram.
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    os.makedirs(os.path.join(save_dir, "figure_plot_data"), exist_ok=True)
    all_data = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")
        if not os.path.exists(data_file):
            continue

        with open(data_file, "r") as f:
            lines = f.readlines()

        current_time = None
        sim_data = []
        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                current_time = float(time_match.group(1))
            else:
                count, species_dict = parse_complex_line(line)
                if species_dict:
                    size = sum(species_dict[s] for s in legend if s in species_dict)
                    sim_data.append((current_time, size, count * size))
        all_data.extend(sim_data)

    if not all_data:
        print("No valid data found.")
        return

    times, sizes, weights = zip(*all_data)
    time_edges = np.linspace(min(times), max(times), time_bins + 1)
    size_edges = np.histogram_bin_edges(sizes, bins=bins)

    hist2d, _, _ = np.histogram2d(times, sizes, bins=[time_edges, size_edges], weights=weights)
    hist2d /= len(simulations_index)

    if frequency:
        hist2d = hist2d / hist2d.sum(axis=1, keepdims=True)
    if normalize:
        bin_width = size_edges[1] - size_edges[0]
        hist2d = hist2d / bin_width

    df = pd.DataFrame(hist2d, index=(time_edges[:-1] + time_edges[1:]) / 2,
                      columns=(size_edges[:-1] + size_edges[1:]) / 2)

    save_path = os.path.join(save_dir, "figure_plot_data", "heatmap_monomer_counts_vs_complex_size.csv")
    df.to_csv(save_path)
    print(f"Heatmap data saved to {save_path}")

    plt.figure(figsize=figure_size)
    heatmap = sns.heatmap(df, cmap="viridis", cbar_kws={"label": "Normalized Frequency" if normalize else ("Frequency" if frequency else "Monomer Count")})
    plt.xlabel("Complex Size")
    plt.ylabel("Time (s)")
    heatmap.set_xticklabels([format_sig(x, 3) for x in df.columns])
    heatmap.set_yticklabels([format_sig(y, 3) for y in df.index])
    plt.tight_layout()

    plot_path = os.path.join(save_dir, "figure_plot_data", "heatmap_monomer_counts_vs_complex_size.svg")
    plt.savefig(plot_path)
    plt.show()
    print(f"Heatmap plot saved to {plot_path}")

def plot_heatmap_species_a_vs_species_b(
    save_dir: str,
    simulations_index: list,
    legend: list,
    bins: int = 10,
    time_bins: int = 10,
    frequency: bool = False,
    normalize: bool = False,
    simulations_dir: list = None,
    figure_size: tuple = (10, 8)
):
    """
    Plot a 2D heatmap of the average number of two selected species (species_a and species_b) in complexes over time.
    The X-axis represents the number of species_a, the Y-axis represents the number of species_b,
    and the color in each box indicates the average number of complexes containing those species.

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Species to be counted in determining complex sizes, e.g., ["A", "B"].
        bins (int): Number of bins for the histogram.
        time_bins (int): Number of time bins for the histogram.
        frequency (bool): Whether to plot frequency instead of absolute count.
        normalize (bool): Whether to normalize the histogram.
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    os.makedirs(os.path.join(save_dir, "figure_plot_data"), exist_ok=True)
    species_x, species_y = legend[0], legend[1]
    all_data = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")
        if not os.path.exists(data_file):
            continue

        with open(data_file, "r") as f:
            lines = f.readlines()

        current_time = None
        sim_data = []
        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                current_time = float(time_match.group(1))
            else:
                count, species_dict = parse_complex_line(line)
                if species_dict:
                    x = species_dict.get(species_x, 0)
                    y = species_dict.get(species_y, 0)
                    sim_data.extend([(x, y)] * count)
        all_data.extend(sim_data)

    if not all_data:
        print("No valid data found.")
        return

    x_vals, y_vals = zip(*all_data)
    heatmap, xedges, yedges = np.histogram2d(x_vals, y_vals, bins=bins)
    heatmap /= len(simulations_index)

    print(f"X edges: {xedges}")
    print(f"Y edges: {yedges}")

    if frequency:
        heatmap = heatmap / heatmap.sum()
    if normalize:
        bin_area = (xedges[1] - xedges[0]) * (yedges[1] - yedges[0])
        heatmap = heatmap / bin_area

    df = pd.DataFrame(heatmap, index=(xedges[:-1] + xedges[1:]) / 2,
                      columns=(yedges[:-1] + yedges[1:]) / 2)
    save_path = os.path.join(save_dir, "figure_plot_data", "heatmap_species_a_vs_b.csv")
    df.to_csv(save_path)
    print(f"Heatmap data saved to {save_path}")

    plt.figure(figsize=figure_size)
    heatmap = sns.heatmap(df, cmap="viridis", cbar_kws={"label": "Normalized Frequency" if normalize else ("Frequency" if frequency else "Complex Count")})
    plt.xlabel(species_y)
    plt.ylabel(species_x)
    heatmap.set_xticklabels([format_sig(x, 3) for x in df.columns])
    heatmap.set_yticklabels([format_sig(y, 3) for y in df.index])
    plt.tight_layout()

    plot_path = os.path.join(save_dir, "figure_plot_data", "heatmap_species_a_vs_b.svg")
    plt.savefig(plot_path)
    plt.show()
    print(f"Heatmap plot saved to {plot_path}")

def plot_stackedhist_complex_species_size(
    save_dir: str,
    simulations_index: list,
    legend: list,
    bins: int = 10,
    time_frame: tuple = None,
    frequency: bool = False,
    normalize: bool = False,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    Plot a stacked histogram of complex species size over time.
    The X-axis represents complex species size (only considering species in the legend),
    and the Y-axis represents the number of complexes found with that size.
    Each color in the stack represents a different condition (species) from the legend.

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list): Species to be counted in determining complex sizes.
        bins (int): Number of bins for the histogram.
        time_frame (tuple, optional): Time range (start, end) to consider for averaging.
        frequency (bool): Whether to plot frequency instead of absolute count.
        normalize (bool): Whether to normalize the histogram.
        show_type (str): Display mode - "both", "individuals", or "average".
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    os.makedirs(os.path.join(save_dir, "figure_plot_data"), exist_ok=True)
    x_species, y_conditions = legend[0].split(":")
    y_conditions = y_conditions.strip().split(",")
    y_var = re.findall(r"[A-Za-z_]+", y_conditions[0])[0]

    all_histograms = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        data_file = os.path.join(sim_dir, "histogram_complexes_time.dat")
        if not os.path.exists(data_file):
            continue

        with open(data_file, "r") as f:
            lines = f.readlines()

        current_time = None
        # strip any whitespace from y_conditions
        y_conditions = [cond.strip() for cond in y_conditions]
        histogram = {cond: [] for cond in y_conditions}

        for line in lines:
            time_match = re.match(r"Time \(s\): (\d*\.?\d+)", line)
            if time_match:
                current_time = float(time_match.group(1))
            elif time_frame and (current_time is None or current_time < time_frame[0] or current_time > time_frame[1]):
                continue
            else:
                count, species_dict = parse_complex_line(line)
                if species_dict:
                    x = species_dict.get(x_species, 0)
                    y = species_dict.get(y_var, 0)
                    for cond in y_conditions:
                        cond = cond.strip()
                        if any(op in cond for op in ['<', '>', '=', '<=', '>=']):
                            op_index = min(cond.find(op) for op in ['<', '>', '=', '<=', '>='] if op in cond)
                            cond_eval = cond[op_index:]
                            # replace = with == for eval
                            cond_eval = cond_eval.replace('=', '==')
                        # Evaluate the condition
                        if eval(f"{y}{cond_eval}"):
                            histogram[cond].extend([x] * count)
        all_histograms.append(histogram)

    if not all_histograms:
        print("No valid simulation data found.")
        return

    stacked_counts = {cond: np.zeros(bins) for cond in y_conditions}
    all_data = sum((hist[cond] for hist in all_histograms for cond in hist), [])
    bin_edges = np.histogram_bin_edges(all_data, bins=bins)

    for histogram in all_histograms:
        for cond, values in histogram.items():
            hist, _ = np.histogram(values, bins=bin_edges)
            stacked_counts[cond] += hist

    for cond in y_conditions:
        stacked_counts[cond] /= len(all_histograms)

    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bottom = np.zeros_like(bin_centers)

    plt.figure(figsize=figure_size)
    for cond in y_conditions:
        plt.bar(bin_centers, stacked_counts[cond], width=bin_edges[1]-bin_edges[0], bottom=bottom, label=cond)
        bottom += stacked_counts[cond]

    plt.xlabel(f"Number of {x_species} in Complexes")
    plt.ylabel("Complex Count")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(save_dir, "figure_plot_data", "stacked_hist_complex_species_size.svg")
    plt.savefig(plot_path)
    plt.show()
    print(f"Stacked histogram saved to {plot_path}")

    # Save the data for further analysis
    stacked_df = pd.DataFrame(stacked_counts, index=bin_centers)
    stacked_df.to_csv(os.path.join(save_dir, "figure_plot_data", "stacked_hist_complex_species_size.csv"))
    print(f"Stacked histogram data saved to {os.path.join(save_dir, 'figure_plot_data', 'stacked_hist_complex_species_size.csv')}")

def parse_transition_lifetime_data(file_path: str, time_frame: Optional[Tuple[float, float]] = None):
    with open(file_path, "r") as f:
        content = f.read()

    time_blocks = re.split(r"time:\s*", content)[1:]  # Skip the first split which is before the first time entry

    time_data = []

    for block in time_blocks:
        lines = block.strip().splitlines()
        time_val = float(lines[0])
        
        # Parse transition matrix
        tm_start = lines.index("transion matrix for each mol type: ") + 2  # skip the "A" line
        tm_lines = []
        for i in range(tm_start, len(lines)):
            if lines[i].startswith("lifetime for each mol type: "):
                break
            if lines[i].strip():
                tm_lines.append([int(x) for x in lines[i].split()])
        transition_matrix = np.array(tm_lines)

        # Parse lifetimes
        lt_block = lines[i+2:]  # start after "A"
        lifetime = defaultdict(list)
        cluster_size = None
        for line in lt_block:
            if line.startswith("size of the cluster:"):
                cluster_size = int(line.split(":")[1])
            elif cluster_size is not None and line.strip():
                lifetime[cluster_size].extend([float(x) for x in line.strip().split()])

        time_data.append((time_val, transition_matrix, lifetime))

    # Sort by time just in case
    time_data.sort(key=lambda x: x[0])

    if time_frame:
        start, end = time_frame
        # Find the nearest time to 'start' and 'end'
        nearest_start = min(time_data, key=lambda x: abs(x[0] - start))
        nearest_end = min(time_data, key=lambda x: abs(x[0] - end))

        t_start, tm_start, lt_start = nearest_start
        t_end, tm_end, lt_end = nearest_end

        if tm_start is None or tm_end is None:
            raise ValueError("Specified time range not found in data.")

        matrix_delta = tm_end - tm_start

        # Lifetime delta: subtract based on how many entries were already present
        lifetime_delta = defaultdict(list)
        for k in lt_end:
            lt1 = lt_start.get(k, [])
            lt2 = lt_end.get(k, [])
            lifetime_delta[k] = lt2[len(lt1):]  # get only new entries

    else:
        matrix_delta = time_data[-1][1]
        lifetime_delta = time_data[-1][2]

    return matrix_delta, lifetime_delta

def plot_line_free_energy(
    save_dir: str,
    simulations_index: list,
    time_frame: tuple = None,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    Plot the change in free energy over a selected time frame for different sizes of complexes.

    The x-axis represents the size of the complex, and the y-axis represents the free energy in units of KbT, calculated as -ln(p(n)), where p(n) is the probability of the complex size n during the simulation.
    The transition matrix tracks the total counts of transitions between different complex sizes. On the diagonal, it shows the count of complexes that remain the same size in a step; off the diagonal, it shows transitions between different sizes. By summing the numbers per row, we can determine the counts of n-mers across the entire simulation.

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        time_frame (tuple, optional): Time range (start, end) to consider for statistic.
        show_type (str): Display mode - "both", "individuals", or "average".
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)

    all_free_energies = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        file_path = os.path.join(sim_dir, "transition_matrix_time.dat")

        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping simulation {idx}.")
            continue

        matrix_delta, _ = parse_transition_lifetime_data(file_path, time_frame)

        counts_per_size = matrix_delta.sum(axis=1)
        total = counts_per_size.sum()
        probabilities = counts_per_size / total

        with np.errstate(divide='ignore'):
            free_energy = -np.log(probabilities)
            free_energy[np.isinf(free_energy)] = np.nan

        all_free_energies.append(free_energy)

    if not all_free_energies:
        print("No valid simulation data found.")
        return

    min_length = min(len(arr) for arr in all_free_energies)
    all_free_energies = [arr[:min_length] for arr in all_free_energies]

    sizes = np.arange(1, min_length + 1)
    free_energy_array = np.array(all_free_energies)
    avg_free_energy = np.nanmean(free_energy_array, axis=0)
    std_free_energy = np.nanstd(free_energy_array, axis=0)

    df_to_save = pd.DataFrame({
        "Cluster Size": sizes,
        "Mean Free Energy (kBT)": avg_free_energy,
        "Std Free Energy": std_free_energy
    })
    save_path = os.path.join(plot_data_dir, "free_energy_vs_size.csv")
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")

    plt.figure(figsize=figure_size)

    if show_type in {"individuals", "both"}:
        for i, fe in enumerate(free_energy_array):
            plt.plot(sizes, fe, alpha=0.3, linestyle="dashed", label=f"Individual run {i}" if show_type == "both" else None)

    if show_type in {"average", "both"}:
        plt.plot(sizes, avg_free_energy, label="Average", linewidth=2)
        plt.fill_between(sizes, avg_free_energy - std_free_energy, avg_free_energy + std_free_energy, alpha=0.2)

    plt.xlabel("Cluster Size (n)")
    plt.ylabel(r"$\mathrm{Free\ Energy}\ (k_\mathrm{B}T)$")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "free_energy_vs_size.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()
    print(f"Plot saved to {plot_path}")

def plot_line_symmetric_association_probability(
    save_dir: str,
    simulations_index: list,
    legend: list = None,
    time_frame: tuple = None,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    This line plot represents the probability of association between complexes of different sizes.
    Each event is counted symmetrically from both participating sizes.
    
    legend examples: ["associate size > n", "associate size = n", "associate size < n"]

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list, optional): Custom legend labels for the plot.
        time_frame (tuple, optional): Time range (start, end) to consider for statistic.
        show_type (str): Display mode - "both", "individuals", or "average".
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    conds = []
    if legend is None:
        legend = ["associate size > 2", "associate size = 2", "associate size < 2"]
        conds = [">2", "==2", "<2"]
    else:
        for l in legend:
            if not l.startswith("associate size"):
                raise ValueError(f"Legend '{l}' must start with 'associate size'.")
            cond = l.replace("associate size", "").strip()
            if not any(op in cond for op in [">=", "<=", "==", "!=", ">", "<", "="]):
                raise ValueError(f"Legend condition '{cond}' must contain a valid comparison operator.")
            cond = cond.replace("=", "==") if "=" in cond and "==" not in cond else cond
            conds.append(cond)

    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)

    all_assoc_probs = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        file_path = os.path.join(sim_dir, "transition_matrix_time.dat")

        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping simulation {idx}.")
            continue

        matrix_delta, _ = parse_transition_lifetime_data(file_path, time_frame)
        max_size = matrix_delta.shape[0]

        assoc_probs = [[] for _ in conds]

        for n in range(max_size - 1):
            assoc_counts = []
            for m in range(n + 1, max_size):
                pair_size = m - n
                count = matrix_delta[m, n]
                if pair_size == n + 1:
                    count /= 2
                assoc_counts.append((pair_size, count))

            total_assoc = sum(c for _, c in assoc_counts)
            for j, cond in enumerate(conds):
                selected = [c for s, c in assoc_counts if eval(f"{s}{cond}")]
                assoc_probs[j].append(sum(selected) / total_assoc if total_assoc > 0 else np.nan)

        all_assoc_probs.append(np.array(assoc_probs))

    if not all_assoc_probs:
        print("No valid simulation data found.")
        return

    min_length = min(prob.shape[1] for prob in all_assoc_probs)
    all_assoc_probs = [prob[:, :min_length] for prob in all_assoc_probs]

    cluster_sizes = np.arange(1, min_length + 1)
    prob_array = np.array(all_assoc_probs)

    avg_probs = np.nanmean(prob_array, axis=0)
    std_probs = np.nanstd(prob_array, axis=0)

    df_to_save = {"Cluster Size": cluster_sizes}
    for i, label in enumerate(legend):
        df_to_save[f"{label} (avg)"] = avg_probs[i]
        df_to_save[f"{label} (std)"] = std_probs[i]
    df_to_save = pd.DataFrame(df_to_save)

    save_path = os.path.join(plot_data_dir, "symmetric_association_probability.csv")
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")

    plt.figure(figsize=figure_size)

    if show_type in {"individuals", "both"}:
        for sim_idx, sim_probs in enumerate(prob_array):
            for i, label in enumerate(legend):
                plt.plot(cluster_sizes, sim_probs[i], linestyle="dashed", alpha=0.3, label=f"{label} (run {sim_idx})" if show_type == "both" else None)

    if show_type in {"average", "both"}:
        for i, label in enumerate(legend):
            plt.plot(cluster_sizes, avg_probs[i], label=f"{label} (avg)", linewidth=2)
            plt.fill_between(cluster_sizes, avg_probs[i] - std_probs[i], avg_probs[i] + std_probs[i], alpha=0.2)

    plt.xlabel("Cluster Size (n)")
    plt.ylabel("Association Probability")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "symmetric_association_probability.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()
    print(f"Plot saved to {plot_path}")

def plot_line_asymmetric_association_probability(
    save_dir: str,
    simulations_index: list,
    legend: list = None,
    time_frame: tuple = None,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    This line plot represents the probability of association between complexes of different sizes.
    Each event is counted asymmetrically from the larger participating size.
    
    legend examples: ["associate size > n", "associate size = n", "associate size < n"]

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list, optional): Custom legend labels for the plot.
        time_frame (tuple, optional): Time range (start, end) to consider for statistic.
        show_type (str): Display mode - "both", "individuals", or "average".
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    conds = []
    if legend is None:
        legend = ["associate size > 2", "associate size = 2", "associate size < 2"]
        conds = [">2", "==2", "<2"]
    else:
        for l in legend:
            if not l.startswith("associate size"):
                raise ValueError(f"Legend '{l}' must start with 'associate size'.")
            cond = l.replace("associate size", "").strip()
            if not any(op in cond for op in [">=", "<=", "==", "!=", ">", "<", "="]):
                raise ValueError(f"Legend condition '{cond}' must contain a valid comparison operator.")
            cond = cond.replace("=", "==") if "=" in cond and "==" not in cond else cond
            conds.append(cond)

    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)

    all_assoc_probs = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        file_path = os.path.join(sim_dir, "transition_matrix_time.dat")

        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping simulation {idx}.")
            continue

        matrix_delta, _ = parse_transition_lifetime_data(file_path, time_frame)
        max_size = matrix_delta.shape[0]

        assoc_probs = [[] for _ in conds]

        for n in range(max_size - 1):
            assoc_counts = []
            for m in range(n + 1, max_size):
                pair_size = m - n
                count = matrix_delta[m, n]
                if pair_size == n + 1:
                    count /= 2
                if pair_size > n + 1:
                    break
                assoc_counts.append((pair_size, count))

            total_assoc = sum(c for _, c in assoc_counts)
            for j, cond in enumerate(conds):
                selected = [c for s, c in assoc_counts if eval(f"{s}{cond}")]
                assoc_probs[j].append(sum(selected) / total_assoc if total_assoc > 0 else np.nan)

        all_assoc_probs.append(np.array(assoc_probs))

    if not all_assoc_probs:
        print("No valid simulation data found.")
        return

    min_length = min(prob.shape[1] for prob in all_assoc_probs)
    all_assoc_probs = [prob[:, :min_length] for prob in all_assoc_probs]

    cluster_sizes = np.arange(1, min_length + 1)
    prob_array = np.array(all_assoc_probs)

    avg_probs = np.nanmean(prob_array, axis=0)
    std_probs = np.nanstd(prob_array, axis=0)

    df_to_save = {"Cluster Size": cluster_sizes}
    for i, label in enumerate(legend):
        df_to_save[f"{label} (avg)"] = avg_probs[i]
        df_to_save[f"{label} (std)"] = std_probs[i]
    df_to_save = pd.DataFrame(df_to_save)

    save_path = os.path.join(plot_data_dir, "asymmetric_association_probability.csv")
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")

    plt.figure(figsize=figure_size)

    if show_type in {"individuals", "both"}:
        for sim_idx, sim_probs in enumerate(prob_array):
            for i, label in enumerate(legend):
                plt.plot(cluster_sizes, sim_probs[i], linestyle="dashed", alpha=0.3, label=f"{label} (run {sim_idx})" if show_type == "both" else None)

    if show_type in {"average", "both"}:
        for i, label in enumerate(legend):
            plt.plot(cluster_sizes, avg_probs[i], label=f"{label} (avg)", linewidth=2)
            plt.fill_between(cluster_sizes, avg_probs[i] - std_probs[i], avg_probs[i] + std_probs[i], alpha=0.2)

    plt.xlabel("Cluster Size (n)")
    plt.ylabel("Association Probability")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "asymmetric_association_probability.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()
    print(f"Plot saved to {plot_path}")

def plot_line_symmetric_dissociation_probability(
    save_dir: str,
    simulations_index: list,
    legend: list = None,
    time_frame: tuple = None,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    This line plot represents the probability of dissociation between complexes of different sizes.
    Each event is counted symmetrically for both generated sizes.
    
    legend examples: ["dissociate size > n", "dissociate size = n", "dissociate size < n"]

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list, optional): Custom legend labels for the plot.
        time_frame (tuple, optional): Time range (start, end) to consider for statistic.
        show_type (str): Display mode - "both", "individuals", or "average".
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    conds = []
    if legend is None:
        legend = ["dissociate size > 2", "dissociate size = 2", "dissociate size < 2"]
        conds = [">2", "==2", "<2"]
    else:
        for l in legend:
            if not l.startswith("dissociate size"):
                raise ValueError(f"Legend '{l}' must start with 'dissociate size'.")
            cond = l.replace("dissociate size", "").strip()
            if not any(op in cond for op in [">=", "<=", "==", "!=", ">", "<", "="]):
                raise ValueError(f"Legend condition '{cond}' must contain a valid comparison operator.")
            cond = cond.replace("=", "==") if "=" in cond and "==" not in cond else cond
            conds.append(cond)

    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)

    all_dissoc_probs = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        file_path = os.path.join(sim_dir, "transition_matrix_time.dat")

        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping simulation {idx}.")
            continue

        matrix_delta, _ = parse_transition_lifetime_data(file_path, time_frame)
        max_size = matrix_delta.shape[0]

        dissoc_probs = [[] for _ in conds]

        for n in range(1, max_size):
            dissoc_counts = []
            # loop from n-1 to 0 to statistically count dissociations
            for m in range(n - 1, -1, -1):
                pair_size = n - m
                count = matrix_delta[m, n]
                if pair_size == m + 1:
                    count /= 2
                dissoc_counts.append((pair_size, count))

            total_dissoc = sum(c for _, c in dissoc_counts)
            for j, cond in enumerate(conds):
                selected = [c for s, c in dissoc_counts if eval(f"{s}{cond}")]
                dissoc_probs[j].append(sum(selected) / total_dissoc if total_dissoc > 0 else np.nan)

        all_dissoc_probs.append(np.array(dissoc_probs))

    if not all_dissoc_probs:
        print("No valid simulation data found.")
        return

    min_length = min(prob.shape[1] for prob in all_dissoc_probs)
    all_dissoc_probs = [prob[:, :min_length] for prob in all_dissoc_probs]

    cluster_sizes = np.arange(2, min_length + 2)  # start from size 2 since we are looking at dissociations
    prob_array = np.array(all_dissoc_probs)

    avg_probs = np.nanmean(prob_array, axis=0)
    std_probs = np.nanstd(prob_array, axis=0)

    df_to_save = {"Cluster Size": cluster_sizes}
    for i, label in enumerate(legend):
        df_to_save[f"{label} (avg)"] = avg_probs[i]
        df_to_save[f"{label} (std)"] = std_probs[i]
    df_to_save = pd.DataFrame(df_to_save)

    save_path = os.path.join(plot_data_dir, "symmetric_dissociation_probability.csv")
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")

    plt.figure(figsize=figure_size)

    if show_type in {"individuals", "both"}:
        for sim_idx, sim_probs in enumerate(prob_array):
            for i, label in enumerate(legend):
                plt.plot(cluster_sizes, sim_probs[i], linestyle="dashed", alpha=0.3, label=f"{label} (run {sim_idx})" if show_type == "both" else None)

    if show_type in {"average", "both"}:
        for i, label in enumerate(legend):
            plt.plot(cluster_sizes, avg_probs[i], label=f"{label} (avg)", linewidth=2)
            plt.fill_between(cluster_sizes, avg_probs[i] - std_probs[i], avg_probs[i] + std_probs[i], alpha=0.2)

    plt.xlabel("Cluster Size (n)")
    plt.ylabel("Dissociation Probability")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "symmetric_dissociation_probability.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()
    print(f"Plot saved to {plot_path}")

def plot_line_asymmetric_dissociation_probability(
    save_dir: str,
    simulations_index: list,
    legend: list = None,
    time_frame: tuple = None,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    This line plot represents the probability of dissociation between complexes of different sizes.
    Each dissociation event is counted once.
    
    legend examples: ["dissociate size > n", "dissociate size = n", "dissociate size < n"]

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list, optional): Custom legend labels for the plot.
        time_frame (tuple, optional): Time range (start, end) to consider for statistic.
        show_type (str): Display mode - "both", "individuals", or "average".
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    conds = []
    if legend is None:
        legend = ["dissociate size > 2", "dissociate size = 2", "dissociate size < 2"]
        conds = [">2", "==2", "<2"]
    else:
        for l in legend:
            if not l.startswith("dissociate size"):
                raise ValueError(f"Legend '{l}' must start with 'dissociate size'.")
            cond = l.replace("dissociate size", "").strip()
            if not any(op in cond for op in [">=", "<=", "==", "!=", ">", "<", "="]):
                raise ValueError(f"Legend condition '{cond}' must contain a valid comparison operator.")
            cond = cond.replace("=", "==") if "=" in cond and "==" not in cond else cond
            conds.append(cond)

    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)

    all_dissoc_probs = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        file_path = os.path.join(sim_dir, "transition_matrix_time.dat")

        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping simulation {idx}.")
            continue

        matrix_delta, _ = parse_transition_lifetime_data(file_path, time_frame)
        max_size = matrix_delta.shape[0]

        dissoc_probs = [[] for _ in conds]

        for n in range(1, max_size):
            dissoc_counts = []
            # loop from n-1 to 0 to statistically count dissociations
            for m in range(n - 1, -1, -1):
                pair_size = n - m
                count = matrix_delta[m, n]
                if pair_size == m + 1:
                    count /= 2
                if pair_size > m + 1:
                    break
                dissoc_counts.append((pair_size, count))

            total_dissoc = sum(c for _, c in dissoc_counts)
            for j, cond in enumerate(conds):
                selected = [c for s, c in dissoc_counts if eval(f"{s}{cond}")]
                dissoc_probs[j].append(sum(selected) / total_dissoc if total_dissoc > 0 else np.nan)

        all_dissoc_probs.append(np.array(dissoc_probs))

    if not all_dissoc_probs:
        print("No valid simulation data found.")
        return

    min_length = min(prob.shape[1] for prob in all_dissoc_probs)
    all_dissoc_probs = [prob[:, :min_length] for prob in all_dissoc_probs]

    cluster_sizes = np.arange(2, min_length + 2)  # start from size 2 since we are looking at dissociations
    prob_array = np.array(all_dissoc_probs)

    avg_probs = np.nanmean(prob_array, axis=0)
    std_probs = np.nanstd(prob_array, axis=0)

    df_to_save = {"Cluster Size": cluster_sizes}
    for i, label in enumerate(legend):
        df_to_save[f"{label} (avg)"] = avg_probs[i]
        df_to_save[f"{label} (std)"] = std_probs[i]
    df_to_save = pd.DataFrame(df_to_save)

    save_path = os.path.join(plot_data_dir, "asymmetric_dissociation_probability.csv")
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")

    plt.figure(figsize=figure_size)

    if show_type in {"individuals", "both"}:
        for sim_idx, sim_probs in enumerate(prob_array):
            for i, label in enumerate(legend):
                plt.plot(cluster_sizes, sim_probs[i], linestyle="dashed", alpha=0.3, label=f"{label} (run {sim_idx})" if show_type == "both" else None)

    if show_type in {"average", "both"}:
        for i, label in enumerate(legend):
            plt.plot(cluster_sizes, avg_probs[i], label=f"{label} (avg)", linewidth=2)
            plt.fill_between(cluster_sizes, avg_probs[i] - std_probs[i], avg_probs[i] + std_probs[i], alpha=0.2)

    plt.xlabel("Cluster Size (n)")
    plt.ylabel("Dissociation Probability")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "asymmetric_dissociation_probability.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()
    print(f"Plot saved to {plot_path}")

def plot_line_growth_probability(
    save_dir: str,
    simulations_index: list,
    legend: list = None,
    time_frame: tuple = None,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    This line plot represents the probability of growth between complexes of different sizes.

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list, optional): Custom legend labels for the plot.
        time_frame (tuple, optional): Time range (start, end) to consider for statistic.
        show_type (str): Display mode - "both", "individuals", or "average".
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)

    all_growth_probs = []

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        file_path = os.path.join(sim_dir, "transition_matrix_time.dat")

        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping simulation {idx}.")
            continue

        matrix_delta, _ = parse_transition_lifetime_data(file_path, time_frame)
        max_size = matrix_delta.shape[0]

        growth_probs = []

        for n in range(0, max_size):
            dissoc_counts = []
            assoc_counts = []
            # loop from n-1 to 0 to statistically count dissociations
            # each dissociation event is counted once
            for m in range(n - 1, -1, -1):
                pair_size = n - m
                count = matrix_delta[m, n]
                if pair_size == m + 1:
                    count /= 2
                if pair_size > m + 1:
                    break
                dissoc_counts.append(count)

            for m in range(n + 1, max_size):
                pair_size = m - n
                count = matrix_delta[m, n]
                if pair_size == n + 1:
                    count /= 2
                assoc_counts.append(count)

            total_dissoc = sum(dissoc_counts) if dissoc_counts else 0
            total_assoc = sum(assoc_counts) if assoc_counts else 0
            growth_probs.append(total_assoc / (total_dissoc + total_assoc) if (total_dissoc + total_assoc) > 0 else np.nan)

        all_growth_probs.append(np.array(growth_probs))

    if not all_growth_probs:
        print("No valid simulation data found.")
        return

    min_length = min(len(prob) for prob in all_growth_probs)
    all_growth_probs = [prob[:min_length] for prob in all_growth_probs]

    cluster_sizes = np.arange(1, min_length + 1)
    prob_array = np.vstack(all_growth_probs)

    avg_probs = np.nanmean(prob_array, axis=0)
    std_probs = np.nanstd(prob_array, axis=0)

    df_to_save = pd.DataFrame({
        "Cluster Size": cluster_sizes,
        "Growth Probability (avg)": avg_probs,
        "Growth Probability (std)": std_probs
    })

    save_path = os.path.join(plot_data_dir, "growth_probability.csv")
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")

    plt.figure(figsize=figure_size)

    if show_type in {"individuals", "both"}:
        for i, sim_probs in enumerate(prob_array):
            plt.plot(cluster_sizes, sim_probs, linestyle="dashed", alpha=0.3, label=f"Run {i}" if show_type == "both" else None)

    if show_type in {"average", "both"}:
        plt.plot(cluster_sizes, avg_probs, label="Average", linewidth=2)
        plt.fill_between(cluster_sizes, avg_probs - std_probs, avg_probs + std_probs, alpha=0.2)

    plt.xlabel("Cluster Size (n)")
    plt.ylabel("Growth Probability")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "growth_probability.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()
    print(f"Plot saved to {plot_path}")

def plot_line_liftime(
    save_dir: str,
    simulations_index: list,
    legend: list = None,
    time_frame: tuple = None,
    show_type: str = "both",
    simulations_dir: list = None,
    figure_size: tuple = (10, 6)
):
    """
    This line plot represents the average lifetime between complexes of different sizes.

    Parameters:
        save_dir (str): The base directory where simulation results are stored.
        simulations_index (list): Indices of the simulations to include.
        legend (list, optional): Custom legend labels for the plot.
        time_frame (tuple, optional): Time range (start, end) to consider for statistic.
        show_type (str): Display mode - "both", "individuals", or "average".
        simulations_dir (list): List of directories for each simulation.
        figure_size (tuple): Size of the figure.
    """
    plot_data_dir = os.path.join(save_dir, "figure_plot_data")
    os.makedirs(plot_data_dir, exist_ok=True)

    all_lifetime_arrays = []

    max_cluster_size = 0

    for idx in simulations_index:
        sim_dir = os.path.join(simulations_dir[idx], "DATA")
        file_path = os.path.join(sim_dir, "transition_matrix_time.dat")

        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping simulation {idx}.")
            continue

        _, lifetime = parse_transition_lifetime_data(file_path, time_frame)
        sizes = sorted(lifetime.keys())
        max_cluster_size = max(max_cluster_size, max(sizes, default=0))

        avg_lifetimes = []
        for size in range(1, max_cluster_size + 1):
            lifetimes = lifetime.get(size, [])
            avg_lifetimes.append(np.mean(lifetimes) if lifetimes else np.nan)

        all_lifetime_arrays.append(avg_lifetimes)

    if not all_lifetime_arrays:
        print("No valid simulation lifetime data found.")
        return
    
    # Pad all arrays to same length
    for i in range(len(all_lifetime_arrays)):
        diff = max_cluster_size - len(all_lifetime_arrays[i])
        if diff > 0:
            all_lifetime_arrays[i].extend([np.nan] * diff)

    cluster_sizes = np.arange(1, max_cluster_size + 1)
    lifetime_array = np.array(all_lifetime_arrays)

    avg_lifetime = np.nanmean(lifetime_array, axis=0)
    std_lifetime = np.nanstd(lifetime_array, axis=0)

    df_to_save = pd.DataFrame({
        "Cluster Size": cluster_sizes,
        "Mean Lifetime (s)": avg_lifetime,
        "Std Lifetime": std_lifetime
    })

    save_path = os.path.join(plot_data_dir, "lifetime_vs_size.csv")
    df_to_save.to_csv(save_path, index=False)
    print(f"Processed data saved to {save_path}")

    # Plotting
    plt.figure(figsize=figure_size)

    if show_type in {"individuals", "both"}:
        for i, lt in enumerate(lifetime_array):
            plt.plot(cluster_sizes, lt, linestyle="dashed", alpha=0.3, label=f"Sim {i}" if show_type == "both" else None)

    if show_type in {"average", "both"}:
        plt.plot(cluster_sizes, avg_lifetime, label="Average", linewidth=2)
        plt.fill_between(cluster_sizes, avg_lifetime - std_lifetime, avg_lifetime + std_lifetime, alpha=0.2)

    plt.xlabel("Cluster Size (n)")
    plt.ylabel("Average Lifetime (s)")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_data_dir, "lifetime_vs_size.svg")
    plt.savefig(plot_path, format="svg")
    plt.show()
    print(f"Plot saved to {plot_path}")
