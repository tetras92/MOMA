from CORE.ElicitationBasedOnExplanation import ExplanationBasedElicitation
from CORE.NecessaryPreference import NecessaryPreference
from CORE.Tools import AS_LEAST_AS_GOOD_AS, NOT_AS_LEAST_AS_GOOD_AS, EMPTYSET
from CORE.InformationStore import NonPI, N, PI, A, AA

import random
# DG : Dialog Game
class DGRecommendationEngine:
    # 20 / 06 / 2021
    """ Classe (de base) modélisant un moteur de Recommandation dans le cadre d'un jeu de dialogue."""
    def __init__(self, problemDescription, **kwargs):
        """Type des paramètres :
        mcda_problem_description : ProblemDescription
        dominanceRelation : List[Couple[Alternative, Alternative]]
        """
        self._dominanceRelation = kwargs["recommendationDominanceRelation"]
        # print(self._dominanceRelation)
        self._problemDescription = problemDescription


    ### - Jeudi 14 octobre 2021 : tentative de maj de process : objectif : traiter indifféremment les comparaisons d'alternatives swaps natifs des comparaisons d'alternatives dont
                                                                          # la difficultyLevel est > 2.
    # def process(self):
    #     best_value = -float("inf")
    #     best_alternative = None
    #     swaps_used = None
    #     other_candidates = None
    #     unexplained_challengers = list()
    #
    #
    #     L = list()
    #     for candidate in self._problemDescription:
    #         L.append(candidate)
    #     random.shuffle(L)
    #     for candidate in L:
    #     # for candidate in self._problemDescription:
    #         dispensed_from_explanation_number = 0      # bug du siecle 20/19/2021
    #         other_alt = [alt for alt in self._problemDescription.alternativesSet if alt != candidate]
    #         can_be_best, number_of_pwc_explained, pareto_dominance, details = ExplanationBasedElicitation.adjudicate(self._problemDescription, candidate, other_alt, self._dominanceRelation)
    #         challengers_unexplained = list()
    #         if can_be_best:
    #             for k in range(len(details)):
    #                 # print("CHECKING", number_of_pwc_explained, details)
    #                 swaps_list_k = details[k]
    #                 if len(swaps_list_k) == 0 and not pareto_dominance[k]:   # non expliqué
    #                     challengers_unexplained.append(other_alt[k])
    #                     if NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (candidate, other_alt[k])):
    #                         # print("I'M DISPENSATED", (candidate, other_alt[k]))
    #                         dispensed_from_explanation_number += 1
    #                         challengers_unexplained.remove(other_alt[k]) # lorsque necessaire : expliqué par défaut
    #             if len(details) == dispensed_from_explanation_number:         # 20/10/2021
    #                 # print("=============================>")
    #                 value = 1
    #             else:
    #                 value = number_of_pwc_explained / (len(details) - dispensed_from_explanation_number)
    #
    #             if value > best_value: # >= pour entrer au moins une fois
    #                 best_value = value
    #                 best_alternative = candidate
    #                 # print("les candidats", best_alternative)
    #                 swaps_used = details
    #                 other_candidates = other_alt
    #                 unexplained_challengers = challengers_unexplained
    #         # break                                                          # A RETIRER (DEBOGAGE)
    #
    #     returned_AInfo_list = list()
    #     explanation_sequences_list = list()
    #     # print("SWAPS", other_candidates, swaps_used)
    #     # print("Value", best_value)
    #     print("\n\n\t\t***** DA thinking... *****\n")
    #     if best_value == 1:
    #         # print("\n\n***** DA thinking... *****{}\n".format(len(other_candidates)))
    #         # print("before for======== A()", A())
    #         # print('=======NonPI()', NonPI())
    #         for k in range(len(other_candidates)):
    #             challenger = other_candidates[k]
    #             correspondingInfo = self._problemDescription.dictOfInformation[(best_alternative, challenger)]
    #             isCorrespondingInfoNecessary = False
    #             # transfert NonPI ==> N
    #             # if (best_alternative, challenger) not in self._dominanceRelation and\
    #             if correspondingInfo not in PI() and\
    #                     NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (best_alternative, challenger)):
    #                 if correspondingInfo.alternative1 == best_alternative:
    #                     correspondingInfo.termN = AS_LEAST_AS_GOOD_AS()
    #                 else:
    #                     correspondingInfo.termN = NOT_AS_LEAST_AS_GOOD_AS()
    #
    #                 isCorrespondingInfoNecessary = True
    #
    #             elif correspondingInfo in PI():
    #                 isCorrespondingInfoNecessary = correspondingInfo.termPConfirm  # always True
    #
    #             else:
    #                 if correspondingInfo.alternative1 == best_alternative:
    #                     correspondingInfo.termA = AS_LEAST_AS_GOOD_AS()
    #                 else:
    #                     correspondingInfo.termA = NOT_AS_LEAST_AS_GOOD_AS()
    #
    #             returned_AInfo_list.append(correspondingInfo)
    #
    #
    #             swaps_used_list = swaps_used[k]
    #             k_alternative_sequence = [best_alternative]
    #             k_explanation_sequence = list()
    #
    #             # print("======== A()", A())
    #             if not isCorrespondingInfoNecessary:
    #                 # if len(swaps_used_list) == 0:
    #                 #     print(correspondingInfo, "=====================SWAPS_USED")
    #                 for (i_, j_) in swaps_used_list:
    #                     prec = k_alternative_sequence[-1]
    #                     i = i_ - 1
    #                     if j_ == EMPTYSET:
    #                         suiv = self._problemDescription.pareto_translation(prec, i)
    #                     else :
    #                         j = j_ - 1
    #                         suiv = self._problemDescription.swap_translation(prec, ({i}, {j}))
    #
    #                     info_prec_suiv = self._problemDescription.generateFictiveAtomicInformation(prec, suiv)
    #
    #                     if NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (prec, suiv)):
    #                             info_prec_suiv.termN = AS_LEAST_AS_GOOD_AS()
    #
    #                     # elif (prec, suiv) in self._dominanceRelation:
    #                     #     raise Exception("peut arriver ????")
    #
    #                     else:
    #                         info_prec_suiv.termAA = AS_LEAST_AS_GOOD_AS()
    #
    #                     k_alternative_sequence.append(suiv)
    #
    #                     k_explanation_sequence.append(info_prec_suiv)
    #
    #                 # if len(k_explanation_sequence) == 0:
    #                 #     print(correspondingInfo, "=====================KEXP_VIDE")
    #                 correspondingInfo.cause = [expl_info for expl_info in k_explanation_sequence]
    #                 print() # Sert a espacer les differents suppositions
    #
    #             else:      # quand necessaire la cause, c'est (pour le moment) l'info elle-meme
    #                 correspondingInfo.cause = [correspondingInfo]
    #
    #             explanation_sequences_list.append(k_explanation_sequence)
    #         # return True, returned_AInfo_list, best_alternative, explanation_sequences_list  OLD VERSION avant la cause des info
    #         return True, returned_AInfo_list, best_alternative
    #
    #     print("\t\t***** DA : there is no explainable potential 1-best alternative ! *****\n")
    #     # return False, [self._problemDescription.dictOfInformation[(best_alternative, challenger)] for challenger in unexplained_challengers], best_alternative, None OLD VERSION anvant la cause des info
    #     return False, [self._problemDescription.dictOfInformation[(best_alternative, challenger)] for challenger in unexplained_challengers], best_alternative
    #

    def process(self):
        EPB = dict()
        EPB_List_candidates = list()
        for candidate in self._problemDescription:
            other_alt = [alt for alt in self._problemDescription.alternativesSet if alt != candidate]
            is_in_EPB, number_of_pairs_explained, number_of_pairs_in_K_ACS, List_of_Corresponding_swaps= ExplanationBasedElicitation.adjudicate(self._problemDescription, candidate, other_alt, self._dominanceRelation)
            if is_in_EPB:
                EPB[candidate] = {"challengers": other_alt, "swaps": List_of_Corresponding_swaps, "number_of_pairs_explained": number_of_pairs_explained, "K_ACS_length": number_of_pairs_in_K_ACS}
                EPB_List_candidates.append(candidate)

        if len(EPB) == 0:
            print("\t\t***** DA : there is no explainable potential 1-best alternative ! *****\n")
            return False, None, None                                                             # ALLER PICKER DANS NONPI

        # Choix aleatoire pour l'instant
        best_alternative = EPB_List_candidates[random.randint(0, len(EPB)-1)]
        # best_alternative = EPB_List_candidates[1]                               # PHASE DEBOOGAGE
        other_candidates = EPB[best_alternative]["challengers"]
        swaps_used = EPB[best_alternative]["swaps"]

        print("\n\n\t\t***** DA thinking... *****\n")
        # print("A", A())
        # print("NonPI", NonPI())
        # print("PI", PI())
        # print("N", N())

        returned_Info_list = list()
        explanation_sequences_list = list()
        for k in range(len(other_candidates)):
            challenger = other_candidates[k]
            correspondingInfo = self._problemDescription.dictOfInformation[(best_alternative, challenger)]
            isCorrespondingInfoInK_ACS = False
            if correspondingInfo in PI():
                isCorrespondingInfoInK_ACS = correspondingInfo.termPConfirm  # always True
            elif NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (best_alternative, challenger)):
                if correspondingInfo.alternative1 == best_alternative:
                    correspondingInfo.termN = AS_LEAST_AS_GOOD_AS()
                else:
                    correspondingInfo.termN = NOT_AS_LEAST_AS_GOOD_AS()
            else:
                if correspondingInfo.alternative1 == best_alternative:
                    correspondingInfo.termA = AS_LEAST_AS_GOOD_AS()
                else:
                    correspondingInfo.termA = NOT_AS_LEAST_AS_GOOD_AS()

            returned_Info_list.append(correspondingInfo)

            swaps_used_list = swaps_used[k]
            k_alternative_sequence = [best_alternative]
            k_explanation_sequence = list()

            if isCorrespondingInfoInK_ACS:
                correspondingInfo.cause = [correspondingInfo]                           # Explication : "tu m'as dit"
            else:
                for (i_, j_) in swaps_used_list:
                    prec = k_alternative_sequence[-1]
                    i = i_
                    if j_ == EMPTYSET:
                        suiv = self._problemDescription.pareto_translation(prec, i)
                    else:
                        j = j_
                        suiv = self._problemDescription.swap_translation(prec, ({i}, {j}))

                    info_prec_suiv = self._problemDescription.generateFictiveAtomicInformation(prec, suiv)    # naissent Atomic et ne sont pas dans NonPI

                    if NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (prec, suiv)):
                            info_prec_suiv.termN = AS_LEAST_AS_GOOD_AS()
                    else:
                        info_prec_suiv.termAA = AS_LEAST_AS_GOOD_AS()

                    k_alternative_sequence.append(suiv)

                    k_explanation_sequence.append(info_prec_suiv)

                correspondingInfo.cause = [expl_info for expl_info in k_explanation_sequence]
                print()                                                                  # Sert a espacer les differents suppositions
                explanation_sequences_list.append(k_explanation_sequence)
            # print("+FOR", A())
        return True, returned_Info_list, best_alternative
