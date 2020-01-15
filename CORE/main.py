from CORE.Commitment import CommitmentStore
from CORE.DA import DA
from CORE.DM import NoisyWS_DM
from CORE.InconsistencySolver import InconsistencySolverFactory
from CORE.InformationPicker import *
from CORE.ProblemDescription import *
from CORE.Recommendation import RecommendationWrapper, KBestRecommendation
from CORE.StopCriterion import *

if __name__ == "__main__" :
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv",
                                                  performanceTableFileName="CSVFILES/PerfTable4+.csv")
    # print(mcda_problem_description)
    dm = NoisyWS_DM("CSVFILES/DM_Utility_Function.csv", 0) # WS_DM("CSVFILES/DM_Utility_Function.csv")

    DA(problemDescription=mcda_problem_description,
       NonPI_InfoPicker=RandomPicker(0),
       stopCriterion=DialogDurationStopCriterion(5),
       N_InfoPicker=RandomPicker(0),
       recommandationMaker=RecommendationWrapper(KBestRecommendation, 5),
       InconsistencySolverType=InconsistencySolverFactory().clearPIInconsistencySolver)

    DA().interactWith(dm)
    DA().show()
    print(CommitmentStore())