import math


def real_PDB_mag(x):
    """
    This function calculates the direct distance b/w 2 coordinates (in a 3d space) based on their dx,dy,dz.

    Args:
        x (list): a list of float values representing the Cartesian coordinates (dx,dy,dz) of the vector.

    Returns:
        A float value representing the magnitude of the vector.

    Example:
        >>> real_PDB_mag([3.0, 4.0, 0.0])
        5.0
    """
    return math.sqrt(sum(i ** 2 for i in x))


