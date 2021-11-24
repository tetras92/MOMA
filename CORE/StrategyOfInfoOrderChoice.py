import random

from CORE.Tools import AS_LEAST_AS_GOOD_AS, NOT_AS_LEAST_AS_GOOD_AS


class RestorationOfInfoStrategy:
    def __init__(self, dm):
        self._dm = dm

    def list_order_values(self, infoList):
        return infoList

class WrongAssertionFirstStrategy:
    def __init__(self, dm):
        self._dm = dm

    def list_order_values(self, infoList):
        returnedList = list()
        for info in infoList:
            valueOfAlternative1 = self._dm.evaluateAlternative(info.alternative1)
            valueOfAlternative2 = self._dm.evaluateAlternative(info.alternative2)
            if (valueOfAlternative1 >= valueOfAlternative2 and info.term is AS_LEAST_AS_GOOD_AS()) or (valueOfAlternative1 <= valueOfAlternative2 and info.term is NOT_AS_LEAST_AS_GOOD_AS()):
                returnedList.append(info)
            else:
                returnedList = [info] + returnedList

        return returnedList

class RandomInfoListStrategy:
    def __init__(self, dm):
        self._dm = dm

    def list_order_values(self, infoList):
        infoListCopy = [info for info in infoList]
        random.shuffle(infoListCopy)
        return infoListCopy
