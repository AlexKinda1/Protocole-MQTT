from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus, value

# Paramètres
m = 6  # Nombre de pièces
n = 3  # Nombre de machines

# M1 ne fait pas parti du flowshop

      # M2   # M3   # M4 
t = [[31.44, 33.44, 35.44],   # Pièce 1
     [34.49, 40.49, 38.49],   # Pièce 2
     [25.51, 28.51, 30.51],   # Pièce 3
     [29.44, 31.49, 22.51],   # Pièce 4
     [30.44, 35.99, 21.51],   # Pièce 5
     [32.44, 30.99, 24.01]]   # Pièce 6

# Création du problème
prob = LpProblem("FlowShopScheduling", LpMinimize)

# Variables de fin de chaque opération
C = [[LpVariable(f"C_{j}_{i}", lowBound=0) for i in range(n)] for j in range(m)]

# Variable du makespan
C_max = LpVariable("C_max", lowBound=0)
prob += C_max  # fonction objectif

# Contraintes de précédence sur les machines
for j in range(m):
    for i in range(1, n):
        prob += C[j][i] >= C[j][i-1] + t[j][i], f"precedence_{j}_{i}"

# Contraintes d'exclusion entre pièces (Big M)
for i in range(n):
    for j1 in range(m):
        for j2 in range(j1 + 1, m):
            y = LpVariable(f"y_{j1}_{j2}_{i}", cat="Binary")
            M = 1000  # Choisir un M suffisamment grand
            prob += C[j1][i] + t[j1][i] <= C[j2][i] + M * (1 - y), f"exclusion_{j1}_{j2}_{i}_1"
            prob += C[j2][i] + t[j2][i] <= C[j1][i] + M * y, f"exclusion_{j1}_{j2}_{i}_2"

# Contraintes de départ
for j in range(m):
    prob += C[j][0] >= 0, f"start_{j}"

# Définir le makespan comme le max des temps de fin sur la dernière machine
for j in range(m):
    prob += C_max >= C[j][n - 1], f"makespan_{j}"

# Résolution
prob.solve()

# Résultats
print(f"Statut : {LpStatus[prob.status]}")
print(f"Makespan optimal : {value(C_max)}\n")

# Affichage du moment où chaque pièce finit chaque machine
for j in range(m):
    for i in range(n):
        print(f"Pièce {j+1} finit sur Machine {i+1} à t = {value(C[j][i])}")

# 🔍 Extraction de l'ordre optimal sur la première machine
ordres = sorted([(j, value(C[j][0]) - t[j][0]) for j in range(m)], key=lambda x: x[1])
ordre_optimal = [f"Piece {j+1}" for j, _ in ordres]

print("\n Ordre optimal de traitement :")
print(" -> ".join(ordre_optimal))


