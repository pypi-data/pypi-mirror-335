#pragma once
#include <stdlib.h>
#include <stdio.h>
#include <math.h>


void copyvals(double vec1[], double vec2[]);
void mult(double vec[], double factor);
void divide(double vec[], double factor);
void add(double vec1[], double vec2[], double output[]);
void subtract(double vec1[], double vec2[], double output[]);
void cross(double vec1[], double vec2[], double output[]);
double dot(double vec1[], double vec2[]);
void normalize(double vec[]);
double magnitude(double vec[]);
double distance(double point1[], double point2[]);
int isEqual(double vec1[], double vec2[]);
void matrixMult(double m[3][3], double x[3], double out[3]);
int pointInsidePolygon(double vertices[][2], const int num_vertices, double point[]);


double TOL = 0.000001;  // 10^-6, tolerance for zero approximation in numerical calculations


/*
multiply a 3x3 matrix and a 3x1 column vector, storing output in "out" argument.
out = m @ x
inputs:
    - m: 3x3 double array, the 3x3 matrix to multiply x by
    - x: length 3 double array, the 3x1 column vector
    - out: length 3 double array, to store the output of the multiplication
output:
    - result of multiplication is stored in out
*/
void matrixMult(double m[3][3], double x[3], double out[3]) {
    for (int i = 0; i < 3; i++) {
        double sum = 0;
        for (int j = 0; j < 3; j++) {
            sum += m[i][j] * x[j];
        }
        out[i] = sum;
    }
}


/*
copy the values from vec2 into vec1. effectively, set vec1=vec2, value wise
arguments:
- vec1: the vector to copy vals into, length 3 double array
- vec2: the vector to copy vals from, length 3 double array
*/
void copyvals(double vec1[], double vec2[]) {
    vec1[0] = vec2[0];
    vec1[1] = vec2[1];
    vec1[2] = vec2[2];
}


/*
multiply a vector by a scalar, modifying it in place
arguments:
- vec: length 3 double array
- factor: scalar to multiply the vector by
*/
void mult(double vec[], double factor) {
    vec[0] = vec[0] * factor;
    vec[1] = vec[1] * factor;
    vec[2] = vec[2] * factor;
}


/*
divide a vector by a scalar, modifying it in place
error checking is not done (ie, if factor = 0, problems will arise). consider this before function call
arguments:
- vec: length 3 double array
- factor: scalar to divide the vector by
*/
void divide(double vec[], double factor) {
    vec[0] = vec[0] / factor;
    vec[1] = vec[1] / factor;
    vec[2] = vec[2] / factor;
}


/*
add vec1 and vec2, elementwise (output = vec1 + vec2)
arguments:
- vec1: length 3 double array
- vec2: length 3 double array
- output: length 3 double array, to store the output
*/
void add(double vec1[], double vec2[], double output[]) {
    output[0] = vec1[0] + vec2[0];
    output[1] = vec1[1] + vec2[1];
    output[2] = vec1[2] + vec2[2]; 
}


/*
subtract vec2 from vec1, elementwise (output = vec1 - vec2)
arguments:
- vec1: length 3 double array
- vec2: length 3 double array
- output: length 3 double array, to store the output
*/
void subtract(double vec1[], double vec2[], double output[]) {
    output[0] = vec1[0] - vec2[0];
    output[1] = vec1[1] - vec2[1];
    output[2] = vec1[2] - vec2[2];
}


/*
compute the cross product of two vectors
arguments:
- vec1: length 3 double array
- vec2: length 3 double array
- output: length 3 double array, to store the output
*/
void cross(double vec1[], double vec2[], double output[]) {
    output[0] = vec1[1]*vec2[2] - vec1[2]*vec2[1];
    output[1] = vec1[2]*vec2[0] - vec1[0]*vec2[2];
    output[2] = vec1[0]*vec2[1] - vec1[1]*vec2[0];
}


/*
compute the dot product of two vectors
arguments:
- vec1: length 3 double array
- vec2: length 3 double array
returns:
- double, the dot product of the two vectors
*/
double dot(double vec1[], double vec2[]) {
    return(vec1[0]*vec2[0] + vec1[1]*vec2[1] + vec1[2]*vec2[2]);  // looks bad but should be fast
}


/*
normalize a vector - modify it in place
arguments:
- vec: length 3 double array
*/
void normalize(double vec[]) {
    double length = sqrt(vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2]);
    for (int i = 0; i < 3; i++) {
        vec[i] = vec[i] / length;
    }
}


