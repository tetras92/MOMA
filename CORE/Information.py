from CORE.AppreciationObject import PairwiseInformation, NInformation, PInformation
from CORE.InformationStore import NonPI, N
from CORE.Commitment import *

class Information:
    NB_OBJECT = 0
    def __init__(self, alternative1, alternative2):
        self.o = PairwiseInformation(self, alternative1, alternative2)
        self.alternative1 = alternative1
        self.alternative2 = alternative2
        self._id = Information.NB_OBJECT

    def getId(self):
        return self._id

    id = property(getId)
    def _nUpgrade(self, v):
        NonPI().remove(self)
        self.o = NInformation(self, self.alternative1, self.alternative2)
        self.o.termN = v

    def _pUpgrade(self, v):
        if isinstance(self.o, NInformation):
            if self.o.termN != v: #DM ne valide pas la valeur inférée
                CommitmentStore().add(InvalidationCommitment(self, v))
                return
            CommitmentStore().add(ValidationCommitment(self, v))
            N().remove(self)

        elif isinstance(self.o, PairwiseInformation):
            CommitmentStore().add(AnswerCommitment(self, v))
            NonPI().remove(self)

        self.o = PInformation(self, self.alternative1, self.alternative2)
        self.o.termP = v

    def _pdowngrade(self):
        pass

    def setTermN(self, v):
        self._nUpgrade(v)

    def setTermP(self, v):
        self._pUpgrade(v)

    def getTermP(self):
        return self.o.termP

    termN = property(None, setTermN)
    termP = property(getTermP, setTermP)


    def __str__(self):
        return self.o.__str__()


    def linear_expr(self, VarDict):
        return (self.alternative1.linear_expr(VarDict) - self.alternative2.linear_expr(VarDict))