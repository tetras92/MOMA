from builtins import property

from CORE.ProblemDescription import *
from CORE.DM import *
from CORE.Tools import EPSILON
from CORE.PLNE_for_Delta11_decomposition import decompose as decompose_under_L0
from CORE.PLNE_for_Delta1m_decomposition import decompose as decompose_under_L1
from CORE.PLNE_for_Deltam1_decomposition import decompose as decompose_under_L2
from CORE.PLNE_for_Delta1m_m1_decomposition import decompose as decompose_under_L3

from datetime import datetime

m = 6
local_epsilon = 0.0001


# # --- A IMPORTER NORMALEMENT
# def encode_preference_model_as_dict(filename):
#     with open(filename) as preferenceModelFile:
#         reader = csv.DictReader(preferenceModelFile)
#         w_list = list()
#         for row in reader:
#             for criterion in reader.fieldnames:
#                 w_list.append(int(row[criterion]))
#         w_list = sorted(w_list, reverse=True)
#         return {chr(ord('a') + i): w_list[i] for i in range(m)}
#
#
# def recommendation_algorithm(AlternativesSubsetsList, Wdict, decomposition_function=None):
#     SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
#                                            key=lambda alt: sum([Wdict[criterion] for criterion in alt]), reverse=True)
#     S_ = [None]
#     for v in range(1, len(SortedAlternativesSubsetsList)):
#         proSet, conSet = SortedAlternativesSubsetsList[0] - SortedAlternativesSubsetsList[v], \
#                          SortedAlternativesSubsetsList[v] - SortedAlternativesSubsetsList[0]
#         success_v, Sv = decomposition_function(proSet, conSet, Wdict)
#         if not success_v:
#             return False, None
#         else:
#             S_.append(Sv)
#
#     return True, S_
#
#
# def generate_n_alternatives_as_subsets(n):
#     while True:
#         L = [integer_to_bin(x) for x in generate_n_integers(n)]
#         chk1, _ = check1(L)
#         chk2, _ = check2(L)
#         if chk1 and chk2:
#             break
#     return [{chr(ord('a') + i) for i in range(m) if alt[i] == '1'} for alt in L]
#
#
# def generate_n_integers(n):
#     return list(*np.random.choice(range(1, 2 ** m - 1), size=(1, n), replace=False))
#
#
# def integer_to_bin(val_int):
#     return format(val_int, "b").zfill(m)
#
#
# def check1(A_binary_encoding_list):
#     """significativite des m criteres"""
#     for i in range(m):
#         if all([alt[i] == '0' for alt in A_binary_encoding_list]) or all(
#                 [alt[i] == '1' for alt in A_binary_encoding_list]):
#             return False, i
#
#     return True, None
#
#
# def check2(A_binary_encoding_list):
#     """absence de dominance"""
#
#     for k1 in range(len(A_binary_encoding_list) - 1):
#         alt1 = A_binary_encoding_list[k1]
#         alt1_int = [int(alt1[i]) for i in range(m)]
#         for k2 in range(k1 + 1, len(A_binary_encoding_list)):
#             alt2 = A_binary_encoding_list[k2]
#             alt2_int = [int(alt2[i]) for i in range(m)]
#             if all([alt1_int[i] >= alt2_int[i] for i in range(m)]) or all(
#                     [alt2_int[i] >= alt1_int[i] for i in range(m)]):
#                 return False, (alt1, alt2)
#     return True, None


# ---- A IMPORTER NORMALEMENT FIN


