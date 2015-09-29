/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "index_prox_hind_arm_length_1.h"
#include <math.h>

double index_prox_hind_arm_length_1(double hind_arm_bend, double hind_arm_side, double root_scale) {

   double index_prox_hind_arm_length_1_result;
   index_prox_hind_arm_length_1_result = root_scale*sin(hind_arm_side)*cos(hind_arm_bend);
   return index_prox_hind_arm_length_1_result;

}
