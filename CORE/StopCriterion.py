from CORE.Commitment import CommitmentStore
from CORE.Dialog import Dialog


class StopCriterion:
    """ Classe (de base) modélisant un critère d'arrêt explicite de l'interaction."""

    def stop(self):
        return True

    def reset(self):
        pass

class DialogDurationStopCriterion(StopCriterion):
    """Critère d'arrêt lié à la durée des échanges."""
    def __init__(self, nbDialogsMax):
        self._nbDialogsMax = nbDialogsMax

    def stop(self):
        return self._nbDialogsMax == Dialog.NB

    def reset(self):
        StopCriterion.reset(self)

class DMVolatilityStopCriterion(StopCriterion):
    """Critère d'arrêt lié au traque de la versalité du DM"""
    def __init__(self, nbMaxOpinionOnTheSameInfo):
        self._nbMaxOpinionOnTheSameInfo = nbMaxOpinionOnTheSameInfo

    def stop(self):
        for info, LOfCommitment in CommitmentStore().info_store.items():
            if len(LOfCommitment) == self._nbMaxOpinionOnTheSameInfo:
                print("Stop because of {}".format(info))
                return True
        return False

    def reset(self):
        StopCriterion.reset(self)

