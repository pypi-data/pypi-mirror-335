"""
geometry_utils.py

Contains utility functions for geometric operations, such as rigid transformations,
steric clash checks, or angle computations. These functions can be used in the
ProteinModel or in other scripts that need geometry calculations.
"""

import numpy as np
from Bio import pairwise2
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1
from scipy.spatial import KDTree
from sklearn.cluster import KMeans
import math

def rigid_transform_3d(points_a: np.ndarray, points_b: np.ndarray):
    """
    Computes a rigid transformation (rotation + translation) that aligns
    points_a to points_b using an SVD-based method.

    Args:
        points_a (np.ndarray): Array of shape (N, 3) for the first set of points.
        points_b (np.ndarray): Array of shape (N, 3) for the second set of points.

    Returns:
        (np.ndarray, np.ndarray):
            - R: A 3x3 rotation matrix
            - t: A 3-element translation vector
    """
    assert len(points_a) == len(points_b), "Point sets must be same length."
    centroid_a = points_a[0]
    centroid_b = points_b[0]
    pa = points_a[1:] - centroid_a
    pb = points_b[1:] - centroid_b
    h = pa.T @ pb
    u, s, vt = np.linalg.svd(h)
    r = vt.T @ u.T
    if np.linalg.det(r) < 0:
        vt[-1, :] *= -1
        r = vt.T @ u.T
    t = centroid_b - r @ centroid_a
    return r, t


def apply_rigid_transform(r: np.ndarray, t: np.ndarray, point: np.ndarray):
    """
    Applies a rigid transformation (r, t) to a point.

    Args:
        r (np.ndarray): A 3x3 rotation matrix.
        t (np.ndarray): A translation vector of length 3.
        point (np.ndarray): A point or array of shape (3,) to transform.

    Returns:
        np.ndarray: The transformed point(s).
    """
    return (r @ point.T).T + t


def rigid_transform_chains(chain1, chain2):
    """
    Aligns chain1 to chain2 by:
    1. Extracting their amino-acid sequences,
    2. Aligning them globally,
    3. Grouping matched residues into spatial clusters,
    4. Computing a coarse-grained set of up to four points,
    5. Finding the rigid transformation that aligns chain2 to chain1.

    Args:
        chain1 (Bio.PDB.Chain.Chain): The first chain.
        chain2 (Bio.PDB.Chain.Chain): The second chain.

    Returns:
        (np.ndarray, np.ndarray):
            - R: 3x3 rotation matrix
            - t: translation vector
    """

    # Step 1: Extract sequences from both chains
    def extract_sequence(chain):
        """Extracts the amino acid sequence from a chain."""
        return "".join(seq1(residue.resname) for residue in chain.get_residues() if is_aa(residue))

    sequence1 = extract_sequence(chain1)
    sequence2 = extract_sequence(chain2)

    # Step 2: Find the best overlap between the two sequences using pairwise alignment
    alignments = pairwise2.align.globalxx(sequence1, sequence2)
    best_alignment = alignments[0]

    aligned_seq1 = best_alignment.seqA
    aligned_seq2 = best_alignment.seqB

    # Step 3: Identify matching residue pairs in the aligned sequences
    residue_pairs = []
    idx1, idx2 = 0, 0
    residues1 = [res for res in chain1 if is_aa(res)]
    residues2 = [res for res in chain2 if is_aa(res)]

    for a1, a2 in zip(aligned_seq1, aligned_seq2):
        if a1 == '-' or a2 == '-':
            if a1 != '-':
                idx1 += 1
            if a2 != '-':
                idx2 += 1
            continue
        residue_pairs.append((residues1[idx1]['CA'].coord, residues2[idx2]['CA'].coord))
        idx1 += 1
        idx2 += 1

    # Step 4: Group residues into four spatially groups
    def group_residues(residues, n_groups=4):
        """Groups residues into n_groups based on their spatial proximity."""
        coords = np.array([res for res, _ in residues])
        kmeans = KMeans(n_clusters=n_groups).fit(coords)
        groups = [[] for _ in range(n_groups)]
        for i, label in enumerate(kmeans.labels_):
            groups[label].append(residues[i])
        return groups

    groups = group_residues(residue_pairs)

    # Step 5: Compute the average position of each group and COM
    P = [np.mean([res[0] for res in group], axis=0) for group in groups]
    Q = [np.mean([res[1] for res in group], axis=0) for group in groups]
    P.insert(0, np.mean([res[0] for res in residue_pairs], axis=0))
    Q.insert(0, np.mean([res[1] for res in residue_pairs], axis=0))

    P = np.array(P)
    Q = np.array(Q)

    # Step 6: Apply rigid transformation
    R, t = rigid_transform_3d(P, Q)

    return R, t


