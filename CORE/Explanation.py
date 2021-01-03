from gurobipy import *

from CORE.NecessaryPreference import NecessaryPreference
from CORE.Tools import covectorOfPairWiseInformationWith2Levels, EPSILON, tradeoff, Counter, CONSTRAINTSFEASIBILITYTOL
from CORE.decorators import counting
from CORE.AppreciationObject import AppreciationObject

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
        concernedBooleanVarDict = {i: list() for i in set(SigmaD) | set(SigmaP)}
        booleanVarDict = dict()

        for i in SigmaP:
            for j in SigmaD:
                fictious_pair = mcda_problemDescription.fictiousPairsOfAlternatives[(i, j)]
                if NecessaryPreference.adjudicate(mcda_problemDescription, Relation, fictious_pair):
                    edgeCoeffDict[(i, j)] = 1
                else:
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

        matching_gurobi_model.setObjective(
            quicksum([edgeCoeffDict[(i, j)] * booleanVarDict[(i, j)] for i, j in edgeCoeffDict]), GRB.MAXIMIZE)
        matching_gurobi_model.update()

        matching_gurobi_model.optimize()
        explainable = matching_gurobi_model.objVal == len(SigmaD)
        if not explainable: return False, s + "\tCan not explain by swaps of order at most 2"
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
            suiv = mcda_problemDescription.getSwapObject(prec, ({i}, {j}))
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
        concernedBooleanVarDict = {i: list() for i in set(SigmaD) | set(SigmaP)}
        booleanVarDict = dict()

        for i in SigmaP:
            for j in SigmaD:
                fictious_pair = mcda_problemDescription.fictiousPairsOfAlternatives[(j, i)]
                if not NecessaryPreference.adjudicate(mcda_problemDescription, Relation, fictious_pair):
                    edgeCoeffDict[(i, j)] = 1
                else:
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

        matching_gurobi_model.setObjective(
            quicksum([edgeCoeffDict[(i, j)] * booleanVarDict[(i, j)] for i, j in edgeCoeffDict]), GRB.MAXIMIZE)
        matching_gurobi_model.update()

        matching_gurobi_model.optimize()
        explainable = matching_gurobi_model.objVal == len(SigmaD)
        if not explainable: return False, s + "\tCan not explain by swaps of order at most 2"
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
            suiv = mcda_problemDescription.getSwapObject(prec, ({i}, {j}))
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
            if len(path) == 0: path.append(altSource)
            if altSource not in dominationDict: return False
            for altDominatedBySource in dominationDict[altSource]:
                path.append(altDominatedBySource)
                if altDominatedBySource == altDest:
                    return True
                elif is_a_path(altDominatedBySource, altDest, path):
                    return True
                else:
                    path.pop()

        s = "Explanation by Transitivity\n"
        path = list()
        Explanation = list()
        if is_a_path(object[0], object[1], path) and len(path) >= 3:
            for i in range(0, len(path) - 1):
                Explanation.append(mcda_problemDescription.getTransitiveObject(path[i], path[i + 1]))

            for elm in Explanation:
                s += "\t" + str(elm) + "\n"

            return True, s
        else:
            return False, s + "\tCan not explain by transitivity"

    @staticmethod
    def Order2SwapMixedExplanation(mcda_problemDescription=None, Relation=None, object=(None, None)):
        plne_model, VarList, VarDict = mcda_problemDescription.generate_gurobi_model_for_explanation_purposes_and_its_varDict_and_varList(
            "2-Swap Mixed Explanation", EPSILON)
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
                    for bi_sup in range(l_i(i, y) + 1, l_i(i, x) + 1):
                        if bi_inf < bi_sup:
                            for bj_inf in range(l_i(j, x), l_i(j, y)):
                                for bj_sup in range(l_i(j, x) + 1, l_i(j, y) + 1):
                                    if bj_inf < bj_sup:
                                        S.append((i, j, bi_inf, bi_sup, bj_inf, bj_sup))
        # print("======================", Bxy, Lxy)
        VarS = {s: plne_model.addVar(vtype=GRB.BINARY, name=tradeoff(s, VarList)) for s in S}

        plne_model.update()
        # print(VarS.values())

        # Swaps constraints
        for s, bs in VarS.items():
            i, j, bi_inf, bi_sup, bj_inf, bj_sup = s
            # plne_model.addConstr(VarList[i][bi_sup][1] - VarList[i][bi_inf][1] - VarList[j][bj_sup][1] + VarList[j][bj_inf][1] >= (1 + EPSILON)*bs - 1)
            plne_model.addConstr(
                VarList[i][bi_sup][1] - VarList[i][bi_inf][1] - VarList[j][bj_sup][1] + VarList[j][bj_inf][1] >= bs - 1)

        plne_model.update()

        # Lxy Constraints
        for j in Lxy:
            for Ij in range(l_i(j, x), l_i(j, y)):
                cst = LinExpr()
                for s, bs in VarS.items():
                    if j == s[1] and Ij >= s[4] and Ij + 1 <= s[5]:
                        cst += bs
            plne_model.addConstr(cst == 1)

        plne_model.update()

        # Bxy Constraints
        for i in Bxy:
            for Ii in range(l_i(i, y), l_i(i, x)):
                cst = LinExpr()
                for s, bs in VarS.items():
                    if i == s[0] and Ii >= s[2] and Ii + 1 <= s[3]:
                        cst += bs
            plne_model.addConstr(cst <= 1)
        plne_model.update()

        # PI constraints
        if Relation is None:
            Relation = list()
        for (altD, altd) in Relation:
            plne_model.addConstr(altD.linear_expr(VarDict) - altd.linear_expr(VarDict) >= EPSILON)
            # plne_model.addConstr(altD.linear_expr(VarDict) - altd.linear_expr(VarDict) >= 0)
        plne_model.update()

        # VERY VERY SPECIFIC TO BINARY CASE (+ and -)
        NSS = set()  # necessary swap set
        for s, bs in VarS.items():
            i, j, bi_inf, bi_sup, bj_inf, bj_sup = s
            fictious_pair = mcda_problemDescription.fictiousPairsOfAlternatives[(i, j)]
            # print("#####", i, j, covectorOfPairWiseInformationWith2Levels(fictious_pair))
            if NecessaryPreference.adjudicate(mcda_problemDescription, Relation, fictious_pair):
                NSS.add(bs)
        # OBJECTIVE
        plne_model.setObjective(quicksum([bool_var for bool_var in NSS]), GRB.MAXIMIZE)
        # plne_model.setObjective(quicksum([bool_var for bool_var in NSS]), GRB.MINIMIZE)
        plne_model.update()
        # STOP VERY VERY

        plne_model.optimize()
        explainable = plne_model.status == GRB.OPTIMAL
        if not explainable:
            return False, ""

        Explanation_text = "Mixed Explanation computable\n"
        # if plne_model.objVal > 0:
        #     Explanation_text += "... at least one necessary swap\n"
        edgeSelected = list()
        for s, bs in VarS.items():
            # print(s, bs.x)
            if bs.x == 1:
                edgeSelected.append((s[0], s[1]))
                # Explanation_text += "\t" + bs.VarName + "\n"

        # ---
        Explanation = list()
        NecessaryIconeList = list()
        ListAttributeLevelsList = list()
        ListAttributeLevelsList.append(object[0])
        for i, j in edgeSelected:
            prec = ListAttributeLevelsList[-1]
            suiv = mcda_problemDescription.getSwapObject(prec, ({i}, {j}))
            Explanation.append(suiv)
            if suiv.is_necessary(mcda_problemDescription, Relation):
                NecessaryIconeList.append(" * ")
            else:
                NecessaryIconeList.append(" ~ ")
            ListAttributeLevelsList.append(suiv.alternative2)

        for i in range(len(Explanation)):
            elm = str(Explanation[i]) + NecessaryIconeList[i]
            Explanation_text += "\t" + elm + "\n"

        return True, Explanation_text

        # return explainable, tradeoff_used

    @staticmethod
    def atMost2OrderNecessarySwapAndPIExplanation(mcda_problemDescription=None, Relation=None, object=(None, None)):
        if Relation is None:
            Relation = list()

        def get_links(G, s, d, OngoingLinkList, ExplanationList):
            if s == d:
                ExplanationList.append(OngoingLinkList + [d])
            if s in G:
                OngoingLinkList.append(s)
                for succ in G[s]:
                    get_links(G, succ, d, OngoingLinkList, ExplanationList)
                OngoingLinkList.pop()

        source_alternative, dest_alternative = object
        # l : explanation max length (by default equal to n (size of alternatives))
        l = mcda_problemDescription.n + 1
        Graph_of_dominance = dict()
        ListOfESet = [{source_alternative}]
        while len(ListOfESet[-1]) != 0 and l > 0:
            l -= 1
            E_0 = ListOfESet[-1]
            E_1 = set()
            E_0_updated = set()
            while len(E_0) != 0:
                x = E_0.pop()
                Sx = mcda_problemDescription.neighborhoodSet(x, Relation)
                for y in Sx:
                    if ((x, y) in Relation or NecessaryPreference.adjudicate(mcda_problemDescription, Relation,
                                                                             (x, y))) and \
                            NecessaryPreference.adjudicate(mcda_problemDescription, Relation,
                                                           (source_alternative, x)) and \
                            NecessaryPreference.adjudicate(mcda_problemDescription, Relation, (y, dest_alternative)):
                        E_0_updated.add(x)
                        E_1.add(y)
                        if x not in Graph_of_dominance:
                            Graph_of_dominance[x] = set()
                        Graph_of_dominance[x].add(y)

            ListOfESet[-1] = E_0_updated
            ListOfESet.append(E_1)
            # print(ListOfESet)
        ExplanationList = list()
        Explanations = list()
        PI_Icone_List = list()

        L = list()
        get_links(Graph_of_dominance, source_alternative, dest_alternative, L, ExplanationList)
        ExplanationList.sort(key=lambda x: len(x))

        Explanation_text = "All ({}) 2-order necessary swaps + PI (#) Explanations \n".format(len(ExplanationList))
        if len(ExplanationList) == 0:
            return False, Explanation_text + "\tCan not be explained via PI + 2-order necessary swap(s)"

        for path in ExplanationList:
            CorrespondingExplanation = list()
            CorrespondingPIIcone = list()
            for i in range(0, len(path) - 1):
                if (path[i], path[i + 1]) in Relation:
                    CorrespondingPIIcone.append(" # ")
                else:
                    CorrespondingPIIcone.append(" * ")
                CorrespondingExplanation.append(mcda_problemDescription.getTransitiveObject(path[i], path[i + 1]))
            Explanations.append(CorrespondingExplanation)
            PI_Icone_List.append(CorrespondingPIIcone)

        for expl_number in range(len(Explanations)):
            Explanation = Explanations[expl_number]
            Explanation_text += "\tExplanation n° {}\n".format(expl_number + 1)
            for i in range(len(Explanation)):
                elm = Explanation[i]
                Explanation_text += "\t" + str(elm) + PI_Icone_List[expl_number][i] + "\n"
            Explanation_text += "\n"
        return True, Explanation_text

    @staticmethod
    def atMost2OrderNecessarySwapAndPIExplanationAndAtMostOnePossibleSwap(mcda_problemDescription=None, Relation=None,
                                                                          object=(None, None)):
        if Relation is None:
            Relation = list()
        plne_model, VarList, VarDict = mcda_problemDescription.generate_gurobi_model_for_explanation_purposes_and_its_varDict_and_varList(
            "Regret computer Model for 2-order necessary swaps -- PI -- at most one 2-order possible swap -- Explanations", EPSILON)
        # PI constraints
        for (altD, altd) in Relation:
            plne_model.addConstr(altD.linear_expr(VarDict) - altd.linear_expr(VarDict) >= EPSILON)
        plne_model.update()
        # -- End PI constraints

        def depth_first_explanation_computing(alternative_from, length, pswap_used, relation, OngoingLinkList,
                                              expl_list):
            if length == 0:
                return
            if alternative_from == dest_alternative:
                if pswap_used:
                    # AssumptionList.append(relation[-1])
                    expl_list.append((OngoingLinkList + [dest_alternative], relation[-1]))
                else:
                    # AssumptionList.append(None)
                    expl_list.append((OngoingLinkList + [dest_alternative], None))
                # expl_list.append(OngoingLinkList + [dest_alternative])
                return
            a_f_Successors = mcda_problemDescription.neighborhoodSet(alternative_from, relation)
            if len(a_f_Successors) != 0:
                OngoingLinkList.append(alternative_from)
            for succ in a_f_Successors:
                if (alternative_from, succ) in relation or NecessaryPreference.adjudicate(mcda_problemDescription,
                                                                                              relation,
                                                                                              (alternative_from, succ)):
                    if NecessaryPreference.adjudicate(mcda_problemDescription, relation,
                                                      (source_alternative, alternative_from)) and \
                            NecessaryPreference.adjudicate(mcda_problemDescription, Relation, (succ, dest_alternative)):

                            depth_first_explanation_computing(succ, length - 1, pswap_used, relation, OngoingLinkList,
                                                              expl_list)
                elif not pswap_used and not NecessaryPreference.adjudicate(mcda_problemDescription, Relation, (succ, alternative_from)):
                    new_relation = relation + [(alternative_from, succ)]
                    depth_first_explanation_computing(succ, length - 1, True,
                                                      new_relation, OngoingLinkList, expl_list)
            OngoingLinkList.pop()

        source_alternative, dest_alternative = object
        # l : explanation max length (by default equal to n (size of alternatives))
        l = mcda_problemDescription.n + 1
        ExplanationList = list()
        AssumptionList = list()
        L = list()
        depth_first_explanation_computing(source_alternative, l, False, Relation, L, ExplanationList)
        Explanations = list()
        PI_Icone_List = list()

        ExplanationList.sort(key=lambda x: len(x[0]))

        Explanation_text = "All ({}) 2-order necessary swaps (*) + PI (#) + at most one 2-order possible swap (~) Explanations\n".format(
            len(ExplanationList))
        if len(ExplanationList) == 0:
            return False, Explanation_text + "\tCan not be explained via PI + 2-order necessary swap(s) + at most one Possible swap"

        for path, assumption in ExplanationList:
            CorrespondingExplanation = list()
            CorrespondingPIIcone = list()
            for i in range(0, len(path) - 1):
                if (path[i], path[i + 1]) in Relation:
                    CorrespondingPIIcone.append(" # ")
                elif not NecessaryPreference.adjudicate(mcda_problemDescription, Relation, (path[i], path[i + 1])):
                    CorrespondingPIIcone.append(" ~ ")
                else:
                    CorrespondingPIIcone.append(" * ")
                CorrespondingExplanation.append(mcda_problemDescription.getTransitiveObject(path[i], path[i + 1]))
            Explanations.append(CorrespondingExplanation)
            PI_Icone_List.append(CorrespondingPIIcone)
            AssumptionList.append(assumption)


        for expl_number in range(len(Explanations)):
            Explanation = Explanations[expl_number]
            # -- PMR Computation
            pmr_value = max([transitive_obj.pairwise_max_regret(plne_model, VarDict) for transitive_obj in Explanation])
            # --
            Explanation_text += "\tExplanation n° {} (PMR = {})\n".format(expl_number + 1, pmr_value)
            if not (AssumptionList[expl_number] is None):
                Explanation_text += "\t{} H \n\n".format(str(mcda_problemDescription.getTransitiveObject(*AssumptionList[expl_number])))
            for i in range(len(Explanation)):
                elm = Explanation[i]
                Explanation_text += "\t" + str(elm) + PI_Icone_List[expl_number][i] + "\n"
            Explanation_text += "\n"
        return True, Explanation_text

    @staticmethod
    def general_1vsk_MixedExplanation(mcda_problemDescription=None, Relation=None,
                                                                          object=(None, None)):
        if Relation is None:
            Relation = list()
        plne_model, VarList, VarDict = mcda_problemDescription.generate_gurobi_model_for_explanation_purposes_and_its_varDict_and_varList(
            "1 pro vs. k cons Mixed Mixed Explanations", EPSILON)
        # PI constraints
        for (altD, altd) in Relation:
            plne_model.addConstr(altD.linear_expr(VarDict) - altd.linear_expr(VarDict) >= EPSILON)
        plne_model.update()
        # -- End PI constraints

        source_alternative, dest_alternative = object

        pro_argument_set, con_argument_set = AppreciationObject(source_alternative, dest_alternative).pro_arguments_set(), AppreciationObject(dest_alternative, source_alternative).pro_arguments_set()
        # print("pro", pro_argument_set, "con", con_argument_set)
        # autant que la complexité de la question
        plne_model.params.PoolSolutions = len(pro_argument_set) + len(con_argument_set)
        plne_model.params.PoolSearchMode = 2
        plne_model.params.PoolGap = 0

        # k_max : explanation max length (by default equal to n (size of alternatives))
        k_max = 2 #len(con_argument_set)

        # B_kl : dict of b_kl binary variables
        B_kl = {k: {l_: plne_model.addVar(vtype=GRB.BINARY, name="b_{}_{}".format(k, l_))for l_ in con_argument_set} for k in pro_argument_set}
        # B_lk : same as B_kl but indexed first on l
        B_lk = {l_: {k: B_kl[k][l_] for k in pro_argument_set} for l_ in con_argument_set}
        plne_model.update()
        # E_kl : dict of e_kl continuous variables
        E_kl = {k: {l_: plne_model.addVar(vtype=GRB.CONTINUOUS, name="e_{}_{}".format(k, l_), lb=0.0, ub=1.0) for l_ in con_argument_set} for k in pro_argument_set}
        # Cons counterbalanced Constraints
        for l, D in B_lk.items():
            plne_model.addConstr(quicksum(D.values()) <= 1)

        # Capacity Constraints and linearization and kMax Constraints
        for k, D in E_kl.items():
            plne_model.addConstr(quicksum(D.values()) <= VarList[k][1][1])
            kmax_constr = LinExpr()
            for l, e_kl in D.items():
                # plne_model.addConstr(e_kl <= VarList[k][1][1]) # ERREUR
                # plne_model.addConstr(e_kl <= B_kl[k][l])
                # plne_model.addConstr(e_kl >= VarList[k][1][1] + B_kl[k][l] - 1) # ERREUR
                plne_model.addConstr(e_kl <= VarList[l][1][1])
                plne_model.addConstr(e_kl <= B_kl[k][l])
                plne_model.addConstr(e_kl >= VarList[l][1][1] + B_kl[k][l] - 1)

                kmax_constr += B_kl[k][l]
            plne_model.addConstr(kmax_constr <= k_max)

        plne_model.update()

        plne_model.setObjective(quicksum([b_kl for k, D in B_kl.items() for l, b_kl in D.items()]), GRB.MAXIMIZE)
        plne_model.update()
        # print(plne_model.display())
        plne_model.optimize()

        if not plne_model.status == GRB.OPTIMAL :
            return False, "Impossible : au moins un con doit pouvoir être couvert"
        if plne_model.objVal != len(con_argument_set):
            return False, "Can not be explained via General 1 vs. {} mixed explanations".format(k_max)

        OptimalSolutions = list()
        for sol_nb in range(0, plne_model.SolCount):
            plne_model.params.SolutionNumber = sol_nb
            SolDict = {k_: [l_ for l_, v in B_kl[k_].items() if int(v.Xn) == 1] for k_ in B_kl}
            OptimalSolutions.append(SolDict)
            # print([VarList[i][1][1].Xn for i in range(len(VarList))], sum([VarList[i][1][1].Xn for i in range(len(VarList))]))
            # print([VarList[i][0][1].Xn for i in range(len(VarList))], sum([VarList[i][1][1].Xn for i in range(len(VarList))]))
            # print(sol_nb, SolDict, plne_model.PoolObjVal)
            # print({k_: [(l_, v.Xn) for l_, v in B_kl[k_].items() if int(v.Xn) == 1] for k_ in B_kl})
            # print({k: {l_: E_kl[k][l_].Xn for l_ in con_argument_set} for k in pro_argument_set})
        # ---
        Explanation_text = "All ({} / {} required) 1 pro VS. {} con(s) Explanations\n".format(plne_model.SolCount, plne_model.params.PoolSolutions, k_max)
        # Explanations = list()
        for opt_sol_dict in OptimalSolutions:
            Explanation = list()
            NecessaryIconeList = list()
            ListAttributeLevelsList = list()
            ListAttributeLevelsList.append(object[0])
            for i, J in opt_sol_dict.items():
                prec = ListAttributeLevelsList[-1]
                suiv = mcda_problemDescription.getSwapObject(prec, ({i}, set(J)))
                Explanation.append(suiv)
                if suiv.is_necessary(mcda_problemDescription, Relation):
                    NecessaryIconeList.append(" * ")
                else:
                    NecessaryIconeList.append(" ~ ")
                ListAttributeLevelsList.append(suiv.alternative2)

            for i in range(len(Explanation)):
                elm = str(Explanation[i]) + NecessaryIconeList[i]
                Explanation_text += "\t" + elm + "\n"

            Explanation_text += "\n"

        return True, Explanation_text