def recommendation_after_deformation_L0(AlternativesSubsetsList, W_dict):
    SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                           key=lambda alt: sum([W_dict[criterion] for criterion in alt]), reverse=True)

    model = Model("Deformation of DM weight -- Delta 1-1")
    DeviationsSigma = {k: (model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig+_{k}'),
                           model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig-_{k}'))
                       for k in W_dict}  # [0] = +; [1] = -
    Swaps = dict()
    model.setParam('OutputFlag', False)
    other_alternative_related_swapVar = dict()

    for v in range(1, len(SortedAlternativesSubsetsList)):
        oth_alt = SortedAlternativesSubsetsList[v]
        pros, cons = SortedAlternativesSubsetsList[0] - oth_alt, oth_alt - SortedAlternativesSubsetsList[0]
        other_alternative_related_swapVar[v] = {
            (i, j): model.addVar(vtype=GRB.BINARY, name=f's_{oth_alt}-{(i, j)}') for i in pros for j in cons}
        for j in cons:
            model.addConstr(quicksum([other_alternative_related_swapVar[v][(i_, j)] for i_ in pros]) == 1)
        for i in pros:
            model.addConstr(quicksum([other_alternative_related_swapVar[v][(i, j_)] for j_ in cons]) <= 1)
        for i in pros:
            for j in cons:
                if (i, j) not in Swaps:
                    Swaps[(i, j)] = model.addVar(vtype=GRB.BINARY, name=f's_{(i, j)}')
                model.addConstr(Swaps[(i, j)] >= other_alternative_related_swapVar[v][(i, j)])

    model.addConstr(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]) == quicksum(
        [sig_pair[1] for sig_pair in DeviationsSigma.values()]))

    sum_w = 1. * sum(W_dict.values())
    W_dict = {k: vk / sum_w for k, vk in W_dict.items()}

    for k in W_dict:
        model.addConstr(DeviationsSigma[k][1] <= W_dict[k])

    for (i, j), var_swap_ij in Swaps.items():
        w_i = W_dict[i]
        w_j = W_dict[j]
        sig_i_plus = DeviationsSigma[i][0]
        sig_i_moins = DeviationsSigma[i][1]
        sig_j_plus = DeviationsSigma[j][0]
        sig_j_moins = DeviationsSigma[j][1]
        model.addConstr(
            w_i - w_j + sig_i_plus - sig_i_moins - sig_j_plus + sig_j_moins >= var_swap_ij - sum_w + local_epsilon)

    model.update()
    model.setObjective(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), GRB.MINIMIZE)
    model.optimize()
    if model.status == GRB.OPTIMAL:
        return True, float(model.objVal) == 0.0
        # criteria_order_w_r_t_w_dict = sorted(W_dict.keys(), key=lambda crit: W_dict[crit], reverse=True)
        #
        # criteria_order_w_r_t_w_dict_deformed = sorted(W_dict.keys(),
        #                                               key=lambda crit: W_dict[crit] + DeviationsSigma[k][0].x -
        #                                                                DeviationsSigma[k][1].x, reverse=True)
        # # print(criteria_order_w_r_t_w_dict_deformed)
        # bijection_criteria = {criteria_order_w_r_t_w_dict[i_crit]: criteria_order_w_r_t_w_dict_deformed[i_crit]
        #                       for i_crit in range(len(criteria_order_w_r_t_w_dict))}
        # # print(model.objVal)
        # for v in range(1, len(SortedAlternativesSubsetsList)):
        #     oth_alt = SortedAlternativesSubsetsList[v]
        #     # print(oth_alt, [(i, j) for (i, j), var_ij in other_alternative_related_swapVar[v].items() if
        #     #                 int(var_ij.x) == 1])
        # SortedAlternativesSubsetsListTranslated = [{bijection_criteria[crit] for crit in alt} for alt in
        #                                            SortedAlternativesSubsetsList]
        # return True, SortedAlternativesSubsetsListTranslated

    # print("Deformation Impossible")
    return False, None


