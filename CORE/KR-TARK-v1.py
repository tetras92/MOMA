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

    Engine1 = Explain.general_MixedExplanation
    Engine2 = Explain.brut_force_general_1_vs_k_and_k_vs_1_MixedExplanation
    TotalRequirementsChecked = 0

    Explainable1 = 0
    Explainable2 = 0

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

        CPn, CPnDict = nCoveringPairs(directory + '/' + dmFile, n)

        dm = WS_DM(directory+'/'+dmFile)

        assert(len(STn) == cardSTn[n])

        PI().clear()
        N().clear()

        Dict_Non_PI = dict()
        for info in [non_pi_elem for non_pi_elem in NonPI()]:
            Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
            Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info


        for a, b in CriticalPair:
            Dialog(Dict_Non_PI[(a, b)]).madeWith(dm)        # chargement du modèle


        Response1 = set()
        Response2 = set()
        cumul1, cumul2 = 0, 0

        for dif, cpndif in CPnDict.items():
            for a, b in set(cpndif) - set(CriticalPair):
            # for a, b in set(CPn) - set(CriticalPair):
                altD = mcda_problem_description[a]
                altd = mcda_problem_description[b]

                ok, text = Engine1(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
                if ok:
                    cumul1 += 1
                    cumul2 += 1
                    DictCumulDif1[dif] += 1
                    DictCumulDif2[dif] += 1
                    # Explainable1 += 1
                    # Explainable2 += 1   # par définition
                else:
                    ok, text = Engine2(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
                    if ok:
                        cumul2 += 1
                        DictCumulDif2[dif] += 1
                    # Explainable2 += 1
        Explainable1 += cumul1
        Explainable2 += cumul2



        ModeleSpec[dmFile] = (cumul1, cumul2)
        if niveau % 500 == 0:
            print("Explainable1", Explainable1 / len(CPn) / (niveau+1), "Explainable2", Explainable2 / len(CPn) / (niveau+1),"avancement", niveau+1, "at", str(datetime.now()))


    print("Explainable1", Explainable1, "Explainable2", Explainable2, "total", len(CPn) * len(os.listdir(directory)), "avancement", niveau+1, "at", str(datetime.now()))
    print("Explainable1", Explainable1 / len(CPn) / len(os.listdir(directory)), "Explainable2", Explainable2 / len(CPn) / len(os.listdir(directory)))
    print("Explainable 1 :")
    for dif in DictCumulDif1:
        print(f'{dif} : {DictCumulDif1[dif]/DictTotalDif[dif]/len(os.listdir(directory))}')
    print("Explainable 2 :")
    for dif in DictCumulDif2:
        print(f'{dif} : {DictCumulDif2[dif]/DictTotalDif[dif]/len(os.listdir(directory))}')
    # print(ModeleSpec)

### --- n = 6 e k_max = m
# avec les triviaux 1 vs 5
# Explainable1 3359230 Explainable2 3583627 total 3849797 avancement 124187 at 2021-02-04 01:05:33.025103
# Explainable1 0.8725732811366418 Explainable2 0.9308612895692941

# sans les triviaux
# Explainable1 2614108 Explainable2 2838505 total 3104675 avancement 124187 at 2021-02-04 01:05:33.025103
# Explainable1 0.8419908686094357 Explainable2 0.9142679990659248

### --- n = 6 e k_max = m//2
# Explainable1 2614337 Explainable2 2838505 total 3104675 avancement 124187 at 2021-02-04 06:21:43.454297
# Explainable1 0.8420646283427412 Explainable2 0.9142679990659247

### --- n = 5 e k_max = m
# Explainable1 0.8761627906976744 Explainable2 0.8761627906976744


########################################################################################################
### --- n = 5 e k_max = m
# Explainable1 2334 Explainable2 2334 total 2650 avancement 265 at 2021-02-11 12:44:08.765169
# Explainable1 0.8807547169811321 Explainable2 0.8807547169811321
# Explainable 1 :
# 1 : 0.8807547169811321
# Explainable 2 :
# 1 : 0.8807547169811321


### --- n = 6 e k_max = m
# Explainable1 701523 Explainable2 780091 total 865150 avancement 34606 at 2021-02-11 14:26:45.626668
# Explainable1 0.8108686354967346 Explainable2 0.9016829451540195
# Explainable 1 :
# 2 : 0.9803560076287349
# 0 : 0.5566375772987343
# Explainable 2 :
# 2 : 0.9803637134215647
# 0 : 0.7836617927527019
