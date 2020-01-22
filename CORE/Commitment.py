from CORE.ComparisonTerm import *
from CORE.Dialog import Dialog
from CORE.Tools import colored_expression

class Commitment:
    """Classe modélisant une déclaration du DM durant l'interaction.
        Elle peut être de 3 types : Une réponse (AnswerCommitment),
        une Validation d'une information induite (ValidationCommitment),
        ou une contestation d'une information inférée (InvalidationCommitment).
        Un Commitment encapsule une Information, l'avis du DM (sous la forme
        d'un terme de comparaison), et la date de cet avis"""

    def __init__(self, info, term):
        self.info = info
        self.term = term
        self.date = Dialog.NB
        self._id = info.id

    def getId(self):
        return self._id

    id = property(getId)

class AnswerCommitment(Commitment):
    """Classe modélisant la déclaration que fait un DM en exprimant sa
        préférence sur une paire d'alternatives à travers le terme de
        comparaison term"""
    def __init__(self, info, term):
        Commitment.__init__(self, info, term)

    def __str__(self):
        symb1, symb2 = colored_expression(self.info.alternative1.symbolicName, self.info.alternative2.symbolicName)
        return "{} at {} :\n\t[{:>2}] : {} {} {} : [{:>2}]\n\tDM answers {}.".format(self.__class__, self.date,
                                                                 self.info.alternative1.id, symb1, ComparisonTerm.NO_TERM,
                                                                 symb2, self.info.alternative2.id, self.term)

class ValidationCommitment(Commitment):
    """Classe modélisant la déclaration que fait un DM en validant
       un élément induit par calcul de la relation nécessaire, term
       représente le terme de comparaison induit"""
    def __init__(self, info, term):
        Commitment.__init__(self, info, term)

    def __str__(self):
        symb1, symb2 = colored_expression(self.info.alternative1.symbolicName, self.info.alternative2.symbolicName)
        return "{} at {} :\n\t[{:>2}] : {} {} {} : [{:>2}]\n\tDM answers YES.".format(self.__class__, self.date,
                                                                                     self.info.alternative1.id, symb1,
                                                                                     self.term,
                                                                                     symb2, self.info.alternative2.id)

class InvalidationCommitment(Commitment):
    """Classe modélisant la déclaration que fait un DM en ne validant pas
       un élément induit par calcul de la relation nécessaire, term
       représente le terme de comparaison contesté"""
    def __init__(self, info, term):
        Commitment.__init__(self, info, term)  # ici, term est la réponse à laquelle s'oppose le DM

    def __str__(self):
        symb1, symb2 = colored_expression(self.info.alternative1.symbolicName, self.info.alternative2.symbolicName)
        return "{} at {} :\n\t[{:>2}] : {} {} {} : [{:>2}]\n\tDM answers NO.".format(self.__class__, self.date,
                                                                                      self.info.alternative1.id, symb1,
                                                                                      self.term,
                                                                                      symb2, self.info.alternative2.id)

from CORE.decorators import singleton
@singleton
class CommitmentStore():
    """Classe conteneur de l'ensemble des Commitments du DM.
        L'enregistrement se fait à la fois par information et par
        date. Dans le premier cas, la 'base de données' est indexée sur
        l'identifiant de l'information. Dans le second, elle est indexée
        sur la 'date' de la déclaration."""
    def __init__(self):
        self._store_info_commitment = dict()
        self._store_date_commitment = list()

    def add(self, commitment):
        print(commitment)
        if commitment.id not in self._store_info_commitment:
            self._store_info_commitment[commitment.info] = list()
        self._store_info_commitment[commitment.info].append(commitment)

        self._store_date_commitment.append(commitment)

    def getDateOf(self, info):
        """Information -> int
        retourne le cas échéant la 'date' de la dernière déclaration
        concernant info (quelle que soit la nature de cette déclaration)"""
        return self._store_info_commitment[info][-1].date

    def __str__(self):
        s = "[COMMITMENT STORE]\n"
        for commitment in self._store_date_commitment:
            s += str(commitment) + "\n"
        return s

