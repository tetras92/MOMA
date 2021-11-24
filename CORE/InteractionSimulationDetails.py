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
    # Engine = Explain.general_1_vs_k_MixedExplanation
    # Engine = Explain.general_k_vs_1_MixedExplanation
    # Engine = Explain.Order2SwapExplanation


    criteriaFile = f'/home/manuel239/PycharmProjects/MOMA/CORE/CSVFILES/ijcai_criteria{n}.csv'
    perfFile = f'/home/manuel239/PycharmProjects/MOMA/CORE/CSVFILES/ijcai_fullPerfTable{n}.csv'
    mcda_problem_description = ProblemDescription(criteriaFileName=criteriaFile,
                                                  performanceTableFileName=perfFile)

    directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/SIMULATION/CBTO{n}'
    # directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/SIMULATION/'


    Tn = Tn_for_OfflineSimulator(n)
    Tn_star = Tn_star_for_OfflineSimulator(n)             #star c'est pour indique |A| >= 2; |B| >= 2

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


    # dmFile = 'model136.csv'
    dmFile = 'model1.csv'

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

    print("Un Star length", len(SUn_star))

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
    if cumul == 0:
        print("BINGO")
        exit()
    NOT_EXPLAINABLE_REDUCED_PAIRS_LIST = [(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in not_explained_not_critical_pairs]
    mnd = 0
    A_max = None
    B_list = None
    for i in range(len(L)-1):
        nd = 0
        Bi_list = list()
        for j in range(i+1, len(L)):
            A, B = L[i] - L[j], L[j] - L[i]
            if (A, B) in NOT_EXPLAINABLE_REDUCED_PAIRS_LIST:
                nd += 1
                Bi_list.append(L[j])
        if nd > mnd:
            A_max = L[i]
            B_list = Bi_list
            mnd = nd
    print("MND of {}, {} = {}".format(dmFile, Engine, mnd), A_max, B_list)
    Un_star_critical = set(SUn_star) & set(CriticalPair)
    pi_dominance_relation_copy = PI().getRelation()["dominanceRelation"].copy()

    deduced_critical_pairs = list()
    not_deduced_critical_pairs = list()

    for crit in Un_star_critical:
        a, b = crit
        altD = mcda_problem_description[a]
        altd = mcda_problem_description[b]

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
    print("({}) Un Star Fundamental Critical Pairs".format(len(L)), L)
    L = [(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in deduced_critical_pairs]
    print("({}) Deduced Critical Pairs".format(len(L)), L)
    L = [(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in not_explained_not_critical_pairs]
    print("({}) Not explained not critical pairs".format(len(L)), L)


# Modele with BCR = C
# n = 3
    # model1.csv [('12', '3'), ('3', '2'), ('2', '1')]
    # model2.csv [('3', '12'), ('2', '1')]

#  n = 4
    # model1.csv : [('4', '123'), ('3', '12'), ('2', '1')]
    # model2.csv [('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
    # model7.csv [('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model8.csv [('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]


# n = 5
    # model1.csv  [('5', '1234'), ('4', '123'), ('3', '12'), ('2', '1')]
    # model2.csv  [('1234', '5'), ('5', '234'), ('4', '123'), ('3', '12'), ('2', '1')]
    # model31.csv [('5', '1234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
    # model32.csv [('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
    # model230.csv [('5', '1234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model231.csv [('1234', '5'), ('5', '234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model256.csv [('5', '1234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model257.csv [('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]

# n = 6
    # model1.csv       [('6', '12345'), ('5', '1234'), ('4', '123'), ('3', '12'), ('2', '1')]
    # model2.csv       [('12345', '6'), ('6', '2345'), ('5', '1234'), ('4', '123'), ('3', '12'), ('2', '1')]
    # model315.csv     [('6', '12345'), ('1234', '5'), ('5', '234'), ('4', '123'), ('3', '12'), ('2', '1')]
    # model316.csv     [('12345', '6'), ('6', '2345'), ('1234', '5'), ('5', '234'), ('4', '123'), ('3', '12'), ('2', '1')]
    # model10691.csv   [('6', '12345'), ('5', '1234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
    # model10692.csv   [('12345', '6'), ('6', '2345'), ('5', '1234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
    # model10875.csv   [('6', '12345'), ('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
    # model10876.csv   [('12345', '6'), ('6', '2345'), ('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
    # model58518.csv   [('6', '12345'), ('5', '1234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model58519.csv   [('12345', '6'), ('6', '2345'), ('5', '1234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model58704.csv   [('6', '12345'), ('1234', '5'), ('5', '234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model58705.csv   [('12345', '6'), ('6', '2345'), ('1234', '5'), ('5', '234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model64282.csv   [('6', '12345'), ('5', '1234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model64283.csv   [('12345', '6'), ('6', '2345'), ('5', '1234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model64462.csv   [('6', '12345'), ('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]
    # model64463.csv   [('12345', '6'), ('6', '2345'), ('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]
