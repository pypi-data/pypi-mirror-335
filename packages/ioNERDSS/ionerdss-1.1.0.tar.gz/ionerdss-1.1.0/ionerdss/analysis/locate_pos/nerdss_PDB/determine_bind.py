from .calculate_distance import calculate_distance

def determine_bind(site_1, site_2, buffer_ratio, site_dict, sigma):
    """Determines whether two sites are binded based on how close they are

    Args:
        site_1 (list): information about 1 site (import part: it's location)
        site_2 (list): information about another site
        buffer_ratio (float): the buffer ratio used to determine binding, defined as a fraction of 'sigma'
        site_dict (dictionary): turns column name (from df) into list index for site_array
        sigma (float): how close the two sites need to be in order to be considered binded

    Returns:
        boolean: whether or not they are bonded
    """
    #calculate distance
    x = (site_1[site_dict['x_coord']],site_1[site_dict['y_coord']],site_1[site_dict['z_coord']])
    y = (site_2[site_dict['x_coord']],site_2[site_dict['y_coord']],site_2[site_dict['z_coord']])
    distance = calculate_distance(x, y)

    #calculate if they are close enough to bind
    return distance >= sigma*(1-buffer_ratio) and distance <= sigma*(1+buffer_ratio)


