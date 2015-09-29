/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "middle_metacarpal_middle_metacarpal_length_0.h"
#include <math.h>

double middle_metacarpal_middle_metacarpal_length_0(double fore_arm_bend, double fore_arm_side, double hind_arm_bend, double hind_arm_side, double middle_metacarpal_bend, double middle_metacarpal_side, double root_scale) {

   double middle_metacarpal_middle_metacarpal_length_0_result;
   middle_metacarpal_middle_metacarpal_length_0_result = root_scale*((((-sin(fore_arm_side)*sin(hind_arm_side) + cos(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side))*cos(fore_arm_bend) - sin(fore_arm_bend)*sin(hind_arm_bend)*cos(hind_arm_side))*cos(middle_metacarpal_side) + (-sin(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side) - sin(hind_arm_side)*cos(fore_arm_side))*sin(middle_metacarpal_side))*cos(middle_metacarpal_bend) - ((-sin(fore_arm_side)*sin(hind_arm_side) + cos(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side))*sin(fore_arm_bend) + sin(hind_arm_bend)*cos(fore_arm_bend)*cos(hind_arm_side))*sin(middle_metacarpal_bend));
   return middle_metacarpal_middle_metacarpal_length_0_result;

}
