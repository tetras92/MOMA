from gurobipy import *

from CORE.ComparisonTerm import *
from CORE.Tools import EPSILON
from CORE.decorators import singleton


class InformationStore:
    def __init__(self, strlen=105):
        self._store = list()
        self._strlen = strlen

    @staticmethod
    def addInformationToModel(store, model, varDict):
        for information in store:
            linexpr = information.linear_expr(varDict)
            term = information.termP
            if term == ComparisonTerm.IS_LESS_PREFERRED_THAN:
                model.addConstr(- linexpr >=  EPSILON)
            elif term == ComparisonTerm.IS_PREFERRED_TO:
                model.addConstr(linexpr >= EPSILON)
            elif term == ComparisonTerm.IS_INDIFERRENT_TO:
                model.addConstr(linexpr == 0)
            else:
                raise Exception("Error in PI")
            model.update()

    def clear(self):
        pass

    def remove(self, info):
        self._store.remove(info)

    def __str__(self):
        s = "{} element(s)\n".format(len(self._store))
        if len(self._store) > self._strlen:
            s += "...\n"
            for elm in self._store[(len(self._store) - self._strlen): ]:
                s += str(elm) + "\n"
            return s

        for elm in self._store:
            s += str(elm) + "\n"
        return s

    def is_empty(self):
        return len(self._store) == 0


    def __getitem__(self, item):
        return self._store[item]

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
        R = dict()
        AL = list()
        AD = list()
        SL = list()
        SD = list()
        relationElementInfoDict = dict()
        for information in self:
            if information.termP == ComparisonTerm.IS_PREFERRED_TO:
                element = (information.alternative1, information.alternative2)
                AL.append((information.alternative1, information.alternative2))
                relationElementInfoDict[information] = element
                AD.append(information.last_commit_date)
            elif information.termP == ComparisonTerm.IS_LESS_PREFERRED_THAN:
                element = (information.alternative2, information.alternative1)
                AL.append((information.alternative2, information.alternative1))
                relationElementInfoDict[information] = element
                AD.append(information.last_commit_date)
            elif information.termP == ComparisonTerm.IS_INDIFERRENT_TO:
                element = (information.alternative1, information.alternative2)
                SL.append((information.alternative1, information.alternative2))
                relationElementInfoDict[information] = element
                SD.append(information.last_commit_date)
            else:
                raise Exception("Error getAsymmetricAndSymmetricParts in PI()")
        R["dominanceAsymmetricPart"] = AL
        R["datesAsymmetricPart"] = AD
        R["dominanceSymmetricPart"] = SL
        R["datesSymmetricPart"] = SD
        R["matchingInfoCoupleAlt"] = relationElementInfoDict
        return R

    def clear(self):
        store_copy = [info for info in self._store] # important car retire des éléments de PI
        for info in store_copy:                     # et si on fait for info in self, l'itérateur est "perturbé"
            del info.termP

    def remove(self, info):
        InformationStore.remove(self, info)

    def __str__(self):
        return InformationStore.__str__(self)

    # def __str__(self):
    #     s = "{} element(s)\n".format(len(self._store))
    #     if len(self._store) > self._strlen:
    #         s += "...\n"
    #         for elm in self._store[(len(self._store) - self._strlen): ]:
    #             s += str(elm) + "added at {} by {}\n".format(elm.last_commit_date, elm.how_entering_pi)
    #         return s
    #
    #     for elm in self._store:
    #         s += str(elm) + " date : {} how :  {}\n".format(elm.last_commit_date, elm.how_entering_pi)
    #     return s
    def is_empty(self):
        return InformationStore.is_empty(self)

    def removeAll(self, ListeInfo):
        for info in ListeInfo:
            del info.termP

@singleton
class NonPI(InformationStore):
    def __init__(self):
        InformationStore.__init__(self)

    def setInfoPicker(self, infoPicker):
        self._infoPicker = infoPicker

    def __len__(self):
        return len(self._store)

    def pick(self):
        return self._infoPicker.pick(self)

    def add(self, information):
        self._store.append(information)

    def remove(self, info):
        InformationStore.remove(self, info) # est utilisée
        #print(info, "removed from NonPI")

    def __iter__(self):
        return self._store.__iter__()

    def __str__(self):
        return InformationStore.__str__(self)

    def clear(self):
        InformationStore.clear(self)

    def is_empty(self):
        return InformationStore.is_empty(self)

    def __getitem__(self, item):
        return InformationStore.__getitem__(self, item)

@singleton
class N(InformationStore):
    def __init__(self):
        InformationStore.__init__(self)

    def setInfoPicker(self, infoPicker):
        self._infoPicker = infoPicker

    def update(self, VarDict, gurobi_model):
        N().clear() # vider pour recalculer
        InformationStore.addInformationToModel(PI(), gurobi_model, VarDict)  # effet de bord sur gurobi_model
        nonPI_copy = [info for info in NonPI()]          # indispensable car des effets de bords se produisent lorsque des éléments entrent ds N
        for info in nonPI_copy:
            # print("N : INFO EVALUATED : {}".format(str(info)))
            pco_linexpr = info.linear_expr(VarDict)
            gurobi_model.setObjective(pco_linexpr, GRB.MINIMIZE)
            gurobi_model.update()
            gurobi_model.optimize()

            # print("NonPI --")
            # print(info, gurobi_model.objVal)

            if gurobi_model.objVal >= 0:
                if gurobi_model.objVal == 0.0:
                    info.termN = ComparisonTerm.IS_INDIFERRENT_TO
                else:
                    info.termN = ComparisonTerm.IS_PREFERRED_TO
            else:
                gurobi_model.setObjective(- pco_linexpr, GRB.MINIMIZE)
                gurobi_model.update()
                gurobi_model.optimize()

                # print(info, gurobi_model.objVal)
                if gurobi_model.objVal >= 0:
                    if gurobi_model.objVal == 0.0:
                        info.termN = ComparisonTerm.IS_INDIFERRENT_TO
                    else:
                        info.termN = ComparisonTerm.IS_LESS_PREFERRED_THAN

    def add(self, information):
        self._store.append(information)



    def pick(self):
        return self._infoPicker.pick(self)

    def __iter__(self):
        return self._store.__iter__()

    def __len__(self):
        return len(self._store)

    def remove(self, info):
        InformationStore.remove(self, info)

    def __str__(self):
        return InformationStore.__str__(self)

    def __getitem__(self, item):
        return InformationStore.__getitem__(self, item)

    def clear(self):
        store_copy = [info for info in self._store] # important tout comme dans le cas de PI
        for info in store_copy:
            del info.termN

    def is_empty(self):
        return InformationStore.is_empty(self)
