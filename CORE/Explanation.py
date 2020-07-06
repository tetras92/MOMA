from gurobipy import *

from CORE.NecessaryPreference import NecessaryPreference
from CORE.Tools import covectorOfPairWiseInformationWith2Levels, EPSILON, tradeoff, Counter
from CORE.decorators import counting

class Explain:

    @staticmethod
    def Order2SwapExplanation(mcda_problemDescription=None, Relation=None, object=(None, None)):
        if Relation is None:
            Relation = list()
        s = "Explanation by at most 2-order necessary swaps\n"
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

        # print("NECESSAIRE", edgeCoeffDict)
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
        if not explainable : return False, s + "\tCan not explain by swaps of order at most 2"
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

        for elm in Explanation:
            s += "\t" + str(elm) + "\n"


        return True, s

    @staticmethod
    def Order2SwapPossibleExplanation(mcda_problemDescription=None, Relation=None, object=(None, None)):
        if Relation is None:
            Relation = list()
        s = "Explanation by at most 2-order possible swaps\n"
        object_covector = covectorOfPairWiseInformationWith2Levels(object)
        SigmaP = [i for i in range(len(object_covector)) if object_covector[i] == 1]
        SigmaD = [i for i in range(len(object_covector)) if object_covector[i] == -1]

        edgeCoeffDict = dict()
        concernedBooleanVarDict = {i : list() for i in set(SigmaD) | set(SigmaP)}
        booleanVarDict = dict()

        for i in SigmaP :
            for j in SigmaD :
                fictious_pair = mcda_problemDescription.fictiousPairsOfAlternatives[(j, i)]
                if not NecessaryPreference.adjudicate(mcda_problemDescription, Relation, fictious_pair):
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
        print("POSSIBLE", edgeCoeffDict)
        matching_gurobi_model.update()
        for i, VarList in concernedBooleanVarDict.items():
            matching_gurobi_model.addConstr(quicksum(VarList) <= 1)

        matching_gurobi_model.setObjective(quicksum([edgeCoeffDict[(i, j)]*booleanVarDict[(i, j)] for i, j in edgeCoeffDict]), GRB.MAXIMIZE)
        matching_gurobi_model.update()

        matching_gurobi_model.optimize()
        explainable = matching_gurobi_model.objVal == len(SigmaD)
        if not explainable : return False, s + "\tCan not explain by swaps of order at most 2"
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

        for elm in Explanation:
            s += "\t" + str(elm) + "\n"


        return True, s



    @staticmethod
    def TransitiveExplanation(mcda_problemDescription=None, Relation=None, object=(None, None)):
        if Relation is None:
            Relation = list()
        dominationDict = dict()
        for (altD, altd) in Relation:
            if altD not in dominationDict:
                dominationDict[altD] = list()
            dominationDict[altD].append(altd)


        def is_a_path(altSource, altDest, path):
            if len(path) == 0 : path.append(altSource)
            if altSource not in dominationDict : return False
            for altDominatedBySource in dominationDict[altSource]:
                path.append(altDominatedBySource)
                if altDominatedBySource == altDest: return True
                elif is_a_path(altDominatedBySource, altDest, path): return True
                else : path.pop()

        s = "Explanation by Transitivity\n"
        path = list()
        Explanation = list()
        if is_a_path(object[0], object[1], path) and len(path) >= 3:
            for i in range(0, len(path)-1):
                Explanation.append(mcda_problemDescription.getTransitiveObject(path[i], path[i+1]))

            for elm in Explanation:
                s += "\t" + str(elm) + "\n"

            return True, s
        else:
            return False, s + "\tCan not explain by transitivity"

    @staticmethod
    def Order2SwapMixedExplanation(mcda_problemDescription=None, Relation=None, object=(None, None)):
        plne_model, VarList, VarDict = mcda_problemDescription.generate_gurobi_model_for_explanation_purposes_and_its_varDict_and_varList("2-Swap Mixed Explanation", EPSILON)
        x, y = object
        object_covector = covectorOfPairWiseInformationWith2Levels(object)
        Bxy = [i for i in range(len(object_covector)) if object_covector[i] == 1]
        Lxy = [i for i in range(len(object_covector)) if object_covector[i] == -1]

        if len(Bxy) == len(Lxy) and len(Bxy) == 1:
            return True, "Exempted of 2-Swap Explanation"
        def l_i(i, alt):
            return alt.attributeLevelsList[i]

        S = list()  # Swaps space
        for i in Bxy:
            for j in Lxy:
                for bi_inf in range(l_i(i, y), l_i(i, x)):
                    for bi_sup in range(l_i(i, y) + 1, l_i(i, x) + 1 ):
                        if bi_inf < bi_sup :
                            for bj_inf in range(l_i(j, x), l_i(j, y)):
                                for bj_sup in range(l_i(j, x) + 1, l_i(j, y) + 1):
                                    if bj_inf < bj_sup:
                                        S.append((i,j,bi_inf,bi_sup,bj_inf,bj_sup))
        # print("======================", Bxy, Lxy)
        VarS = {s : plne_model.addVar(vtype=GRB.BINARY, name=tradeoff(s, VarList)) for s in S}

        plne_model.update()
        # print(VarS.values())

        # Swaps constraints
        for s, bs in VarS.items():
            i, j, bi_inf, bi_sup, bj_inf, bj_sup = s
            # plne_model.addConstr(VarList[i][bi_sup][1] - VarList[i][bi_inf][1] - VarList[j][bj_sup][1] + VarList[j][bj_inf][1] >= (1 + EPSILON)*bs - 1)
            plne_model.addConstr(VarList[i][bi_sup][1] - VarList[i][bi_inf][1] - VarList[j][bj_sup][1] + VarList[j][bj_inf][1] >= bs - 1)

        plne_model.update()

        #Lxy Constraints
        for j in Lxy:
            for Ij in range(l_i(j, x), l_i(j, y)):
                cst = LinExpr()
                for s, bs in VarS.items():
                    if j == s[1] and Ij >= s[4] and Ij + 1 <= s[5]:
                        cst += bs
            plne_model.addConstr(cst == 1)

        plne_model.update()

        #Bxy Constraints
        for i in Bxy:
            for Ii in range(l_i(i, y), l_i(i, x)):
                cst =LinExpr()
                for s, bs in VarS.items():
                    if i == s[0] and Ii >= s[2] and Ii + 1 <= s[3]:
                        cst += bs
            plne_model.addConstr(cst <= 1)
        plne_model.update()

        #PI constraints
        if Relation is None:
            Relation = list()
        for (altD, altd) in Relation:
            plne_model.addConstr(altD.linear_expr(VarDict) - altd.linear_expr(VarDict) >= EPSILON)
            # plne_model.addConstr(altD.linear_expr(VarDict) - altd.linear_expr(VarDict) >= 0)
        plne_model.update()

        plne_model.optimize()
        explainable = plne_model.status == GRB.OPTIMAL
        if not explainable:
            return False, ""

        Explanation_text = "Mixed Explanation computable\n"
        edgeSelected = list()
        for s, bs in VarS.items():
            # print(s, bs.x)
            if bs.x == 1:
                edgeSelected.append((s[0], s[1]))
                # Explanation_text += "\t" + bs.VarName + "\n"

        # ---
        Explanation = list()
        ListAttributeLevelsList = list()
        ListAttributeLevelsList.append(object[0])
        for i, j in edgeSelected:
            prec = ListAttributeLevelsList[-1]
            suiv = mcda_problemDescription.getSwapObject(prec, (i, j))
            Explanation.append(suiv)
            ListAttributeLevelsList.append(suiv.alternative2)

        for elm in Explanation:
            Explanation_text += "\t" + str(elm) + "\n"


        return True, Explanation_text

        # return explainable, tradeoff_used

class ExplanationWrapper():
    counter = Counter()
    def __init__(self, ListOfExplanationEngines, UseAll=True):
        self.ListOfExplanationEngines = ListOfExplanationEngines
        self.useAllEngines = UseAll
        self.explanation = ""
        self.summary = {engine.__name__ : 0 for engine in self.ListOfExplanationEngines} # summary of explanations that have been computed
        self.summary["ALL"] = 0


    @counting(counter)
    def computeExplanation(self, problemDescription, object, **kwargs):
        self.explanation = ""
        dominanceRelation = kwargs["dominanceRelation"]
        for engine in self.ListOfExplanationEngines:
            result, detail = engine(problemDescription, dominanceRelation, object)
            if result :
                self.explanation += detail
                self.summary[engine.__name__] += 1
                if not self.useAllEngines : break
        if self.explanation != "" :
            self.summary["ALL"] += 1

    def __str__(self):
        s = "\n** EXPLANATION ENGINES PERFORMANCE **\n"
        for engine, n in self.summary.items():
                s += "\t{:<30} : {} / {}\n".format(engine, n, ExplanationWrapper.counter.nb)
        return s
