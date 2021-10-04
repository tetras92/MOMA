import csv
from itertools import combinations

def allItems(n):
    V = [v for v in range(1, n+1)]
    ALL = list()
    for i in range(1, n+1):
        for elem in combinations(V, i):
            ALL.append(set(elem))
    return ALL

def Tn(n):
    ALL_items = allItems(n)
    return [elemt for elemt in combinations(ALL_items, 2) if len(elemt[0] | elemt[1]) == len(elemt[0]) + len(elemt[1])]

def superSet_and_subset_Dicts(n):
    ALL_items = allItems(n)
    size2ALL_items = [it for it in ALL_items if len(it) >= 2]
    # print(size2ALL_items)
    SuperSetDict = {val(it, n): {val(it, n)} for it in size2ALL_items}
    SubSetDict = {val(it, n): {val(it, n)} for it in size2ALL_items}
    for i in range(len(size2ALL_items)-1):
        for j in range(i+1, len(size2ALL_items)):
            # print(size2ALL_items[i], size2ALL_items[j])
            # if size2ALL_items[i] & size2ALL_items[j] == size2ALL_items[i]:
            if size2ALL_items[i] & size2ALL_items[j] == size2ALL_items[i]:
                SuperSetDict[val(size2ALL_items[j], n)].add(val(size2ALL_items[i], n))
                SubSetDict[val(size2ALL_items[i], n)].add(val(size2ALL_items[j], n))
            if size2ALL_items[j] & size2ALL_items[i] == size2ALL_items[j]:
                SuperSetDict[val(size2ALL_items[i], n)].add(val(size2ALL_items[j], n))
                SubSetDict[val(size2ALL_items[j], n)].add(val(size2ALL_items[i], n))
    return SuperSetDict, SubSetDict


def Tn_star(n):
    return [(A, B) for A, B in Tn(n) if len(A) >= 2 and len(B) >= 2]# and len(A) + len(B) == n]

def Un(n, letter=False):
    Tn_ = Tn(n)
    Un_ = list()
    for A, B in Tn_:
        LA = list(A)
        LA.sort()
        LB = list(B)
        LB.sort()
        if not injectionFromAToB(LA, LB) and not injectionFromAToB(LB, LA):
            Un_.append((A, B))
    print([("".join([str(a) for a in A]), "".join([str(b) for b in B])) for A, B in Un_])
    def SetRankOf(Couple):
        A, B = Couple
        A_, B_ = set(), set()
        AB_ = A|B
        m = len(A) + len(B)
        for v in sorted(AB_, reverse=True):
            if v in A:
                A_.add(m)
            else:
                B_.add(m)
            m -= 1
        return "".join([chr(ord('a') + (len(A) + len(B) - valueA)) for valueA in sorted(A_, reverse=True)]), "".join([chr(ord('a') + (len(A) + len(B) - valueB)) for valueB in sorted(B_, reverse=True)])

    if letter:
        # Un_ = [(SetRankOf(AB), AB) for AB in Un_]
        # print(Un_)
        Un_ = {("".join([str(a) for a in A]), "".join([str(b) for b in B])): SetRankOf((A,B)) for A, B in Un_}
        # Un_ = {("".join([str(a) for a in A]), "".join([str(b) for b in B])): [("".join([chr(ord('a') + (n - valueA)) for valueA in sorted(A, reverse=True)]), "".join([chr(ord('a') + (n - valueB)) for valueB in sorted(B, reverse=True)])), SetRankOf((A,B))] for A, B in Un_}
    return Un_

def Un_star_for_IJCAI(filename, n):
    L = regenerateCBTOfromModel(filename, n)
    Tn_ = Tn_star(n)
    Un_ = list()
    for A, B in Tn_:
        LA = list(A)
        LA.sort()
        LB = list(B)
        LB.sort()
        if not injectionFromAToB(LA, LB) and not injectionFromAToB(LB, LA):
            Un_.append((A, B))

    SUn = [(min(pair, key=lambda x: L.index(x)),
            max(pair, key=lambda x: L.index(x))) for pair in Un_]
    # SUn = sorted(SUn, key=lambda x: (len(x[0]), -len(x[1])))
    # print("SUn", SUn)
    SUn = [(val(A, n), val(B, n)) for A, B in SUn]
    return SUn

# def Un_star_for_IJCAI_N(filename, n):
#     L = regenerateCBTOfromModel(filename, n)
#     Tn_ = Tn_star(n)
#     # Tn_ = Tn(n)
#     Un_ = list()
#     for A, B in Tn_:
#         LA = list(A)
#         LA.sort()
#         LB = list(B)
#         LB.sort()
#         if not injectionFromAToB(LA, LB) and not injectionFromAToB(LB, LA):
#             Un_.append((A, B))
#
#     Un_ = Tn_
#     SUn = [(min(pair, key=lambda x: L.index(x)),
#             max(pair, key=lambda x: L.index(x))) for pair in Un_ if len(pair[0] | pair[1]) == n]
#     # SUn = sorted(SUn, key=lambda x: (len(x[0]), -len(x[1])))
#     # print("SUn", SUn)
#     SUn = [(val(A, n), val(B, n)) for A, B in SUn]
#     return SUn

