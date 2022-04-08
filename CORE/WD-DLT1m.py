from CORE.ProblemDescription import *
from CORE.DM import *
from CORE.Tools import EPSILON


# WD-DLT1m : Weight Deformation
def deform(problem_description, dm):
    dm_best_alternative = dm.best_alternative(problem_description)
    print(dm_best_alternative)
    model = Model("Deformation of DM weight -- Delta 1-m")
    DeviationsSigma = {k: (model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig+_{k}'),
                           model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig-_{k}'))
                       for k in range(problem_description.m)}  # [0] = +; [1] = -
    Assocs_ij = dict()
    E_ijVarDictPlus = dict()
    E_ijVarDictMoins = dict()
    Pros = set()
    Cons = set()
    model.setParam('OutputFlag', False)
    other_alternative_related_swapVar = dict()
    local_epsilon = 0.0001
    for oth_alt in problem_description.alternativesSet:
        if oth_alt != dm_best_alternative:
            array_dif = np.array(dm_best_alternative.attributeLevelsList) - np.array(oth_alt.attributeLevelsList)
            pros, cons = set([i for i in range(len(array_dif)) if array_dif[i] == 1]), set(
                [i for i in range(len(array_dif)) if array_dif[i] == -1])
            Pros = Pros | pros
            Cons = Cons | cons
            print(oth_alt, "pros", pros, "cons", cons)
            other_alternative_related_swapVar[oth_alt] = {
                (i, j): model.addVar(vtype=GRB.BINARY, name=f's_{oth_alt}-{(i, j)}') for i in pros for j in cons}
            E_ijVarDictPlus[oth_alt] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{oth_alt}-{(i, j)}')
                                        for i in pros for j in cons}
            E_ijVarDictMoins[oth_alt] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{oth_alt}-{(i, j)}')
                                         for i in pros for j in cons}

            for j in cons:
                model.addConstr(quicksum([other_alternative_related_swapVar[oth_alt][(i_, j)] for i_ in pros]) == 1)

            for i in pros:
                w_i = dm.utilitiesList[i]
                sig_i_plus = DeviationsSigma[i][0]
                sig_i_moins = DeviationsSigma[i][1]

                model.addConstr(w_i + sig_i_plus - sig_i_moins - quicksum([other_alternative_related_swapVar[oth_alt][
                                                                               (i, j_)] * dm.utilitiesList[j_] +
                                                                           E_ijVarDictPlus[oth_alt][(i, j_)] -
                                                                           E_ijVarDictMoins[oth_alt][(i, j_)] for j_ in
                                                                           cons]) >= local_epsilon)

            # linearisation
            for i in pros:
                for j in cons:
                    sig_j_plus = DeviationsSigma[j][0]
                    sig_j_moins = DeviationsSigma[j][1]

                    model.addConstr(
                        E_ijVarDictPlus[oth_alt][(i, j)] <= other_alternative_related_swapVar[oth_alt][(i, j)])
                    model.addConstr(
                        E_ijVarDictMoins[oth_alt][(i, j)] <= other_alternative_related_swapVar[oth_alt][(i, j)])

                    model.addConstr(E_ijVarDictPlus[oth_alt][(i, j)] <= sig_j_plus)
                    model.addConstr(E_ijVarDictMoins[oth_alt][(i, j)] <= sig_j_moins)

                    model.addConstr(
                        E_ijVarDictPlus[oth_alt][(i, j)] >= sig_j_plus - 1 + other_alternative_related_swapVar[oth_alt][
                            (i, j)])
                    model.addConstr(E_ijVarDictMoins[oth_alt][(i, j)] >= sig_j_moins - 1 +
                                    other_alternative_related_swapVar[oth_alt][(i, j)])

    model.addConstr(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]) == quicksum(
        [sig_pair[1] for sig_pair in DeviationsSigma.values()]))

    for k in range(problem_description.m):
        model.addConstr(DeviationsSigma[k][1] <= dm.utilitiesList[k])

    model.update()
    model.setObjective(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), GRB.MINIMIZE)
    # model.setObjectiveN(quicksum(X.values()), 0, priority=0)
    # model.setObjectiveN(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), 1, priority=1)
    # model.setObjective(Lambda, GRB.MINIMIZE)
    model.optimize()
    print(model.objVal)
    for oth_alt in problem_description.alternativesSet:
        if oth_alt != dm_best_alternative:
            array_dif = np.array(dm_best_alternative.attributeLevelsList) - np.array(oth_alt.attributeLevelsList)
            pros, cons = set([i for i in range(len(array_dif)) if array_dif[i] == 1]), set(
                [i for i in range(len(array_dif)) if array_dif[i] == -1])

            R1m = {i: [j_ for j_ in cons if other_alternative_related_swapVar[oth_alt][(i, j_)].x == 1] for i in pros}
            print(oth_alt, R1m)
            # print(oth_alt, [(i, j) for (i, j), var_ij in other_alternative_related_swapVar[oth_alt].items() if int(var_ij.x) == 1])

    print()
    print("old", [round(dm.utilitiesList[k], 4) for k in range(problem_description.m)])
    print("dv+", [round(DeviationsSigma[k][0].x, 4) for k in range(problem_description.m)])
    print("dv-", [round(DeviationsSigma[k][1].x, 4) for k in range(problem_description.m)])
    print("new", [round(dm.utilitiesList[k] + DeviationsSigma[k][0].x - DeviationsSigma[k][1].x, 4) for k in
                  range(problem_description.m)])


if __name__ == "__main__":
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria7.csv",
                                                  # performanceTableFileName="CSVFILES/kr-v2-7.csv")
                                                  performanceTableFileName="CSVFILES/test-alternatives-7.csv")
    print(mcda_problem_description)
    dm = WS_DM("CSVFILES/DM-kr-v2-7.csv")
    deform(mcda_problem_description, dm)
