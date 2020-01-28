

from CORE.Tools import EPSILON
from CORE.NecessaryPreference import *

class InconsistencySolver:
    """Classe (de base) modélisant un solveur d'inconsistance.
        La méthode principale est la méthode solve. Elle retourne le
        sous-ensemble d'éléments de la relation qui est consistante.
        Ce sous-ensemble est retournée sous d'un couple : partie assymétrique
        et partie symétrique."""
    # def __init__(self, mcda_problem_description, dominanceAsymmetricPart=[], datesAsymmetricPart=[],
    #              dominanceSymmetricPart=[], datesSymmetricPart=[], matchingInfoCoupleAlt=dict()):
    def __init__(self, mcda_problem_description, dominanceRelation=None, datesInRelation=None,
                 matchingInfoCoupleAlt=None):
        """Type des paramètres :
        mcda_problem_description : ProblemDescription
        dominanceAsymmetricPart : List[Couple[Alternative, Alternative]]
        dominanceSymmetricPart : List[Couple[Alternative, Alternative]]
        datesAsymmetricPart : List[int]
        datesSymmetricPart : List[int]
        matchingInfoCoupleAlt : Dict[Information : Couple[Alternative, Alternative]]
        """
        if matchingInfoCoupleAlt is None:
            matchingInfoCoupleAlt = dict()
        if datesInRelation is None:
            datesInRelation = list()
        if dominanceRelation is None:
            dominanceRelation = list()
        self._mcda_problem_description = mcda_problem_description
        self.dominanceRelation = dominanceRelation
        # self.dominanceSymmetricPart = dominanceSymmetricPart
        self.datesInRelation = datesInRelation
        # self.datesSymmetricPart = datesSymmetricPart
        self.matchingInfoCoupleAlt = matchingInfoCoupleAlt
        self.datesDict = dict() # datesDict associe à une date (un entier) un couple de la relation
        for das, date in list(zip(dominanceRelation, datesInRelation)):
            self.datesDict[date] = das
        # for das, date in list(zip(dominanceSymmetricPart, datesSymmetricPart)):
        #     self.datesDict[date] = das
        self.date_max = max(self.datesDict.keys())
        # self._store ne contient pas l'élément rajouté dernièrement
        self._store = [self.datesDict[date] for date in self.datesDict if date != self.date_max]

    def solve(self):
        pass

class RadicalInconsistencySolver(InconsistencySolver):
    """Classe modélisant un solveur (radical) d'une inconsistance.
        Le sous-ensemble  consistant retourné est vide."""
    def __init__(self, mcda_problem_description, dominanceRelation=None, datesInRelation=None,
                 matchingInfoCoupleAlt=None):
        InconsistencySolver.__init__(self, mcda_problem_description, dominanceRelation, datesInRelation, matchingInfoCoupleAlt)


    def solve(self):
        return [self.datesDict[self.date_max]]


class ITInconsistencySolver(InconsistencySolver):
    """Classe modélisant un solveur d'une inconsistance dont le fonctionnement
        est le suivant :
        Sachant que l'union de dominanceAsymmetricPart et de dominanceSymmetricPart est un ensemble
        inconsistant, le sous-ensemble (consistant) calculé est le plus grand inclus au sens strict dans
        l'union de dominanceAsymmetricPart et de dominanceSymmetricPart et dont l'information fournie
        le plus récemment est la plus vieille."""
    def __init__(self, mcda_problem_description, dominanceRelation=None, datesInRelation=None,
                 matchingInfoCoupleAlt=None):
        InconsistencySolver.__init__(self, mcda_problem_description, dominanceRelation, datesInRelation, matchingInfoCoupleAlt)

    # def _generate_inconsistency_solver_model_and_its_varDict(self, potentialConsistentStore):
    #     """List[Couple[Alternative, Alternative]] -> GurobiModel, Couple[Couple[Alternative, Alternative], Couple[Alternative, Alternative]]
    #         retourne d'une part le programme linéaire dont la faisabibilité déterminera la consistance de potentialConsistentStore"""
    #     model, VarDict = self._mcda_problem_description.generate_basic_gurobi_model_and_its_varDict(
    #         "Test IT IncSolv")
    #     newDominanceAsymmetricPart = list()
    #     newDominanceSymmetricPart = list()
    #
    #     for coupleAlt in potentialConsistentStore:
    #         alt1, alt2 = coupleAlt
    #         if coupleAlt in self.dominanceRelation:
    #             newDominanceAsymmetricPart.append(coupleAlt)
    #             model.addConstr(alt1.linear_expr(VarDict) >= alt2.linear_expr(VarDict) + EPSILON)
    #         elif coupleAlt in self.dominanceSymmetricPart:
    #             newDominanceSymmetricPart.append(coupleAlt)
    #             model.addConstr(alt1.linear_expr(VarDict) == alt2.linear_expr(VarDict))
    #
    #
    #     model.update()
    #     return model, (newDominanceAsymmetricPart, newDominanceSymmetricPart)


    def solve(self):
        def date_of(x):
            for date, coupleAlt in self.datesDict.items():
                if x == coupleAlt: return date
            raise Exception("InconsistencySolver : information not found")
        date_of_set_of_coupleAlt = lambda C: max([date_of(elmt) for elmt in C])

        for k in range(len(self._store), -1, -1):
            # print("k", k)
            kList_of_parts_of_store_copy = list(ite.combinations(self._store, k))
            # print("--- {}".format(len(kList_of_parts_of_store_copy)))
            if k != 0:
                kList_of_parts_of_store_copy.sort(key=lambda C: date_of_set_of_coupleAlt(C), reverse=False)
                for elmtK in kList_of_parts_of_store_copy:
                    potential_consistent_store_without_last_element = list(elmtK) # + [self.datesDict[self.date_max]]
                    new_element = self.datesDict[self.date_max]
                    # print("new element", new_element)
                    if NecessaryPreference.adjudicate(self._mcda_problem_description, potential_consistent_store_without_last_element, new_element):
                        return potential_consistent_store_without_last_element + [new_element]
            else : # le nouveau élément ne peut rester que seul dans PI
                return [self.datesDict[self.date_max]]
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
        kwargs = self._store.getRelation()
        self.iso = self._solverType(problemDescription, **kwargs)
        newDominanceRelation = self.iso.solve()
        # print("AS", newDominanceRelation)
        self._infoToDeleteStore = list()
        for information in self._store:
            coupleMatchingWithInfo = self.iso.matchingInfoCoupleAlt[information]
            #print("couple", coupleMatchingWithInfo)
            if not coupleMatchingWithInfo in newDominanceRelation:
                self._infoToDeleteStore.append(information)

        # print("{} elements to remove".format(str(len(self._infoToDeleteStore))))

    def solve(self):
        print("Inconsistency Solver : Info removed from PI :")
        for info in self._infoToDeleteStore:
            print(info, "added at {} by {}".format(info.last_commit_date, info.how_entering_pi))
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

    itics = ITInconsistencySolver(mcda_problem_description, dominanceAsymmetricPart, datesAsymmetricPart)
    a, b = itics.solve()
    print("a", a)
    print(b)
