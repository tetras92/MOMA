class InformationPicker:
    pass


class DifficultyLevelPicker(InformationPicker):
    def __init__(self, reverse=False):
        self._reverse = reverse

    def pick(self, store):
        storeCopy = [info for info in store]
        storeCopy.sort(key=lambda x: x.difficultyLevel, reverse=self._reverse)
        return storeCopy[0]


import random as rdm


class RandomPicker(InformationPicker):
    def __init__(self, seedValue=None):
        self._generator = rdm.Random()
        if not seedValue is None:
            self._generator.seed(seedValue)

    def pick(self, store):
        storeSize = len(store)
        return store[self._generator.randrange(storeSize)]

class DiscoveryPicker(RandomPicker):
    def __init__(self, seedValue=None):
        RandomPicker.__init__(self, seedValue)
        self.alternativesSet = set()

    def pick(self, store):
        storeCopy = [info for info in store]
        rdm.shuffle(storeCopy)
        for info in storeCopy:
            if info.alternative1 not in self.alternativesSet \
                    and info.alternative2 not in self.alternativesSet:
                self.alternativesSet.add(info.alternative1)
                self.alternativesSet.add(info.alternative2)
                return info

        for info in storeCopy:
            if info.alternative1 not in self.alternativesSet \
                    or info.alternative2 not in self.alternativesSet:
                self.alternativesSet.add(info.alternative1)
                self.alternativesSet.add(info.alternative2)
                return info
        infoToPick = RandomPicker.pick(self, store)
        self.alternativesSet.add(infoToPick.alternative1)
        self.alternativesSet.add(infoToPick.alternative2)

        return infoToPick

class DeterministicPicker(InformationPicker):
    def __init__(self):
        # self.L = [(57, 60), (45, 51), (46, 53), (27, 58), (43, 54), (30, 39), (23, 29), (15, 30), (46, 54), (46, 57), (27, 45), (57, 58), (43, 45), (39, 43)] #(23, 58)
        self.L = [(53, 58), (23, 46), (29, 30), (43, 53)] #(39, 58)
        # self.L = [(15, 23), (15, 27), (15, 29), (15, 30), (15, 39), (15, 43), (15, 45), (23, 27),
        #           (45, 58), (15, 58), (45, 54), (15, 54),
        #           (23, 58), (23, 43),
        #           (23, 57),
        #           (29, 43), (29, 39),
        #           (29, 54), (29, 58), (30, 45), (39, 58), (43, 53), (53, 58)]
        self.L.reverse()


    def pick(self, store):
        elmt = self.L.pop()
        for info in store:
            # print(info, elmt)
            if info.alternative1.id == elmt[0] and info.alternative2.id == elmt[1]:
                return info



if __name__ == "__main__":
    r1 = RandomPicker(0)
    r2 = RandomPicker(1)
    L1 = list()
    for i in range(5):
        L1.append(r1.pick(5))
    L2 = list()
    for j in range(5):
        L2.append(r2.pick(5))

    print(L1)
    print(L2)
