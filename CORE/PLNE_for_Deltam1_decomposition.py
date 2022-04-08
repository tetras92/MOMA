from gurobipy import *


def decompose(proSet, conSet, W):
    model = Model("PLNE for Delta m1 decomposition")
    model.setParam('OutputFlag', False)
    #-- Variables
    Sij = {(i, j): model.addVar(vtype=GRB.BINARY, name=f's_{i}_{j}') for i in proSet for j in conSet}


    # Chaque pro utilise au plus une fois
    for i in proSet:
        model.addConstr(quicksum([Sij[(i, j_)] for j_ in conSet]) <= 1)

    # Compatibilite swap et jeu de poids
    for j in conSet:
        model.addConstr(W[j] <= quicksum([W[i_]*Sij[(i_, j)] for i_ in proSet]))

    model.update()
    model.optimize()

    if model.status == GRB.OPTIMAL:
        chainons_arguments_list = list()
        # print("\nDelta m-1")
        # for j in conSet:
        #     chainons_arguments_list.append(({i_ for i_ in proSet if Sij[(i_, j)].x == 1}, {j}))
            # print(f'{[i_ for i_ in proSet if Sij[(i_, j)].x == 1]} -> \'{j}\'')
        return True, chainons_arguments_list
    else:
        # print("Non Delta m1 decomposable")
        return False, list()


if __name__ == "__main__":
    decompose({'c', 'd', 'e'}, {'b', 'f'}, {'a': 128, 'b': 126, 'c': 77, 'd': 59, 'e': 52, 'f': 41, 'g': 37})

    # decompose({'b', 'd'}, {'c', 'e'}, {'a': 0.2456, 'b': 0.2455, 'c': 0.1455, 'd': 0.1135, 'e': 0.1000, 'f': 0.0788, 'g': 0.0712})
