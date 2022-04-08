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

    # Engine = Explain.Order2SwapExplanation
    # Engine = Explain.brut_force_general_1_vs_k_and_k_vs_1_MixedExplanation
    # Engine = Explain.general_1_vs_k_MixedExplanation
    Engine = Explain.general_k_vs_1_MixedExplanation


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
    niveau = -1
    CorrespondingSetDict = correspondingSet(n)
    # print(CorrespondingSetDict)

    for dmFile in os.listdir(directory):
        niveau += 1
        if niveau % 500 == 0: print(niveau, datetime.now())

        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, n)
        CBTOrderBySetsOfCriteria = [CorrespondingSetDict[elm] for elm in CBTOrder]
        # print(CBTOrderBySetsOfCriteria)
        # exit(0)

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

        NOT_EXPLAINABLE_REDUCED_PAIRS_LIST = [(CorrespondingSetDict[a], CorrespondingSetDict[b]) for a, b in not_explainable_pairs]  # REDUCED ie. sans les neutres

        res = 0
        A_best_but_not_explainable = list()
        number_of_A_considered = 0
        for i in range(len(CBTOrderBySetsOfCriteria)):            # Je suis plus fin que ceci : [excluons l'alternative subset de tous les criteres (2^n - 2 candidats donc)]
            is_explainable = True
            to_take_into_account = False
            criteria_considered_set = set()
            for k in range(i, len(CBTOrderBySetsOfCriteria)):
                criteria_considered_set = criteria_considered_set | CBTOrderBySetsOfCriteria[k]
                if len(criteria_considered_set) == n:      # Pas très bonne facon de tester la significativite de tous les critères (ce 30/01/22)
                    to_take_into_account = True
                    break
            if to_take_into_account:
                number_of_A_considered += 1
                for j in range(i+1, len(CBTOrderBySetsOfCriteria)):
                    A, B = CBTOrderBySetsOfCriteria[i] - CBTOrderBySetsOfCriteria[j], CBTOrderBySetsOfCriteria[j] - CBTOrderBySetsOfCriteria[i]
                    if (A, B) in NOT_EXPLAINABLE_REDUCED_PAIRS_LIST:
                        find_an_intermediaire = False
                        for k in range(i+1, j):
                            C = CBTOrderBySetsOfCriteria[k]
                            if (C, B) not in NOT_EXPLAINABLE_REDUCED_PAIRS_LIST:
                                find_an_intermediaire = True
                                break

                        is_explainable = find_an_intermediaire
                        break
                if is_explainable:
                    res += 1
                else:
                    A_best_but_not_explainable.append(CBTOrderBySetsOfCriteria[i])

        RESULT[dmFile] = {'model': dmFile, 'metric-value': res, 'number-of-alt-considered': number_of_A_considered, 'metric-value-percent': round(100*res/number_of_A_considered,1),
                          "best-alt-not-explainable": ["".join([str(a) for a in A]) for A in A_best_but_not_explainable]}
        # print("Metrics of {}, {} = {}".format(dmFile, Engine, res), A_best_but_not_explainable)
    # print(RESULT)
    # with open(f'Metrics-For-Dialog-Values-1m-m1-Decomposition-{n}.csv', 'w', newline='') as csvfile:
    with open(f'Metrics-For-Dialog-Values-m1-Decomposition-{n}.csv', 'w', newline='') as csvfile:
    # with open(f'Metrics-For-Dialog-Values-1m-Decomposition-{n}.csv', 'w', newline='') as csvfile:
    # with open(f'Metrics-For-Dialog-Values-1-1-Decomposition-{n}.csv', 'w', newline='') as csvfile:

        fieldnames = ['model', 'metric-value', 'number-of-alt-considered', 'metric-value-percent', "best-alt-not-explainable"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in RESULT.values():
            writer.writerow(row)
