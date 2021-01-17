import csv
from CORE.SIMULATION.Item import allItems
from itertools import combinations
def Tn(n):
    ALL_items = allItems(n)
    return [elemt for elemt in combinations(ALL_items, 2) if len(elemt[0] | elemt[1]) == len(elemt[0]) + len(elemt[1])]

def Tn_for_OfflineSimulator(n):
    return [(val(A, n), val(B, n)) for A, B in Tn(n)]

def explanation1vsN_eligibleTn(n):
    return [elemt for elemt in Tn(n) if len(elemt[0]) >= 2] # BUG : changer de nom car pas d'ordre . ex pour n=4 (on peut avoir 123 > 4)

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
if __name__ == "__main__":
    # print(Tn_for_OfflineSimulator(4))
    # print(explanation1vsN_eligibleTn(4))
    print(regenerateCBTOfromModel('CoherentBooleanTermOrders6/model1.csv', 6))
    # print(CBTO_formated_for_OfflineSimulator('CoherentBooleanTermOrders4/model1.csv', 4))
    # print(regenerateCBTOfromModel('CoherentBooleanTermOrders4/model2.csv', 4))
    # print("eligible ", len(explanation1vsN_eligibleTn(6)) + len(explanation1vsN_eligibleTn(5)) + len(explanation1vsN_eligibleTn(4)))

O=[{1, 2, 3, 4}, {2, 3, 4}, {1, 3, 4}, {1, 2, 4}, {1, 2, 3}, {3, 4}, {2, 4}, {2, 3}, {1, 4}, {1, 3}, {1, 2}, {4}, {3}, {2}, {1}]
O=[(15, 14), (14, 13), (13, 11), (11, 7), (7, 12), (12, 10), (10, 6), (6, 9), (9, 5), (5, 3), (3, 8), (8, 4), (4, 2), (2, 1)]
