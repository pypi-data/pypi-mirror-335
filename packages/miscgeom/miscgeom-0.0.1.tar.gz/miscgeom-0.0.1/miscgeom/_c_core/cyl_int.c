#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "utils.c"


int intersectsCylinder(double *cyl_path, double *other_path, int size_cyl, int size_other, double sweep_diameter);
void fourPointNormals(double p0[], double p1[], double p2[], double p3[], double n1[], double n2[]);
int segmentIntersectsCylinder(double p1[], double p2[], double c1[], double c2[], double n1[], double n2[], double d);
double D(double s, double t, double a, double b, double c, double d, double e, double f);
double minDistSegmentLine(double p0[], double p1[], double q0[], double q1[]);
int truncateSegment(double p1[], double p2[], double n1[], double c1[], double n2[], double c2[]);
void intersection(double p1[], double p2[], double n[], double c[], double output[]);


/*
determine if a streamline intersects the bounding cylinder of another streamline. to be used as a port to python
arguments:
- cyl_path: pointer to 1d double array, which in actuality represents an n by 3 array, the points of the streamline to use as the
            central axis to the bounding cylinder
- other_path: pointer to 1d double array, which in actuality represents an m by 3 array, the points of the "other" streamline
              to check for intersection with the bounding cylinder
- size_cyl: int, the number of points in the cylinder streamline array
- size_other: int, the number of points in the "other" streamline array
- sweep_diameter: double, the diameter to use for the swept cylinder
- result: int, where the output of the calculation is stored
output:
- result will be assigned 0 if the streamline doesn't intersect the cylinder, otherwise 1
*/
int intersectsCylinder(double *cyl_path, double *other_path, int size_cyl, int size_other, double sweep_diameter) {
    // creating local copies for easier indexing - if this takes too much time, can try not doing this
    double (*local_cyl_path)[3] = malloc(size_cyl * sizeof(double[3]));
    if (!local_cyl_path) {  // ensure memory allocation was successful
        return -1;
    }
    for (int i = 0; i < size_cyl; i++) {
        for (int j = 0; j < 3; j++) {
            local_cyl_path[i][j] = cyl_path[i*3 + j];
        }
    }

    double (*local_other_path)[3] = malloc(size_other * sizeof(double[3]));
    if (!local_other_path) {  // ensure memory allocation was successful
        return -1;
    }
    for (int i = 0; i < size_other; i++) {
        for (int j = 0; j < 3; j++) {
            local_other_path[i][j] = other_path[i*3 + j];
        }
    }


    // iterating over each segment in the cylinder array
    for (int i = 0; i < size_cyl - 1; i++) {  // with size_cyl # of points, there are size_cyl-1 # of segments
        double p1[3] = {local_cyl_path[i][0], local_cyl_path[i][1], local_cyl_path[i][2]};
        double p2[3] = {local_cyl_path[i+1][0], local_cyl_path[i+1][1], local_cyl_path[i+1][2]};

        // getting normal vectors
        double n1[3];
        double n2[3];
        if (i == 0) {  // first segment, need to "manually" create a point to use for calculating first normal vector
            double p0[3];
            double tmp[3];
            copyvals(tmp, p1);
            mult(tmp, 2);
            subtract(tmp, p2, p0);  // p0 = (2*p1) - p2 = p1 + (p1 - p2), the artificially implanted point
            double p3[3] = {local_cyl_path[2][0], local_cyl_path[2][1], local_cyl_path[2][2]};  // the last point
            fourPointNormals(p0, p1, p2, p3, n1, n2);
        } else if (i == size_cyl - 2) {  // last segment, need to "manually" create the last point for calculating the second normal vector
            double p3[3];
            double tmp[3];
            copyvals(tmp, p2);
            mult(tmp, 2);
            subtract(tmp, p1, p3);  // p3 = (2*p2) - p1 = p2 + (p2 - p1), the artificially created point to get the normal vector
            double p0[3] = {local_cyl_path[size_cyl - 3][0], local_cyl_path[size_cyl - 3][1], local_cyl_path[size_cyl - 3][2]};
            fourPointNormals(p0, p1, p2, p3, n1, n2);
        } else {  // not first or last segment, don't need to artifically create points
            double p0[3] = {local_cyl_path[i-1][0], local_cyl_path[i-1][1], local_cyl_path[i-1][2]};
            double p3[3] = {local_cyl_path[i+2][0], local_cyl_path[i+2][1], local_cyl_path[i+2][2]};
            fourPointNormals(p0, p1, p2, p3, n1, n2);
        }

        for (int j = 0; j < size_other - 1; j++) {  // for every segment of other paths
            double otherp1[3] = {local_other_path[j][0], local_other_path[j][1], local_other_path[j][2]};
            double otherp2[3] = {local_other_path[j+1][0], local_other_path[j+1][1], local_other_path[j+1][2]};
            if (segmentIntersectsCylinder(otherp1, otherp2, p1, p2, n1, n2, sweep_diameter)) {  // the current segments intersects the bounding cylinder
                free(local_cyl_path);
                free(local_other_path);
                return(1);
            }
        }
    }

    // at this point, all of the segment pairs have been checked for intersection, and no intersections have been found
    free(local_cyl_path);
    free(local_other_path);
    return(0);
}


