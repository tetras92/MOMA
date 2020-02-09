from CORE.DA import DA
from CORE.DM import NoisyWS_DM
from CORE.InconsistencySolver import InconsistencySolverWrapper, RadicalInconsistencySolver
from CORE.InformationPicker import RandomPicker
from CORE.ProblemDescription import *
from CORE.Recommendation import RecommendationWrapper, KRankingRecommendation
from CORE.StopCriterion import *
from CORE.Explanation import ExplanationWrapper, Explain

if __name__ == "__main__":

    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv",
                                                  performanceTableFileName="CSVFILES/PerfTable4+.csv")
    print(mcda_problem_description)
    dm = NoisyWS_DM("CSVFILES/DM_Utility_Function6.csv", 1, 0) # WS_DM("CSVFILES/DM_Utility_Function.csv")

    DA(problemDescription=mcda_problem_description,
       NonPI_InfoPicker=RandomPicker(),
       stopCriterion=DialogDurationStopCriterion(105),
       N_InfoPicker=RandomPicker(),
       recommandationMaker=RecommendationWrapper(KRankingRecommendation, mcda_problem_description.getNumberOfAlternatives()),
       InconsistencySolverType=InconsistencySolverWrapper(RadicalInconsistencySolver),
       ExplanationWrapper=ExplanationWrapper(ListOfExplanationEngines=list([Explain.Order2SwapExplanation,
                                                                            Explain.TransitiveExplanation]),
                                             UseAll=True)
       )

    DA().interactWith(dm)
    DA().show()
    # print(CommitmentStore())
    # mcda_problem_description.listOfInformation[3].showMinMaxRegretHistory()
