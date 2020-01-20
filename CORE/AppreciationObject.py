from CORE.ComparisonTerm import ComparisonTerm
from CORE.InformationStore import NonPI, PI, N
from CORE.Tools import colored_expression

class AppreciationObject:
    def __init__(self, alternative1, alternative2):
        self.alternative1 = alternative1
        self.alternative2 = alternative2

class PairwiseInformation(AppreciationObject):
    def __init__(self, infoConteneur, alternative1, alternative2): #infoConteneur : changer nom dès que possible
        """alternative1.id < alternative2.id"""
        NonPI().add(infoConteneur)
        AppreciationObject.__init__(self, alternative1, alternative2)



    def __str__(self):
        symb1, symb2 = colored_expression(self.alternative1.symbolicName, self.alternative2.symbolicName)
        return "[{:>2}] : {} {} {} : [{:>2}]".format(self.alternative1.id, symb1, ComparisonTerm.NO_TERM, symb2, self.alternative2.id)

    def __repr__(self):
        return self.__str__()



class NInformation(AppreciationObject):
    def __init__(self, infoConteneur, alternative1, alternative2): #infoConteneur : changer nom dès que possible
        """alternative1.id < alternative2.id"""
        N().add(infoConteneur)
        AppreciationObject.__init__(self, alternative1, alternative2)
        self._termN = ComparisonTerm.NO_TERM

    def getTermN(self):
        return self._termN

    def setTermN(self, v):
        self._termN = v

    termN = property(getTermN, setTermN)

    def __str__(self):
        symb1, symb2 = colored_expression(self.alternative1.symbolicName, self.alternative2.symbolicName)
        return "[{:>2}] : {} {} {} : [{:>2}]".format(self.alternative1.id, symb1, self._termN, symb2,
                                                     self.alternative2.id)




class PInformation(AppreciationObject):
    def __init__(self, infoConteneur, alternative1, alternative2): #infoConteneur : changer nom dès que possible
        """alternative1.id < alternative2.id"""
        PI().add(infoConteneur)
        AppreciationObject.__init__(self, alternative1, alternative2)
        self._termP = ComparisonTerm.NO_TERM


    def getTermP(self):
        return self._termP

    def setTermP(self, v):
        self._termP = v

    termP = property(getTermP, setTermP)

    def __str__(self):
        symb1, symb2 = colored_expression(self.alternative1.symbolicName, self.alternative2.symbolicName)
        return "[{:>2}] : {} {} {} : [{:>2}]".format(self.alternative1.id, symb1, self._termP, symb2,
                                                     self.alternative2.id)

