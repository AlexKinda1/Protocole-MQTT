import paho.mqtt.client as mqtt
import time
from pyniryo import *
from config import BROKER_IP, PORT, TOPIC_BRAS1, TOPIC_CONV2
from flowshop import get_ordre_optimal  

robot = NiryoRobot('192.168.0.104')
robot.clear_collision_detected()

# Liste des objets à traiter
liste_objets = []

# Variables globales
ordre_optimal = []
indice_piece_actuelle = 0  # pour suivre l'avancement
positions_objets = {}  # (shape, color): list of positions

# MQTT - callback
def on_message(client, userdata, msg):
    global indice_piece_actuelle
    if msg.topic == TOPIC_BRAS1 and msg.payload.decode() == "next":
        if indice_piece_actuelle < len(ordre_optimal):
            print(f"Traitement de la pièce {indice_piece_actuelle+1}/{len(ordre_optimal)}")
            shape, color = ordre_optimal[indice_piece_actuelle]
            prendre_et_deposer_piece(shape, color)
            client.publish(TOPIC_CONV2, "start")
            indice_piece_actuelle += 1
        else:
            print("Toutes les pièces ont été traitées.")

# Détection des objets présents
def detecter_objets():
    global positions_objets
    liste = []
    for shape in [ObjectShape.CIRCLE, ObjectShape.SQUARE]:
        for color in [ObjectColor.BLUE, ObjectColor.RED, ObjectColor.GREEN]:
            value = robot.detect_object(workspace_name="robot1", shape=shape, color=color)
            print(f"Valeur pour {shape}, {color} : {value}")
            if value[0]:
                liste.append((shape, color))
                # Ajout de la position dans une liste pour gérer plusieurs objets identiques
                positions_objets.setdefault((shape, color), []).append(value[1])
    return liste

# Mouvement + prise + dépôt
def prendre_et_deposer_piece(shape, color):
    print(f"Bras 1 traite une pièce : {shape}, {color}")
    pos = positions_objets[(shape, color)].pop(0)  # Prend la première position disponible
    pose_obj = PoseObject(pos[0], pos[1], pos[2], 0, 0, 0)
    robot.move(pose_obj)
    robot.vision_pick("robot1", shape=shape, color=color)
    robot.place(robot.get_pose_saved("convoyeur2"))
    robot.move(robot.get_pose_saved("pose"))  # retour à la position initiale

# Initialisation MQTT
client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_message = on_message
client.connect(BROKER_IP, PORT, 60)
client.subscribe(TOPIC_BRAS1)

#  Lancement initial
print("Détection des pièces...")
liste_objets = detecter_objets()

# ⚙ Calcul de l’ordre optimal
ordre_optimal = get_ordre_optimal(liste_objets)  # Doit retourner une liste de tuples (shape, color)

print("Ordre optimal reçu :", ordre_optimal)

# Démarrage avec la première pièce
if ordre_optimal:
    shape, color = ordre_optimal[0]
    prendre_et_deposer_piece(shape, color)
    client.publish(TOPIC_CONV2, "start")
    indice_piece_actuelle += 1
else:
    print("Aucune pièce détectée.")

# Boucle d'attente des messages MQTT
client.loop_forever()

