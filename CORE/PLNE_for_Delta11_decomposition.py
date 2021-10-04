from gurobipy import *


def decompose(proSet, conSet, W):
    model = Model("PLNE for Delta 11 decomposition")
    model.setParam('OutputFlag', False)
    #-- Variables
    Sij = {(i, j): model.addVar(vtype=GRB.BINARY, name=f's_{i}_{j}') for i in proSet for j in conSet}


    # Couverture de tout critere con
    for j in conSet:
        model.addConstr(quicksum([Sij[(i_, j)] for i_ in proSet]) == 1)

    # Chaque critere pro utilise au plus une fois
    for i in proSet:
        model.addConstr(quicksum([Sij[(i, j_)] for j_ in conSet]) <= 1)

    # Compatibilite swap et jeu de poids
    for i in proSet:
        for j in conSet:
            model.addConstr(W[i] >= W[j]*Sij[(i, j)])

    model.update()
    model.optimize()

    if model.status == GRB.OPTIMAL:
        print("\nDelta 1-1")
        for j in conSet:
            for i in proSet:
                if Sij[(i, j)].x == 1:
                    print(f'\'{i}\' -> \'{j}\'')
    else:
        print("Non Delta 11 decomposable")


if __name__ == "__main__":
    decompose({'b', 'd'}, {'c', 'e'}, {'a': 0.2456, 'b': 0.2455, 'c': 0.1455, 'd': 0.1135, 'e': 0.1000, 'f': 0.0788, 'g': 0.0712})
