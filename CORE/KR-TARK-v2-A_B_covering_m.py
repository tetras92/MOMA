from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.Explanation import Explain
from CORE.SIMULATION.CBTOprocessing import nCoveringPairs, flat_CBTO_formated_for_OfflineSimulator, Tn_for_OfflineSimulator, Un_star_for_IJCAI, Tn_star_for_OfflineSimulator, correspondingSet
import os
from CORE.Dialog import Dialog
import random
from CORE.DM import WS_DM
from datetime import datetime


def breakpoint(series):
    V = list()
    for i in range(1, len(series)):
        if series[i] != series[i-1]:
            V.append((series[i-1], i+1))
    return V


if __name__ == "__main__":
    n = 6

    cardSDn = {4: 19,
               5: 64,
               6: 203,
               7: 622,
               8: 1867}

    cardSUn = {4: 6,
               5: 26,
               6: 98,
               7: 344,
               8: 1158}

    cardSTn = {4: 25,
               5: 90,
               6: 301,
               7: 966,
               8: 3025}

    # Engine1 = Explain.general_MixedExplanation
    Engine = Explain.brut_force_general_1_vs_k_and_k_vs_1_MixedExplanation
    TotalRequirementsChecked = 0


    criteriaFile = f'/home/manuel239/PycharmProjects/MOMA/CORE/CSVFILES/ijcai_criteria{n}.csv'
    perfFile = f'/home/manuel239/PycharmProjects/MOMA/CORE/CSVFILES/ijcai_fullPerfTable{n}.csv'
    mcda_problem_description = ProblemDescription(criteriaFileName=criteriaFile,
                                                  performanceTableFileName=perfFile)

    directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/SIMULATION/CBTO{n}'


    Tn = Tn_for_OfflineSimulator(n)
    Tn_star = Tn_star_for_OfflineSimulator(n)

    dmTemoin = WS_DM(directory+'/model1.csv')
    Dn = list()
    N().update(mcda_problem_description, **PI().getRelation()) # But : éliminer la dominance
    N().drop()
    NonPI().filter()
    assert len(NonPI()) == len(Tn)

    CPnTemoin, CPnDictTemoin = nCoveringPairs(directory + '/model1.csv', n)
    DictCumulDif1 = {dif : 0 for dif in CPnDictTemoin}
    DictCumulDif2 = {dif : 0 for dif in CPnDictTemoin}
    DictTotalDif = {dif : len(SetAss) for dif, SetAss in CPnDictTemoin.items()}


    Dict_Non_PI = dict()
    for info in [non_pi_elem for non_pi_elem in NonPI()]:
        Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
        Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info

    # Singletons Hypothesis
    for i in range(n - 1):
        altId_inf = 2 ** i
        altId_sup = 2 ** (i+1)
        Dn.append((altId_inf, altId_sup))
        Dialog(Dict_Non_PI[(altId_inf, altId_sup)]).madeWith(dmTemoin)
    # print("============= ", PI().getRelation()["dominanceRelation"])

    N().update(mcda_problem_description, **PI().getRelation())
    for pair in Tn:
        for infoN in N():
            if infoN.alternative1.id in pair and infoN.alternative2.id in pair:
                Dn.append(pair)
    Un = list(set(Tn) - set(Dn))

    assert(len(Dn) == cardSDn[n])
    assert(len(Tn) == cardSTn[n])
    assert(len(Un) == cardSUn[n])

    N().clear()
    PI().clear()

    Dn_star = set(Dn) & set(Tn_star)
    Un_star = set(Un) & set(Tn_star)
    print("to examine", len(Dn_star) + len(Un_star))
    niveau = -1

    A_B_ordering_dict = dict()
    A_B_xplained_dict = dict()

    RESULT = dict()
    denominateur = None
    for dmFile in os.listdir(directory):
        niveau += 1
        if niveau % 500 == 0: print(niveau, datetime.now())
        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, n)
        STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]

        CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn]  # contigu et disjoints
        STn_star = [(min(pair, key=lambda x: CBTOrder.index(x)),
                    max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn_star]

        SDn_star = [(min(pair, key=lambda x: CBTOrder.index(x)),
                    max(pair, key=lambda x: CBTOrder.index(x))) for pair in Dn_star]


        CPn, CPnDict = nCoveringPairs(directory + '/' + dmFile, n)
        denominateur = len(CPn)

        # for pair in CPn:
        #     if pair not in A_B_ordering_dict:
        #         A_B_ordering_dict[pair] = 0
        #     if (pair[1], pair[0]) not in A_B_ordering_dict:
        #         A_B_ordering_dict[(pair[1], pair[0])] = 0
        #     A_B_ordering_dict[pair] += 1
        #
        # for pair in set(CPn) & set(SDn_star):
        #     if pair not in A_B_xplained_dict:
        #         A_B_xplained_dict[pair] = 0
        #     if (pair[1], pair[0]) not in A_B_xplained_dict:
        #         A_B_xplained_dict[(pair[1], pair[0])] = 0
        #     A_B_xplained_dict[pair] += 1


        dm = WS_DM(directory+'/'+dmFile)

        assert(len(STn) == cardSTn[n])

        PI().clear()
        N().clear()

        Dict_Non_PI = dict()
        for info in [non_pi_elem for non_pi_elem in NonPI()]:
            Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
            Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info


        for a, b in CriticalPair:
            Dialog(Dict_Non_PI[(a, b)]).madeWith(dm)        # chargement du modèle


        cumul = len(set(CPn) & set(SDn_star))

        for a, b in (set(CPn) - set(SDn_star)):
            altD = mcda_problem_description[a]
            altd = mcda_problem_description[b]

            ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
            if ok:
                cumul += 1
                # if (a, b) not in A_B_xplained_dict:
                #     A_B_xplained_dict[(a, b)] = 0
                # A_B_xplained_dict[(a, b)] += 1
        RESULT[dmFile] = cumul



    # print(sorted(RESULT.keys(), key=lambda file : RESULT[file]))
    SERIES = sorted([round(100*val/denominateur,2) for val in RESULT.values()])
    print(SERIES)
    print(breakpoint(SERIES))
    print("Minimum", min(SERIES), "Median", SERIES[len(SERIES)//2], "Maximum", max(SERIES))
    # for pair in A_B_ordering_dict.keys() - A_B_xplained_dict.keys():
    #     A_B_xplained_dict[pair] = 0
    # # print("ordering", A_B_ordering_dict)
    # # print("xplained", A_B_xplained_dict)
    #
    # A_B_ordering_dict_Factorized = {(min(pair), max(pair)): dict() for pair in A_B_ordering_dict}
    # for pair, val in A_B_ordering_dict.items():
    #     if pair in A_B_ordering_dict_Factorized:
    #         A_B_ordering_dict_Factorized[pair][True] = val
    #     elif (pair[1], pair[0]) in A_B_ordering_dict_Factorized:
    #         A_B_ordering_dict_Factorized[(pair[1], pair[0])][False] = val
    # print(A_B_ordering_dict_Factorized)
    #
    # A_B_xplained_dict_Factorized = {(min(pair), max(pair)): {True : 0, False : 0} for pair in A_B_ordering_dict}
    # for pair, val in A_B_xplained_dict.items():
    #     if pair in A_B_xplained_dict_Factorized:
    #         A_B_xplained_dict_Factorized[pair][True] = val
    #     elif (pair[1], pair[0]) in A_B_xplained_dict_Factorized:
    #         A_B_xplained_dict_Factorized[(pair[1], pair[0])][False] = val
    # print(A_B_xplained_dict_Factorized,"\n")
    #
    # Corresp_Set = correspondingSet(n)
    # for pair, ordering_dict in A_B_ordering_dict_Factorized.items():
    #     # print(pair)
    #     a, b = pair
    #     obj = (Corresp_Set[a], Corresp_Set[b])
    #     nb_files = sum(ordering_dict.values())
    #     p_a_b = ordering_dict[True] / nb_files
    #     p_b_a = ordering_dict[False] / nb_files
    #
    #     p_xplain_a_b = 0
    #     aff_p_xplain_a_b = None
    #     if ordering_dict[True] != 0:
    #         p_xplain_a_b = round(A_B_xplained_dict_Factorized[pair][True] / ordering_dict[True], 2)
    #         aff_p_xplain_a_b = round(100 * p_xplain_a_b,2)
    #
    #
    #     p_xplain_b_a = 0
    #     aff_p_xplain_b_a = None
    #     if ordering_dict[False] != 0:
    #         p_xplain_b_a = round(A_B_xplained_dict_Factorized[pair][False] / ordering_dict[False], 2)
    #         aff_p_xplain_b_a = round(100*p_xplain_b_a,2)
    #     p_xplain = p_xplain_a_b * p_a_b + p_b_a * p_xplain_b_a
    #
    #
    #     print(obj, round(100*p_a_b, 2), aff_p_xplain_a_b,  round(100*p_b_a, 2), aff_p_xplain_b_a, round(100*p_xplain, 2))

# n = 4
# Minimum 66.67 Median 66.67 Maximum 100.0
# {(3, 12): {False: 14, True: 0}, (5, 10): {False: 14, True: 0}, (6, 9): {False: 9, True: 5}}
# {(3, 12): {True: 0, False: 14}, (5, 10): {True: 0, False: 14}, (6, 9): {True: 0, False: 4}}
# ({1, 2}, {3, 4}) 0.0 None 100.0 100.0 100.0
# ({1, 3}, {2, 4}) 0.0 None 100.0 100.0 100.0
# ({2, 3}, {1, 4}) 35.71 0.0 64.29 44.0 28.29

# n=5
# Minimum 80.0 Median 90.0 Maximum 100.0
# {(3, 28): {False: 516, True: 0}, (5, 26): {False: 516, True: 0}, (9, 22): {False: 516, True: 0}, (14, 17): {True: 454, False: 62}, (6, 25): {False: 516, True: 0}, (10, 21): {False: 516, True: 0}, (13, 18): {False: 178, True: 338}, (12, 19): {False: 461, True: 55}, (11, 20): {False: 431, True: 85}, (7, 24): {False: 504, True: 12}}
# {(3, 28): {True: 0, False: 516}, (5, 26): {True: 0, False: 516}, (9, 22): {True: 0, False: 516}, (14, 17): {True: 420, False: 28}, (6, 25): {True: 0, False: 516}, (10, 21): {True: 0, False: 516}, (13, 18): {True: 190, False: 96}, (12, 19): {True: 0, False: 321}, (11, 20): {True: 24, False: 370}, (7, 24): {True: 0, False: 492}}
# ({1, 2}, {3, 4, 5}) 0.0 None 100.0 100.0 100.0
# ({1, 3}, {2, 4, 5}) 0.0 None 100.0 100.0 100.0
# ({1, 4}, {2, 3, 5}) 0.0 None 100.0 100.0 100.0
# ({2, 3, 4}, {1, 5}) 87.98 93.0 12.02 45.0 87.23
# ({2, 3}, {1, 4, 5}) 0.0 None 100.0 100.0 100.0
# ({2, 4}, {1, 3, 5}) 0.0 None 100.0 100.0 100.0
# ({1, 3, 4}, {2, 5}) 65.5 56.0 34.5 54.0 55.31
# ({3, 4}, {1, 2, 5}) 10.66 0.0 89.34 70.0 62.54
# ({1, 2, 4}, {3, 5}) 16.47 28.0 83.53 86.0 76.45
# ({1, 2, 3}, {4, 5}) 2.33 0.0 97.67 98.0 95.72

# n = 6
# Minimum 80.0 Median 92.0 Maximum 100.0
# {(3, 60): {False: 124187, True: 0}, (5, 58): {False: 124187, True: 0}, (9, 54): {False: 124187, True: 0}, (17, 46): {False: 124187, True: 0}, (30, 33): {True: 122018, False: 2169}, (6, 57): {False: 124187, True: 0}, (10, 53): {False: 124187, True: 0}, (18, 45): {False: 124187, True: 0}, (29, 34): {True: 118409, False: 5778}, (12, 51): {False: 124187, True: 0}, (20, 43): {False: 124187, True: 0}, (27, 36): {True: 106996, False: 17191}, (24, 39): {False: 121625, True: 2562}, (23, 40): {False: 60051, True: 64136}, (15, 48): {False: 101144, True: 23043}, (7, 56): {False: 124187, True: 0}, (11, 52): {False: 124187, True: 0}, (19, 44): {False: 124187, True: 0}, (28, 35): {True: 104074, False: 20113}, (13, 50): {False: 124187, True: 0}, (21, 42): {False: 124187, True: 0}, (26, 37): {True: 71973, False: 52214}, (25, 38): {False: 104790, True: 19397}, (22, 41): {False: 111509, True: 12678}, (14, 49): {False: 122823, True: 1364}}
# {(3, 60): {True: 0, False: 124187}, (5, 58): {True: 0, False: 124187}, (9, 54): {True: 0, False: 124187}, (17, 46): {True: 0, False: 124187}, (30, 33): {True: 120893, False: 1032}, (6, 57): {True: 0, False: 124187}, (10, 53): {True: 0, False: 124187}, (18, 45): {True: 0, False: 124187}, (29, 34): {True: 114290, False: 3294}, (12, 51): {True: 0, False: 124187}, (20, 43): {True: 0, False: 124187}, (27, 36): {True: 93157, False: 11352}, (24, 39): {True: 0, False: 108919}, (23, 40): {True: 52069, False: 50658}, (15, 48): {True: 17551, False: 96443}, (7, 56): {True: 0, False: 124187}, (11, 52): {True: 0, False: 124187}, (19, 44): {True: 0, False: 124187}, (28, 35): {True: 84839, False: 12441}, (13, 50): {True: 0, False: 124187}, (21, 42): {True: 0, False: 124187}, (26, 37): {True: 38560, False: 29904}, (25, 38): {True: 6707, False: 70649}, (22, 41): {True: 2889, False: 78311}, (14, 49): {True: 0, False: 106961}}
#
# A- ({1, 2}, {3, 4, 5, 6}) 0.0 None 100.0 100.0 100.0
# B- ({1, 3}, {2, 4, 5, 6}) 0.0 None 100.0 100.0 100.0
# C- ({1, 4}, {2, 3, 5, 6}) 0.0 None 100.0 100.0 100.0
# D- ({1, 5}, {2, 3, 4, 6}) 0.0 None 100.0 100.0 100.0
# E- ({2, 3}, {1, 4, 5, 6}) 0.0 None 100.0 100.0 100.0
# F- ({2, 4}, {1, 3, 5, 6}) 0.0 None 100.0 100.0 100.0
# G- ({2, 5}, {1, 3, 4, 6}) 0.0 None 100.0 100.0 100.0
# H- ({3, 4}, {1, 2, 5, 6}) 0.0 None 100.0 100.0 100.0
# I- ({3, 5}, {1, 2, 4, 6}) 0.0 None 100.0 100.0 100.0
# J- ({1, 2, 3}, {4, 5, 6}) 0.0 None 100.0 100.0 100.0
# K- ({1, 2, 4}, {3, 5, 6}) 0.0 None 100.0 100.0 100.0
# L- ({1, 2, 5}, {3, 4, 6}) 0.0 None 100.0 100.0 100.0

# ({1, 3, 4}, {2, 5, 6}) 0.0 None 100.0 100.0 100.0
# ({1, 3, 5}, {2, 4, 6}) 0.0 None 100.0 100.0 100.0

# ({1, 2, 4, 5}, {3, 6}) 86.16 87.0 13.84 66.0 84.09
# ({4, 5}, {1, 2, 3, 6}) 2.06 0.0 97.94 90.0 88.14

# ({1, 2, 3, 5}, {4, 6}) 51.64 81.0 48.36 84.0 82.45
# ({1, 2, 3, 4}, {5, 6}) 18.56 76.0 81.44 95.0 91.47

# ({1, 3, 4, 5}, {2, 6}) 95.35 97.0 4.65 57.0 95.14
# ({2, 3, 4, 5}, {1, 6}) 98.25 99.0 1.75 48.0 98.11

# ({3, 4, 5}, {1, 2, 6}) 83.8 82.0 16.2 62.0 78.76
# ({2, 4, 5}, {1, 3, 6}) 57.96 54.0 42.04 57.0 55.26

# ({1, 4, 5}, {2, 3, 6}) 15.62 35.0 84.38 67.0 62.0
# ({2, 3, 5}, {1, 4, 6}) 10.21 23.0 89.79 70.0 65.2
# ({2, 3, 4}, {1, 5, 6}) 1.1 0.0 98.9 87.0 86.04

# n = 6 FONCTION DE REPARTITION
# [(80.0, 4722), (84.0, 21652), (88.0, 38301), (92.0, 77312), (96.0, 123156)]
# Minimum 80.0 Median 92.0 Maximum 100.0
