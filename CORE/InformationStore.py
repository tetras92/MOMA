from gurobipy import *

from CORE.ComparisonTerm import *
from CORE.decorators import singleton


class InformationStore:
    def __init__(self):
        self._store = list()
    pass

@singleton
class PI(InformationStore):
    def __init__(self):
        self._store = list()
        pass #InformationStore.__init__()

    def add(self, information):
        self._store.append(information)

    def __len__(self):
        return len(self._store)

    def get_linear_expr_and_term_of_preference_information_stored(self, VarDict):
        return [pis.linear_expr_and_term(VarDict) for pis in self._store]

@singleton
class NonPI(InformationStore):
    def __init__(self, aoPicker):
        self._store = list()
        self._aoPicker = aoPicker

    def __len__(self):
        return len(self._store)

    def pick(self):
        indexToPick = self._aoPicker.pickIndex(len(self))
        return self._store.pop(indexToPick)

    def add(self, information):
        self._store.append(information)

    def update(self):
        for pco in N():
            if pco in self._store:
                self._store.remove(pco)

    def __iter__(self):
        self.update()
        return self._store.__iter__()

    def __repr__(self):
        s = ""
        for elm in self._store:
            s += str(elm) + "\n"
        return s
@singleton
class N(InformationStore):
    def __init__(self, aoPicker):
        # InformationStore.__init__()
        self._store = list()
        self._aoPicker = aoPicker

    def _check(self, pco, VarDict, gurobi_model):
        pco_linexpr, term = pco.linear_expr_and_term(VarDict)
        gurobi_model.setObjective(pco_linexpr, GRB.MINIMIZE)
        gurobi_model.update()
        gurobi_model.optimize()

        if gurobi_model.objVal >= 0:
            pco.termN = ComparisonTerm.IS_PREFERRED_TO
            return True
        gurobi_model.setObjective(- pco_linexpr, GRB.MINIMIZE)
        gurobi_model.update()
        gurobi_model.optimize()

        if gurobi_model.objVal >= 0:
            pco.termN = ComparisonTerm.IS_LESS_PREFERRED_THAN
            return True

        return False

    def update(self, VarDict, gurobi_model):
        for pco in NonPI():
            pco_linexpr, term = pco.linear_expr_and_term(VarDict)
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

        NonPI().update()

    def add(self, information):
        self._store.append(information)

    def is_empty(self):
        return len(self._store) == 0

    def pick(self):
        indexToPick = self._aoPicker.pickIndex(len(self))
        return self._store.pop(indexToPick)

    def __iter__(self):
        return self._store.__iter__()

    def __len__(self):
        return len(self._store)