def check_steric_clashes(points_1, points_2, cutoff: float = 3.5, number_threshold: int = 2):
    """
    Checks for steric clashes between two sets of points. If more than
    `number_threshold` points are within `cutoff` Angstroms, a clash is flagged.

    Args:
        points_1 (np.ndarray): N x 3 array of coordinates for the first set.
        points_2 (np.ndarray): M x 3 array of coordinates for the second set.
        cutoff (float, optional): Distance threshold in Angstroms. Defaults to 3.5.
        number_threshold (int, optional): Minimum count of close-contact points
            to consider it a clash. Defaults to 2.

    Returns:
        bool: True if a clash is detected, False otherwise.
    """
    tree = KDTree(points_2)
    clashes = tree.query_ball_point(points_1, r=cutoff)
    return any(len(clash) >= number_threshold for clash in clashes)


def _unit_vector(x: np.ndarray, tol=1e-6) -> np.ndarray:
    """
    Safely return the unit vector (normalized) of x.
    If the vector is near zero-length, return a zero vector to avoid NaNs.
    """
    norm_x = np.linalg.norm(x)
    if norm_x < tol:
        return np.zeros(3)
    return x / norm_x


def _triangle_correction(x: float, eps=1e-6) -> float:
    """
    Clamp floating-point x into the range [-1, 1], allowing for slight
    numerical overshoot (e.g., -1.000000001 -> -1.0, etc.).
    Raises ValueError if x is out of range beyond eps tolerance.
    """
    if x < -1 and (x + 1) < -eps:
        raise ValueError(f"{x} is out of range for arccos/arcsin < -1.")
    if x > 1 and (x - 1) > eps:
        raise ValueError(f"{x} is out of range for arccos/arcsin > 1.")
    return max(min(x, 1.0), -1.0)


def calculate_angles(c1, c2, p1, p2, n1, n2):
    """
    Determines angles of the reaction (theta1, theta2, phi1, phi2, omega)
    given coordinates of two molecule COMs (c1, c2), two interface sites (p1, p2),
    and two normal vectors (n1, n2).

    Note: The n1 and n2 in the NERDSS inp file’s reaction list is the internal 
    direction regarding the molecule rotation in the template file. When calculating 
    the binding angles, the n1 and n2 used in the input here should be adjusted to the current molecule rotation.

    Args:
        c1 (np.ndarray): COM of molecule 1.
        c2 (np.ndarray): COM of molecule 2.
        p1 (np.ndarray): Interface site of molecule 1.
        p2 (np.ndarray): Interface site of molecule 2.
        n1 (np.ndarray): Normal vector for molecule 1.
        n2 (np.ndarray): Normal vector for molecule 2.

    Returns:
        tuple: (theta1, theta2, phi1, phi2, omega) in radians.
    """
    v1 = p1 - c1
    v2 = p2 - c2
    sigma1 = p1 - p2
    sigma2 = -sigma1

    if np.dot(v1, sigma1) / (np.linalg.norm(v1) * np.linalg.norm(sigma1)) <= 1:  # prevent float point arithematic rounding errors
        theta1 = np.arccos(
            np.dot(v1, sigma1) / (np.linalg.norm(v1) * np.linalg.norm(sigma1))
        )
    else:
        theta1 = 0

    if np.dot(v2, sigma2) / (np.linalg.norm(v2) * np.linalg.norm(sigma2)) <= 1:   # prevent float point arithematic rounding errors
        theta2 = np.arccos(
            np.dot(v2, sigma2) / (np.linalg.norm(v2) * np.linalg.norm(sigma2))
        )
    else:
        theta2 = 0

    t1 = np.cross(v1, sigma1)
    t2 = np.cross(v1, n1)
    norm_t1 = t1 / np.linalg.norm(t1)
    norm_t2 = t2 / np.linalg.norm(t2)
    if np.dot(norm_t1, norm_t2) <= 1:  # prevent float point arithematic rounding errors
        phi1 = np.arccos(np.dot(norm_t1, norm_t2))
    else:
        phi1 = 0

    # the sign of phi1 is determined by the direction of t2 relative to the right-hand rule of cross product of v1 and t1
    if np.dot(np.cross(v1, t1), t2) > 0:
        phi1 = -phi1

    t1 = np.cross(v2, sigma2)
    t2 = np.cross(v2, n2)
    norm_t1 = t1 / np.linalg.norm(t1)
    norm_t2 = t2 / np.linalg.norm(t2)
    if np.dot(norm_t1, norm_t2) <= 1:   # prevent float point arithematic rounding errors
        phi2 = np.arccos(np.dot(norm_t1, norm_t2))
    else: 
        phi2 = 0

    # the sign of phi2 is determined by the direction of t2 relative to the right-hand rule of cross product of v2 and t1
    if np.dot(np.cross(v2, t1), t2) > 0:
        phi2 = -phi2

    if not np.isclose(np.linalg.norm(np.cross(v1, sigma1)), 0) and not np.isclose(
        np.linalg.norm(np.cross(v2, sigma2)), 0
    ):
        t1 = np.cross(sigma1, v1)
        t2 = np.cross(sigma1, v2)
    else:
        t1 = np.cross(sigma1, n1)
        t2 = np.cross(sigma1, n2)
    

    if np.dot(t1, t2) / (np.linalg.norm(t1) * np.linalg.norm(t2)) <= 1:  # prevent float point arithematic rounding errors
        omega = np.arccos(np.dot(t1, t2) / (np.linalg.norm(t1) * np.linalg.norm(t2)))
    else:
        omega = 0

    # the sign of omega is determined by the direction of t2 relative to the right-hand rule of cross product of sigma1 and t1
    if np.dot(np.cross(sigma1, t1), t2) > 0:
        omega = -omega

    return theta1, theta2, phi1, phi2, omega, n1, n2

