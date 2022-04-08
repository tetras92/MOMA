import numpy as np
import csv
import os
from CORE.PLNE_for_Delta11_decomposition import decompose as decompose_under_L0
from CORE.PLNE_for_Delta1m_decomposition import decompose as decompose_under_L1
from CORE.PLNE_for_Deltam1_decomposition import decompose as decompose_under_L2
from CORE.PLNE_for_Delta1m_m1_decomposition import decompose as decompose_under_L3
from CORE.ITOR_XP.deformationAlgorithm import recommendation_after_deformation_L0 as translationL0, recommendation_after_deformation_L1 as translationL1
from CORE.ITOR_XP.deformationAlgorithm import recommendation_after_deformation_L2 as translationL2, recommendation_after_deformation_L3 as translationL3

TRANSLATION_METHODS = [translationL0, translationL1, translationL2, translationL3]

from datetime import datetime

m = 8
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
    # LANGUAGES = [decompose_under_L0, decompose_under_L1, decompose_under_L2, decompose_under_L3]
    LANGUAGES = [decompose_under_L3]
    for A_list_file in os.listdir(A_dest_directory):
        for W_list_file in os.listdir(W_dest_directory):
            A_list = load_set_of_alternatives_set(A_dest_directory + '/' + A_list_file)
            W_list = load_set_of_score_functions(W_dest_directory + '/' + W_list_file)
            print(A_list_file, "||", W_list_file)
            for ilanguage in range(0, len(LANGUAGES)):
                language = LANGUAGES[ilanguage]
                print("Date", datetime.now())
                print("L"+str(ilanguage))
                result = 0
                result_transitivity = 0
                result_relaxation = 0
                result_translation = 0
                result_transitivity_relaxation_translation = 0
                for A in A_list:
                    for W in W_list:
                        success_h1, S_h1 = recommendation_algorithm(A, W, decomposition_function=language)
                        if success_h1:
                            result += 1
                            result_relaxation += 1
                            result_transitivity += 1
                            result_translation += 1
                            result_transitivity_relaxation_translation += 1
                        else:
                            success_hN = False
                            if ilanguage == 3:
                                success_hN, S_hN = recommendation_algorithm_any_tree_height(A, W, decomposition_function=language)
                                if success_hN:
                                    result_transitivity += 1

                            success_relax, S_relax = recommendation_relaxation(A, W, decomposition_function=language)
                            if success_relax:
                                result_relaxation += 1

                            success_translation, S_translation = TRANSLATION_METHODS[ilanguage](A, W)
                            if success_translation:
                                result_translation += 1

                            if success_relax or success_hN or success_translation:
                                result_transitivity_relaxation_translation += 1
                print("Date", datetime.now())
                print("simple reco", 100. * result / len(A_list) / len(W_list), "%")
                print("transitivity", 100. * result_transitivity / len(A_list) / len(W_list), "%")
                print("relaxation", 100. * result_relaxation / len(A_list) / len(W_list), "%")
                print("translation", 100. * result_translation / len(A_list) / len(W_list), "%")
                print("gain:transitivity-relaxation-translation", 100. * result_transitivity_relaxation_translation / len(A_list) / len(W_list), "%")

    print("Date", datetime.now())
    # A_List = load_set_of_alternatives_set(A_dest_directory + '/' + 'A_n6_seed239_size500.a')
    # W_list = load_set_of_score_functions(W_dest_directory + '/' + 'W_seed23_size1000.sf')
    # result = 0
    # num_A_examined = 0
    # for A in A_List:
    #     num_A_examined += 1
    #     print("Date", datetime.now())
    #     for W in W_list:
    #         success_h1, S_h1 = recommendation_algorithm(A, W, decomposition_function=decompose_under_L2)
    #         if success_h1:
    #             result += 1
    #     print("n°", num_A_examined, 100. * result / num_A_examined / len(W_list), "%")
    #
    # print("Date", datetime.now(), 100. * result / len(A_List) / len(W_list), "%")
