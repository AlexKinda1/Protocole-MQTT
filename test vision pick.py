import paho.mqtt.client as mqtt
import time
from pyniryo import*


#ned B
robot4 = NiryoRobot("192.168.0.101")
robot4.clear_collision_detected()
#robot4.calibrate_auto()

robot4.move(robot4.get_pose_saved("pose3"))
obj_found, shape_ret, color_ret = robot4.vision_pick("robot4")