def recommendation_after_deformation_L1(AlternativesSubsetsList, W_dict):
    SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                           key=lambda alt: sum([W_dict[criterion] for criterion in alt]), reverse=True)

    model = Model("Deformation of DM weight -- Delta 1-m")
    DeviationsSigma = {k: (model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig+_{k}'),
                           model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig-_{k}'))
                       for k in W_dict}  # [0] = +; [1] = -

    model.setParam('OutputFlag', False)
    other_alternative_related_swapVar = dict()

    E_ijVarDictPlus = dict()
    E_ijVarDictMoins = dict()
    sum_w = 1. * sum(W_dict.values())
    W_dict = {k: vk / sum_w for k, vk in W_dict.items()}

    for v in range(1, len(SortedAlternativesSubsetsList)):
        oth_alt = SortedAlternativesSubsetsList[v]
        pros, cons = SortedAlternativesSubsetsList[0] - oth_alt, oth_alt - SortedAlternativesSubsetsList[0]
        other_alternative_related_swapVar[v] = {
            (i, j): model.addVar(vtype=GRB.BINARY, name=f's_{oth_alt}-{(i, j)}') for i in pros for j in cons}

        E_ijVarDictPlus[v] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{oth_alt}-{(i, j)}')
                              for i in pros for j in cons}
        E_ijVarDictMoins[v] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{oth_alt}-{(i, j)}')
                               for i in pros for j in cons}

        for j in cons:
            model.addConstr(quicksum([other_alternative_related_swapVar[v][(i_, j)] for i_ in pros]) == 1)

        for i in pros:
            w_i = W_dict[i]
            sig_i_plus = DeviationsSigma[i][0]
            sig_i_moins = DeviationsSigma[i][1]

            model.addConstr(w_i + sig_i_plus - sig_i_moins - quicksum([other_alternative_related_swapVar[v][
                                                                           (i, j_)] * W_dict[j_] +
                                                                       E_ijVarDictPlus[v][(i, j_)] -
                                                                       E_ijVarDictMoins[v][(i, j_)] for j_ in
                                                                       cons]) >= local_epsilon)
        # Linearization
        for i in pros:
            for j in cons:
                sig_j_plus = DeviationsSigma[j][0]
                sig_j_moins = DeviationsSigma[j][1]

                model.addConstr(
                    E_ijVarDictPlus[v][(i, j)] <= other_alternative_related_swapVar[v][(i, j)])
                model.addConstr(
                    E_ijVarDictMoins[v][(i, j)] <= other_alternative_related_swapVar[v][(i, j)])

                model.addConstr(E_ijVarDictPlus[v][(i, j)] <= sig_j_plus)
                model.addConstr(E_ijVarDictMoins[v][(i, j)] <= sig_j_moins)

                model.addConstr(
                    E_ijVarDictPlus[v][(i, j)] >= sig_j_plus - 1 + other_alternative_related_swapVar[v][
                        (i, j)])
                model.addConstr(E_ijVarDictMoins[v][(i, j)] >= sig_j_moins - 1 +
                                other_alternative_related_swapVar[v][(i, j)])

    for k in W_dict:
        model.addConstr(DeviationsSigma[k][1] <= W_dict[k])

    model.addConstr(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]) == quicksum(
        [sig_pair[1] for sig_pair in DeviationsSigma.values()]))

    model.update()
    model.setObjective(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), GRB.MINIMIZE)
    model.optimize()
    if model.status == GRB.OPTIMAL:
        return True, float(model.objVal) == 0.0

    return False, None


