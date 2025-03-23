import math
import numpy as np
from .real_PDB_unit import real_PDB_unit
from .real_PDB_triangle_correction import real_PDB_triangle_correction
from .real_PDB_calculate_phi import real_PDB_calculate_phi


def real_PDB_angles(COM1, COM2, int_site1, int_site2, normal_point1, normal_point2):
    """Calculates the angles for binding using the provided inputs.

    Args:
        COM1 (array): The center of mass of particle 1.
        COM2 (array): The center of mass of particle 2.
        int_site1 (array): The interface site of particle 1.
        int_site2 (array): The interface site of particle 2.
        normal_point1 (array): The normal point of particle 1.
        normal_point2 (array): The normal point of particle 2.

    Returns:
        Tuple of floats: The calculated values for theta1, theta2, phi1, phi2, omega, and sigma_magnitude respectively.

    Raises:
        ValueError: If n1 and v1 or n2 and v2 are parallel.
        """

    # Convert sequences into arrays for convinience
    COM1 = np.array(COM1)
    COM2 = np.array(COM2)
    int_site1 = np.array(int_site1)
    int_site2 = np.array(int_site2)
    normal_point1 = np.array(normal_point1)
    normal_point2 = np.array(normal_point2)

    # Get Vectors
    v1 = int_site1 - COM1  # from COM to interface (particle 1)
    v2 = int_site2 - COM2  # from COM to interface (particle 2)
    sigma1 = int_site1 - int_site2  # sigma, from p2 to p1
    sigma2 = int_site2 - int_site1  # sigma, from p1 to p2
    n1 = real_PDB_unit(normal_point1 - COM1)  # normal vector for p1
    n2 = real_PDB_unit(normal_point2 - COM2)  # normal vector for p2

    # Calculate the magnititude of sigma
    sigma_magnitude = np.linalg.norm(sigma1)

    # Calculate theta1 and theta2
    costheta1 = np.dot(v1, sigma1) / np.linalg.norm(v1) / \
        np.linalg.norm(sigma1)
    costheta2 = np.dot(v2, sigma2) / np.linalg.norm(v2) / \
        np.linalg.norm(sigma2)
    theta1 = math.acos(real_PDB_triangle_correction(costheta1))
    theta2 = math.acos(real_PDB_triangle_correction(costheta2))

    # check geometry
    errormsg = ''
    iferror = False  # determine if v // n
    if np.linalg.norm(np.cross(n1, v1)) < 10**-6:
        iferror = True
        errormsg += '\n\tn1 and v1 parallel, phi1 not available'
    if np.linalg.norm(np.cross(n2, v2)) < 10**-6:
        iferror = True
        errormsg += '\n\tn2 and v2 parallel, phi2 not available'
    if iferror:
        raise ValueError(errormsg)

    # determine if phi1 exists (v1 // sigma1 ?)
    if np.linalg.norm(np.cross(sigma1, v1)) < 10**-6:
        phi1 = float('nan')
        # omega_parallel = True
        omega_t1 = real_PDB_unit(np.cross(sigma1, n1))
    else:
        phi1 = real_PDB_calculate_phi(v1, n1, sigma1)
        omega_t1 = real_PDB_unit(np.cross(sigma1, v1))

    # determine if phi2 exists (v2 // sigma2 ?)
    if np.linalg.norm(np.cross(sigma2, v2)) < 10**-6:
        phi2 = float('nan')
        # omega_parallel = True
        omega_t2 = real_PDB_unit(np.cross(sigma1, n2))
    else:
        phi2 = real_PDB_calculate_phi(v2, n2, sigma2)
        omega_t2 = real_PDB_unit(np.cross(sigma1, v2))

    # calculate omega (both cases are same)
    omega = math.acos(real_PDB_triangle_correction(np.dot(omega_t1, omega_t2)))
    # determine the sign of omega (+/-)
    sigma1_uni = real_PDB_unit(sigma1)
    sigma1xomega_t1 = np.cross(sigma1, omega_t1)
    sigma1xomega_t2 = np.cross(sigma1, omega_t2)
    omega_dir = real_PDB_unit(np.cross(sigma1xomega_t1, sigma1xomega_t2))
    if np.dot(sigma1_uni, omega_dir) > 0:
        omega = -omega
    else:
        omega = omega

    return theta1, theta2, phi1, phi2, omega, sigma_magnitude


