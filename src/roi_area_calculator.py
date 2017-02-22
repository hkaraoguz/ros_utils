#!/usr/bin/env python
import numpy as np
import rospy
from scipy.spatial import ConvexHull
from geometry_msgs.msg import PoseArray
from geometry_msgs.msg import Pose
from soma_msgs.msg import SOMAROIObject
from ros_utils.srv import *
from ros_utils.msg import ROIArea
import argparse

class ROIAreaCalculator:

    def calculateCB(self,msg):
        roias = []
        for roi in msg.rois:
            vertices = []
            for apose in roi.posearray.poses:
                vertices.append([apose.position.x,apose.position.y])
            hull = ConvexHull(vertices)
            roia = ROIArea()
            roia.id = roi.id
            roia.config = roi.config
            roia.area = hull.volume
            roias.append(roia)
        return CalculateROIAreaResponse(roias)


    def __init__(self):
        s = rospy.Service('calculate_roi_area', CalculateROIArea, self.calculateCB)


if __name__ == '__main__':

    #parser = argparse.ArgumentParser()
    #parser.add_argument("--tf_topic", nargs=1, help="the tf topic that the node will subscribe to. Default is tf_old", default="tf_old")
    #args = parser.parse_args(rospy.myargv(argv=sys.argv)[1:])

    rospy.init_node('roi_area_calculator_node')

    obj = ROIAreaCalculator()

    print "Ready to calculate the ROI area..."

    rospy.spin()
