import numpy as np
from gurobipy import quicksum
class Alternative:
    """Classe modélisant une alternative.
        Ses attributs :
        - idAlt : son identifiant (un entier).
        - attributesList : la liste ordonnée de ses attributs suivant les critères.
        - attributeLevelsList : liste des évaluations numériques de chacun de ses attributs.
        - symbolicName : nom symbolique de l'alternative."""

    def __init__(self, idAlt, attributesList, attributeLevelsList, altListOfSymbols):
        self._idAlt = idAlt
        self._attributesList = attributesList
        self._attributeLevelsList = attributeLevelsList
        self._symbolicName = ''.join(altListOfSymbols)

    def getId(self):
        return self._idAlt
    def getAttributesList(self):
        return self._attributesList
    def getAttributeLevelsList(self):
        return self._attributeLevelsList
    def getSymbolicName(self):
        return self._symbolicName

    attributesList = property(getAttributesList)
    attributeLevelsList = property(getAttributeLevelsList)
    id = property(getId)
    symbolicName = property(fget=getSymbolicName)

    def linear_expr(self, VarDict):
        """Dict[str : gurobiVariable] --> LinExpr
        retourne l'expression linéaire correspondant à l'alternative"""
        return quicksum([VarDict[attr] for attr in self._attributesList])

    # -- Différentes méthodes spéciales pour calculer les dominances de Pareto -- #

    def __eq__(self, other):
        return all(np.array(self._attributeLevelsList) == np.array(other.attributeLevelsList))

    def __lt__(self, other):
        return all(np.array(self._attributeLevelsList) <= np.array(other.attributeLevelsList)) \
               and any(np.array(self._attributeLevelsList) < np.array(other.attributeLevelsList))

    def __gt__(self, other):
        return other < self

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def __str__(self):
        return "[{:>2}] : {}".format(str(self._idAlt), self._symbolicName)

    def __repr__(self):
        return "[{:>2}] : {}".format(str(self._idAlt), self._symbolicName)

    def __hash__(self):
        return int("".join([str(b) for b in self.attributeLevelsList]), 2)
        # return self._idAlt
