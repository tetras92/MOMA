from CORE.Exceptions import DMdoesntValidateNElementException
from CORE.InconsistencySolver import InconsistencySolverFactory
from CORE.InformationStore import *
from CORE.Recommendation import KBestRecommendationWrapper
from CORE.Dialog import Dialog

@singleton
class DA:
    def __init__(self, problemDescription=None, NonPI_InfoPicker=None, N_InfoPicker=None,
                 stopCriterion=None, recommandationMaker=KBestRecommendationWrapper(1),
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
        self.recommendation = None

    def show(self):
        print("MY RECOMMENDATION IS : ", self.recommendation)


    def interactWith(self, dm):
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

        self.recommendation = self._recommendationMaker.recommendation



