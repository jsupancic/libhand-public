/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "middle_inter_fore_arm_length_1.h"
#include <math.h>

double middle_inter_fore_arm_length_1(double fore_arm_bend, double fore_arm_side, double hind_arm_bend, double hind_arm_side, double root_scale) {

   double middle_inter_fore_arm_length_1_result;
   middle_inter_fore_arm_length_1_result = root_scale*((sin(fore_arm_side)*cos(hind_arm_side) + sin(hind_arm_side)*cos(fore_arm_side)*cos(hind_arm_bend))*cos(fore_arm_bend) - sin(fore_arm_bend)*sin(hind_arm_bend)*sin(hind_arm_side));
   return middle_inter_fore_arm_length_1_result;

}
