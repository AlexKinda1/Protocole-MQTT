from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus, value
from pyniryo import *

def get_ordre_optimal(pieces):
    """
    pieces: liste de tuples (shape, color) détectés
    Retourne un ordre optimal basé sur la logique de flowshop
    """
    from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus, value

    # ⚠ Tes temps de traitement pour chaque pièce (forme, couleur) sur les 3 machines
    temps_traitement = {
        (ObjectShape.CIRCLE, ObjectColor.BLUE):   [32.44, 30.99, 24.01],
        (ObjectShape.SQUARE, ObjectColor.RED):    [33.44, 40.49, 28.51],
        (ObjectShape.CIRCLE, ObjectColor.GREEN):  [29.44, 31.49, 22.51],
        (ObjectShape.SQUARE, ObjectColor.GREEN):  [31.44, 34.49, 25.51],
        (ObjectShape.CIRCLE, ObjectColor.RED):    [30.44, 35.99, 21.51],
        (ObjectShape.SQUARE, ObjectColor.BLUE):   [35.44, 38.49, 30.51],
        # ➕ ajoute d'autres combinaisons si besoin
    }

    # ⚙️ Crée la matrice des temps pour les pièces détectées
    t = [temps_traitement.get(p, [10, 10, 10]) for p in pieces]  # valeur par défaut si inconnue

    m = len(pieces)  # nombre de pièces
    n = 3            # nombre de machines

    prob = LpProblem("FlowShopScheduling", LpMinimize)

    C = [[LpVariable(f"C_{j}_{i}", lowBound=0) for i in range(n)] for j in range(m)]
    C_max = LpVariable("C_max", lowBound=0)
    prob += C_max

    for j in range(m):
        for i in range(1, n):
            prob += C[j][i] >= C[j][i-1] + t[j][i]

    for i in range(n):
        for j1 in range(m):
            for j2 in range(j1 + 1, m):
                y = LpVariable(f"y_{j1}_{j2}_{i}", cat="Binary")
                M = 10000
                prob += C[j1][i] + t[j1][i] <= C[j2][i] + M * (1 - y)
                prob += C[j2][i] + t[j2][i] <= C[j1][i] + M * y

    for j in range(m):
        prob += C[j][0] >= 0
        prob += C_max >= C[j][n - 1]

    prob.solve()

    # Trie les pièces selon leur date de début sur M1 (machine 1)
    ordres = sorted([(j, value(C[j][0]) - t[j][0]) for j in range(m)], key=lambda x: x[1])
    return [pieces[j] for j, _ in ordres]