def recommendation_after_deformation_L2(AlternativesSubsetsList, W_dict):
    SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                           key=lambda alt: sum([W_dict[criterion] for criterion in alt]), reverse=True)

    model = Model("Deformation of DM weight -- Delta m-1")
    DeviationsSigma = {k: (model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig+_{k}'),
                           model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig-_{k}'))
                       for k in W_dict}  # [0] = +; [1] = -

    model.setParam('OutputFlag', False)
    other_alternative_related_swapVar = dict()

    E_ijVarDictPlus = dict()
    E_ijVarDictMoins = dict()
    sum_w = 1. * sum(W_dict.values())
    W_dict = {k: vk / sum_w for k, vk in W_dict.items()}

    for v in range(1, len(SortedAlternativesSubsetsList)):
        oth_alt = SortedAlternativesSubsetsList[v]
        pros, cons = SortedAlternativesSubsetsList[0] - oth_alt, oth_alt - SortedAlternativesSubsetsList[0]
        other_alternative_related_swapVar[v] = {
            (i, j): model.addVar(vtype=GRB.BINARY, name=f's_{oth_alt}-{(i, j)}') for i in pros for j in cons}

        E_ijVarDictPlus[v] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{oth_alt}-{(i, j)}')
                              for i in pros for j in cons}
        E_ijVarDictMoins[v] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{oth_alt}-{(i, j)}')
                               for i in pros for j in cons}

        for j in cons:
            model.addConstr(quicksum([other_alternative_related_swapVar[v][(i_, j)] for i_ in pros]) >= 1)

        for i in pros:
            model.addConstr(quicksum([other_alternative_related_swapVar[v][(i, j_)] for j_ in cons]) <= 1)

        for j in cons:
            w_j = W_dict[j]
            sig_j_plus = DeviationsSigma[j][0]
            sig_j_moins = DeviationsSigma[j][1]

            model.addConstr(quicksum([other_alternative_related_swapVar[v][(i_, j)] * W_dict[i_] +
                                      E_ijVarDictPlus[v][(i_, j)] - E_ijVarDictMoins[v][(i_, j)]
                                      for i_ in pros]) >= w_j + sig_j_plus - sig_j_moins + local_epsilon)

        # linearisation
        for i in pros:
            sig_i_plus = DeviationsSigma[i][0]
            sig_i_moins = DeviationsSigma[i][1]

            for j in cons:
                model.addConstr(
                    E_ijVarDictPlus[v][(i, j)] <= other_alternative_related_swapVar[v][(i, j)])
                model.addConstr(
                    E_ijVarDictMoins[v][(i, j)] <= other_alternative_related_swapVar[v][(i, j)])

                model.addConstr(E_ijVarDictPlus[v][(i, j)] <= sig_i_plus)
                model.addConstr(E_ijVarDictMoins[v][(i, j)] <= sig_i_moins)

                model.addConstr(
                    E_ijVarDictPlus[v][(i, j)] >= sig_i_plus - 1 + other_alternative_related_swapVar[v][
                        (i, j)])
                model.addConstr(E_ijVarDictMoins[v][(i, j)] >= sig_i_moins - 1 +
                                other_alternative_related_swapVar[v][(i, j)])

    model.addConstr(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]) == quicksum(
        [sig_pair[1] for sig_pair in DeviationsSigma.values()]))

    for k in W_dict:
        model.addConstr(DeviationsSigma[k][1] <= W_dict[k])

    model.update()
    model.setObjective(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), GRB.MINIMIZE)
    model.optimize()
    if model.status == GRB.OPTIMAL:
        return True, float(model.objVal) == 0.0

    return False, None


