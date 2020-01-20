from CORE.decorators import singleton
from CORE.Tools import EPSILON
from gurobipy import *

class InconsistencySolver:
    def __init__(self, mcda_problem_description, dominanceAsymmetricPart=[], datesAsymmetricPart=[],
                 dominanceSymmetricPart=[], datesSymmetricPart=[], matchingInfoCoupleAlt=dict()):
        self._mcda_problem_description = mcda_problem_description
        self.dominanceAsymmetricPart = dominanceAsymmetricPart
        self.dominanceSymmetricPart = dominanceSymmetricPart
        self.datesAsymmetricPart = datesAsymmetricPart
        self.datesSymmetricPart = datesSymmetricPart
        self.matchingInfoCoupleAlt = matchingInfoCoupleAlt
        self.datesDict = dict()
        for das, date in list(zip(dominanceAsymmetricPart, datesAsymmetricPart)):
            self.datesDict[date] = das
        for das, date in list(zip(dominanceSymmetricPart, datesSymmetricPart)):
            self.datesDict[date] = das
        self.date_max = max(self.datesDict.keys())
        # self._store ne contient pas l'élément rajouté dernièrement
        self._store = [self.datesDict[date] for date in self.datesDict if date != self.date_max]
        # print("combi", self._store)
        # self._store = infoStore

    def solve(self):
        pass

class ClearPIInconsistencySolver(InconsistencySolver):
    def __init__(self, mcda_problem_description, dominanceAsymmetricPart=[], datesAsymmetricPart=[],
                 dominanceSymmetricPart=[], datesSymmetricPart=[], matchingInfoCoupleAlt=dict()):
        InconsistencySolver.__init__(self, mcda_problem_description, dominanceAsymmetricPart, datesAsymmetricPart,
                                     dominanceSymmetricPart, datesSymmetricPart, matchingInfoCoupleAlt)


    def solve(self):
        return list(), list()


class ITInconsistencySolver(InconsistencySolver):
    def __init__(self, mcda_problem_description, dominanceAsymmetricPart=[], datesAsymmetricPart=[],
                 dominanceSymmetricPart=[], datesSymmetricPart=[], matchingInfoCoupleAlt=dict()):
        InconsistencySolver.__init__(self, mcda_problem_description, dominanceAsymmetricPart, datesAsymmetricPart,
                 dominanceSymmetricPart, datesSymmetricPart, matchingInfoCoupleAlt)

    def generate_inconsistency_solver_model_and_its_varDict(self, potentialConsistentStore):
        model, VarDict = self._mcda_problem_description.generate_basic_gurobi_model_and_its_varDict(
            "Test IT IncSolv")
        newDominanceAsymmetricPart = list()
        newDominanceSymmetricPart = list()

        for coupleAlt in potentialConsistentStore:
            alt1, alt2 = coupleAlt
            if coupleAlt in self.dominanceAsymmetricPart:
                newDominanceAsymmetricPart.append(coupleAlt)
                model.addConstr(alt1.linear_expr(VarDict) >= alt2.linear_expr(VarDict) + EPSILON)
            elif coupleAlt in self.dominanceSymmetricPart:
                newDominanceSymmetricPart.append(coupleAlt)
                model.addConstr(alt1.linear_expr(VarDict) == alt2.linear_expr(VarDict))


        model.update()
        return model, (newDominanceAsymmetricPart, newDominanceSymmetricPart)


    def solve(self):
        def date_of(x):
            for date, coupleAlt in self.datesDict.items():
                if x == coupleAlt: return date
            raise Exception("InconsistencySolver : not found")
        date_of_set_of_coupleAlt = lambda C: max([date_of(elmt) for elmt in C])

        for k in range(len(self._store), -1, -1):
            kList_of_parts_of_store_copy = list(ite.combinations(self._store, k))
            if k != 0:
                kList_of_parts_of_store_copy.sort(key=lambda C: date_of_set_of_coupleAlt(C))
            for elmtK in kList_of_parts_of_store_copy:
                potential_consistent_store = list(elmtK) + [self.datesDict[self.date_max]]
                model, (newDominanceAsymmetricPart, newDominanceSymmetricPart) = self.generate_inconsistency_solver_model_and_its_varDict(potential_consistent_store)
                model.update()
                model.optimize()
                # print(elmtK, "age", date_of_set_of_coupleAlt(elmtK))
                if model.status == GRB.OPTIMAL:
                    return newDominanceAsymmetricPart, newDominanceSymmetricPart
                # elif model.status == GRB.INFEASIBLE:
                #     print("INFEASIBLE")
        raise Exception("Error in IT InconsistencySolver")


class InconsistencySolverWrapper():
    def __init__(self, SolverType):
        self._solverType = SolverType

    def initialize_store(self, store):
        self._store = store

    def update(self, problemDescription):
        kwargs = self._store.getAsymmetricAndSymmetricParts()
        self.iso = self._solverType(problemDescription, **kwargs)
        newDominanceAsymmetricPart, newDominanceSymmetricPart = self.iso.solve()
        # print("AS", newDominanceAsymmetricPart)
        self._infoToDeleteStore = list()
        for information in self._store:
            coupleMatchingWithInfo = self.iso.matchingInfoCoupleAlt[information.id]
            #print("couple", coupleMatchingWithInfo)
            if not coupleMatchingWithInfo in newDominanceAsymmetricPart and not coupleMatchingWithInfo in newDominanceSymmetricPart:
                self._infoToDeleteStore.append(information)

        # print("{} elements to remove".format(str(len(self._infoToDeleteStore))))

    def solve(self):
        print("Inconsistency Solver : Info removed from PI :")
        for info in self._infoToDeleteStore:
            print(info)
        self._store.removeAll(self._infoToDeleteStore)


from CORE.ProblemDescription import ProblemDescription
import itertools as ite
if __name__ == "__main__":
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv",
                                                  performanceTableFileName="CSVFILES/PerfTable4+.csv")
    print(mcda_problem_description)
    # dominanceAsymmetricPart = list([(mcda_problem_description[29], mcda_problem_description[60]),
    #                                 (mcda_problem_description[23], mcda_problem_description[54]),
    #                                 (mcda_problem_description[46], mcda_problem_description[15]),
    #                                 (mcda_problem_description[15], mcda_problem_description[15])])

    dominanceAsymmetricPart = list([(mcda_problem_description[15], mcda_problem_description[15]),
                                    (mcda_problem_description[29], mcda_problem_description[60])])
    dominanceSymmetricPart = []
    datesAsymmetricPart = list([0, 1])
    datesSymmetricPart = list()

    itics = ITInconsistencySolver(mcda_problem_description, dominanceAsymmetricPart, datesAsymmetricPart,
                                  dominanceSymmetricPart, datesSymmetricPart)
    a, b = itics.solve()
    print("a", a)
    print(b)