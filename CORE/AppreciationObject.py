from CORE.InformationStore import NonPI, PI, N, A
from CORE.Tools import NO_TERM
from CORE.Tools import colored_expression, AS_LEAST_AS_GOOD_AS, NOT_AS_LEAST_AS_GOOD_AS
from CORE.NecessaryPreference import NecessaryPreference
from gurobipy import GRB
from CORE.Tools import ROUNDED_NUMBER_OF_DECIMALS
import numpy as np
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

    def number_of_pro_arguments(self):
        return np.count_nonzero((np.array(self.alternative1.attributeLevelsList) - np.array(self.alternative2.attributeLevelsList)) == 1)

    def number_of_con_arguments(self):
        return np.count_nonzero((np.array(self.alternative2.attributeLevelsList) - np.array(self.alternative1.attributeLevelsList)) == 1)

    def pro_arguments_set(self):
        array_dif = np.array(self.alternative1.attributeLevelsList) - np.array(self.alternative2.attributeLevelsList)
        return set([i for i in range(len(array_dif)) if array_dif[i] == 1])

    def con_arguments_set(self):
        array_dif = np.array(self.alternative2.attributeLevelsList) - np.array(self.alternative1.attributeLevelsList)
        return set([i for i in range(len(array_dif)) if array_dif[i] == 1])

    def is_disjointed(self):
        for b1, b2 in zip(self.alternative2.attributeLevelsList, self.alternative1.attributeLevelsList):
            if b1 == b2 == 1:
                return False
        return True

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

    def is_necessary(self, mcda_problemDescription=None, Relation=None):
        return NecessaryPreference.adjudicate(mcda_problemDescription, Relation, (self.alternative1, self.alternative2))

class TransitiveObject(AppreciationObject):
    def __init__(self, alternativeD, alternatived):
        AppreciationObject.__init__(self, alternativeD, alternatived)

    def __getattr__(self, item):
        return AS_LEAST_AS_GOOD_AS()

    def __str__(self):
        return AppreciationObject.__str__(self)

    def pairwise_max_regret(self, gurobi_model_with_PI_constraints, varDict):
        objective = - AppreciationObject.linear_expr(self, varDict)
        gurobi_model_with_PI_constraints.setObjective(objective, GRB.MAXIMIZE)
        gurobi_model_with_PI_constraints.update()
        gurobi_model_with_PI_constraints.optimize()
        return round(gurobi_model_with_PI_constraints.objVal, ROUNDED_NUMBER_OF_DECIMALS)

class AInformation(AppreciationObject):
    # 20/06/2021
    """Classe modélisant une paire d'alternatives supposee vraie par le DA
     : l'information correspondante se trouve
        donc dans N ou NonPI """
    def __init__(self, information, alternative1, alternative2):
        """ Information * Alternative² --> NoneType
        Hyp : alternative1.id < alternative2.id
        le paramètre information est la 'capsule' enveloppant
         la paire d'alternative."""
        A().add(information)
        AppreciationObject.__init__(self, alternative1, alternative2)
        self._termA = NO_TERM()

    def getTermA(self):
        return self._termA

    def setTermA(self, v):
        self._termA = v

    termA = property(getTermA, setTermA)

    def __str__(self):
        return AppreciationObject.__str__(self)
        # symb1, symb2 = colored_expression(self.alternative1.symbolicName, self.alternative2.symbolicName)
        # return "[{:>2}] : {} {} {} : [{:>2}]".format(self.alternative1.id, symb1, self.term, symb2,
        #                                              self.alternative2.id)


    term = property(getTermA)

    def _getCorrespondingObject(self):
        if self._termA is AS_LEAST_AS_GOOD_AS():
            return self.alternative1, self.alternative2
        elif self._termA is NOT_AS_LEAST_AS_GOOD_AS():
            return self.alternative2, self.alternative1

    dominanceObject = property(fget=_getCorrespondingObject)
