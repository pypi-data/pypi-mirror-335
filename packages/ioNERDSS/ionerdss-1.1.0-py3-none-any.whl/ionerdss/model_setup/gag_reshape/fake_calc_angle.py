import numpy as np

def calculateAngles(c1, c2, p1, p2, n1, n2):
        """
        Determine the angles of the reaction (theta1, theta2, phi1, phi2, omega) given the coordinates of the two Center of Mass (c1 and c2) and two reaction sites (p1 and p2), and two norm vectors (n1 and n2).

        Parameters
        ----------
        c1 : numpy.array
            Center of Mass vector for the first molecule.
        c2 : numpy.array
            Center of Mass vector for the second molecule.
        p1 : numpy.array
            Reaction site vector for the first molecule.
        p2 : numpy.array
            Reaction site vector for the second molecule.
        n1 : numpy.array
            Norm vector for the first molecule.
        n2 : numpy.array
            Norm vector for the second molecule.

        Returns
        -------
        tuple
            The tuple (theta1, theta2, phi1, phi2, omega), where theta1, theta2, phi1, phi2, omega are the angles in radians.
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
        if np.abs(omega) < 1.4902e-8:
            omega = 0

        # the sign of omega is determined by the direction of t2 relative to the right-hand rule of cross product of sigma1 and t1
        if np.dot(np.cross(sigma1, t1), t2) > 0:
            omega = -omega

        return np.linalg.norm(sigma1), theta1, theta2, phi1, phi2, omega