import numpy as np
import csv
import os
from CORE.PLNE_for_Delta11_decomposition import decompose as decompose_under_L0
from CORE.PLNE_for_Delta1m_decomposition import decompose as decompose_under_L1
from CORE.PLNE_for_Deltam1_decomposition import decompose as decompose_under_L2
from CORE.PLNE_for_Delta1m_m1_decomposition import decompose as decompose_under_L3
from CORE.ITOR_XP.deformationAlgorithm import recommendation_after_deformation_L0 as translationL0, \
    recommendation_after_deformation_L1 as translationL1
from CORE.ITOR_XP.deformationAlgorithm import recommendation_after_deformation_L2 as translationL2, \
    recommendation_after_deformation_L3 as translationL3

TRANSLATION_METHODS = [translationL0, translationL1, translationL2, translationL3]

from datetime import datetime

m = 20
A_dest_directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/ITOR_XP/m_{m}/A_directory_m{m}'
W_dest_directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/ITOR_XP/m_{m}/W_directory_m{m}'


def recommendation_algorithm(AlternativesSubsetsList, Wdict, decomposition_function=None):
    SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                           key=lambda alt: sum([Wdict[criterion] for criterion in alt]), reverse=True)
    S_ = [None]
    for v in range(1, len(SortedAlternativesSubsetsList)):  # GROS BUG 1 au lieu de 2
        proSet, conSet = SortedAlternativesSubsetsList[0] - SortedAlternativesSubsetsList[v], \
                         SortedAlternativesSubsetsList[v] - SortedAlternativesSubsetsList[0]
        success_v, Sv = decomposition_function(proSet, conSet, Wdict)
        if not success_v:
            return False, None
        else:
            S_.append(Sv)

    return True, S_


def recommendation_algorithm_any_tree_height(AlternativesSubsetsList, W_dict, decomposition_function=None):
    SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                           key=lambda alt: sum([W_dict[criterion] for criterion in alt]), reverse=True)
    SS = dict()
    for v in range(1, len(SortedAlternativesSubsetsList)):  # GROS BUG 1 au lieu de 2
        success_v = False
        for u in range(0, v):
            proSet, conSet = SortedAlternativesSubsetsList[u] - SortedAlternativesSubsetsList[v], \
                             SortedAlternativesSubsetsList[v] - SortedAlternativesSubsetsList[u]
            success_uv, Suv = decomposition_function(proSet, conSet, W_dict)
            if success_uv:
                success_v = True
                SS[(u, v)] = Suv
                break
        if not success_v:
            return False, None

    return True, SS


def recommendation_relaxation(AlternativesSubsetsList, Wdict, decomposition_function=None, kmax=2):
    SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                           key=lambda alt: sum([Wdict[criterion] for criterion in alt]), reverse=True)
    # print(SortedAlternativesSubsetsList)

    S = dict()
    k = 2
    while k <= kmax + 1:
        v = k
        while v <= len(SortedAlternativesSubsetsList):
            S[v] = dict()
            u = 1
            failure_uv = False
            while not failure_uv and u <= k - 1:
                proSet, conSet = SortedAlternativesSubsetsList[u - 1] - SortedAlternativesSubsetsList[v - 1], \
                                 SortedAlternativesSubsetsList[v - 1] - SortedAlternativesSubsetsList[u - 1]
                success_uv, Suv = decomposition_function(proSet, conSet, Wdict)
                # print(SortedAlternativesSubsetsList[u - 1], "vs", SortedAlternativesSubsetsList[v - 1], "res", Suv)
                if not success_uv:
                    failure_uv = True
                    break
                S[v][u] = Suv
                u += 1
            if failure_uv:
                k += 1
                break
            v += 1
        if v <= len(SortedAlternativesSubsetsList):
            del S[v]
            continue

        return True, S

    return False, None


