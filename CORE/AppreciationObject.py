from CORE.ComparisonTerm import ComparisonTerm
from CORE.InformationStore import NonPI, PI, N
from CORE.Tools import colored_expression, NO_TERM

class AppreciationObject:
    """Classe de base modélisation une paire d'alternatives"""
    def __init__(self, alternative1, alternative2):
        self.alternative1 = alternative1
        self.alternative2 = alternative2

    def linear_expr(self, VarDict):
        return (self.alternative1.linear_expr(VarDict) - self.alternative2.linear_expr(VarDict))


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

    def linear_expr(self, VarDict):
        return AppreciationObject.linear_expr(self, VarDict)
