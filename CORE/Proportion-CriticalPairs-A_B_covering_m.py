from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.SIMULATION.CBTOprocessing import nCoveringPairs, flat_CBTO_formated_for_OfflineSimulator, Tn_for_OfflineSimulator, Tn_star_for_OfflineSimulator, correspondingSet
import os
from CORE.Dialog import Dialog
from CORE.DM import WS_DM
from datetime import datetime


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
    # print("to examine", len(Dn_star) + len(Un_star))
    niveau = -1

    A_B_ordering_dict = dict()
    A_B_is_critical_dict = dict()


    for dmFile in os.listdir(directory):
        niveau += 1
        if niveau % 500 == 0: print(niveau, datetime.now())
        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, n)
        STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]

        CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn]  # contigu et disjoints

        CPn, CPnDict = nCoveringPairs(directory + '/' + dmFile, n)


        for pair in CPn:
            if pair not in A_B_ordering_dict:
                A_B_ordering_dict[pair] = 0
            if (pair[1], pair[0]) not in A_B_ordering_dict:
                A_B_ordering_dict[(pair[1], pair[0])] = 0
            A_B_ordering_dict[pair] += 1

        for pair in set(CPn) & set(CriticalPair):
            if pair not in A_B_is_critical_dict:
                A_B_is_critical_dict[pair] = 0
            if (pair[1], pair[0]) not in A_B_is_critical_dict:
                A_B_is_critical_dict[(pair[1], pair[0])] = 0

            A_B_is_critical_dict[pair] += 1





    for pair in A_B_ordering_dict.keys() - A_B_is_critical_dict.keys():
        A_B_is_critical_dict[pair] = 0
    # print("ordering", A_B_ordering_dict)

    A_B_ordering_dict_Factorized = {(min(pair), max(pair)): dict() for pair in A_B_ordering_dict}
    for pair, val in A_B_ordering_dict.items():
        if pair in A_B_ordering_dict_Factorized:
            A_B_ordering_dict_Factorized[pair][True] = val
        elif (pair[1], pair[0]) in A_B_ordering_dict_Factorized:
            A_B_ordering_dict_Factorized[(pair[1], pair[0])][False] = val
    print(A_B_ordering_dict_Factorized)

    A_B_is_critical_dict_Factorized = {(min(pair), max(pair)): {True : 0, False : 0} for pair in A_B_ordering_dict}
    for pair, val in A_B_is_critical_dict.items():
        if pair in A_B_is_critical_dict_Factorized:
            A_B_is_critical_dict_Factorized[pair][True] = val
        elif (pair[1], pair[0]) in A_B_is_critical_dict_Factorized:
            A_B_is_critical_dict_Factorized[(pair[1], pair[0])][False] = val
    print(A_B_is_critical_dict_Factorized, "\n")

    Corresp_Set = correspondingSet(n)
    nb_files = len(os.listdir(directory))
    for pair, ordering_dict in A_B_ordering_dict_Factorized.items():
        # print(pair)
        a, b = pair
        obj = (Corresp_Set[a], Corresp_Set[b])
        p_a_b = ordering_dict[True] / nb_files
        p_b_a = ordering_dict[False] / nb_files

        p_is_critical_a_b = 0
        aff_p_is_critical_a_b = None
        if ordering_dict[True] != 0:
            p_is_critical_a_b = round(A_B_is_critical_dict_Factorized[pair][True] / ordering_dict[True], 2)
            aff_p_is_critical_a_b = round(100 * p_is_critical_a_b, 2)


        p_is_critical_b_a = 0
        aff_p_is_critical_b_a = None
        if ordering_dict[False] != 0:
            p_is_critical_b_a = round(A_B_is_critical_dict_Factorized[pair][False] / ordering_dict[False], 2)
            aff_p_is_critical_b_a = round(100 * p_is_critical_b_a, 2)
        p_is_critical = p_is_critical_a_b * p_a_b + p_b_a * p_is_critical_b_a


        print(obj, round(100*p_a_b, 2), aff_p_is_critical_a_b, round(100 * p_b_a, 2), aff_p_is_critical_b_a, round(100 * p_is_critical, 2))

