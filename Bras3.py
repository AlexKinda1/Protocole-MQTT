import paho.mqtt.client as mqtt
import time
from pyniryo import*
from config import BROKER_IP, PORT, TOPIC_CONV3, TOPIC_BRAS2, TOPIC_CONV4

#ned B
robot3 = NiryoRobot("192.168.0.102")
robot3.clear_collision_detected()
color = None
shape = None

sensor_pin_id3 = PinID.DI5
conveyor_id3 = ConveyorID.ID_1

def on_message(client, userdata, msg):
    if msg.topic == TOPIC_CONV3 and msg.payload.decode() == "start":
        print("Bras 3 démarre son convoyeur.")
        activer_convoyeur()
        prise_et_traitement()
        deposer_piece()
        print("Bras 3 a déposé la pièce dans la zone finale.")
        client.publish(TOPIC_BRAS2, "next")  # Dire à Bras 2 de reprendre une nouvelle pièce
        revenir_position_initiale()
        client.publish(TOPIC_CONV4, "start")
    elif msg.topic == TOPIC_CONV3 and msg.payload.decode() == "end":
        client.publish(TOPIC_CONV4, "end")
        robot3.close_connection()

def activer_convoyeur():
    while True:
        robot3.run_conveyor(conveyor_id3, speed=80, direction=ConveyorDirection.FORWARD)
        if robot3.digital_read(sensor_pin_id3) == PinState.LOW:
           robot3.stop_conveyor(conveyor_id3)
           break

    
def prise_et_traitement():
    print("Bras 3 prend la pièce.")
    obj_found, pos_array, shape, color = robot3.detect_object("robot3")
    robot3.move(robot3.get_pose_saved("pose2"))
    robot3.pick(robot3.get_pose_saved("pick2"))
    robot3.move(robot3.get_pose_saved("traitement2"))
    if color == ObjectColor.RED:
        robot3.wait(12)
    if color == ObjectColor.BLUE:
        robot3.wait(6)
    if color == ObjectColor.GREEN:
        robot3.wait(2)
       
def deposer_piece():
    robot3.place(robot3.get_pose_saved("convoyeur4"))
    

def revenir_position_initiale():
    robot3.move(robot3.get_pose_saved("pose2"))
    

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_message = on_message
client.connect(BROKER_IP, PORT, 60)
client.subscribe(TOPIC_CONV3)
client.loop_forever()
