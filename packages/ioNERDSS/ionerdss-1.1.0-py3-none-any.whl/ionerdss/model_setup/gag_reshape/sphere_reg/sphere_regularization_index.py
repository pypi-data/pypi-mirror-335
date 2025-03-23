import numpy as np
from .fitSphere import fitSphere
from .single_restart_to_df import single_restart_to_df
from ....analysis.histogram.single_species import single_hist_obj
import os

def sphere_regularization_index(PathName: str, IterNum: int, TimeStep: float,
                                ComplexNum: int, SpeciesName: str = "gag"):
    """This function calculates the regularization index of the given parameters.

    Parameters:
        PathName(String): The path of the histogram file, PDB, and restart file
        IterNum(int): The iteration number of the simulation
        TimeStep(float): the time step of the simulation in micro-seconds
        ComplexNum(int): The number of complexes to be analyzed, starting from the largest complex size
        SpeciesName(String): The of the species intended to be analyzed
    
    Returns:
        max_complex_size_return: A list of integers representing the maximum complex size of each complex
        theta_ideal_return: A list of floats representing the ideal spherical angle of each complex
        sphere_radius_return: A list of floats representing the sphere radius of each complex
        sphere_center_position_return: A list of floats representing the sphere center position of each complex
        complex_COM_return: A list of floats representing the center of mass of each complex
        regularization_index_return: A list of floats representing the regularization index of each complex
    
    This function calculates the regularization index of the given parameters. 
    It firsts get the data from the histogram and then calculates the maximum complex size. 
    It then fits 3 spheres and does a sanity check. 
    It then calculates the center of mass of the max complex and determines the spherical angle
    corresponding to the ideal complex with surface area. 
    It then determines if the monomer on complex is on the ideal cap and returns the regularization index.
    """
    
    # reads in the histogram file and obtain the size of complexes formed and their corresponding counts at inputted simulation step
    t = TimeStep * IterNum * 0.000001
    FileNameHist = os.path.join(PathName, 'histogram_complexes_time.dat')
    histogram_obj = single_hist_obj.SingleHistogram(FileNameHist, FileNum = 1, InitialTime = t, FinalTime = t+TimeStep, SpeciesName = SpeciesName)
    data = histogram_obj.hist_complex_count(ShowFig = False)
    cmplx_sizes = data[0]
    cmplx_count = data[1]
    
    # obtain the list of complex sizes that have non-zero counts and sort them in descending order
    size_list = []
    i = len(cmplx_sizes)-1
    while i >= 0:
        if cmplx_count[i] != 0:
            size_list.append(cmplx_sizes[i])
        i -= 1


    max_complex_size_return = []
    theta_ideal_return = []
    sphere_radius_return = []
    sphere_center_position_return = []
    complex_COM_return = []
    regularization_index_return = []
    SerialNum = 0
    
    # For the specificed ComplexNum of complexes from the greatest size to the least size, fit a sphere and calculate the regularization index
    for m in range(ComplexNum):
        pdb_file_name = os.path.join(PathName, "PDB", str(IterNum)+'.pdb')
        restart_file_name = os.path.join(PathName, "RESTARTS",'restart'+str(IterNum)+'.dat')
        complex_pdb_df, SerialNum = single_restart_to_df(FileNamePdb=pdb_file_name,
                                                         ComplexSizeList=size_list,
                                                         FileNameRestart=restart_file_name,
                                                         SerialNum=SerialNum)
        max_complex_size = len(complex_pdb_df)
        sphere_center_position_candidate = np.zeros((3, 3))
        sphere_radius_candidate = np.zeros((3, 1))

        # Shuffle the dataframe
        complex_pdb_df = complex_pdb_df.sample(frac=1)

        # if the COM number is gearter than 30, then split the COM list into 3 parts and fit 3 spheres
        # if the differences of sphere center coordinates are smaller than 0.1
        # and the |fiited radius - 50| < 0.1 , we consider the fitting as good
        x_list = np.array(complex_pdb_df['x_coord'])
        if(x_list.size > 30):
            partition = [[0, int(len(x_list)/3)], [int(len(x_list)/3),
                                               int(len(x_list)/3*2)], [int(len(x_list)/3*2), -1]]
            for ind, part in enumerate(partition):
                r, cx, cy, cz = fitSphere(np.array(complex_pdb_df['x_coord'][part[0]:part[1]]),
                                          np.array(
                                              complex_pdb_df['y_coord'][part[0]:part[1]]),
                                          np.array(complex_pdb_df['z_coord'][part[0]:part[1]]))
                sphere_center_position_candidate[ind, :] = [cx[0], cy[0], cz[0]]
                sphere_radius_candidate[ind, :] = r
        else:
            r, cx, cy, cz = fitSphere(np.array(complex_pdb_df['x_coord']),
                                      np.array(complex_pdb_df['y_coord']),
                                      np.array(complex_pdb_df['z_coord']))
            for i in range(3):
                sphere_center_position_candidate[i, :] = [cx[0], cy[0], cz[0]]
                sphere_radius_candidate[i, :] = r
        # check sphere radius error. If the error is > 0.1, print a warning
        if sum(abs(np.array(sphere_radius_candidate) - r)) >= 0.1 * 3:
            print("Caution, the radius error is > 0.1! The fitted radii are: \n",
                  sphere_radius_candidate)

        # check sphere center coordinate error. If the error is > 0.1, print a warning
        count = 0
        for i in range(3):
            if abs(sphere_center_position_candidate[0][i] - sphere_center_position_candidate[1][i]) >= 0.1 \
                    and abs(sphere_center_position_candidate[1][i] - sphere_center_position_candidate[2][i]) >= 0.1 \
                    and abs(sphere_center_position_candidate[0][i] - sphere_center_position_candidate[2][i]) >= 0.1:
                count += 1
        if count > 0:
            print("Caution, the center coordinate error is > 0.1! The fitted coordinates are: \n",
                  sphere_center_position_candidate)

        sphere_center_position = np.mean(sphere_center_position_candidate, 0)
        sphere_radius = np.mean(sphere_radius_candidate)

        # calculate the center of mass of the max complex
        complex_COM = [np.mean(complex_pdb_df['x_coord']), np.mean(complex_pdb_df['y_coord']), np.mean(complex_pdb_df['z_coord'])]
        # directional vector that directs from sphere center to complex COM
        dir_vector = complex_COM - sphere_center_position

        # the surface area of a Gag complex is
        S_whole_sphere = 4*np.pi*50**2  # nm^2
        S_per_Gag = S_whole_sphere/3697  # nm^2
        S_max_complex = S_per_Gag*max_complex_size  # nm^2

        # determine the spherical angle corresponding to the ideal complex with surface area S_max_complex
        # A = 2*pi*r^2*(1-cos(theta))
        # max polar angle possible
        theta_ideal = np.arccos(1-S_max_complex/2/np.pi/sphere_radius**2)

        # determine if the monomer on complex is on the ideal cap
        counter = 0
        inside_sphere_cap = []
        outside_sphere_cap = []
        for i in range(max_complex_size):
            monomer_vector = list(
                complex_pdb_df.iloc[i][['x_coord', 'y_coord', 'z_coord']])-sphere_center_position
            monomer_theta = np.arccos(float(np.dot(monomer_vector, dir_vector)/np.linalg.norm(
                monomer_vector.astype(float))/np.linalg.norm(dir_vector.astype(float))))
            if monomer_theta <= theta_ideal:
                counter += 1
                inside_sphere_cap.append(
                    list(complex_pdb_df.iloc[i][['x_coord', 'y_coord', 'z_coord']]))
            else:
                outside_sphere_cap.append(
                    list(complex_pdb_df.iloc[i][['x_coord', 'y_coord', 'z_coord']]))
        regularization_index = counter/max_complex_size

        max_complex_size_return.append(max_complex_size)
        theta_ideal_return.append(theta_ideal)
        sphere_radius_return.append(sphere_radius)
        sphere_center_position_return.append(sphere_center_position)
        complex_COM_return.append(list(complex_COM))
        regularization_index_return.append(regularization_index)

        print("Complex Size: %f \nTheta of the sphere cap: %f \nR of the fitted circle: %f " % (
            max_complex_size, theta_ideal, sphere_radius))
        print('Sphere center coord: ', sphere_center_position)
        print('Sphere cap COM: ', list(complex_COM))
        print("Regularixation index: ", regularization_index)
        if m != ComplexNum-1:
            print(
                '------------------------------------------------------------------------------')
        else:
            print(
                '------------------------------------End---------------------------------------')

    return max_complex_size_return, theta_ideal_return, sphere_radius_return, sphere_center_position_return, complex_COM_return, regularization_index_return