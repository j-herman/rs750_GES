#!/usr/bin/env python

import math
import rospy
import tf

from geometry_msgs.msg import Vector3Stamped
from std_msgs.msg import Float64

class SailController(object):
    ''' Simple sail controller
    
    A simple sail controller that uses the measured apparent wind
    and a angle of attach to set the sail position command.

    main_sail_cmd_msg (std_msgs/Float64)
        Angle in radians of main sail from x-axis (ahead)

    fore_sail_cmd_msg (std_msgs/Float64)
        Angle in radians of main fore from x-axis (ahead)
    '''

    def __init__(self):
        # Parameters
        self._sail_attack_angle = math.pi * 10 / 180.
        self._sail_angle_min = math.pi * 10 / 180.
        self._sail_angle_max = math.pi * 90 / 180.

        # Subscribers
        self._app_wind_msg = Vector3Stamped()
        self._app_wind_sub = rospy.Subscriber('/wind/apparent', Vector3Stamped, self._app_wind_cb)

        # Publishers
        self._main_sail_cmd_msg = Float64()
        self._main_sail_pub = rospy.Publisher('main_sail_position/command', Float64, queue_size=10)

        self._fore_sail_cmd_msg = Float64()
        self._fore_sail_pub = rospy.Publisher('fore_sail_position/command', Float64, queue_size=10)


    def update(self, event):
        ''' Callback for the control loop.
        
        Parameters
        ----------
        event : rospy.Timer
            A rospy.Timer event.
        '''

        time = event.current_real

        # Calculate the (apparent) wind incident angle (free-stream velocity)
        # 
        # NOTE: Ignore intra-body frame transforms at this point...
        # 
        wind_vel = self._app_wind_msg.vector 

        wind_speed = math.sqrt(
            wind_vel.x * wind_vel.x
            + wind_vel.y * wind_vel.y
            + wind_vel.z * wind_vel.z)
        
        # For low wind speeds the angle will be noisy. 
        wind_angle = 0.0
        if wind_speed > 0.01:
            # Measure wind angle between (-1 * wind_vel) and positive x-axis
            wind_angle = math.atan2(-wind_vel.y, -wind_vel.x)


        # Set the sail trim
        sail_angle = 0.0
        if wind_angle > 0.0:
            # wind_angle > 0, sail_angle > 0
            sail_angle = wind_angle - self._sail_attack_angle
            
            # Apply bounds
            sail_angle = max(self._sail_angle_min, sail_angle)
            sail_angle = min(self._sail_angle_max, sail_angle)
        else:
            # wind_angle < 0, sail_angle < 0
            sail_angle = wind_angle + self._sail_attack_angle

            # Apply bounds
            sail_angle = min(-self._sail_angle_min, sail_angle)
            sail_angle = max(-self._sail_angle_max, sail_angle)

        self._main_sail_cmd_msg.data = sail_angle
        self._fore_sail_cmd_msg.data = sail_angle

        rospy.loginfo('wind_vel: ({:.2f}, {:.2f}, {:.2f})'.format(wind_vel.x, wind_vel.y, wind_vel.z))
        rospy.loginfo('wind_speed: {:.2f}'.format(wind_speed))
        rospy.loginfo('wind_angle: {:.0f}'.format(self._deg(wind_angle)))
        rospy.loginfo('sail_angle: {:.0f}'.format(self._deg(sail_angle)))

        # Publish the position commands 
        self._main_sail_pub.publish(self._main_sail_cmd_msg)
        self._fore_sail_pub.publish(self._fore_sail_cmd_msg)


    def _app_wind_cb(self, msg):
        '''Capture the current state of the apparent wind'''

        self._app_wind_msg = msg

    def _deg(self, rad):
        return rad * 180 / math.pi


def main():
    '''ROS node for sail trim controller'''

    rospy.init_node('sail_trim_controller')
    rospy.loginfo('Starting sail trim controller')

    # Create the controller
    controller = SailController()

    # Start the control loop
    control_frequency = 10.0
    if rospy.has_param('~control_frequency'):
        control_frequency = rospy.get_param('~control_frequency')

    rospy.loginfo('Starting control loop at {} Hz'.format(control_frequency))
    control_timer = rospy.Timer(
        rospy.Duration(1.0 / control_frequency),
        controller.update)

    # Spin
    rospy.spin()

if __name__ == '__main__':
    main()
