#!/usr/bin/env python3

import mission_execution_control as mxc
import rospy
from aerostack_msgs.msg import ListOfBeliefs
import math
import time
qr_codes = []

points = [
 [6.7, 4.5, 0.58], [6.4, 5.5, 0.58], [6.4, 14.4, 0.58] ,[6.4, 14.4, 1.30], [6.4, 5.5, 1.20] , [6.4, 5.5, 1.9], [6.4, 14.4, 1.9], [6, 14.4, 0.65], [6.4, 5.5, 0.65], [10.7, 4.5, 0.65]]

def qr_callback(msg):
  global qr_codes
  index = msg.beliefs.find('code(')
	
  if not index == -1:
    substring = msg.beliefs[index+10:index+12]  

    if not substring.isdigit():
      substring = substring[:-1]

    if qr_codes.count(substring) == 0:
      qr_codes.append(substring)
      print('QR code: {}'.format(substring))


def mission():
  global qr_codes
  print("Starting mission...")
  print("Taking off...")
  mxc.executeTask('TAKE_OFF')
  mxc.startTask('HOVER')
  print("Take off completed...")
  j=0
  rospy.Subscriber("/drone111/all_beliefs", ListOfBeliefs, qr_callback)
  uid = 0
  mxc.startTask('CLEAR_OCCUPANCY_GRID')	
  for j, point in enumerate (points, 0):
      retry = 0
      print("Generating path")
      print (str(point))
      if (j == 4 or j == 6 or j == 8):
	time.sleep(5)
        mxc.startTask('CLEAR_OCCUPANCY_GRID')
      exit_code = 3	  
      while (retry == 0 or exit_code == 3):
	if (j == 3 or j == 5 or j == 7):
		exit_code = mxc.executeTask('FOLLOW_PATH', path=[points[j-1],points[j]])[1]
		retry = 1		
	else:
		traject = mxc.executeTask('GENERATE_PATH', destination=point)
        	query = "path(?x,?y)"
      		success , unification = mxc.queryBelief(query)
      		print (query)
      		print (success)
      		if success:
			x = str(unification['x'])
			y = str(unification['y'])
			predicate_path = "path(" + x + "," + y + ")"
			mxc.removeBelief(predicate_path)
			predicate_object = "object(" + x + ", path)"
			mxc.removeBelief(predicate_object)
           		traject = eval(unification['y'])
           		traject = [[b for b in a ]for a in traject]
           		i=0
	   		print ("Moving to"+str(traject[len(traject)-1]))
           		print len(traject)
           		print ("Following path")
           		print ("---------------------------------")
           		exit_code = mxc.executeTask('FOLLOW_PATH', path=traject)[1]
	   		retry = 1
        	else:
           		print("next iteration")
	   		mxc.startTask('CLEAR_OCCUPANCY_GRID')
		if (j == 1):
	   		mxc.startTask('PAY_ATTENTION_TO_QR_CODES')


  #print(qr_codes)
  print('-> Total QR codes detected: {}'.format(len(qr_codes)))
  result = mxc.executeTask('LAND')
  print('-> result {}'.format(traject))
  print('Finish mission...')
