#!/usr/bin/python2.7
import code
import sympy as sp
import numpy as np

def sp2np(An):
    return np.array(np.array(An), np.float)

from sympy import *

def bend_mat_sym():
    return Matrix([
        [cos(symbols('bend')), 0, sin(symbols('bend')), 0],
        [0             , 1, 0             , 0],
        [-sin(symbols('bend')), 0, cos(symbols('bend')), 0],
        [0, 0, 0, 1]])        

def side_mat_sym():
    return Matrix([
        [cos(symbols('side')), -sin(symbols('side')), 0, 0],
        [sin(symbols('side')),  cos(symbols('side')), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])        

def trans_mat_sym():
    T = Matrix([
        [1,0,0,symbols('tx')],
        [0,1,0,symbols('ty')],
        [0,0,1,symbols('tz')],
        [0,0,0,1]])
    return T

# rotation about the unit vector u by theta radians.
def rotation_mat_sym():
    ux = symbols('ux')
    uy = symbols('uy')
    uz = symbols('uz')
    t = symbols('theta')
    
    return Matrix([
        [cos(theta) + ux*ux*(1 - cos(theta)), ux*uy*(1-cos(t))-uz*sin(t), ux*uz*(1-cos(t))+uy*sin(t), 0],
        [uy*ux*(1-cos(t))+uz*sin(t),          cos(t)+uy*uy*(1-cos(t)),    uy*uz*(1-cos(t))-ux*sin(t), 0],
        [uz*ux*(1-cos(t))-uy*sin(t),          uz*uy*(1-cos(t))+ux*sin(t), cos(t)+uz*uz*(1-cos(t)),    0],
        [0,                                   0,                          0,                          1]])

def scale_matrix_sym():
    sx = symbols('sx')
    sy = symbols('sy')
    sz = symbols('sz')
    
    return Matrix([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]])