/*
get the normalized outward normal vectors of the inner two points of a four point sequence. In other words,
calculate the bisecting plane between each consecutive segment pair, and return the normalized outward
normal of each bisecting plane
arguments:
- p0: length 3 double array, the first point of the sequence
- p1: length 3 double array, the second point of the sequence
- p2: length 3 double array, the third point of the sequence
- p3: length 3 double array, the fourth point of the sequence
- n1: length 3 double array, to store the output of the first normal vector (eminating outward from p1)
- n2: length 3 double array, to store the output of the second normal vector (eminating outward from p2)
*/
void fourPointNormals(double p0[], double p1[], double p2[], double p3[], double n1[], double n2[]) {
    // calculating the first normal vector
    double tmp1[3];
    double tmp2[3];
    double tmp3[3];
    subtract(p2, p1, tmp1);
    subtract(p0, p1, tmp2);
    cross(tmp1, tmp2, tmp3);  // tmp3 = (p2 - p1) x (p0 - p1)
    if (fabs(tmp3[0]) < TOL && fabs(tmp3[1]) < TOL && fabs(tmp3[2]) < TOL) {  // cross product is zero, so first two segments are parallel
        copyvals(n1, tmp2);  // n1 = p0 - p1
        normalize(n1);  // n1 is in final form
    } else {
        normalize(tmp1);  // tmp1 = (p2 - p1) / ||p2 - p1||
        normalize(tmp2);  // tmp2 = (p0 - p1) / ||p0 - p1||
        add(tmp1, tmp2, tmp3);  // tmp3 is on the bisecting plane (on the same plane as both segments, bisecting them)
        double tmp4[3];
        cross(tmp1, tmp2, tmp4);  // tmp4 is on the bisecting plane, normal to both segments, so also normal to tmp3
        cross(tmp3, tmp4, n1);  // n1 is first normal vector, don't know which way it points yet
        normalize(n1);
        if (dot(n1, tmp1) > 0) {  // n1 is pointing inwards, needs to point outwards
            mult(n1, -1.0);  // flip the way n1 points, now in final form
        }
    }

    // calculating second normal vector
    subtract(p3, p2, tmp1);  // tmp1 = p3 - p2
    subtract(p1, p2, tmp2);  // tmp2 = p1 - p2
    cross(tmp1, tmp2, tmp3);  // tmp3 = (p3 - p2) x (p1 - p2)
    if (fabs(tmp3[0]) < TOL && fabs(tmp3[1]) < TOL && fabs(tmp3[2]) < TOL) {  // segments 2 and 3 are parallel
        copyvals(n2, tmp1);  // n2 = p3 - p2
        normalize(n2);  // n2 is in final form
    } else {
        normalize(tmp1);  // tmp1 = (p3-p2) / ||p3-p2||
        normalize(tmp2);  // tmp2 = (p1-p2) / ||p1-p2||
        add(tmp1, tmp2, tmp3);  // tmp3 is on bisecting plane (on the same plane as both segments, bisecting them)
        double tmp4[3];
        cross(tmp1, tmp2, tmp4);  // tmp4 is on the bisecting plane and normal to both segments, so also normal to tmp3
        cross(tmp3, tmp4, n2);  // n2 is the normal vector of the bisecting plane, don't know which way it points yet
        normalize(n2);
        if (dot(n2, tmp2) > 0) {  // if n2 . normalized(p1 - p2) > 0, the normal vector is pointing inwards. need to flip it
            mult(n2, -1.0);  // n2 is flipped, now in final form
        }
    }
}


