from gurobipy import *


def decompose(proSet, conSet, W):
    model = Model("PLNE for Delta 1m and Delta m1 decomposition")
    model.setParam('OutputFlag', False)
    #-- Variables
    B1m = {(i, j): model.addVar(vtype=GRB.BINARY, name=f'b_{i}_{j}_1m') for i in proSet for j in conSet}
    Bm1 = {(i, j): model.addVar(vtype=GRB.BINARY, name=f'b_{i}_{j}_m1') for i in proSet for j in conSet}

    Lambda = model.addVar(vtype=GRB.CONTINUOUS, name=f'Lambda')

    BigM = sum(W.values())*2

    # 1. tentative de modification (ce 16/02/22)
    for i in proSet:
        for j in conSet:
            model.addConstr(Bm1[(i, j)] + quicksum([B1m[(i_, j)] for i_ in proSet]) <= 1, name="C1 ({})".format((i, j)))

    # 3. Unicite inter-worlds
    for i in proSet:
        for j in conSet:
            model.addConstr(B1m[(i, j)] + quicksum([Bm1[(i, j_)] for j_ in conSet]) <= 1, name="C3 ({})".format((i, j)))

    # 4. Couverture Delta 1m
    for i in proSet:
        model.addConstr(quicksum([B1m[(i, j_)]*W[j_] for j_ in conSet]) <= W[i], name="C4 ({})".format(i))

    # 5. Couverture Delta m1
    for j in conSet:
        model.addConstr(quicksum([Bm1[(i_, j)]*W[i_] + B1m[(i_, j)]*W[i_] for i_ in proSet]) >= W[j], "C5 ({})".format(j))

    #
    for i in proSet:
        for j in conSet:
            model.addConstr(W[i] - quicksum([B1m[(i, j_)]*W[j_] for j_ in conSet]) + (1 - B1m[(i, j)])*BigM >= Lambda)
            model.addConstr(quicksum([Bm1[(i_, j)]*W[i_] for i_ in proSet]) - W[j] + (1 - Bm1[(i, j)])*BigM >= Lambda)

    model.update()
    model.setObjective(Lambda, GRB.MAXIMIZE)
    model.optimize()

    if model.status == GRB.OPTIMAL:
        chainons_arguments_list = list()
        I_non_pareto = set()


        # print("\nDelta 1m")
        for i in proSet:
            if sum([int(B1m[(i, j_)].x) for j_ in conSet]) > 0:
                localJ1m = {j_ for j_ in conSet if int(B1m[(i, j_)].x) == 1}
                chainons_arguments_list.append(({i}, localJ1m))
                # print("{} -> {}".format(i, localJ1m))
                I_non_pareto.add(i)
                # J1m = J1m | localJ1m

        # print("\nDelta m1")

        for j in conSet:
            if sum([int(Bm1[(i_, j)].x) for i_ in proSet]) > 0:
                localIm1 = {i_ for i_ in proSet if int(Bm1[(i_, j)].x) == 1}
                chainons_arguments_list.append((localIm1, {j}))
                I_non_pareto = I_non_pareto | localIm1
                # print("{} -> {}".format(localIm1, j))
        print("\n", W, proSet, conSet)
        print("Écart Min", float(model.objVal))

        for pos in range(len(chainons_arguments_list)):
            chainon_pro, chainon_con = chainons_arguments_list[pos]
            delta = sum([W[i] for i in chainon_pro]) - sum([W[j] for j in chainon_con])
            print(chainon_pro, "->", chainon_con, ":", delta)
        print("pros dominance", (proSet - I_non_pareto))
        return True, chainons_arguments_list
    else:
        # print("Non Delta 1m and Delta m1 decomposable")
        return False, list()


if __name__ == "__main__":

    decompose({'b', 'f', 'g', 'h'}, {'c', 'd', 'e'}, {'a': 0.2462, 'b': 0.2423, 'c': 0.1480, 'd': 0.1135, 'e': 0.1000, 'f': 0.0788, 'g': 0.0712, 'h': 0.00001})

    decompose({'a', 'b', 'c'}, {'d', 'e', 'f', 'g'}, {'a': 5, 'b': 5, 'c': 1, 'd': 2, 'e': 3, 'f': 2, 'g': 3})
    #
    decompose({'a', 'b', 'c', 'd', 'e'}, {'f', 'g', 'h', 'i', 'j'}, {'a': 5, 'b': 5, 'c': 5, 'd': 5, 'e': 5, 'f': 2, 'g': 2, 'h': 2, 'i': 2, 'j': 2})
