from CORE.Dialog import Dialog
class Commitment:
    def __init__(self, info, term):
        self.info = info
        self._term = term
        self.date = Dialog.NB
        self._id = info.id
        CommitmentStore().add(self)

    def getId(self):
        return self._id

    id = property(getId)

class AnswerCommitment(Commitment):
    def __init__(self, ao, term):
        Commitment.__init__(self,ao, term)

class ValidationCommitment(Commitment):
    def __init__(self, ao, term):
        Commitment.__init__(self, ao, term)

from CORE.decorators import singleton
@singleton
class CommitmentStore():
    def __init__(self):
        self._store = dict()

    def add(self, commitment):
        if commitment.id not in self._store:
            self._store[commitment.id] = set()
        self._store[commitment.id].add(commitment)