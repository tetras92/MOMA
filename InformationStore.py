from decorators import singleton

class InformationStore:
    def __init__(self):
        self._store = list()
    pass

@singleton
class PI(InformationStore):
    def __init__(self):
        self._store = list()
        pass #InformationStore.__init__()

    def add(self, information):
        self._store.append(information)


    def __len__(self):
        return len(self._store)

@singleton
class NonPI(InformationStore):
    def __init__(self, aoPicker):
        #InformationStore.__init__()
        self._store = list()
        self._aoPicker = aoPicker

    def __len__(self):
        return len(self._store)

    def pick(self):
        indexToPick = self._aoPicker.pickIndex(len(self))
        return self._store.pop(indexToPick)

    def add(self, information):
        self._store.append(information)


    def __repr__(self):
        s = ""
        for elm in self._store:
            s += str(elm) + "\n"
        return s
@singleton
class N(InformationStore):
    def __init__(self):
        #InformationStore.__init__()
        pass