class ExplanationWrapper():
    counter = Counter()

    def __init__(self, ListOfExplanationEngines, UseAll=True):
        self.ListOfExplanationEngines = ListOfExplanationEngines
        self.useAllEngines = UseAll
        self.explanation = ""
        self.summary = {engine.__name__: 0 for engine in
                        self.ListOfExplanationEngines}  # summary of explanations that have been computed
        self.summary["ALL"] = 0

    @counting(counter)
    def computeExplanation(self, problemDescription, object, **kwargs):
        self.explanation = ""
        # dominanceRelation = kwargs["recommendationDominanceRelation"]
        dominanceRelation = kwargs["dominanceRelation"]
        for engine in self.ListOfExplanationEngines:
            result, detail = engine(problemDescription, dominanceRelation, object)
            if result:
                self.explanation += detail
                self.summary[engine.__name__] += 1
                if not self.useAllEngines: break
        if self.explanation != "":
            self.summary["ALL"] += 1

    def __str__(self):
        s = "\n** EXPLANATION ENGINES PERFORMANCE **\n"
        for engine, n in self.summary.items():
            s += "\t{:<30} : {} / {}\n".format(engine, n, ExplanationWrapper.counter.nb)
        return s

    def reset(self):
        ExplanationWrapper.counter.nb = 0
        for engine_name in self.summary:
            self.summary[engine_name] = 0
