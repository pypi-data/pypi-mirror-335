def real_PDB_triangle_correction(x: float) -> float:
    """If x is slightly out of the range of [-1,1], it will be set to -1 or 1, whatever is closer. Else, it will return error.
    
    Args:
        x (float): A ratio meant to be input into acos/asin.

    Returns:
        float: A corrected ratio in the range [-1, 1].

    Raises:
        ValueError: If x is out of the range of arcsine or arccosine.

    Examples:
        >>> real_PDB_triangle_correction(1.00000000001)
        1.0
        >>> real_PDB_triangle_correction(1.1)
        Traceback (most recent call last):
    """

    if x < -1 and abs(x+1) < 10**-6:
        return -1
    elif x > 1 and abs(x-1) < 10**-6:
        return 1
    elif -1 <= x <= 1:
        return x
    else:
        raise ValueError(f'{x} is out of the range of arcsine or arccosine')


