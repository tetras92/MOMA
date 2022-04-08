from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.Explanation import Explain
from CORE.SIMULATION.CBTOprocessing import nCoveringPairs, flat_CBTO_formated_for_OfflineSimulator, \
    Tn_for_OfflineSimulator, Un_star_for_IJCAI, Tn_star_for_OfflineSimulator, correspondingSet
import os
from CORE.Dialog import Dialog
import random
from CORE.DM import WS_DM
from datetime import datetime
from CORE.NecessaryPreference import NecessaryPreference
from CORE.SmallestSetOfPairs import SmallestSetOfPairs

def contenu(file):
    with open(file)as ofile:
        return ofile.readlines()

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

    directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/SIMULATION/KR-CBTO{n}'

    # Tn = Tn_for_OfflineSimulator(n)
    # Tn_star = Tn_star_for_OfflineSimulator(n)
    #
    # dmTemoin = WS_DM(directory + '/model1.csv')
    # Dn = list()
    # N().update(mcda_problem_description, **PI().getRelation())  # But : éliminer la dominance
    # N().drop()
    # NonPI().filter()
    # assert len(NonPI()) == len(Tn)
    #
    # Dict_Non_PI = dict()
    # for info in [non_pi_elem for non_pi_elem in NonPI()]:
    #     Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
    #     Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info
    #
    # # Singletons Hypothesis
    # for i in range(n - 1):
    #     altId_inf = 2 ** i
    #     altId_sup = 2 ** (i + 1)
    #     Dn.append((altId_inf, altId_sup))
    #     Dialog(Dict_Non_PI[(altId_inf, altId_sup)]).madeWith(dmTemoin)
    # # print("============= ", PI().getRelation()["dominanceRelation"])
    #
    # N().update(mcda_problem_description, **PI().getRelation())
    # for pair in Tn:
    #     for infoN in N():
    #         if infoN.alternative1.id in pair and infoN.alternative2.id in pair:
    #             Dn.append(pair)
    # Un = list(set(Tn) - set(Dn))
    #
    # assert (len(Dn) == cardSDn[n])
    # assert (len(Tn) == cardSTn[n])
    # assert (len(Un) == cardSUn[n])
    #
    # N().clear()
    # PI().clear()
    #
    # Dn_star = set(Dn) & set(Tn_star)
    # Un_star = set(Un) & set(Tn_star)
    # # print("to examine", len(Dn_star) + len(Un_star))
    niveau = -1
    #
    RESULT = 0
    CorrespondingSetDict = correspondingSet(n)
    plus_serre = float("inf")
    v_p_s = None
    v_p_l = None
    plus_large = 0
    for dmFile in os.listdir(directory):
        niveau += 1
        # if niveau % 500 == 0: print(niveau, datetime.now())
        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, n)
        strCBTOrder = [CorrespondingSetDict[elmt] for elmt in CBTOrder]
        i2456 = strCBTOrder.index("2456")
        i1356 = strCBTOrder.index("1356")
        i2346 = strCBTOrder.index("2346")
        i1256 = strCBTOrder.index("1256")
        i1345 = strCBTOrder.index("1345")
        i1245 = strCBTOrder.index("1245")
        i1234 = strCBTOrder.index("1234")
        if RESULT % 100 == 0:
            print(RESULT, niveau)
        if i2456 < i1356 < i2346 < i1256 < i1345 < i1245 < i1234:
            cut = strCBTOrder[i2456: i1234+1]
            if len(cut) < plus_serre:
                plus_serre = len(cut)
                v_p_s = cut, contenu(directory + '/' + dmFile)
            if len(cut) > plus_large:
                plus_large = len(cut)
                v_p_l = cut, contenu(directory + '/' + dmFile)
            # print(dmFile, len(cut))
            RESULT+=1
            # print(cut, len(cut))
            # print(cut, len(cut))

    print("large", v_p_l) # \omega = 2,7,18,26,36,58
    print("serre", v_p_s) # \omega = 24,26,31,32,38,42

        # STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
        #         max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]