def nCoveringPairs(filename, n):
    L = regenerateCBTOfromModel(filename, n)
    Tn_ = Tn(n)

    CPn = [(min(pair, key=lambda x: L.index(x)),
            max(pair, key=lambda x: L.index(x))) for pair in Tn_ if len(pair[0] | pair[1]) == n and len(pair[0]) >=2 and len(pair[1]) >= 2]

    CPnDict = dict()
    for A, B in CPn:
        dif = abs(len(A) - len(B))
        if dif not in CPnDict:
            CPnDict[dif] = list()
        CPnDict[dif].append((val(A, n), val(B, n)))

    return [(val(A, n), val(B, n)) for A, B in CPn], CPnDict

def difficultyDict(filename, n):
    L = regenerateCBTOfromModel(filename, n)

    STn = [(min(pair, key=lambda x: L.index(x)),
            max(pair, key=lambda x: L.index(x))) for pair in Tn(n)]

    DDict = {(val(A, n), val(B, n)): {(val(C, n), val(D, n)) for C, D in STn if (len(C) <= len(A) and len(D) < len(B)) or (len(C) < len(A) and len(D) <= len(B))}
             for A, B in STn}

    CorrespondanceDict = {val(A, n) : A for A in allItems(n)}
    return DDict, CorrespondanceDict

def injectionFromAToB(A_list, B_list):
    # A_list and B_list are sorted (ascending)

    if len(A_list) < len(B_list):
        return False
    if len(B_list) == 0:
        return True
    i = 0
    while i < len(A_list) and A_list[i] < B_list[0]:
        i += 1
    if i == len(A_list):
        return False
    return injectionFromAToB(A_list[i+1:], B_list[1:])


def Tn_for_OfflineSimulator(n):
    return [(val(A, n), val(B, n)) for A, B in Tn(n)]

def Tn_star_for_OfflineSimulator(n):
    return [(val(A, n), val(B, n)) for A, B in Tn(n) if len(A) >= 2 and len(B) >= 2]

def explanation1vsN_eligibleTn(n):
    return [elemt for elemt in Tn(n) if len(elemt[0]) >= 2 and len(elemt[1])] # BUG : changer de nom car pas d'ordre . ex pour n=4 (on peut avoir 123 > 4)

def infoToExplain_formated_for_OfflineSimulator(n):
    L = explanation1vsN_eligibleTn(n)
    return [(val(elmt[0], n), val(elmt[1], n)) for elmt in L]

def regenerateCBTOfromModel(filename, n):
    with open(filename) as utilityFile:
        reader = csv.DictReader(utilityFile)
        w_dict = dict()
        for row in reader:
            for criterion in reader.fieldnames:
                w_dict[int(criterion[3:])] = float(row[criterion])

        L = allItems(n)
        L.sort(key=lambda criteriaSet: sum([w_dict[criterion] for criterion in criteriaSet]), reverse=True)
        # print(sorted([sum([w_dict[criterion] for criterion in criteriaSet]) for criteriaSet in L], reverse=True))
        return L


def val(L, n):
        s = ''
        i = n
        while i >= 1:
            if i in L:
                s += '1'
            else:
                s += '0'
            i -= 1
        return int(s, 2)

def correspondingSet(n):
    # {("".join([str(a) for a in A]), "".join([str(b) for b in B])): SetRankOf((A,B)) for A, B in Un_}
    return {val(item, n) : item for item in allItems(n)}
    # return {val(item, n): "".join([str(a) for a in item]) for item in allItems(n)}

def CBTO_formated_for_OfflineSimulator(filename, n):
    R = list()
    L = regenerateCBTOfromModel(filename, n)
    for j in range(1, len(L)):
        R.append((val(L[j-1], n), val(L[j], n)))
    return R

def flat_CBTO_formated_for_OfflineSimulator(filename, n):
    R = list()
    L = regenerateCBTOfromModel(filename, n)
    for j in range(0, len(L)):
        R.append(val(L[j], n))
    return R


import os
if __name__ == "__main__":
    m = 5
    D = Un(m, False)
    # for c1, c2 in D.items():
    #     print(c1, c2)
    # print(len(nCoveringPairs(f'CBTO{m}/model1.csv', m)))
    # print(len(explanation1vsN_eligibleTn(4)), explanation1vsN_eligibleTn(4))
    # print(Tn_for_OfflineSimulator(4))
    # print(explanation1vsN_eligibleTn(4))
    # for model in os.listdir('KR-CBTO7'):
    # L = regenerateCBTOfromModel('model1.csv', 5)
    # print(difficultyDict('model1.csv', 5))
    # print(CBTO_formated_for_OfflineSimulator('CoherentBooleanTermOrders4/model1.csv', 4))
    # print(regenerateCBTOfromModel('CoherentBooleanTermOrders4/model2.csv', 4))
    # print("eligible ", len(explanation1vsN_eligibleTn(6)) + len(explanation1vsN_eligibleTn(5)) + len(explanation1vsN_eligibleTn(4)))

O=[{1, 2, 3, 4}, {2, 3, 4}, {1, 3, 4}, {1, 2, 4}, {1, 2, 3}, {3, 4}, {2, 4}, {2, 3}, {1, 4}, {1, 3}, {1, 2}, {4}, {3}, {2}, {1}]
O=[(15, 14), (14, 13), (13, 11), (11, 7), (7, 12), (12, 10), (10, 6), (6, 9), (9, 5), (5, 3), (3, 8), (8, 4), (4, 2), (2, 1)]