# n = 4
# {(3, 12): {False: 14, True: 0}, (5, 10): {False: 14, True: 0}, (6, 9): {False: 9, True: 5}}
# {(3, 12): {True: 0, False: 0}, (5, 10): {True: 0, False: 0}, (6, 9): {True: 5, False: 5}}
#
# ({1, 2}, {3, 4}) 0.0 None 100.0 0.0 0.0
# ({1, 3}, {2, 4}) 0.0 None 100.0 0.0 0.0
# ({2, 3}, {1, 4}) 35.71 100.0 64.29 56.0 71.71

# n = 5
# {(3, 28): {False: 516, True: 0}, (5, 26): {False: 516, True: 0}, (9, 22): {False: 516, True: 0}, (14, 17): {True: 454, False: 62}, (6, 25): {False: 516, True: 0}, (10, 21): {False: 516, True: 0}, (13, 18): {False: 178, True: 338}, (12, 19): {False: 461, True: 55}, (11, 20): {False: 431, True: 85}, (7, 24): {False: 504, True: 12}}
# {(3, 28): {True: 0, False: 0}, (5, 26): {True: 0, False: 0}, (9, 22): {True: 0, False: 0}, (14, 17): {True: 34, False: 34}, (6, 25): {True: 0, False: 0}, (10, 21): {True: 0, False: 0}, (13, 18): {True: 82, False: 82}, (12, 19): {True: 55, False: 55}, (11, 20): {True: 61, False: 61}, (7, 24): {True: 12, False: 12}}
#
# ({1, 2}, {3, 4, 5}) 0.0 None 100.0 0.0 0.0
# ({1, 3}, {2, 4, 5}) 0.0 None 100.0 0.0 0.0
# ({1, 4}, {2, 3, 5}) 0.0 None 100.0 0.0 0.0
# ({2, 3, 4}, {1, 5}) 87.98 7.0 12.02 55.0 12.77
# ({2, 3}, {1, 4, 5}) 0.0 None 100.0 0.0 0.0
# ({2, 4}, {1, 3, 5}) 0.0 None 100.0 0.0 0.0
# ({1, 3, 4}, {2, 5}) 65.5 24.0 34.5 46.0 31.59
# ({3, 4}, {1, 2, 5}) 10.66 100.0 89.34 12.0 21.38
# ({1, 2, 4}, {3, 5}) 16.47 72.0 83.53 14.0 23.55
# ({1, 2, 3}, {4, 5}) 2.33 100.0 97.67 2.0 4.28

