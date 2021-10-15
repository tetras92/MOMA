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



    RESULT = 0
    CorrespondingSetDict = correspondingSet(n)
    for dmFile in os.listdir(directory):
        niveau += 1
        if niveau % 500 == 0: print(niveau, datetime.now())
        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, n)
        STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]

        CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn] # contigu et disjoints
        concerned = False
        for a, b in CriticalPair:
            a_str, b_str = CorrespondingSetDict[a], CorrespondingSetDict[b]
            if len(a_str) > 1 and len(b_str) > 1:
                concerned = True
                break

        if not concerned: RESULT += 1
    print(RESULT)

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
