from CORE.DA import DA
from CORE.DM import WS_DM
from CORE.InconsistencySolver import InconsistencySolverWrapper, RadicalInconsistencySolver
from CORE.InformationPicker import RandomPicker, DifficultyLevelPicker, DeterministicPicker, DiscoveryPicker
from CORE.ProblemDescription import *
from CORE.Recommendation import RecommendationWrapper, KRankingRecommendation, KBestRecommendation
from CORE.StopCriterion import *
from CORE.Explanation import ExplanationWrapper, Explain
from CORE.ElicitationBasedOnExplanation import ExplanationBasedElicitation
from CORE.StrategyOfInfoOrderChoice import *

def build_explanation_text(mcda_problemDescription, best_alternative, challenger, swap_used_list, Relation):
    Explanation_text = "{} is preferred to {} because : \n".format(best_alternative, challenger)
    Explanation = list()
    NecessaryIconeList = list()
    ListAttributeLevelsList = list()
    ListAttributeLevelsList.append(best_alternative)
    if (best_alternative, challenger) in Relation:
        Explanation_text += "\tYou told me so.\n"
        return Explanation_text
    # print(swap_used_list)
    for (i_, j_) in swap_used_list:
        i = i_ - 1
        j = j_ - 1
        prec = ListAttributeLevelsList[-1]
        suiv = mcda_problemDescription.getSwapObject(prec, ({i}, {j}))
        Explanation.append(suiv)
        if suiv.is_necessary(mcda_problemDescription, Relation):
            NecessaryIconeList.append(" * ")
        else:
            NecessaryIconeList.append(" ~ ")
        ListAttributeLevelsList.append(suiv.alternative2)

    for i in range(len(Explanation)):
        elm = str(Explanation[i]) + NecessaryIconeList[i]
        Explanation_text += "\t" + elm + "\n"

    return Explanation_text

def recommend_and_explain(problem_description, relation=[]):
    best_value = 0
    best_alternative = None
    Swaps_used = None
    other_candidates = None
    for candidate in problem_description:
        other_alt = [alt for alt in mcda_problem_description.alternativesSet if alt != candidate]
        can_be_best, number_of_pwc_explained, _, details = ExplanationBasedElicitation.adjudicate(problem_description, candidate, other_alt, relation)
        if can_be_best and number_of_pwc_explained > best_value:
            best_value = number_of_pwc_explained
            best_alternative = candidate
            Swaps_used = details
            other_candidates = other_alt

    complete_text = ""
    for k in range(len(other_candidates)):
        complete_text += build_explanation_text(problem_description, best_alternative, other_candidates[k], Swaps_used[k], relation) + "\n"

    return complete_text


if __name__ == "__main__":
    ### - !!! ACTIVER / DÉSACTIVER L'AFFICHAGE COMPLET EN DÉCOMMENTANT LA LIGNE 159 DE COMMITMENT.PY function add(self, Commitment) de CommitmentStore.
    # m = 6
    # mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv",
    #                                               performanceTableFileName="CSVFILES/test_da2pl_5alt.csv")
    #
    # dm = NoisyWS_DM("CSVFILES/DM_Utility_Function_ebe_test.csv", 0)

    # m = 7
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria7.csv",
                                                  performanceTableFileName="CSVFILES/test-alternatives-7.csv")
    dm = WS_DM("CSVFILES/DM-kr-v2-7.csv", ChoiceOfInfoStrategy=RandomInfoListStrategy)

    DA(problemDescription=mcda_problem_description, N_InfoPicker=RandomPicker(), NonPI_InfoPicker=RandomPicker(), InconsistencySolverType=InconsistencySolverWrapper(RadicalInconsistencySolver))
    DA().interactInADialogGameWith(dm)
