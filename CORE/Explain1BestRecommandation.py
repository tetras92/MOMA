from CORE.ProblemDescription import *
from CORE.DM import *

from CORE.PLNE_for_Delta11_decomposition import decompose as decompose0
from CORE.PLNE_for_Delta1m_decomposition import decompose as decompose1
from CORE.PLNE_for_Deltam1_decomposition import decompose as decompose2
from CORE.PLNE_for_Delta1m_m1_decomposition import decompose as decompose3

from CORE.AppreciationObject import AppreciationObject

def explain(problem_description, dm, language=3):
    plne_function_to_use = None
    W_vector = dm.utilitiesList
    W_dict = {k: W_vector[k] for k in range(len(W_vector))}

    if language == 0:
        plne_function_to_use = decompose0
    elif language == 1:
        plne_function_to_use = decompose1
    elif language == 2:
        plne_function_to_use = decompose2
    else:
        plne_function_to_use = decompose3


    OrderedListOfAlternatives = [None] + dm.alternatives_ordering_list(problem_description)

    print(OrderedListOfAlternatives)
    ExplanationsOfPairs = dict()
    for j in range(2, problem_description.numberOfAlternatives + 1):
        AlternativeJ = OrderedListOfAlternatives[j]
        success_j = False
        for i in range(1, j):
            AlternativeI = OrderedListOfAlternatives[i]
            AppreciationObject_IJ = AppreciationObject(AlternativeI, AlternativeJ)
            pro_argument_set, con_argument_set = AppreciationObject_IJ.pro_arguments_set(), AppreciationObject_IJ.con_arguments_set()
            print(pro_argument_set, con_argument_set)
            feasible, details = plne_function_to_use(pro_argument_set, con_argument_set, W_dict)
            if feasible:
                success_j = True
                ExplanationsOfPairs[AppreciationObject_IJ] = details
                break
        if not success_j:
            print("Complete Explanation of Recommendation INFEASIBLE !!!")
            return False, None

    # print(ExplanationsOfPairs)
    Explanation_text = ""
    for explanandum, explanans in ExplanationsOfPairs.items():
        Explanation = list()
        calculus = list()
        ListAttributeLevelsList = list()
        ListAttributeLevelsList.append(explanandum.alternative1)
        print(explanans)
        for i, j in explanans:
            prec = ListAttributeLevelsList[-1]
            suiv = problem_description.getSwapObject(prec, (set(i), set(j)))
            Explanation.append(suiv)
            calculus.append(f'\t(as --{i}-- {round(sum([W_dict[i_component] for i_component in set(i)]), 5)} >= {round(sum([W_dict[j_component] for j_component in set(j)]), 5)} --{j}-- )')
            ListAttributeLevelsList.append(suiv.alternative2)

        Explanation_text += "\n" + str(explanandum) + "\tbecause \n"
        for i in range(len(Explanation)):
            elm = str(Explanation[i]) + calculus[i]
            Explanation_text += "\t" + elm + "\n"

    print("Recommendation : {}".format(OrderedListOfAlternatives[1]))
    print(Explanation_text)
    return True, Explanation_text

if __name__ == "__main__":
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria7.csv",
                                                  # performanceTableFileName="CSVFILES/kr-v2-7.csv")
                                                  performanceTableFileName="CSVFILES/test-alternatives-7.csv")
    # print(mcda_problem_description)
    dm = WS_DM("CSVFILES/DM-kr-v2-7.csv")
    explain(mcda_problem_description, dm, 3)
