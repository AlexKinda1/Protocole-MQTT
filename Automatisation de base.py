from pyniryo import *
import time

# Connexion au robot avec gestion des erreurs
try:
    robot = NiryoRobot("192.168.0.106")
except Exception as e:
    print(f"Erreur de connexion au robot : {e}")
    exit(1)

# Paramètres
sensor_pin_id = PinID.DI5
conveyor_id = ConveyorID.ID_1

max_catch_count = int(input("Entrez le nombre maximal de pièces à prendre: "))

ligne = 2
colonne = 5

x_offset_size = 0.05
y_offset_size = 0.05

color_map = {"R": ObjectColor.RED, "G": ObjectColor.GREEN, "B": ObjectColor.BLUE}
shape_map = {"S": ObjectShape.SQUARE, "C": ObjectShape.CIRCLE}

def get_color_from_input(color_input):
    return color_map.get(color_input.upper())

def get_shape_from_input(shape_input):
    return shape_map.get(shape_input.upper())

def get_pattern(zone_name):
    pattern_zone = []

    num_pieces = int(input(f"Nombre de pièces dans la zone {zone_name}: "))

    for i in range(num_pieces):
        print(f"\nSaisie de la pièce {i+1} :")

        color = None
        while color is None:
            color = get_color_from_input(input("Entrez la couleur (R: Rouge, G: Vert, B: Bleu) : "))
            if color is None:
                print("Couleur invalide, réessayez.")

        shape = None
        while shape is None:
            shape = get_shape_from_input(input("Entrez la forme (S: Carré, C: Cercle) : "))
            if shape is None:
                print("Forme invalide, réessayez.")

        x, y = int(input(f"Position X (1/{ligne}) : ")), int(input(f"Position Y (1/{colonne}) : "))

        if not (0 < x <= ligne and 0 < y <= colonne):
            print("Position invalide.")
            continue
        pattern_zone.append({"color": color, "shape": shape, "position": (x, y), "placed": False})

    return pattern_zone

def calcul_position_pour_la_zone(place_pose, ligne, colonne):
    positions = []
    for i in range(ligne):
        for j in range(colonne):
            positions.append(place_pose.copy_with_offsets(
                x_offset=i * x_offset_size, 
                y_offset=j * y_offset_size
            ))
    return positions

# Initialisation des patterns et positions
pattern_alpha = get_pattern("Alpha")

pattern_beta = get_pattern("Beta")

positions_alpha = calcul_position_pour_la_zone(robot.get_saved_dynamic_frame("Repère Alpha"), ligne, colonne)

positions_beta = calcul_position_pour_la_zone(robot.get_saved_dynamic_frame("Convoyeur Beta"), ligne, colonne)

position_rebut = robot.get_pose_saved("beta Alex")


# Démarrage du convoyeur
robot.run_conveyor(conveyor_id, speed=50, direction=ConveyorDirection.BACKWARD)
robot.clear_collision_detected()

catch_count = 0
failed_attempts = 0

while catch_count < max_catch_count:
    while robot.digital_read(sensor_pin_id) == PinState.HIGH:
        time.sleep(0.1)
    
    robot.stop_conveyor(conveyor_id)

    print("Objet détecté !")

    robot.move(robot.get_pose_saved("Convoyeur Alex"))

    obj_found, shape, color = robot.vision_pick(Nom du workspace)
    
    if not obj_found:
        failed_attempts += 1  

        print(f"Échec ({failed_attempts}/3). Nouvelle tentative...")

        if failed_attempts >= 3:
            print("Échec répété ! Envoi à la zone de rebut.")
            robot.place(position_rebut)
            failed_attempts = 0  
        robot.run_conveyor(conveyor_id)
        continue  

    failed_attempts = 0
    print(f"Objet détecté - Forme: {shape}, Couleur: {color}")
    
    placed = False
    for item, pos in zip(pattern_alpha, positions_alpha):
        if not item["placed"] and item["color"] == color and item["shape"] == shape:
            item["placed"], placed = True, True
            next_place = pos
            break

    if not placed:
        for item, pos in zip(pattern_beta, positions_beta):
            if not item["placed"] and item["color"] == color and item["shape"] == shape:
                item["placed"], placed = True, True
                next_place = pos
                break
    
    if not placed:
        next_place = position_rebut
    
    robot.place(next_place)
    print(f"Objet placé en {next_place}")
    catch_count += 1  
    
    while robot.digital_read(sensor_pin_id) == PinState.LOW:
        time.sleep(0.04)
    
    print("Objet retiré ! Redémarrage du convoyeur...")

    robot.run_conveyor(conveyor_id)

    robot.move(robot.get_pose_saved("Convoyeur Alex"))

print("Fin du programme : nombre max de pièces atteint.")
robot.stop_conveyor(conveyor_id)
robot.close_connection()
