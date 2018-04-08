#!/usr/bin/env python

import sys
import rospy
from std_msgs.msg import String
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import GetModelState
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Quaternion
from math import sin
from math import cos
import tf

PI = 3.14159265359

modelname = ''
alvoname = ''
relX = 1.0
relY = 1.0
relZ = 0.0
relYaw = 0.0  #Em graus

def quaternion2euler(orientation):
	quaternion = (orientation.x,orientation.y,orientation.z,orientation.w)
	euler = tf.transformations.euler_from_quaternion(quaternion)
	roll = euler[0]
	pitch = euler[1]
	yaw = euler[2]
	return roll, pitch, yaw

def euler2quaternion(roll, pitch, yaw):
	quaternion = tf.transformations.quaternion_from_euler(roll, pitch, yaw)
	orientation = Quaternion()
	orientation.x = quaternion[0]
	orientation.y = quaternion[1]
	orientation.z = quaternion[2]
	orientation.w = quaternion[3]
	return orientation


def movimentacao():
	objetivoMsgs = "objetivo_" + modelname
	pub = rospy.Publisher(objetivoMsgs, Pose, queue_size=10)
	rospy.init_node('movimentacaoDF', anonymous=True)
	rate = rospy.Rate(10) # 10hz

	while not rospy.is_shutdown():

		rospy.wait_for_service('gazebo/get_model_state')
		try:
			GetState = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
			alvoState = GetState(alvoname, 'world')
			selfState = GetState(modelname, 'world')
		except rospy.ServiceException, e:
			print "Service call failed: %s"%e


		alvo_roll, alvo_pitch, alvo_yaw = quaternion2euler(alvoState.pose.orientation)

		obj_yaw = alvo_yaw + (relYaw*PI/180)



		objetivo = Pose()

		seno = sin(alvo_yaw)
		cosseno = cos(alvo_yaw)

		objetivo.position.x = alvoState.pose.position.x + relX * cosseno - relY * seno
		objetivo.position.y = alvoState.pose.position.y + relX * seno + relY * cosseno
		objetivo.position.z = alvoState.pose.position.z + relZ

		objetivo.orientation = euler2quaternion(0, 0, obj_yaw)

		pub.publish(objetivo)

		rate.sleep()

if __name__ == '__main__':
	if len(sys.argv) == 7:
		modelname = sys.argv[1]
		alvoname = sys.argv[2]
		relX = float(sys.argv[3])
		relY = float(sys.argv[4])
		relZ = float(sys.argv[5])
		relYaw = float(sys.argv[6])
		print 'modelname: ' + modelname
		print 'alvoname: ' + alvoname
	else:
		print "Favor fornecer o nome de um model ativo, o alvo que ele deve seguir e X, Y, Z e Yaw relativos"
		sys.exit(1)
	try:
		movimentacao()
	except rospy.ROSInterruptException:
		pass