def calculate_angles_back(c1, c2, p1, p2, n1, n2, eps=1e-4):
    """
    Determines angles of the reaction (theta1, theta2, phi1, phi2, omega)
    given coordinates of two molecule COMs (c1, c2), two interface sites (p1, p2),
    and two normal vectors (n1, n2).

    Note: The n1 and n2 in the NERDSS inp file’s reaction list is the internal 
    direction regarding the molecule rotation in the template file. When calculating 
    the binding angles, the n1 and n2 used in the input hereshould be adjusted to the current molecule rotation.

    Args:
        c1 (np.ndarray): COM of molecule 1.
        c2 (np.ndarray): COM of molecule 2.
        p1 (np.ndarray): Interface site of molecule 1.
        p2 (np.ndarray): Interface site of molecule 2.
        n1 (np.ndarray): Normal vector for molecule 1.
        n2 (np.ndarray): Normal vector for molecule 2.

    Returns:
        tuple: (theta1, theta2, phi1, phi2, omega) in radians.
    """
    v1 = p1 - c1
    v2 = p2 - c2
    sigma1 = p1 - p2
    sigma2 = -sigma1
    sigma_magnitute = np.linalg.norm(sigma1)
    v1_uni = _unit_vector(v1)
    v2_uni = _unit_vector(v2)
    n1_proj = [n1[0] - v1_uni[0] * np.dot(v1_uni, n1), n1[1] - v1_uni[1] * np.dot(v1_uni, n1), n1[2] - v1_uni[2] * np.dot(v1_uni, n1)]
    sigma1_proj = [sigma1[0] - v1_uni[0] * np.dot(v1_uni, sigma1), sigma1[1] - v1_uni[1] * np.dot(v1_uni, sigma1), sigma1[2] - v1_uni[2] * np.dot(v1_uni, sigma1)]
    n2_proj = [n2[0] - v2_uni[0] * np.dot(v2_uni, n2), n2[1] - v2_uni[1] * np.dot(v2_uni, n2), n2[2] - v2_uni[2] * np.dot(v2_uni, n2)]
    sigma2_proj = [sigma2[0] - v2_uni[0] * np.dot(v2_uni, sigma2), sigma2[1] - v2_uni[1] * np.dot(v2_uni, sigma2), sigma2[2] - v2_uni[2] * np.dot(v2_uni, sigma2)]
    phi1_dir = _unit_vector(np.cross(sigma1_proj, n1_proj))
    phi2_dir = _unit_vector(np.cross(sigma2_proj, n2_proj))
    sigma1_uni = _unit_vector(sigma1)

    theta1 = np.arccos(
        np.dot(v1, sigma1) / (np.linalg.norm(v1) * np.linalg.norm(sigma1))
    )
    theta2 = np.arccos(
        np.dot(v2, sigma2) / (np.linalg.norm(v2) * np.linalg.norm(sigma2))
    )

    t1 = np.cross(v1, sigma1)
    t2 = np.cross(v1, n1)
    norm_t1 = t1 / np.linalg.norm(t1)
    norm_t2 = t2 / np.linalg.norm(t2)
    phi1 = np.arccos(np.dot(norm_t1, norm_t2))

    t1 = np.cross(v2, sigma2)
    t2 = np.cross(v2, n2)
    norm_t1 = t1 / np.linalg.norm(t1)
    norm_t2 = t2 / np.linalg.norm(t2)
    phi2 = np.arccos(np.dot(norm_t1, norm_t2))

    if abs(v1_uni[0] - phi1_dir[0]) < eps:
        phi1 = -phi1
    elif abs(v1_uni[0] + phi1_dir[0]) < eps:
        phi1 = phi1
    else:
        print("Wrong phi1 angle.")
        print(f"v1_uni[0] - phi1_dir[0]: {v1_uni[0] - phi1_dir[0]}")
        print(f"v1_uni[0] + phi1_dir[0]: {v1_uni[0] + phi1_dir[0]}")

    if abs(v2_uni[0] - phi2_dir[0]) < eps:
        phi2 = -phi2
    elif abs(v2_uni[0] + phi2_dir[0]) < eps:
        phi2 = phi2
    else:
        print("Wrong phi2 angle.")
        print(f"v2_uni[0] - phi2_dir[0]: {v2_uni[0] - phi2_dir[0]}")
        print(f"v2_uni[0] + phi2_dir[0]: {v2_uni[0] + phi2_dir[0]}")

    if not np.isclose(np.linalg.norm(np.cross(v1, sigma1)), 0) and not np.isclose(
        np.linalg.norm(np.cross(v2, sigma2)), 0
    ):
        t1 = np.cross(sigma1, v1)
        t2 = np.cross(sigma1, v2)
        v1_proj = [v1[0] - sigma1_uni[0] * np.dot(sigma1_uni, v1), v1[1] - sigma1_uni[1] * np.dot(sigma1_uni, v1), v1[2] - sigma1_uni[2] * np.dot(sigma1_uni, v1)]
        v2_proj = [v2[0] - sigma1_uni[0] * np.dot(sigma1_uni, v2), v2[1] - sigma1_uni[1] * np.dot(sigma1_uni, v2), v2[2] - sigma1_uni[2] * np.dot(sigma1_uni, v2)]
        omega_dir = _unit_vector(np.cross(v1_proj, v2_proj))
    else:
        t1 = np.cross(sigma1, n1)
        t2 = np.cross(sigma1, n2)
        n1_proj = [n1[0] - sigma1_uni[0] * np.dot(sigma1_uni, n1), n1[1] - sigma1_uni[1] * np.dot(sigma1_uni, n1), n1[2] - sigma1_uni[2] * np.dot(sigma1_uni, n1)]
        n2_proj = [n2[0] - sigma1_uni[0] * np.dot(sigma1_uni, n2), n2[1] - sigma1_uni[1] * np.dot(sigma1_uni, n2), n2[2] - sigma1_uni[2] * np.dot(sigma1_uni, n2)]
        omega_dir = _unit_vector(np.cross(n1_proj, n2_proj))

    omega = np.arccos(np.dot(t1, t2) / (np.linalg.norm(t1) * np.linalg.norm(t2)))

    if abs(sigma1_uni[0] - omega_dir[0]) < eps:
        omega = -omega
    elif abs(sigma1_uni[0] + omega_dir[0]) < eps:
        omega = omega
    else:
        print("Wrong omega angle.")
        print(f"sigma1_uni[0] - omega_dir[0]: {sigma1_uni[0] - omega_dir[0]}")
        print(f"sigma1_uni[0] + omega_dir[0]: {sigma1_uni[0] + omega_dir[0]}")

    return theta1, theta2, phi1, phi2, omega, n1, n2


