import paho.mqtt.client as mqtt
import time
from pyniryo import *
from config import BROKER_IP, PORT, TOPIC_BRAS1, TOPIC_CONV2

robot1 = NiryoRobot('192.168.0.104')
robot1.clear_collision_detected()
color = None
shape = None

def on_message(client, userdata, msg):
    if msg.topic == TOPIC_BRAS1 and msg.payload.decode() == "next":
        print("Bras 1 reprend une nouvelle pièce.")
        prendre_piece()
        deposer_piece()
        print("Bras 1 a déposé la pièce sur le convoyeur de Bras 2.")
        client.publish(TOPIC_CONV2, "start")  # Dire à Bras 2 de démarrer son convoyeur
        revenir_position_initiale()

def prendre_piece():
    print("Bras 1 prend une pièce.")
    robot1.move(robot1.get_pose_saved("pose"))
    obj_found, shape_ret, color_ret = robot1.vision_pick("robot1")

def deposer_piece():
    print("Bras 1 dépose la pièce sur le convoyeur de Bras 2.")
    robot1.place(robot1.get_pose_saved("convoyeur2"))
    

def revenir_position_initiale():
    print("Bras 1 revient à sa position initiale.")
    robot1.move(robot1.get_pose_saved("pose"))

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_message = on_message
client.connect(BROKER_IP, PORT, 60)
client.subscribe(TOPIC_BRAS1)
  
# 🔥 Démarrage automatique de la première tâche de Bras 1 🔥
print("Démarrage du processus avec Bras 1.")
prendre_piece()
deposer_piece()
print("Bras 1 a déposé la première pièce sur le convoyeur de Bras 2.")
client.publish(TOPIC_CONV2, "start")  # Dire à Bras 2 de commencer son travail
revenir_position_initiale()

client.loop_forever()  # Attend les prochains messages pour continuer le cycle
