from CORE.ComparisonTerm import *
from CORE.Dialog import Dialog


class Commitment:
    def __init__(self, info, term):
        self.info = info
        self.term = term
        self.date = Dialog.NB
        self._id = info.id
        #CommitmentStore().add(self)

    def getId(self):
        return self._id

    id = property(getId)


class AnswerCommitment(Commitment):
    def __init__(self, info, term):
        Commitment.__init__(self, info, term)
        #print("\tDM answers {}".format(term))

    def __str__(self):
        return "{} at {} :\n\t{} {} {}\n\tDM answers {}.".format(self.__class__, self.date,
                                                                 self.info.alternative1, ComparisonTerm.NO_TERM,
                                                                 self.info.alternative2, self.term)

class ValidationCommitment(Commitment):
    def __init__(self, info, term):
        Commitment.__init__(self, info, term)
        #print("\tDM answers YES")

    def __str__(self):
        return "{} at {} :\n\t{} {} {}\n\tDM answers YES.".format(self.__class__, self.date,
                                                                  self.info.alternative1, self.term, self.info.alternative2)

class InvalidationCommitment(Commitment):
    def __init__(self, info, term):
        Commitment.__init__(self, info, term)  # ici, term est la réponse à laquelle s'oppose le DM
        #print("\tDM answers NO")

    def __str__(self):
        return "{} at {} :\n\t{} {} {}\n\tDM answers NO.".format(self.__class__, self.date,
                                                                  self.info.alternative1, self.term, self.info.alternative2)

from CORE.decorators import singleton
@singleton
class CommitmentStore():
    def __init__(self):
        self._store_info_commitment = dict()
        self._store_date_commitment = list()

    def add(self, commitment):
        #print(commitment)
        if commitment.id not in self._store_info_commitment:
            self._store_info_commitment[commitment.id] = set()
        self._store_info_commitment[commitment.id].add(commitment)

        self._store_date_commitment.append(commitment)

    def __str__(self):
        s = "[COMMITMENT STORE]\n"
        for commitment in self._store_date_commitment:
            s += str(commitment) + "\n"
        return s