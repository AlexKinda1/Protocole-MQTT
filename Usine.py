from pyniryo import *

robot = NiryoRobot("192.168.0.102")
robot.update_tool()

default_pose = robot.get_pose()
nom_pos = "pose3"
robot.save_pose(nom_pos,default_pose)
print(nom_pos,"saved:", default_pose)

"""from pyniryo import *

# Connexion au robot
robot = NiryoRobot("192.168.0.101")

# Mise à jour de l'outil
robot.calibrate_auto()"""