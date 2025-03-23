import os

def read_file(file_path: str, species_name: str):
    """Reads a `histogram.dat` file and extracts time-series data for a specific species.

    This function parses a `.dat` file containing histogram data, extracting information about 
    the species of interest and returning a structured list representation.

    Args:
        file_path (str): 
            Path to the `histogram.dat` file.
        species_name (str): 
            The name of the species to extract from the file. It must be present in the file.

    Returns:
        list[list]: 
            A nested list structure where:
            - `hist[i][0]`: Timestamp of the data entry.
            - `hist[i][1]`: List of complex counts corresponding to each size.
            - `hist[i][2]`: List of species counts in each complex.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the species name is not found in the file.

    Example:
        >>> read_file("histogram.dat", "SpeciesA")
        [[0.0, [1, 2], [10, 20]], [50.0, [3, 1], [30, 5]], [100.0, [2, 4], [15, 25]]]
    """

    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    histogram_data = []  # Main list that holds all timestamped entries
    temp_data = []  # Temporary list to store current timestamp data
    species_counts = []  # Stores species count at a given timestamp
    complex_counts = []  # Stores complex size count at a given timestamp

    # Read the file
    species_found = False
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # Identify a new timestamp entry
            if line.startswith("Time"):
                # Store previous timestamp data if it exists
                if temp_data:
                    temp_data.append(species_counts)
                    temp_data.append(complex_counts)
                    histogram_data.append(temp_data)

                # Reset temporary lists
                species_counts = []
                complex_counts = []
                temp_data = []

                # Extract timestamp
                try:
                    timestamp = float(line.replace("Time (s):", "").strip())
                    temp_data.append(timestamp)
                except ValueError:
                    raise ValueError(f"Invalid time format in line: {line}")

            # Extract species-related data
            else:
                species_prefix = f"\t{species_name}: "
                if species_prefix not in line:
                    continue  # Skip if species name does not match
                
                # Parse species data
                try:
                    count, size = map(float, line.split(species_prefix))
                    species_counts.append(count)
                    complex_counts.append(size)
                    species_found = True
                except ValueError:
                    raise ValueError(f"Invalid species data format in line: {line}")
                
    # Check if species was found
    if not species_found:
        raise ValueError(f"Species '{species_name}' not found in the file.")

    # Add last parsed entry if valid
    if temp_data:
        temp_data.append(species_counts)
        temp_data.append(complex_counts)
        histogram_data.append(temp_data)

    return histogram_data