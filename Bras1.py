import paho.mqtt.client as mqtt
from pyniryo import *
from config import BROKER_IP, PORT, TOPIC_BRAS1, TOPIC_CONV2

robot1 = NiryoRobot('192.168.0.104')
robot1.clear_collision_detected()

ligne = 3
colonne = 3

# Décalage entre les cases (en mètres)
x_offset_size = 0.07
y_offset_size = 0.07

base_pose = robot1.get_pose_saved("pick_pose")
place_pose = robot1.get_pose_saved("convoyeur2")


def generer_positions(base_pose, ligne, colonne):
    positions = []
    for i in range(ligne):
        for j in range(colonne):
            new_pose = base_pose.copy_with_offsets(
                x_offset=i * x_offset_size,  # ligne = axe x
                y_offset=j * y_offset_size   # colonne = axe y
            )
            positions.append(new_pose)
    return positions

liste_positions = generer_positions(base_pose, ligne, colonne)
index_courant = 0


def prendre_et_deposer():
    global index_courant
    if index_courant >= len(liste_positions):
        print(" Tous les objets ont été traités.")
        client.publish(TOPIC_CONV2, "end")  # Dis à Bras 2 de terminer
        client.loop_stop()  # Arrête le client MQTT
        robot1.close_connection()
        return
    
    print(f" Prise de l'objet à la position matrice index {index_courant + 1}")
    robot1.pick(liste_positions[index_courant])
    robot1.place(place_pose)
    index_courant += 1
    print(" Objet transféré au convoyeur de Bras 2.")

def revenir_position_initiale():
    print(" Retour à la position initiale.")
    robot1.move(robot1.get_pose_saved("pose"))

# Callback MQTT
def on_message(client, userdata, msg):
    if msg.topic == TOPIC_BRAS1 and msg.payload.decode() == "next":
        print(" Message reçu de Bras 2 : 'next'")
        prendre_et_deposer()
        revenir_position_initiale()
        client.publish(TOPIC_CONV2, "start")  # Déclenche le convoyeur de Bras 2

# Configuration MQTT
client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_message = on_message
client.connect(BROKER_IP, PORT, 60)
client.subscribe(TOPIC_BRAS1)


print(" Démarrage du processus. Bras 1 s'occupe de la première pièce.")
prendre_et_deposer()
revenir_position_initiale()
client.publish(TOPIC_CONV2, "start")


client.loop_forever()
