from CORE.Dialog import Dialog
from CORE.Exceptions import DMdoesntValidateNElementException
from CORE.InformationStore import *
from CORE.Recommendation import RecommendationWrapper, KBestRecommendation


@singleton
class DA:
    """Classe modélisant l'analyste. Il est composé des outils suivants :
        - problemDescription : objet rassemblant l'ensemble des informations relatives
                                au problème MCDA traité.
        - NonPI_InfoPicker : objet de sélection d'élément au sein de NonPI.
        - N_InfoPicker : objet de sélection d'élément au sein de N (disjoint avec PI).
        - stopCriterion : objet-condition (explicite) d'arrêt.
        - recommandationMaker : objet-outil de recommandation.
        - InconsistencySolverType : objet-outil de résolution d'inconsistances."""

    def __init__(self, problemDescription=None, NonPI_InfoPicker=None, N_InfoPicker=None,
                 stopCriterion=None, recommandationMaker=RecommendationWrapper(KBestRecommendation, 1),
                 InconsistencySolverType=None):
        # -- Types des attributs :
        # - problemDescription : ProblemDescription (ProblemDescription.py)
        # - NonPI_InfoPicker : InformationPicker (InformationPicker.py)
        # - N_InfoPicker : InformationPicker (InformationPicker.py)
        # - stopCriterion : StopCriterion (StopCriterion.py)
        # - recommandationMaker : Recommendation (Recommendation.py)
        # - InconsistencySolverType : InconsistencySolver (InconsistencySolver.py)

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
        # End of Initialization of the InformationStore Objects

        self._stopCriterion = stopCriterion
        self._recommendationMaker = recommandationMaker

        self.inconsistencySolver = InconsistencySolverType
        self.inconsistencySolver.initialize_store(PI())

        self.recommendation = None

    def show(self):
        """ --> NoneType
        affiche une recommandation partielle, complète ou Échec"""
        print("MY RECOMMENDATION IS : ", self.recommendation)


    def interactWith(self, dm):
        """DM --> NoneType
        Méthode principale qui simule l'interaction entre le DA et le DM"""


        self._recommendationMaker.update(self._problemDescription, **PI().getAsymmetricAndSymmetricParts())
        while not self._recommendationMaker.canRecommend and not self._stopCriterion.stop():
            model, varDict = self._problemDescription.generate_basic_gurobi_model_and_its_varDict("MOMA_MCDA")
            N().update(varDict, model)
            N_initial_empty_state = N().is_empty()

            assert len(N()) + len(PI()) + len(NonPI()) == self._problemDescription.numberOfInformation

            print("PI : \n{}".format(str(PI())))
            print("N : \n{}".format(str(N())))

            if not N_initial_empty_state:
                info = N().pick()
                try:
                    Dialog(info).madeWith(dm)
                except DMdoesntValidateNElementException:
                    self.inconsistencySolver.update(self._problemDescription)
                    self.inconsistencySolver.solve()

            if not N_initial_empty_state: continue # Une question à chaque tour

            info = NonPI().pick()
            Dialog(info).madeWith(dm)
            self._recommendationMaker.update(self._problemDescription, **PI().getAsymmetricAndSymmetricParts())

        self.recommendation = self._recommendationMaker.recommendation



