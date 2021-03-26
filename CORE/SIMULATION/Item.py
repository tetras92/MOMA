import csv
from gurobipy import *
from CBTOprocessing import Tn
import random
from math import ceil

class Context():
    def __init__(self, n, KnownCoherentTermOrder=None):
        self.n = n
        self.model = Model("Context model")
        self.model.params.outputflag = 0
        self.varDict = {i: self.model.addVar(vtype=GRB.INTEGER, name="w_{}".format(i), lb=1) for i in range(1, n+1)}
        self.Constrs = list()
        # -- Singleton Order
        for i in range(2, n+1):
            self.Constrs.append(self.model.addConstr(self.varDict[i] >= self.varDict[i-1] + 1))
        # -

        #-- No item better than n//2 any other items (we will consider the set [1; n//2]
        # self.Constrs.append(self.model.addConstr(self.varDict[n] + 1 <= quicksum([self.varDict[j] for j in range(1, ceil(n/2) + 1)])))

        # # artificial for kr example
        # self.Constrs.append(self.model.addConstr(self.varDict[n] + 1 <= quicksum([self.varDict[j] for j in range(1, ceil(n/2))])))
        #
        # #-
        #
        # #--
        # self.model.addConstr(self.varDict[3] + self.varDict[4] + self.varDict[5] + 1 <= self.varDict[1] + self.varDict[2] + self.varDict[3] + self.varDict[4])
        # self.model.addConstr(self.varDict[1] + self.varDict[2] + self.varDict[3] + self.varDict[4] + 1 <= self.varDict[1] + self.varDict[2] + self.varDict[6])
        # self.model.addConstr(self.varDict[1] + self.varDict[2] + self.varDict[6] + 1 <= self.varDict[1] + self.varDict[2] + self.varDict[3] + self.varDict[5])
        # self.model.addConstr(self.varDict[1] + self.varDict[2] + self.varDict[3] + self.varDict[5] + 1 <= self.varDict[3] + self.varDict[4] + self.varDict[7])
        # self.model.addConstr(self.varDict[3] + self.varDict[4] + self.varDict[7] + 1 <= self.varDict[1] + self.varDict[2] + self.varDict[5] + self.varDict[6])
        # self.model.addConstr(self.varDict[7] + 1 <= self.varDict[1] + self.varDict[6])
        # self.model.addConstr(self.varDict[7] + 1 <= self.varDict[1] + self.varDict[2] + self.varDict[5])
        # self.model.addConstr(self.varDict[4] + self.varDict[7] + 1 <= self.varDict[1] + self.varDict[2] + self.varDict[6])
        # self.model.addConstr(self.varDict[3] + self.varDict[7] + 1 <=  self.varDict[5] + self.varDict[6])
        # # self.model.addConstr(self.varDict[4] + self.varDict[7] + 1 <= self.varDict[1] + self.varDict[3] + self.varDict[5])
        # self.model.addConstr(self.varDict[1] + self.varDict[5] + 1 <= self.varDict[7])
        # self.model.addConstr(self.varDict[7] + 1 <= self.varDict[3] + self.varDict[5])
        # self.model.addConstr(self.varDict[1] + self.varDict[7] + 1 <=  self.varDict[2] + self.varDict[6])
        #
        # #-

        self.model.update()
        if not KnownCoherentTermOrder is None:
            for i in range(1, len(KnownCoherentTermOrder)):
                info = KnownCoherentTermOrder[i-1], KnownCoherentTermOrder[i]
                self.addInfo(info)
        # else:
        #     def injectionFromAToB(A_list, B_list):
        #         # A_list and B_list are sorted (ascending)
        #
        #         if len(A_list) < len(B_list):
        #             return False
        #         if len(B_list) == 0:
        #             return True
        #         i = 0
        #         while i < len(A_list) and A_list[i] < B_list[0]:
        #             i += 1
        #         if i == len(A_list):
        #             return False
        #         return injectionFromAToB(A_list[i+1:], B_list[1:])
        #     # Dn et Un Computation
        #     self.Tn = Tn(n)
        #     self.Dn = list()
        #     self.Un = list()
        #     for A, B in self.Tn:
        #         LA = list(A)
        #         LA.sort()
        #         LB = list(B)
        #         LB.sort()
        #         if injectionFromAToB(LA, LB):
        #             self.Dn.append((B, A))       # A > B
        #         elif injectionFromAToB(LB, LA):
        #             self.Dn.append((A, B))       # A < B
        #         else:
        #             self.Un.append((A, B))       # same order as in Tn
        #
        #     # print("Dn", len(self.Dn))
        #     # print("Un", len(self.Un))
        #
        #     self.cutModel1 = Model("Cut model 1")
        #     self.cutModel1.params.outputflag = 0
        #     self.varDict1 = {i: self.cutModel1.addVar(vtype=GRB.INTEGER, name="w_{}".format(i), lb=0) for i in range(1, n+1)}
        #
        #     self.cutModel2 = Model("Cut model 2")
        #     self.cutModel2.params.outputflag = 0
        #     self.varDict2 = {i: self.cutModel2.addVar(vtype=GRB.INTEGER, name="w_{}".format(i), lb=0) for i in range(1, n+1)}


    def removeLastConstraint(self):
        # self.numberOfConstaints -= 1
        lastConstraint = self.Constrs[-1]
        self.model.remove(lastConstraint)
        self.model.update()

    def addInfo(self, info):
        A, B = info   # A < B
        # self.model.addConstr(quicksum([self.varDict[a] for a in A]) + 1 <= quicksum([self.varDict[b] for b in B]))  ERREUR !!!
        self.Constrs.append(self.model.addConstr(quicksum([self.varDict[a] for a in A]) + 1 <= quicksum([self.varDict[b] for b in B])))
        # self.numberOfConstaints += 1
        self.model.update()

    def isConsistent(self):
        self.model.optimize()
        return self.model.status == GRB.OPTIMAL

    def generate_weight_vector(self):
        self.model.setObjective(quicksum([var for var in self.varDict.values()]), GRB.MINIMIZE)
        self.model.optimize()
        self.weight_vector = {"var{}".format(i): self.varDict[i].x/self.model.objVal for i in range(1, self.n+1)}

    def generate_integer_weight_vector(self):
        self.model.setObjective(quicksum([var for var in self.varDict.values()]), GRB.MINIMIZE)
        self.model.optimize()
        self.weight_vector = {"var{}".format(i): int(self.varDict[i].x) for i in range(1, self.n+1)}

    def isCandidate(self, item, TermOrderList, RemainingItems):
        ToRemoveConstr = list()
        for i in range(1, len(TermOrderList)):
            A, B = TermOrderList[i-1], TermOrderList[i]
            ToRemoveConstr.append(self.model.addConstr(quicksum([self.varDict[a] for a in A]) + 1 <= quicksum([self.varDict[b] for b in B])))

        # self.model.update()
        i_ = 0
        while i_ < len(RemainingItems):
            remain_item = RemainingItems[i_]
            self.addInfo((item, remain_item))
            consistent = self.isConsistent()
            self.removeLastConstraint()
            if not consistent: break
            i_ += 1

        for constr_add in ToRemoveConstr:
            self.model.remove(constr_add)

        self.model.update()
        return i_ == len(RemainingItems)

    def cbto_completed(self, Cbto):
        ToRemoveConstr1 = [self.cutModel1.addConstr(quicksum([self.varDict1[a] for a in Cbto[i-1]]) + 1 <= quicksum([self.varDict1[b] for b in Cbto[i]])) for i in range(1, len(Cbto))]
        ToRemoveConstr2 = [self.cutModel2.addConstr(quicksum([self.varDict2[a] for a in Cbto[i-1]]) + 1 <= quicksum([self.varDict2[b] for b in Cbto[i]])) for i in range(1, len(Cbto))]

        completed = True
        random.shuffle(self.Un)
        for pair in self.Un:
            A, B = pair
            A_inf_B_constr = self.cutModel1.addConstr(quicksum([self.varDict1[a] for a in A]) + 1 <= quicksum([self.varDict1[b] for b in B]))
            B_inf_A_constr = self.cutModel2.addConstr(quicksum([self.varDict2[b] for b in B]) + 1 <= quicksum([self.varDict2[a] for a in A]))
            self.cutModel1.optimize()
            self.cutModel2.optimize()
            answer1 = self.cutModel1.status == GRB.OPTIMAL
            answer2 = self.cutModel2.status == GRB.OPTIMAL
            self.cutModel2.remove(B_inf_A_constr)
            self.cutModel1.remove(A_inf_B_constr)

            if answer1 and answer2:
                completed = False
                break

        for constr_add in ToRemoveConstr1:
            self.cutModel1.remove(constr_add)

        for constr_add in ToRemoveConstr2:
            self.cutModel2.remove(constr_add)

        self.cutModel1.update()
        self.cutModel2.update()

        return completed



