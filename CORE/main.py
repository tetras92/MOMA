from CORE.DA import DA
from CORE.DM import NoisyWS_DM
from CORE.InconsistencySolver import InconsistencySolverWrapper, ITInconsistencySolver2, RadicalInconsistencySolver
from CORE.InformationPicker import RandomPicker, DeterministicPicker
from CORE.ProblemDescription import *
from CORE.Recommendation import RecommendationWrapper, KBestRecommendation, KRankingRecommendation
from CORE.StopCriterion import *

if __name__ == "__main__" :

    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv",
                                                  performanceTableFileName="CSVFILES/PerfTable4+.csv")

    dm = NoisyWS_DM("CSVFILES/DM_Utility_Function6.csv", 1, 0)# WS_DM("CSVFILES/DM_Utility_Function.csv")

    DA(problemDescription=mcda_problem_description,
       NonPI_InfoPicker=RandomPicker(0),
       stopCriterion=DialogDurationStopCriterion(105),
       N_InfoPicker=RandomPicker(0),
       recommandationMaker=RecommendationWrapper(KBestRecommendation, mcda_problem_description.getNumberOfAlternatives()//2),
       InconsistencySolverType=InconsistencySolverWrapper(ITInconsistencySolver2))

    DA().interactWith(dm)
    DA().show()
    # print(CommitmentStore())