def recommendation_after_deformation_L3(AlternativesSubsetsList, W_dict):
    SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                           key=lambda alt: sum([W_dict[criterion] for criterion in alt]), reverse=True)

    model = Model("Deformation of DM weight -- Delta 1m-m1")
    DeviationsSigma = {k: (model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig+_{k}'),
                           model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'sig-_{k}'))
                       for k in W_dict}  # [0] = +; [1] = -

    model.setParam('OutputFlag', False)
    sum_w = 1. * sum(W_dict.values())
    W_dict = {k: vk / sum_w for k, vk in W_dict.items()}

    E_ijVarDictPlus_I_1m = dict()
    E_ijVarDictMoins_I_1m = dict()
    E_ijVarDictPlus_J_1m = dict()
    E_ijVarDictMoins_J_1m = dict()

    E_ijVarDictPlus_m1 = dict()
    E_ijVarDictMoins_m1 = dict()

    other_alternative_related_swapVar_1m = dict()
    other_alternative_related_swapVar_m1 = dict()

    for v in range(1, len(SortedAlternativesSubsetsList)):
        oth_alt = SortedAlternativesSubsetsList[v]
        pros, cons = SortedAlternativesSubsetsList[0] - oth_alt, oth_alt - SortedAlternativesSubsetsList[0]

        other_alternative_related_swapVar_1m[v] = {
            (i, j): model.addVar(vtype=GRB.BINARY, name=f's_{oth_alt}-{(i, j)}_1m') for i in pros for j in cons}
        other_alternative_related_swapVar_m1[v] = {
            (i, j): model.addVar(vtype=GRB.BINARY, name=f's_{oth_alt}-{(i, j)}_m1') for i in pros for j in cons}

        E_ijVarDictPlus_I_1m[v] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{oth_alt}-{(i, j)}_I_1m')
                                   for i in pros for j in cons}
        E_ijVarDictMoins_I_1m[v] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{oth_alt}-{(i, j)}_I_1m')
                                    for i in pros for j in cons}
        E_ijVarDictPlus_J_1m[v] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{oth_alt}-{(i, j)}_J_1m')
                                   for i in pros for j in cons}
        E_ijVarDictMoins_J_1m[v] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{oth_alt}-{(i, j)}_J_1m')
                                    for i in pros for j in cons}
        E_ijVarDictPlus_m1[v] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e+_{oth_alt}-{(i, j)}_m1') for
                                 i in pros for j in cons}
        E_ijVarDictMoins_m1[v] = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f'e-_{oth_alt}-{(i, j)}_m1') for
                                  i in pros for j in cons}

        # -- Constraints
        # - (a)ON PEUT S'EN PASSER A CAUSE DE (c) c 05/02/22
        for i in pros:
            model.addConstr(quicksum([other_alternative_related_swapVar_m1[v][(i, j_)] for j_ in cons]) <= 1)

        # - (b)
        for i in pros:
            for j in cons:
                model.addConstr(other_alternative_related_swapVar_1m[v][(i, j)] +
                                quicksum([other_alternative_related_swapVar_m1[v][(i, j_)] for j_ in cons]) <= 1)

        # - (c)
        # for j in cons:
        #     for i in pros:
        #         for i_prim in pros:
        #             model.addConstr(
        #                 other_alternative_related_swapVar_1m[v][(i, j)] + other_alternative_related_swapVar_m1[v][
        #                     (i_prim, j)] <= 1)

        # - (c) ajouté ce 16/02/22 comme maj de l'ancien (c) - le même travail a été fait dans PLNE_for_Delta1m_m1_decomposition :
                                                                # model.addConstr(Bm1[(i, j)] + quicksum([B1m[(i_, j)] for i_ in proSet]) <= 1, name="C1 ({})".format((i, j)))
        for i in pros:
            for j in cons:
                model.addConstr(other_alternative_related_swapVar_m1[v][(i, j)] + quicksum(
                    [other_alternative_related_swapVar_1m[v][(i_, j)] for i_ in pros]) <= 1)

        # - (d)
        for i in pros:
            w_i = W_dict[i]
            sig_i_plus = DeviationsSigma[i][0]
            sig_i_moins = DeviationsSigma[i][1]
            model.addConstr(w_i + sig_i_plus - sig_i_moins >= quicksum([other_alternative_related_swapVar_1m[v][
                                                                            (i, j_)] * W_dict[j_] +
                                                                        E_ijVarDictPlus_J_1m[v][(i, j_)] -
                                                                        E_ijVarDictMoins_J_1m[v][(i, j_)] for j_ in
                                                                        cons]) + local_epsilon)

        # - (e)
        for j in cons:
            w_j = W_dict[j]
            sig_j_plus = DeviationsSigma[j][0]
            sig_j_moins = DeviationsSigma[j][1]
            model.addConstr(quicksum([other_alternative_related_swapVar_1m[v][(i_, j)] * W_dict[i_] +
                                      other_alternative_related_swapVar_m1[v][(i_, j)] * W_dict[i_] +
                                      E_ijVarDictPlus_I_1m[v][(i_, j)] - E_ijVarDictMoins_I_1m[v][(i_, j)] +
                                      E_ijVarDictPlus_m1[v][(i_, j)] - E_ijVarDictMoins_m1[v][(i_, j)] for i_ in
                                      pros]) >= w_j + sig_j_plus - sig_j_moins + local_epsilon)

        # linearisation
        for i in pros:
            sig_i_plus = DeviationsSigma[i][0]
            sig_i_moins = DeviationsSigma[i][1]
            for j in cons:
                sig_j_plus = DeviationsSigma[j][0]
                sig_j_moins = DeviationsSigma[j][1]

                model.addConstr(E_ijVarDictPlus_I_1m[v][(i, j)] <= other_alternative_related_swapVar_1m[v][(i, j)])
                model.addConstr(E_ijVarDictMoins_I_1m[v][(i, j)] <= other_alternative_related_swapVar_1m[v][(i, j)])
                model.addConstr(E_ijVarDictPlus_m1[v][(i, j)] <= other_alternative_related_swapVar_m1[v][(i, j)])
                model.addConstr(E_ijVarDictMoins_m1[v][(i, j)] <= other_alternative_related_swapVar_m1[v][(i, j)])

                model.addConstr(E_ijVarDictPlus_I_1m[v][(i, j)] <= sig_i_plus)
                model.addConstr(E_ijVarDictMoins_I_1m[v][(i, j)] <= sig_i_moins)
                model.addConstr(E_ijVarDictPlus_m1[v][(i, j)] <= sig_i_plus)
                model.addConstr(E_ijVarDictMoins_m1[v][(i, j)] <= sig_i_moins)

                model.addConstr(
                    E_ijVarDictPlus_I_1m[v][(i, j)] >= sig_i_plus - 1 + other_alternative_related_swapVar_1m[v][(i, j)])
                model.addConstr(
                    E_ijVarDictMoins_I_1m[v][(i, j)] >= sig_i_moins - 1 + other_alternative_related_swapVar_1m[v][
                        (i, j)])
                model.addConstr(
                    E_ijVarDictPlus_m1[v][(i, j)] >= sig_i_plus - 1 + other_alternative_related_swapVar_m1[v][(i, j)])
                model.addConstr(
                    E_ijVarDictMoins_m1[v][(i, j)] >= sig_i_moins - 1 + other_alternative_related_swapVar_m1[v][(i, j)])

                model.addConstr(E_ijVarDictPlus_J_1m[v][(i, j)] <= other_alternative_related_swapVar_1m[v][(i, j)])
                model.addConstr(E_ijVarDictMoins_J_1m[v][(i, j)] <= other_alternative_related_swapVar_1m[v][(i, j)])
                model.addConstr(E_ijVarDictPlus_J_1m[v][(i, j)] <= sig_j_plus)
                model.addConstr(E_ijVarDictMoins_J_1m[v][(i, j)] <= sig_j_moins)
                model.addConstr(
                    E_ijVarDictPlus_J_1m[v][(i, j)] >= sig_j_plus - 1 + other_alternative_related_swapVar_1m[v][(i, j)])
                model.addConstr(
                    E_ijVarDictMoins_J_1m[v][(i, j)] >= sig_j_moins - 1 + other_alternative_related_swapVar_1m[v][
                        (i, j)])

    model.addConstr(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]) == quicksum(
        [sig_pair[1] for sig_pair in DeviationsSigma.values()]))

    for k in W_dict:
        model.addConstr(DeviationsSigma[k][1] <= W_dict[k])

    model.update()
    model.setObjective(quicksum([sig_pair[0] for sig_pair in DeviationsSigma.values()]), GRB.MINIMIZE)
    model.optimize()
    if model.status == GRB.OPTIMAL:
        return True, float(model.objVal) == 0.0

    return False, None

