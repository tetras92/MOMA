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


    RESULT = dict()

    CorrespondingSetDict = correspondingSet(n)
    # print(CorrespondingSetDict)
    for dmFile in os.listdir(directory):
        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, n)
        CBTOrderBySetsOfCriteria = [CorrespondingSetDict[elm] for elm in CBTOrder]
        # L.reverse()

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




        not_explainable_pairs = list()
        for a, b in set(SUn_star):
            altD = mcda_problem_description[a]
            altd = mcda_problem_description[b]

            ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
            if not ok:
                # cumul += 1
                not_explainable_pairs.append((a, b))

        NOT_EXPLAINABLE_REDUCED_PAIRS_LIST = [(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in not_explainable_pairs]
        mnd = 0
        A_max = set()
        B_list = list()
        for i in range(len(CBTOrderBySetsOfCriteria) - 1):
            nd = 0
            Bi_list = list()
            for j in range(i+1, len(CBTOrderBySetsOfCriteria)):
                A, B = CBTOrderBySetsOfCriteria[i] - CBTOrderBySetsOfCriteria[j], CBTOrderBySetsOfCriteria[j] - CBTOrderBySetsOfCriteria[i]
                if (A, B) in NOT_EXPLAINABLE_REDUCED_PAIRS_LIST:
                    nd += 1
                    Bi_list.append(CBTOrderBySetsOfCriteria[j])
            if nd > mnd:
                A_max = CBTOrderBySetsOfCriteria[i]
                B_list = Bi_list
                mnd = nd
        RESULT[dmFile] = {'model': dmFile, 'mnd-value': mnd, 'best-alternative': "".join([str(a) for a in A_max]),
                          "challengers": ["".join([str(b) for b in B]) for B in B_list]}
        print("MND of {}, {} = {}".format(dmFile, Engine, mnd), A_max, B_list)

    with open(f'MNT-Values-1mDecomposition-{n}.csv', 'w', newline='') as csvfile:
    # with open(f'MNT-Values-m1Decomposition-{n}.csv', 'w', newline='') as csvfile:

        fieldnames = ['model', 'mnd-value', 'best-alternative', "challengers"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in RESULT.values():
            writer.writerow(row)
