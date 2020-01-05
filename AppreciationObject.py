from Commitment import *
from ComparisonTerm import ComparisonTerm
from InformationStore import NonPI, PI


class AppreciationObject:
    pass

class PairwiseComparisonObject(AppreciationObject):
    NB_OF_OBJECTS = 0
    def __init__(self, alternative1, alternative2):
        """alternative1.id < alternative2.id"""
        NonPI().add(self)
        self.alternative1 = alternative1
        self.alternative2 = alternative2
        self._termN = ComparisonTerm.NO_TERM          # à remplacer par mieux
        self._termP = ComparisonTerm.NO_TERM
        self._id = PairwiseComparisonObject.NB_OF_OBJECTS
        PairwiseComparisonObject.NB_OF_OBJECTS += 1

    def getId(self):
        return self._id

    id = property(getId)

    def getTermP(self):
        return self._termP
    def setTermP(self, v):
        self._termP = v
        PI().add(self)
        CommitmentStore().add(Commitment(self, v))
        print(" \tDM answers {}".format(v))

    def getTermN(self):
        return self._termN
    def setTermN(self, v):
        self._termN = v
    termP = property(getTermP, setTermP)
    termN = property(getTermN, setTermN)

    def __str__(self):
        term = self._termP
        if self._termN != ComparisonTerm.NO_TERM:
            term = self._termN
        return "{} {} {}".format(self.alternative1, term, self.alternative2)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.alternative1 == other.alternative1 and self.alternative2 == other.alternative2

    def linear_expr_and_term(self, VarDict):
        return (self.alternative1.linear_expr(VarDict) - self.alternative2.linear_expr(VarDict), self._termP)
