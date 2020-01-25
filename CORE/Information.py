from CORE.AppreciationObject import PairwiseInformation, NInformation, PInformation
from CORE.Commitment import *
from CORE.Exceptions import DMdoesntValidateNElementException
from CORE.InformationStore import NonPI, N, PI
from CORE.Tools import covectorOfPairWiseInformationWith2Levels

class Information:
    """ Classe représentant une information. Elle est conçue comme une 'capsule'
        qui contient un objet de type AppreciationObject. Les objets de type Information
        peuvent évoluer. Cette évolution se veut être la traduction de ses passages entre
         NonPI, PI et N."""
    # Attribut static indiquant le nombre total d'objets instanciés.
    NB_OBJECT = 0
    def __init__(self, alternative1, alternative2):
        """À l'initialisation, cet objet contient un simple PairwiseInformation (élément de NonPI)"""
        self.o = PairwiseInformation(self, alternative1, alternative2)
        self._id = Information.NB_OBJECT
        Information.NB_OBJECT += 1
        # Calcul du covector : np.array[{1,-1,0}]
        self.covector = covectorOfPairWiseInformationWith2Levels((alternative1, alternative2))

    def _nUpgrade(self, v):
        """Méthode traduisant le passage de l'information de NonPI à N.
        Elle est privée et appelée lorsque le termN de l'information (property)
        est modifié (accès par écriture)."""
        NonPI().remove(self)
        self.o = NInformation(self, self.alternative1, self.alternative2)
        self.o.termN = v

    def _pUpgrade(self, v):
        """Méthode traduisant le passage de l'information vers PI.
        Elle est privée et appelée lorsque le termP de l'information (property)
        est modifié  (accès par écriture)."""
        oldO = self.o
        self.o = PInformation(self, self.alternative1, self.alternative2)
        self.o.termP = v

        if isinstance(oldO, NInformation):
            N().remove(self)
            if not oldO.termN is v: # DM ne valide pas la valeur inférée
                CommitmentStore().add(InvalidationCommitment(self, oldO.termN))
                raise DMdoesntValidateNElementException(self)
            CommitmentStore().add(ValidationCommitment(self, v))

        elif isinstance(oldO, PairwiseInformation):
            NonPI().remove(self)
            CommitmentStore().add(AnswerCommitment(self, v))


    def _downgrade(self):
        """Méthode traduisant le retour de l'information dans Non PI.
        Elle est privée et appelée lorsque le termP ou le termN de l'information (property)
        est supprimé."""
        if isinstance(self.o, PInformation):
            PI().remove(self)
        elif isinstance(self.o, NInformation):
            N().remove(self)
        self.o = PairwiseInformation(self, self.alternative1, self.alternative2)

    def setTermN(self, v):
        self._nUpgrade(v)

    def setTermP(self, v):
        self._pUpgrade(v)

    def getTermP(self):
        return self.o.termP

    def deleteTerm(self):
        self._downgrade()

    def lastCommitDate(self):
        return CommitmentStore().getDateOf(self)

    def getAlternative1(self):
        return self.o.alternative1

    def getAlternative2(self):
        return self.o.alternative2

    def getId(self):
        return self._id

    def linear_expr(self, VarDict):
        """Dict[str:GurobiVar] -> GurobiLinExpr"""
        return self.o.linear_expr(VarDict)


    id = property(getId)
    termN = property(fset=setTermN, fdel=deleteTerm)
    termP = property(fget=getTermP, fset=setTermP, fdel=deleteTerm)
    last_commit_date = property(fget=lastCommitDate)
    alternative1 = property(fget=getAlternative1)
    alternative2 = property(fget=getAlternative2)


    def __str__(self):
        return self.o.__str__()

    def __hash__(self):
        return self._id
