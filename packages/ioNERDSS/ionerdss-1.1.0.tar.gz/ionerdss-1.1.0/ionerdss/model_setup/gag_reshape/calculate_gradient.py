import numpy as np


def calculate_gradient(centers,xyzR): 
    """calculate the gradient of the gag positions for the optimization of the gag positions on the sphere surface
         
    Args:
        centers (18*3 list of floats): the x, y, z coordinates of the 18 gag centers
        xyzR (list of floats): the x, y, z coordinates of the center of the gag sphere and the radius of the gagsphere

    Returns:
        gradient (list of floats): the gradient of the gag positions
    """

    x0 = xyzR[0]
    y0 = xyzR[1]
    z0 = xyzR[2]
    r0 = xyzR[3]
    dsdx = 0
    dsdy = 0
    dsdz = 0
    dsdr = 0
    for i in range(0,centers.shape[0]):
        xi = centers[i,0]
        yi = centers[i,1]
        zi = centers[i,2]
        ri = np.sqrt( (xi-x0)**2 + (yi-y0)**2 + (zi-z0)**2 )
        dsdx = dsdx + (-2.0/ri)*(ri-r0)*(xi-x0)
        dsdy = dsdy + (-2.0/ri)*(ri-r0)*(yi-y0)
        dsdz = dsdz + (-2.0/ri)*(ri-r0)*(zi-z0)
        dsdr = dsdr + (-2.0)*(ri-r0)
    gradient = np.array([dsdx, dsdy, dsdz, dsdr])
    return gradient

