from CORE.decorators import singleton
from CORE.Tools import EPSILON
from gurobipy import *

class InconsistencySolver:
    """Classe (de base) modélisant un solveur d'inconsistance.
        La méthode principale est la méthode solve. Elle retourne le
        sous-ensemble d'éléments de la relation qui est consistante.
        Ce sous-ensemble est retournée sous d'un couple : partie assymétrique
        et partie symétrique."""
    def __init__(self, mcda_problem_description, dominanceAsymmetricPart=[], datesAsymmetricPart=[],
                 dominanceSymmetricPart=[], datesSymmetricPart=[], matchingInfoCoupleAlt=dict()):
        """Type des paramètres :
        mcda_problem_description : ProblemDescription
        dominanceAsymmetricPart : List[Couple[Alternative, Alternative]]
        dominanceSymmetricPart : List[Couple[Alternative, Alternative]]
        datesAsymmetricPart : List[int]
        datesSymmetricPart : List[int]
        matchingInfoCoupleAlt : Dict[Information : Couple[Alternative, Alternative]]
        """
        self._mcda_problem_description = mcda_problem_description
        self.dominanceAsymmetricPart = dominanceAsymmetricPart
        self.dominanceSymmetricPart = dominanceSymmetricPart
        self.datesAsymmetricPart = datesAsymmetricPart
        self.datesSymmetricPart = datesSymmetricPart
        self.matchingInfoCoupleAlt = matchingInfoCoupleAlt
        self.datesDict = dict() # datesDict associe à une date (un entier) un couple de la relation
        for das, date in list(zip(dominanceAsymmetricPart, datesAsymmetricPart)):
            self.datesDict[date] = das
        for das, date in list(zip(dominanceSymmetricPart, datesSymmetricPart)):
            self.datesDict[date] = das
        self.date_max = max(self.datesDict.keys())
        # self._store ne contient pas l'élément rajouté dernièrement
        self._store = [self.datesDict[date] for date in self.datesDict if date != self.date_max]

    def solve(self):
        pass

class RadicalInconsistencySolver(InconsistencySolver):
    """Classe modélisant un solveur (radical) d'une inconsistance.
        Le sous-ensemble  consistant retourné est vide."""
    def __init__(self, mcda_problem_description, dominanceAsymmetricPart=[], datesAsymmetricPart=[],
                 dominanceSymmetricPart=[], datesSymmetricPart=[], matchingInfoCoupleAlt=dict()):
        InconsistencySolver.__init__(self, mcda_problem_description, dominanceAsymmetricPart, datesAsymmetricPart,
                                     dominanceSymmetricPart, datesSymmetricPart, matchingInfoCoupleAlt)


    def solve(self):
        return list(), list()


class ITInconsistencySolver(InconsistencySolver):
    """Classe modélisant un solveur d'une inconsistance dont le fonctionnement
        est le suivant :
        Sachant que l'union de dominanceAsymmetricPart et de dominanceSymmetricPart est un ensemble
        inconsistant, le sous-ensemble (consistant) calculé est le plus grand inclus au sens strict dans
        l'union de dominanceAsymmetricPart et de dominanceSymmetricPart dont l'information fournie
        le plus récemment est la plus vieille."""
    def __init__(self, mcda_problem_description, dominanceAsymmetricPart=[], datesAsymmetricPart=[],
                 dominanceSymmetricPart=[], datesSymmetricPart=[], matchingInfoCoupleAlt=dict()):
        InconsistencySolver.__init__(self, mcda_problem_description, dominanceAsymmetricPart, datesAsymmetricPart,
                 dominanceSymmetricPart, datesSymmetricPart, matchingInfoCoupleAlt)

    def _generate_inconsistency_solver_model_and_its_varDict(self, potentialConsistentStore):
        """List[Couple[Alternative, Alternative]] -> GurobiModel, Couple[Couple[Alternative, Alternative], Couple[Alternative, Alternative]]
            retourne d'une part le programme linéaire dont la faisabibilité déterminera la consistance de potentialConsistentStore"""
        model, VarDict = self._mcda_problem_description.generate_uta_gms_basic_gurobi_model_and_its_varDict(
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
            raise Exception("InconsistencySolver : information not found")
        date_of_set_of_coupleAlt = lambda C: max([date_of(elmt) for elmt in C])

        for k in range(len(self._store), -1, -1):
            kList_of_parts_of_store_copy = list(ite.combinations(self._store, k))
            if k != 0:
                kList_of_parts_of_store_copy.sort(key=lambda C: date_of_set_of_coupleAlt(C))
            for elmtK in kList_of_parts_of_store_copy:
                potential_consistent_store = list(elmtK) + [self.datesDict[self.date_max]]
                model, (newDominanceAsymmetricPart, newDominanceSymmetricPart) = \
                    self._generate_inconsistency_solver_model_and_its_varDict(potential_consistent_store)
                model.update()
                model.optimize()
                # print(elmtK, "age", date_of_set_of_coupleAlt(elmtK))
                if model.status == GRB.OPTIMAL:
                    return newDominanceAsymmetricPart, newDominanceSymmetricPart
                # elif model.status == GRB.INFEASIBLE:
                #     print("INFEASIBLE")
        raise Exception("Error in IT InconsistencySolver")


class InconsistencySolverWrapper():
    """Classe permettant l'intégration d'un solveur d'inconsistance dans le cadre que nous envisageons ici.
        À l'initialisation,  on instancie le type de solveur à utiliser."""
    def __init__(self, SolverType):
        self._solverType = SolverType

    def initialize_store(self, store):
        self._store = store

    def update(self, problemDescription):
        """Cette méthode 'charge' le solveur à utiliser avec les paramètres
            attendus, lance une résolution du problème et récupère le sous-ensemble
            consistant à retenir."""
        kwargs = self._store.getAsymmetricAndSymmetricParts()
        self.iso = self._solverType(problemDescription, **kwargs)
        newDominanceAsymmetricPart, newDominanceSymmetricPart = self.iso.solve()
        # print("AS", newDominanceAsymmetricPart)
        self._infoToDeleteStore = list()
        for information in self._store:
            coupleMatchingWithInfo = self.iso.matchingInfoCoupleAlt[information]
            #print("couple", coupleMatchingWithInfo)
            if not coupleMatchingWithInfo in newDominanceAsymmetricPart\
                    and not coupleMatchingWithInfo in newDominanceSymmetricPart:
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
