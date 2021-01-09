from CORE.InformationStore import NonPI, N, PI
from CORE.ProblemDescription import *
from CORE.Tools import AS_LEAST_AS_GOOD_AS, NOT_AS_LEAST_AS_GOOD_AS
from CORE.Explanation import Explain
if __name__ == "__main__":

    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria9.csv",
                                                  performanceTableFileName="CSVFILES/PerfTable9.csv")

    # Dominance Relation To add to PI()
    R = list([(45, 12), (6, 1), (6, 2), (45, 3), (56, 3), (46, 3), (17, 48), (28, 59), (39, 67)])
    # Pairwise Comparison to Explain
    E = list([(123, 456)])
    print(mcda_problem_description)
    for info in [elem for elem in NonPI()]:
        if (info.alternative1.id, info.alternative2.id) in R:
            info.termP = AS_LEAST_AS_GOOD_AS()
        elif (info.alternative2.id, info.alternative1.id) in R:
            info.termP = NOT_AS_LEAST_AS_GOOD_AS()

    print("============= ", PI().getRelation()["dominanceRelation"])
    N().update(mcda_problem_description, **PI().getRelation())

    # Explanation Engine
    for ExplanationEngine in [Explain.general_k_vs_1_MixedExplanation, Explain.general_1_vs_k_MixedExplanation]:
        print(ExplanationEngine)
        for info in N():
            ok, text = False, ""
            if (info.alternative1.id, info.alternative2.id) in E:
                ok, text = ExplanationEngine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(info.alternative1, info.alternative2))
            elif (info.alternative2.id, info.alternative1.id) in E:
                ok, text = ExplanationEngine(mcda_problem_description, PI().getRelation()["dominanceRelation"], object=(info.alternative2, info.alternative1))
            if ok:
                print(text)