/*
determine if the line segment p1--p2 intersects the skew bounding cylinder associated with line segment c1--c2
arguments:
- p1: length 3 double array, the first endpoint of the potentially intersecting line segment
- p2: length 3 double array, the second endpoint of the potentially intersecting line segment
- c1: length 3 double array, the first endpoint of the skew cylinder central axis
- c2: length 3 double array, the second endpoint of the skew cylinder central axis
- n1: length 3 double array, the normal vector of the skew cylinder endcap at c1. must point away from the central axis
- n2: length 3 double array, the normal vector of the skew cylinder endcap at c2. must point away from the central axis
- d: double, the diameter of the skew bounding cylinder
returns:
- int, whether or not the segment p1--p2 intersects the cylinder (1 if intersection, otherwise 0)
*/
int segmentIntersectsCylinder(double p1[], double p2[], double c1[], double c2[], double n1[], double n2[], double d) {
    int outsidePlanes;
    outsidePlanes = truncateSegment(p1, p2, n1, c1, n2, c2);
    if (outsidePlanes) {  // the segment has no component inside the skew cylinder endcaps. cannot intersect the cylinder
        return(0);
    } else {  // the segment p1--p2 has been modified to be confined within the skew cylinder endcaps
        double minDist = minDistSegmentLine(p1, p2, c1, c2);
        if (fabs(minDist - (d/2)) < TOL) {  // min distance is exactly the cylinder radius - segment coincides with cylinder
            return(1);
        } else if (minDist < (d/2)) {  // min distance is less than cylinder radius, so the segment intersects the radius
            return(1);
        } else {  // min distance must be greater than cylinder radius, so no intersection
            return(0);
        }
    }
}


/*
get the value of D(s, t), the squared distance function, at a given (s, t) input
arguments:
- s: double, the s-coordinate to calculate the value of D at
- t: double, the t-coordinate to calculate the value of D at
- a: double, the "a" parameter in the D function definition -> (p1 - p0) . (p1 - p0)
- b: double, the "b" parameter in the D function definition -> (p1 - p0) . (q1 - q0)
- c: double, the "c" parameter in the D function definition -> (q1 - q0) . (q1 - q0)
- d: double, the "d" parameter in the D function definition -> (p1 - p0) . (p0 - q0)
- e: double, the "e" parameter in the D function definition -> (q1 - q0) . (p0 - q0)
- f: double, the "f" parameter in the D function definition -> (p0 - q0) . (p0 - q0)
returns:
- a double the value D(s, t) at given s and t, calculated with given function parameters
*/
double D(double s, double t, double a, double b, double c, double d, double e, double f) {
    return ((a*s*s) - (2.0*b*s*t) + (c*t*t) + (2*d*s) - (2*e*t) + f);
}


