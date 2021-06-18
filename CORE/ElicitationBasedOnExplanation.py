import numpy as np
from gurobipy import *

from CORE.Tools import covectorOfPairWiseInformationWith2Levels
from CORE.Tools import CONSTRAINTSFEASIBILITYTOL, EPSILON
from itertools import permutations, product

class ExplanationBasedElicitation:
    @staticmethod
    def adjudicate(mcda_problemDescription=None, best_alternative=None, other_alternatives=None, Relation=None):
        if Relation is None:
            Relation = list()

        model, VarList, VarDict = mcda_problemDescription.generate_gurobi_model_for_explanation_purposes_and_its_varDict_and_varList(
            "MOMBA Explanation Based Elicitation fragment", EPSILON)

        model.Params.FeasibilityTol = CONSTRAINTSFEASIBILITYTOL

        # best_alternative := X
        # an other_alternative := Y

        XYCovList = [covectorOfPairWiseInformationWith2Levels((best_alternative, y)) for y in other_alternatives]

        # BaseVectorVar : ici la base ce sont les swaps retenus ainsi que les paires (x,y) non explicables par des swaps
        BaseVectorVar = [model.addVar(vtype=GRB.BINARY, name="({}, {})_in_base".format(best_alternative, y)) for y in other_alternatives]

        # AllSwapsList : List[(i, j)]
        AllSwapsList = list(permutations(range(1, mcda_problemDescription.n +1), 2))

        # AllSwapsCovectorDict : Dict[tuple(int, int), np.array]
        def swap_covector(i, j):
            res = np.zeros(mcda_problemDescription.n)
            res[i-1] = 1
            res[j-1] = -1
            return res
        AllSwapsCovectorDict = {(i, j): swap_covector(i, j) for (i, j) in AllSwapsList}

        BooleanSwapsCoeffDict = {k: {(i, j): model.addVar(vtype=GRB.BINARY, name="c_{}_{}".format((i, j), k)) for (i, j) in AllSwapsList if XYCovList[k][i-1] == 1 and XYCovList[k][j-1] == -1}
                                 for k in range(len(other_alternatives))}

        VarMDict = {k: [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="M_{}_{}".format(i, k)) for i in range(mcda_problemDescription.n)] for k in range(len(other_alternatives))}


        # PI CONSTRAINTS
        for (altD, altd) in Relation:
            model.addConstr(altD.linear_expr(VarDict) - altd.linear_expr(VarDict) >= EPSILON)

        # X the best alternative CONSTRAINTS
        for y in other_alternatives:
            model.addConstr(best_alternative.linear_expr(VarDict) - y.linear_expr(VarDict) >= EPSILON)

        model.update()

        DoublonsAvoidanceDict = dict()
        # Swaps selected consequence
        # for (i, j) in AllSwapsList:
        #     for k in range(len(other_alternatives)):
        for k, ijDict in BooleanSwapsCoeffDict.items():
            for (i, j) in ijDict:
                model.addConstr(VarList[i-1][1][1] - VarList[j-1][1][1] >= BooleanSwapsCoeffDict[k][(i, j)] - 1)
                # Profitons pour stocker les var (i, j)
                min_, max_ = min(i, j), max(i, j)
                if (min_, max_) not in DoublonsAvoidanceDict:
                    DoublonsAvoidanceDict[(min_, max_)] = {True : set(), False : set()}
                if (min_, max_) == (i, j):
                    DoublonsAvoidanceDict[(min_, max_)][True].add(ijDict[(i, j)])
                else:
                    DoublonsAvoidanceDict[(min_, max_)][False].add(ijDict[(i, j)])
                # model.addConstr(VarList[i-1][1][1] - VarList[j-1][1][1] >= (1 + EPSILON)*BooleanSwapsCoeffDict[k][(i, j)] - 1)

        # Swaps equivalence avoidance
        # for (i, j) in AllSwapsList:
        #     model.addConstr(quicksum([BooleanSwapsCoeffDict[k][(i, j)] for k in range(len(other_alternatives))]) + quicksum([BooleanSwapsCoeffDict[k][(j, i)] for k in range(len(other_alternatives))]) <= 1)

        for _, trueFalseDict in DoublonsAvoidanceDict.items():
            Product = list(product(trueFalseDict[True], trueFalseDict[False]))
            for (P1, P2) in Product:
                model.addConstr(P1 + P2 <= 1)

        for k in range(len(XYCovList)):
            object_covector = XYCovList[k]
            Member_p_0 = np.array([BaseVectorVar[k]]*mcda_problemDescription.n) * object_covector
            To_accumulate = list()
            # for (i, j) in AllSwapsList:
            for (i, j) in BooleanSwapsCoeffDict[k]:
                var_ij_k = BooleanSwapsCoeffDict[k][(i, j)]
                To_accumulate.append(np.array([var_ij_k]*mcda_problemDescription.n) * AllSwapsCovectorDict[(i, j)])
            Member_p_1 = [quicksum([element_of_To_accumulate[i_] for element_of_To_accumulate in To_accumulate]) for i_ in range(mcda_problemDescription.n)]
            Member_p_2 = VarMDict[k]

            for i in range(mcda_problemDescription.n):
                model.addConstr(Member_p_0[i] + Member_p_1[i] + Member_p_2[i] == object_covector[i])
            model.update()

        model.setObjective(quicksum(BaseVectorVar), GRB.MINIMIZE)
        model.optimize()

        status = model.status == GRB.OPTIMAL
        if status:
            number_of_pairs_explained = len(other_alternatives) - int(model.objVal)
            percentage = round(number_of_pairs_explained / len(other_alternatives), 2)
            List_of_swap_used = [[(i, j) for (i, j) in BooleanSwapsCoeffDict[k] if int(BooleanSwapsCoeffDict[k][(i, j)].x) == 1] for k in range(len(XYCovList))]

            return status, number_of_pairs_explained, percentage, List_of_swap_used
        return False, 0, 0, list()
