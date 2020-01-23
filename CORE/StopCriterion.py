from CORE.Dialog import Dialog
class StopCriterion:
    """ Classe (de base) modélisant un critère d'arrêt explicite de l'interaction."""

    def stop(self):
        return True


class DialogDurationStopCriterion(StopCriterion):
    """Critère d'arrêt lié à la durée des échanges."""
    def __init__(self, nbDialogsMax):
        self._nbDialogsMax = nbDialogsMax

    def stop(self):
        return self._nbDialogsMax == Dialog.NB
