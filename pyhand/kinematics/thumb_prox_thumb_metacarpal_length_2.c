/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "thumb_prox_thumb_metacarpal_length_2.h"
#include <math.h>

double thumb_prox_thumb_metacarpal_length_2(double fore_arm_bend, double fore_arm_side, double hind_arm_bend, double root_scale, double thumb_metacarpal_bend, double thumb_metacarpal_side) {

   double thumb_prox_thumb_metacarpal_length_2_result;
   thumb_prox_thumb_metacarpal_length_2_result = root_scale*(((-sin(fore_arm_bend)*cos(hind_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend)*cos(fore_arm_side))*cos(thumb_metacarpal_side) + sin(fore_arm_side)*sin(hind_arm_bend)*sin(thumb_metacarpal_side))*cos(thumb_metacarpal_bend) - (-sin(fore_arm_bend)*sin(hind_arm_bend)*cos(fore_arm_side) + cos(fore_arm_bend)*cos(hind_arm_bend))*sin(thumb_metacarpal_bend));
   return thumb_prox_thumb_metacarpal_length_2_result;

}
