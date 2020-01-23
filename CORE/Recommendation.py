from gurobipy import *

from CORE.Tools import EPSILON


class Recommendation:
    """ Classe (de base) modélisant une Recommandation."""
    def __init__(self, problemDescription=None, dominanceAsymmetricPart=list(), dominanceSymmetricPart=list()):
        """Type des paramètres :
        mcda_problem_description : ProblemDescription
        dominanceAsymmetricPart : List[Couple[Alternative, Alternative]]
        dominanceSymmetricPart : List[Couple[Alternative, Alternative]]
        """
        self._dominanceAsymmetricPart = dominanceAsymmetricPart
        self._dominanceSymmetricPart = dominanceSymmetricPart
        self._ListOfRepresentedAlternatives = list()

        for alt1, alt2 in dominanceAsymmetricPart + dominanceSymmetricPart:
            if alt1 not in self._ListOfRepresentedAlternatives:
                self._ListOfRepresentedAlternatives.append(alt1)
            if alt2 not in self._ListOfRepresentedAlternatives:
                self._ListOfRepresentedAlternatives.append(alt2)

        self._problemDescription = problemDescription

    def generate_recommendation_model_and_its_varDict(self):
        """Retourne le corps complet d'un programme linéaire dont la résolution
        avec différents objectifs permettra de faire ou non la recommandation requise."""
        model, VarDict = self._problemDescription.generate_basic_gurobi_model_and_its_varDict("MOMA Model For Recommendation")

        for alt1, alt2 in self._dominanceAsymmetricPart:
            model.addConstr(alt1.linear_expr(VarDict) >= alt2.linear_expr(VarDict) + EPSILON)

        for alt1, alt2 in self._dominanceSymmetricPart:
            model.addConstr(alt1.linear_expr(VarDict) == alt2.linear_expr(VarDict))

        model.update()
        return model, VarDict

class KRankingRecommendation(Recommendation):
    """Classe modélisant une recommandation du type k-Best ordonné.
        La recommandation, lorsqu'elle peut être faite, est composée des k
        meilleures alternatives qui, par ailleurs, sont ordonnées suivant
        les préférences du DM"""
    def __init__(self, k, problemDescription, dominanceAsymmetricPart, dominanceSymmetricPart):
        Recommendation.__init__(self, problemDescription, dominanceAsymmetricPart, dominanceSymmetricPart)
        self.K = k

    def _oneBest(self, ListOfPreviousBest):
        model, varDict = Recommendation.generate_recommendation_model_and_its_varDict(self)
        for altB in self._ListOfRepresentedAlternatives:
            if altB in ListOfPreviousBest:
                continue
            isBest = True
            for alt in self._ListOfRepresentedAlternatives:
                if alt in ListOfPreviousBest:
                    continue          # omet les previous Bests
                model.setObjective(altB.linear_expr(varDict) - alt.linear_expr(varDict), GRB.MINIMIZE)
                model.update()
                model.optimize()
                if model.objVal < 0:
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
    def __init__(self, k, problemDescription, dominanceAsymmetricPart, dominanceSymmetricPart):
        Recommendation.__init__(self, problemDescription, dominanceAsymmetricPart, dominanceSymmetricPart)
        self.K = k

    def _generate_recommendation(self):
        model, varDict = Recommendation.generate_recommendation_model_and_its_varDict(self)
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
        dominanceAsymmetricPart = kwargs["dominanceAsymmetricPart"]
        dominanceSymmetricPart = kwargs["dominanceSymmetricPart"]
        self.ro = self._recommendationType(*self.args, problemDescription, dominanceAsymmetricPart, dominanceSymmetricPart)

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
    dominanceAsymmetricPart = list([(mcda_problem_description[7], mcda_problem_description[11]),
                                    (mcda_problem_description[7], mcda_problem_description[14]),
                                    (mcda_problem_description[13], mcda_problem_description[11]),
                                    (mcda_problem_description[13], mcda_problem_description[14])])
    dominanceSymmetricPart = []
    recommendation = KRankingRecommendation(4, mcda_problem_description, dominanceAsymmetricPart, dominanceSymmetricPart)
    # recommendation = KBestRecommendation(mcda_problem_description, dominanceAsymmetricPart, dominanceSymmetricPart, 4)

    if recommendation.canRecommend:
        print(recommendation.recommendation)
