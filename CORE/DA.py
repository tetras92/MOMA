from CORE.Dialog import Dialog
from CORE.Exceptions import DMdoesntValidateNElementException
from CORE.Explanation import Explain
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
                 InconsistencySolverType=None, ExplanationWrapper=None):
        # -- Types des attributs :
        # - problemDescription : ProblemDescription (ProblemDescription.py)
        # - NonPI_InfoPicker : InformationPicker (InformationPicker.py)
        # - N_InfoPicker : InformationPicker (InformationPicker.py)
        # - stopCriterion : StopCriterion (StopCriterion.py)
        # - recommandationMaker : Recommendation (Recommendation.py)
        # - InconsistencySolverType : InconsistencySolver (InconsistencySolver.py)

        self._problemDescription = problemDescription
        # - 08 / 07 / 20
        self._nonPIPicker = NonPI_InfoPicker
        self._NPicker = N_InfoPicker
        # -
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

        self.explanationEngine = ExplanationWrapper
        self.recommendation = None

    def show(self):
        """ --> NoneType
        affiche une recommandation partielle, complète ou Échec"""
        print("MY RECOMMENDATION IS : ", self.recommendation)
        print(self.explanationEngine)

    def interactWith(self, dm):
        """DM --> NoneType
        Méthode principale qui simule l'interaction entre le DA et le DM"""

        # n = 0
        # n_exp = 0
        # exp = 0
        self._recommendationMaker.update(self._problemDescription, **PI().getRelation())
        while (not self._recommendationMaker.canRecommend and not self._stopCriterion.stop()) or not N().is_empty():

            # model, VarDict = self._problemDescription.generate_basic_gurobi_model_and_its_varDict("MOMA_MCDA")
            # InformationStore.addInformationToModel(PI(), model, VarDict)
            # InformationStore.computeRegrets(self._problemDescription, model, VarDict)

            # print("==============Non-PI : \n{}".format(str(NonPI())))
            # print("===============N : \n{}".format(str(N())))
            # print("============= ", PI().getRelation()["dominanceRelation"])
            N().update(self._problemDescription, **PI().getRelation())
            N_initial_empty_state = N().is_empty()

            assert len(N()) + len(PI()) + len(NonPI()) == self._problemDescription.numberOfInformation

            # print("Non-PI : \n{}".format(str(NonPI())))
            # print("PI : \n{}".format(str(PI())))
            print("N : \n{}".format(str(N())))
            print("===> RECOMMENDATION ", self._recommendationMaker.recommendation)
            if not N_initial_empty_state:

                info = N().pick()
                # try:

                if info.difficultyLevel > 2:
                    self.explanationEngine.computeExplanation(self._problemDescription, info.o.dominanceObject, **PI().getRelation())
                    # n += 1
                    if self.explanationEngine.explanation == "": print("NO_EXPLANATION")
                    else: print(self.explanationEngine.explanation)
                Dialog(info).madeWith(dm)
                # except DMdoesntValidateNElementException as dme:
                #     self.explanationEngine.computeExplanation(self._problemDescription, dme.dominanceObject, **PI().getRelation())
                #     print(self.explanationEngine.explanation)
                #     self.inconsistencySolver.update(self._problemDescription)
                #     self.inconsistencySolver.solve()
                #     N().clear()


            self._recommendationMaker.update(self._problemDescription, **PI().getRelation())  # Les 2 sont nécessaires

            if not N_initial_empty_state: continue # Une question à chaque tour

            info = NonPI().pick()
            Dialog(info).madeWith(dm)
            N().update(self._problemDescription, **PI().getRelation())
            self._recommendationMaker.update(self._problemDescription, **PI().getRelation())  # Les 2 sont nécessaires
        self.recommendation = self._recommendationMaker.recommendation
        # print("N (Final): \n{}".format(str(N())))
        # print("Bilan", n, exp, n_exp)
        # model, VarDict = self._problemDescription.generate_basic_gurobi_model_and_its_varDict("MOMA_MCDA")
        # InformationStore.addInformationToModel(PI(), model, VarDict)
        # InformationStore.computeRegrets(self._problemDescription, model, VarDict)

    def reset(self):

        self._nonPIPicker.reset()
        self._NPicker.reset()
        self._stopCriterion.reset()
        # -
        self._recommendationMaker.reset()
        self.recommendation = ""
        # - #
        self.inconsistencySolver.reset()
        self.explanationEngine.reset()

        Dialog.NB = 0
        PI().clear()
        N().clear()


    # def interactWith(self, dm):
    #         """DM --> NoneType
    #         Méthode principale qui simule l'interaction entre le DA et le DM"""
    #
    #         n = 0
    #         n_exp = 0
    #         exp = 0
    #         self._recommendationMaker.update(self._problemDescription, **PI().getRelation())
    #         while not self._recommendationMaker.canRecommend and not self._stopCriterion.stop():
    #
    #             # model, VarDict = self._problemDescription.generate_basic_gurobi_model_and_its_varDict("MOMA_MCDA")
    #             # InformationStore.addInformationToModel(PI(), model, VarDict)
    #             # InformationStore.computeRegrets(self._problemDescription, model, VarDict)
    #
    #             N().update(self._problemDescription, **PI().getRelation())
    #             N_initial_empty_state = N().is_empty()
    #
    #             assert len(N()) + len(PI()) + len(NonPI()) == self._problemDescription.numberOfInformation
    #
    #             print("PI : \n{}".format(str(PI())))
    #             print("N : \n{}".format(str(N())))
    #
    #             if not N_initial_empty_state:
    #                 L = list()
    #                 D = list()
    #                 while not N().is_empty():
    #                     info = N().pick()
    #                     L.append(info.o.dominanceObject)
    #                     D.append(info.difficultyLevel)
    #                     Dialog(info).madeWith(dm)
    #                 try:
    #                     print("========================================================")
    #                     print("PI : \n{}".format(str(PI())))
    #                     for i in range(len(L)):
    #                         # self.explanationEngine.computeExplanation(self._problemDescription, info.o.dominanceObject, **PI().getRelation())
    #                         self.explanationEngine.computeExplanation(self._problemDescription, L[i], **PI().getRelation())
    #
    #                         if D[i] > 2:
    #                             n += 1
    #                             if self.explanationEngine.explanation == "": print("NO_EXPLANATION"); n_exp += 1
    #                             else: print(self.explanationEngine.explanation); exp += 1
    #
    #                 except DMdoesntValidateNElementException as dme:
    #                     self.explanationEngine.computeExplanation(self._problemDescription, dme.dominanceObject, **PI().getRelation())
    #                     print(self.explanationEngine.explanation)
    #                     self.inconsistencySolver.update(self._problemDescription)
    #                     self.inconsistencySolver.solve()
    #                     N().clear()
    #
    #
    #             self._recommendationMaker.update(self._problemDescription, **PI().getRelation())  # Les 2 sont nécessaires
    #             if not N_initial_empty_state: continue # Une question à chaque tour
    #
    #             info = NonPI().pick()
    #             Dialog(info).madeWith(dm)
    #             self._recommendationMaker.update(self._problemDescription, **PI().getRelation())  # Les 2 sont nécessaires
    #         self.recommendation = self._recommendationMaker.recommendation
    #         print("Bilan", n, exp, n_exp)
    #         # model, VarDict = self._problemDescription.generate_basic_gurobi_model_and_its_varDict("MOMA_MCDA")
    #         # InformationStore.addInformationToModel(PI(), model, VarDict)
    #         # InformationStore.computeRegrets(self._problemDescription, model, VarDict)
    #
    #
