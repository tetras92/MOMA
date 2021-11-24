import numpy as np
from gurobipy import *

from CORE.Tools import covectorOfPairWiseInformationWith2Levels
from CORE.Tools import CONSTRAINTSFEASIBILITYTOL, EPSILON, EMPTYSET
from itertools import permutations, product
from CORE.AppreciationObject import AppreciationObject

from CORE.ProblemDescription import *

class ExplanationBasedElicitation:
    @staticmethod
    def adjudicate(mcda_problemDescription=None, best_alternative=None, other_alternatives=None, Relation=None):
        if Relation is None:
            Relation = list()

        model, VarList, VarDict = mcda_problemDescription.generate_gurobi_model_for_explanation_purposes_and_its_varDict_and_varList(
            "MOMBA is best_alternative in EPB (see def EXPLANATION SUMMER 2021)", EPSILON)

        # PI CONSTRAINTS
        for (altD, altd) in Relation:
            model.addConstr(altD.linear_expr(VarDict) - altd.linear_expr(VarDict) >= EPSILON)
            
        # model.Params.FeasibilityTol = CONSTRAINTSFEASIBILITYTOL

        # oth_alt_to_consider_indexes_set : other alternatives y such that (best_alternative, y) not in relation
        oth_alt_to_consider_indexes_set = {k for k in range(len(other_alternatives)) if (best_alternative, other_alternatives[k]) not in Relation}
        if len(oth_alt_to_consider_indexes_set) == 0:
            # status, number_of_pairs_explained, number_of_pairsi_n_K_ACS, List_of_Corresponding_swaps
            return True, 0, len(other_alternatives), [list() for k in range(len(other_alternatives))]


        # ProConDict : dico d'index pris dans oth_alt_to_consider_indexes_set et de valeur la paire ((x, y)^+, (x, y)^-)
        ProConDict = {k: (AppreciationObject(best_alternative, other_alternatives[k]).pro_arguments_set(), AppreciationObject(best_alternative, other_alternatives[k]).con_arguments_set())
                      for k in oth_alt_to_consider_indexes_set}

        # BooleanSwapsSetDict : dico d'index pris dans oth_alt_to_consider_indexes_set et de valeur un dico (i, j) : b_ij^k variable booleene correspondant au swap (i, j)
        BooleanSwapsSetDict = {k: {(i, j): model.addVar(vtype=GRB.BINARY, name="b_{}_{}".format((i, j), k)) for i in ProConDict[k][0] for j in ProConDict[k][1]}
                               for k in oth_alt_to_consider_indexes_set}

        # Ajouter les contraintes de compatibilité
        for k, ijDict in BooleanSwapsSetDict.items():
            for (i, j), varBij in ijDict.items():
                model.addConstr(VarList[i][1][1] - VarList[j][1][1] >= varBij - 1 + EPSILON)

        model.update()

        # Ajouter les contraintes : tout con couvert
        for k, ijDict in BooleanSwapsSetDict.items():
            for j_ in ProConDict[k][1]:
                model.addConstr(quicksum([varBij for (i, j), varBij in ijDict.items() if j == j_]) == 1)
        model.update()

        # Ajouter les contraintes : tout pro utilisé au plus une fois couvert
        for k, ijDict in BooleanSwapsSetDict.items():
            for i_ in ProConDict[k][0]:
                model.addConstr(quicksum([varBij for (i, j), varBij in ijDict.items() if i == i_]) <= 1)
        model.update()

        model.optimize()

        status = model.status == GRB.OPTIMAL
        if status:
            DictOfSwaps = {k: [(i, j) for (i, j), varBij in ijDict.items() if int(varBij.x) == 1] + [(i, EMPTYSET) for i in ProConDict[k][0] if sum([int(varbij.x) for (i_, j_), varbij in ijDict.items() if i_ == i]) == 0]
                           for k, ijDict in BooleanSwapsSetDict.items()}

            ListOfSwaps = list()
            number_of_pairs_in_K_ACS = 0
            for k in range(len(other_alternatives)):
                if k in oth_alt_to_consider_indexes_set:
                    ListOfSwaps.append(DictOfSwaps[k])
                else:
                    ListOfSwaps.append(list())
                    number_of_pairs_in_K_ACS += 1
            # status, number_of_pairs_explained, number_of_pairs_in_K_ACS, List_of_Corresponding_swaps
            return True, len(oth_alt_to_consider_indexes_set), number_of_pairs_in_K_ACS, ListOfSwaps

        # À AMELIORER POUR MAXIMISER LE NOMBRE DE PAIRES EXPLICABLES
        return False, 0, len(other_alternatives) - len(oth_alt_to_consider_indexes_set), [list() for k in range(len(other_alternatives))]

        # print(VarList)
        # print("\n\n", VarDict)


if __name__ == "__main__":

    # m = 7
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria7.csv",
                                                  performanceTableFileName="CSVFILES/test-alternatives-7.csv")
    print(ExplanationBasedElicitation.adjudicate(mcda_problem_description, mcda_problem_description[20],
                                           [mcda_problem_description[19],  mcda_problem_description[18],  mcda_problem_description[21]]))
