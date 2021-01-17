from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.Tools import AS_LEAST_AS_GOOD_AS, NOT_AS_LEAST_AS_GOOD_AS
from CORE.Explanation import Explain
from CORE.SIMULATION.CBTOprocessing import CBTO_formated_for_OfflineSimulator, flat_CBTO_formated_for_OfflineSimulator, Tn_for_OfflineSimulator, infoToExplain_formated_for_OfflineSimulator, regenerateCBTOfromModel, val
from CORE.Recommendation import RecommendationWrapper, KRankingRecommendation, KBestRecommendation
import os, numpy as np
from CORE.InformationPicker import RandomPicker
from CORE.Dialog import Dialog
import random
from CORE.DM import WS_DM
def convert_info(infoId):
    a, b = infoId
    bin_a = str(bin(a))[2:]
    bin_b = str(bin(b))[2:]
    str_a = ""
    str_b = ""

    r = (len(bin_a))
    for l in bin_a:
        if l == '1':
            str_a = str(r) + str_a
        r -= 1

    r = (len(bin_b))
    for l in bin_b:
        if l == '1':
            str_b = str(r) + str_b
        r -=1

    return str_a, str_b

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
    Engine = Explain.brut_force_general_1_vs_k_and_k_vs_1_MixedExplanation
    RequirementsOnSwapObject = pro_geq_2_req
    TotalRequirementsChecked = 0
    Explainable = 0

    criteriaFile = f'CSVFILES/ijcai_criteria{n}.csv'
    perfFile = f'CSVFILES/ijcai_fullPerfTable{n}.csv'
    mcda_problem_description = ProblemDescription(criteriaFileName=criteriaFile,
                                                  performanceTableFileName=perfFile)

    directory = f'SIMULATION/CoherentBooleanTermOrders{n}'


    Tn = Tn_for_OfflineSimulator(n)

    dmTemoin = WS_DM(directory+'/model1.csv')
    Dn = list()
    # print(len(NonPI()))
    N().update(mcda_problem_description, **PI().getRelation()) # But : éliminer la dominance
    N().drop()
    # print(len(NonPI()))

    Dict_Non_PI = dict()
    for info in [non_pi_elem for non_pi_elem in NonPI()]:
        Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
        Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info

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


    nb_min_of_Critical_pair= float("inf")
    nb_max_of_Critical_pair= 0
    niveau = 0
    for dmFile in os.listdir(directory):
        # dmFile = 'model1.csv'
        niveau += 1
        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory+'/'+ dmFile, n)
        STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]

        SUn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Un]

        CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn] # contigu et disjoints
        nb_min_of_Critical_pair = min(len(CriticalPair), nb_min_of_Critical_pair)
        nb_max_of_Critical_pair = max(len(CriticalPair), nb_max_of_Critical_pair)
        # print(CriticalPair)
        DeductibleCriticalPair = list()
        dm = WS_DM(directory+'/'+dmFile)

        for c_pair in CriticalPair:
            c_pair_swap_object = None
            for info in [elem for elem in NonPI()]:
                if (info.alternative1.id, info.alternative2.id) in CriticalPair and (info.alternative1.id, info.alternative2.id) != c_pair:
                    info.termP = AS_LEAST_AS_GOOD_AS()
                elif (info.alternative2.id, info.alternative1.id) in CriticalPair and (info.alternative1.id, info.alternative2.id) != c_pair:
                    info.termP = NOT_AS_LEAST_AS_GOOD_AS()
                elif info.alternative2.id in c_pair and info.alternative1.id in c_pair:
                    altD_id = min([info.alternative2.id, info.alternative1.id], key=lambda x: CBTOrder.index(x))
                    if info.alternative1.id == altD_id:
                        c_pair_swap_object = SwapObject(info.alternative1, info.alternative2)
                    else:
                        c_pair_swap_object = SwapObject(info.alternative2, info.alternative1)
            if not c_pair_swap_object is None and c_pair_swap_object.is_necessary(mcda_problem_description, PI().getRelation()["dominanceRelation"]):
                # if RequirementsOnSwapObject(c_pair_swap_object): TotalRequirementsChecked += 1
                DeductibleCriticalPair.append(c_pair)
            PI().clear()

        NecessaryAskedPairsQueries = list(set(CriticalPair) - set(DeductibleCriticalPair))

        assert(len(SUn) == cardSUn[n])
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
        N().update(mcda_problem_description, **PI().getRelation())
        # print("===============N : \n{}".format(str(N())))
        # print("==============Non-PI : \n{}".format(str(NonPI())))
        assert len(NonPI()) == 0
        for a, b in (set(SUn) - set(CriticalPair)):
            altD = mcda_problem_description[a]
            altd = mcda_problem_description[b]

            swap_object_ab = SwapObject(altD, altd)
            if RequirementsOnSwapObject(swap_object_ab) and len(swap_object_ab.con_arguments_set()) > 1:      # Non trivial
                TotalRequirementsChecked += 1
                ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
                # okT, textT = EngineTest(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
                if ok:
                    Explainable += 1
                    # print(text)
                # if okT and not ok:
                #     print("Reussite\n", textT)


        # for a, b in (set(SDn) - set(CriticalPair)):
        #     altD = mcda_problem_description[a]
        #     altd = mcda_problem_description[b]
        #
        #     swap_object_ab = SwapObject(altD, altd)
        #     if RequirementsOnSwapObject(swap_object_ab):
        #         TotalRequirementsChecked += 1
        #         Explainable += 1                                        # by definition

        # if niveau % 1000 == 0:

        print("Explainable", Explainable, "Total", TotalRequirementsChecked, "avancement", niveau)
        # break

    # print("Critical Pair (min et max)", nb_min_of_Critical_pair, nb_max_of_Critical_pair)


