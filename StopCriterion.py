class StopCriterion:
    pass
from Dialog import Dialog
class DialogDurationStopCriterion(StopCriterion):
    def __init__(self, nbDialogsMax):
        self._nbDialogsMax = nbDialogsMax

    def stop(self):
        return self._nbDialogsMax == Dialog.NB
