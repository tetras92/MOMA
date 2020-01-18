from CORE.Commitment import CommitmentStore
from CORE.DA import DA
from CORE.DM import NoisyWS_DM, WS_DM
from CORE.InconsistencySolver import InconsistencySolverFactory
from CORE.InformationPicker import *
from CORE.ProblemDescription import *
from CORE.Recommendation import RecommendationWrapper, KBestRecommendation, KRankingRecommendation
from CORE.StopCriterion import *

if __name__ == "__main__" :
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv",
                                                  performanceTableFileName="CSVFILES/PerfTable4+.csv")
    # print(mcda_problem_description)
    dm = NoisyWS_DM("CSVFILES/DM_Utility_Function.csv", 0)# WS_DM("CSVFILES/DM_Utility_Function.csv")

    DA(problemDescription=mcda_problem_description,
       NonPI_InfoPicker=RandomPicker(0),
       stopCriterion=DialogDurationStopCriterion(239),
       N_InfoPicker=RandomPicker(0),
       recommandationMaker=RecommendationWrapper(KRankingRecommendation, 2),
       InconsistencySolverType=InconsistencySolverFactory().clearPIInconsistencySolver)

    DA().interactWith(dm)
    DA().show()
    print(CommitmentStore())

# [[60] : ++++--, [54] : ++-++-, [46] : +-+++-, [58] : +++-+-, [39] : +--+++, [53] : ++-+-+, [51] : ++--++, [57] : +++--+, [45] : +-++-+]