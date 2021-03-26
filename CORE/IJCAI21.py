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
# def convert_info(infoId):
#     a, b = infoId
#     bin_a = str(bin(a))[2:]
#     bin_b = str(bin(b))[2:]
#     str_a = ""
#     str_b = ""
#
#     r = (len(bin_a))
#     for l in bin_a:
#         if l == '1':
#             str_a = str(r) + str_a
#         r -= 1
#
#     r = (len(bin_b))
#     for l in bin_b:
#         if l == '1':
#             str_b = str(r) + str_b
#         r -=1
#
#     return str_a, str_b

def pro_geq_2_req(swap_object):
    return swap_object.number_of_pro_arguments() >= 2

def pro_geq_3_req(swap_object):
    return swap_object.number_of_pro_arguments() >= 3

def always_true_req(swap_object):
    return True

if __name__ == "__main__":
    n = 5
    cardSDn = {4: 19,
               5: 64,
               6: 203}

    cardSUn = {4: 6,
               5: 26,
               6: 98}

    cardSTn = {4: 25,
               5: 90,
               6: 301}
    # EngineTest = Explain.general_MixedExplanation
    Engine1 = Explain.general_MixedExplanation
    Engine2 = Explain.brut_force_general_1_vs_k_and_k_vs_1_MixedExplanation
    RequirementsOnSwapObject = pro_geq_2_req
    TotalRequirementsChecked = 0
    Explainable0 = 0
    Explainable1 = 0
    Explainable2 = 0
    NbCriticalPairs = 0

    criteriaFile = f'CSVFILES/ijcai_criteria{n}.csv'
    perfFile = f'CSVFILES/ijcai_fullPerfTable{n}.csv'
    mcda_problem_description = ProblemDescription(criteriaFileName=criteriaFile,
                                                  performanceTableFileName=perfFile)

    directory = f'SIMULATION/CBTO{n}'


    Tn = Tn_for_OfflineSimulator(n)
    Tn_star = Tn_star_for_OfflineSimulator(n)
    print("triviaux", len(Tn) - len(Tn_star))
    SuperSetDict_star, SubSetDict_star = superSet_and_subset_Dicts(n)
    print("Super", SuperSetDict_star)
    print("Sub", SubSetDict_star)

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
    Explainable1 += Explainable0 #par définition
    Explainable2 += Explainable0 # par definition

    # ExplN = 0

    TotalRequirementsChecked += len(os.listdir(directory)) * len(Tn_star)

    nb_min_of_Critical_pair= float("inf")
    nb_max_of_Critical_pair= 0
    niveau = -1
    for dmFile in os.listdir(directory):
        # dmFile = 'model5872.csv'
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
        # SUn_star = Un_star_for_IJCAI_N(directory + '/' + dmFile, n)

        CriticalPair_star = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn_star]  # contigu et disjoints
        NbCriticalPairs += len(CriticalPair_star)

        nb_min_of_Critical_pair = min(len(CriticalPair), nb_min_of_Critical_pair)
        nb_max_of_Critical_pair = max(len(CriticalPair), nb_max_of_Critical_pair)
        # if niveau % 100 == 0 : print("CR len", len(CriticalPair), "niveau", niveau)
        # DeductibleCriticalPair = list()
        dm = WS_DM(directory+'/'+dmFile)

        # for c_pair in CriticalPair:
        #     c_pair_swap_object = None
        #     for info in [elem for elem in NonPI()]:
        #         if (info.alternative1.id, info.alternative2.id) in CriticalPair and (info.alternative1.id, info.alternative2.id) != c_pair:
        #             info.termP = AS_LEAST_AS_GOOD_AS()
        #         elif (info.alternative2.id, info.alternative1.id) in CriticalPair and (info.alternative1.id, info.alternative2.id) != c_pair:
        #             info.termP = NOT_AS_LEAST_AS_GOOD_AS()
        #         elif info.alternative2.id in c_pair and info.alternative1.id in c_pair:
        #             altD_id = min([info.alternative2.id, info.alternative1.id], key=lambda x: CBTOrder.index(x))
        #             if info.alternative1.id == altD_id:
        #                 c_pair_swap_object = SwapObject(info.alternative1, info.alternative2)
        #             else:
        #                 c_pair_swap_object = SwapObject(info.alternative2, info.alternative1)
        #     if not c_pair_swap_object is None and c_pair_swap_object.is_necessary(mcda_problem_description, PI().getRelation()["dominanceRelation"]):
        #         # if RequirementsOnSwapObject(c_pair_swap_object): TotalRequirementsChecked += 1
        #         DeductibleCriticalPair.append(c_pair)
        #     PI().clear()
        # # print(DeductibleCriticalPair)
        # NecessaryAskedPairsQueries = list(set(CriticalPair) - set(DeductibleCriticalPair))

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

        # print("============= ", PI().getRelation()["dominanceRelation"])
        # N().update(mcda_problem_description, **PI().getRelation())
        # # print("===============N : \n{}".format(str(N())))
        # # print("==============Non-PI : \n{}".format(str(NonPI())))
        # assert len(NonPI()) == 0
        # for a, b in (set(SUn) - set(CriticalPair)):
        # for a, b in SUn:
        #     altD = mcda_problem_description[a]
        #     altd = mcda_problem_description[b]
        #
        #     swap_object_ab = SwapObject(altD, altd)
        #     if RequirementsOnSwapObject(swap_object_ab) and len(swap_object_ab.con_arguments_set()) > 1:      # Non trivial
        #         TotalRequirementsChecked += 1
        #         if (a, b) in CriticalPair:
        #             NbCriticalPairs += 1
        #         else :
        #             ok, text = Engine1(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
        #             if ok:
        #                 Explainable1 += 1
        #                 Explainable2 += 1 #par définition
        #             else:
        #                 ok, text = Engine2(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
        #                 if ok:
        #                     Explainable2 += 1
        #             # print(text)
        #         # if okT and not ok:
        #         #     print("Reussite\n", textT)

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
            # if (altD.id, altd.id) in Response1:
            #     Explainable1 += 1
            #     Explainable2 += 1
            #     ExplN += 1
            #     # print("allo")
            # elif (altD.id, altd.id) in Response2:
            #     Explainable2 += 1
            #     ExplN += 1
            # else:
            ok, text = Engine1(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
            # activ1+=1
            if ok:
                Explainable1 += 1
                Explainable2 += 1   # par définition
                # ExplN += 1
                # for sub_altd in SubSetDict_star[altd.id]:
                #     for sup_alD in SuperSetDict_star[altD.id]:
                #         Response1.add((sup_alD, sub_altd))
                #         Response2.add((sup_alD, sub_altd))
            else:
                ok, text = Engine2(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
                if ok:
                    Explainable2 += 1
                    # ExplN += 1
                    # for sub_altd in SubSetDict_star[altd.id]:
                    #     for sup_alD in SuperSetDict_star[altD.id]:
                    #         Response2.add((sup_alD, sub_altd))


        # for a, b in set(STn) - set(SUn): #SDn
        #     altD = mcda_problem_description[a]
        #     altd = mcda_problem_description[b]
        #
        #     swap_object_ab = SwapObject(altD, altd)
        #     if RequirementsOnSwapObject(swap_object_ab) and len(swap_object_ab.con_arguments_set()) > 1:
        #         TotalRequirementsChecked += 1
        #         if (a, b) in CriticalPair:
        #             print("never in")
        #             NbCriticalPairs += 1
        #         Explainable1 += 1                                        # by definition
        #         Explainable2 += 1
        #         Explainable0 += 1
        # if niveau == 1 :
        #     break
        # print(activ1)
        if niveau % 50 == 0:
            print("Explainable0", Explainable0, "Explainable1", Explainable1, "Explainable2", Explainable2, "Total", TotalRequirementsChecked, "avancement", niveau, "at", str(datetime.now()))
        # break

    print("Critical Pair (min et max)", nb_min_of_Critical_pair, nb_max_of_Critical_pair)
    print("Explainable0", Explainable0, "Explainable1", Explainable1, "Explainable2", Explainable2, "CR", NbCriticalPairs, "Total", TotalRequirementsChecked, "avancement", niveau+1, "at", str(datetime.now()))
    # print("EXN", ExplN)
# n=4
# Explainable1 32 Explainable2 32 CR 10 Total 42 avancement 14 at 2021-01-27 00:53:32.130078
# n = 5
# Explainable1 10545 Explainable2 10545 CR 1372 Total 12900 avancement 516 at 2021-01-27 00:54:52.959304


# n =6 (mCda)
# Explainable0 2560844 Explainable1 3727528 Explainable2 3739016 CR 268479 Total 4498780 avancement 34606 at 2021-01-30 23:45:34.804780
