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
        SUn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                     max(pair, key=lambda x: CBTOrder.index(x))) for pair in Un]

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


        # Un_star_deductible_non_critical_Set = set(SUn_star) - set(CriticalPair)
        # deductible_len = len(Un_star_deductible_non_critical_Set)
        #
        # # Pairs of Un_star deductible non explainable
        # deductible_but_non_explainable = list()
        #
        # for a, b in Un_star_deductible_non_critical_Set:
        #     altD = mcda_problem_description[a]
        #     altd = mcda_problem_description[b]
        #
        #     ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
        #     if not ok:
        #         deductible_but_non_explainable.append((altD, altd))
        #     else:
        #         deductible_but_non_explainable.append((altD, altd))
        #
        # Un_star_critical = set(SUn_star) & set(CriticalPair)
        #
        # for crit in Un_star_critical:
        #     a, b = crit
        #     altD = mcda_problem_description[a]
        #     altd = mcda_problem_description[b]
        #
        #     if NecessaryPreference.adjudicate(mcda_problem_description, deductible_but_non_explainable, (altD, altd)):
        #         print(CorrespondingSetDict[crit[0]], CorrespondingSetDict[crit[1]])
        #
        Un_deductible_non_critical_Set = set(SUn) - set(CriticalPair)
        deductible_len = len(Un_deductible_non_critical_Set)

        # Pairs of Un_star deductible non explainable
        deductible_but_non_explainable = list()

        for a, b in Un_deductible_non_critical_Set:
            altD = mcda_problem_description[a]
            altd = mcda_problem_description[b]

            deductible_but_non_explainable.append((altD, altd))

        Un_critical = set(SUn) & set(CriticalPair)

        for crit in Un_critical:
            a, b = crit
            altD = mcda_problem_description[a]
            altd = mcda_problem_description[b]

            if NecessaryPreference.adjudicate(mcda_problem_description, deductible_but_non_explainable, (altD, altd)):
                print([(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in Un_deductible_non_critical_Set])
                print("imply: ", (CorrespondingSetDict[crit[0]], CorrespondingSetDict[crit[1]]))
