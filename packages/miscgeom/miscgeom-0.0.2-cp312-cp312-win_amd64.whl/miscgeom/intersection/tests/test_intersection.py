import numpy as np
import pytest

from miscgeom.intersection import sweptCylinderCurveIntersects, getCylinderMesh


def test_cyl_int():
    # intersecting case
    cyl_ax = np.array([[_x, np.pow(10, _x) / 10, 0] for _x in np.linspace(0, 1, 100)])
    curve = np.array([[0.5, 0.2 + (np.pow(10, _x) / 10), _x - 0.2] for _x in np.linspace(0, 1, 100)])
    d = 0.1
    res = sweptCylinderCurveIntersects(cyl_ax, curve, d)
    assert res == True

    # non-intersecting case
    curve2 = np.array([[0.5, 0.2 + (np.pow(10, _x) / 10), _x - 0.2] for _x in np.linspace(0, 1, 100)]) + 2
    d = 0.1
    res = sweptCylinderCurveIntersects(cyl_ax, curve2, d)
    assert res == False


def test_cyl_mesh():
    cyl_ax = np.array([[_x, np.pow(10, _x) / 10, 0] for _x in np.linspace(0, 1, 100)])
    d = 0.1

    # get mesh for cylinder
    cyl_verts, cyl_faces = getCylinderMesh(cyl_ax, d)

    assert cyl_verts.shape[0] > 0
    assert cyl_faces.shape[0] > 0
