/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "fore_arm_root_scale_2.h"
#include <math.h>

double fore_arm_root_scale_2(double fore_arm_bend, double fore_arm_length, double fore_arm_side, double hind_arm_bend, double hind_arm_length) {

   double fore_arm_root_scale_2_result;
   fore_arm_root_scale_2_result = fore_arm_length*(-sin(fore_arm_bend)*cos(hind_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend)*cos(fore_arm_side)) - hind_arm_length*sin(hind_arm_bend);
   return fore_arm_root_scale_2_result;

}
