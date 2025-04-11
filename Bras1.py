import paho.mqtt.client as mqtt               # Importation du client MQTT
from pyniryo import *                         # Importation de la bibliothèque Niryo One
from config import BROKER_IP, PORT, TOPIC_BRAS1, TOPIC_CONV2  # Import des paramètres de configuration MQTT

# Connexion au robot Niryo via son IP
robot1 = NiryoRobot('192.168.0.104')# remplace par IP de ton robot
robot1.clear_collision_detected()  # Réinitialise les détections de collision

# Définition de la taille de la matrice d'objets à traiter
ligne = 2
colonne = 3

# Décalage (en mètres) entre chaque objet sur la matrice
x_offset_size = 0.07
y_offset_size = 0.07

# Récupération de la position de prise et de dépôt sauvegardée dans le robot
base_pose = robot1.get_pose_saved("pick_pose")
place_pose = robot1.get_pose_saved("convoyeur2")

# Génère une liste de positions de prise en fonction de la grille ligne x colonne
def generer_positions(base_pose, ligne, colonne):
    positions = []
    for i in range(ligne):
        for j in range(colonne):
            # Applique un décalage à la position de base pour chaque case de la matrice
            new_pose = base_pose.copy_with_offsets(
                x_offset=i * x_offset_size,  # ligne = axe x
                y_offset=j * y_offset_size   # colonne = axe y
            )
            positions.append(new_pose)
    return positions

# Liste de toutes les positions calculées
liste_positions = generer_positions(base_pose, ligne, colonne)
index_courant = 0  # Index de la prochaine position à traiter

# Fonction qui prend un objet à une position donnée et le dépose sur le convoyeur 2
def prendre_et_deposer():
    global index_courant
    if index_courant >= len(liste_positions):
        print(" Tous les objets ont été traités.")
        client.publish(TOPIC_CONV2, "end")  # Informe Bras 2 que c’est terminé
        client.loop_stop()  # Arrête la boucle MQTT
        robot1.close_connection()  # Ferme la connexion au robot
        return

    # Affiche l'index de l'objet traité
    print(f" Prise de l'objet à la position matrice index {index_courant + 1}")
    robot1.pick(liste_positions[index_courant])  # Prend l'objet
    robot1.place(place_pose)                     # Le dépose sur le convoyeur
    index_courant += 1
    print(" Objet transféré au convoyeur de Bras 2.")

# Remet le bras robotisé dans une position initiale sauvegardée
def revenir_position_initiale():
    print(" Retour à la position initiale.")
    robot1.move(robot1.get_pose_saved("pose"))

# Callback déclenché à la réception d’un message MQTT
def on_message(client, userdata, msg):
    if msg.topic == TOPIC_BRAS1 and msg.payload.decode() == "next":
        print(" Message reçu de Bras 2 : 'next'")
        prendre_et_deposer()  # Exécute une prise et un dépôt
        revenir_position_initiale()  # Ramène le bras à sa position initiale
        client.publish(TOPIC_CONV2, "start")  # Redémarre le convoyeur de Bras 2

# Configuration du client MQTT
client = mqtt.Client(protocol=mqtt.MQTTv5)  # Utilise le protocole MQTT v5
client.on_message = on_message              # Associe le callback de réception
client.connect(BROKER_IP, PORT, 60)         # Connexion au broker MQTT
client.subscribe(TOPIC_BRAS1)               # Abonnement au topic de contrôle de Bras 1

# Automatisation du traitement de la première pièce et Lancement du processus initial 
print(" Démarrage du processus. Bras 1 s'occupe de la première pièce.")
prendre_et_deposer()
revenir_position_initiale()
client.publish(TOPIC_CONV2, "start")  # Lance le convoyeur de Bras 2

# Boucle infinie MQTT pour écouter les messages
client.loop_forever()