def isCandidate(item, n, TermOrderList, RemainingItems):
    C = Context(n)
    for i in range(1, len(TermOrderList)):
        info = TermOrderList[i-1], TermOrderList[i]
        C.addInfo(info)

    for remain_item in RemainingItems:
        C.addInfo((item, remain_item))
        if not C.isConsistent():
            # print('incons')
            return False
        C.removeLastConstraint()
        # print("Constr", len(C.Constrs))
    return True



import itertools as iter

def allItems(n):
    V = [v for v in range(1, n+1)]
    ALL = list()
    for i in range(1, n+1):
        for elem in iter.combinations(V, i):
            ALL.append(set(elem))
    return ALL

# def recursive_generateCoherentBooleanTermsOrders(n, remainingItems, onGoingTermOrder, collector=list()):
#     # print(remainingItems)
#     if len(onGoingTermOrder) > ((1 << n) - 2)/2:
#         collector.append(onGoingTermOrder)
#         return
#
#     for candidate_item in [copy_item for copy_item in remainingItems]:
#         newRemainingItems = [item for item in remainingItems if item != candidate_item]
#         if isCandidate(candidate_item, n, onGoingTermOrder, newRemainingItems):
#             # print("candidate", candidate_item)
#             newOnGoingTermOrder = onGoingTermOrder + [candidate_item]
#             recursive_generateCoherentBooleanTermsOrders(n, newRemainingItems, newOnGoingTermOrder, collector)


