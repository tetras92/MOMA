from gurobipy import *


def decompose(proSet, conSet, W):
    model = Model("PLNE for Delta 1m and Delta m1 decomposition")
    model.setParam('OutputFlag', False)
    #-- Variables
    B1m = {(i, j): model.addVar(vtype=GRB.BINARY, name=f'b_{i}_{j}_1m') for i in proSet for j in conSet}
    Bm1 = {(i, j): model.addVar(vtype=GRB.BINARY, name=f'b_{i}_{j}_m1') for i in proSet for j in conSet}


    # 1. Tout j con couvert ON PEUT S'EN PASSER (Cotonou le 11 Septembre 2021)
    # for j in conSet:
    #     model.addConstr(quicksum([B1m[(i_, j)] + Bm1[(i_, j)] for i_ in proSet]) >= 1, name="C1 ({})".format(j))


    #1. Pour tout critère con j, on a :
    #   - soit j est couvert en Delta(1,\,m) par un critère pro i donné,
    #   - soit j est couvert en Delta(m,\,1) par un critère pro i' donné.
    proSetList = list(proSet)
    for ki in range(len(proSetList)):
        for ki_ in range(ki, len(proSetList)):
            i = proSetList[ki]
            i_ = proSetList[ki_]
            for j in conSet:
                model.addConstr(B1m[(i, j)] + Bm1[(i_, j)] <= 1, name="C1 ({})".format((i, i_, j)))



    # 2. Unicite contribution de i dans le Delta m1 world
    for i in proSet:
        model.addConstr(quicksum([Bm1[(i, j_)] for j_ in conSet]) <= 1, name="C2 ({})".format(i))

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


    model.update()
    # model.setObjective(quicksum(B1m.values()), GRB.MAXIMIZE)
    model.optimize()

    if model.status == GRB.OPTIMAL:
        chainons_arguments_list = list()
        I1m = set()
        J1m = set()
        print(model.objVal)
        print("World 1m")
        for i in proSet:
            for j in conSet:
                print(f'({i}, {j})', int(B1m[(i, j)].x))

        print("World m1")
        for i in proSet:
            for j in conSet:
                print(f'({i}, {j})', int(Bm1[(i, j)].x))

        print("\nDelta 1m")
        for i in proSet:
            if sum([int(B1m[(i, j_)].x) for j_ in conSet]) > 0:
                localJ1m = {j_ for j_ in conSet if int(B1m[(i, j_)].x) == 1}
                chainons_arguments_list.append(({i}, localJ1m))
                print("{} -> {}".format(i, localJ1m))
                I1m.add(i)
                J1m = J1m | localJ1m

        print("\nDelta m1")
        for j in conSet - J1m:
            if sum([int(Bm1[(i_, j)].x) for i_ in proSet]) > 0:
                localIm1 = {i_ for i_ in proSet if int(Bm1[(i_, j)].x) == 1}
                chainons_arguments_list.append((localIm1, {j}))
                print("{} -> {}".format(localIm1, j))

        return True, chainons_arguments_list
    else:
        print("Non Delta 1m and Delta m1 decomposable")
        return False, list()


if __name__ == "__main__":
    # decompose({'b', 'f', 'g'}, {'a', 'd'}, {'a': 128, 'b': 126, 'c': 77, 'd': 59, 'e': 52, 'f': 41, 'g': 37})
    # decompose({'b', 'e', 'g'}, {'c', 'd', 'f'}, {'a': 128, 'b': 126, 'c': 77, 'd': 59, 'e': 52, 'f': 41, 'g': 37})
    # decompose({'a', 'f'}, {'c', 'e', 'g'}, {'a': 128, 'b': 126, 'c': 77, 'd': 59, 'e': 52, 'f': 41, 'g': 37})
    # decompose({'a', 'c', 'd'}, {'b'}, {'a': 1, 'b': 5, 'c': 3, 'd': 2})
    # decompose({'a', 'd'}, {'c', 'e', 'g'}, {'a': 0.2462, 'b': 0.2423, 'c': 0.1480, 'd': 0.1135, 'e': 0.1000, 'f': 0.0788, 'g': 0.0712})
    decompose({'b', 'f', 'g'}, {'c', 'd', 'e'}, {'a': 0.2462, 'b': 0.2423, 'c': 0.1480, 'd': 0.1135, 'e': 0.1000, 'f': 0.0788, 'g': 0.0712})

    # decompose({'a', 'f', 'g'}, {'c', 'e', 'd'}, {'a': 0.2456, 'b': 0.2455, 'c': 0.1455, 'd': 0.1135, 'e': 0.1000, 'f': 0.0788, 'g': 0.0712})
    # decompose({'a', 'f'}, {'c', 'e'}, {'a': 0.2456, 'b': 0.2455, 'c': 0.1455, 'd': 0.1135, 'e': 0.1000, 'f': 0.0788, 'g': 0.0712})
    # decompose({'b', 'd'}, {'c', 'e', 'g'}, {'a': 0.2456, 'b': 0.2455, 'c': 0.1455, 'd': 0.1135, 'e': 0.1000, 'f': 0.0788, 'g': 0.0712})
    # decompose({'a', 'f', 'g'}, {'b', 'd'}, {'a': 0.2456, 'b': 0.2455, 'c': 0.1455, 'd': 0.1135, 'e': 0.1000, 'f': 0.0788, 'g': 0.0712})

