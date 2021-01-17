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
    nb_random_pi = 10

    # Cn : arbitraire
    Cn = {4 : (5, 10),
          5 : (8, 16),
          6 : (13 , 28)
          }
    Pasn = {4 : 1,
            5 : 2,
            6 : 3
            }
    # Engines = [Explain.Order2SwapExplanation, Explain.atMost2OrderNecessarySwapAndPIExplanation, Explain.Order2SwapMixedExplanation, Explain.general_1_vs_k_MixedExplanation, Explain.general_k_vs_1_MixedExplanation, Explain.general_MixedExplanation]
    # RequirementsOnSwapObject = [pro_geq_2_req, always_true_req, pro_geq_2_req, pro_geq_2_req, pro_geq_3_req, pro_geq_2_req]
    Engines = [Explain.Order2SwapExplanation, Explain.Order2SwapMixedExplanation, Explain.general_1_vs_k_MixedExplanation, Explain.general_k_vs_1_MixedExplanation, Explain.general_MixedExplanation]
    RequirementsOnSwapObject = [pro_geq_2_req, pro_geq_2_req, pro_geq_2_req, pro_geq_3_req, pro_geq_2_req]

    Results = {engine: {taille_pi: {'checkedRequirements': 0,
                                    'success': 0} for taille_pi in range(Cn[n][0], Cn[n][1] + 1, Pasn[n])}
                for engine in Engines}
    criteriaFile = f'CSVFILES/ijcai_criteria{n}.csv'
    perfFile = f'CSVFILES/ijcai_fullPerfTable{n}.csv'
    mcda_problem_description = ProblemDescription(criteriaFileName=criteriaFile,
                                                  performanceTableFileName=perfFile)

    directory = f'SIMULATION/CoherentBooleanTermOrders{n}'

    # niveau = 1
    Tn = Tn_for_OfflineSimulator(n)
    STnDict = dict()
    for dmFile in os.listdir(directory):
        CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory+'/'+ dmFile, n)
        STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
                max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]
        STnDict[dmFile] = STn
    # print("parti")
    for taille_pi in range(Cn[n][0], Cn[n][1] + 1, Pasn[n]):
        print("taille", taille_pi)
        for _ in range(nb_random_pi):
            Tn_copy = Tn[:]
            random.shuffle(Tn_copy)
            Queries = Tn_copy[: taille_pi]                 # mêmes queries à tous les DM
            PotentialNec = Tn_copy[taille_pi:]
            for dmFile in os.listdir(directory):
                CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory+'/'+ dmFile, n)
                STn = STnDict[dmFile]
                dm = WS_DM(directory+'/'+dmFile)
                # STn_copy = STn[:]
                # random.shuffle(STn_copy)
                # Queries = STn_copy[:taille_pi]
                # PotentialNec = STn_copy[taille_pi:]
                Dict_Non_PI = dict()
                for info in [non_pi_elem for non_pi_elem in NonPI()]:
                    Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
                    Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info
                for query in Queries:
                    Dialog(Dict_Non_PI[(query[0], query[1])]).madeWith(dm)
                for potential_nec in PotentialNec:
                    info_to_check = Dict_Non_PI[(potential_nec[0], potential_nec[1])]
                    altD, altd = None, None
                    if (info_to_check.alternative1.id, info_to_check.alternative2.id) in STn:
                        altD = info_to_check.alternative1
                        altd = info_to_check.alternative2
                    else:
                        altD = info_to_check.alternative2
                        altd = info_to_check.alternative1

                    swap_object = SwapObject(altD, altd)
                    if swap_object.is_necessary(mcda_problem_description, PI().getRelation()["dominanceRelation"]):
                        enginesOr = []
                        for eng_i in range(len(Engines)-1):
                            if RequirementsOnSwapObject[eng_i](swap_object):
                                Results[Engines[eng_i]][taille_pi]['checkedRequirements'] += 1
                                if eng_i == 2: #if checked for 1->k then checked for (1-k or k->1)
                                    Results[Engines[-1]][taille_pi]['checkedRequirements'] += 1
                                ok, _ = Engines[eng_i](mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
                                if eng_i == 2 or eng_i == 3: # if of for 1->k or k->1 then ok for (1-k or k->1)
                                        enginesOr.append(ok)
                                if ok:
                                    Results[Engines[eng_i]][taille_pi]['success'] += 1
                        if any(enginesOr):
                            Results[Engines[-1]][taille_pi]['success'] += 1
                PI().clear()


    for eng, value in Results.items():
        print(eng, value)

    # nb_min_of_Critical_pair= float("inf")
    # nb_max_of_Critical_pair= 0
    # for dmFile in os.listdir(directory):
    #     CBTOrder = flat_CBTO_formated_for_OfflineSimulator(directory+'/'+ dmFile, n)
    #
    #     STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
    #             max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]
    #
    #     CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn]
    #     nb_min_of_Critical_pair = min(len(CriticalPair), nb_min_of_Critical_pair)
    #     nb_max_of_Critical_pair = max(len(CriticalPair), nb_max_of_Critical_pair)
    #     print(CriticalPair)
    #     DeductibleCriticalPair = list()
    #     for c_pair in CriticalPair:
    #         c_pair_swap_object = None
    #         for info in [elem for elem in NonPI()]:
    #             if (info.alternative1.id, info.alternative2.id) in CriticalPair and (info.alternative1.id, info.alternative2.id) != c_pair:
    #                 info.termP = AS_LEAST_AS_GOOD_AS()
    #             elif (info.alternative2.id, info.alternative1.id) in CriticalPair and (info.alternative1.id, info.alternative2.id) != c_pair:
    #                 info.termP = NOT_AS_LEAST_AS_GOOD_AS()
    #             elif info.alternative2.id in c_pair and info.alternative1.id in c_pair:
    #                 altD_id = min([info.alternative2.id, info.alternative1.id], key=lambda x: CBTOrder.index(x))
    #                 if info.alternative1.id == altD_id:
    #                     c_pair_swap_object = SwapObject(info.alternative1, info.alternative2)
    #                 else:
    #                     c_pair_swap_object = SwapObject(info.alternative2, info.alternative1)
    #         if not c_pair_swap_object is None and c_pair_swap_object.is_necessary(mcda_problem_description, PI().getRelation()["dominanceRelation"]):
    #                 DeductibleCriticalPair.append(c_pair)
    #         PI().clear()
    #
    # print(nb_min_of_Critical_pair, nb_max_of_Critical_pair)


    # -- OLD VERSION -- #
    # Bilan = dict()
    # for dmFile in os.listdir(directory):
    #     Bilan[dmFile] = dict()
    #     dm = WS_DM(directory+'/'+dmFile)
    #     # Dominance Relation To add to PI()
    #     R = CBTO_formated_for_OfflineSimulator(directory+'/'+dmFile, n)
    #     # print("R", R)
    #     # Pairwise Comparison to Explain
    #     E = infoToExplain_formated_for_OfflineSimulator(n)
    #     # print("E", E)
    #     # print(mcda_problem_description)
    #
    #     for infoE in E:
    #         Bilan[dmFile][convert_info(infoE)] = {'deductible': False, 'successes': 0, 'failures':0}
    #         deductible = False
    #         R_copy = R.copy()
    #         if infoE in [(a, b) for a, b in R]:
    #             R_copy.remove(infoE)
    #         elif infoE in [(b, a) for a, b in R]:
    #             R_copy.remove((infoE[1], infoE[0]))
    #         else:
    #             deductible = True
    #             # print(convert_info(infoE), "is deductible by Necessary Preference Relation " + dmFile)
    #         if not deductible:
    #             for info in [elem for elem in NonPI()]:
    #                 if (info.alternative1.id, info.alternative2.id) in R_copy:
    #                     info.termP = AS_LEAST_AS_GOOD_AS()
    #                 elif (info.alternative2.id, info.alternative1.id) in R_copy:
    #                     info.termP = NOT_AS_LEAST_AS_GOOD_AS()
    #             N().update(mcda_problem_description, **PI().getRelation())
    #
    #             for infoN in N():
    #                 if (infoN.alternative1.id, infoN.alternative2.id) == infoE or (infoN.alternative2.id, infoN.alternative1.id) == infoE:
    #                     deductible = True
    #         N().clear()
    #         PI().clear()
    #         if deductible:
    #             Bilan[dmFile][convert_info(infoE)]['deductible'] = True
    #             for i in range(nb_random_pi):
    #                 picker = RandomPicker()
    #                 nb_queries = min(np.random.randint(int(0.5 * Cn[n]), int(1.5 * Cn[n]) + 1), len(NonPI()))
    #                 for query in range(nb_queries):
    #                     info = picker.pick(NonPI())
    #                     Dialog(info).madeWith(dm)
    #
    #                 N().update(mcda_problem_description, **PI().getRelation())
    #                 ExplanationEngine = Explain.general_1_vs_k_MixedExplanation
    #
    #                 ok, text = False, ""
    #                 L = [val(elmt, n) for elmt in regenerateCBTOfromModel(directory+'/'+dmFile, n)]
    #                 if L.index(infoE[0]) > L.index(infoE[1]):
    #                     ok, text = ExplanationEngine(mcda_problem_description, PI().getRelation()["dominanceRelation"],
    #                                                  object=(mcda_problem_description[infoE[0]], mcda_problem_description[infoE[1]]))
    #                 else :
    #                     ok, text = ExplanationEngine(mcda_problem_description, PI().getRelation()["dominanceRelation"],
    #                                                  object=(mcda_problem_description[infoE[1]], mcda_problem_description[infoE[0]]))
    #
    #                 if ok:
    #                     Bilan[dmFile][convert_info(infoE)]['successes'] += 1
    #                 else:
    #                     Bilan[dmFile][convert_info(infoE)]['failures'] += 1
    #                 N().clear()
    #                 PI().clear()
    #             # print(convert_info(infoE), "is deductible by Necessary Preference Relation " + dmFile)
    #     print(dmFile, Bilan[dmFile])





    # print("============= ", len(PI().getRelation()["dominanceRelation"]), PI().getRelation()["dominanceRelation"])

    # recommander.update(mcda_problem_description, **PI().getRelation())
    # print(recommander.canRecommend)
    # print(recommander.recommendation)
    # N().update(mcda_problem_description, **PI().getRelation())
    #
    #
    #
    # # print(N())
    # # Explanation Engine
    # ExplanationEngine = Explain.general_1_vs_k_MixedExplanation
    # seen = 0
    # for info in N():
    #     ok, text = False, ""
    #     if (info.alternative1.id, info.alternative2.id) in E:
    #         seen += 1
    #         ok, text = ExplanationEngine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(info.alternative1, info.alternative2))
    #     elif (info.alternative2.id, info.alternative1.id) in E:
    #         seen += 1
    #         ok, text = ExplanationEngine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(info.alternative2, info.alternative1))
    #     if ok:
    #         print(text)
    # print("seen", seen)

#                      n = 4
# <function Explain.Order2SwapExplanation at 0x7f89ada8a290> {5: {'checkedRequirements': 6551, 'success': 4606}, 6: {'checkedRequirements': 7450, 'success': 5660}, 7: {'checkedRequirements': 7580, 'success': 5742}, 8: {'checkedRequirements': 7415, 'success': 5847}, 9: {'checkedRequirements': 7190, 'success': 5541}, 10: {'checkedRequirements': 7245, 'success': 5855}}
# <function Explain.Order2SwapMixedExplanation at 0x7f89adab5ef0> {5: {'checkedRequirements': 6551, 'success': 6502}, 6: {'checkedRequirements': 7450, 'success': 7354}, 7: {'checkedRequirements': 7580, 'success': 7439}, 8: {'checkedRequirements': 7415, 'success': 7256}, 9: {'checkedRequirements': 7190, 'success': 6951}, 10: {'checkedRequirements': 7245, 'success': 6914}}
# <function Explain.general_1_vs_k_MixedExplanation at 0x7f89adab80e0> {5: {'checkedRequirements': 6551, 'success': 6506}, 6: {'checkedRequirements': 7450, 'success': 7362}, 7: {'checkedRequirements': 7580, 'success': 7445}, 8: {'checkedRequirements': 7415, 'success': 7270}, 9: {'checkedRequirements': 7190, 'success': 6991}, 10: {'checkedRequirements': 7245, 'success': 6937}}
# <function Explain.general_k_vs_1_MixedExplanation at 0x7f89adab8170> {5: {'checkedRequirements': 3049, 'success': 3049}, 6: {'checkedRequirements': 3090, 'success': 3090}, 7: {'checkedRequirements': 3248, 'success': 3248}, 8: {'checkedRequirements': 2964, 'success': 2964}, 9: {'checkedRequirements': 3104, 'success': 3104}, 10: {'checkedRequirements': 2872, 'success': 2872}}
# <function Explain.general_MixedExplanation at 0x7f89adab8200> {5: {'checkedRequirements': 6551, 'success': 6539}, 6: {'checkedRequirements': 7450, 'success': 7440}, 7: {'checkedRequirements': 7580, 'success': 7552}, 8: {'checkedRequirements': 7415, 'success': 7366}, 9: {'checkedRequirements': 7190, 'success': 7139}, 10: {'checkedRequirements': 7245, 'success': 7131}}

#
# n= 5
#
# <function Explain.Order2SwapExplanation at 0x7f21bcdff290> {8: {'checkedRequirements': 82215 / 138714, 'success': 61042}, 10: {'checkedRequirements': 125229, 'success': 58347}, 12: {'checkedRequirements': 138714, 'success': 82215}, 14: {'checkedRequirements': 138957, 'success': 82714}, 16: {'checkedRequirements': 147062, 'success': 91928}}
# <function Explain.Order2SwapMixedExplanation at 0x7f21bce2aef0> {8: {'checkedRequirements': 104128, 'success': 104055}, 10: {'checkedRequirements': 125229, 'success': 124362}, 12: {'checkedRequirements': 138714, 'success': 137490}, 14: {'checkedRequirements': 138957, 'success': 136926}, 16: {'checkedRequirements': 147062, 'success': 141394}}
# <function Explain.general_1_vs_k_MixedExplanation at 0x7f21bce2d0e0> {8: {'checkedRequirements': 104128, 'success': 104128}, 10: {'checkedRequirements': 125229, 'success': 124432}, 12: {'checkedRequirements': 138714, 'success': 137565}, 14: {'checkedRequirements': 138957, 'success': 137328}, 16: {'checkedRequirements': 147062, 'success': 142195}}
# <function Explain.general_k_vs_1_MixedExplanation at 0x7f21bce2d170> {8: {'checkedRequirements': 75352, 'success': 75316}, 10: {'checkedRequirements': 89289, 'success': 89289}, 12: {'checkedRequirements': 94531, 'success': 94531}, 14: {'checkedRequirements': 94547, 'success': 94543}, 16: {'checkedRequirements': 97523, 'success': 97501}}
# <function Explain.general_MixedExplanation at 0x7f21bce2d200> {8: {'checkedRequirements': 104128, 'success': 104128}, 10: {'checkedRequirements': 125229, 'success': 125131}, 12: {'checkedRequirements': 138714, 'success': 138641}, 14: {'checkedRequirements': 138957, 'success': 138644}, 16: {'checkedRequirements': 147062, 'success': 145828}}
#
# Process finished with exit code 0
