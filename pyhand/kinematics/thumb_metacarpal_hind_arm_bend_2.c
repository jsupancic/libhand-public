/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "thumb_metacarpal_hind_arm_bend_2.h"
#include <math.h>

double thumb_metacarpal_hind_arm_bend_2(double fore_arm_bend, double fore_arm_length, double fore_arm_side, double hind_arm_bend, double hind_arm_length, double local_x, double local_y, double local_z, double root_scale, double thumb_metacarpal_bend, double thumb_metacarpal_length, double thumb_metacarpal_side) {

   double thumb_metacarpal_hind_arm_bend_2_result;
   thumb_metacarpal_hind_arm_bend_2_result = fore_arm_length*root_scale*(sin(fore_arm_bend)*sin(hind_arm_bend) - cos(fore_arm_bend)*cos(fore_arm_side)*cos(hind_arm_bend)) - hind_arm_length*root_scale*cos(hind_arm_bend) + local_x*(((sin(fore_arm_bend)*sin(hind_arm_bend) - cos(fore_arm_bend)*cos(fore_arm_side)*cos(hind_arm_bend))*cos(thumb_metacarpal_side) + sin(fore_arm_side)*sin(thumb_metacarpal_side)*cos(hind_arm_bend))*cos(thumb_metacarpal_bend) - (-sin(fore_arm_bend)*cos(fore_arm_side)*cos(hind_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend))*sin(thumb_metacarpal_bend)) + local_y*(-(sin(fore_arm_bend)*sin(hind_arm_bend) - cos(fore_arm_bend)*cos(fore_arm_side)*cos(hind_arm_bend))*sin(thumb_metacarpal_side) + sin(fore_arm_side)*cos(hind_arm_bend)*cos(thumb_metacarpal_side)) + local_z*(((sin(fore_arm_bend)*sin(hind_arm_bend) - cos(fore_arm_bend)*cos(fore_arm_side)*cos(hind_arm_bend))*cos(thumb_metacarpal_side) + sin(fore_arm_side)*sin(thumb_metacarpal_side)*cos(hind_arm_bend))*sin(thumb_metacarpal_bend) + (-sin(fore_arm_bend)*cos(fore_arm_side)*cos(hind_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend))*cos(thumb_metacarpal_bend)) + root_scale*thumb_metacarpal_length*(((sin(fore_arm_bend)*sin(hind_arm_bend) - cos(fore_arm_bend)*cos(fore_arm_side)*cos(hind_arm_bend))*cos(thumb_metacarpal_side) + sin(fore_arm_side)*sin(thumb_metacarpal_side)*cos(hind_arm_bend))*cos(thumb_metacarpal_bend) - (-sin(fore_arm_bend)*cos(fore_arm_side)*cos(hind_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend))*sin(thumb_metacarpal_bend));
   return thumb_metacarpal_hind_arm_bend_2_result;

}
