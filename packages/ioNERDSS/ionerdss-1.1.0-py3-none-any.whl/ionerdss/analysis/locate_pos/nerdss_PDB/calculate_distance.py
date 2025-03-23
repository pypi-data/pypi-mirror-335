def calculate_distance(x, y):
    """Calculates the Euclidean distance between two points in 3D space.

    Args:
        x (Tuple[float, float, float]): the coordinates of the first point as a tuple (x, y, z)
        y (Tuple[float, float, float]): the coordinates of the second point as a tuple (x, y, z)

    Returns:
        float: the Euclidean distance between the two points

    Example:
        >>> x = (1.0, 2.0, 3.0)
        >>> y = (4.0, 5.0, 6.0)
        >>> calculate_distance(x, y)
        5.196152422706632
    """
        
    return ((x[0]-y[0])**2+(x[1]-y[1])**2+(x[2]-y[2])**2)**0.5


