from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.Explanation import Explain
from CORE.SIMULATION.CBTOprocessing import nCoveringPairs, flat_CBTO_formated_for_OfflineSimulator, Tn_for_OfflineSimulator
import os
from CORE.Dialog import Dialog
import random
from CORE.DM import WS_DM
from datetime import datetime




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

    Engine = Explain.Order2SwapExplanation

    TotalRequirementsChecked = 0

    Explainable0 = 0

    criteriaFile = f'/home/manuel239/PycharmProjects/MOMA/CORE/CSVFILES/ijcai_criteria{n}.csv'
    perfFile = f'/home/manuel239/PycharmProjects/MOMA/CORE/CSVFILES/ijcai_fullPerfTable{n}.csv'
    mcda_problem_description = ProblemDescription(criteriaFileName=criteriaFile,
                                                  performanceTableFileName=perfFile)

    directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/SIMULATION/MCDA-CBTO{n}'


    Tn = Tn_for_OfflineSimulator(n)

    dmTemoin = WS_DM(directory+'/model1.csv')
    Dn = list()
    N().update(mcda_problem_description, **PI().getRelation()) # But : éliminer la dominance
    N().drop()
    NonPI().filter()
    assert len(NonPI()) == len(Tn)

    CPnTemoin, CPnDictTemoin = nCoveringPairs(directory + '/model1.csv', n)
    DictCumulDif = {dif : 0 for dif in CPnDictTemoin}
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

        SUn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Un]

        SDn = set(STn) - set(SUn)

        # CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn]  # contigu et disjoints

        CPn, CPnDict = nCoveringPairs(directory + '/' + dmFile, n)

        cumul = len(set(CPn) & SDn)
        for dif, cpndif in CPnDict.items():
            DictCumulDif[dif] += len(set(cpndif) & SDn)

        # dm = WS_DM(directory+'/'+dmFile)
        #
        # assert(len(STn) == cardSTn[n])
        #
        # PI().clear()
        # N().clear()
        #
        # Dict_Non_PI = dict()
        # for info in [non_pi_elem for non_pi_elem in NonPI()]:
        #     Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
        #     Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info
        #
        #
        # for a, b in CriticalPair:
        #     Dialog(Dict_Non_PI[(a, b)]).madeWith(dm)        # chargement du modèle
        #
        #
        # Response1 = set()
        # Response2 = set()
        # cumul=0
        # for a, b in set(STn) - set(SUn): #SDn
        #     altD = mcda_problem_description[a]
        #     altd = mcda_problem_description[b]
        #
        # for a, b in set(CPn) - set(CriticalPair):
        #     altD = mcda_problem_description[a]
        #     altd = mcda_problem_description[b]
        #     swap_object_ab = SwapObject(altD, altd)
        #     if len(swap_object_ab.pro_arguments_set()) >= len(swap_object_ab.con_arguments_set()):
        #         ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
        #         if ok:
        #             cumul += 1

        Explainable0 += cumul
        if niveau % 500 == 0:
            print("Explainable0", Explainable0 / len(CPn) / (niveau+1),"avancement", niveau+1, "at", str(datetime.now()))


    print("Explainable0", Explainable0, "total", len(CPn) * len(os.listdir(directory)), "avancement", niveau+1, "at", str(datetime.now()))
    print("Explainable0", Explainable0 / len(CPn) / len(os.listdir(directory)))
    for dif in DictCumulDif:
        print(f'{dif} : {DictCumulDif[dif]/DictTotalDif[dif]/len(os.listdir(directory))}')
    # print(ModeleSpec)

### --- n = 6 et k_max = m
# avec les triviaux 1 vs 5
# Explainable1 3359230 Explainable2 3583627 total 3849797 avancement 124187 at 2021-02-04 01:05:33.025103
# Explainable1 0.8725732811366418 Explainable2 0.9308612895692941

# sans les triviaux
# Explainable1 2614108 Explainable2 2838505 total 3104675 avancement 124187 at 2021-02-04 01:05:33.025103
# Explainable1 0.8419908686094357 Explainable2 0.9142679990659248

### --- n = 6 et k_max = m//2
# Explainable1 2614337 Explainable2 2838505 total 3104675 avancement 124187 at 2021-02-04 06:21:43.454297
# Explainable1 0.8420646283427412 Explainable2 0.9142679990659247

### --- n = 8 et k_max = 1
# Explainable0 620000 total 1190000 avancement 10000 at 2021-02-05 10:31:03.623727
# Explainable0 0.5210084033613445

### --- n = 7 et k_max = 1
# Explainable0 280000 total 560000 avancement 10000 at 2021-02-05 10:16:22.138531
# Explainable0 0.5

### --- n = 6 et k_max = 1
# Explainable0 1738618 total 3104675 avancement 124187 at 2021-02-04 11:59:35.369804
# Explainable0 0.56

### --- n = 5 et k_max = 1
# Explainable0 2580 total 5160 avancement 516 at 2021-02-05 10:10:38.455644
# Explainable0 0.5

### --- n = 4 et k_max = 1
# Explainable0 28 total 42 avancement 14 at 2021-02-05 10:11:44.535021
# Explainable0 0.67


##########################################################################
# MCDA - CBTO
### --- n = 4
# Explainable0 4 total 6 avancement 2 at 2021-02-11 12:28:24.251433
# Explainable0 0.6666666666666666
# 0 : 0.6666666666666666

### --- n = 5
# Explainable0 1325 total 2650 avancement 265 at 2021-02-11 12:29:45.442400
# Explainable0 0.5
# 1 : 0.5