/*
get the shortest distance between a finite line segment and an infinite line
arguments:
- p0: length 3 double array, the first point of the finite segment
- p1: length 3 double array, the second point of the finite segment
- q0: length 3 double array, the first defining point of the infinite line
- q1: length 3 double array, the second defining point of the infinite line
returns:
- the minimum distance between the segment and the line, as a double
*/
double minDistSegmentLine(double p0[], double p1[], double q0[], double q1[]) {
    if (isEqual(p0, p1) && isEqual(q0, q1)) {  // just point - point distance
        return(distance(p0, q0));  // without loss of generality, return the distance between p0 and q0
    } else if (isEqual(p0, p1)) {  // point - infinite line case
        double tmp1[3];
        subtract(q1, q0, tmp1);  // tmp1 = q1 - q0
        double tmp2[3];
        subtract(q0, p0, tmp2);  // tmp2 = q0 - p0
        double tmp3[3];
        cross(tmp1, tmp2, tmp3);  // tmp3 = (q1 - q0) x (q0 - p0)
        return(magnitude(tmp3) / magnitude(tmp1));  // return ||(q1-q0) x (q0-p0)|| / ||q1-q0||
    } else if (isEqual(q0, q1)) {  // segment - point case
        // first, need to calculate a, d, and f parameters
        double tmp1[3];
        double tmp2[3];
        subtract(p1, p0, tmp1);
        subtract(p1, p0, tmp2);
        double a = dot(tmp1, tmp2);  // a = (p1 - p0) . (p1 - p0)
        subtract(p0, q0, tmp2);
        double d = dot(tmp1, tmp2);  // d = (p1 - p0) . (p0 - q0)
        subtract(p0, q0, tmp1);
        double f = dot(tmp1, tmp2);  // f = (p0 - q0) . (p0 - q0)
        
        // finding absolute minimum. note, for segment/point case: D(s) = a*(s^2) + 2*d*s + f
        double shat = (-1.0) * d / a;
        if (shat <= 0) {  // min is at s = 0
            return(sqrt(f));
        } else if (shat >= 1) {  // min is at s = 1
            return(sqrt(a + 2*d + f));
        } else {  // min is at shat
            return(sqrt(a*shat*shat + 2*d*shat + f));  // return sqrt of evaluation of D at shat
        }
    } else {
        // first, calculate a-f parameters
        double tmp1[3];
        double tmp2[3];
        subtract(p1, p0, tmp1);
        subtract(p1, p0, tmp2);
        double a = dot(tmp1, tmp2);  // a = (p1 - p0) . (p1 - p0)
        subtract(q1, q0, tmp2);
        double b = dot(tmp1, tmp2);  // b = (p1 - p0) . (q1 - q0)
        subtract(q1, q0, tmp1);
        double c = dot(tmp1, tmp2);  // c = (q1 - q0) . (q1 - q0)
        subtract(p1, p0, tmp1);
        subtract(p0, q0, tmp2);
        double d = dot(tmp1, tmp2);  // d = (p1 - p0) . (p0 - q0)
        subtract(q1, q0, tmp1);
        double e = dot(tmp1, tmp2);  // e = (q1 - q0) . (p0 - q0)
        subtract(p0, q0, tmp1);
        double f = dot(tmp1, tmp2);  // f = (p0 - q0) . (p0 - q0)

        // find and return distance at minimum s, t coords within 0 <= s <= 1
        if (a*c - b*b > 0) {  // not parallel, D is a paraboloid
            double shat = (b*e - c*d) / (a*c - b*b);
            if (shat <= 0) {  // (0, t0 is minimum)
                return(sqrt(D(0, e/c, a, b, c, d, e, f)));  // return sqrt(D(0, t0)), t0 = e/c
            } else if (shat >= 1) {  // (1, t1 is minimum)
                return(sqrt(D(1, (b+e)/c, a, b, c, d, e, f)));  // return sqrt(D(1, t1)), t1 = (b+e) / c
            } else {  // (shat, that) is minimum
                double that = (a*e - b*d) / (a*c - b*b);
                return(sqrt(D(shat, that, a, b, c, d, e, f)));  // return sqrt(D(shat, that))
            }
        } else {  // parallel, D is a parabolic cylinder, level set at Dmin is a line (cannot be horizontal or vertical)
            return(sqrt(D(0, e/c, a, b, c, d, e, f)));  // D(0, t0) = D(1, t1) = Dmin, so just pick t0 arbitrarily            
        }
    }
}


