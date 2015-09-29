/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "index_dist_fore_arm_length_2.h"
#include <math.h>

double index_dist_fore_arm_length_2(double fore_arm_bend, double fore_arm_side, double hind_arm_bend, double root_scale) {

   double index_dist_fore_arm_length_2_result;
   index_dist_fore_arm_length_2_result = root_scale*(-sin(fore_arm_bend)*cos(hind_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend)*cos(fore_arm_side));
   return index_dist_fore_arm_length_2_result;

}
