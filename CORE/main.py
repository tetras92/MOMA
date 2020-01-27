from CORE.DA import DA
from CORE.DM import NoisyWS_DM
from CORE.InconsistencySolver import InconsistencySolverWrapper, ITInconsistencySolver
from CORE.InformationPicker import RandomPicker
from CORE.ProblemDescription import *
from CORE.Recommendation import RecommendationWrapper, KRankingRecommendation
from CORE.StopCriterion import *

if __name__ == "__main__" :
    # mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria4.csv",
    #                                               performanceTableFileName="CSVFILES/fullPerfTableTruncated.csv")

    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv",
                                                  performanceTableFileName="CSVFILES/PerfTable4+.csv")
    # print(mcda_problem_description)

    dm = NoisyWS_DM("CSVFILES/DM_Utility_Function6.csv", 1)# WS_DM("CSVFILES/DM_Utility_Function.csv")

    DA(problemDescription=mcda_problem_description,
       NonPI_InfoPicker=RandomPicker(0),
       stopCriterion=DialogDurationStopCriterion(105),
       N_InfoPicker=RandomPicker(0),
       recommandationMaker=RecommendationWrapper(KRankingRecommendation, mcda_problem_description.getNumberOfAlternatives()),
       InconsistencySolverType=InconsistencySolverWrapper(ITInconsistencySolver))

    DA().interactWith(dm)
    DA().show()
    # print(CommitmentStore())
