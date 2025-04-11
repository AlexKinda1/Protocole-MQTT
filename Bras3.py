import paho.mqtt.client as mqtt           # Bibliothèque pour la communication MQTT
from pyniryo import*                      # Contrôle du robot Niryo
from config import BROKER_IP, PORT, TOPIC_CONV3, TOPIC_BRAS2, TOPIC_CONV4  # Paramètres du broker MQTT et des topics

# Initialisation du robot 3 avec son adresse IP
robot3 = NiryoRobot("192.168.0.102")
robot3.clear_collision_detected()             # Nettoie les éventuelles détections de collision
robot3.move(robot3.get_pose_saved("pose2"))   # Positionne le bras en position initiale

# Détecteur infra et convoyeur utilisés
sensor_pin_id3 = PinID.DI5
conveyor_id3 = ConveyorID.ID_1

# Variables globales pour stocker les informations sur la pièce
color = None
shape = None

# Fonction déclenchée à la réception d’un message MQTT
def on_message(client, userdata, msg):
    if msg.topic == TOPIC_CONV3 and msg.payload.decode() == "start":
        print("Bras 3 démarre son convoyeur.")
        robot3.clear_collision_detected()        # Réinitialisation des collisions
        activer_convoyeur()                     
        prise_et_traitement()                   
        deposer_piece()                         
        print("Bras 3 a déposé la pièce dans la zone finale.")
        client.publish(TOPIC_BRAS2, "next")     # Signale au bras 2 qu’il peut continuer
        revenir_position_initiale()             # Retour à la position initiale
        client.publish(TOPIC_CONV4, "start")    # Signal au bras 4 de démarrer son convoyeur (TOPIC_CONV4)

# Active le convoyeur jusqu'à ce qu’un objet soit détecté par le capteur
def activer_convoyeur():
    while True:
        robot3.run_conveyor(conveyor_id3, speed=80, direction=ConveyorDirection.FORWARD)
        if robot3.digital_read(sensor_pin_id3) == PinState.LOW:  # Si détection de pièce
           robot3.stop_conveyor(conveyor_id3)  # Arrêt du convoyeur
           break

# Prise de la pièce, détection, traitement en fonction des propriétés
def prise_et_traitement():
    print("Bras 3 prend la pièce.")
    obj_found, pos_array, shape, color = robot3.detect_object("robot3")  # Détection de l’objet
    robot3.move(robot3.get_pose_saved("pose2"))        # Retour à la position avant prise
    robot3.pick(robot3.get_pose_saved("pick2"))        # Prend l’objet
    robot3.move(robot3.get_pose_saved("traitement2"))  # Se déplace vers l’endroit de traitement

    # Applique un temps de traitement en fonction de la forme et la couleur
    if color == ObjectColor.RED and shape == ObjectShape.SQUARE:
        robot3.wait(11)
    if color == ObjectColor.BLUE and shape == ObjectShape.SQUARE:
        robot3.wait(9)
    if color == ObjectColor.GREEN and shape == ObjectShape.SQUARE:
        robot3.wait(5)
    if color == ObjectColor.GREEN and shape == ObjectShape.CIRCLE:
        robot3.wait(2)
    if color == ObjectColor.RED and shape == ObjectShape.CIRCLE:
        robot3.wait(6.5)
    if color == ObjectColor.BLUE and shape == ObjectShape.CIRCLE:
        robot3.wait(1.5)

# Dépose la pièce dans la zone finale (représentée par convoyeur 4)
def deposer_piece():
    robot3.place(robot3.get_pose_saved("convoyeur4"))

# Replace le bras en position initiale
def revenir_position_initiale():
    robot3.move(robot3.get_pose_saved("pose2"))

# Configuration du client MQTT
client = mqtt.Client(protocol=mqtt.MQTTv5)     # Création d’un client MQTT 
client.on_message = on_message                 # Associe la fonction de gestion des messages
client.connect(BROKER_IP, PORT, 60)            # Connexion au broker MQTT
client.subscribe(TOPIC_CONV3)                  # Abonnement au sujet de Bras 3
client.loop_forever()                          # Écoute continue des messages MQTT

