from CORE.DA import DA
from CORE.DM import NoisyWS_DM
from CORE.InconsistencySolver import InconsistencySolverWrapper, RadicalInconsistencySolver
from CORE.InformationPicker import RandomPicker, DifficultyLevelPicker, DeterministicPicker, DiscoveryPicker
from CORE.ProblemDescription import *
from CORE.Recommendation import RecommendationWrapper, KRankingRecommendation, KBestRecommendation
from CORE.StopCriterion import *
from CORE.Explanation import ExplanationWrapper, Explain

import time
if __name__ == "__main__":

    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv",
                                                  # performanceTableFileName="CSVFILES/test_da2pl_test.csv")
                                                  performanceTableFileName="CSVFILES/itor-test-7-alter.csv")
    print(mcda_problem_description)
    dm = NoisyWS_DM("CSVFILES/DM_Utility_Function6.csv", 0) # WS_DM("CSVFILES/DM_Utility_Function.csv")
    # dm = NoisyWS_DM("CSVFILES/DM_Utility_Function_da2pl.csv", 0) # WS_DM("CSVFILES/DM_Utility_Function.csv")

    DA(problemDescription=mcda_problem_description,
       # NonPI_InfoPicker=RandomPicker(), #,
       NonPI_InfoPicker=DeterministicPicker(), #,
       stopCriterion=DialogDurationStopCriterion(float("inf")),
       N_InfoPicker=RandomPicker(0),
       # recommandationMaker=RecommendationWrapper(KBestRecommendation, 4),
       recommandationMaker=RecommendationWrapper(KBestRecommendation, 1),
       InconsistencySolverType=InconsistencySolverWrapper(RadicalInconsistencySolver),
       ExplanationWrapper=ExplanationWrapper(ListOfExplanationEngines=list([Explain.Order2SwapMixedExplanation, Explain.general_1_vs_k_MixedExplanation,
                                                                            Explain.brut_force_general_1_vs_k_and_k_vs_1_MixedExplanation]),
                                             # Explain.Order2SwapPossibleExplanation, Explain.Order2SwapExplanation,]),
                                             #  Explain.TransitiveExplanation]),
                                             UseAll=True)
       )

    DA().interactWith(dm)
    DA().show()
    # t = time.time()
    # for i in range(100):
    #     DA().reset()
    #     DA().interactWith(dm)
    #     DA().show()
    # print((time.time() - t) / 100, "secondes en moyenne" )
    # print(CommitmentStore())
    # mcda_problem_description.listOfInformation[3].showMinMaxRegretHistory()
# MY RECOMMENDATION IS :  [[46] : +-+++-, [60] : ++++--, [45] : +-++-+, [30] : -++++-, [15] : --++++, [54] : ++-++-, [29] : -+++-+, [39] : +--+++, [58] : +++-+-, [53] : ++-+-+, [43] : +-+-++, [57] : +++--+, [23] : -+-+++, [27] : -++-++, [51] : ++--++]
