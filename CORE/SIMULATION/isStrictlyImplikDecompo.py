from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.Explanation import Explain
from CORE.SIMULATION.CBTOprocessing import nCoveringPairs, flat_CBTO_formated_for_OfflineSimulator, Tn_for_OfflineSimulator, difficultyDict
import os
from CORE.Dialog import Dialog
import random
from CORE.DM import WS_DM
from datetime import datetime

from CORE.Tools import AS_LEAST_AS_GOOD_AS, NOT_AS_LEAST_AS_GOOD_AS


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

    Engine1 = Explain.general_MixedExplanation
    Engine2 = Explain.brut_force_general_1_vs_k_and_k_vs_1_MixedExplanation
    TotalRequirementsChecked = 0

    Explainable1 = 0
    Explainable2 = 0

    criteriaFile = f'/home/manuel239/PycharmProjects/MOMA/CORE/CSVFILES/ijcai_criteria{n}.csv'
    perfFile = f'/home/manuel239/PycharmProjects/MOMA/CORE/CSVFILES/ijcai_fullPerfTable{n}.csv'
    mcda_problem_description = ProblemDescription(criteriaFileName=criteriaFile,
                                                  performanceTableFileName=perfFile)

    directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/SIMULATION/KR-CBTO{n}'
    # directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/SIMULATION/MCDA-CBTO{n}'

    Tn = Tn_for_OfflineSimulator(n)

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

    niveau = -1


    ModeleSpec = dict()
    for dmFile in os.listdir(directory):
        niveau += 1

        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, n)
        STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]

        CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn]  # contigu et disjoints
        DDict, CorrespondanceDict = difficultyDict(directory + '/' + dmFile, n)

        DDictF = {ddictpair: LessDifficult & set(CriticalPair) for ddictpair, LessDifficult in DDict.items() if ddictpair in CriticalPair}
        if dmFile == 'model106.csv':
            for c_pair, lessDifficult_cpairs in DDictF.items():
                if len(lessDifficult_cpairs) > 0 : # and len(CorrespondanceDict[c_pair[0]] | CorrespondanceDict[c_pair[1]]) < n:
                    c_pair_swap_object = None
                    for info in [elem for elem in NonPI()]:
                        if (info.alternative1.id, info.alternative2.id) in lessDifficult_cpairs:
                            info.termP = AS_LEAST_AS_GOOD_AS()
                        elif (info.alternative2.id, info.alternative1.id) in lessDifficult_cpairs:
                            info.termP = NOT_AS_LEAST_AS_GOOD_AS()
                        elif (info.alternative1.id, info.alternative2.id) == c_pair:
                            c_pair_swap_object = SwapObject(info.alternative1, info.alternative2)
                        elif (info.alternative2.id, info.alternative1.id) == c_pair:
                            c_pair_swap_object = SwapObject(info.alternative2, info.alternative1)
                    if c_pair_swap_object.is_necessary(mcda_problem_description, PI().getRelation()["dominanceRelation"]):
                        print("Found", c_pair, lessDifficult_cpairs)
                        print([CorrespondanceDict[elem] for elem in CBTOrder])
                        print(f'({CorrespondanceDict[c_pair[0]]}, {CorrespondanceDict[c_pair[1]]})',
                              [f'({CorrespondanceDict[oth_pair[0]]}, {CorrespondanceDict[oth_pair[1]]})' for oth_pair in lessDifficult_cpairs])
                        print("======", dmFile)
                    PI().clear()