def yield_generateCoherentBooleanTermsOrders(n):
    C = Context(n)
    Pile = [(list(), allItems(n))]
    while len(Pile) != 0:
        onGoingTermOrder, remainingItems = Pile.pop()
        if len(onGoingTermOrder) > ((1 << n) - 2)/2 :#or C.cbto_completed(onGoingTermOrder):
            # if not len(onGoingTermOrder) > ((1 << n) - 2)/2 :
            #     print("Coupé !!!")
            yield onGoingTermOrder
            continue
        for candidate_item in remainingItems:
            newRemainingItems = [item for item in remainingItems if item != candidate_item]
            if C.isCandidate(candidate_item, onGoingTermOrder, newRemainingItems):
            # if isCandidate(candidate_item, n, onGoingTermOrder, newRemainingItems):       #ancienne version trop lente (trop de model gurobi créés)
                Pile.append((onGoingTermOrder + [candidate_item], newRemainingItems))

def sampled_yield_generateCoherentBooleanTermsOrders(n, nb=10000):
    C = Context(n)
    All_items = allItems(n)
    All_items.remove({1})
    All_items.remove({2})
    Pile = [(list([{1}, {2}]), All_items)]

    while nb != 0:
        total = sum([len(elt) for elt in Pile])
        print("max", max([len(elt[0]) for elt in Pile]), "total", total, "Pilelen", len(Pile))
        print()
        i_r = np.random.choice(range(len(Pile)), p=[len(elt)/total for elt in Pile])
        # print(i_r)
        onGoingTermOrder, remainingItems = Pile.pop(i_r)
        if len(onGoingTermOrder) >= ((1 << n) - 2)/2 :#or C.cbto_completed(onGoingTermOrder):
            # if not len(onGoingTermOrder) > ((1 << n) - 2)/2 :
            #     print("Coupé !!!")
            nb -= 1
            yield onGoingTermOrder
            continue
        if len(Pile) < 100:
            for candidate_item in remainingItems:
                newRemainingItems = [item for item in remainingItems if item != candidate_item]
                if C.isCandidate(candidate_item, onGoingTermOrder, newRemainingItems):
                # if isCandidate(candidate_item, n, onGoingTermOrder, newRemainingItems):       #ancienne version trop lente (trop de model gurobi créés)
                    Pile.append((onGoingTermOrder + [candidate_item], newRemainingItems))

import time
import numpy as np
if __name__ == "__main__":
    Collector = list()
    n = 4
    i = 0
    debut = time.time()
    for to in yield_generateCoherentBooleanTermsOrders(n):
        i += 1
        to_Context = Context(n, KnownCoherentTermOrder=to)
        to_Context.generate_integer_weight_vector()

        # with open('SAMPLE-CBTO{}/model{}.csv'.format(n, i), 'w', newline='') as csvfile:
        with open('KR-CBTO{}/model{}.csv'.format(n, i), 'w', newline='') as csvfile:
        # with open('model{}.csv'.format(i), 'w', newline='') as csvfile:

            fieldnames = ['var{}'.format(j) for j in range(1, n+1)]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow(to_Context.weight_vector)

    print(i, "models avec n =", n, "durée", (time.time()-debut)/60)

# exhaustif
# 124187 models avec n = 6 durée 319.573734219869 minutes
# 516 models avec n = 5 durée 0.26444804668426514 minute
# 14 models avec n = 4 durée 0.002292199929555257 minute

# mcda : n < \sum ceil(n/2)
# 34606 models avec n = 6 durée 76.92 minutes
# 265 models avec n = 5 durée 0.112 minute
# 2 models avec n = 4 durée 0.00067 minute
