#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <Python.h>
#include <numpy/arrayobject.h>
#include "cyl_int.c"


/*
Python arguments:
    cyl_ax: numpy.ndarray, shape (N, 3)
    curve: numpy.ndarray, shape (M, 3)
    d: float

Returns:
    bool
*/
static PyObject* cylinderCurveIntersects(PyObject* self, PyObject* args) {
    PyObject* cyl_ax=NULL, *curve=NULL;
    PyArrayObject* cyl_arr=NULL, *curve_arr=NULL;
    double d;

    if (!PyArg_ParseTuple(args, "O!O!d", &PyArray_Type, &cyl_ax,
                                         &PyArray_Type, &curve,
                                         &d)) {
        return NULL;
    }

    cyl_arr = (PyArrayObject*) PyArray_FROM_OTF(cyl_ax, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);
    curve_arr = (PyArrayObject*) PyArray_FROM_OTF(curve, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);

    if (!cyl_arr || !curve_arr) {
        Py_XDECREF(cyl_arr);
        Py_XDECREF(curve_arr);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate memory for numpy arrays.");
        return NULL;
    }

    double* cyl_ax_data = (double*) PyArray_DATA(cyl_arr);
    double* curve_data = (double*) PyArray_DATA(curve_arr);

    int num_cyl_points = PyArray_DIM(cyl_arr, 0);
    int num_curve_points = PyArray_DIM(curve_arr, 0);

    int result = intersectsCylinder(cyl_ax_data, curve_data, num_cyl_points, num_curve_points, d);

    // free memory
    Py_DECREF(cyl_arr);
    Py_DECREF(curve_arr);

    if (result) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyMethodDef methods[] = {
    {"cylinderCurveIntersects", (PyCFunction)cylinderCurveIntersects, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "fast_intersection",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit_fast_intersection(void) {
    import_array();  // Initialize the NumPy C API
    return PyModule_Create(&module);
}
