import copy
import numpy as np
from . import fast_intersection


def sweptCylinderCurveIntersects(cyl_ax, curve, d):
    """Determines if a 3D swept cylinder intersects a 3D curve. Cylinder is defined by the
    central axis 'cyl_ax' and the diameter 'd'. Curve is defined by a list of 3D points.

    Parameters
    ----------
    cyl_ax : numpy.ndarray
        An array of shape (N, 3) representing the central axis of the cylinder.
    curve : numpy.ndarray
        An array of shape (M, 3) representing the curve to intersect with the cylinder.
    d : float
        The diameter of the cylinder.

    Returns
    -------
    bool
        True if any part of the curve intersects the cylinder, False otherwise.
    """

    cyl_ax_c = np.array(copy.deepcopy(cyl_ax), dtype=np.float64, order='C')
    curve_c = np.array(copy.deepcopy(curve), dtype=np.float64, order='C')

    return fast_intersection.cylinderCurveIntersects(cyl_ax_c, curve_c, d)


def _circlesMisaligned(c1, c2):
    """
    given two circles, determine if "winding" direction is the same.
    inputs:
    - c1: n by 3 numpy array, point sequence for circle 1
    - c2: n by 3 numpy array, point sequence for circle 2
    output:
    - True if the circles have different winding directions, otherwise False if they have the same winding direction
    """

    total_wirelength = 0
    total_wirelength_flipped = 0
    second_inds_flipped = [0] + list(np.flip(list(range(1, len(c1)))))
    for i in range(len(c1)):
        total_wirelength += np.linalg.norm(c1[i] - c2[i])
        total_wirelength_flipped += np.linalg.norm(c1[i] - c2[second_inds_flipped[i]])
    
    if total_wirelength_flipped < total_wirelength:  # need to flip one of the circles
        return True
    else:
        return False


def _circlePoints(n, c, r, num_sample_points):
    """
    given a circle in 3d defined by a point, normal, and radius, get an array of sampled points along the circle
    inputs:
    - n: length 3 numpy array, normal vector for the circle
    - c: length 3 numpy array, the center point of the circle
    - r: float/int, the radius of the circle
    - num_sample_points: int, number of sample points to take along the circle
    output:
    - returns num_sample_points by 3 array, the list of sample points along the circle. The first point is guaranteed to be the lowest
        on the circle, as long as the given normal vector points up
    """

    nhat = copy.deepcopy(n) / np.linalg.norm(n)
    vhat = np.cross(nhat, np.array([0, 0, 1])) / np.linalg.norm(np.cross(nhat, np.array([0, 0, 1])))
    uhat = np.cross(vhat, nhat)

    ret_points = np.zeros((num_sample_points, 3))
    theta_step = (2*np.pi) / num_sample_points
    for i in range(num_sample_points):
        theta = i*theta_step
        ret_points[i, :] = c + (r*np.cos(theta)*uhat) + (r*np.sin(theta)*vhat)

    return ret_points


def getCylinderMesh(cyl_ax, d, circ_sample_points=16, inc_endcaps=True):
    """Get a mesh representation of a swept cylinder.

    Parameters
    ----------
    cyl_ax : numpy.ndarray
        An array of shape (N, 3) representing the central axis of the cylinder.
    d : float
        The diameter of the cylinder.
    circ_sample_points : int, optional
        The number of points to sample around the circumference of the cylinder.
    inc_endcaps : bool, optional
        Whether to include endcaps in the mesh.

    Returns
    -------
    numpy.ndarray, numpy.ndarray
        Two arrays representing the vertices and faces of the cylinder mesh.
    """


    verts = np.zeros((len(cyl_ax)*circ_sample_points, 3))
    for i in range(len(cyl_ax)):  # getting vertices for print line
        c = cyl_ax[i]

        n = None  # getting normal vector for circle
        if i == 0:  # first point
            n = (cyl_ax[1] - c) / np.linalg.norm(cyl_ax[1] - c)
        elif i == (len(cyl_ax) - 1):  # last point
            n = (c - cyl_ax[-2]) / np.linalg.norm(c - cyl_ax[-2])
        else:
            bisect = ((cyl_ax[i+1] - c) / np.linalg.norm(cyl_ax[i+1] - c)) + ((cyl_ax[i-1] - c) / np.linalg.norm(cyl_ax[i-1] - c))
            if np.abs(np.linalg.norm(bisect)) < 0.000001:  # segments are parallel, just use one of segments as normal
                n = (cyl_ax[i+1] - c) / np.linalg.norm(cyl_ax[i+1] - c)
            else:
                bisect = bisect / np.linalg.norm(bisect)  # bisecting both adjacent segments
                perp = np.cross(cyl_ax[i+1] - c, cyl_ax[i-1] - c)
                perp = perp / np.linalg.norm(perp)  # perp to both adjacent segments
                n = np.cross(perp, bisect)
        
        if n[2] < 0:  # flip normal if pointing down
            n = -1 * n
        
        circ_points = _circlePoints(n, c, d/2, circ_sample_points)
        if i > 0:  # ensuring winding direction for all circles after the first
            circ_points_prev = verts[circ_sample_points*(i-1):circ_sample_points*i, :]  # points of last circle
            if _circlesMisaligned(circ_points_prev, circ_points):
                circ_points[1:, :] = np.flip(circ_points[1:, :], axis=0)
        
        verts[(circ_sample_points*i):(circ_sample_points*(i+1)), :] = circ_points
    
    # getting faces (indices of vertices)
    faces = np.zeros((2*(circ_sample_points-2) + (len(cyl_ax)-1)*2*circ_sample_points, 3))
    ind = 0

    if inc_endcaps:
        i = 0
        j = circ_sample_points - 1
        for x in range(circ_sample_points - 2):  # endcaps
            if x % 2 == 0:
                faces[ind, :] = [circ_sample_points*0 + i, circ_sample_points*0 + j, circ_sample_points*0 + j-1]
                ind += 1
                faces[ind, :] = [circ_sample_points*(len(cyl_ax) - 1) + i, circ_sample_points*(len(cyl_ax) - 1) + j, circ_sample_points*(len(cyl_ax) - 1) + j - 1]
                ind += 1
                j -= 1
            else:
                faces[ind, :] = [circ_sample_points*0 + i, circ_sample_points*0 + i + 1, circ_sample_points*0 + j]
                ind += 1
                faces[ind, :] = [circ_sample_points*(len(cyl_ax) - 1) + i, circ_sample_points*(len(cyl_ax) - 1) + i + 1, circ_sample_points*(len(cyl_ax) - 1) + j]
                ind += 1
                i += 1

    for i in range(0, len(cyl_ax) - 1):  # for every segment
        c1 = list(range(circ_sample_points*i, circ_sample_points*(i+1)))  # circle 1 indices
        c2 = list(range(circ_sample_points*(i+1), circ_sample_points*(i+2)))  # circle 2 indices

        for j in range(circ_sample_points):
            k = (j + 1) % circ_sample_points
            faces[ind, :] = [c1[j], c1[k], c2[j]]
            ind += 1
            faces[ind, :] = [c1[k], c2[j], c2[k]]
            ind += 1
    
    return verts, faces
