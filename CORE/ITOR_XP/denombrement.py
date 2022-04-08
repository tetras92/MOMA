import itertools as it
import numpy as np

m = 6


def check1(A_binary_encoding_list):
    """significativite des m criteres"""
    for i in range(6):
        if all([alt[i] == '0' for alt in A_binary_encoding_list]) or all(
                [alt[i] == '1' for alt in A_binary_encoding_list]):
            return False, i

    return True, None


def check2(A_binary_encoding_list):
    """absence de dominance"""
    for k1 in range(len(A_binary_encoding_list) - 1):
        alt1 = A_binary_encoding_list[k1]
        alt1_int = [int(alt1[i]) for i in range(m)]
        for k2 in range(k1 + 1, len(A_binary_encoding_list)):
            alt2 = A_binary_encoding_list[k2]
            alt2_int = [int(alt2[i]) for i in range(m)]
            if all([alt1_int[i] >= alt2_int[i] for i in range(m)]) or all(
                    [alt2_int[i] >= alt1_int[i] for i in range(m)]):
                return False, (alt1, alt2)
    return True, None


def check3(A_binary_encoding_list):
    """Tous disjoints"""
    for k1 in range(len(A_binary_encoding_list) - 1):
        alt1 = A_binary_encoding_list[k1]
        alt1_int = [int(alt1[i]) for i in range(m)]
        for k2 in range(k1 + 1, len(A_binary_encoding_list)):
            alt2 = A_binary_encoding_list[k2]
            alt2_int = [int(alt2[i]) for i in range(m)]
            if any([alt1_int[i] == alt2_int[i] == 1 for i in range(m)]):
                return False, (alt1, alt2)
    return True, None


def generate_n_integers(n):
    return list(*np.random.choice(range(1, 2 ** 6 - 1), size=(1, n), replace=False))


def integer_to_bin(val_int):
    return format(val_int, "b").zfill(6)


def generate_n_alternatives_as_subsets(n):
    while True:
        L = [integer_to_bin(x) for x in generate_n_integers(n)]
        chk1, _ = check1(L)
        chk2, _ = check2(L)
        if chk1 and chk2:
            break
    return [{chr(ord('a') + i) for i in range(6) if alt[i] == '1'} for alt in L]


nb = 0
for triplet in it.combinations(set(range(1, 63)), 5):
    L = [integer_to_bin(x) for x in triplet]
    chk1, _ = check1(L)
    chk2, _ = check2(L)
    chk3, _ = check3(L)
    if chk1 and chk2 and chk3:
        nb += 1

print(nb)
