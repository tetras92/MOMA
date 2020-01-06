from CORE.Commitment import *
from CORE.ComparisonTerm import ComparisonTerm
from CORE.InformationStore import NonPI, PI, N


class AppreciationObject:
    def __init__(self, alternative1, alternative2):
        self.alternative1 = alternative1
        self.alternative2 = alternative2



class PairwiseInformation(AppreciationObject):
    #NB_OF_OBJECTS = 0
    def __init__(self, infoConteneur, alternative1, alternative2): #infoConteneur : changer nom dès que possible
        """alternative1.id < alternative2.id"""
        NonPI().add(infoConteneur)
        self.conteneur = infoConteneur
        AppreciationObject.__init__(self, alternative1, alternative2)


    def getId(self):
        return self._id


    def __str__(self):
        return "{} {} {}".format(self.alternative1, ComparisonTerm.NO_TERM, self.alternative2)

    def __repr__(self):
        return self.__str__()



class NInformation(AppreciationObject):
    def __init__(self,infoConteneur, alternative1, alternative2): #infoConteneur : changer nom dès que possible
        """alternative1.id < alternative2.id"""
        N().add(infoConteneur)
        AppreciationObject.__init__(self, alternative1, alternative2)
        self._termN = ComparisonTerm.NO_TERM

    def getTermN(self):
        return self._termN
    def setTermN(self, v):
        self._termN = v
        #CommitmentStore().add(ValidationCommitment(self, v))

    termN = property(getTermN, setTermN)

    def __str__(self):
        return "{} {} {}".format(self.alternative1, self._termN, self.alternative2)




class PInformation(AppreciationObject):
    def __init__(self, infoConteneur, alternative1, alternative2): #infoConteneur : changer nom dès que possible
        """alternative1.id < alternative2.id"""
        PI().add(infoConteneur)
        self._conteneur = infoConteneur
        AppreciationObject.__init__(self, alternative1, alternative2)
        self._termP = ComparisonTerm.NO_TERM


    def getTermP(self):
        return self._termP
    def setTermP(self, v):
        self._termP = v
        CommitmentStore().add(AnswerCommitment(self._conteneur, v))
        print("\tDM answers {}".format(v))

    termP = property(getTermP, setTermP)

    def __str__(self):
        return "{} {} {}".format(self.alternative1, self._termP, self.alternative2)

