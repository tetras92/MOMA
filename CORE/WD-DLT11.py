from builtins import property

from CORE.ProblemDescription import *
from CORE.DM import *
from CORE.Tools import EPSILON

# WD-DLT11 : Weight Deformation
def deform(problem_description, dm):
    dm_order_of_alternatives = dm.alternatives_ordering_list(problem_description)
    dm_best_alternative = dm_order_of_alternatives[0]
    # dm_best_alternative = dm.best_alternative(problem_description)
    print(dm_best_alternative)
    model = Model("Deformation of DM weight -- Delta 1-1")
    DeviationsSigma = {k: (model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig+_{k}'), model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig-_{k}'))
                       for k in range(problem_description.n)} # [0] = +; [1] = -
    Swaps = dict()
    model.setParam('OutputFlag', False)
    other_alternative_related_swapVar = dict()

    for oth_alt in problem_description.alternativesSet:
        if oth_alt != dm_best_alternative:
            array_dif = np.array(dm_best_alternative.attributeLevelsList) - np.array(oth_alt.attributeLevelsList)
            pros, cons = set([i for i in range(len(array_dif)) if array_dif[i] == 1]), set([i for i in range(len(array_dif)) if array_dif[i] == -1])
            print(oth_alt, "pros", pros, "cons", cons)
            other_alternative_related_swapVar[oth_alt] = {(i, j): model.addVar(vtype=GRB.BINARY, name=f's_{oth_alt}-{(i, j)}') for i in pros for j in cons}
            for j in cons:
                model.addConstr(quicksum([other_alternative_related_swapVar[oth_alt][(i_, j)] for i_ in pros]) == 1)
            for i in pros:
                model.addConstr(quicksum([other_alternative_related_swapVar[oth_alt][(i, j_)] for j_ in cons]) <= 1)
            for i in pros:
                for j in cons:
                    if (i, j) not in Swaps:
                        Swaps[(i, j)] = model.addVar(vtype=GRB.BINARY, name=f's_{(i, j)}')
                    model.addConstr(Swaps[(i, j)] >= other_alternative_related_swapVar[oth_alt][(i, j)])
            # model.addConstr(sum([dm.utilitiesList[k_] for k_ in pros]) - sum([dm.utilitiesList[k_] for k_ in cons])
            #                 + quicksum([DeviationsSigma[k_][0] - DeviationsSigma[k_][1] for k_ in pros]) - quicksum([DeviationsSigma[k_][0] - DeviationsSigma[k_][1] for k_ in cons]) >= EPSILON)


    model.addConstr(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]) == quicksum([sig_pair[1] for sig_pair in DeviationsSigma.values()]))
    for k in range(problem_description.n):
        model.addConstr(DeviationsSigma[k][1] <= dm.utilitiesList[k])

    sum_w = sum(dm.utilitiesList)
    local_epsilon = 0.0001
    for (i, j), var_swap_ij in Swaps.items():
        w_i = dm.utilitiesList[i]
        w_j = dm.utilitiesList[j]
        sig_i_plus = DeviationsSigma[i][0]
        sig_i_moins = DeviationsSigma[i][1]
        sig_j_plus = DeviationsSigma[j][0]
        sig_j_moins = DeviationsSigma[j][1]
        model.addConstr(w_i - w_j + sig_i_plus - sig_i_moins - sig_j_plus + sig_j_moins >= var_swap_ij - sum_w + local_epsilon)

    # Limiter le declassement du critere 1
    # best_criteria = dm.utilitiesList.index(max(dm.utilitiesList))
    # w_star = dm.utilitiesList[best_criteria]
    # sig_star_plus = DeviationsSigma[best_criteria][0]
    # sig_star_moins = DeviationsSigma[best_criteria][1]
    # X = {oth_crit: model.addVar(vtype=GRB.BINARY, name=f'x_{oth_crit}') for oth_crit in range(problem_description.n) if oth_crit != best_criteria}
    # for j, var_xj in X.items():
    #     w_j = dm.utilitiesList[j]
    #     sig_j_plus = DeviationsSigma[j][0]
    #     sig_j_moins = DeviationsSigma[j][1]
    #     model.addConstr(sum_w*var_xj + w_star + sig_star_plus - sig_star_moins >= w_j + sig_j_plus - sig_j_moins)

    # minimiser les deviations
    # Lambda = model.addVar(vtype=GRB.CONTINUOUS, lb=0)
    # for k in range(problem_description.n):
    #     model.addConstr(Lambda >= DeviationsSigma[k][0] - DeviationsSigma[k][1])
    #     model.addConstr(Lambda >= DeviationsSigma[k][1] - DeviationsSigma[k][0])

    model.update()

    YZwVarDict = {(p1, p2): model.addVar(vtype=GRB.BINARY, name=f'b_{(dm_order_of_alternatives[p1], dm_order_of_alternatives[p2])}') for p1 in range(1, len(dm_order_of_alternatives)-1)
                  for p2 in range(p1 + 1, len(dm_order_of_alternatives))}
    Eval_alt_after_deformation_list = [dm.evaluateAlternative(alt) + quicksum([DeviationsSigma[k][0] for k in range(problem_description.n) if alt.attributeLevelsList[k] == 1]) - quicksum([DeviationsSigma[k][1] for k in range(problem_description.n) if alt.attributeLevelsList[k] == 1])
                                       for alt in dm_order_of_alternatives]

    for (p1, p2), yzwVar in YZwVarDict.items():
        model.addConstr(Eval_alt_after_deformation_list[p1] - Eval_alt_after_deformation_list[p2] >= yzwVar - sum_w + local_epsilon)

    model.update()
    # model.setObjective(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), GRB.MINIMIZE)
    # model.setObjective(quicksum(YZwVarDict.values()), GRB.MAXIMIZE)
    model.setObjectiveN(quicksum(YZwVarDict.values()), 0, 1)
    model.setObjectiveN(-quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), 1, 0)
    model.modelSense = -1 # MAXIMISATION



    # model.setObjectiveN(quicksum(X.values()), 0, priority=0)
    # model.setObjectiveN(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), 1, priority=1)
    # model.setObjective(Lambda, GRB.MINIMIZE)
    model.optimize()
    print("objVal", model.objVal, "/", (len(dm_order_of_alternatives) - 1)*(len(dm_order_of_alternatives) - 2)/2, "pairs in YZw")
    for oth_alt in problem_description.alternativesSet:
        if oth_alt != dm_best_alternative:
            print(oth_alt, [(i, j) for (i, j), var_ij in other_alternative_related_swapVar[oth_alt].items() if int(var_ij.x) == 1])

    print([round(dm.utilitiesList[k] + DeviationsSigma[k][0].x - DeviationsSigma[k][1].x, 4) for k in range(problem_description.n)])

if __name__ == "__main__":
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria7.csv",
                                                  performanceTableFileName="CSVFILES/test-alternatives-7.csv")
    print(mcda_problem_description)
    dm = WS_DM("CSVFILES/DM-kr-v2-7.csv")
    deform(mcda_problem_description, dm)
