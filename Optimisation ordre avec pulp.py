from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus, value
import matplotlib as plt
# Paramètres
n = 4  # Nombre de machines
m = 8  # Nombre de pièces
t = [[1, 5, 2, 8],   # Pièce 0
     [8, 2, 3, 9],  # Pièce 1
     [2, 5, 7, 8],
     [4, 4, 8, 6],
     [5, 1, 7, 7],
     [6, 8, 7, 4],
     [9, 4, 2, 1],
     [5, 9, 7, 3]]   # Pièce 2

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
        prob += C[j][i] >= C[j][i-1] + t[j][i]

# Contraintes d'exclusion entre pièces (Big M)
for i in range(n):
    for j1 in range(m):
        for j2 in range(j1 + 1, m):
            y = LpVariable(f"y_{j1}_{j2}_{i}", cat="Binary")
            M = 1000
            prob += C[j1][i] + t[j1][i] <= C[j2][i] + M * (1 - y)
            prob += C[j2][i] + t[j2][i] <= C[j1][i] + M * y

# Contraintes de départ
for j in range(m):
    prob += C[j][0] >= t[j][0]

# Définir le makespan comme le max des temps de fin sur la dernière machine
for j in range(m):
    prob += C_max >= C[j][n - 1]

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

