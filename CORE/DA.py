import random

from CORE.Dialog import Dialog
from CORE.Exceptions import DMdoesntValidateNElementException, DMdoesntValidateAtomicAssumedElementException, AskWhyException
from CORE.Explanation import Explain
from CORE.InformationStore import *
from CORE.Recommendation import RecommendationWrapper, KBestRecommendation
from CORE.DG_RecommendationEngine import DGRecommendationEngine


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

    def ijcai_interaction(self, dm):
        """DM --> NoneType
        Méthode qui simule l'interaction entre le DA et le DM telle que pensée pour IJCAI21"""

        while not self._stopCriterion.stop():
            info = NonPI().pick()
            Dialog(info).madeWith(dm)

    def interactInADialogGameWith(self, dm):
        all_validated = False
        while not all_validated:
            recommendation_engine = DGRecommendationEngine(self._problemDescription, **PI().getRelation())
            all_validated = True
            # print("A : \n{}".format(str(A())))
            print()
            able_to_fully_explain, infoList, best_alternative, explanation_swap_A_info = recommendation_engine.process()
            # print(explanation_swap_A_info)
            if able_to_fully_explain:
                print("\t\t** RECOMMENDATION : {} **\n\n\n\n\t\t\t** The Dialog **".format(best_alternative))
                order_k_list = [k_ for k_ in range(len(infoList))]
                random.shuffle(order_k_list)
                for k in order_k_list: # Utiliser APicker
                    info = infoList[k]
                    k_swap_explanation = explanation_swap_A_info[k]
                    # print("out PI : \n{}".format(str(PI())))
                    try:
                        # print("\n", info)
                        Dialog(info).madeWith(dm)
                    except AskWhyException as awe:
                        for swap_a_info in k_swap_explanation:
                            try:
                                Dialog(swap_a_info).madeWith(dm)
                            except DMdoesntValidateAtomicAssumedElementException as dma2:
                                all_validated = False
                                # break
                        N().clear()        # rajouté le 15/10/2021
                        A().clear()
                        # AA().clear()         # rajouté le 15/10/2021 : essentiellement pour le garbage collector qui detruira ces objets
                        break

            else: # use NonPi picker a domaine restreint
                all_validated = False
                k = random.randint(0, len(infoList)-1)
                Dialog(infoList[k]).madeWith(dm)

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