eps = 10**-6
norm = np.linalg.norm

def unit(x:np.ndarray) -> np.ndarray:
    '''Get the unit vector of x\n
    Return 0 if ||x||=0\n
    Return itself if ||x||=1'''
    x_norm = norm(x)
    if abs(x_norm-1) < eps:
        return x
    elif x_norm < eps:
        return np.zeros(3)
    else:
        return x/x_norm


def triangle_correction(x: float) -> float:
    '''make x in range of [-1, 1], correct precision'''
    if x < -1 and abs(x+1) < eps:
        return -1
    elif x > 1 and abs(x-1) < eps:
        return 1
    elif -1 <= x <= 1:
        return x
    else:
        raise ValueError(f'{x} is out of the range of sin/cos')

def calculate_phi(v:np.ndarray, n:np.ndarray, sigma:np.ndarray) -> float:

    # calculate phi
    t1 = unit(np.cross(v, sigma))
    t2 = unit(np.cross(v, n))
    phi = math.acos(triangle_correction(np.dot(t1, t2)))

    # determine the sign of phi (+/-)
    v_uni = unit(v)
    n_proj = n - v_uni * np.dot(v_uni, n)
    sigma_proj = sigma - v_uni * np.dot(v_uni, sigma)
    phi_dir = unit(np.cross(sigma_proj, n_proj))

    if np.dot(v_uni, phi_dir) > 0:
        phi = -phi
    else:
        phi = phi
    
    return phi


