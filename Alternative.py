import numpy as np

class Alternative:
    def __init__(self, idAlt, attributesList, attributeLevelsList):
        self._idAlt = idAlt
        self._attributesList = attributesList
        self._attributeLevelsList = attributeLevelsList

    def getId(self):
        return self._idAlt
    def getAttributesList(self):
        return self._attributesList
    def getAttributeLevelsList(self):
        return self._attributeLevelsList

    attributesList = property(getAttributesList)
    attributeLevelsList = property(getAttributeLevelsList)
    id = property(getId)


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
        return "[{:>2}] : {}".format(str(self._idAlt), self._attributesList)
    def __repr__(self):
        return "[{:>2}] : {}".format(str(self._idAlt), self._attributesList)