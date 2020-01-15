from CORE.DA import DA
from CORE.InconsistencySolver import InconsistencySolverFactory
from CORE.InformationPicker import *
from CORE.ProblemDescription import *
from CORE.StopCriterion import *
from CORE.DM import *
from CORE.Recommendation import RecommendationWrapper, KBestRecommendation, KRankingRecommendation
from CORE.InformationStore import PI
if __name__ == "__main__" :
    mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria4.csv",
                                                  performanceTableFileName="CSVFILES/fullPerfTableTruncated.csv")
    dm = WS_DM("CSVFILES/DM_Utility_Function.csv") #
    limitDialogDuration = 16
    DA(problemDescription=mcda_problem_description, NonPI_InfoPicker=RandomPicker(0),
            stopCriterion=DialogDurationStopCriterion(limitDialogDuration), N_InfoPicker=RandomPicker(0),
            recommandationMaker=RecommendationWrapper(KBestRecommendation, 1),
            InconsistencySolverType=InconsistencySolverFactory().clearPIInconsistencySolver
            )
    DA().interactWith(dm)
    DA().show()

    ref_dialogDuration = Dialog.NB
    ref_recommendation = DA().recommendation

    nb_iterations = 64#32
    raison = 0.8
    LNBDIALOG = list()
    LSUCCES = list()
    for t in range(1, 11):
        noise_sigma = t/10.
        #print(noise_sigma)
        dmN = VNoisyWS_DM("CSVFILES/DM_Utility_Function.csv", noise_sigma, raison)

        NBDIALOG = list()
        nb_succes = 0
        for ite in range(nb_iterations):
            PI().clear()
            Dialog.NB = 0
            DA().interactWith(dmN)
            #print("nombre de questions : {}".format(Dialog.NB))
            NBDIALOG.append(Dialog.NB)
           # DA().show()
            if DA().recommendation == ref_recommendation:
                nb_succes += 1

        LNBDIALOG.append(np.mean(NBDIALOG))
        LSUCCES.append(100*nb_succes/nb_iterations)


    print(LNBDIALOG)
    print(LSUCCES)




    #print(CommitmentStore())