import math
import numpy as np


def fitSphere(x, y, z):
    """This function takes three arrays of equal length x, y and z and returns the radius and center of a sphere that best fits the data.

    Parameters
        x: array of x coordinates
        y: array of y coordinates
        z: array of z coordinates
    Returns
        A tuple of four elements:
            radius: the radius of the best fit sphere
            x_center: the x coordinate of the sphere's center
            y_center: the y coordinate of the sphere's center
            z_center: the z coordinate of the sphere's center
    """
    A = np.zeros((len(x), 4))
    A[:, 0] = 2*x
    A[:, 1] = 2*y
    A[:, 2] = 2*z
    A[:, 3] = 1
    f = np.zeros((len(x), 1))
    f[:, 0] = x*x+y*y+z*z
    C, residules, rank, singval = np.linalg.lstsq(A, f, rcond=None)
    t = (C[0]*C[0])+(C[1]*C[1])+(C[2]*C[2])+C[3]
    radius = math.sqrt(t)
    return radius, C[0], C[1], C[2]