def check_int_List_1(int_List):
    A_binary_encoding_list = [integer_to_bin(val_int) for val_int in int_List]
    """significativite des m criteres"""
    for i in range(m):
        if all([alt[i] == '0' for alt in A_binary_encoding_list]) or all(
                [alt[i] == '1' for alt in A_binary_encoding_list]):
            return False

    return True


def check_int_List_2(int_List):
    A_binary_encoding_list = [integer_to_bin(val_int) for val_int in int_List]
    """absence de dominance"""
    for alt1 in A_binary_encoding_list:
        for alt2 in A_binary_encoding_list:
            if alt2 != alt1:
                alt1_int = [int(alt1[i]) for i in range(m)]
                alt2_int = [int(alt2[i]) for i in range(m)]
                if all([alt1_int[i] >= alt2_int[i] for i in range(m)]) or all(
                        [alt2_int[i] >= alt1_int[i] for i in range(m)]):
                    return False
    return True


def integer_to_bin(val_int):
    return format(val_int, "b").zfill(m)


def load_set_of_alternatives_set(filename):
    Alternatives_set_list = list()
    with open(filename) as alt_file:
        n = int(alt_file.readline())
        line = alt_file.readline()
        while line != "":
            line = line[:len(line) - 1]  # supprimer '\n' de fin
            line_alt_int_List = [integer_to_bin(int(e)) for e in line.split(" ", maxsplit=n - 1)]
            line_alt_subset_List = [{chr(ord('a') + i) for i in range(m) if alt[i] == '1'} for alt in line_alt_int_List]
            Alternatives_set_list.append(line_alt_subset_List)
            line = alt_file.readline()

    return Alternatives_set_list


def load_set_of_score_functions(filename):
    Omega_list = list()
    with open(filename) as w_file:
        line = w_file.readline()
        while line != "":
            line = line[:len(line) - 1]  # supprimer '\n' de fin
            # print(line.split(' ', maxsplit=m-1))
            line_score_function = [float(e) for e in line.split(' ', maxsplit=m - 1)]
            score_function_dict = {chr(ord('a') + i): line_score_function[i] for i in range(m)}
            Omega_list.append(score_function_dict)
            line = w_file.readline()
        return Omega_list


