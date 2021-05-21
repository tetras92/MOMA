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

def breakpoint(series):
    V = list()
    for i in range(1, len(series)):
        if series[i] != series[i-1]:
            V.append((series[i-1], i+1))
    return V


if __name__ == "__main__":
    n = 5

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

    # A_B_ordering_dict = dict()
    # A_B_xplained_dict = dict()
    RESULT2 = dict()
    RESULT = dict()
    CorrespondingSetDict = correspondingSet(n)
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

        # for pair in CPn:
        #     if pair not in A_B_ordering_dict:
        #         A_B_ordering_dict[pair] = 0
        #     if (pair[1], pair[0]) not in A_B_ordering_dict:
        #         A_B_ordering_dict[(pair[1], pair[0])] = 0
        #     A_B_ordering_dict[pair] += 1
        #
        # for pair in set(CPn) & set(SDn_star):
        #     if pair not in A_B_xplained_dict:
        #         A_B_xplained_dict[pair] = 0
        #     if (pair[1], pair[0]) not in A_B_xplained_dict:
        #         A_B_xplained_dict[(pair[1], pair[0])] = 0
        #     A_B_xplained_dict[pair] += 1

        Un_star_deductible_non_critical_Set = set(SUn_star) - set(CriticalPair)
        deductible_len = len(Un_star_deductible_non_critical_Set)

        # Pairs of Un_star deductible non explainable
        cumul = 0

        for a, b in Un_star_deductible_non_critical_Set:
            altD = mcda_problem_description[a]
            altd = mcda_problem_description[b]

            ok, text = Engine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(altD, altd))
            if not ok:
                cumul += 1

        # aziza = 0
        Un_star_critical = set(SUn_star) & set(CriticalPair)
        pi_dominance_relation_copy = PI().getRelation()["dominanceRelation"].copy()
        for crit in Un_star_critical:
            a, b = crit
            altD = mcda_problem_description[a]
            altd = mcda_problem_description[b]

            pi_dominance_relation_copy.remove((altD, altd))
            if NecessaryPreference.adjudicate(mcda_problem_description, pi_dominance_relation_copy, (altD, altd)):
                cumul += 1
                deductible_len += 1
                print(CorrespondingSetDict[crit[0]], CorrespondingSetDict[crit[1]])
                # aziza += 1
            pi_dominance_relation_copy.append((altD, altd))

        # print(dmFile, aziza)
        RESULT2[dmFile] = cumul, deductible_len
        RESULT[dmFile] = {'model' : dmFile, 'Unexpl' : cumul, 'total' : deductible_len, 'criticalLength': len(CriticalPair)}


    # with open(f'InteractionSimulation{n}.csv', 'w', newline='') as csvfile:
    #
    #         fieldnames = ['model', 'Unexpl', 'total', 'criticalLength']
    #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #         writer.writeheader()
    #         for row in RESULT.values():
    #             writer.writerow(row)
    print(RESULT2)
    print(sorted(RESULT2.keys(), key=lambda file : RESULT2[file][0]))
    SERIES = sorted([round(100*cumul/denominateur, 2) for cumul, denominateur in RESULT2.values()])
    # print(SERIES)
    # print(breakpoint(SERIES))
    print("Minimum", min(SERIES), "Median", SERIES[len(SERIES)//2], "Maximum", max(SERIES))

# n = 5
# {'model106.csv': (3, 8), 'model187.csv': (2, 7), 'model26.csv': (2, 7), 'model507.csv': (2, 6), 'model289.csv': (1, 7), 'model67.csv': (0, 8), 'model390.csv': (4, 8), 'model394.csv': (4, 8), 'model97.csv': (3, 8), 'model306.csv': (2, 7), 'model391.csv': (3, 7), 'model216.csv': (2, 6), 'model71.csv': (2, 7), 'model33.csv': (0, 9), 'model239.csv': (2, 9), 'model294.csv': (0, 8), 'model2.csv': (0, 10), 'model426.csv': (0, 8), 'model109.csv': (3, 8), 'model440.csv': (0, 8), 'model300.csv': (2, 8), 'model69.csv': (1, 9), 'model149.csv': (0, 8), 'model348.csv': (2, 6), 'model50.csv': (2, 7), 'model463.csv': (3, 7), 'model180.csv': (3, 8), 'model415.csv': (3, 7), 'model47.csv': (3, 9), 'model14.csv': (2, 8), 'model173.csv': (1, 9), 'model197.csv': (3, 7), 'model486.csv': (1, 5), 'model262.csv': (0, 9), 'model314.csv': (3, 8), 'model287.csv': (1, 7), 'model39.csv': (2, 8), 'model329.csv': (1, 9), 'model153.csv': (2, 7), 'model469.csv': (4, 8), 'model101.csv': (0, 9), 'model81.csv': (3, 8), 'model328.csv': (1, 9), 'model302.csv': (2, 7), 'model368.csv': (3, 8), 'model455.csv': (3, 7), 'model356.csv': (0, 9), 'model339.csv': (4, 8), 'model392.csv': (3, 7), 'model470.csv': (4, 8), 'model159.csv': (3, 8), 'model313.csv': (2, 7), 'model140.csv': (4, 8), 'model29.csv': (2, 8), 'model433.csv': (3, 8), 'model245.csv': (2, 8), 'model430.csv': (2, 8), 'model141.csv': (4, 8), 'model206.csv': (5, 8), 'model243.csv': (1, 7), 'model105.csv': (1, 9), 'model435.csv': (4, 9), 'model478.csv': (3, 7), 'model19.csv': (3, 8), 'model253.csv': (1, 7), 'model130.csv': (3, 7), 'model466.csv': (2, 6), 'model271.csv': (2, 8), 'model386.csv': (2, 7), 'model464.csv': (3, 7), 'model103.csv': (0, 8), 'model361.csv': (0, 8), 'model349.csv': (2, 6), 'model258.csv': (0, 9), 'model61.csv': (2, 8), 'model23.csv': (3, 8), 'model409.csv': (3, 7), 'model52.csv': (2, 7), 'model79.csv': (2, 7), 'model424.csv': (1, 9), 'model188.csv': (3, 8), 'model210.csv': (3, 7), 'model265.csv': (2, 9), 'model25.csv': (3, 8), 'model178.csv': (3, 8), 'model494.csv': (3, 7), 'model449.csv': (3, 8), 'model215.csv': (3, 7), 'model83.csv': (3, 7), 'model341.csv': (4, 8), 'model379.csv': (0, 8), 'model445.csv': (0, 8), 'model31.csv': (0, 10), 'model144.csv': (4, 8), 'model38.csv': (2, 8), 'model320.csv': (2, 7), 'model24.csv': (2, 7), 'model233.csv': (0, 9), 'model295.csv': (0, 8), 'model299.csv': (0, 8), 'model284.csv': (0, 6), 'model421.csv': (4, 8), 'model198.csv': (5, 8), 'model235.csv': (0, 9), 'model278.csv': (1, 7), 'model244.csv': (2, 8), 'model315.csv': (3, 8), 'model227.csv': (2, 6), 'model124.csv': (4, 8), 'model35.csv': (0, 9), 'model371.csv': (2, 7), 'model327.csv': (0, 8), 'model222.csv': (3, 7), 'model43.csv': (2, 8), 'model292.csv': (0, 9), 'model510.csv': (1, 5), 'model220.csv': (3, 7), 'model462.csv': (4, 8), 'model148.csv': (1, 9), 'model515.csv': (3, 7), 'model423.csv': (0, 9), 'model147.csv': (0, 9), 'model461.csv': (2, 6), 'model476.csv': (2, 6), 'model442.csv': (0, 8), 'model321.csv': (2, 7), 'model160.csv': (2, 7), 'model254.csv': (1, 7), 'model479.csv': (3, 7), 'model355.csv': (0, 9), 'model7.csv': (2, 8), 'model411.csv': (3, 7), 'model344.csv': (3, 7), 'model337.csv': (2, 7), 'model308.csv': (2, 7), 'model467.csv': (3, 7), 'model94.csv': (3, 7), 'model62.csv': (2, 8), 'model13.csv': (2, 8), 'model403.csv': (3, 7), 'model164.csv': (2, 7), 'model481.csv': (1, 5), 'model274.csv': (0, 6), 'model325.csv': (0, 9), 'model310.csv': (1, 6), 'model219.csv': (4, 8), 'model110.csv': (2, 7), 'model229.csv': (4, 8), 'model305.csv': (2, 7), 'model273.csv': (2, 8), 'model248.csv': (0, 6), 'model6.csv': (0, 9), 'model446.csv': (2, 8), 'model185.csv': (1, 6), 'model212.csv': (3, 7), 'model145.csv': (4, 8), 'model45.csv': (2, 8), 'model4.csv': (0, 9), 'model281.csv': (1, 7), 'model400.csv': (2, 6), 'model138.csv': (5, 8), 'model334.csv': (3, 8), 'model405.csv': (1, 5), 'model412.csv': (3, 7), 'model437.csv': (0, 9), 'model376.csv': (0, 9), 'model252.csv': (1, 7), 'model452.csv': (3, 7), 'model352.csv': (3, 7), 'model136.csv': (5, 8), 'model10.csv': (1, 7), 'model279.csv': (1, 7), 'model465.csv': (2, 6), 'model358.csv': (0, 8), 'model458.csv': (3, 7), 'model484.csv': (2, 6), 'model92.csv': (3, 7), 'model230.csv': (0, 10), 'model509.csv': (1, 5), 'model98.csv': (3, 8), 'model324.csv': (0, 9), 'model362.csv': (2, 8), 'model293.csv': (0, 9), 'model502.csv': (2, 6), 'model56.csv': (2, 7), 'model406.csv': (2, 6), 'model266.csv': (2, 8), 'model290.csv': (1, 7), 'model457.csv': (4, 8), 'model74.csv': (1, 6), 'model129.csv': (2, 6), 'model54.csv': (2, 7), 'model117.csv': (2, 6), 'model472.csv': (3, 7), 'model389.csv': (4, 8), 'model413.csv': (3, 7), 'model259.csv': (0, 9), 'model223.csv': (3, 7), 'model139.csv': (4, 7), 'model416.csv': (3, 7), 'model157.csv': (2, 7), 'model8.csv': (2, 8), 'model451.csv': (4, 8), 'model495.csv': (1, 5), 'model322.csv': (2, 7), 'model497.csv': (2, 6), 'model217.csv': (2, 6), 'model489.csv': (3, 7), 'model395.csv': (2, 6), 'model288.csv': (1, 7), 'model27.csv': (2, 8), 'model96.csv': (2, 6), 'model112.csv': (2, 7), 'model343.csv': (3, 7), 'model429.csv': (0, 8), 'model238.csv': (2, 9), 'model242.csv': (1, 7), 'model332.csv': (2, 7), 'model340.csv': (4, 8), 'model146.csv': (0, 9), 'model354.csv': (3, 7), 'model107.csv': (2, 7), 'model199.csv': (4, 7), 'model408.csv': (2, 6), 'model241.csv': (2, 8), 'model111.csv': (3, 8), 'model93.csv': (2, 6), 'model439.csv': (1, 9), 'model380.csv': (0, 8), 'model17.csv': (3, 9), 'model40.csv': (1, 7), 'model9.csv': (2, 8), 'model364.csv': (2, 8), 'model475.csv': (3, 7), 'model155.csv': (2, 7), 'model66.csv': (0, 9), 'model419.csv': (3, 7), 'model330.csv': (3, 9), 'model177.csv': (2, 7), 'model1.csv': (0, 10), 'model251.csv': (1, 7), 'model501.csv': (2, 6), 'model41.csv': (3, 9), 'model432.csv': (3, 8), 'model399.csv': (2, 6), 'model365.csv': (2, 8), 'model68.csv': (0, 8), 'model80.csv': (1, 6), 'model28.csv': (2, 8), 'model240.csv': (2, 8), 'model143.csv': (3, 7), 'model468.csv': (2, 6), 'model338.csv': (2, 7), 'model170.csv': (0, 9), 'model342.csv': (4, 8), 'model72.csv': (3, 8), 'model200.csv': (5, 8), 'model436.csv': (0, 9), 'model272.csv': (2, 8), 'model456.csv': (4, 8), 'model64.csv': (2, 8), 'model86.csv': (2, 6), 'model158.csv': (2, 7), 'model142.csv': (3, 7), 'model176.csv': (2, 7), 'model102.csv': (0, 9), 'model218.csv': (4, 8), 'model161.csv': (3, 8), 'model301.csv': (3, 9), 'model428.csv': (0, 8), 'model303.csv': (3, 8), 'model280.csv': (1, 7), 'model425.csv': (1, 9), 'model122.csv': (3, 7), 'model182.csv': (2, 7), 'model5.csv': (0, 9), 'model236.csv': (0, 9), 'model77.csv': (2, 7), 'model192.csv': (3, 8), 'model133.csv': (4, 7), 'model347.csv': (2, 6), 'model285.csv': (0, 6), 'model505.csv': (1, 5), 'model53.csv': (3, 8), 'model42.csv': (2, 8), 'model48.csv': (2, 8), 'model438.csv': (0, 8), 'model156.csv': (3, 8), 'model513.csv': (3, 7), 'model490.csv': (3, 7), 'model309.csv': (3, 8), 'model418.csv': (2, 6), 'model260.csv': (0, 9), 'model275.csv': (0, 6), 'model318.csv': (2, 7), 'model201.csv': (4, 7), 'model333.csv': (3, 8), 'model128.csv': (4, 8), 'model282.csv': (2, 8), 'model75.csv': (3, 8), 'model137.csv': (4, 7), 'model234.csv': (0, 9), 'model132.csv': (5, 8), 'model116.csv': (3, 7), 'model473.csv': (2, 6), 'model150.csv': (0, 8), 'model485.csv': (2, 6), 'model276.csv': (1, 7), 'model11.csv': (3, 9), 'model202.csv': (4, 7), 'model434.csv': (4, 9), 'model312.csv': (2, 7), 'model186.csv': (3, 8), 'model183.csv': (2, 7), 'model196.csv': (4, 8), 'model448.csv': (3, 8), 'model512.csv': (1, 5), 'model263.csv': (0, 9), 'model59.csv': (2, 8), 'model357.csv': (1, 9), 'model91.csv': (3, 7), 'model57.csv': (2, 8), 'model316.csv': (1, 6), 'model250.csv': (1, 7), 'model115.csv': (2, 7), 'model95.csv': (3, 7), 'model500.csv': (2, 6), 'model283.csv': (2, 8), 'model267.csv': (2, 8), 'model123.csv': (2, 6), 'model114.csv': (3, 8), 'model194.csv': (5, 9), 'model374.csv': (3, 8), 'model203.csv': (3, 6), 'model488.csv': (1, 5), 'model366.csv': (3, 8), 'model277.csv': (1, 7), 'model135.csv': (4, 7), 'model256.csv': (0, 10), 'model12.csv': (2, 8), 'model214.csv': (3, 7), 'model407.csv': (1, 5), 'model375.csv': (0, 9), 'model402.csv': (2, 6), 'model493.csv': (3, 7), 'model104.csv': (0, 8), 'model304.csv': (1, 6), 'model127.csv': (2, 6), 'model345.csv': (3, 7), 'model163.csv': (3, 8), 'model152.csv': (2, 7), 'model297.csv': (0, 8), 'model190.csv': (3, 8), 'model503.csv': (3, 7), 'model482.csv': (1, 5), 'model335.csv': (1, 6), 'model60.csv': (2, 8), 'model89.csv': (3, 7), 'model181.csv': (2, 7), 'model88.csv': (2, 6), 'model460.csv': (3, 7), 'model384.csv': (2, 8), 'model261.csv': (0, 9), 'model370.csv': (3, 8), 'model491.csv': (3, 7), 'model171.csv': (0, 9), 'model237.csv': (0, 9), 'model32.csv': (0, 10), 'model477.csv': (3, 7), 'model506.csv': (1, 5), 'model151.csv': (3, 8), 'model270.csv': (2, 8), 'model508.csv': (2, 6), 'model221.csv': (3, 7), 'model388.csv': (2, 7), 'model51.csv': (3, 8), 'model207.csv': (4, 7), 'model381.csv': (1, 9), 'model286.csv': (1, 7), 'model255.csv': (1, 7), 'model447.csv': (2, 8), 'model420.csv': (4, 8), 'model453.csv': (3, 7), 'model454.csv': (3, 7), 'model34.csv': (0, 9), 'model184.csv': (3, 8), 'model450.csv': (4, 8), 'model353.csv': (3, 7), 'model100.csv': (3, 8), 'model249.csv': (0, 6), 'model369.csv': (3, 8), 'model118.csv': (3, 7), 'model396.csv': (3, 7), 'model373.csv': (3, 8), 'model191.csv': (1, 6), 'model90.csv': (2, 6), 'model121.csv': (2, 6), 'model37.csv': (2, 8), 'model44.csv': (2, 8), 'model224.csv': (3, 7), 'model172.csv': (0, 8), 'model363.csv': (3, 9), 'model76.csv': (2, 7), 'model323.csv': (2, 7), 'model232.csv': (0, 9), 'model359.csv': (0, 8), 'model480.csv': (3, 7), 'model471.csv': (3, 7), 'model82.csv': (2, 7), 'model166.csv': (4, 8), 'model179.csv': (1, 6), 'model474.csv': (1, 5), 'model65.csv': (0, 9), 'model336.csv': (2, 7), 'model87.csv': (3, 7), 'model499.csv': (2, 6), 'model154.csv': (3, 8), 'model378.csv': (1, 9), 'model46.csv': (1, 7), 'model134.csv': (5, 8), 'model268.csv': (1, 7), 'model20.csv': (2, 7), 'model84.csv': (2, 6), 'model487.csv': (2, 6), 'model414.csv': (4, 8), 'model387.csv': (3, 8), 'model311.csv': (1, 6), 'model496.csv': (1, 5), 'model444.csv': (0, 8), 'model58.csv': (2, 8), 'model55.csv': (3, 8), 'model246.csv': (2, 8), 'model120.csv': (3, 7), 'model298.csv': (1, 9), 'model21.csv': (3, 8), 'model228.csv': (4, 8), 'model126.csv': (3, 7), 'model231.csv': (0, 10), 'model18.csv': (2, 8), 'model125.csv': (2, 6), 'model131.csv': (2, 6), 'model30.csv': (2, 8), 'model73.csv': (2, 7), 'model208.csv': (5, 8), 'model393.csv': (4, 8), 'model410.csv': (3, 7), 'model398.csv': (3, 7), 'model16.csv': (1, 7), 'model296.csv': (1, 9), 'model492.csv': (3, 7), 'model3.csv': (0, 9), 'model351.csv': (3, 7), 'model397.csv': (2, 6), 'model346.csv': (3, 7), 'model36.csv': (0, 9), 'model22.csv': (2, 7), 'model427.csv': (0, 8), 'model264.csv': (2, 9), 'model213.csv': (3, 7), 'model175.csv': (0, 8), 'model78.csv': (3, 8), 'model504.csv': (3, 7), 'model319.csv': (2, 7), 'model257.csv': (0, 10), 'model307.csv': (3, 8), 'model63.csv': (2, 8), 'model382.csv': (3, 9), 'model331.csv': (3, 8), 'model377.csv': (0, 8), 'model514.csv': (3, 7), 'model195.csv': (3, 7), 'model85.csv': (3, 7), 'model404.csv': (3, 7), 'model205.csv': (3, 6), 'model193.csv': (2, 7), 'model269.csv': (1, 7), 'model162.csv': (2, 7), 'model169.csv': (4, 9), 'model291.csv': (1, 7), 'model165.csv': (4, 8), 'model516.csv': (3, 7), 'model459.csv': (3, 7), 'model422.csv': (0, 9), 'model167.csv': (3, 7), 'model247.csv': (2, 8), 'model350.csv': (2, 6), 'model174.csv': (0, 8), 'model108.csv': (2, 7), 'model326.csv': (0, 8), 'model511.csv': (1, 5), 'model385.csv': (2, 7), 'model372.csv': (2, 7), 'model226.csv': (2, 6), 'model209.csv': (4, 7), 'model441.csv': (1, 9), 'model119.csv': (2, 6), 'model168.csv': (4, 9), 'model204.csv': (4, 7), 'model189.csv': (2, 7), 'model113.csv': (2, 7), 'model70.csv': (0, 8), 'model15.csv': (2, 8), 'model401.csv': (2, 6), 'model317.csv': (1, 6), 'model225.csv': (3, 7), 'model211.csv': (3, 7), 'model483.csv': (2, 6), 'model360.csv': (1, 9), 'model443.csv': (0, 8), 'model417.csv': (4, 8), 'model431.csv': (2, 8), 'model498.csv': (2, 6), 'model49.csv': (3, 8), 'model383.csv': (2, 8), 'model99.csv': (3, 8), 'model367.csv': (2, 7)}
# ['model67.csv', 'model33.csv', 'model294.csv', 'model2.csv', 'model426.csv', 'model440.csv', 'model149.csv', 'model262.csv', 'model101.csv', 'model356.csv', 'model103.csv', 'model361.csv', 'model258.csv', 'model379.csv', 'model445.csv', 'model31.csv', 'model233.csv', 'model295.csv', 'model299.csv', 'model284.csv', 'model235.csv', 'model35.csv', 'model327.csv', 'model292.csv', 'model423.csv', 'model147.csv', 'model442.csv', 'model355.csv', 'model274.csv', 'model325.csv', 'model248.csv', 'model6.csv', 'model4.csv', 'model437.csv', 'model376.csv', 'model358.csv', 'model230.csv', 'model324.csv', 'model293.csv', 'model259.csv', 'model429.csv', 'model146.csv', 'model380.csv', 'model66.csv', 'model1.csv', 'model68.csv', 'model170.csv', 'model436.csv', 'model102.csv', 'model428.csv', 'model5.csv', 'model236.csv', 'model285.csv', 'model438.csv', 'model260.csv', 'model275.csv', 'model234.csv', 'model150.csv', 'model263.csv', 'model256.csv', 'model375.csv', 'model104.csv', 'model297.csv', 'model261.csv', 'model171.csv', 'model237.csv', 'model32.csv', 'model34.csv', 'model249.csv', 'model172.csv', 'model232.csv', 'model359.csv', 'model65.csv', 'model444.csv', 'model231.csv', 'model3.csv', 'model36.csv', 'model427.csv', 'model175.csv', 'model257.csv', 'model377.csv', 'model422.csv', 'model174.csv', 'model326.csv', 'model70.csv', 'model443.csv', 'model289.csv', 'model69.csv', 'model173.csv', 'model486.csv', 'model287.csv', 'model329.csv', 'model328.csv', 'model243.csv', 'model105.csv', 'model253.csv', 'model424.csv', 'model278.csv', 'model510.csv', 'model148.csv', 'model254.csv', 'model481.csv', 'model310.csv', 'model185.csv', 'model281.csv', 'model405.csv', 'model252.csv', 'model10.csv', 'model279.csv', 'model509.csv', 'model290.csv', 'model74.csv', 'model495.csv', 'model288.csv', 'model242.csv', 'model439.csv', 'model40.csv', 'model251.csv', 'model80.csv', 'model280.csv', 'model425.csv', 'model505.csv', 'model276.csv', 'model512.csv', 'model357.csv', 'model316.csv', 'model250.csv', 'model488.csv', 'model277.csv', 'model407.csv', 'model304.csv', 'model482.csv', 'model335.csv', 'model506.csv', 'model381.csv', 'model286.csv', 'model255.csv', 'model191.csv', 'model179.csv', 'model474.csv', 'model378.csv', 'model46.csv', 'model268.csv', 'model311.csv', 'model496.csv', 'model298.csv', 'model16.csv', 'model296.csv', 'model269.csv', 'model291.csv', 'model511.csv', 'model441.csv', 'model317.csv', 'model360.csv', 'model187.csv', 'model26.csv', 'model507.csv', 'model306.csv', 'model216.csv', 'model71.csv', 'model239.csv', 'model300.csv', 'model348.csv', 'model50.csv', 'model14.csv', 'model39.csv', 'model153.csv', 'model302.csv', 'model313.csv', 'model29.csv', 'model245.csv', 'model430.csv', 'model466.csv', 'model271.csv', 'model386.csv', 'model349.csv', 'model61.csv', 'model52.csv', 'model79.csv', 'model265.csv', 'model38.csv', 'model320.csv', 'model24.csv', 'model244.csv', 'model227.csv', 'model371.csv', 'model43.csv', 'model461.csv', 'model476.csv', 'model321.csv', 'model160.csv', 'model7.csv', 'model337.csv', 'model308.csv', 'model62.csv', 'model13.csv', 'model164.csv', 'model110.csv', 'model305.csv', 'model273.csv', 'model446.csv', 'model45.csv', 'model400.csv', 'model465.csv', 'model484.csv', 'model362.csv', 'model502.csv', 'model56.csv', 'model406.csv', 'model266.csv', 'model129.csv', 'model54.csv', 'model117.csv', 'model157.csv', 'model8.csv', 'model322.csv', 'model497.csv', 'model217.csv', 'model395.csv', 'model27.csv', 'model96.csv', 'model112.csv', 'model238.csv', 'model332.csv', 'model107.csv', 'model408.csv', 'model241.csv', 'model93.csv', 'model9.csv', 'model364.csv', 'model155.csv', 'model177.csv', 'model501.csv', 'model399.csv', 'model365.csv', 'model28.csv', 'model240.csv', 'model468.csv', 'model338.csv', 'model272.csv', 'model64.csv', 'model86.csv', 'model158.csv', 'model176.csv', 'model182.csv', 'model77.csv', 'model347.csv', 'model42.csv', 'model48.csv', 'model418.csv', 'model318.csv', 'model282.csv', 'model473.csv', 'model485.csv', 'model312.csv', 'model183.csv', 'model59.csv', 'model57.csv', 'model115.csv', 'model500.csv', 'model283.csv', 'model267.csv', 'model123.csv', 'model12.csv', 'model402.csv', 'model127.csv', 'model152.csv', 'model60.csv', 'model181.csv', 'model88.csv', 'model384.csv', 'model270.csv', 'model508.csv', 'model388.csv', 'model447.csv', 'model90.csv', 'model121.csv', 'model37.csv', 'model44.csv', 'model76.csv', 'model323.csv', 'model82.csv', 'model336.csv', 'model499.csv', 'model20.csv', 'model84.csv', 'model487.csv', 'model58.csv', 'model246.csv', 'model18.csv', 'model125.csv', 'model131.csv', 'model30.csv', 'model73.csv', 'model397.csv', 'model22.csv', 'model264.csv', 'model319.csv', 'model63.csv', 'model193.csv', 'model162.csv', 'model247.csv', 'model350.csv', 'model108.csv', 'model385.csv', 'model372.csv', 'model226.csv', 'model119.csv', 'model189.csv', 'model113.csv', 'model15.csv', 'model401.csv', 'model483.csv', 'model431.csv', 'model498.csv', 'model383.csv', 'model367.csv', 'model106.csv', 'model97.csv', 'model391.csv', 'model109.csv', 'model463.csv', 'model180.csv', 'model415.csv', 'model47.csv', 'model197.csv', 'model314.csv', 'model81.csv', 'model368.csv', 'model455.csv', 'model392.csv', 'model159.csv', 'model433.csv', 'model478.csv', 'model19.csv', 'model130.csv', 'model464.csv', 'model23.csv', 'model409.csv', 'model188.csv', 'model210.csv', 'model25.csv', 'model178.csv', 'model494.csv', 'model449.csv', 'model215.csv', 'model83.csv', 'model315.csv', 'model222.csv', 'model220.csv', 'model515.csv', 'model479.csv', 'model411.csv', 'model344.csv', 'model467.csv', 'model94.csv', 'model403.csv', 'model212.csv', 'model334.csv', 'model412.csv', 'model452.csv', 'model352.csv', 'model458.csv', 'model92.csv', 'model98.csv', 'model472.csv', 'model413.csv', 'model223.csv', 'model416.csv', 'model489.csv', 'model343.csv', 'model354.csv', 'model111.csv', 'model17.csv', 'model475.csv', 'model419.csv', 'model330.csv', 'model41.csv', 'model432.csv', 'model143.csv', 'model72.csv', 'model142.csv', 'model161.csv', 'model301.csv', 'model303.csv', 'model122.csv', 'model192.csv', 'model53.csv', 'model156.csv', 'model513.csv', 'model490.csv', 'model309.csv', 'model333.csv', 'model75.csv', 'model116.csv', 'model11.csv', 'model186.csv', 'model448.csv', 'model91.csv', 'model95.csv', 'model114.csv', 'model374.csv', 'model203.csv', 'model366.csv', 'model214.csv', 'model493.csv', 'model345.csv', 'model163.csv', 'model190.csv', 'model503.csv', 'model89.csv', 'model460.csv', 'model370.csv', 'model491.csv', 'model477.csv', 'model151.csv', 'model221.csv', 'model51.csv', 'model453.csv', 'model454.csv', 'model184.csv', 'model353.csv', 'model100.csv', 'model369.csv', 'model118.csv', 'model396.csv', 'model373.csv', 'model224.csv', 'model363.csv', 'model480.csv', 'model471.csv', 'model87.csv', 'model154.csv', 'model387.csv', 'model55.csv', 'model120.csv', 'model21.csv', 'model126.csv', 'model410.csv', 'model398.csv', 'model492.csv', 'model351.csv', 'model346.csv', 'model213.csv', 'model78.csv', 'model504.csv', 'model307.csv', 'model382.csv', 'model331.csv', 'model514.csv', 'model195.csv', 'model85.csv', 'model404.csv', 'model205.csv', 'model516.csv', 'model459.csv', 'model167.csv', 'model225.csv', 'model211.csv', 'model49.csv', 'model99.csv', 'model390.csv', 'model394.csv', 'model469.csv', 'model339.csv', 'model470.csv', 'model140.csv', 'model141.csv', 'model435.csv', 'model341.csv', 'model144.csv', 'model421.csv', 'model124.csv', 'model462.csv', 'model219.csv', 'model229.csv', 'model145.csv', 'model457.csv', 'model389.csv', 'model139.csv', 'model451.csv', 'model340.csv', 'model199.csv', 'model342.csv', 'model456.csv', 'model218.csv', 'model133.csv', 'model201.csv', 'model128.csv', 'model137.csv', 'model202.csv', 'model434.csv', 'model196.csv', 'model135.csv', 'model207.csv', 'model420.csv', 'model450.csv', 'model166.csv', 'model414.csv', 'model228.csv', 'model393.csv', 'model169.csv', 'model165.csv', 'model209.csv', 'model168.csv', 'model204.csv', 'model417.csv', 'model206.csv', 'model198.csv', 'model138.csv', 'model136.csv', 'model200.csv', 'model132.csv', 'model194.csv', 'model134.csv', 'model208.csv']
# Minimum 0.0 Median 28.57 Maximum 62.5
