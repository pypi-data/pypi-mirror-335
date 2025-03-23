def hist_temp(histogram_data: list, initial_time: float, final_time: float):
    """Calculates the average count of each complex size within a specified time range.

    This function extracts complex size distributions from a time-series histogram dataset
    and computes the average occurrence of each complex size over the given time interval.

    Args:
        histogram_data (list): 
            A list of time-dependent histogram data, where each element represents a time step.
            Each element is structured as `[time, complex_counts, complex_sizes]`, where:
            - `time` (float): The timestamp.
            - `complex_counts` (list[int]): A list of counts corresponding to each complex size.
            - `complex_sizes` (list[int]): The sizes of the complexes.
        initial_time (float): 
            The starting time for the analysis. Must be within the time range of the histogram data. Initial time inclusive.
        final_time (float): 
            The ending time for the analysis. Must be within the time range of the histogram data. Final time exclusive.

    Returns:
        tuple:
            - list[int]: Unique complex sizes present in the specified time range.
            - list[float]: The average count of each complex size over the selected time range.

    Raises:
        ValueError: If `initial_time` is greater than `final_time`.
        ValueError: If `histogram_data` is empty or improperly formatted.

    Example:
        >>> hist_data = [
        ...     [0.0, [10, 5], [1, 2]],
        ...     [50.0, [15, 8], [1, 2]],
        ...     [100.0, [20, 10], [1, 2]]
        ... ]
        >>> hist_temp(hist_data, 0, 100)
        ([1, 2], [15.0, 7.67])
    """

    if initial_time > final_time:
        raise ValueError("`initial_time` must be less than or equal to `final_time`.")

    if not histogram_data or not isinstance(histogram_data, list):
        raise ValueError("`histogram_data` must be a non-empty list.")

    complex_counts = {}  # Dictionary to store counts for each complex size
    time_steps = 0  # Counter for the number of time steps in the range

    # Process each timestep
    for timestep in histogram_data:
        if not isinstance(timestep, list) or len(timestep) != 3:
            raise ValueError("Each timestep in `histogram_data` must be a list of [time, complex_counts, complex_sizes].")

        time, counts, sizes = timestep

        if not isinstance(time, (int, float)) or not isinstance(counts, list) or not isinstance(sizes, list):
            raise ValueError("Invalid data format in `histogram_data`. Expected [time, list[int], list[int]].")

        # Consider only timesteps within the specified range
        if initial_time <= time < final_time:
            time_steps += 1

            for size, count in zip(sizes, counts):
                if size in complex_counts:
                    complex_counts[size] += count
                else:
                    complex_counts[size] = count

        elif time > final_time:
            break  # Since times are sorted, we can exit early

    # Compute mean counts per complex size
    if time_steps == 0:
        return [], []  # No valid data within the time range

    unique_complex_sizes = sorted(complex_counts.keys())
    average_counts = [complex_counts[size] / time_steps for size in unique_complex_sizes]

    return unique_complex_sizes, average_counts
