from gurobipy import *

from CORE.NecessaryPreference import NecessaryPreference
from CORE.Tools import covectorOfPairWiseInformationWith2Levels


class Explain:

    @staticmethod
    def Order2SwapExplanation(mcda_problemDescription=None, Relation=None, object=(None, None)):
        if Relation is None:
            Relation = list()

        object_covector = covectorOfPairWiseInformationWith2Levels(object)
        SigmaP = [i for i in range(len(object_covector)) if object_covector[i] == 1]
        SigmaD = [i for i in range(len(object_covector)) if object_covector[i] == -1]

        edgeCoeffDict = dict()
        concernedBooleanVarDict = {i : list() for i in set(SigmaD) | set(SigmaP)}
        booleanVarDict = dict()

        for i in SigmaP :
            for j in SigmaD :
                fictious_pair = mcda_problemDescription.fictiousPairsOfAlternatives[(i, j)]
                if NecessaryPreference.adjudicate(mcda_problemDescription, Relation, fictious_pair):
                    edgeCoeffDict[(i, j)] = 1
                else :
                    edgeCoeffDict[(i, j)] = 0

        matching_gurobi_model = Model("Explain Matching Model")
        matching_gurobi_model.setParam('OutputFlag', False)
        for i, j in edgeCoeffDict:
            var_ij = matching_gurobi_model.addVar(vtype=GRB.BINARY, name="B_{}_{}".format(i, j))
            concernedBooleanVarDict[i].append(var_ij)
            concernedBooleanVarDict[j].append(var_ij)
            booleanVarDict[(i, j)] = var_ij

        matching_gurobi_model.update()
        for i, VarList in concernedBooleanVarDict.items():
            matching_gurobi_model.addConstr(quicksum(VarList) <= 1)

        matching_gurobi_model.setObjective(quicksum([edgeCoeffDict[(i, j)]*booleanVarDict[(i, j)] for i, j in edgeCoeffDict]), GRB.MAXIMIZE)
        matching_gurobi_model.update()

        matching_gurobi_model.optimize()
        explainable = matching_gurobi_model.objVal == len(SigmaD)
        if not explainable : return "Can not explain by swaps of order at most 2"
        edgeSelected = list()
        for i, j in booleanVarDict:
            if booleanVarDict[(i, j)].x == 1:
                edgeSelected.append((i, j))
        # ---
        Explanation = list()
        ListAttributeLevelsList = list()
        ListAttributeLevelsList.append(object[0])
        for i, j in edgeSelected:
            prec = ListAttributeLevelsList[-1]
            suiv = mcda_problemDescription.getSwapObject(prec, (i, j))
            Explanation.append(suiv)
            ListAttributeLevelsList.append(suiv.alternative2)

        s = "Explanation\n"
        i = 1
        for elm in Explanation:
            s += str(elm)
            s += "\n" + "\t"*i
            i += 1

        return s
