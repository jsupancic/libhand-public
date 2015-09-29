/******************************************************************************
 *                      Code generated with sympy 0.7.6                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                       This file is part of 'project'                       *
 ******************************************************************************/
#include "pinky_metacarpal_fore_arm_bend_0.h"
#include <math.h>

double pinky_metacarpal_fore_arm_bend_0(double fore_arm_bend, double fore_arm_length, double fore_arm_side, double hind_arm_bend, double hind_arm_side, double local_x, double local_y, double local_z, double pinky_metacarpal_bend, double pinky_metacarpal_length, double pinky_metacarpal_side, double root_scale) {

   double pinky_metacarpal_fore_arm_bend_0_result;
   pinky_metacarpal_fore_arm_bend_0_result = fore_arm_length*root_scale*(-(-sin(fore_arm_side)*sin(hind_arm_side) + cos(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side))*sin(fore_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend)*cos(hind_arm_side)) + local_x*((-(-sin(fore_arm_side)*sin(hind_arm_side) + cos(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side))*sin(fore_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend)*cos(hind_arm_side))*cos(pinky_metacarpal_bend)*cos(pinky_metacarpal_side) - ((-sin(fore_arm_side)*sin(hind_arm_side) + cos(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side))*cos(fore_arm_bend) - sin(fore_arm_bend)*sin(hind_arm_bend)*cos(hind_arm_side))*sin(pinky_metacarpal_bend)) - local_y*(-(-sin(fore_arm_side)*sin(hind_arm_side) + cos(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side))*sin(fore_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend)*cos(hind_arm_side))*sin(pinky_metacarpal_side) + local_z*((-(-sin(fore_arm_side)*sin(hind_arm_side) + cos(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side))*sin(fore_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend)*cos(hind_arm_side))*sin(pinky_metacarpal_bend)*cos(pinky_metacarpal_side) + ((-sin(fore_arm_side)*sin(hind_arm_side) + cos(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side))*cos(fore_arm_bend) - sin(fore_arm_bend)*sin(hind_arm_bend)*cos(hind_arm_side))*cos(pinky_metacarpal_bend)) + pinky_metacarpal_length*root_scale*((-(-sin(fore_arm_side)*sin(hind_arm_side) + cos(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side))*sin(fore_arm_bend) - sin(hind_arm_bend)*cos(fore_arm_bend)*cos(hind_arm_side))*cos(pinky_metacarpal_bend)*cos(pinky_metacarpal_side) - ((-sin(fore_arm_side)*sin(hind_arm_side) + cos(fore_arm_side)*cos(hind_arm_bend)*cos(hind_arm_side))*cos(fore_arm_bend) - sin(fore_arm_bend)*sin(hind_arm_bend)*cos(hind_arm_side))*sin(pinky_metacarpal_bend));
   return pinky_metacarpal_fore_arm_bend_0_result;

}
