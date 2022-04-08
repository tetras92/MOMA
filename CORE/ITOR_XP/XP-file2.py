import numpy as np
import csv
import os
from CORE.PLNE_for_Delta11_decomposition import decompose as decompose_under_L0
from CORE.PLNE_for_Delta1m_decomposition import decompose as decompose_under_L1
from CORE.PLNE_for_Deltam1_decomposition import decompose as decompose_under_L2
from CORE.PLNE_for_Delta1m_m1_decomposition import decompose as decompose_under_L3

from datetime import datetime

m = 6
directory = f'/home/manuel239/PycharmProjects/MOMA/CORE/SIMULATION/KR-CBTO{m}'


def generate_n_integers(n):
    return list(*np.random.choice(range(1, 2 ** m - 1), size=(1, n), replace=False))


def integer_to_bin(val_int):
    return format(val_int, "b").zfill(m)


def generate_n_alternatives_as_subsets(n):
    while True:
        L = [integer_to_bin(x) for x in generate_n_integers(n)]
        chk1, _ = check1(L)
        chk2, _ = check2(L)
        if chk1 and chk2:
            break
    return [{chr(ord('a') + i) for i in range(m) if alt[i] == '1'} for alt in L]


def encode_preference_model_as_dict(filename):
    with open(filename) as preferenceModelFile:
        reader = csv.DictReader(preferenceModelFile)
        w_list = list()
        for row in reader:
            for criterion in reader.fieldnames:
                w_list.append(int(row[criterion]))
        w_list = sorted(w_list, reverse=True)
        return {chr(ord('a') + i): w_list[i] for i in range(m)}


def recommendation_algorithm(AlternativesSubsetsList, Wdict, decomposition_function=None):
    SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                           key=lambda alt: sum([Wdict[criterion] for criterion in alt]), reverse=True)
    S_ = [None]
    for v in range(1, len(SortedAlternativesSubsetsList)):
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
    for v in range(1, len(SortedAlternativesSubsetsList)):
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


def check1(A_binary_encoding_list):
    """significativite des m criteres"""
    for i in range(m):
        if all([alt[i] == '0' for alt in A_binary_encoding_list]) or all(
                [alt[i] == '1' for alt in A_binary_encoding_list]):
            return False, i

    return True, None


def check2(A_binary_encoding_list):
    """absence de dominance"""
    for alt1 in A_binary_encoding_list:
        for alt2 in A_binary_encoding_list:
            if alt2 != alt1:
                alt1_int = [int(alt1[i]) for i in range(m)]
                alt2_int = [int(alt2[i]) for i in range(m)]
                if all([alt1_int[i] >= alt2_int[i] for i in range(m)]) or all(
                        [alt2_int[i] >= alt1_int[i] for i in range(m)]):
                    return False, (alt1, alt2)
    return True, None


# Proportion = dict()
# nb_replications = 1000
# for n in range(2, 16):
#     Proportion[n] = 0
#     for _ in range(nb_replications):
#         A = [integer_to_bin(x) for x in generate_n_integers(n)]
#         if check1(A)[0]:
#             Proportion[n] += 1
#     Proportion[n] /= nb_replications
# print("significativite des criteres\n", Proportion)
#
# for n in range(2, 16):
#     Proportion[n] = 0
#     for _ in range(nb_replications):
#         A = [integer_to_bin(x) for x in generate_n_integers(n)]
#         if check2(A)[0]:
#             Proportion[n] += 1
#         # else:
#         #     print(check2(A))
#     Proportion[n] /= nb_replications

# print("Absence de dominance\n", Proportion)

# A = [integer_to_bin(x) for x in generate_n_integers(2)]
# print(A, check1(A))
# print(integer_to_bin(5))
# print(Proportion)
# print(generate_n_alternatives_as_subsets(5))
# print(encode_preference_model_as_dict(directory + '/model1.csv'))

if __name__ == "__main__":
    LanguagesSelected = [decompose_under_L0, decompose_under_L3]
    RESULT_H1 = {Language: 0 for Language in LanguagesSelected}
    RESULT_Hn = {Language: 0 for Language in LanguagesSelected}
    success_ratio = 0
    nb_replications = 30
    for repli in range(nb_replications):
        print("Date", repli, datetime.now())
        A = generate_n_alternatives_as_subsets(6)
        for file in os.listdir(directory):
            w_file = directory + '/' + file
            W = encode_preference_model_as_dict(w_file)
            for language in LanguagesSelected:
                success_h1, S_h1 = recommendation_algorithm(A, W, decomposition_function=language)
                if success_h1:
                    RESULT_H1[language] += 1

                success_hn, S_hn = recommendation_algorithm_any_tree_height(A, W, decomposition_function=language)
                if success_hn:
                    RESULT_Hn[language] += 1

        #- Affichage
        for language in LanguagesSelected:
            print("n°", repli, language.__name__, "H=1", 100. * RESULT_H1[language] / (repli + 1) / len(os.listdir(directory)), "%")
            print("n°", repli, language.__name__, "H=n", 100. * RESULT_Hn[language] / (repli + 1) / len(os.listdir(directory)), "%")