#
# directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/SIMULATION/KR-CBTO{m}'
#
#
# def recommendation_is_deformable_m6(AlternativesSubsetsList, W_dict, decomposition_function=None):
#     translation_result, SortedAlternativesSubsetsListTranslated = recommendation_after_deformation_L0(
#         AlternativesSubsetsList, W_dict)
#     if not translation_result:
#         return False, None
#     niveau = 0
#     for file in os.listdir(directory):
#         niveau += 1
#         if niveau % 500 == 0: print(niveau)
#         w_file = directory + '/' + file
#         W = encode_preference_model_as_dict(w_file)
#         W_SortedAlternativesSubsetsListTranslated = sorted(SortedAlternativesSubsetsListTranslated,
#                                                            key=lambda alt: sum([W[criterion] for criterion in alt]),
#                                                            reverse=True)
#         # best alternative inchangé
#         if W_SortedAlternativesSubsetsListTranslated[0] == SortedAlternativesSubsetsListTranslated[0]:
#             success_h1, S_h1 = recommendation_algorithm(SortedAlternativesSubsetsListTranslated, W,
#                                                         decomposition_function)
#             if success_h1:
#                 return True, S_h1  # ne faut il par reconsiderer la bijection ici?
#
#     return False, None


# if __name__ == "__main__":
#     # succ, R = recommendation_after_deformation([{'b', 'f', 'g'}, {'c', 'd', 'e'}, {'a', 'd'}, {'c', 'e', 'g'}],
#     #                                            {'a': 0.2462, 'b': 0.2423, 'c': 0.1480, 'd': 0.1135, 'e': 0.1,
#     #                                             'f': 0.0788,
#     #                                             'g': 0.0712})
#     # print(R)
#
#     LanguagesSelected = [decompose_under_L0]
#
#     RESULT_WITHOUT_TRANSLATION = {Language: 0 for Language in LanguagesSelected}
#     RESULT_WITH_TRANSLATION = {Language: 0 for Language in LanguagesSelected}
#     success_ratio = 0
#     nb_replications = 30
#     for repli in range(nb_replications):
#         print("Date", repli, datetime.now())
#         A = generate_n_alternatives_as_subsets(5)
#         print(A)
#         local_A_success_without = 0
#         local_A_success_with = 0
#         for file in os.listdir(directory):
#             w_file = directory + '/' + file
#             W = encode_preference_model_as_dict(w_file)
#             for language in LanguagesSelected:
#                 success_without, S_without = recommendation_algorithm(A, W, decomposition_function=language)
#                 if success_without:
#                     RESULT_WITHOUT_TRANSLATION[language] += 1
#                     RESULT_WITH_TRANSLATION[language] += 1
#                     local_A_success_without += 1
#                 else:
#                     print("defo")
#                     success_with, S_with = recommendation_is_deformable_m6(A, W, decomposition_function=language)
#                     if success_with:
#                         RESULT_WITH_TRANSLATION[language] += 1
#                         local_A_success_with += 1
#
#         print(A, "with", 100. * local_A_success_with / len(os.listdir(directory)), "%", "without",
#               100. * local_A_success_without / len(os.listdir(directory)), "%")
#
#         # - Affichage
#         for language in LanguagesSelected:
#             print("n°", repli, language, "H=1",
#                   100. * RESULT_WITHOUT_TRANSLATION[language] / (repli + 1) / len(os.listdir(directory)),
#                   "%")
#             print("n°", repli, language, "H=n",
#                   100. * RESULT_WITH_TRANSLATION[language] / (repli + 1) / len(os.listdir(directory)),
#                   "%")
