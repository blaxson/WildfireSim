from random import randint
from math import atan2 # for computing polar angle

''' returns the polar angle (in radians) from p1 to p2,
    if p2 is None, defaults to replacing with starting point '''
def polar_angle(p1, p2=None):
    if p2 is None:
        p2 = starting_point
    y_span = p1.y - p2.y
    x_span = p1.x - p2.x
    return atan2(y_span,x_span)

''' returns distance from p1 to p2,
    if p2 is None, default to replacing with starting point '''
def distance(p1, p2=None):
    if p2 is None: 
        p2 = starting_point
    y_span = p1.y - p2.y
    x_span = p1.x - p2.x
    return y_span**2 + x_span**2

''' returns determinant of the 3x3 matrix,
    if > 0 then ccw
    if < 0 then cw
    if = 0 then collinear '''
def determinant(p1, p2, p3):
	return (p2.x - p1.x) * (p3.y - p1.y) \
		 - (p2.y - p1.y) * (p3.x - p1.x)

''' sorts in order of increasing polar angle from starting point,
    for values with equal polar angles, sort by distance from starting point '''
def quicksort(a):
    if len(a) <= 1: 
        return a
    smaller,equal,larger = [],[],[]
    rand_idx = randint(0, len(a) - 1)
    piv_angle = polar_angle(a[rand_idx]) # select random pivot
    for point in a:
        point_angle = polar_angle(point) # calculate current point angle
        if point_angle < piv_angle:  
            smaller.append(point)
        elif point_angle == piv_angle: 
            equal.append(point)
        else:
            larger.append(point)
    return quicksort(smaller) \
		 + sorted(equal,key=distance) \
		 + quicksort(larger)

''' returns the points comprising the boundaries of convex hull
    input is list of point objects'''
def get_perimeter(points):
    global starting_point # to be set w/ point w/ smallest y val

    # find point with lowest y val, and its index in list
    min_idx = None
    for i, point in enumerate(points):
        if min_idx == None or point.y < points[min_idx].y:
            min_idx=i 
        if point.y == points[min_idx].y and point.x < points[min_idx].x:
            min_idx=i
    
    # set global var 'starting_point', used by polar_angle() and distance()
    starting_point = points[min_idx]
	# sort points by polar angle then removing starting_point
    sorted_points = quicksort(points)
    del sorted_points[sorted_points.index(starting_point)]

	# starting_point and point with smallest polar angle will always be on perimeter
    perimeter = [starting_point, sorted_points[0]]
    for s in sorted_points[1:]:
        while determinant(perimeter[-2], perimeter[-1], s) < 0:
            del perimeter[-1] # backtrack
			#if len(hull)<2: break
        perimeter.append(s)
    return perimeter
