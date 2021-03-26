from CORE.SIMULATION.CBTOprocessing import CBTO_formated_for_OfflineSimulator, flat_CBTO_formated_for_OfflineSimulator, Tn_for_OfflineSimulator, infoToExplain_formated_for_OfflineSimulator, regenerateCBTOfromModel, val
import random
from CORE.InformationStore import NonPI, N, PI
from CORE.DM import WS_DM
from CORE.Dialog import Dialog
from CORE.Explanation import Explain
from CORE.ProblemDescription import *




if __name__ == "__main__":
    nb = 0
    n = 5
    min_ = 2**5
    for i in range(1, 516+1):
        dmFile = f'KR-CBTO{n}/model{i}.csv'
        cbto = regenerateCBTOfromModel(dmFile, n)
        i_15 = cbto.index({1, 5})
        i_12 = cbto.index({1,2})
        i_24 = cbto.index({2, 4})
        i_4 = cbto.index({4})
        i_5 = cbto.index({5})
        i_23 = cbto.index({2, 3})

        tmp = min(min_, abs(i_24 - i_15))

        # if min_ > tmp :
        #     min_ = tmp
        #     print(cbto, "n°", i)
        if i_15 == i_24 -1: #and i_5 <= i_23 - 1 and i_12 <= i_4 - 1:
            nb += 1
            print(cbto, "n°", i)
    print(nb)
    # while True:
    #     i = random.randint(1, 124187)
    #     dmFile = f'CoherentBooleanTermOrders6/model{i}.csv'
    #     cbto = regenerateCBTOfromModel(dmFile, n)
    #     ecart = cbto.index({5, 6}) - cbto.index({1, 2, 3, 4})
    #
    #     if ecart >= 2 and cbto.index({2,4,5}) < cbto.index({1,3,6}):
    #         print("model n°", i, "ecart = ", ecart)
    #         print("details", cbto)

    # Engines = [Explain.general_1_vs_k_MixedExplanation,Explain.general_k_vs_1_MixedExplanation, Explain.brut_force_general_1_vs_k_and_k_vs_1_MixedExplanation]
    #
    # criteriaFile = f'../CSVFILES/ijcai_criteria{n}.csv'
    # perfFile = f'../CSVFILES/ijcai_fullPerfTable{n}.csv'
    # Tn = Tn_for_OfflineSimulator(n)
    # mcda_problem_description = ProblemDescription(criteriaFileName=criteriaFile,
    #                                               performanceTableFileName=perfFile)
    #
    # for i in [89277]:
    #     dmFile = f'CoherentBooleanTermOrders6/model{i}.csv'
    #     cbto = regenerateCBTOfromModel(dmFile, n)
    #     print(cbto)
    #     cbto_copy = regenerateCBTOfromModel('89277.csv', n)
    #     print(cbto_copy)
    #     # CBTOrder = flat_CBTO_formated_for_OfflineSimulator(dmFile, n)
    #     # STn = [(min(pair, key=lambda x: CBTOrder.index(x)),
    #     #         max(pair, key=lambda x: CBTOrder.index(x))) for pair in Tn]
    #     #
    #     #
    #     #
    #     # CriticalPair = [(CBTOrder[j], CBTOrder[j+1]) for j in range(len(CBTOrder)-1) if (CBTOrder[j], CBTOrder[j+1]) in STn] # contigu et disjoints
    #     # print("*****************************************Model", i)
    #     # print(cbto)
    #     # print(len(CriticalPair), "critical pairs")
    #     # Dict_Non_PI = dict()
    #     # for info in [non_pi_elem for non_pi_elem in NonPI()]:
    #     #     Dict_Non_PI[(info.alternative1.id, info.alternative2.id)] = info
    #     #     Dict_Non_PI[(info.alternative2.id, info.alternative1.id)] = info
    #     #
    #     # dm = WS_DM(dmFile)
    #     # for a, b in CriticalPair:
    #     #     Dialog(Dict_Non_PI[(a, b)]).madeWith(dm)        # chargement du modèle
    #     #
    #     # N().update(mcda_problem_description, **PI().getRelation())
    #     # assert len(NonPI()) == 0
    #     #
    #     # # alt256 = mcda_problem_description[val([2,5,6], n)]
    #     # # alt134 = mcda_problem_description[val([1,3,4], n)]
    #     #
    #     # # alt1234 = mcda_problem_description[val([1,2,3,4], n)]
    #     # # alt56 = mcda_problem_description[val([5,6], n)]
    #     # #
    #     # alt126 = mcda_problem_description[val([1,2,6], n)]
    #     # alt345 = mcda_problem_description[val([3,4,5], n)]
    #     # for Engine in Engines:
    #     #     print(Engine)
    #     #     ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(alt126, alt345))
    #     #     if ok:
    #     #         print(text)
    #     #
    #     #     # ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(alt134, alt256))
    #     #     # if ok:
    #     #     #     print(text)
    #     # for a, b in STn:
    #     #     bin_a = str(bin(a))[2:]
    #     #     bin_b = str(bin(b))[2:]
    #     #     c_a = n - len(bin_a)
    #     #     c_b = n - len(bin_b)
    #     #     bin_a = '0'*c_a + bin_a
    #     #     bin_b = '0'*c_b + bin_b
    #     #
    #     #     i_ = 1
    #     #     bin_a_set = {i_ for i_ in range(1, n+1) if bin_a[i_-1] == '1'}
    #     #     bin_b_set = {i_ for i_ in range(1, n+1) if bin_b[i_-1] == '1'}
    #     #     if len(bin_a_set) == 4 and len(bin_b_set) == 2:
    #     #         print("============== 4 vs 2")
    #     #         for Engine in Engines:
    #     #             print(Engine)
    #     #             ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(mcda_problem_description[a], mcda_problem_description[b]))
    #     #             if ok:
    #     #                 print(text)
    #     #     if len(bin_a_set) == 2 and len(bin_b_set) == 4:
    #     #         print("============== 2 vs 4")
    #     #         for Engine in Engines:
    #     #             print(Engine)
    #     #             ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(mcda_problem_description[a], mcda_problem_description[b]))
    #     #             if ok:
    #     #                 print(text)
    #     #     if len(bin_a_set) == 3 and len(bin_b_set) == 3:
    #     #         print("============== 3 vs 3")
    #     #         for Engine in Engines:
    #     #             print(Engine)
    #     #             ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(mcda_problem_description[a], mcda_problem_description[b]))
    #     #             if ok:
    #     #                 print(text)
    #     # PI().clear()
    #     # N().clear()
