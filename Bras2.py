import paho.mqtt.client as mqtt
import time
from pyniryo import *
from config import BROKER_IP, PORT, TOPIC_CONV2, TOPIC_BRAS2, TOPIC_CONV3, TOPIC_BRAS1

#ned C
robot2 = NiryoRobot("192.168.0.103")
robot2.clear_collision_detected()
sensor_pin_id2 = PinID.DI5
conveyor_id2 = ConveyorID.ID_1

color = None
shape = None

def on_message(client, userdata, msg):
    if msg.topic == TOPIC_CONV2 and msg.payload.decode() == "start":
        print("Bras 2 démarre son convoyeur.")
        activer_convoyeur()
        prise_et_traitement()
        deposer_piece()
        print("Bras 2 a déposé la pièce sur le convoyeur de Bras 3.")
        client.publish(TOPIC_BRAS1, "next")   
        revenir_position_initiale()
        client.publish(TOPIC_CONV3, "start")
    elif msg.topic == TOPIC_CONV2 and msg.payload.decode() == "end":
        client.publish(TOPIC_CONV3, "end")
        robot2.close_connection()

def activer_convoyeur():
    robot2.run_conveyor(conveyor_id2, speed=80, direction=ConveyorDirection.BACKWARD)
    while True:
        if robot2.digital_read(sensor_pin_id2) == PinState.LOW:
           robot2.stop_conveyor(conveyor_id2)
           break
    
def prise_et_traitement():
    print("Bras 2 prend la pièce.")
    obj_found, pos_array, shape, color = robot2.detect_object("robot2")
    robot2.move(robot2.get_pose_saved("pose1"))
    robot2.pick(robot2.get_pose_saved("pick1"))
    robot2.move(robot2.get_pose_saved("traitement1"))
    if color == ObjectColor.RED:
        robot2.wait(10)
    if color == ObjectColor.BLUE:
        robot2.wait(7)
    if color == ObjectColor.GREEN:
        robot2.wait(5)

def deposer_piece():
    robot2.place(robot2.get_pose_saved("convoyeur3"))
    
def revenir_position_initiale():
    robot2.move(robot2.get_pose_saved("pose1"))
    

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_message = on_message
client.connect(BROKER_IP, PORT, 60)
client.subscribe(TOPIC_CONV2)
client.loop_forever()

"""cd "C:\Program Files\mosquitto"
mosquitto.exe -v
"""