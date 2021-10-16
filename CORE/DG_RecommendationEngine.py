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

    # def process(self):
    #     best_value = 0
    #     best_alternative = None
    #     swaps_used = None
    #     other_candidates = None
    #     unexplained_challengers = None
    #     dispensed_from_explanation_number = 0
    #     for candidate in self._problemDescription:
    #         other_alt = [alt for alt in self._problemDescription.alternativesSet if alt != candidate]
    #         can_be_best, number_of_pwc_explained, pareto_dominance, details = ExplanationBasedElicitation.adjudicate(self._problemDescription, candidate, other_alt, self._dominanceRelation)
    #         challengers_unexplained = list()
    #         if can_be_best:
    #             for k in range(len(details)):
    #                 swaps_list = details[k]
    #                 if len(swaps_list) == 0 and not pareto_dominance[k]:   # non expliqué
    #                     challengers_unexplained.append(other_alt[k])
    #                     if NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (candidate, other_alt[k])):
    #                         dispensed_from_explanation_number += 1
    #             value = number_of_pwc_explained / (len(details) - dispensed_from_explanation_number)
    #             if value > best_value:
    #                 best_value = value
    #                 best_alternative = candidate
    #                 # print("les candidats", best_alternative)
    #                 swaps_used = details
    #                 other_candidates = other_alt
    #                 unexplained_challengers = challengers_unexplained
    #
    #
    #     returned_AInfo_list = list()
    #     explanation_sequences_list = list()
    #
    #     if best_value == 1:
    #         for k in range(len(other_candidates)):
    #             challenger = other_candidates[k]
    #             correspondingInfo = self._problemDescription.dictOfInformation[(best_alternative, challenger)]
    #
    #             # transfert NonPI ==> N
    #             if (best_alternative, challenger) not in self._dominanceRelation and NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (best_alternative, challenger)):
    #                 if correspondingInfo.alternative1 == best_alternative:
    #                     correspondingInfo.termN = AS_LEAST_AS_GOOD_AS()
    #                 else:
    #                     correspondingInfo.termN = NOT_AS_LEAST_AS_GOOD_AS()
    #
    #             if correspondingInfo.alternative1 == best_alternative:
    #                 correspondingInfo.termA = AS_LEAST_AS_GOOD_AS()
    #             else:
    #                 correspondingInfo.termA = NOT_AS_LEAST_AS_GOOD_AS()
    #             returned_AInfo_list.append(correspondingInfo)
    #
    #             swaps_used_list = swaps_used[k]
    #             k_alternative_sequence = [best_alternative]
    #             k_explanation_sequence = list()
    #             if len(swaps_used_list) > 1:
    #                 for (i_, j_) in swaps_used_list:
    #                     i = i_ - 1
    #                     j = j_ - 1
    #                     prec = k_alternative_sequence[-1]
    #                     suiv = self._problemDescription.swap_translation(prec, ({i}, {j}))
    #                     # attention (15/07/2021) getInformation pourrait contenir un bug (constat lors de l'implem de WD-DLT11)
    #                     info_prec_suiv = self._problemDescription.getInformation(prec, suiv)
    #                     if (prec, suiv) not in self._dominanceRelation and NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (prec, suiv)):
    #                         if info_prec_suiv.alternative1 == prec:
    #                             info_prec_suiv.termN = AS_LEAST_AS_GOOD_AS()
    #                         else:
    #                             info_prec_suiv.termN = NOT_AS_LEAST_AS_GOOD_AS()
    #
    #                     k_alternative_sequence.append(suiv)
    #                     # attention
    #                     if info_prec_suiv.alternative1 == prec:
    #                         info_prec_suiv.termA = AS_LEAST_AS_GOOD_AS()
    #                     else:
    #                         info_prec_suiv.termA = NOT_AS_LEAST_AS_GOOD_AS()
    #
    #                     k_explanation_sequence.append(info_prec_suiv)
    #
    #             explanation_sequences_list.append(k_explanation_sequence)
    #         return True, returned_AInfo_list, best_alternative, explanation_sequences_list
    #
    #     return False, [self._problemDescription.dictOfInformation[(best_alternative, challenger)] for challenger in unexplained_challengers], best_alternative, None


    ### - Jeudi 14 octobre 2021 : tentative de maj de process : objectif : traiter indifféremment les comparaisons d'alternatives swaps natifs des comparaisons d'alternatives dont
                                                                          # la difficultyLevel est > 2.
    def process(self):
        best_value = 0
        best_alternative = None
        swaps_used = None
        other_candidates = None
        unexplained_challengers = None
        dispensed_from_explanation_number = 0

        L = list()
        for candidate in self._problemDescription:
            L.append(candidate)
        random.shuffle(L)
        for candidate in L:
        # for candidate in self._problemDescription:
            other_alt = [alt for alt in self._problemDescription.alternativesSet if alt != candidate]
            can_be_best, number_of_pwc_explained, pareto_dominance, details = ExplanationBasedElicitation.adjudicate(self._problemDescription, candidate, other_alt, self._dominanceRelation)
            challengers_unexplained = list()
            if can_be_best:
                for k in range(len(details)):
                    swaps_list = details[k]
                    if len(swaps_list) == 0 and not pareto_dominance[k]:   # non expliqué
                        challengers_unexplained.append(other_alt[k])
                        if NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (candidate, other_alt[k])):
                            dispensed_from_explanation_number += 1
                value = number_of_pwc_explained / (len(details) - dispensed_from_explanation_number)
                if value > best_value:
                    best_value = value
                    best_alternative = candidate
                    # print("les candidats", best_alternative)
                    swaps_used = details
                    other_candidates = other_alt
                    unexplained_challengers = challengers_unexplained
            # break                                                          # A RETIRER (DEBOGAGE)

        returned_AInfo_list = list()
        explanation_sequences_list = list()
        # print("SWAPS", other_candidates, swaps_used)
        print("\n\n\t\t***** DA thinking... *****\n")
        if best_value == 1:
            # print("\n\n***** DA thinking... *****{}\n".format(len(other_candidates)))
            for k in range(len(other_candidates)):
                challenger = other_candidates[k]
                correspondingInfo = self._problemDescription.dictOfInformation[(best_alternative, challenger)]
                isCorrespondingInfoNecessary = False
                # transfert NonPI ==> N
                # if (best_alternative, challenger) not in self._dominanceRelation and\
                if correspondingInfo not in PI() and\
                        NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (best_alternative, challenger)):
                    if correspondingInfo.alternative1 == best_alternative:
                        correspondingInfo.termN = AS_LEAST_AS_GOOD_AS()
                    else:
                        correspondingInfo.termN = NOT_AS_LEAST_AS_GOOD_AS()

                    isCorrespondingInfoNecessary = True

                elif correspondingInfo in PI():
                    isCorrespondingInfoNecessary = correspondingInfo.termPConfirm  # always True

                else:
                    if correspondingInfo.alternative1 == best_alternative:
                        correspondingInfo.termA = AS_LEAST_AS_GOOD_AS()
                    else:
                        correspondingInfo.termA = NOT_AS_LEAST_AS_GOOD_AS()

                returned_AInfo_list.append(correspondingInfo)


                swaps_used_list = swaps_used[k]
                k_alternative_sequence = [best_alternative]
                k_explanation_sequence = list()

                if not isCorrespondingInfoNecessary:
                    for (i_, j_) in swaps_used_list:
                        prec = k_alternative_sequence[-1]
                        i = i_ - 1
                        if j_ == EMPTYSET:
                            suiv = self._problemDescription.pareto_translation(prec, i)
                        else :
                            j = j_ - 1
                            suiv = self._problemDescription.swap_translation(prec, ({i}, {j}))

                        info_prec_suiv = self._problemDescription.generateFictiveAtomicInformation(prec, suiv)

                        if NecessaryPreference.adjudicate(self._problemDescription, self._dominanceRelation, (prec, suiv)):
                                info_prec_suiv.termN = AS_LEAST_AS_GOOD_AS()

                        # elif (prec, suiv) in self._dominanceRelation:
                        #     raise Exception("peut arriver ????")

                        else:
                            info_prec_suiv.termAA = AS_LEAST_AS_GOOD_AS()

                        k_alternative_sequence.append(suiv)

                        k_explanation_sequence.append(info_prec_suiv)
                    print() # Sert a espacer les differents suppositions

                explanation_sequences_list.append(k_explanation_sequence)
            return True, returned_AInfo_list, best_alternative, explanation_sequences_list

        print("\t\t***** DA : there is no explainable potential 1-best alternative ! *****\n")
        return False, [self._problemDescription.dictOfInformation[(best_alternative, challenger)] for challenger in unexplained_challengers], best_alternative, None