/*
calculate the magnitude of a vector (length)
arguments:
- vec: length 3 double array
output:
- double, the length of the vector
*/
double magnitude(double vec[]) {
    return sqrt(vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2]);
}


/*
calculate the euclidean distance between two points
arguments:
- point1: length 3 double array, one of the points
- point2: length 3 double array, the other point
returns:
- double, the distance between the two points
*/
double distance(double point1[], double point2[]) {
    return(sqrt(pow(point1[0] - point2[0], 2.0) + pow(point1[1] - point2[1], 2.0) + pow(point1[2] - point2[2], 2.0)));
}


/*
determine if two 3-dimensional vectors are equal, using 10^-6 float approximation
arguments:
- vec1: length 3 double array
- vec2: length 3 double array
returns:
- whether or not the vectors are equal (1 if they are equal, otherwise 0)
*/
int isEqual(double vec1[], double vec2[]) {
    if (fabs(vec1[0] - vec2[0]) < TOL && fabs(vec1[1] - vec2[1]) < TOL && fabs(vec1[2] - vec2[2]) < TOL) {
        return(1);
    } else {
        return(0);
    }
}


/*
return whether a point lies inside a polygon. Considers a point on an edge to not be inside the polygon
more info here: https://www.gorillasun.de/blog/an-algorithm-for-polygon-intersections/#beyond-rectangles-polygon-intersections
inputs:
    - vertices: 2D, n by 2 double array, the sequential vertices along the perimeter of the polygon
    - num_vertices: int, number of vertices of polygon. 'vertices' array should be of length 2*num_vertices
    - point: length 2 double array, the point to consider
output:
    - returns int: 1 if point is inside polygon, otherwise 0
*/
int pointInsidePolygon(double vertices[][2], const int num_vertices, double point[]) {
    int inside = 0;  // bool to track if point is inside
    for (int i = 0; i < num_vertices; i++) {
        int j = (i + 1) % num_vertices;  // "wraps around"
        if (((vertices[i][1] > point[1]) != (vertices[j][1] > point[1])) && (fabs(vertices[j][1] - vertices[i][1]) < TOL)) {  // edge is horizontal, and point lies on edge - consider to intersect (results in point being outside polygon)
            inside = abs(inside - 1);
        } else if (((vertices[i][1] > point[1]) != (vertices[j][1] > point[1])) && (point[0] < ((vertices[j][0] - vertices[i][0])*(point[1]-vertices[i][1])/(vertices[j][1] - vertices[i][1])) + vertices[i][0])) {
            inside = abs(inside - 1);  // if inside was 1, is now 0; if inside was 0, is now 1
        }
    }
    return inside;
}


/*
get the xy region limits of a 2D region defined by a list of points. very simple function
inputs:
- border_points: double[num_border_points][2], the points defining the border of the region
- num_border_points: int, the number of border points in the border_points array
- out: double[4], the array to store the limit values in the format:
    [x_min, x_max, y_min, y_max]
output:
- the region limits are stored in out array
*/
void getXyRegionLimits(double border_points[][2], int num_border_points, double out[4]) {
    double x_min = border_points[0][0];
    double x_max = border_points[0][0];
    double y_min = border_points[0][1];
    double y_max = border_points[0][1];
    for (int i = 0; i < num_border_points; i++) {
        if (border_points[i][0] < x_min) {
            x_min = border_points[i][0];
        }
        if (border_points[i][0] > x_max) {
            x_max = border_points[i][0];
        }
        if (border_points[i][1] < y_min) {
            y_min = border_points[i][1];
        }
        if (border_points[i][1] > y_max) {
            y_max = border_points[i][1];
        }
    }
    out[0] = x_min;
    out[1] = x_max;
    out[2] = y_min;
    out[3] = y_max;
}


/*
copy the xy coordinates from a 3D row-major point array to a
    2D array.
inputs:
- *arr_3D: double[3*num_verts], row-major 3D (x, y, z) point sequence
- arr_2D: double[num_verts][2], the array to store the output points in
- num_verts: int, number of points in the point sequence
output:
- output xy points are stored in arr_2D array
*/
void array3DTo2D(double *arr_3D, double arr_2D[][2], int num_verts) {
    for (int i = 0; i < num_verts; i++) {
        for (int j = 0; j < 2; j++) {
            arr_2D[i][j] = arr_3D[(3*i) + j];
        }
    }
}
