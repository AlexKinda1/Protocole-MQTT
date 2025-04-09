import paho.mqtt.client as mqtt
import time
from pyniryo import*
from config import BROKER_IP, PORT, TOPIC_CONV3, TOPIC_BRAS3, TOPIC_CONV4

#ned A
robot4 = NiryoRobot("192.168.0.101")
robot4.clear_collision_detected()
color = None
shape = None

sensor_pin_id3 = PinID.DI5
conveyor_id3 = ConveyorID.ID_1

def on_message(client, userdata, msg):
    if msg.topic == TOPIC_CONV4 and msg.payload.decode() == "start":
        print("Bras 3 démarre son convoyeur.")
        activer_convoyeur()
        prise_et_traitement()
        deposer_piece()
        print("Bras 3 a déposé la pièce dans la zone finale.")
        client.publish(TOPIC_BRAS3, "next")  # Dire à Bras 2 de reprendre une nouvelle pièce
        revenir_position_initiale()
    elif msg.topic == TOPIC_CONV4 and msg.payload.decode() == "end":
        robot4.close_connection()

def activer_convoyeur():
    robot4.run_conveyor(conveyor_id3, speed=80, direction=ConveyorDirection.BACKWARD)
    while True:
        if robot4.digital_read(sensor_pin_id3) == PinState.LOW:
           robot4.stop_conveyor(conveyor_id3)
           break

    
def prise_et_traitement():
    print("Bras 4 prend la pièce.")
    obj_found, pos_array, shape, color = robot4.detect_object("robot4")
    robot4.move(robot4.get_pose_saved("pose3"))
    robot4.pick(robot4.get_pose_saved("pick3"))
    robot4.move(robot4.get_pose_saved("traitement3"))
    if color == ObjectColor.RED:
        robot4.wait(10)
    if color == ObjectColor.BLUE:
        robot4.wait(4)
    if color == ObjectColor.GREEN:
        robot4.wait(1)
    

def deposer_piece():
    robot4.place(robot4.get_pose_saved("depot"))
    

def revenir_position_initiale():
    robot4.move(robot4.get_pose_saved("pose3"))
    

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_message = on_message
client.connect(BROKER_IP, PORT, 60)
client.subscribe(TOPIC_CONV4)
client.loop_forever()
