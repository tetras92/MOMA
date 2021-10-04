from CORE.ProblemDescription import *
from CORE.DM import *
from CORE.Tools import EPSILON

# WD-DLT1m-m1 : Weight Deformation
def deform(problem_description, dm):
    dm_best_alternative = dm.best_alternative(problem_description)
    print(dm_best_alternative)
    model = Model("Deformation of DM weight -- Delta 1-m & m-1")

    #-- Variables globales (= non relatives)
    #- Deviation
    DeviationsSigma = {k: (model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig+_{k}'), model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig-_{k}'))
                       for k in range(problem_description.n)} # [0] = +; [1] = -

    #-

    E_ijVarDictPlus_I_1m = dict()
    E_ijVarDictMoins_I_1m = dict()
    E_ijVarDictPlus_J_1m = dict()
    E_ijVarDictMoins_J_1m = dict()

    E_ijVarDictPlus_m1 = dict()
    E_ijVarDictMoins_m1 = dict()

    Pros = set()
    Cons = set()

    # model.setParam('OutputFlag', False)
    other_alternative_related_swapVar_1m = dict()
    other_alternative_related_swapVar_m1 = dict()
    local_epsilon = 0.0001
    for oth_alt in problem_description.alternativesSet:
        if oth_alt != dm_best_alternative:
            array_dif = np.array(dm_best_alternative.attributeLevelsList) - np.array(oth_alt.attributeLevelsList)
            pros, cons = set([i for i in range(len(array_dif)) if array_dif[i] == 1]), set([i for i in range(len(array_dif)) if array_dif[i] == -1])
            # Pros = Pros | pros
            # Cons = Cons | cons
            # print(oth_alt, "pros", pros, "cons", cons)
            other_alternative_related_swapVar_1m[oth_alt] = {(i, j): model.addVar(vtype=GRB.BINARY, name=f's_{oth_alt}-{(i, j)}_1m') for i in pros for j in cons}
            other_alternative_related_swapVar_m1[oth_alt] = {(i, j): model.addVar(vtype=GRB.BINARY, name=f's_{oth_alt}-{(i, j)}_m1') for i in pros for j in cons}

            E_ijVarDictPlus_I_1m[oth_alt] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{oth_alt}-{(i, j)}_I_1m') for i in pros for j in cons}
            E_ijVarDictMoins_I_1m[oth_alt] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{oth_alt}-{(i, j)}_I_1m') for i in pros for j in cons}
            E_ijVarDictPlus_J_1m[oth_alt] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{oth_alt}-{(i, j)}_J_1m') for i in pros for j in cons}
            E_ijVarDictMoins_J_1m[oth_alt] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{oth_alt}-{(i, j)}_J_1m') for i in pros for j in cons}
            E_ijVarDictPlus_m1[oth_alt] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{oth_alt}-{(i, j)}_m1') for i in pros for j in cons}
            E_ijVarDictMoins_m1[oth_alt] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{oth_alt}-{(i, j)}_m1') for i in pros for j in cons}


            #-- Constraints
            #- (a)
            for i in pros:
                model.addConstr(quicksum([other_alternative_related_swapVar_m1[oth_alt][(i, j_)] for j_ in cons]) <= 1)

            #- (b)
            for i in pros:
                for j in cons:
                    model.addConstr(other_alternative_related_swapVar_1m[oth_alt][(i, j)] +
                                    quicksum([other_alternative_related_swapVar_m1[oth_alt][(i, j_)] for j_ in cons]) <= 1)

            #- (c)
            for j in cons:
                for i in pros:
                    for i_prim in pros:
                        model.addConstr(other_alternative_related_swapVar_1m[oth_alt][(i, j)] + other_alternative_related_swapVar_m1[oth_alt][(i_prim, j)] <= 1)

            #- (d)
            for i in pros:
                w_i = dm.utilitiesList[i]
                sig_i_plus = DeviationsSigma[i][0]
                sig_i_moins = DeviationsSigma[i][1]
                model.addConstr(w_i + sig_i_plus - sig_i_moins >= quicksum([other_alternative_related_swapVar_1m[oth_alt][(i, j_)]*dm.utilitiesList[j_] + E_ijVarDictPlus_J_1m[oth_alt][(i, j_)] - E_ijVarDictMoins_J_1m[oth_alt][(i, j_)] for j_ in cons]) + local_epsilon)

            #- (e)
            for j in cons:
                w_j = dm.utilitiesList[j]
                sig_j_plus = DeviationsSigma[j][0]
                sig_j_moins = DeviationsSigma[j][1]
                model.addConstr(quicksum([other_alternative_related_swapVar_1m[oth_alt][(i_, j)]*dm.utilitiesList[i_] +
                                          other_alternative_related_swapVar_m1[oth_alt][(i_, j)]*dm.utilitiesList[i_] +
                                          E_ijVarDictPlus_I_1m[oth_alt][(i_, j)] - E_ijVarDictMoins_I_1m[oth_alt][(i_, j)] +
                                          E_ijVarDictPlus_m1[oth_alt][(i_, j)] - E_ijVarDictMoins_m1[oth_alt][(i_, j)] for i_ in pros]) >= w_j + sig_j_plus - sig_j_moins + local_epsilon)



            # linearisation
            for i in pros:
                sig_i_plus = DeviationsSigma[i][0]
                sig_i_moins = DeviationsSigma[i][1]
                for j in cons:
                    sig_j_plus = DeviationsSigma[j][0]
                    sig_j_moins = DeviationsSigma[j][1]

                    model.addConstr(E_ijVarDictPlus_I_1m[oth_alt][(i, j)] <= other_alternative_related_swapVar_1m[oth_alt][(i, j)])
                    model.addConstr(E_ijVarDictMoins_I_1m[oth_alt][(i, j)] <= other_alternative_related_swapVar_1m[oth_alt][(i, j)])
                    model.addConstr(E_ijVarDictPlus_m1[oth_alt][(i, j)] <= other_alternative_related_swapVar_m1[oth_alt][(i, j)])
                    model.addConstr(E_ijVarDictMoins_m1[oth_alt][(i, j)] <= other_alternative_related_swapVar_m1[oth_alt][(i, j)])

                    model.addConstr(E_ijVarDictPlus_I_1m[oth_alt][(i, j)] <= sig_i_plus)
                    model.addConstr(E_ijVarDictMoins_I_1m[oth_alt][(i, j)] <= sig_i_moins)
                    model.addConstr(E_ijVarDictPlus_m1[oth_alt][(i, j)] <= sig_i_plus)
                    model.addConstr(E_ijVarDictMoins_m1[oth_alt][(i, j)] <= sig_i_moins)

                    model.addConstr(E_ijVarDictPlus_I_1m[oth_alt][(i, j)] >= sig_i_plus - 1 + other_alternative_related_swapVar_1m[oth_alt][(i, j)])
                    model.addConstr(E_ijVarDictMoins_I_1m[oth_alt][(i, j)] >= sig_i_moins - 1 + other_alternative_related_swapVar_1m[oth_alt][(i, j)])
                    model.addConstr(E_ijVarDictPlus_m1[oth_alt][(i, j)] >= sig_i_plus - 1 + other_alternative_related_swapVar_m1[oth_alt][(i, j)])
                    model.addConstr(E_ijVarDictMoins_m1[oth_alt][(i, j)] >= sig_i_moins - 1 + other_alternative_related_swapVar_m1[oth_alt][(i, j)])

                    model.addConstr(E_ijVarDictPlus_J_1m[oth_alt][(i, j)] <= other_alternative_related_swapVar_1m[oth_alt][(i, j)])
                    model.addConstr(E_ijVarDictMoins_J_1m[oth_alt][(i, j)] <= other_alternative_related_swapVar_1m[oth_alt][(i, j)])
                    model.addConstr(E_ijVarDictPlus_J_1m[oth_alt][(i, j)] <= sig_j_plus)
                    model.addConstr(E_ijVarDictMoins_J_1m[oth_alt][(i, j)] <= sig_j_moins)
                    model.addConstr(E_ijVarDictPlus_J_1m[oth_alt][(i, j)] >= sig_j_plus - 1 + other_alternative_related_swapVar_1m[oth_alt][(i, j)])
                    model.addConstr(E_ijVarDictMoins_J_1m[oth_alt][(i, j)] >= sig_j_moins - 1 + other_alternative_related_swapVar_1m[oth_alt][(i, j)])
    #- (f)
    model.addConstr(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]) == quicksum([sig_pair[1] for sig_pair in DeviationsSigma.values()]))

    #- (g)
    for k in range(problem_description.n):
        model.addConstr(DeviationsSigma[k][1] <= dm.utilitiesList[k])
        # model.addConstr(DeviationsSigma[k][1] + local_epsilon <= dm.utilitiesList[k])


    model.update()
    model.setObjective(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), GRB.MINIMIZE)

    model.optimize()
    print(model.objVal)
    for oth_alt in problem_description.alternativesSet:
        if oth_alt != dm_best_alternative:
            array_dif = np.array(dm_best_alternative.attributeLevelsList) - np.array(oth_alt.attributeLevelsList)
            pros, cons = set([i for i in range(len(array_dif)) if array_dif[i] == 1]), set([i for i in range(len(array_dif)) if array_dif[i] == -1])

            R1m = {i: [j_ for j_ in cons if int(other_alternative_related_swapVar_1m[oth_alt][(i, j_)].x) == 1] for i in pros}
            Rm1 = {j: [i_ for i_ in pros if int(other_alternative_related_swapVar_m1[oth_alt][(i_, j)].x) == 1] for j in cons}
            print(oth_alt, "1m =>", R1m, "m1 =>", Rm1)

            # print()
            # for j in cons:
            #     print("j=", j, sum([(other_alternative_related_swapVar_1m[oth_alt][(i_, j)].x + other_alternative_related_swapVar_m1[oth_alt][(i_, j)].x)*(dm.utilitiesList[i_] + DeviationsSigma[i_][0].x - DeviationsSigma[i_][1].x) for i_ in pros]),
            #           ">=", dm.utilitiesList[j] + DeviationsSigma[j][0].x - DeviationsSigma[j][1].x)
    print()
    print("old", [round(dm.utilitiesList[k], 4) for k in range(problem_description.n)])
    print("dv+", [round(DeviationsSigma[k][0].x, 4) for k in range(problem_description.n)])
    print("dv-", [round(DeviationsSigma[k][1].x, 4) for k in range(problem_description.n)])
    print("new", [round(dm.utilitiesList[k] + DeviationsSigma[k][0].x - DeviationsSigma[k][1].x, 4) for k in range(problem_description.n)])


if __name__ == "__main__":
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria7.csv",
                                                  # performanceTableFileName="CSVFILES/kr-v2-7.csv")
                                                  performanceTableFileName="CSVFILES/test-alternatives-7.csv")
    # print(mcda_problem_description)
    dm = WS_DM("CSVFILES/DM-kr-v2-7.csv")
    deform(mcda_problem_description, dm)
