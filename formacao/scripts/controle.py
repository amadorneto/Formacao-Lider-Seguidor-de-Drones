#!/usr/bin/env python

import sys
import rospy
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import GetModelState
from geometry_msgs.msg import Pose
import tf

modelname = ''

def quaternion2euler(orientation):
	quaternion = (orientation.x,orientation.y,orientation.z,orientation.w)
	euler = tf.transformations.euler_from_quaternion(quaternion)
	roll = euler[0]
	pitch = euler[1]
	yaw = euler[2]
	return roll, pitch, yaw

def callback(objetivo):
	pub = rospy.Publisher('gazebo/set_model_state', ModelState, queue_size=10)
	rospy.wait_for_service('gazebo/get_model_state')
	
	GetState = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
	selfState = GetState(modelname, 'world')
	

	comando = ModelState()
	comando.pose.position.y = selfState.pose.position.y
	comando.pose.position.z = selfState.pose.position.z
	comando.pose.position.x = selfState.pose.position.x

	comando.pose.orientation.x = selfState.pose.orientation.x
	comando.pose.orientation.y = selfState.pose.orientation.y
	comando.pose.orientation.z = selfState.pose.orientation.z
	comando.pose.orientation.w = selfState.pose.orientation.w

	self_roll, self_pitch, self_yaw = quaternion2euler(selfState.pose.orientation)
	obj_roll, obj_pitch, obj_yaw = quaternion2euler(objetivo.orientation)


	comando.twist.linear.x = 0.5*(objetivo.position.x - selfState.pose.position.x)
	comando.twist.linear.y = 0.5*(objetivo.position.y - selfState.pose.position.y)
	comando.twist.linear.z = 0.5*(objetivo.position.z - selfState.pose.position.z)

	comando.twist.angular.x = 0.25*(obj_roll - self_roll)
	comando.twist.angular.y = 0.25*(obj_pitch - self_pitch)
	comando.twist.angular.z = 0.25*(obj_yaw - self_yaw)

	comando.model_name = modelname
	
	pub.publish(comando)


def controle():

	objetivoMsgs = "objetivo_" + modelname
	rospy.Subscriber(objetivoMsgs, Pose, callback)

	rospy.init_node('controle', anonymous=True)

	rospy.spin()


if __name__ == '__main__':
	if len(sys.argv) == 2:
		modelname = sys.argv[1]
		print 'modelname:' + modelname
	else:
		print "Favor fornecer o nome de um model ativo"
		sys.exit(1)
	try:
		controle()
	except rospy.ROSInterruptException:
		pass
