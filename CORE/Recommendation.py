from CORE.Tools import EPSILON
from gurobipy import *
class Recommendation:
    def __init__(self, problemDescription=None, dominanceAsymmetricPart=list(), dominanceSymmetricPart=list()):
        """dominanceAsymmetricPart and dominanceSymmetricPart : sont des List"""

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
        model, VarDict = self._problemDescription.generate_basic_gurobi_model_and_its_varDict("MOMA Model For Recommendation")

        for alt1, alt2 in self._dominanceAsymmetricPart:
            model.addConstr(alt1.linear_expr(VarDict) >= alt2.linear_expr(VarDict) + EPSILON)

        for alt1, alt2 in self._dominanceSymmetricPart:
            model.addConstr(alt1.linear_expr(VarDict) == alt2.linear_expr(VarDict))

        model.update()
        return model, VarDict

class KBestRecommendation(Recommendation):
    def __init__(self, problemDescription, dominanceAsymmetricPart, dominanceSymmetricPart, k=1):
        Recommendation.__init__(self, problemDescription, dominanceAsymmetricPart, dominanceSymmetricPart)
        self.K = k


    def _generate_recommendation(self):
        model, varDict = Recommendation.generate_recommendation_model_and_its_varDict(self)
        ListOfKBest = list()

        for altB in self._ListOfRepresentedAlternatives:
            isBest = True
            for alt in self._ListOfRepresentedAlternatives:
                if alt in ListOfKBest:
                    continue          # omet les first Bests
                model.setObjective(altB.linear_expr(varDict) - alt.linear_expr(varDict), GRB.MINIMIZE)
                model.update()
                model.optimize()
                if model.objVal < 0:
                    isBest = False
                    continue
            if isBest:
                ListOfKBest.append(altB)
            if len(ListOfKBest) == self.K:
                break

        return len(ListOfKBest) == self.K, ListOfKBest

    def isAbleToRecommend(self):
        answer, self.ListOfKBest = self._generate_recommendation() # passe en premier pour pouvoir instancier self.ListOfKBest
        if len(self._ListOfRepresentedAlternatives) != self._problemDescription.numberOfAlternatives :
            return False
        return answer

    def getRecommendation(self):
        return self.ListOfKBest

    canRecommend = property(isAbleToRecommend)
    recommendation = property(getRecommendation)


class KBestRecommendationWrapper():

    def __init__(self, k=1):
        self.K = k

    def update(self, problemDescription, dominanceAsymmetricPart, dominanceSymmetricPart):
        self.kbro = KBestRecommendation(problemDescription, dominanceAsymmetricPart, dominanceSymmetricPart, self.K)


    def isAbleToRecommend(self):
        return self.kbro.canRecommend

    def getRecommendation(self):
        return self.kbro.recommendation

    canRecommend = property(isAbleToRecommend)
    recommendation = property(getRecommendation)


from CORE.ProblemDescription import ProblemDescription
if __name__ == "__main__" :
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv", performanceTableFileName="CSVFILES/fullPerfTableTruncated.csv")
    print(mcda_problem_description)
    dominanceAsymmetricPart = list([(mcda_problem_description[7], mcda_problem_description[11]),
                                    (mcda_problem_description[11], mcda_problem_description[13]),
                                    (mcda_problem_description[13], mcda_problem_description[14])])
    dominanceSymmetricPart = []
    recommendation = KBestRecommendation(mcda_problem_description, dominanceAsymmetricPart, dominanceSymmetricPart, 4)

    if recommendation.canRecommend:
        print(recommendation.recommendation)