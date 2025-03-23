import numpy as np


def real_PDB_unit(x: np.ndarray) -> np.ndarray:
    """Returns the unit vector of the input vector x.

    Args:
        x (numpy.ndarray): The input vector.

    Returns:
        numpy.ndarray: The unit vector of x.

    Note:
        If the magnitude of x is zero, this function will return a vector of zeros.
        If the magnitude of x is one, this function will return x.

    Examples:
        >>> real_PDB_unit(np.array([1, 2, 3]))
        array([0.26726124, 0.53452248, 0.80178373])
        >>> real_PDB_unit(np.array([0, 0, 0]))
        array([0, 0, 0])
        >>> real_PDB_unit(np.array([1, 0, 0]))
        array([1, 0, 0])
    """

    x_norm = np.linalg.norm(x)
    if abs(x_norm-1) < 10**-6:
        return x
    elif x_norm < 10**-6:
        return np.zeros(3)
    else:
        return x/x_norm


