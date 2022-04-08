from CORE.ProblemDescription import *
from CORE.DM import *
from CORE.Tools import EPSILON

# WD-DLT1m-m1 : Weight Deformation with the hypothesis to stay in the same hyperplan wrt to A than dm.utilitiesList        (16/11/2021)
def deform(problem_description, dm):
    dm_order_of_alternatives = dm.alternatives_ordering_list(problem_description)
    dm_best_alternative = dm_order_of_alternatives[0]

    local_epsilon = 0.000001
    print(dm_best_alternative)
    model = Model("Deformation of DM weight -- Delta 1-m & m-1 -- Same Hyperplan")
    model.setParam('OutputFlag', False)
    #-- Variables globales (= non relatives)
    #- Deviation
    DeviationsSigma = {i: (model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig+_{i}'), model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig-_{i}'))
                       for i in range(problem_description.m)} # [0] = +; [1] = -
    #-

    #- p_{(k, l)}
    RecommendationTreeVarDict = dict()
    for k in range(problem_description.numberOfAlternatives-1):
        for l in range(k+1, problem_description.numberOfAlternatives):
            RecommendationTreeVarDict[(k, l)] = model.addVar(vtype=GRB.BINARY, name=f'p_{(k, l)}')



    E_ijVarDictPlus_I_k_l_1m = dict()
    E_ijVarDictMoins_I_k_l_1m = dict()
    E_ijVarDictPlus_J_k_l_1m = dict()
    E_ijVarDictMoins_J_k_l_1m = dict()

    E_ijVarDictPlus_k_l_m1 = dict()
    E_ijVarDictMoins_k_l_m1 = dict()

    F_j_VarDictPlus_k_l = dict()
    F_j_VarDictMoins_k_l = dict()


    # - CONTRAINTES GÉNÉRALES

    #- (a)
    for l in range(1, problem_description.numberOfAlternatives):
        model.addConstr(quicksum([RecommendationTreeVarDict[(k_, l)] for k_ in range(0, l)]) == 1)

    #- (b)
    model.addConstr(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]) == quicksum([sig_pair[1] for sig_pair in DeviationsSigma.values()]))

    #- (c)
    for k in range(problem_description.m):
        # model.addConstr(DeviationsSigma[k][1] <= dm.utilitiesList[k])
        model.addConstr(DeviationsSigma[k][1] + local_epsilon <= dm.utilitiesList[k])

    # - CONTRAINTES SPÉCIFIQUES
    k_l_pair_related_swapVar_1m = dict()
    k_l_pair_related_swapVar_m1 = dict()

    for (k, l) in RecommendationTreeVarDict:
        array_dif = np.array(dm_order_of_alternatives[k].attributeLevelsList) - np.array(dm_order_of_alternatives[l].attributeLevelsList)
        pros, cons = set([i for i in range(len(array_dif)) if array_dif[i] == 1]), set([i for i in range(len(array_dif)) if array_dif[i] == -1])
        k_l_pair_related_swapVar_1m[(k, l)] = {(i, j): model.addVar(vtype=GRB.BINARY, name=f's_{(k, l)}-{(i, j)}_1m') for i in pros for j in cons}
        k_l_pair_related_swapVar_m1[(k, l)] = {(i, j): model.addVar(vtype=GRB.BINARY, name=f's_{(k, l)}-{(i, j)}_m1') for i in pros for j in cons}

        E_ijVarDictPlus_I_k_l_1m[(k, l)] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{(k, l)}-{(i, j)}_I_1m') for i in pros for j in cons}
        E_ijVarDictMoins_I_k_l_1m[(k, l)] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{(k, l)}-{(i, j)}_I_1m') for i in pros for j in cons}
        E_ijVarDictPlus_J_k_l_1m[(k, l)] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{(k, l)}-{(i, j)}_J_1m') for i in pros for j in cons}
        E_ijVarDictMoins_J_k_l_1m[(k, l)] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{(k, l)}-{(i, j)}_J_1m') for i in pros for j in cons}
        E_ijVarDictPlus_k_l_m1[(k, l)] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{(k, l)}-{(i, j)}_m1') for i in pros for j in cons}
        E_ijVarDictMoins_k_l_m1[(k, l)] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{(k, l)}-{(i, j)}_m1') for i in pros for j in cons}

        F_j_VarDictPlus_k_l[(k, l)] = {j: model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'f+_{(k, l)}-{j}') for j in cons}
        F_j_VarDictMoins_k_l[(k, l)] = {j: model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'f-_{(k, l)}-{j}') for j in cons}

        #- (a)
        for i in pros:
            model.addConstr(quicksum([k_l_pair_related_swapVar_m1[(k, l)][(i, j_)] for j_ in cons]) <= 1)

        #- (b)
        for i in pros:
            for j in cons:
                model.addConstr(k_l_pair_related_swapVar_1m[(k, l)][(i, j)] +
                                quicksum([k_l_pair_related_swapVar_m1[(k, l)][(i, j_)] for j_ in cons]) <= 1)


        #- (c)
        for j in cons:
            for i in pros:
                for i_prim in pros:
                    model.addConstr(k_l_pair_related_swapVar_1m[(k, l)][(i, j)] + k_l_pair_related_swapVar_m1[(k, l)][(i_prim, j)] <= 1)


        #- (d)
        for i in pros:
            w_i = dm.utilitiesList[i]
            sig_i_plus = DeviationsSigma[i][0]
            sig_i_moins = DeviationsSigma[i][1]
            model.addConstr(w_i + sig_i_plus - sig_i_moins >= quicksum([k_l_pair_related_swapVar_1m[(k, l)][(i, j_)]*dm.utilitiesList[j_] + E_ijVarDictPlus_J_k_l_1m[(k, l)][(i, j_)] - E_ijVarDictMoins_J_k_l_1m[(k, l)][(i, j_)] for j_ in cons]))


        #- (e)
        for j in cons:
            w_j = dm.utilitiesList[j]
            model.addConstr(quicksum([k_l_pair_related_swapVar_1m[(k, l)][(i_, j)]*dm.utilitiesList[i_] +
                                      k_l_pair_related_swapVar_m1[(k, l)][(i_, j)]*dm.utilitiesList[i_] +
                                      E_ijVarDictPlus_I_k_l_1m[(k, l)][(i_, j)] - E_ijVarDictMoins_I_k_l_1m[(k, l)][(i_, j)] +
                                      E_ijVarDictPlus_k_l_m1[(k, l)][(i_, j)] - E_ijVarDictMoins_k_l_m1[(k, l)][(i_, j)] for i_ in pros]) >= RecommendationTreeVarDict[(k,l)]*w_j + F_j_VarDictPlus_k_l[(k,l)][j] - F_j_VarDictMoins_k_l[(k, l)][j])

            # linearisation
            for i in pros:
                sig_i_plus = DeviationsSigma[i][0]
                sig_i_moins = DeviationsSigma[i][1]
                for j in cons:
                    sig_j_plus = DeviationsSigma[j][0]
                    sig_j_moins = DeviationsSigma[j][1]

                    model.addConstr(E_ijVarDictPlus_I_k_l_1m[(k, l)][(i, j)] <= k_l_pair_related_swapVar_1m[(k, l)][(i, j)])
                    model.addConstr(E_ijVarDictMoins_I_k_l_1m[(k, l)][(i, j)] <= k_l_pair_related_swapVar_1m[(k, l)][(i, j)])
                    model.addConstr(E_ijVarDictPlus_k_l_m1[(k, l)][(i, j)] <= k_l_pair_related_swapVar_m1[(k, l)][(i, j)])
                    model.addConstr(E_ijVarDictMoins_k_l_m1[(k, l)][(i, j)] <= k_l_pair_related_swapVar_m1[(k, l)][(i, j)])

                    model.addConstr(E_ijVarDictPlus_I_k_l_1m[(k, l)][(i, j)] <= sig_i_plus)
                    model.addConstr(E_ijVarDictMoins_I_k_l_1m[(k, l)][(i, j)] <= sig_i_moins)
                    model.addConstr(E_ijVarDictPlus_k_l_m1[(k, l)][(i, j)] <= sig_i_plus)
                    model.addConstr(E_ijVarDictMoins_k_l_m1[(k, l)][(i, j)] <= sig_i_moins)

                    model.addConstr(E_ijVarDictPlus_I_k_l_1m[(k, l)][(i, j)] >= sig_i_plus - 1 + k_l_pair_related_swapVar_1m[(k, l)][(i, j)])
                    model.addConstr(E_ijVarDictMoins_I_k_l_1m[(k, l)][(i, j)] >= sig_i_moins - 1 + k_l_pair_related_swapVar_1m[(k, l)][(i, j)])
                    model.addConstr(E_ijVarDictPlus_k_l_m1[(k, l)][(i, j)] >= sig_i_plus - 1 + k_l_pair_related_swapVar_m1[(k, l)][(i, j)])
                    model.addConstr(E_ijVarDictMoins_k_l_m1[(k, l)][(i, j)] >= sig_i_moins - 1 + k_l_pair_related_swapVar_m1[(k, l)][(i, j)])

                    model.addConstr(E_ijVarDictPlus_J_k_l_1m[(k, l)][(i, j)] <= k_l_pair_related_swapVar_1m[(k, l)][(i, j)])
                    model.addConstr(E_ijVarDictMoins_J_k_l_1m[(k, l)][(i, j)] <= k_l_pair_related_swapVar_1m[(k, l)][(i, j)])
                    model.addConstr(E_ijVarDictPlus_J_k_l_1m[(k, l)][(i, j)] <= sig_j_plus)
                    model.addConstr(E_ijVarDictMoins_J_k_l_1m[(k, l)][(i, j)] <= sig_j_moins)
                    model.addConstr(E_ijVarDictPlus_J_k_l_1m[(k, l)][(i, j)] >= sig_j_plus - 1 + k_l_pair_related_swapVar_1m[(k, l)][(i, j)])
                    model.addConstr(E_ijVarDictMoins_J_k_l_1m[(k, l)][(i, j)] >= sig_j_moins - 1 + k_l_pair_related_swapVar_1m[(k, l)][(i, j)])

                    model.addConstr(F_j_VarDictPlus_k_l[(k, l)][j] <= RecommendationTreeVarDict[(k, l)])
                    model.addConstr(F_j_VarDictMoins_k_l[(k, l)][j] <= RecommendationTreeVarDict[(k, l)])
                    model.addConstr(F_j_VarDictPlus_k_l[(k, l)][j] <= sig_j_plus)
                    model.addConstr(F_j_VarDictMoins_k_l[(k, l)][j] <= sig_j_moins)
                    model.addConstr(F_j_VarDictPlus_k_l[(k, l)][j] >= sig_j_plus - 1 + RecommendationTreeVarDict[(k, l)])
                    model.addConstr(F_j_VarDictMoins_k_l[(k, l)][j] >= sig_j_moins - 1 + RecommendationTreeVarDict[(k, l)])


    model.update()
    model.setObjective(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), GRB.MINIMIZE)

    model.optimize()
    print(model.objVal)

    Tree = dict()
    for l in range(1, problem_description.numberOfAlternatives):
        for k in range(0, l):
            if int(RecommendationTreeVarDict[(k, l)].x) == 1:
                Tree[(k, l)] = (dm_order_of_alternatives[k], dm_order_of_alternatives[l])


    for (k ,l), PairAlt in Tree.items():
        array_dif = np.array(dm_order_of_alternatives[k].attributeLevelsList) - np.array(dm_order_of_alternatives[l].attributeLevelsList)
        pros, cons = set([i for i in range(len(array_dif)) if array_dif[i] == 1]), set([i for i in range(len(array_dif)) if array_dif[i] == -1])

        R1m = {i: [j_ for j_ in cons if int(k_l_pair_related_swapVar_1m[(k, l)][(i, j_)].x) == 1] for i in pros}
        Rm1 = {j: [i_ for i_ in pros if int(k_l_pair_related_swapVar_m1[(k, l)][(i_, j)].x) == 1] for j in cons}
        print(PairAlt, "1m =>", R1m, "m1 =>", Rm1)

    # for oth_alt in problem_description.alternativesSet:
    #     if oth_alt != dm_best_alternative:
    #         array_dif = np.array(dm_best_alternative.attributeLevelsList) - np.array(oth_alt.attributeLevelsList)
    #         pros, cons = set([i for i in range(len(array_dif)) if array_dif[i] == 1]), set([i for i in range(len(array_dif)) if array_dif[i] == -1])
    #
    #         R1m = {i: [j_ for j_ in cons if int(other_alternative_related_swapVar_1m[oth_alt][(i, j_)].x) == 1] for i in pros}
    #         Rm1 = {j: [i_ for i_ in pros if int(other_alternative_related_swapVar_m1[oth_alt][(i_, j)].x) == 1] for j in cons}
    #         print(oth_alt, "1m =>", R1m, "m1 =>", Rm1)
    #
    #         # print()
    #         # for j in cons:
    #         #     print("j=", j, sum([(other_alternative_related_swapVar_1m[oth_alt][(i_, j)].x + other_alternative_related_swapVar_m1[oth_alt][(i_, j)].x)*(dm.utilitiesList[i_] + DeviationsSigma[i_][0].x - DeviationsSigma[i_][1].x) for i_ in pros]),
    #         #           ">=", dm.utilitiesList[j] + DeviationsSigma[j][0].x - DeviationsSigma[j][1].x)
    print()
    print("old", [round(dm.utilitiesList[k], 4) for k in range(problem_description.m)])
    print("dv+", [round(DeviationsSigma[k][0].x, 4) for k in range(problem_description.m)])
    print("dv-", [round(DeviationsSigma[k][1].x, 4) for k in range(problem_description.m)])
    print("new", [round(dm.utilitiesList[k] + DeviationsSigma[k][0].x - DeviationsSigma[k][1].x, 4) for k in range(problem_description.m)])


if __name__ == "__main__":
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria7.csv",
                                                  # performanceTableFileName="CSVFILES/kr-v2-7.csv")
                                                  performanceTableFileName="CSVFILES/test-alternatives-7-2.csv")
    # print(mcda_problem_description)
    dm = WS_DM("CSVFILES/DM-kr-v2-7.csv")
    deform(mcda_problem_description, dm)
