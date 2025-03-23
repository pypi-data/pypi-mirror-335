import os
import numpy as np


def add_empty_lists(data_list: list) -> list:
    """Recursively adds 'Empty List' to empty lists within a given list.

    This function checks if a list or its sublists (including NumPy arrays) are empty.
    If a list is empty, it appends `"Empty List"`. Otherwise, it processes sublists recursively.

    Args:
        data_list (list): The input list to be processed.

    Returns:
        list: The modified list with 'Empty List' inserted where necessary.

    Example:
        >>> add_empty_lists([])
        ['Empty List']

        >>> add_empty_lists([[], [1, 2, 3], np.array([])])
        [['Empty List'], [1, 2, 3], ['Empty List']]
    """
    if not isinstance(data_list, list):
        raise TypeError("`data_list` must be a list.")

    # If list is empty, insert "Empty List"
    if len(data_list) == 0:
        return ["Empty List"]

    # Recursively process sublists
    return [add_empty_lists(list(item)) if isinstance(item, (list, np.ndarray)) else item for item in data_list]


def save_vars_to_file(variable_dict: dict, output_dir: str) -> None:
    """Saves variables from a dictionary to text or CSV files.

    This function iterates through a dictionary and saves each variable in an appropriate format:
        - Integers and floats are stored as `.txt` files.
        - Strings are stored as `.txt` files.
        - Lists and NumPy arrays are stored as `.csv` files.
        - Multi-dimensional lists (2D+) are stored with sublists written on separate lines.

    Args:
        variable_dict (dict): A dictionary where keys are variable names and values are the data to save.
        output_dir (str, optional): Directory where the files will be saved. Defaults to `"vars"`.

    Raises:
        TypeError: If `variable_dict` is not a dictionary.
        OSError: If unable to create the directory.

    Example:
        >>> save_vars_to_file({"temperature": 36.5, "names": ["Alice", "Bob"]}, "vars")
        # Saves "vars/temperature_number.txt" and "vars/names_list.csv"
    """

    if not isinstance(variable_dict, dict):
        raise TypeError("`variable_dict` must be a dictionary.")

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            raise OSError(f"Error creating directory '{output_dir}': {e}")

    for key, value in variable_dict.items():
        file_extension = ""
        file_type = ""
        file_content = ""

        # Determine file type based on value type
        if isinstance(value, (int, float)):  # Number
            file_extension = f"{key}_number.txt"
            file_type = "txt"
            file_content = str(value)

        elif isinstance(value, str):  # String
            file_extension = f"{key}_string.txt"
            file_type = "txt"
            file_content = value

        elif isinstance(value, (list, np.ndarray)):  # List or NumPy array
            file_extension = f"{key}_list.csv"
            processed_value = add_empty_lists(list(value))  # Handle empty lists

            if isinstance(processed_value[0], (list, np.ndarray)):  # 2D+ list
                file_type = "2D_list"
            else:  # 1D list
                file_type = "1D_list"

        else:  # Unsupported type
            file_extension = f"{key}_unknown.txt"
            file_type = "txt"
            file_content = str(value)

        file_path = os.path.join(output_dir, file_extension)

        # Write data to file
        with open(file_path, mode="w", encoding="utf-8") as file:
            if file_type == "txt":
                file.write(file_content)

            elif file_type == "1D_list":
                file.write(",".join(map(str, processed_value)))

            elif file_type == "2D_list":
                for sublist in processed_value:
                    file.write(",".join(map(str, sublist)) + "\n")
                    