if __name__ == "__main__":
    # create_a_set_of_n_alternatives(6, seed=239, size=500)
    # create_a_set_of_omega_score_function(seed=22)
    LANGUAGES = [decompose_under_L0, decompose_under_L1, decompose_under_L2, decompose_under_L3]
    assert len(LANGUAGES) == 4

    for A_list_file in os.listdir(A_dest_directory):
        for W_list_file in os.listdir(W_dest_directory):
            A_list = load_set_of_alternatives_set(A_dest_directory + '/' + A_list_file)
            W_list = load_set_of_score_functions(W_dest_directory + '/' + W_list_file)
            print("\n", A_list_file, "||", W_list_file)

            RESULT_RECO_ETOILE = {i: 0 for i in
                                  range(0, len(LANGUAGES) + 1)}  # + 1 POUR COMPTABILISER LE "OU EXCLUSIF" L1 - L2
            RESULT_RECO_TRANSITIVITY = {i: 0 for i in range(0, len(LANGUAGES) + 1)}
            RESULT_RECO_RELAXATION = {i: 0 for i in range(0, len(LANGUAGES) + 1)}
            RESULT_RECO_TRANSLATION = {i: 0 for i in range(0, len(LANGUAGES) + 1)}
            print("Date", datetime.now())
            number = 0
            for A in A_list:
                for W in W_list:
                    if number % 100000 == 0:
                        print(number, datetime.now())
                    number += 1
                    CPT_DICT = {i: False for i in range(0, len(LANGUAGES))}
                    for ilanguage in range(0, len(LANGUAGES)):
                        language = LANGUAGES[ilanguage]
                        # print("L"+str(ilanguage))
                        if ilanguage == 0:
                            success_h1, S_h1 = recommendation_algorithm(A, W, decomposition_function=language)
                            if success_h1:
                                CPT_DICT[0] = True
                                RESULT_RECO_ETOILE[0] += 1
                        elif ilanguage == 1 or ilanguage == 2:
                            if CPT_DICT[0]:
                                CPT_DICT[ilanguage] = True
                                RESULT_RECO_ETOILE[ilanguage] += 1
                            else:
                                success_h1, S_h1 = recommendation_algorithm(A, W, decomposition_function=language)
                                if success_h1:
                                    CPT_DICT[ilanguage] = True
                                    RESULT_RECO_ETOILE[ilanguage] += 1
                        elif ilanguage == 3:
                            if CPT_DICT[0] or CPT_DICT[1] or CPT_DICT[2]:
                                CPT_DICT[ilanguage] = True
                                RESULT_RECO_ETOILE[ilanguage] += 1
                                RESULT_RECO_ETOILE[4] += 1  # L0 L1 L2 OU EXCLUSIF
                            else:
                                success_h1, S_h1 = recommendation_algorithm(A, W, decomposition_function=language)
                                if success_h1:
                                    CPT_DICT[ilanguage] = True
                                    RESULT_RECO_ETOILE[ilanguage] += 1

                    # Transitivité : NE VAUT QUE POUR L3
                    if (CPT_DICT[0] or CPT_DICT[1] or CPT_DICT[
                        2]):  # Valable uniquement parce que ilanguage prend la valeur 1 avant de prendre la valeur 2:
                        RESULT_RECO_TRANSITIVITY[4] += 1
                    for ilanguage in range(0, len(LANGUAGES)):
                        language = LANGUAGES[ilanguage]
                        if CPT_DICT[ilanguage]:
                            RESULT_RECO_TRANSITIVITY[ilanguage] += 1
                        else:
                            if ilanguage == 3:  # NE VAUT QUE POUR L3
                                success_hN, S_hN = recommendation_algorithm_any_tree_height(A, W,
                                                                                            decomposition_function=language)
                                if success_hN:
                                    RESULT_RECO_TRANSITIVITY[3] += 1

                    # Relaxation 2-best
                    CPT_DICT_RELAXATION = {i: False for i in range(0, len(LANGUAGES))}

                    for ilanguage in range(0, len(LANGUAGES)):
                        language = LANGUAGES[ilanguage]

                        if ilanguage == 3 and (CPT_DICT_RELAXATION[0] or CPT_DICT_RELAXATION[1] or CPT_DICT_RELAXATION[
                            2]):  # Valable uniquement parce que ilanguage prend la valeur 1 avant de prendre la valeur 2:
                            RESULT_RECO_RELAXATION[4] += 1

                        if CPT_DICT[ilanguage]:  # SI 1-BEST OK
                            CPT_DICT_RELAXATION[ilanguage] = True  # a mon avis pas tres utile
                            RESULT_RECO_RELAXATION[ilanguage] += 1
                        else:
                            if ilanguage == 0:
                                success_relax, S_relax = recommendation_relaxation(A, W,
                                                                                   decomposition_function=language)
                                if success_relax:
                                    CPT_DICT_RELAXATION[0] = True
                                    RESULT_RECO_RELAXATION[0] += 1
                            elif ilanguage == 1 or ilanguage == 2:
                                if CPT_DICT_RELAXATION[0]:
                                    CPT_DICT_RELAXATION[ilanguage] = True
                                    RESULT_RECO_RELAXATION[ilanguage] += 1
                                else:
                                    success_relax, S_relax = recommendation_relaxation(A, W,
                                                                                       decomposition_function=language)
                                    if success_relax:
                                        CPT_DICT_RELAXATION[ilanguage] = True
                                        RESULT_RECO_RELAXATION[ilanguage] += 1
                            elif ilanguage == 3:
                                if CPT_DICT_RELAXATION[0] or CPT_DICT_RELAXATION[1] or CPT_DICT_RELAXATION[2]:
                                    CPT_DICT_RELAXATION[ilanguage] = True
                                    RESULT_RECO_RELAXATION[ilanguage] += 1
                                    # RESULT_RECO_RELAXATION[4] += 1  # L0 L1 L2 OU EXCLUSIF
                                else:
                                    success_relax, S_relax = recommendation_relaxation(A, W,
                                                                                       decomposition_function=language)
                                    if success_relax:
                                        CPT_DICT_RELAXATION[ilanguage] = True
                                        RESULT_RECO_RELAXATION[ilanguage] += 1

                    # Translation
                    CPT_DICT_TRANSLATION = {i: False for i in range(0, len(LANGUAGES))}
                    # if (CPT_DICT[0] or CPT_DICT[1] or CPT_DICT[
                    #     2]):  # Valable uniquement parce que ilanguage prend la valeur 1 avant de prendre la valeur 2:
                    #     RESULT_RECO_TRANSLATION[4] += 1

                    for ilanguage in range(0, len(LANGUAGES)):

                        if ilanguage == 3 and (
                                CPT_DICT_TRANSLATION[0] or CPT_DICT_TRANSLATION[1] or CPT_DICT_TRANSLATION[2]):  # Valable uniquement parce que ilanguage prend la valeur 1 avant de prendre la valeur 2:
                            RESULT_RECO_TRANSLATION[4] += 1

                        if CPT_DICT[ilanguage]:  # SI 1-BEST OK
                            CPT_DICT_TRANSLATION[ilanguage] = True
                            RESULT_RECO_TRANSLATION[ilanguage] += 1
                        else:
                            if ilanguage == 0:
                                success_translation, S_translation = TRANSLATION_METHODS[ilanguage](A, W)
                                if success_translation:
                                    CPT_DICT_TRANSLATION[0] = True
                                    RESULT_RECO_TRANSLATION[0] += 1
                            elif ilanguage == 1 or ilanguage == 2:
                                if CPT_DICT_TRANSLATION[0]:
                                    CPT_DICT_TRANSLATION[ilanguage] = True
                                    RESULT_RECO_TRANSLATION[ilanguage] += 1
                                else:
                                    success_translation, S_translation = TRANSLATION_METHODS[ilanguage](A, W)
                                    if success_translation:
                                        CPT_DICT_TRANSLATION[ilanguage] = True
                                        RESULT_RECO_TRANSLATION[ilanguage] += 1
                            elif ilanguage == 3:
                                if CPT_DICT_TRANSLATION[0] or CPT_DICT_TRANSLATION[1] or CPT_DICT_TRANSLATION[2]:
                                    CPT_DICT_TRANSLATION[ilanguage] = True
                                    RESULT_RECO_TRANSLATION[ilanguage] += 1
                                    # RESULT_RECO_TRANSLATION[4] += 1  # L0 L1 L2 OU EXCLUSIF
                                else:
                                    success_translation, S_translation = TRANSLATION_METHODS[ilanguage](A, W)
                                    if success_translation:
                                        CPT_DICT_TRANSLATION[ilanguage] = True
                                        RESULT_RECO_TRANSLATION[ilanguage] += 1

                                    assert False  # on n'entrera jamais ici théoriquement car CPT_DICT_TRANSLATION[1] "est" toujours True

            print("RECO-ETOILE",
                  [100. * RESULT_RECO_ETOILE[il] / len(A_list) / len(W_list) for il in range(0, len(LANGUAGES) + 1)],
                  "%")

            print("RECO-TRANSITIVITY", [100. * RESULT_RECO_TRANSITIVITY[il] / len(A_list) / len(W_list) for il in
                                        range(0, len(LANGUAGES) + 1)], "%")

            print("RECO-RELAXATION", [100. * RESULT_RECO_RELAXATION[il] / len(A_list) / len(W_list) for il in
                                      range(0, len(LANGUAGES) + 1)], "%")

            print("RECO-TRANSLATION", [100. * RESULT_RECO_TRANSLATION[il] / len(A_list) / len(W_list) for il in
                                       range(0, len(LANGUAGES) + 1)], "%")

    print("Date", datetime.now())
