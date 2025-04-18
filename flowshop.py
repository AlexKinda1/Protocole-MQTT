def get_ordre_optimal(pieces):
    """
    pieces: liste de tuples (shape, color) détectés
    Retourne un ordre optimal basé sur la logique de flowshop
    """
    from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus, value

    # Simuler des durées arbitraires pour l'exemple
    t = [[20 + i*3 + j for j in range(3)] for i in range(len(pieces))]  # exemple simple
    m = len(pieces)
    n = 3

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
                M = 1000
                prob += C[j1][i] + t[j1][i] <= C[j2][i] + M * (1 - y)
                prob += C[j2][i] + t[j2][i] <= C[j1][i] + M * y
    for j in range(m):
        prob += C[j][0] >= 0
    for j in range(m):
        prob += C_max >= C[j][n - 1]
    prob.solve()

    # Trie des pièces en fonction de la fin sur M1
    ordres = sorted([(j, value(C[j][0]) - t[j][0]) for j in range(m)], key=lambda x: x[1])
    return [pieces[j] for j, _ in ordres]
