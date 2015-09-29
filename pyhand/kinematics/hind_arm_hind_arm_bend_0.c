/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "hind_arm_hind_arm_bend_0.h"
#include <math.h>

double hind_arm_hind_arm_bend_0(double hind_arm_bend, double hind_arm_length, double hind_arm_side, double local_x, double local_z, double root_scale) {

   double hind_arm_hind_arm_bend_0_result;
   hind_arm_hind_arm_bend_0_result = -hind_arm_length*root_scale*sin(hind_arm_bend)*cos(hind_arm_side) - local_x*sin(hind_arm_bend)*cos(hind_arm_side) + local_z*cos(hind_arm_bend)*cos(hind_arm_side);
   return hind_arm_hind_arm_bend_0_result;

}
