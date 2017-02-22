#!/usr/bin/env python
import roslib

import rospy
import tf

from geometry_msgs.msg import TransformStamped

from sensor_msgs.msg import PointCloud2

from geometry_msgs.msg import Pose

import argparse

#pcpublisher= rospy.Publisher("points",PointCloud2,queue_size=1)

class RobotPoseTFPublisher:


    def posecallback(self, posemessage):
        self.pose = posemessage
        print self.pose.position.x
        print self.pose.position.y

    def __init__(self, pose_topic):
         self.pose = None
         self.pose_topic = pose_topic
         self.poseproxy = rospy.Subscriber(self.pose_topic,Pose,self.posecallback)
         rospy.loginfo("Subscribed to %s topic",self.pose_topic)



#pcproxy = rospy.Subscriber("/head_xtion/depth/points",PointCloud2,pccallback)



parser = argparse.ArgumentParser()
parser.add_argument("--pose_topic", help="the robot pose topic that the node will subscribe to. Default is robot_pose", default="robot_pose")
args = parser.parse_args(rospy.myargv(argv=sys.argv)[1:])
rospy.init_node("robot_pose_tf_publisher")
rate = rospy.Rate(10)
robotposetfpublisher = RobotPoseTFPublisher(args.pose_topic)
br = tf.TransformBroadcaster()
while not rospy.is_shutdown():


    if robotposetfpublisher.pose:
        # Here i was originally sending tf with position.x, position.y but that was problemmatic. Now i send it as x,y swapped and it semms to be working
        #(robotposetfpublisher.pose.orientation.x, robotposetfpublisher.pose.orientation.y, robotposetfpublisher.pose.orientation.z,robotposetfpublisher.pose.orientation.w)
        br.sendTransform((robotposetfpublisher.pose.position.x, robotposetfpublisher.pose.position.y, robotposetfpublisher.pose.position.z),
                 (robotposetfpublisher.pose.orientation.x, robotposetfpublisher.pose.orientation.y, robotposetfpublisher.pose.orientation.z,robotposetfpublisher.pose.orientation.w),
                 rospy.Time.now(),
                 "base_footprint",
                 "map")


    rate.sleep()
