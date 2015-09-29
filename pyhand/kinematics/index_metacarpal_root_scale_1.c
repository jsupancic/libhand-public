/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "index_metacarpal_root_scale_1.h"
#include <math.h>

double index_metacarpal_root_scale_1(double fore_arm_bend, double fore_arm_length, double fore_arm_side, double hind_arm_bend, double hind_arm_length, double hind_arm_side, double index_metacarpal_bend, double index_metacarpal_length, double index_metacarpal_side) {

   double index_metacarpal_root_scale_1_result;
   index_metacarpal_root_scale_1_result = fore_arm_length*((sin(fore_arm_side)*cos(hind_arm_side) + sin(hind_arm_side)*cos(fore_arm_side)*cos(hind_arm_bend))*cos(fore_arm_bend) - sin(fore_arm_bend)*sin(hind_arm_bend)*sin(hind_arm_side)) + hind_arm_length*sin(hind_arm_side)*cos(hind_arm_bend) + index_metacarpal_length*((((sin(fore_arm_side)*cos(hind_arm_side) + sin(hind_arm_side)*cos(fore_arm_side)*cos(hind_arm_bend))*cos(fore_arm_bend) - sin(fore_arm_bend)*sin(hind_arm_bend)*sin(hind_arm_side))*cos(index_metacarpal_side) + (-sin(fore_arm_side)*sin(hind_arm_side)*cos(hind_arm_bend) + cos(fore_arm_side)*cos(hind_arm_side))*sin(index_metacarpal_side))*cos(index_metacarpal_bend) - ((sin(fore_arm_side)*cos(hind_arm_side) + sin(hind_arm_side)*cos(fore_arm_side)*cos(hind_arm_bend))*sin(fore_arm_bend) + sin(hind_arm_bend)*sin(hind_arm_side)*cos(fore_arm_bend))*sin(index_metacarpal_bend));
   return index_metacarpal_root_scale_1_result;

}