# n = 6
# {(3, 60): {False: 124187, True: 0}, (5, 58): {False: 124187, True: 0}, (9, 54): {False: 124187, True: 0}, (17, 46): {False: 124187, True: 0}, (30, 33): {True: 122018, False: 2169}, (6, 57): {False: 124187, True: 0}, (10, 53): {False: 124187, True: 0}, (18, 45): {False: 124187, True: 0}, (29, 34): {True: 118409, False: 5778}, (12, 51): {False: 124187, True: 0}, (20, 43): {False: 124187, True: 0}, (27, 36): {True: 106996, False: 17191}, (24, 39): {False: 121625, True: 2562}, (23, 40): {False: 60051, True: 64136}, (15, 48): {False: 101144, True: 23043}, (7, 56): {False: 124187, True: 0}, (11, 52): {False: 124187, True: 0}, (19, 44): {False: 124187, True: 0}, (28, 35): {True: 104074, False: 20113}, (13, 50): {False: 124187, True: 0}, (21, 42): {False: 124187, True: 0}, (26, 37): {True: 71973, False: 52214}, (25, 38): {False: 104790, True: 19397}, (22, 41): {False: 111509, True: 12678}, (14, 49): {False: 122823, True: 1364}}
# {(3, 60): {True: 0, False: 0}, (5, 58): {True: 0, False: 0}, (9, 54): {True: 0, False: 0}, (17, 46): {True: 0, False: 0}, (30, 33): {True: 1125, False: 1137}, (6, 57): {True: 0, False: 0}, (10, 53): {True: 0, False: 0}, (18, 45): {True: 0, False: 0}, (29, 34): {True: 2335, False: 2484}, (12, 51): {True: 0, False: 0}, (20, 43): {True: 0, False: 0}, (27, 36): {True: 5580, False: 5839}, (24, 39): {True: 2562, False: 2562}, (23, 40): {True: 9278, False: 9393}, (15, 48): {True: 4728, False: 4701}, (7, 56): {True: 0, False: 0}, (11, 52): {True: 0, False: 0}, (19, 44): {True: 0, False: 0}, (28, 35): {True: 5412, False: 5320}, (13, 50): {True: 0, False: 0}, (21, 42): {True: 0, False: 0}, (26, 37): {True: 12390, False: 12170}, (25, 38): {True: 9084, False: 8955}, (22, 41): {True: 7825, False: 7547}, (14, 49): {True: 1364, False: 1364}}
#
# ({1, 2}, {3, 4, 5, 6}) 0.0 None 100.0 0.0 0.0
# ({1, 3}, {2, 4, 5, 6}) 0.0 None 100.0 0.0 0.0
# ({1, 4}, {2, 3, 5, 6}) 0.0 None 100.0 0.0 0.0
# ({1, 5}, {2, 3, 4, 6}) 0.0 None 100.0 0.0 0.0
# ({2, 3, 4, 5}, {1, 6}) 98.25 1.0 1.75 52.0 1.89
# ({2, 3}, {1, 4, 5, 6}) 0.0 None 100.0 0.0 0.0
# ({2, 4}, {1, 3, 5, 6}) 0.0 None 100.0 0.0 0.0
# ({2, 5}, {1, 3, 4, 6}) 0.0 None 100.0 0.0 0.0
# ({1, 3, 4, 5}, {2, 6}) 95.35 2.0 4.65 43.0 3.91
# ({3, 4}, {1, 2, 5, 6}) 0.0 None 100.0 0.0 0.0
# ({3, 5}, {1, 2, 4, 6}) 0.0 None 100.0 0.0 0.0
# ({1, 2, 4, 5}, {3, 6}) 86.16 5.0 13.84 34.0 9.01
# ({4, 5}, {1, 2, 3, 6}) 2.06 100.0 97.94 2.0 4.02
# ({1, 2, 3, 5}, {4, 6}) 51.64 14.0 48.36 16.0 14.97
# ({1, 2, 3, 4}, {5, 6}) 18.56 21.0 81.44 5.0 7.97
# ({1, 2, 3}, {4, 5, 6}) 0.0 None 100.0 0.0 0.0
# ({1, 2, 4}, {3, 5, 6}) 0.0 None 100.0 0.0 0.0
# ({1, 2, 5}, {3, 4, 6}) 0.0 None 100.0 0.0 0.0
# ({3, 4, 5}, {1, 2, 6}) 83.8 5.0 16.2 26.0 8.4
# ({1, 3, 4}, {2, 5, 6}) 0.0 None 100.0 0.0 0.0
# ({1, 3, 5}, {2, 4, 6}) 0.0 None 100.0 0.0 0.0
# ({2, 4, 5}, {1, 3, 6}) 57.96 17.0 42.04 23.0 19.52
# ({1, 4, 5}, {2, 3, 6}) 15.62 47.0 84.38 9.0 14.94
# ({2, 3, 5}, {1, 4, 6}) 10.21 62.0 89.79 7.0 12.61
# ({2, 3, 4}, {1, 5, 6}) 1.1 100.0 98.9 1.0 2.09
#
# Process finished with exit code 0
#
# GeneralINEXP = [71.71, 12.77, 44.69, 37.46, 23.55, 4.28, 15.91, 11.86, 17.55, 8.53, 4.86, 1.89, 21.24, 44.74, 38, 34.8, 13.96]
# GeneralCRITI = [71.71, 12.77, 31.59, 21.38, 23.55, 4.28, 9.01, 4.02, 14.97, 7.97, 3.91, 1.89, 8.4, 19.52, 14.94, 12.61, 2.09]
