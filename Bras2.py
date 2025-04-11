import paho.mqtt.client as mqtt           # Importation du client MQTT
from pyniryo import *                     # Bibliothèque pour contrôler le robot Niryo
from config import BROKER_IP, PORT, TOPIC_CONV2, TOPIC_BRAS2, TOPIC_CONV3, TOPIC_BRAS1  # Import des paramètres de configuration

# Initialisation du robot 2 avec son adresse IP
robot2 = NiryoRobot("192.168.0.103")
robot2.clear_collision_detected()         # Réinitialise les détections de collision
robot2.move(robot2.get_pose_saved("pose1"))  # Place le robot dans sa position initiale

# Configuration du capteur et du convoyeur utilisés par le robot
sensor_pin_id2 = PinID.DI5
conveyor_id2 = ConveyorID.ID_1

# Variables globales pour stocker la couleur et la forme détectées
color = None
shape = None

# Fonction callback appelée à la réception d'un message MQTT
def on_message(client, userdata, msg):
    if msg.topic == TOPIC_CONV2 and msg.payload.decode() == "start":
        print("Bras 2 démarre son convoyeur.")
        robot2.clear_collision_detected()      # Réinitialise les collisions
        activer_convoyeur()                   
        prise_et_traitement()                 
        deposer_piece()                       
        print("Bras 2 a déposé la pièce sur le convoyeur de Bras 3.")
        client.publish(TOPIC_BRAS1, "next")   # Indique à Bras 1 de continuer
        revenir_position_initiale()           # Revient à la position de départ
        client.publish(TOPIC_CONV3, "start")  # Lance le convoyeur de Bras 3

# Active le convoyeur jusqu'à ce que le capteur détecte une pièce
def activer_convoyeur():
    robot2.run_conveyor(conveyor_id2, speed=80, direction=ConveyorDirection.BACKWARD)
    while True:
        if robot2.digital_read(sensor_pin_id2) == PinState.LOW:  # Si objet détecté
           robot2.stop_conveyor(conveyor_id2)  # Arrête le convoyeur
           break

# Détection, prise et traitement de l'objet selon couleur et forme
def prise_et_traitement():
    print("Bras 2 prend la pièce.")
    obj_found, pos_array, shape, color = robot2.detect_object("robot2")  # Détection de l'objet avec caméra
    robot2.move(robot2.get_pose_saved("pose1"))  
    robot2.pick(robot2.get_pose_saved("pick1"))  # Prend la pièce
    robot2.move(robot2.get_pose_saved("traitement1"))  # Se déplace à la station de traitement

    # Temps d'attente différent selon la couleur et la forme détectées
    if color == ObjectColor.RED and shape == ObjectShape.SQUARE:
        robot2.wait(6)
    if color == ObjectColor.BLUE and shape == ObjectShape.SQUARE:
        robot2.wait(8)
    if color == ObjectColor.GREEN and shape == ObjectShape.SQUARE:
        robot2.wait(4)
    if color == ObjectColor.GREEN and shape == ObjectShape.CIRCLE:
        robot2.wait(2)
    if color == ObjectColor.RED and shape == ObjectShape.CIRCLE:
        robot2.wait(3)
    if color == ObjectColor.BLUE and shape == ObjectShape.CIRCLE:
        robot2.wait(5)

# Dépose la pièce sur le convoyeur 3
def deposer_piece():
    robot2.place(robot2.get_pose_saved("convoyeur3"))

# Replace le bras à sa position initiale
def revenir_position_initiale():
    robot2.move(robot2.get_pose_saved("pose1"))

# Configuration du client MQTT
client = mqtt.Client(protocol=mqtt.MQTTv5)     
client.on_message = on_message                 # Attribution de la fonction de rappel
client.connect(BROKER_IP, PORT, 60)            # Connexion au broker MQTT
client.subscribe(TOPIC_CONV2)                  # Abonnement au sujet envoyé par le convoyeur 2
client.loop_forever()                          # Boucle infinie pour écouter les messages MQTT

"""cd "C:\Program Files\mosquitto"
mosquitto.exe -v
"""