/*
truncate a line segment to be within two planes
plane normals must point towards the "outside" of the region of interest
refer to updated intersection algorithm outline for more in-depth information
arguments:
- p1: length 3 double array, first point of the segment
- p2: length 3 double array, second point of the segment
- n1: length 3 double array, the normal vector of one of the planes
- c1: length 3 double array, a point on the first plane
- n2: length 3 double array, the normal vector of the second plane
- c2: length 3 double array, a point on the second plane
output cases:
    1) if any part of the segment lies within the planes, p1 and p2 will be modified
       such that they are the truncated segment endpoints, with order preserved. 0 is returned
    2) if the segment is entirely outside the planes, then the points are not modified,
       and 1 is returned
*/
int truncateSegment(double p1[], double p2[], double n1[], double c1[], double n2[], double c2[]) {
    double pnew1[3];  // endpoint 1 of truncated segment
    double pnew2[3];  // endpoint 2 of truncated segment
    double tmp_arr[3];  // for tmp calculations
    double tmp_arr2[3];  // for tmp calculations

    cross(n1, n2, tmp_arr);  // tmp_arr = n1 x n2
    subtract(c1, c2, tmp_arr2);  // tmp_arr2 = c1 - c2
    // next if statement: ||n1 x n2|| = 0 and [(c1 - c2) . n1] = 0
    if (fabs(magnitude(tmp_arr)) < TOL && fabs(dot(tmp_arr2, n1)) < TOL) {  // planes are coincident
        intersection(p1, p2, n1, c1, tmp_arr);  // tmp_arr = pint
        if (fabs(tmp_arr[0] + 99.0) < TOL) {  // both points are on plane
            return 0;  // keep original points, and return 0 (both points lie on both planes - shouldn't really happen)
        } else if (fabs(tmp_arr[0] + 9.0) < TOL) {  // no intersection
            return 1;  // no intersection with coincident planes
        } else {  // there is one intersection point
            copyvals(p1, tmp_arr);  // p1 = pint
            copyvals(p2, tmp_arr);  // p2 = pint
            return 0;
        }
    } else {  // planes are not coincident
        intersection(p1, p2, n1, c1, tmp_arr);  // tmp_arr = pint (plane 1 intersection)
        if (fabs(tmp_arr[0] + 99.0) < TOL) {  // both points on plane 1
            copyvals(pnew1, p1);  // pnew1 = p1
            copyvals(pnew2, p2);  // pnew2 = p2
        } else if (fabs(tmp_arr[0] + 9.0) < TOL) {  // no intersection points
            subtract(p1, c1, tmp_arr2);  // tmp_arr2 = p1 - c1
            if (dot(tmp_arr2, n1) < 0) {  // (p1 - c1) . n1 < 0, p1 and p2 both inside plane 1
                copyvals(pnew1, p1);
                copyvals(pnew2, p2);
            } else {  // p1 and p2 both outside plane 1, no truncated segment exists
                return 1;
            }
        } else {  // p1-p2 intersects plane 1 at one point
            subtract(p1, c1, tmp_arr2);  // tmp_arr2 = p1 - c1
            if (dot(tmp_arr2, n1) > 0) {  // (p1 - c1) . n1 > 0, p1 is outside plane 1, p2 is inside
                copyvals(pnew1, tmp_arr);  // pnew1 = pint
                copyvals(pnew2, p2);  // pnew2 = p2
            } else {  // p2 is outside plane 1, p1 is inside
                copyvals(pnew1, p1);  // pnew1 = p1
                copyvals(pnew2, tmp_arr);  // pnew2 = pint
            }
        }

        intersection(pnew1, pnew2, n2, c2, tmp_arr);  // tmp_arr = pint, intersection of semi-truncated segment with plane 2
        if (fabs(tmp_arr[0] + 99.0) < TOL) {  // both points on plane 2
            copyvals(p1, pnew1);  // modify for return
            copyvals(p2, pnew2);  // modify for return
            return 0;
        } else if (fabs(tmp_arr[0] + 9.0) < TOL) {  // no intersection, both pnew1 and pnew2 either inside or outside plane 2
            subtract(pnew1, c2, tmp_arr2);  // tmp_arr2 = pnew1 - c2
            if (dot(tmp_arr2, n2) < 0) {  // (pnew1 - c2) . n2 < 0, both pnew1 and pnew2 inside plane 2
                copyvals(p1, pnew1);  // modify for return
                copyvals(p2, pnew2);  // modify for return
                return 0;
            } else {  // both pnew1 and pnew2 outside plane 2
                return 1;
            }
        } else {  // pnew1--pnew2 intersects plane 2 at one point
            subtract(pnew1, c2, tmp_arr2);  // tmp_arr2 = pnew1 - c2
            if (dot(tmp_arr2, n2) > 0) {  // (pnew1 - c2) . n2 > 0, pnew1 is outside plane 2, pnew2 is inside
                copyvals(p1, tmp_arr);  // modify for return, p1 = pint
                copyvals(p2, pnew2);  // modify for return, p2 = pnew2
                return 0;
            } else {  // pnew2 is outside plane 2, pnew1 is inside
                copyvals(p1, pnew1);  // modify for return, p1 = pnew1
                copyvals(p2, tmp_arr);  // modify for return, p2 = pint
                return 0;
            }
        }
    }
}


