from CORE.InformationStore import *
from CORE.ProblemDescription import *
from CORE.Recommendation import KBestRecommendationWrapper
@singleton
class DA:
    def __init__(self, problemDescription=None, NonPI_InfoPicker=None, N_InfoPicker=None, stopCriterion=None, recommandationMaker=None):
        self._problemDescription = problemDescription
        # Initialization of the InformationStore Objects
            # NonPi
        NonPI()
        NonPI().setInfoPicker(NonPI_InfoPicker)
            # PI
        PI()
            # N
        N()
        N().setInfoPicker(N_InfoPicker)
        # End
        self._stopCriterion = stopCriterion
        self._recommendationMaker = recommandationMaker

    def process(self, dm):
        self._recommendationMaker.update(self._problemDescription, *PI().getAsymmetricAndSymmetricParts())
        while not self._recommendationMaker.canRecommend and not self._stopCriterion.stop():
            model, varDict = self._problemDescription.generate_basic_gurobi_model_and_its_varDict("MOMA_MCDA")
            N().update(varDict, model)
            N_initial_empty_state = N().is_empty()
            if not N_initial_empty_state:
                info = N().pick()
                Dialog(info).madeWith(dm)

            if not N_initial_empty_state:
                continue

            info = NonPI().pick()
            Dialog(info).madeWith(dm)
            self._recommendationMaker.update(self._problemDescription, *PI().getAsymmetricAndSymmetricParts())

        print("MY RECOMMENDATION IS : ", self._recommendationMaker.recommendation)



from CORE.StopCriterion import *
from CORE.InformationPicker import *
from CORE.DM import NoisyWS_DM
from CORE.Commitment import CommitmentStore

if __name__ == "__main__" :
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv", performanceTableFileName="CSVFILES/fullPerfTableTruncated.csv")
    dm = NoisyWS_DM("CSVFILES/DM_Utility_Function.csv", 1)

    DA(problemDescription=mcda_problem_description, NonPI_InfoPicker=RandomPicker(0),
       stopCriterion=DialogDurationStopCriterion(16), N_InfoPicker=RandomPicker(0),
       recommandationMaker=KBestRecommendationWrapper(1))

    DA().process(dm)

    print(CommitmentStore())