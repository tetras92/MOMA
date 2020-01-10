from CORE.InformationStore import *
from CORE.ProblemDescription import *
from CORE.Recommendation import KBestRecommendationWrapper
from CORE.InconsistencySolver import InconsistencySolverFactory
from CORE.Exceptions import DMdoesntValidateNElementException
@singleton
class DA:
    def __init__(self, problemDescription=None, NonPI_InfoPicker=None, N_InfoPicker=None,
                 stopCriterion=None, recommandationMaker=None,
                 InconsistencySolverType=InconsistencySolverFactory().emptyInconsistencySolver):
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
        self.inconsistencySolver = InconsistencySolverType(PI())
        print(self.inconsistencySolver.__class__)

    def process(self, dm):
        self._recommendationMaker.update(self._problemDescription, *PI().getAsymmetricAndSymmetricParts())
        while not self._recommendationMaker.canRecommend and not self._stopCriterion.stop():
            model, varDict = self._problemDescription.generate_basic_gurobi_model_and_its_varDict("MOMA_MCDA")
            N().update(varDict, model)
            N_initial_empty_state = N().is_empty()

            assert len(N()) + len(PI()) + len(NonPI()) == self._problemDescription.numberOfInformation

            # print("PI : \n\t{}".format(str(PI())))
            # print("N : \n\t{}".format(str(N())))

            if not N_initial_empty_state:
                info = N().pick()
                try :
                    Dialog(info).madeWith(dm)
                except DMdoesntValidateNElementException:
                    self.inconsistencySolver.solve()

            if not N_initial_empty_state:
                continue

            info = NonPI().pick()
            Dialog(info).madeWith(dm)
            self._recommendationMaker.update(self._problemDescription, *PI().getAsymmetricAndSymmetricParts())

        print("MY RECOMMENDATION IS : ", self._recommendationMaker.recommendation)



from CORE.StopCriterion import *
from CORE.InformationPicker import *
from CORE.DM import NoisyWS_DM


if __name__ == "__main__" :
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv", performanceTableFileName="CSVFILES/fullPerfTableTruncated.csv")
    dm = NoisyWS_DM("CSVFILES/DM_Utility_Function.csv", 1)

    DA(problemDescription=mcda_problem_description, NonPI_InfoPicker=RandomPicker(0),
       stopCriterion=DialogDurationStopCriterion(16), N_InfoPicker=RandomPicker(0),
       recommandationMaker=KBestRecommendationWrapper(1),
       InconsistencySolverType=InconsistencySolverFactory().clearPIInconsistencySolver)

    DA().process(dm)

    #print(CommitmentStore())