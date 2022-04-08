from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.Explanation import Explain
from CORE.SIMULATION.CBTOprocessing import correspondingSet, flat_CBTO_formated_for_OfflineSimulator, \
    Tn_for_OfflineSimulator, Un_star_for_IJCAI, Tn_star_for_OfflineSimulator, correspondingSet
import os
from CORE.Dialog import Dialog
import random
from CORE.DM import WS_DM
from datetime import datetime

from CORE.PLNE_for_Delta11_decomposition import decompose as decompose_under_L0
from CORE.PLNE_for_Delta1m_decomposition import decompose as decompose_under_L1
from CORE.PLNE_for_Deltam1_decomposition import decompose as decompose_under_L2
from CORE.PLNE_for_Delta1m_m1_decomposition import decompose as decompose_under_L3

if __name__ == "__main__":
    m = 6


    def encode_preference_model_as_dict(filename):
        with open(filename) as preferenceModelFile:
            reader = csv.DictReader(preferenceModelFile)
            w_list = list()
            for row in reader:
                for criterion in reader.fieldnames:
                    w_list.append(int(row[criterion]))
            w_list = sorted(w_list, reverse=False)
            return {chr(ord('1') + i): w_list[i] for i in range(m)}

    def recommendation_algorithm(AlternativesSubsetsList, Wdict, decomposition_function=None):
        SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                               key=lambda alt: sum([Wdict[criterion] for criterion in alt]), reverse=True)
        # print(Wdict)
        S_ = [None]
        # print(SortedAlternativesSubsetsList, AlternativesSubsetsList)
        # assert SortedAlternativesSubsetsList == AlternativesSubsetsList
        for v in range(1, len(SortedAlternativesSubsetsList)):
            proSet, conSet = SortedAlternativesSubsetsList[0] - SortedAlternativesSubsetsList[v], \
                             SortedAlternativesSubsetsList[v] - SortedAlternativesSubsetsList[0]
            success_v, Sv = decomposition_function(proSet, conSet, Wdict)
            if not success_v:
                return False, None
            else:
                S_.append(Sv)

        return True, S_

    def recommendation_algorithm_any_tree_height(AlternativesSubsetsList, W_dict_p, decomposition_function=None):
        SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                               key=lambda alt: sum([W_dict_p[criterion] for criterion in alt]), reverse=True)
        SS = dict()
        for v in range(1, len(SortedAlternativesSubsetsList)):
            success_v = False
            for u in range(0, v):
                proSet, conSet = SortedAlternativesSubsetsList[u] - SortedAlternativesSubsetsList[v], \
                                 SortedAlternativesSubsetsList[v] - SortedAlternativesSubsetsList[u]
                success_uv, Suv = decomposition_function(proSet, conSet, W_dict_p)
                if success_uv:
                    success_v = True
                    SS[(u, v)] = Suv
                    break
            if not success_v:
                return False, None

        return True, SS

    def recommendation_relaxation(AlternativesSubsetsList, Wdict, decomposition_function=None, kmax=3):
        SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                               key=lambda alt: sum([Wdict[criterion] for criterion in alt]), reverse=True)
        # print(SortedAlternativesSubsetsList)

        S = dict()
        k_ = 2
        while k_ <= kmax + 1:
            v = k_
            while v <= len(SortedAlternativesSubsetsList):
                S[v] = dict()
                u = 1
                failure_uv = False
                while not failure_uv and u <= k_ - 1:
                    proSet, conSet = SortedAlternativesSubsetsList[u - 1] - SortedAlternativesSubsetsList[v - 1], \
                                     SortedAlternativesSubsetsList[v - 1] - SortedAlternativesSubsetsList[u - 1]
                    success_uv, Suv = decomposition_function(proSet, conSet, Wdict)
                    # print(SortedAlternativesSubsetsList[u - 1], "vs", SortedAlternativesSubsetsList[v - 1], "res", Suv)
                    if not success_uv:
                        failure_uv = True
                        break
                    S[v][u] = Suv
                    u += 1
                if failure_uv:
                    k_ += 1
                    break
                v += 1
            if v <= len(SortedAlternativesSubsetsList):
                del S[v]
                continue

            return True, S

        return False, None

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

    # Engine = decompose_under_L0
    Engine = decompose_under_L3

    criteriaFile = f'/home/manuel239/PycharmProjects/MOMA/CORE/CSVFILES/ijcai_criteria{m}.csv'
    perfFile = f'/home/manuel239/PycharmProjects/MOMA/CORE/CSVFILES/ijcai_fullPerfTable{m}.csv'
    mcda_problem_description = ProblemDescription(criteriaFileName=criteriaFile,
                                                  performanceTableFileName=perfFile)

    directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/SIMULATION/KR-CBTO{m}'

    Tn = Tn_for_OfflineSimulator(m)
    Tn_star = Tn_star_for_OfflineSimulator(m)

    dmTemoin = WS_DM(directory + '/model1.csv')
    Dn = list()
    N().update(mcda_problem_description, **PI().getRelation())  # But : éliminer la dominance
    N().drop()
    NonPI().filter()
    assert len(NonPI()) == len(Tn)

    Dict_Non_PI = dict()
    for info in [non_pi_elem for non_pi_elem in NonPI()]:
        Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
        Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info

    # Singletons Hypothesis
    for i in range(m - 1):
        altId_inf = 2 ** i
        altId_sup = 2 ** (i + 1)
        Dn.append((altId_inf, altId_sup))
        Dialog(Dict_Non_PI[(altId_inf, altId_sup)]).madeWith(dmTemoin)
    # print("============= ", PI().getRelation()["dominanceRelation"])

    N().update(mcda_problem_description, **PI().getRelation())
    for pair in Tn:
        for infoN in N():
            if infoN.alternative1.id in pair and infoN.alternative2.id in pair:
                Dn.append(pair)
    Un = list(set(Tn) - set(Dn))

    assert (len(Dn) == cardSDn[m])
    assert (len(Tn) == cardSTn[m])
    assert (len(Un) == cardSUn[m])

    N().clear()
    PI().clear()

    Dn_star = set(Dn) & set(Tn_star)
    Un_star = set(Un) & set(Tn_star)

    RESULT = dict()
    niveau = -1
    CorrespondingSetDict = correspondingSet(m)
    LISTE = list()

    # dmFile = 'model3.csv'
    for dmFile in os.listdir(directory):
        # dmFile = 'model3.csv'
        # print(dmFile)
        niveau += 1
        if niveau % 50 == 0:
            print(niveau, datetime.now())
            if len(LISTE) > 0:
                LISTE = sorted(LISTE)
                print(len(LISTE), ":", min(LISTE), LISTE[len(LISTE)//4], LISTE[len(LISTE)//2], LISTE[3*len(LISTE)//4], max(LISTE))

        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, m)
        CBTOrderBySetsOfCriteria = [CorrespondingSetDict[elm] for elm in CBTOrder]
        # print(CBTOrderBySetsOfCriteria)
        # exit(0)
        STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]

        CriticalPair = [(CBTOrder[j], CBTOrder[j + 1]) for j in range(len(CBTOrder) - 1) if
                        (CBTOrder[j], CBTOrder[j + 1]) in STn]  # contigu et disjoints
        # print(CriticalPair)
        SUn_star = [(min(pair, key=lambda x: CBTOrder.index(x)),
                     max(pair, key=lambda x: CBTOrder.index(x))) for pair in Un_star]
        file = directory + '/' + dmFile
        dm = WS_DM(file)
        W_dict = encode_preference_model_as_dict(filename=file)
        # assert(len(STn) == cardSTn[n])

        PI().clear()
        N().clear()

        Dict_Non_PI = dict()
        for info in [non_pi_elem for non_pi_elem in NonPI()]:
            Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
            Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info

        for a, b in CriticalPair:
            Dialog(Dict_Non_PI[(a, b)]).madeWith(dm)  # chargement du modèle

        NOT_EXPLAINABLE_REDUCED_PAIRS_LIST = list()
        for a, b in set(SUn_star):
            altD = CorrespondingSetDict[a]
            altd = CorrespondingSetDict[b]
            proSet, conSet = altD - altd, altd - altD
            proSet = {str(e) for e in proSet}
            conSet = {str(e) for e in conSet}
            ok, _ = Engine(proSet, conSet, W_dict)
            if not ok:
                NOT_EXPLAINABLE_REDUCED_PAIRS_LIST.append((altD, altd))

        res = 0
        A_best_but_not_explainable = list()
        number_of_A_considered = 0

        for i in range(
                len(CBTOrderBySetsOfCriteria)):  # prenons aussi l'alternative rassemblant tous les critères
            is_explainable = True
            to_take_into_account = False
            criteria_considered_set = set()
            for k in range(i, len(CBTOrderBySetsOfCriteria)):
                criteria_considered_set = criteria_considered_set | CBTOrderBySetsOfCriteria[k]
                if len(criteria_considered_set) == m:  # Pas très bonne facon de tester la significativite de tous les critères (ce 30/01/22)
                    to_take_into_account = True
                    break
            # completer la verification de to_take_into_account

            if to_take_into_account:
                number_of_A_considered += 1
                W_dict = {int(e): val for e, val in W_dict.items()}
                is_explainable, _ = recommendation_relaxation(CBTOrderBySetsOfCriteria[i:], W_dict, Engine)
                # is_explainable, _ = recommendation_algorithm(CBTOrderBySetsOfCriteria[i:], W_dict, Engine)
                # for j in range(i + 1, len(CBTOrderBySetsOfCriteria)):
                #     A, B = CBTOrderBySetsOfCriteria[i] - CBTOrderBySetsOfCriteria[j], CBTOrderBySetsOfCriteria[j] - \
                #            CBTOrderBySetsOfCriteria[i]
                #     if (A, B) in NOT_EXPLAINABLE_REDUCED_PAIRS_LIST:
                #         # find_an_intermediaire = False
                #         # for k in range(i + 1, j):
                #         #     C = CBTOrderBySetsOfCriteria[k]
                #         #     if (C, B) not in NOT_EXPLAINABLE_REDUCED_PAIRS_LIST:
                #         #         find_an_intermediaire = True
                #         #         break
                #         #
                #         # is_explainable = find_an_intermediaire
                #         is_explainable = False
                #         break
                if is_explainable:
                    # print(CBTOrderBySetsOfCriteria[i])
                    res += 1
                    # reco_ok, _ = recommendation_algorithm(CBTOrderBySetsOfCriteria[i:], W_dict, Engine)
                    # if not reco_ok:
                    #     print("relax wins")
                else:
                    A_best_but_not_explainable.append(CBTOrderBySetsOfCriteria[i])
        # print("considered", number_of_A_considered, "positive", res, "proportion", round(100. * res / number_of_A_considered, 2), "%")
        LISTE.append(round(res / number_of_A_considered, 4))
        # exit(0)
    LISTE = sorted(LISTE)
    print(len(LISTE), ":", min(LISTE), LISTE[len(LISTE)//4], LISTE[len(LISTE)//2], LISTE[3*len(LISTE)//4], max(LISTE))
