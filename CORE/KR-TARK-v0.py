from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.Tools import AS_LEAST_AS_GOOD_AS, NOT_AS_LEAST_AS_GOOD_AS
from CORE.Explanation import Explain
from CORE.SIMULATION.CBTOprocessing import superSet_and_subset_Dicts, CBTO_formated_for_OfflineSimulator, Un_star_for_IJCAI, flat_CBTO_formated_for_OfflineSimulator, Tn_for_OfflineSimulator, Tn_star_for_OfflineSimulator, infoToExplain_formated_for_OfflineSimulator, regenerateCBTOfromModel, val
from CORE.Recommendation import RecommendationWrapper, KRankingRecommendation, KBestRecommendation
import os, numpy as np
from CORE.InformationPicker import RandomPicker
from CORE.Dialog import Dialog
import random
from CORE.DM import WS_DM
from datetime import datetime




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
    Engine1 = Explain.general_MixedExplanation
    Engine2 = Explain.brut_force_general_1_vs_k_and_k_vs_1_MixedExplanation
    TotalRequirementsChecked = 0
    Explainable0 = 0
    Explainable1 = 0
    Explainable2 = 0
    NbCriticalPairs = 0

    criteriaFile = f'CSVFILES/ijcai_criteria{n}.csv'
    perfFile = f'CSVFILES/ijcai_fullPerfTable{n}.csv'
    mcda_problem_description = ProblemDescription(criteriaFileName=criteriaFile,
                                                  performanceTableFileName=perfFile)

    directory = f'SIMULATION/SAMPLE-CBTO{n}'


    Tn = Tn_for_OfflineSimulator(n)
    Tn_star = Tn_star_for_OfflineSimulator(n)
    SuperSetDict_star, SubSetDict_star = superSet_and_subset_Dicts(n)
    # print("Super", SuperSetDict_star)
    # print("Sub", SubSetDict_star)

    dmTemoin = WS_DM(directory+'/model1.csv')
    Dn = list()
    # print(len(NonPI()))
    N().update(mcda_problem_description, **PI().getRelation()) # But : éliminer la dominance
    N().drop()
    # print(len(NonPI()))
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
    print("============= ", PI().getRelation()["dominanceRelation"])
    # PI().freeze()

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


    Explainable0 += len(os.listdir(directory)) * len(Dn_star)
    # Explainable0 += 1000 * len(Dn_star)
    Explainable1 += Explainable0 #par définition
    Explainable2 += Explainable0 # par definition

    TotalRequirementsChecked += len(os.listdir(directory)) * len(Tn_star)
    # TotalRequirementsChecked += 1000 * len(Tn_star)

    nb_min_of_Critical_pair= float("inf")
    nb_max_of_Critical_pair= 0
    niveau = -1


    # for ir in np.random.choice(range(1, len(os.listdir(directory))+1), 1000, replace=False):
    for dmFile in os.listdir(directory):
        # dmFile = f'model{ir}.csv'
        niveau += 1

        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory + '/' + dmFile, n)
        STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]

        # SUn = [(min(pair, key=lambda x: CBTOrder.index(x)),
        #         max(pair, key=lambda x: CBTOrder.index(x))) for pair in Un]

        CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn]  # contigu et disjoints

        STn_star = [(min(pair, key=lambda x: CBTOrder.index(x)),
                    max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn_star]

        SUn_star = Un_star_for_IJCAI(directory + '/' + dmFile, n)

        CriticalPair_star = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn_star]  # contigu et disjoints
        NbCriticalPairs += len(CriticalPair_star)

        nb_min_of_Critical_pair = min(len(CriticalPair), nb_min_of_Critical_pair)
        nb_max_of_Critical_pair = max(len(CriticalPair), nb_max_of_Critical_pair)
        # if niveau % 100 == 0 : print("CR len", len(CriticalPair), "niveau", niveau)
        # DeductibleCriticalPair = list()
        dm = WS_DM(directory+'/'+dmFile)

        # assert(len(SUn) == cardSUn[n])
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

        for cr_star in CriticalPair_star:
            if cr_star in SUn_star:
                SUn_star.remove(cr_star)
        # print(SUn_star)
        # activ1 = 0
        for a, b in SUn_star:
            altD = mcda_problem_description[a]
            altd = mcda_problem_description[b]
            # print("a, b ", (altD.id, altd.id))
            # print("1", Response1)
            # print("2", Response2)
            if (altD.id, altd.id) in Response1:
                Explainable1 += 1
                Explainable2 += 1
                # print("allo")
            elif (altD.id, altd.id) in Response2:
                Explainable2 += 1
            else:
                ok, text = Engine1(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
                # activ1+=1
                if ok:
                    Explainable1 += 1
                    Explainable2 += 1   # par définition
                    for sub_altd in SubSetDict_star[altd.id]:
                        for sup_alD in SuperSetDict_star[altD.id]:
                            Response1.add((sup_alD, sub_altd))
                            Response2.add((sup_alD, sub_altd))
                else:
                    ok, text = Engine2(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
                    if ok:
                        Explainable2 += 1
                        for sub_altd in SubSetDict_star[altd.id]:
                            for sup_alD in SuperSetDict_star[altD.id]:
                                Response2.add((sup_alD, sub_altd))

        if niveau % 500 == 0:
            print("Explainable0", Explainable0, "Explainable1", Explainable1, "Explainable2", Explainable2, "CR", NbCriticalPairs, "Total", TotalRequirementsChecked, "avancement", niveau, "at", str(datetime.now()))


    print("Critical Pair (min et max)", nb_min_of_Critical_pair, nb_max_of_Critical_pair)
    print("Explainable0", Explainable0, "Explainable1", Explainable1, "Explainable2", Explainable2, "CR", NbCriticalPairs, "Total", TotalRequirementsChecked, "avancement", niveau+1, "at", str(datetime.now()))

# n=4
# Explainable1 32 Explainable2 32 CR 10 Total 42 avancement 14 at 2021-01-27 00:53:32.130078
# n = 5
# Explainable1 10545 Explainable2 10545 CR 1372 Total 12900 avancement 516 at 2021-01-27 00:54:52.959304


# n =6 (mCda)
# Explainable0 2560844 Explainable1 3727528 Explainable2 3739016 CR 268479 Total 4498780 avancement 34606 at 2021-01-30 23:45:34.804780

#n =7 echantillon 1000 (CR_max = 27) CR_min 13
# Explainable0 301000 Explainable1 494499 Explainable2 496497 CR 11195 Total 546000 avancement 1000 at 2021-01-31 15:00:40.153786

#n =7 echantillon 10000 (CR_max = 27) CR_min 12
# Explainable0 3010000 Explainable1 4944928 Explainable2 4964140 CR 111480 Total 5460000 avancement 10000 at 2021-01-31 18:23:21.743322

#n =7 echantillon 1000 (CR_max = 31) CR_min 9
# Explainable0 301000 Explainable1 487657 Explainable2 488795 CR 12041 Total 546000 avancement 1000 at 2021-01-31 22:44:51.815204

# n = 7 echantillon 1000 (CR_max = 35) CR_min 8
# Explainable0 3010000 Explainable1 3010162 Explainable2 3010162 Total 5460000 avancement 0 at 2021-02-01 01:42:08.563986
# Critical Pair (min et max) 8 35
# Explainable0 3010000 Explainable1 4880364 Explainable2 4891399 CR 118869 Total 5460000 avancement 10000 at 2021-02-01 05:43:32.323244

# Explainable0 10980000 Explainable1 10980786 Explainable2 10980786 Total 20370000 avancement 0 at 2021-02-02 18:36:50.215758
# Explainable0 10980000 Explainable1 11372863 Explainable2 11375843 Total 20370000 avancement 500 at 2021-02-02 19:38:12.033127
# Explainable0 10980000 Explainable1 11765245 Explainable2 11770968 Total 20370000 avancement 1000 at 2021-02-02 20:38:05.920563
# Explainable0 10980000 Explainable1 12156585 Explainable2 12165154 Total 20370000 avancement 1500 at 2021-02-02 21:40:31.785924
# Explainable0 10980000 Explainable1 12549569 Explainable2 12561096 Total 20370000 avancement 2000 at 2021-02-02 22:40:08.026356
# Explainable0 10980000 Explainable1 12941189 Explainable2 12955577 Total 20370000 avancement 2500 at 2021-02-02 23:37:30.992998
# Explainable0 10980000 Explainable1 13333860 Explainable2 13351141 Total 20370000 avancement 3000 at 2021-02-03 00:34:02.412569
# Explainable0 10980000 Explainable1 13726833 Explainable2 13746798 Total 20370000 avancement 3500 at 2021-02-03 01:32:01.092169
# Explainable0 10980000 Explainable1 14120363 Explainable2 14143272 Total 20370000 avancement 4000 at 2021-02-03 02:28:39.627348
# Explainable0 10980000 Explainable1 14512843 Explainable2 14538480 Total 20370000 avancement 4500 at 2021-02-03 03:25:49.609073
# Explainable0 10980000 Explainable1 14906404 Explainable2 14934887 Total 20370000 avancement 5000 at 2021-02-03 04:23:11.144467
# Explainable0 10980000 Explainable1 15299594 Explainable2 15330818 Total 20370000 avancement 5500 at 2021-02-03 05:19:12.732215
# Explainable0 10980000 Explainable1 15692802 Explainable2 15726964 Total 20370000 avancement 6000 at 2021-02-03 06:14:37.703270
# Explainable0 10980000 Explainable1 16086905 Explainable2 16123726 Total 20370000 avancement 6500 at 2021-02-03 07:08:55.657622
