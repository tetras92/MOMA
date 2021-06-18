from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.Explanation import Explain
from CORE.SIMULATION.CBTOprocessing import correspondingSet, flat_CBTO_formated_for_OfflineSimulator, Tn_for_OfflineSimulator, Un_star_for_IJCAI, Tn_star_for_OfflineSimulator, correspondingSet
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
    n = 5

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


    dmFile = 'model421.csv'

    CorrespondingSetDict = correspondingSet(n)
    # print(CorrespondingSetDict)
    # for dmFile in os.listdir(directory):
    CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, n)
    L = [CorrespondingSetDict[elm] for elm in CBTOrder]
    # L.reverse()

    STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
            max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]

    CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn] # contigu et disjoints
    SUn_star = [(min(pair, key=lambda x: CBTOrder.index(x)),
                 max(pair, key=lambda x: CBTOrder.index(x))) for pair in Un_star]

    print(L)
    print("({}) Critical Pairs".format(len(CriticalPair)), [(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in CriticalPair])


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


    Un_star_deductible_non_critical_Set = set(SUn_star) - set(CriticalPair)
    deductible_len = len(Un_star_deductible_non_critical_Set)

    # Pairs of Un_star deductible non explainable
    cumul = 0

    not_explained_not_critical_pairs = list()
    for a, b in Un_star_deductible_non_critical_Set:
        altD = mcda_problem_description[a]
        altd = mcda_problem_description[b]

        ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
        if not ok:
            cumul += 1
            not_explained_not_critical_pairs.append((a, b))

    Un_star_critical = set(SUn_star) & set(CriticalPair)
    pi_dominance_relation_copy = PI().getRelation()["dominanceRelation"].copy()
    # print(pi_dominance_relation_copy)
    deduced_critical_pairs = list()
    not_deduced_critical_pairs = list()

    for crit in CriticalPair:
        a, b = crit
        altD = mcda_problem_description[a]
        altd = mcda_problem_description[b]
        # print((altD, altd))
        pi_dominance_relation_copy.remove((altD, altd))
        if NecessaryPreference.adjudicate(mcda_problem_description, pi_dominance_relation_copy, (altD, altd)):
            cumul += 1
            deductible_len += 1
            deduced_critical_pairs.append(crit)
            # print(dmFile)
        else:
            not_deduced_critical_pairs.append(crit)
        pi_dominance_relation_copy.append((altD, altd))


    L = [(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in not_deduced_critical_pairs]
    print("({}) Fundamental Critical Pairs".format(len(L)), L)
    L = [(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in deduced_critical_pairs]
    print("({}) Deduced Critical Pairs".format(len(L)), L)
    L = [(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in not_explained_not_critical_pairs]
    print("({}) Not explained not critical pairs".format(len(L)), L)


    large_queries = not_explained_not_critical_pairs + CriticalPair
    aprioriSelection = [True] * len(not_explained_not_critical_pairs) + [False] * len(CriticalPair)

    # ('13', '5') : (5, 16)
    # ('5', '4') : (16, 8)
    # ('4', '3') : (8, 4)
    # ('3', '12') : (4, 3)
    # ('2', '1') : (2, 1)
    # '23' : 6
    # '13' : 5

    # print("My Large queries", [(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in large_queries])
    large_queries_alt = [(mcda_problem_description[a], mcda_problem_description[b]) for a, b in large_queries]

    # for crit in CriticalPair:
    #     if crit not in large_queries:
    #         a, b = crit
    #         altD = mcda_problem_description[a]
    #         altd = mcda_problem_description[b]
    #
    #         if NecessaryPreference.adjudicate(mcda_problem_description, queries_alt, (altD, altd)):
    #             print('(\'{}\', \'{}\')'.format(CorrespondingSetDict[a], CorrespondingSetDict[b]))

    Relation = [(mcda_problem_description[a], mcda_problem_description[b]) for a, b in CriticalPair]
    answer1, smallestsize1, selectedList1 = SmallestSetOfPairs.compute(mcda_problem_description, Relation)
    print("Smallest size ({}) of Critical Pairs".format(int(smallestsize1)), [(CorrespondingSetDict[CriticalPair[v][0]], CorrespondingSetDict[CriticalPair[v][1]]) for v in selectedList1])

    # answer, smallestsize, selectedList = SmallestSetOfPairs.compute(mcda_problem_description, large_queries_alt, aprioriSelection)
    # print("My ({}) restricted queries".format(int(smallestsize)), [(CorrespondingSetDict[large_queries[v][0]], CorrespondingSetDict[large_queries[v][1]]) for v in selectedList])

    # print("Smallest Set of queries of size {}".format(int(smallestsize)))
    # if answer:
    #     print("My ({}) restricted queries".format(int(smallestsize)), [(CorrespondingSetDict[large_queries[v][0]], CorrespondingSetDict[large_queries[v][1]]) for v in selectedList])
    #     if len(large_queries) > smallestsize:
    #         print("With restriction")
    #
    # print(smallestsize1, "/", smallestsize)
