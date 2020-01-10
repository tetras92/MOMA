from CORE.decorators import singleton

class InconsistencySolver:
    def __init__(self, infoStore):
        self._store = infoStore

    def solve(self):
        pass

class ClearPIInconsistencySolver(InconsistencySolver):
    def __init__(self, infoStore):
        InconsistencySolver.__init__(self, infoStore)

    def solve(self):
        self._store.clear()

@singleton
class InconsistencySolverFactory():

    clearPIInconsistencySolver = ClearPIInconsistencySolver
    emptyInconsistencySolver = InconsistencySolver