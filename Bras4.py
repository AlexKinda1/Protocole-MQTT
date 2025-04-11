import paho.mqtt.client as mqtt           # Bibliothèque pour la communication MQTT
from pyniryo import*                      # Contrôle du robot Niryo
from config import BROKER_IP, PORT, TOPIC_CONV3, TOPIC_BRAS3, TOPIC_CONV4  # Paramètres du broker MQTT et des topics

# Initialisation du robot 4 avec son adresse IP
robot4 = NiryoRobot("192.168.0.101")
robot4.clear_collision_detected()             # Nettoie les éventuelles détections de collision
robot4.move(robot4.get_pose_saved("pose3"))   # Positionne le bras en position initiale

# Détecteur infra et convoyeur utilisés
sensor_pin_id3 = PinID.DI5
conveyor_id3 = ConveyorID.ID_1

# Variables globales pour stocker les informations sur la pièce
color = None
shape = None

# Fonction déclenchée à la réception d’un message MQTT
def on_message(client, userdata, msg):
    if msg.topic == TOPIC_CONV4 and msg.payload.decode() == "start":
        print("Bras 4 démarre son convoyeur.")
        robot4.clear_collision_detected()        # Réinitialisation des collisions
        activer_convoyeur()                     # Démarrage du convoyeur jusqu’à détection de pièce
        prise_et_traitement()                   # Prise et traitement selon couleur/forme
        deposer_piece()                         # Dépôt dans la zone finale
        print("Bras 4 a déposé la pièce dans la zone finale.")
        client.publish(TOPIC_BRAS3, "next")     # Signale au bras 3 qu’il peut continuer
        revenir_position_initiale()             # Retour à la position initiale

# Active le convoyeur jusqu'à ce qu’un objet soit détecté par le capteur
def activer_convoyeur():
    robot4.run_conveyor(conveyor_id3, speed=80, direction=ConveyorDirection.BACKWARD)
    while True:
        if robot4.digital_read(sensor_pin_id3) == PinState.LOW:  # Si détection de pièce
           robot4.stop_conveyor(conveyor_id3)  # Arrêt du convoyeur
           break

# Prise de la pièce, détection, traitement en fonction des propriétés
def prise_et_traitement():
    print("Bras 4 prend la pièce.")
    obj_found, pos_array, shape, color = robot4.detect_object("robot4")  # Détection de l’objet
    robot4.move(robot4.get_pose_saved("pose3"))        # Retour à la position avant prise
    robot4.pick(robot4.get_pose_saved("pick3"))        # Prend l’objet
    robot4.move(robot4.get_pose_saved("traitement3"))  # Se déplace vers l’endroit de traitement

    # Applique un temps de traitement en fonction de la forme et la couleur
    if color == ObjectColor.RED and shape == ObjectShape.SQUARE:
        robot4.wait(8)
    if color == ObjectColor.BLUE and shape == ObjectShape.SQUARE:
        robot4.wait(10)
    if color == ObjectColor.GREEN and shape == ObjectShape.SQUARE:
        robot4.wait(5)
    if color == ObjectColor.GREEN and shape == ObjectShape.CIRCLE:
        robot4.wait(2)
    if color == ObjectColor.RED and shape == ObjectShape.CIRCLE:
        robot4.wait(1)
    if color == ObjectColor.BLUE and shape == ObjectShape.CIRCLE:
        robot4.wait(3.5)

# Dépose la pièce dans la zone finale (représentée par dépôt)
def deposer_piece():
    robot4.place(robot4.get_pose_saved("depot"))

# Replace le bras en position initiale
def revenir_position_initiale():
    robot4.move(robot4.get_pose_saved("pose3"))

# Configuration du client MQTT
client = mqtt.Client(protocol=mqtt.MQTTv5)     # Création d’un client MQTT 
client.on_message = on_message                 # Associe la fonction de gestion des messages
client.connect(BROKER_IP, PORT, 60)            # Connexion au broker MQTT
client.subscribe(TOPIC_CONV4)                  # Abonnement au sujet de Bras 4
client.loop_forever()                          # Écoute continue des messages MQTT
