from gurobipy import *

from CORE.ComparisonTerm import *
from CORE.decorators import singleton


class InformationStore:
    def __init__(self):
        self._store = list()



@singleton
class PI(InformationStore):
    def __init__(self):
        self._store = list()

    def add(self, information):
        self._store.append(information)

    def __len__(self):
        return len(self._store)

    def get_linear_constraint(self, VarDict):
        return [pinf.linear_constraint(VarDict) for pinf in self._store]

    def __iter__(self):
        return self._store.__iter__()

@singleton
class NonPI(InformationStore):
    def __init__(self, aoPicker):
        self._store = list()
        self._aoPicker = aoPicker

    def __len__(self):
        return len(self._store)

    def pick(self):
        indexToPick = self._aoPicker.pickIndex(len(self))
        return self._store[indexToPick]

    def add(self, information):
        self._store.append(information)

    def remove(self, info):
        self._store.remove(info)


    def __iter__(self):
        return self._store.__iter__()

    def __str__(self):
        s = ""
        for elm in self._store:
            s += str(elm) + "\n"
        return s
@singleton
class N(InformationStore):
    def __init__(self, aoPicker):
        self._store = list()
        self._aoPicker = aoPicker

    def update(self, VarDict, gurobi_model):
        for pco in NonPI():
            pco_linexpr = pco.linear_expr(VarDict)
            gurobi_model.setObjective(pco_linexpr, GRB.MINIMIZE)
            gurobi_model.update()
            gurobi_model.optimize()

            if gurobi_model.objVal >= 0:
                pco.termN = ComparisonTerm.IS_PREFERRED_TO
            else:
                gurobi_model.setObjective(- pco_linexpr, GRB.MINIMIZE)
                gurobi_model.update()
                gurobi_model.optimize()
                if gurobi_model.objVal >= 0:
                    pco.termN = ComparisonTerm.IS_LESS_PREFERRED_THAN



    def add(self, information):
        self._store.append(information)

    def is_empty(self):
        return len(self._store) == 0

    def pick(self):
        indexToPick = self._aoPicker.pickIndex(len(self))
        return self._store[indexToPick]

    def __iter__(self):
        return self._store.__iter__()

    def __len__(self):
        return len(self._store)

    def remove(self, info):
        self._store.remove(info)