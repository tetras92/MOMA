from gurobipy import *

from CORE.Tools import covectorOfPairWiseInformationWith2Levels
from CORE.Dialog import *

class Recommendation:
    """ Classe (de base) modélisant une Recommandation."""
    def __init__(self, problemDescription=None, dominanceRelation=list()):
        """Type des paramètres :
        mcda_problem_description : ProblemDescription
        dominanceAsymmetricPart : List[Couple[Alternative, Alternative]]
        dominanceSymmetricPart : List[Couple[Alternative, Alternative]]
        """
        self._dominanceRelation = dominanceRelation
        self._ListOfRepresentedAlternatives = list()

        for alt1, alt2 in dominanceRelation:
            if alt1 not in self._ListOfRepresentedAlternatives:
                self._ListOfRepresentedAlternatives.append(alt1)
            if alt2 not in self._ListOfRepresentedAlternatives:
                self._ListOfRepresentedAlternatives.append(alt2)

        self._problemDescription = problemDescription

    def generate_recommendation_model_and_its_varList(self):
        """Retourne le corps complet d'un programme linéaire dont la résolution
        avec différents objectifs permettra de faire ou non la recommandation requise."""

        model, VarList = self._problemDescription.generate_kb_basic_gurobi_model_and_its_varList("MOMA Model For Recommendation")
        for coupleAlt in self._dominanceRelation:
            covector = covectorOfPairWiseInformationWith2Levels(coupleAlt)
            model.addConstr(quicksum(covector * VarList) >= 0)

        model.update()
        return model, VarList

class KRankingRecommendation(Recommendation):
    """Classe modélisant une recommandation du type k-Best ordonné.
        La recommandation, lorsqu'elle peut être faite, est composée des k
        meilleures alternatives qui, par ailleurs, sont ordonnées suivant
        les préférences du DM"""
    def __init__(self, k, problemDescription, dominanceRelation):
        Recommendation.__init__(self, problemDescription, dominanceRelation)
        self.K = k
        # if Dialog.NB == 105:
        #     for c in dominanceRelation:
        #         if c[0].id == 46 :
        #             print(c)

    def _oneBest(self, ListOfPreviousBest):
        """Retourne True si dans l'ensemble des alternatives apparaissant dans la relation d'ordre
         privé de celles contenues dans ListOfPreviousBest, se dégage un 1-Best (qui par ailleurs,
         est rajouté à ListOfPreviousBest)"""
        model, varList = Recommendation.generate_recommendation_model_and_its_varList(self)
        for altB in self._ListOfRepresentedAlternatives:
            if altB in ListOfPreviousBest: continue
            isBest = True
            for alt in self._ListOfRepresentedAlternatives:
                if alt in ListOfPreviousBest or alt == altB: continue          # omet les previous Bests
                covector = covectorOfPairWiseInformationWith2Levels((altB, alt))
                model.setObjective(quicksum(covector * varList), GRB.MINIMIZE)
                model.update()
                model.optimize()
                # if altB.id == 46 and model.objVal < 0:
                #     print("altB", altB, "alt", alt, "obj", float(model.objVal))

                if model.objVal < 0:
                    # if altB.id == 46 and Dialog.NB == 105:
                    #     print(alt)
                    isBest = False
                    continue
            if isBest:
                ListOfPreviousBest.append(altB)           # effet de bord
                return True
        return False

    def _generate_recommendation(self):
        ListOfKBest = list()

        for i in range(self.K):
            if not self._oneBest(ListOfKBest):
                return False, ListOfKBest
        return True, ListOfKBest


    def isAbleToRecommend(self):
        answer, self.ListOfKBest = self._generate_recommendation() # passe en premier pour pouvoir instancier self.ListOfKBest
        if len(self._ListOfRepresentedAlternatives) != self._problemDescription.numberOfAlternatives:
            return False
        return answer

    def getRecommendation(self):
        return self.ListOfKBest

    canRecommend = property(isAbleToRecommend)
    recommendation = property(getRecommendation)

class KBestRecommendation(Recommendation):
    """Classe modélisant une recommandation du type k-Best.
        La recommandation, lorsqu'elle peut être faite, est composée des k
        meilleures alternatives"""
    def __init__(self, k, problemDescription, dominanceRelation, dominanceSymmetricPart):
        Recommendation.__init__(self, problemDescription, dominanceRelation, dominanceSymmetricPart)
        self.K = k

    def _generate_recommendation(self):
        model, varDict = Recommendation.generate_recommendation_model_and_its_varList(self)
        ListKBest = list()
        for altB in self._ListOfRepresentedAlternatives:
            nb_alt_domined_by_altB = 0
            for alt in self._ListOfRepresentedAlternatives:
                if alt == altB : continue
                model.setObjective(altB.linear_expr(varDict) - alt.linear_expr(varDict), GRB.MINIMIZE)
                model.update()
                model.optimize()
                if model.objVal >= 0:
                    nb_alt_domined_by_altB += 1
            if nb_alt_domined_by_altB >= self._problemDescription.numberOfAlternatives - self.K :
                ListKBest.append(altB)
        return len(ListKBest) >= self.K, ListKBest


    def isAbleToRecommend(self):
        answer, self.ListOfKBest = self._generate_recommendation()  # passe en premier pour pouvoir instancier self.ListOfKBest
        if len(self._ListOfRepresentedAlternatives) != self._problemDescription.numberOfAlternatives:
            return False
        return answer

    def getRecommendation(self):
        return self.ListOfKBest

    canRecommend = property(isAbleToRecommend)
    recommendation = property(getRecommendation)

class RecommendationWrapper():
    """ Classe enveloppant un objet de type Recommmandation et qui rend l'inclusion
     de ce type d'objet possible dans le cadre que nous nous sommes ici fixé."""
    def __init__(self, recommendationType, *args):
        """args, sont l'ensemble des paramètres obligatoires à l'initialisation de
        recommendationType."""
        self.args = args
        self._recommendationType = recommendationType

    def update(self, problemDescription, **kwargs):
        dominanceRelation = kwargs["dominanceRelation"]
        self.ro = self._recommendationType(*self.args, problemDescription, dominanceRelation)

    def isAbleToRecommend(self):
        return self.ro.canRecommend

    def getRecommendation(self):
        return self.ro.recommendation

    canRecommend = property(isAbleToRecommend)
    recommendation = property(getRecommendation)


from CORE.ProblemDescription import ProblemDescription
if __name__ == "__main__" :
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria4.csv",
                                                  performanceTableFileName="CSVFILES/fullPerfTableTruncated.csv")
    print(mcda_problem_description)
    dominanceRelation = list([(mcda_problem_description[7], mcda_problem_description[11]),
                              (mcda_problem_description[7], mcda_problem_description[14]),
                              (mcda_problem_description[11], mcda_problem_description[13])])

    recommendation = KRankingRecommendation(1, mcda_problem_description, dominanceRelation)
    # recommendation = KBestRecommendation(mcda_problem_description, dominanceAsymmetricPart, dominanceSymmetricPart, 4)

    if recommendation.canRecommend:
        print(recommendation.recommendation)
