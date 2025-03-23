import numpy as np
import pandas as pd


def translate_gags_on_sphere(hexmer, center1, center2): 
    """move a hexamer gags on the sphere surface
       express the hexmer in the internal coord system, which is based on the point 'from' (center1)

    Args:
        hexmer (_type_): _description_
        center1 (_type_): _description_
        center2 (_type_): _description_

    Returns:
        _type_: _description_
    """

    # set up the internal coordinate basis for hexmer: vec1, vec2, vec3
    vec1 = center1 / np.linalg.norm(center1) # vec1 is along the radius direction
    vec2 = center2 - center1                 # vec2 considers the translational direction
    vec3 = np.cross(vec1,vec2)               # vec3 is along the tangent line of the hexmer
    vec3 = vec3/np.linalg.norm(vec3)
    vec2 = np.cross(vec3,vec1)
    vec2 = vec2/np.linalg.norm(vec2)
    coeffs = np.zeros([hexmer.shape[0],3])
    for i in range (0,hexmer.shape[0]) :
        b = hexmer[i,:] - center1
        A = np.array([vec1, vec2, vec3])
        coeff = [0.0, 0.0, 0.0]
        if (np.linalg.norm(b) > 1e-10) :    
            coeff = np.dot(b, np.linalg.inv(A))
        coeffs[i,:] = coeff
    # move the internal coord system to the point 'to' (center2)
    # find the internal coord system based on the point 'to'
    vec1 = center2 / np.linalg.norm(center2)
    vec2 = center2 - center1 
    vec3 = np.cross(vec1,vec2)
    vec3 = vec3/np.linalg.norm(vec3)
    vec2 = np.cross(vec3,vec1)
    vec2 = vec2/np.linalg.norm(vec2)
    # rebuid the hexmer at this new point 'to'
    newhexmer = np.zeros([hexmer.shape[0],3])
    for i in range (0,hexmer.shape[0]) :
        newhexmer[i,:] = coeffs[i,0]*vec1 + coeffs[i,1]*vec2 + coeffs[i,2]*vec3 + center2
    return newhexmer



