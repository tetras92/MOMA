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
    n = 4

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
    card = 0
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
        Un_star_deductible_and_adjacent = Un_star_deductible_non_critical_Set & set(CriticalPair)

        if len(Un_star_deductible_and_adjacent) > 0:
            RESULT[dmFile] = {'model': dmFile, "critical_length": len(CriticalPair), 'minimal_number_of_queries': smallestsize1, "non_trivial_critical_pairs": len(set(SUn_star) & set(CriticalPair)), 'non_trivial_deduced_critical_pairs': len(Un_star_deductible_and_adjacent)}
    print("Nombre de modeles concernes", len(RESULT), round(100 * len(RESULT) / len(os.listdir(directory)), 2), "%")

    with open(f'XP_TotalOrderJustification{n}.csv', 'w', newline='') as csvfile:
        fieldnames = ['model', "critical_length", 'minimal_number_of_queries', "non_trivial_critical_pairs", 'non_trivial_deduced_critical_pairs']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in RESULT.values():
            writer.writerow(row)

# n = 5
# Nombre de modeles concernes 72 / 516, 14 %
# model106.csv [('25', '134')]
# model69.csv [('14', '23')]
# model173.csv [('23', '14')]
# model329.csv [('234', '15')]
# model153.csv [('134', '25')]
# model328.csv [('234', '15')]
# model368.csv [('134', '25')]
# model105.csv [('234', '15')]
# model478.csv [('124', '35')]
# model424.csv [('15', '234')]
# model188.csv [('23', '14')]
# model178.csv [('23', '14')]
# model124.csv [('23', '14')]
# model462.csv [('124', '35')]
# model148.csv [('15', '234')]
# model467.csv [('23', '14')]
# model94.csv [('134', '25')]
# model403.csv [('35', '124')]
# model305.csv [('14', '23')]
# model334.csv [('25', '134')]
# model406.csv [('24', '15')]
# model332.csv [('25', '134')]
# model408.csv [('24', '15')]
# model111.csv [('25', '134')]
# model439.csv [('23', '14')]
# model475.csv [('15', '24')]
# model419.csv [('24', '15')]
# model330.csv [('25', '134')]
# model72.csv [('14', '23')]
# model158.csv [('134', '25')]
# model161.csv [('134', '25')]
# model301.csv [('14', '23')]
# model303.csv [('14', '23')]
# model425.csv [('15', '234')]
# model156.csv [('15', '34')]
# model309.csv [('14', '23')]
# model333.csv [('25', '134')]
# model128.csv [('23', '14')]
# model473.csv [('15', '24')]
# model485.csv [('23', '14')]
# model357.csv [('15', '234')]
# model91.csv [('134', '25')]
# model194.csv [('23', '14')]
# model366.csv [('15', '34')]
# model190.csv [('23', '14')]
# model460.csv [('15', '24')]
# model477.csv [('124', '35')]
# model151.csv [('15', '34')]
# model381.csv [('234', '15')]
# model184.csv [('23', '14')]
# model396.csv [('14', '23')]
# model363.csv [('14', '23')]
# model336.csv [('34', '15')]
# model378.csv [('23', '14')]
# model487.csv [('23', '14')]
# model414.csv [('14', '23')]
# model387.csv [('23', '14')]
# model298.csv [('14', '23')]
# model398.csv [('14', '23')]
# model296.csv [('14', '23')]
# model78.csv [('14', '23')]
# model307.csv [('14', '23')]
# model382.csv [('25', '134')]
# model331.csv [('25', '134')]
# model404.csv [('35', '124')]
# model162.csv [('134', '25')]
# model165.csv [('134', '25')]
# model108.csv [('34', '15')]
# model441.csv [('23', '14')]
# model113.csv [('34', '15')]
# model360.csv [('14', '23')]
# model417.csv [('35', '124')]

# n = 6
# Nombre de modeles concernes 101264 81.54 %