/*
determine if the segment defined by p1 and p2 intersects the plane described by normal n and point c
arguments, and calculate the intersection point. makes use of the following article:
    https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
CAVEAT: if both points lie on the plane, p1 is deemed the intersection point
- p1: length 3 double array, the first point of the segment
- p2: length 3 double array, the second point of the segment
- n: length 3 double array, the normal vector of the plane
- c: length 3 double array, a point on the plane
- output: length 3 double array
    output cases:
        1) the segment does not intersect the plane: {-9, -9, -9}
        2) the segment intersects the plane at a unique point: the intersection point
        3) both segment points lie on the plane: {-99, -99, -99}
*/
void intersection(double p1[], double p2[], double n[], double c[], double output[]) {
    double tmp_arr[3];  // for temp calculations
    double tmp;  // for temp calculations

    // checking if either point lies on cylinder
    int p1on = 0;
    int p2on = 0;
    subtract(p1, c, tmp_arr);  // p1 - c
    if (fabs(dot(tmp_arr, n)) < TOL) {  // quasi equals
        p1on = 1;
    }
    subtract(p2, c, tmp_arr);  // p2 - c
    if (fabs(dot(tmp_arr, n)) < TOL) {  // quasi equals
        p2on = 1;
    }

    if (p1on == 1 && p2on == 1) {  // both points on plane
        output[0] = -99;
        output[1] = -99;
        output[2] = -99;
        return;
    } else if (p1on == 1) {  // only p1 on plane
        output[0] = p1[0];
        output[1] = p1[1];
        output[2] = p1[2];
        return;
    } else if (p2on == 1) {  // only p2 on plane
        output[0] = p2[0];
        output[1] = p2[1];
        output[2] = p2[2];
        return;
    }

    // determining if points lie on opposite sides of plane
    subtract(p1, c, tmp_arr);  // tmp_arr = p1 - c
    tmp = dot(n, tmp_arr);  // tmp = n . (p1 - c)
    subtract(p2, c, tmp_arr);  // tmp_arr = p2 - c
    tmp = tmp * dot(n, tmp_arr);  // tmp = [n . (p1 - c)] * [n . (p2 - c)]

    if (tmp > 0) {  // points are on same side of plane
        output[0] = -9;
        output[1] = -9;
        output[2] = -9;
    } else {  // tmp < 0, points are on opposite side of plane
        // bunch of math, check notes for details
        double l1, l2;
        subtract(p1, c, tmp_arr);  // tmp_arr = p1 - c
        l1 = fabs(dot(tmp_arr, n));  // l1 = |(p1 - c) . n|
        subtract(p2, c, tmp_arr);  // tmp_arr = p2 - c
        l2 = fabs(dot(tmp_arr, n));  // l2 = |(p2 - c) . n|
        subtract(p1, p2, tmp_arr);  // tmp_arr = p1 - p2
        mult(tmp_arr, (l2 / (l1 + l2)));  // tmp_arr = (p1 - p2) * (l2 / (l1 + l2))
        add(p2, tmp_arr, output);  // output = p2 + (p1 - p2) * (l2 / (l1 + l2))
    }
}


