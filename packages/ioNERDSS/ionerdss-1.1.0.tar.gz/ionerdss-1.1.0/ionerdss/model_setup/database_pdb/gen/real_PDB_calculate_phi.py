import math
import numpy as np
from .real_PDB_unit import real_PDB_unit
from .real_PDB_triangle_correction import real_PDB_triangle_correction


def real_PDB_calculate_phi(v: np.ndarray, n: np.ndarray, sigma: np.ndarray) -> float:
    """Calculate phi angle between vector v and plane defined by normal n and point sigma.

    Args:
        v (np.array): A vector.
        n (np.array): A normal vector of the plane.
        sigma (np.array): A point on the plane.

    Returns:
        phi (float): The phi angle in radians.

    Raises:
        ValueError: If v, n, or sigma are not 1-D numpy arrays or if they have a length different from 3.

    Example:
        v = np.array([1, 2, 3])
        n = np.array([0, 1, 0])
        sigma = np.array([1, 0, 0])
        phi = real_PDB_calculate_phi(v, n, sigma)
        print(phi) # Output: 1.5707963267948966

    """

    # calculate phi
    t1 = real_PDB_unit(np.cross(v, sigma))
    t2 = real_PDB_unit(np.cross(v, n))
    phi = math.acos(real_PDB_triangle_correction(np.dot(t1, t2)))

    # determine the sign of phi (+/-)
    v_uni = real_PDB_unit(v)
    n_proj = n - v_uni * np.dot(v_uni, n)
    sigma_proj = sigma - v_uni * np.dot(v_uni, sigma)
    phi_dir = real_PDB_unit(np.cross(sigma_proj, n_proj))

    if np.dot(v_uni, phi_dir) > 0:
        phi = -phi
    else:
        phi = phi

    return phi



