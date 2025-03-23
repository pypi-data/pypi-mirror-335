import numpy as np


def xyz_to_sphere_coordinates(position): # translate x-y-z coords to spherical coords
    """
    Translate x-y-z coordinates to spherical coordinates.
    Args:
        position (list): x-y-z coordinates of a point
    Returns:
        spherecoordinates (list): theta-phi-r coordinates of the point
    """
    x = position[0]
    y = position[1]
    z = position[2]
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(z/r)
    phi = np.arccos( x/r/np.sin(theta) )
    if y < 0 :
        phi = 2.0*np.pi - phi
    spherecoordinates = [theta, phi, r]
    return spherecoordinates

