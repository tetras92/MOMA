class AOPicker:
    pass

import random as rdm
class RandomPicker(AOPicker):
    def __init__(self, seedValue=None):
        self._generator = rdm.Random()
        if not seedValue is None:
            self._generator.seed(seedValue)

    def pickIndex(self, storeSize):
        return self._generator.randrange(storeSize)


if __name__ == "__main__" :
    r1 = RandomPicker(0)
    r2 = RandomPicker(1)
    L1 = list()
    for i in range(5):
        L1.append(r1.pickIndex(5))
    L2 = list()
    for j in range(5):
        L2.append(r2.pickIndex(5))

    print(L1)
    print(L2)