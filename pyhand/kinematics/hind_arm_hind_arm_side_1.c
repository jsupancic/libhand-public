/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "hind_arm_hind_arm_side_1.h"
#include <math.h>

double hind_arm_hind_arm_side_1(double hind_arm_bend, double hind_arm_length, double hind_arm_side, double local_x, double local_y, double local_z, double root_scale) {

   double hind_arm_hind_arm_side_1_result;
   hind_arm_hind_arm_side_1_result = hind_arm_length*root_scale*cos(hind_arm_bend)*cos(hind_arm_side) + local_x*cos(hind_arm_bend)*cos(hind_arm_side) - local_y*sin(hind_arm_side) + local_z*sin(hind_arm_bend)*cos(hind_arm_side);
   return hind_arm_hind_arm_side_1_result;

}
