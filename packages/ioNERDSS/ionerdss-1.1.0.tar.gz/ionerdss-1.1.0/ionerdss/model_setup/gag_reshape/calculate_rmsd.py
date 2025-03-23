import numpy as np

# function definition
def calculate_rmsd(centers, xyzR):  
    """
    Calculates the root mean squared deviation (rmsd) to describe how gags' centers are biased from a perfect sphere surface

    Args:
        centers (18*3 list of floats): the x, y, z coordinates of the 18 gag centers
        xyzR (list of floats): the x, y, z coordinates of the center of the sphere and the radius of the sphere

    Returns:
        s (float): the rmsd value
    """
    x0 = xyzR[0]
    y0 = xyzR[1]
    z0 = xyzR[2]
    r0 = xyzR[3]
    s = 0.0
    for i in range(0,centers.shape[0]):
        xi = centers[i,0]
        yi = centers[i,1]
        zi = centers[i,2]
        ri = np.sqrt( (xi-x0)**2 + (yi-y0)**2 + (zi-z0)**2 )
        s = s + (ri-r0)**2
    return s

