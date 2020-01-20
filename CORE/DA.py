from CORE.Dialog import Dialog
from CORE.Exceptions import DMdoesntValidateNElementException
from CORE.InformationStore import *
from CORE.Recommendation import RecommendationWrapper, KBestRecommendation


@singleton
class DA:
    def __init__(self, problemDescription=None, NonPI_InfoPicker=None, N_InfoPicker=None,
                 stopCriterion=None, recommandationMaker=RecommendationWrapper(KBestRecommendation, 1),
                 InconsistencySolverType=None):
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

        self.inconsistencySolver = InconsistencySolverType
        self.inconsistencySolver.initialize_store(PI())

        self.recommendation = None

    def show(self):
        print("MY RECOMMENDATION IS : ", self.recommendation)


    def interactWith(self, dm):
        self._recommendationMaker.update(self._problemDescription, **PI().getAsymmetricAndSymmetricParts())
        while not self._recommendationMaker.canRecommend and not self._stopCriterion.stop():
            model, varDict = self._problemDescription.generate_basic_gurobi_model_and_its_varDict("MOMA_MCDA")
            N().update(varDict, model)
            N_initial_empty_state = N().is_empty()
            # if not  PI().is_empty():
            #     self.inconsistencySolver.update(self._problemDescription)
            assert len(N()) + len(PI()) + len(NonPI()) == self._problemDescription.numberOfInformation

            print("PI : \n{}".format(str(PI())))
            print("N : \n{}".format(str(N())))

            if not N_initial_empty_state:
                info = N().pick()
                try :
                    Dialog(info).madeWith(dm)
                except DMdoesntValidateNElementException:
                    self.inconsistencySolver.update(self._problemDescription)
                    self.inconsistencySolver.solve()

            if not N_initial_empty_state:
                continue

            info = NonPI().pick()
            Dialog(info).madeWith(dm)
            self._recommendationMaker.update(self._problemDescription, **PI().getAsymmetricAndSymmetricParts())

        self.recommendation = self._recommendationMaker.recommendation



