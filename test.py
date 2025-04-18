"""import paho.mqtt.client as mqtt
import time
from pyniryo import *
from config import BROKER_IP, PORT, TOPIC_BRAS1, TOPIC_CONV2
from flowshop import get_ordre_optimal  # ⚠️ fonction à créer pour retourner l’ordre optimal depuis ton flowshop

robot = NiryoRobot('192.168.0.104')
robot.clear_collision_detected()

robot.move(robot.get_pose_saved("pose"))
# Liste des objets à traiter
liste_objets = []

# Variables globales
ordre_optimal = []
indice_piece_actuelle = 0  # pour suivre l'avancement
positions_objets = {}  # (shape, color): position

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
            print("✅ Toutes les pièces ont été traitées.")

# Détection des objets présents
def detecter_objets():
    global positions_objets
    liste = []
    for shape in [ObjectShape.CIRCLE, ObjectShape.SQUARE]:
        for color in [ObjectColor.BLUE, ObjectColor.RED, ObjectColor.GREEN]:
            value = robot.detect_object(workspace_name="robot1", shape=shape, color=color)
            print(f"Valeur pour {shape}, {color} : {value}")
            if value[0] and isinstance(value[1], list) and len(value[1]) == 6:
                liste.append((shape, color))
                positions_objets[(shape, color)] = value[1]
            else:
                print(f"⚠️ Problème avec la position de {shape}, {color} : {value[1]}")

    return liste

# Mouvement + prise + dépôt
def prendre_et_deposer_piece(shape, color):
    print(f"🤖 Bras 1 traite une pièce : {shape}, {color}")
    valeurs = positions_objets[(shape, color)]
    
    # Securité au cas où
    assert isinstance(valeurs, list) and len(valeurs) == 6, f"Position invalide pour {shape}, {color}: {valeurs}"
    
    pose_obj = PoseObject(
        valeurs[0], valeurs[1], valeurs[2],
        valeurs[3], valeurs[4], valeurs[5],
        metadata=PoseMetadata.v1()
    )
    robot.move(pose_obj)
    robot.vision_pick("robot1", shape=shape, color=color)
    robot.place(robot.get_pose_saved("convoyeur2"))
    robot.move(robot.get_pose_saved("pose"))


# Initialisation MQTT
client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_message = on_message
client.connect(BROKER_IP, PORT, 60)
client.subscribe(TOPIC_BRAS1)

# 🔥 Lancement initial
print("🔍 Détection des pièces...")
liste_objets = detecter_objets()

# ⚙️ Calcul de l’ordre optimal
ordre_optimal = get_ordre_optimal(liste_objets)  # Doit retourner une liste de tuples (shape, color)

print("🧠 Ordre optimal reçu :", ordre_optimal)

# Démarrage avec la première pièce
if ordre_optimal:
    shape, color = ordre_optimal[0]
    prendre_et_deposer_piece(shape, color)
    client.publish(TOPIC_CONV2, "start")
    indice_piece_actuelle += 1
else:
    print("❌ Aucune pièce détectée.")

# Boucle d'attente des messages MQTT
client.loop_forever()

import paho.mqtt.client as mqtt
import time
from pyniryo import *
from config import BROKER_IP, PORT, TOPIC_BRAS1, TOPIC_CONV2
from flowshop import get_ordre_optimal  # ⚠️ fonction à créer pour retourner l’ordre optimal depuis ton flowshop

robot = NiryoRobot('192.168.0.104')
robot.clear_collision_detected()

# Liste des objets à traiter
liste_objets = []

# Variables globales
ordre_optimal = []
indice_piece_actuelle = 0  # pour suivre l'avancement
positions_objets = {}  # (shape, color): position

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
            print(" Toutes les pièces ont été traitées.")

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
                # Sauvegarde de la position de l’objet pour plus tard
                positions_objets[(shape, color)] = value[1]
    return liste

# Mouvement + prise + dépôt
def prendre_et_deposer_piece(shape, color):
    print(f" Bras 1 traite une pièce : {shape}, {color}")
    pos = positions_objets[(shape, color)]
    pose_obj = PoseObject(pos.x, pos.y, pos.z, pos.roll, pos.pitch, pos.yaw, metadata=PoseMetadata.v1())
    robot.move(pose_obj)
    robot.vision_pick("robot1", shape=shape, color=color)
    robot.place(robot.get_pose_saved("convoyeur2"))
    robot.move(robot.get_pose_saved("pose"))  # retour à la position initiale

# Initialisation MQTT
client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_message = on_message
client.connect(BROKER_IP, PORT, 60)
client.subscribe(TOPIC_BRAS1)

# 🔥 Lancement initial
print(" Détection des pièces...")
liste_objets = detecter_objets()

# ⚙️ Calcul de l’ordre optimal
ordre_optimal = get_ordre_optimal(liste_objets)  # Doit retourner une liste de tuples (shape, color)

print(" Ordre optimal reçu :", ordre_optimal)

# Démarrage avec la première pièce
if ordre_optimal:
    shape, color = ordre_optimal[0]
    prendre_et_deposer_piece(shape, color)
    client.publish(TOPIC_CONV2, "start")
    indice_piece_actuelle += 1
else:
    print(" Aucune pièce détectée.")

# Boucle d'attente des messages MQTT
client.loop_forever()"""

import paho.mqtt.client as mqtt
import time
from pyniryo import *
from config import BROKER_IP, PORT, TOPIC_BRAS1, TOPIC_CONV2
from flowshop import get_ordre_optimal  # ⚠️ fonction à créer pour retourner l’ordre optimal depuis ton flowshop

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

# 🔥 Lancement initial
print("Détection des pièces...")
liste_objets = detecter_objets()

# ⚙️ Calcul de l’ordre optimal
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

