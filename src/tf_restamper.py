#!/usr/bin/env python
import roslib

import rospy
import tf

from geometry_msgs.msg import TransformStamped

from sensor_msgs.msg import PointCloud2

import argparse

class TFRestamper:


    def tfcallback(self, tfmessage):

        for transf in tfmessage.transforms:
            transf.header.stamp=rospy.Time.now()

        if not self.tfs:
            self.tfs=tfmessage
        else:
            for transf in self.tfs.transforms:
                transf.header.stamp=rospy.Time.now()
                tfmessage.transforms.append(transf)
            self.tfs= tfmessage
        self.tfproxy.unregister()



    def __init__(self, tf_topic):
         self.tfs = []
         self.tf_topic = tf_topic
         self.tfpublisher= rospy.Publisher("tf",tf.msg.tfMessage,queue_size=1)
         self.tfproxy = rospy.Subscriber(self.tf_topic,tf.msg.tfMessage,self.tfcallback)
         rospy.loginfo("Subscribed to %s topic",self.tf_topic)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--tf_topic", nargs=1, help="the tf topic that the node will subscribe to. Default is tf_old", default="tf_old")
    args = parser.parse_args(rospy.myargv(argv=sys.argv)[1:])

    rospy.init_node("tf_restamper")
    rate = rospy.Rate(10)



    tfrestamper = TFRestamper(args.tf_topic)
    while not rospy.is_shutdown():

        if tfrestamper.tfs:
            for transf in tfrestamper.tfs.transforms:
                transf.header.stamp=rospy.Time.now()
            tfrestamper.tfpublisher.publish(tfrestamper.tfs)


        rate.sleep()
