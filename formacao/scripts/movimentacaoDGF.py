#!/usr/bin/env python

import sys
import rospy
from std_msgs.msg import String
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import GetModelState
from geometry_msgs.msg import Pose

modelname = ''
alvoname = ''
movX = 1.0
movY = 1.0
movZ = 0.0

def movimentacao():
	objetivoMsgs = "objetivo_" + modelname
	pub = rospy.Publisher(objetivoMsgs, Pose, queue_size=10)
	rospy.init_node('movimentacaoDGF', anonymous=True)
	rate = rospy.Rate(10) # 10hz

	while not rospy.is_shutdown():

		rospy.wait_for_service('gazebo/get_model_state')
		try:
			GetState = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
			alvoState = GetState(alvoname, 'world')
			selfState = GetState(modelname, 'world')
		except rospy.ServiceException, e:
			print "Service call failed: %s"%e

		objetivo = Pose()

		objetivo.position.x = alvoState.pose.position.x + movX
		objetivo.position.y = alvoState.pose.position.y + movY
		objetivo.position.z = alvoState.pose.position.z + movZ

		objetivo.orientation.x = alvoState.pose.orientation.x
		objetivo.orientation.y = alvoState.pose.orientation.y
		objetivo.orientation.z = alvoState.pose.orientation.z
		objetivo.orientation.w = alvoState.pose.orientation.w

		pub.publish(objetivo)

		rate.sleep()

if __name__ == '__main__':
	if len(sys.argv) == 6:
		modelname = sys.argv[1]
		alvoname = sys.argv[2]
		movX = float(sys.argv[3])
		movY = float(sys.argv[4])
		movZ = float(sys.argv[5])
		print 'modelname: ' + modelname
		print 'alvoname: ' + alvoname
	else:
		print "Favor fornecer o nome de um model ativo, o alvo que ele deve seguir e X, Y e Z de Diferenca Global Fixa"
		sys.exit(1)
	try:
		movimentacao()
	except rospy.ROSInterruptException:
		pass
