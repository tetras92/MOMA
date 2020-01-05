from CORE.Dialog import Dialog
class Commitment:
    def __init__(self, ao, term):
        self._ao = ao
        self._term = term
        self.date = Dialog.NB
        self._id = ao.id
        CommitmentStore().add(self)

    def getId(self):
        return self._id

    id = property(getId)


from CORE.decorators import singleton
@singleton
class CommitmentStore():
    def __init__(self):
        self._store = dict()

    def add(self, commitment):
        if commitment.id not in self._store:
            self._store[commitment.id] = set()
        self._store[commitment.id].add(commitment)