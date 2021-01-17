# class Item():
#     def __init__(self, L):
#         L.sort()
#         self.tupled_item = tuple(L)
#
#     def __len__(self):
#         return len(self.tupled_item)
#
#     def __lt__(self, other):
#         if len(other) > len(self):
#             return False
#         elif len(self) > len(other):
#             return set(other.tupled_item) in set(self.tupled_item)
#         elif len(self) == 1:
#             return self.tupled_item[0] < other.tupled_item[0]

from gurobipy import *

class Context():
    def __init__(self, n, KnownCoherentTermOrder=None):
        self.n = n
        self.model = Model("Context model")
        self.model.params.outputflag = 0
        self.varDict = {i: self.model.addVar(vtype=GRB.INTEGER, name="w_{}".format(i)) for i in range(1, n+1)}
        self.Constrs = list()
        # -
        # self.numberOfConstaints = 0
        for i in range(2, n+1):
            self.Constrs.append(self.model.addConstr(self.varDict[i] >= self.varDict[i-1] + 1))
            # self.numberOfConstaints += 1
        # --
        self.model.update()
        if not KnownCoherentTermOrder is None:
            for i in range(1, len(KnownCoherentTermOrder)):
                info = KnownCoherentTermOrder[i-1], KnownCoherentTermOrder[i]
                self.addInfo(info)

    def removeLastConstraint(self):
        # self.numberOfConstaints -= 1
        lastConstraint = self.Constrs[-1]
        self.model.remove(lastConstraint)
        self.model.update()

    def addInfo(self, info):
        A, B = info   # A < B
        self.model.addConstr(quicksum([self.varDict[a] for a in A]) + 1 <= quicksum([self.varDict[b] for b in B]))
        # self.numberOfConstaints += 1
        self.model.update()

    def isConsistent(self):
        self.model.optimize()
        return self.model.status == GRB.OPTIMAL

    def generate_weight_vector(self):
        self.model.setObjective(quicksum([var for var in self.varDict.values()]), GRB.MINIMIZE)
        self.model.optimize()
        self.weight_vector = {"var{}".format(i): self.varDict[i].x/self.model.objVal for i in range(1, n+1)}


def isCandidate(item, n, TermOrderList, RemainingItems):
    C = Context(n)
    for i in range(1, len(TermOrderList)):
        info = TermOrderList[i-1], TermOrderList[i]
        C.addInfo(info)

    for remain_item in RemainingItems:
        C.addInfo((item, remain_item))
        if not C.isConsistent():
            return False
        C.removeLastConstraint()
    return True



import itertools as iter

def allItems(n):
    V = [v for v in range(1, n+1)]
    ALL = list()
    for i in range(1, n+1):
        for elem in iter.combinations(V, i):
            ALL.append(set(elem))
    return ALL

def generateCoherentBooleanTermsOrders(n, remainingItems, onGoingTermOrder, collector=list()):
    # print(remainingItems)
    if len(onGoingTermOrder) > ((1 << n) - 2)/2:
        collector.append(onGoingTermOrder)
        return

    for candidate_item in [copy_item for copy_item in remainingItems]:
        newRemainingItems = [item for item in remainingItems if item != candidate_item]
        if isCandidate(candidate_item, n, onGoingTermOrder, newRemainingItems):
            # print("candidate", candidate_item)
            newOnGoingTermOrder = onGoingTermOrder.copy() + [candidate_item]
            generateCoherentBooleanTermsOrders(n, newRemainingItems, newOnGoingTermOrder, collector)

# print(allItems(6))
# Collector = list()
# n = 4
# generateCoherentBooleanTermsOrders(n, allItems(n), list(), Collector)
# print(len(Collector))

# import csv
#
# for i in range(len(Collector)):
#     to = Collector[i]
#     # print(to)
#     to_Context = Context(n, KnownCoherentTermOrder=to)
#     to_Context.generate_weight_vector()
#     # with open('CoherentBooleanTermOrders{}/model{}.csv'.format(n, i+1), 'w', newline='') as csvfile:
#     with open('model{}.csv'.format(n, i+1), 'w', newline='') as csvfile:
#
#         fieldnames = ['var{}'.format(j) for j in range(1, n+1)]
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#
#         writer.writeheader()
#         writer.writerow(to_Context.weight_vector)
#     # print("====")

