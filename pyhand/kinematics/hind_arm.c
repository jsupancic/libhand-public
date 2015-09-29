/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "hind_arm.h"
#include <math.h>

void hind_arm(double hind_arm_bend, double hind_arm_length, double hind_arm_side, double local_x, double local_y, double local_z, double root_scale, double root_x, double root_y, double root_z, double *out_7742181326631954002) {

   out_7742181326631954002[0] = hind_arm_length*root_scale*cos(hind_arm_bend)*cos(hind_arm_side) + local_x*cos(hind_arm_bend)*cos(hind_arm_side) - local_y*sin(hind_arm_side) + local_z*sin(hind_arm_bend)*cos(hind_arm_side) + root_x;
   out_7742181326631954002[1] = hind_arm_length*root_scale*sin(hind_arm_side)*cos(hind_arm_bend) + local_x*sin(hind_arm_side)*cos(hind_arm_bend) + local_y*cos(hind_arm_side) + local_z*sin(hind_arm_bend)*sin(hind_arm_side) + root_y;
   out_7742181326631954002[2] = -hind_arm_length*root_scale*sin(hind_arm_bend) - local_x*sin(hind_arm_bend) + local_z*cos(hind_arm_bend) + root_z;
   out_7742181326631954002[3] = 1;

}
