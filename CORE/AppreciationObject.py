from CORE.InformationStore import NonPI, PI, N
from CORE.Tools import NO_TERM
from CORE.Tools import colored_expression, AS_LEAST_AS_GOOD_AS, NOT_AS_LEAST_AS_GOOD_AS


class AppreciationObject:
    """Classe de base modélisation une paire d'alternatives"""
    def __init__(self, alternative1, alternative2):
        self.alternative1 = alternative1
        self.alternative2 = alternative2

    def linear_expr(self, VarDict):
        return (self.alternative1.linear_expr(VarDict) - self.alternative2.linear_expr(VarDict))

    def __str__(self):
        symb1, symb2 = colored_expression(self.alternative1.symbolicName, self.alternative2.symbolicName)
        return "[{:>2}] : {} {} {} : [{:>2}]".format(self.alternative1.id, symb1, self.term, symb2,
                                                     self.alternative2.id)

class PairwiseInformation(AppreciationObject):
    """Classe modélisant une paire d'alternatives sur
    laquelle ne s'est pas encore (re)prononcé le DM :
    l'information correspndante se trouve donc dans NonPI"""

    def __init__(self, information, alternative1, alternative2):
        """ Information * Alternative² --> NoneType
        Hyp : alternative1.id < alternative2.id
        le paramètre information est la 'capsule' enveloppant
         la paire d'alternative."""
        NonPI().add(information)
        AppreciationObject.__init__(self, alternative1, alternative2)


    def linear_expr(self, VarDict):
        return AppreciationObject.linear_expr(self, VarDict)

    def __str__(self):
        symb1, symb2 = colored_expression(self.alternative1.symbolicName, self.alternative2.symbolicName)
        return "[{:>2}] : {} {} {} : [{:>2}]".format(self.alternative1.id, symb1, NO_TERM(), symb2, self.alternative2.id)

    def __repr__(self):
        return self.__str__()



class NInformation(AppreciationObject):
    """Classe modélisant une paire d'alternatives induite par calcul
        de la relation nécessaire : l'information correspondante se trouve
        donc dans N"""
    def __init__(self, information, alternative1, alternative2):
        """ Information * Alternative² --> NoneType
        Hyp : alternative1.id < alternative2.id
        le paramètre information est la 'capsule' enveloppant
         la paire d'alternative."""
        N().add(information)
        AppreciationObject.__init__(self, alternative1, alternative2)
        self._termN = NO_TERM()

    def getTermN(self):
        return self._termN

    def setTermN(self, v):
        self._termN = v

    termN = property(getTermN, setTermN)

    def __str__(self):
        return AppreciationObject.__str__(self)
        # symb1, symb2 = colored_expression(self.alternative1.symbolicName, self.alternative2.symbolicName)
        # return "[{:>2}] : {} {} {} : [{:>2}]".format(self.alternative1.id, symb1, self.term, symb2,
        #                                              self.alternative2.id)


    term = property(getTermN)

    def _getCorrespondingObject(self):
        if self._termN is AS_LEAST_AS_GOOD_AS():
            return self.alternative1, self.alternative2
        elif self._termN is NOT_AS_LEAST_AS_GOOD_AS():
            return self.alternative2, self.alternative1

    dominanceObject = property(fget=_getCorrespondingObject)

class PInformation(AppreciationObject):
    """Classe modélisant une paire d'alternatives sur laquelle s'est
        prononcé le décideur: l'information correspondante se trouve
        donc dans PI"""
    def __init__(self, information, alternative1, alternative2):
        """ Information * Alternative² --> NoneType
        Hyp : alternative1.id < alternative2.id
        le paramètre information est la 'capsule' enveloppant
         la paire d'alternative."""
        PI().add(information)
        AppreciationObject.__init__(self, alternative1, alternative2)
        self._termP = NO_TERM()


    def getTermP(self):
        return self._termP

    def setTermP(self, v):
        self._termP = v

    termP = property(getTermP, setTermP)

    def __str__(self):
        return AppreciationObject.__str__(self)
        # symb1, symb2 = colored_expression(self.alternative1.symbolicName, self.alternative2.symbolicName)
        # return "[{:>2}] : {} {} {} : [{:>2}]".format(self.alternative1.id, symb1, self.term, symb2,
        #                                              self.alternative2.id)

    def linear_expr(self, VarDict):
        return AppreciationObject.linear_expr(self, VarDict)

    term = property(getTermP)


class SwapObject(AppreciationObject):
    def __init__(self, alternativeD, alternatived):
        AppreciationObject.__init__(self, alternativeD, alternatived)

    def __getattr__(self, item):
        return AS_LEAST_AS_GOOD_AS()

    def __str__(self):
        return AppreciationObject.__str__(self)

class TransitiveObject(AppreciationObject):
    def __init__(self, alternativeD, alternatived):
        AppreciationObject.__init__(self, alternativeD, alternatived)

    def __getattr__(self, item):
        return AS_LEAST_AS_GOOD_AS()

    def __str__(self):
        return AppreciationObject.__str__(self)


