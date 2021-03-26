from gurobipy import *
from CBTOprocessing import Tn
import csv
import numpy as np
from itertools import combinations

class Noyau():
    def __init__(self, n, Model_Pairs=None):
        self.n = n
        self.model = Model("Noyau model")
        self.model.params.outputflag = 0
        self.varDict = {i: self.model.addVar(vtype=GRB.INTEGER, name="w_{}".format(i), lb=0) for i in range(1, n+1)}
        self.Constrs = list()
        self.Hypothesis = list()
        # -- Singleton Order
        for i in range(2, n+1):
            self.Constrs.append(self.model.addConstr(self.varDict[i] >= self.varDict[i-1] + 1))
            self.Hypothesis.append(({i-1}, {i}))
        # --

        #-- No item better than n//2 any other items (we will consider the set [1; n//2]
        # self.Constrs.append(self.model.addConstr(self.varDict[n] + 1 <= quicksum([self.varDict[j] for j in range(1, ceil(n/2) + 1)])))

        #--
        self.model.update()

        # Dn et Un Computation
        self.Tn = Tn(n)
        self.Dn = list()
        self.Un = list()


        if not Model_Pairs is None:
            for A, B in Model_Pairs:
                self.model.addConstr(quicksum([self.varDict[a] for a in A]) + 1 <= quicksum([self.varDict[b] for b in B]))

        else:
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

            for A, B in self.Tn:
                LA = list(A)
                LA.sort()
                LB = list(B)
                LB.sort()
                if injectionFromAToB(LA, LB):
                    self.Dn.append((B, A))       # A > B
                elif injectionFromAToB(LB, LA):
                    self.Dn.append((A, B))       # A < B
                else:
                    self.Un.append((A, B))       # same order as in Tn

            print("Dn", len(self.Dn))
            print("Un", len(self.Un))

    def is_droppable_given_Un(self, pair, selected_Un):
        ConstrAdded = [self.model.addConstr(quicksum([self.varDict[a] for a in A]) + 1 <= quicksum([self.varDict[b] for b in B])) for A, B in selected_Un]

        A, B = pair
        A_inf_B_constr = self.model.addConstr(quicksum([self.varDict[a] for a in A]) + 1 <= quicksum([self.varDict[b] for b in B]))
        self.model.update()
        if not self.isConsistent():
            return True
        self.model.remove(A_inf_B_constr)
        self.model.update()

        B_inf_A_constr = self.model.addConstr(quicksum([self.varDict[b] for b in B]) + 1 <= quicksum([self.varDict[a] for a in A]))
        self.model.update()
        if not self.isConsistent():
            return True
        self.model.remove(B_inf_A_constr)
        self.model.update()
        for constr_add in ConstrAdded:
            self.model.remove(constr_add)
        self.model.update()
        return False


    def isConsistent(self):
        self.model.optimize()
        return self.model.status == GRB.OPTIMAL

    def generate_weight_vector(self):
        self.model.setObjective(quicksum([var for var in self.varDict.values()]), GRB.MINIMIZE)
        self.model.optimize()
        self.weight_vector = {"var{}".format(i): self.varDict[i].x/self.model.objVal for i in range(1, self.n+1)}


    @staticmethod
    def random_integer_CBTO(n, size=10000):

        while size != 0:
            choices = list(np.random.choice(range(1, 10000), size=n, replace=False))
            ALL = list()
            for i in range(1, n+1):
                for elem in combinations(choices, i):
                    ALL.append(sum(elem))
            # ALL.sort()
            len_before = len(ALL)
            ALL = set(ALL)
            len_after = len(ALL)
            if len_before == len_after:
                size -=1
                choices.sort()
                yield choices
            else:
                print("echec")


def yield_generateCBTO_withNoyau(n):
    noyau = Noyau(n)
    # random.shuffle(noyau.Un)

    Pile = [(list(), noyau.Un[:])]             # Un_selected, Un_non_selected
    while len(Pile) != 0:
        Un_selected, Un_non_selected = Pile.pop()
        # maj Un_non_selected
        for pair in Un_non_selected[:]:
            if noyau.is_droppable_given_Un(pair, Un_selected):
                Un_non_selected.remove(pair)
        #-
        print("Un non selected len", len(Un_non_selected))
        if len(Un_non_selected) == 0:
            yield Un_selected
            continue


        non_ordered_pair = Un_non_selected.pop()
        A, B = non_ordered_pair
        Pile.append((Un_selected + [(A, B)], Un_non_selected[:]))
        Pile.append((Un_selected + [(B, A)], Un_non_selected[:]))



import time
if __name__ == "__main__":
    n = 8
    i = 0
    debut = time.time()
    for to_number in Noyau.random_integer_CBTO(n):
        i += 1
        with open('SAMPLE-CBTO{}/model{}.csv'.format(n, i), 'w', newline='') as csvfile:

            fieldnames = ['var{}'.format(j) for j in range(1, n+1)]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow({f'var{i}': to_number[i-1] for i in range(1, n+1)})
    print(i, "models avec n =", n, "durée", (time.time()-debut)/60)


    # for to in yield_generateCBTO_withNoyau(n):
    #     i += 1
    #     to_Context = Noyau(n, Model_Pairs=to)
    #     to_Context.generate_weight_vector()
    #     # with open('CBTO{}/model{}.csv'.format(n, i), 'w', newline='') as csvfile:
    #     with open('model{}.csv'.format(i), 'w', newline='') as csvfile:
    #
    #         fieldnames = ['var{}'.format(j) for j in range(1, n+1)]
    #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #
    #         writer.writeheader()
    #         writer.writerow(to_Context.weight_vector)
    #
    # print(i, " cbto noyau avec n =", n)

# def isCandidate(self, item, TermOrderList, RemainingItems):
#         C = Context(self.n)
#         ToRemoveConstr = list()
#         for i in range(1, len(TermOrderList)):
#             A, B = TermOrderList[i-1], TermOrderList[i]
#             ToRemoveConstr.append(self.model.addConstr(quicksum([self.varDict[a] for a in A]) + 1 <= quicksum([self.varDict[b] for b in B])))
#
#         i = 0
#         consistent = True
#         while consistent and i < len(RemainingItems):
#             remain_item = RemainingItems[i]
#             C.addInfo((item, remain_item))
#             consistent = C.isConsistent()
#             C.removeLastConstraint()
#             i += 1
#
#         for constr_add in ToRemoveConstr:
#             self.model.remove(constr_add)
#
#         self.model.update()
#         return i == len(RemainingItems)