def angles(COM1, COM2, int_site1, int_site2, normal_point1, normal_point2):
    '''Calculate the angles for binding
    
    Note: The n1 and n2 in the NERDSS inp file’s reaction list is the internal 
    direction regarding the molecule rotation in the template file. When calculating 
    the binding angles, the n1 and n2 used in the input here should be adjusted to the current molecule rotation.
    '''

    # Convert sequences into arrays for convinience
    COM1 = np.array(COM1)
    COM2 = np.array(COM2)
    int_site1 = np.array(int_site1)
    int_site2 = np.array(int_site2)
    normal_point1 = np.array(normal_point1)
    normal_point2 = np.array(normal_point2)

    # Get Vectors
    v1 = int_site1 - COM1 # from COM to interface (particle 1)
    v2 = int_site2 - COM2  # from COM to interface (particle 2)
    sigma1 = int_site1 - int_site2 # sigma, from p2 to p1
    sigma2 = int_site2 - int_site1  # sigma, from p1 to p2
    n1 = unit(normal_point1 - COM1) # normal vector for p1
    n2 = unit(normal_point2 - COM2) # normal vector for p2

    # Calculate the magnititude of sigma
    sigma_magnitude = norm(sigma1)

    # Calculate theta1 and theta2
    costheta1 = np.dot(v1, sigma1) / norm(v1) / norm(sigma1)
    costheta2 = np.dot(v2, sigma2) / norm(v2) / norm(sigma2)
    theta1 = math.acos(triangle_correction(costheta1))
    theta2 = math.acos(triangle_correction(costheta2))

    # check geometry
    errormsg = ''
    iferror = False # determine if v // n
    if norm(np.cross(n1, v1)) < eps:
        iferror = True
        errormsg += f'\n\tn1 ({n1}) and v1 ({v1}) parallel, phi1 not available'
    if norm(np.cross(n2, v2)) < eps:
        iferror = True
        errormsg += f'\n\tn2 ({n2}) and v2 ({v2}) parallel, phi2 not available'
    if iferror:
        raise ValueError(errormsg)

    # determine if phi1 exists (v1 // sigma1 ?)
    if norm(np.cross(sigma1, v1)) < eps:
        phi1 = float('nan')
        # omega_parallel = True
        omega_t1 = unit(np.cross(sigma1, n1))
    else:
        phi1 = calculate_phi(v1, n1, sigma1)
        omega_t1 = unit(np.cross(sigma1, v1))

    # determine if phi2 exists (v2 // sigma2 ?)
    if norm(np.cross(sigma2, v2)) < eps:
        phi2 = float('nan')
        # omega_parallel = True
        omega_t2 = unit(np.cross(sigma1, n2))
    else:
        phi2 = calculate_phi(v2, n2, sigma2)
        omega_t2 = unit(np.cross(sigma1, v2))

    # calculate omega (both cases are same)
    omega = math.acos(triangle_correction(np.dot(omega_t1, omega_t2)))
    # determine the sign of omega (+/-)
    sigma1_uni = unit(sigma1)
    sigma1xomega_t1 = np.cross(sigma1, omega_t1)
    sigma1xomega_t2 = np.cross(sigma1, omega_t2)
    omega_dir = unit(np.cross(sigma1xomega_t1, sigma1xomega_t2))
    if np.dot(sigma1_uni, omega_dir) > 0:
        omega = -omega
    else:
        omega = omega

    if abs(theta1 - np.pi) < eps:
        theta1 = 'M_PI'
    else:
        theta1 = "%.6f" % theta1
    if abs(theta2 - np.pi) < eps:
        theta2 = 'M_PI'
    else:
        theta2 = "%.6f" % theta2
    if abs(phi1 - np.pi) < eps:
        phi1 = 'M_PI'
    else:
        phi1 = "%.6f" % phi1
    if abs(phi2 - np.pi) < eps:
        phi2 = 'M_PI'
    else:
        phi2 = "%.6f" % phi2
    if abs(omega - np.pi) < eps:
        omega = 'M_PI'
    else:
        omega = "%.6f" % omega

    return theta1, theta2, phi1, phi2, omega, sigma_magnitude
