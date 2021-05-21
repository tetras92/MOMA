from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.Explanation import Explain
from CORE.SIMULATION.CBTOprocessing import nCoveringPairs, flat_CBTO_formated_for_OfflineSimulator, Tn_for_OfflineSimulator, Un_star_for_IJCAI, Tn_star_for_OfflineSimulator, correspondingSet
import os
from CORE.Dialog import Dialog
import random
from CORE.DM import WS_DM
from datetime import datetime
from CORE.NecessaryPreference import NecessaryPreference
from CORE.SmallestSetOfPairs import SmallestSetOfPairs

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


    RESULT2 = dict()
    RESULT = dict()
    CorrespondingSetDict = correspondingSet(n)
    for dmFile in os.listdir(directory):
        niveau += 1
        if niveau % 500 == 0: print(niveau, datetime.now())
        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, n)
        STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]

        CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn] # contigu et disjoints
        SUn_star = [(min(pair, key=lambda x: CBTOrder.index(x)),
                     max(pair, key=lambda x: CBTOrder.index(x))) for pair in Un_star]


        dm = WS_DM(directory+'/'+dmFile)

        # assert(len(STn) == cardSTn[n])

        PI().clear()
        N().clear()

        Dict_Non_PI = dict()
        for info in [non_pi_elem for non_pi_elem in NonPI()]:
            Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
            Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info


        for a, b in CriticalPair:
            Dialog(Dict_Non_PI[(a, b)]).madeWith(dm)        # chargement du modèle

        # Minimal Number of queries
        Relation = [(mcda_problem_description[a], mcda_problem_description[b]) for a, b in CriticalPair]
        answer1, smallestsize1, selectedList1 = SmallestSetOfPairs.compute(mcda_problem_description, Relation)
        smallestSetOfQueries = [CriticalPair[v] for v in selectedList1]


        Un_star_deductible_non_critical_Set = set(SUn_star) - set(smallestSetOfQueries)
        deductible_but_non_explainable_Un_Star = list()
        # Pairs of Un_star deductible non explainable
        cumul = 0

        for a, b in Un_star_deductible_non_critical_Set:
            altD = mcda_problem_description[a]
            altd = mcda_problem_description[b]

            ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
            if not ok:
                cumul += 1
                deductible_but_non_explainable_Un_Star.append((a, b))

        large_queries = deductible_but_non_explainable_Un_Star + CriticalPair
        aprioriSelection = [True] * len(deductible_but_non_explainable_Un_Star) + [False] * len(CriticalPair)

        large_queries_alt = [(mcda_problem_description[a], mcda_problem_description[b]) for a, b in large_queries]
        answer2, smallestsize2, selectedList2 = SmallestSetOfPairs.compute(mcda_problem_description, large_queries_alt, aprioriSelection)


        RESULT2[dmFile] = smallestsize1, smallestsize2
        RESULT[dmFile] = {'model': dmFile, 'all_explainable_minimal_number_of_queries': int(smallestsize2), 'minimal_number_of_queries': int(smallestsize1), "critical_length": len(CriticalPair),
                          "number_of_non_explainable": len(deductible_but_non_explainable_Un_Star)}


    with open(f'QuestionSimulation{n}.csv', 'w', newline='') as csvfile:
            fieldnames = ['model', "critical_length", 'minimal_number_of_queries', "number_of_non_explainable", 'all_explainable_minimal_number_of_queries']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in RESULT.values():
                writer.writerow(row)
    # print(RESULT2)
    # print(sorted(RESULT2.keys(), key=lambda file : RESULT2[file][0]))
    SERIES = sorted([round(100*(s2 - s1)/s1, 2) for s1, s2 in RESULT2.values()])
    # print(SERIES)
    # print(breakpoint(SERIES))
    print("Minimum", min(SERIES), "Median", SERIES[len(SERIES)//2], "Maximum", max(SERIES))
    Histogram = dict()
    for val in SERIES:
        if int(val) not in Histogram:
            Histogram[int(val)] = 0
        Histogram[int(val)] += 1

    print(Histogram)


# n = 4
# Minimum 0.0 Median 0.0 Maximum 0.0
# {0: 14}

# n = 5
# Minimum 0.0 Median 40.0 Maximum 125.0
# {0: 86, 12: 4, 14: 17, 16: 21, 20: 26, 25: 3, 28: 29, 33: 70, 40: 60, 42: 3, 50: 39, 60: 98, 66: 12, 75: 5, 80: 34, 100: 7, 125: 2}

# n = 6
# Minimum 0.0 Median 200.0 Maximum 500.0
# {0: 454, 7: 1, 9: 19, 10: 70, 11: 109, 12: 175, 14: 204, 15: 2, 16: 100, 18: 20, 20: 99, 22: 306, 23: 1, 25: 561, 27: 25, 28: 641, 30: 55, 33: 431, 36: 47, 37: 513, 40: 152, 41: 4, 42: 952, 44: 247, 45: 22, 50: 988, 53: 1, 54: 11, 55: 274, 57: 805, 58: 1, 60: 82, 61: 4, 62: 539, 63: 22, 66: 692, 69: 2, 70: 80, 71: 686, 72: 39, 75: 700, 76: 1, 77: 239, 80: 97, 81: 35, 83: 501, 84: 4, 85: 975, 87: 550, 88: 301, 90: 245, 91: 20, 92: 1, 100: 3367, 108: 15, 109: 93, 110: 355, 111: 641, 112: 904, 114: 1007, 115: 1, 116: 1066, 118: 63, 120: 340, 122: 758, 125: 1333, 127: 55, 128: 1235, 130: 290, 133: 1998, 136: 52, 137: 1659, 140: 241, 142: 1713, 144: 850, 145: 68, 150: 3022, 154: 42, 155: 782, 157: 2289, 160: 281, 162: 2305, 163: 20, 166: 1693, 170: 312, 171: 2918, 172: 5, 175: 2132, 177: 654, 180: 144, 183: 1231, 185: 3666, 187: 2077, 188: 920, 190: 58, 200: 8691, 210: 1, 211: 412, 212: 1807, 214: 3750, 216: 2596, 220: 10, 222: 178, 225: 2441, 228: 3644, 233: 3350, 237: 1919, 240: 14, 242: 3296, 244: 1, 250: 4423, 257: 3216, 260: 9, 262: 377, 266: 3466, 271: 4112, 275: 58, 280: 17, 283: 3272, 285: 2996, 287: 2, 300: 4046, 314: 523, 316: 2798, 320: 10, 328: 78, 333: 3364, 340: 19, 342: 1, 350: 2226, 360: 11, 366: 891, 380: 8, 383: 257, 400: 60, 416: 1, 420: 17, 440: 23, 460: 25, 480: 7, 500: 4}

