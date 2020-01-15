from gurobipy import *

from CORE.ComparisonTerm import *
from CORE.Tools import EPSILON
from CORE.decorators import singleton


class InformationStore:
    def __init__(self):
        self._store = list()

    @staticmethod
    def addInformationToModel(store, model, varDict):
        for information in store:
            linexpr = information.linear_expr(varDict)
            term = information.termP
            if term == ComparisonTerm.IS_LESS_PREFERRED_THAN:
                model.addConstr(linexpr <= - EPSILON)
            elif term == ComparisonTerm.IS_PREFERRED_TO:
                model.addConstr(linexpr >= EPSILON)
            elif term == ComparisonTerm.IS_INDIFERRENT_TO:
                model.addConstr(linexpr == 0)
            else:
                raise Exception("Error in PI")

    def clear(self):
        pass
    def remove(self, info):
        self._store.remove(info)

    def __str__(self):
        s = ""
        for elm in self._store:
            s += str(elm) + "\n"
        return s

@singleton
class PI(InformationStore):
    def __init__(self):
        InformationStore.__init__(self)

    def add(self, information):
        self._store.append(information)

    def __len__(self):
        return len(self._store)

    def get_linear_constraint(self, VarDict):
        return [pinf.linear_constraint(VarDict) for pinf in self._store]

    def __iter__(self):
        return self._store.__iter__()

    def getAsymmetricAndSymmetricParts(self):
        AL = list()
        SL = list()
        for information in self:
            if information.termP == ComparisonTerm.IS_PREFERRED_TO:
                AL.append((information.alternative1, information.alternative2))
            elif information.termP == ComparisonTerm.IS_LESS_PREFERRED_THAN:
                AL.append((information.alternative2, information.alternative1))
            elif information.termP == ComparisonTerm.IS_INDIFERRENT_TO:
                SL.append((information.alternative1, information.alternative2))
            else:
                raise Exception("Error getAsymmetricAndSymmetricParts in PI()")

        return AL, SL

    def clear(self):
        store_copy = [info for info in self._store] # important car retire des éléments de PI
        for info in store_copy:                     # et si on fait for info in self, l'itérateur est "perturbé"
            del info.termP

    def remove(self, info):
        InformationStore.remove(self, info)

    def __str__(self):
        return InformationStore.__str__(self)

@singleton
class NonPI(InformationStore):
    def __init__(self):
        InformationStore.__init__(self)

    def setInfoPicker(self, infoPicker):
        self._infoPicker = infoPicker

    def __len__(self):
        return len(self._store)

    def pick(self):
        indexToPick = self._infoPicker.pickIndex(len(self))
        return self._store[indexToPick]

    def add(self, information):
        self._store.append(information)

    def remove(self, info):
        InformationStore.remove(self, info)


    def __iter__(self):
        return self._store.__iter__()

    def __str__(self):
        return InformationStore.__str__(self)

    def clear(self):
        InformationStore.clear(self)

@singleton
class N(InformationStore):
    def __init__(self):
        InformationStore.__init__(self)

    def setInfoPicker(self, infoPicker):
        self._infoPicker = infoPicker

    def update(self, VarDict, gurobi_model):
        N().clear() # vider pour recalculer
        InformationStore.addInformationToModel(PI(), gurobi_model, VarDict)  # effet de bord sur gurobi_model
        for info in NonPI():
            pco_linexpr = info.linear_expr(VarDict)
            gurobi_model.setObjective(pco_linexpr, GRB.MINIMIZE)
            gurobi_model.update()
            gurobi_model.optimize()

            if gurobi_model.objVal >= 0:
                info.termN = ComparisonTerm.IS_PREFERRED_TO
            else:
                gurobi_model.setObjective(- pco_linexpr, GRB.MINIMIZE)
                gurobi_model.update()
                gurobi_model.optimize()
                if gurobi_model.objVal >= 0:
                    info.termN = ComparisonTerm.IS_LESS_PREFERRED_THAN

    def add(self, information):
        self._store.append(information)

    def is_empty(self):
        return len(self._store) == 0

    def pick(self):
        indexToPick = self._infoPicker.pickIndex(len(self))
        return self._store[indexToPick]

    def __iter__(self):
        return self._store.__iter__()

    def __len__(self):
        return len(self._store)

    def remove(self, info):
        InformationStore.remove(self, info)

    def __str__(self):
        return InformationStore.__str__(self)

    def clear(self):
        store_copy = [info for info in self._store] # important tout comme dans le cas de PI
        for info in store_copy:
            del info.termN