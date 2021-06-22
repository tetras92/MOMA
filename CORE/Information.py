from CORE.AppreciationObject import PairwiseInformation, NInformation, PInformation, AInformation
from CORE.Commitment import *
from CORE.Exceptions import DMdoesntValidateNElementException, DMdoesntValidateAElementException, AskWhyException
from CORE.InformationStore import NonPI, N, PI, A
from CORE.Tools import difficultyLevel, covectorOfPairWiseInformationWith2Levels

class Information:
    """ Classe représentant une information. Elle est conçue comme une 'capsule'
        qui contient un objet de type AppreciationObject. Les objets de type Information
        peuvent évoluer. Cette évolution se veut être la traduction de ses passages entre
         NonPI, PI et N."""
    # Attribut static indiquant le nombre total d'objets instanciés.
    NB_OBJECT = 0
    def __init__(self, alternative1, alternative2):
        """À l'initialisation, cet objet contient un simple PairwiseInformation (élément de NonPI)"""
        Information.NB_OBJECT += 1
        self._id = Information.NB_OBJECT
        self.o = PairwiseInformation(self, alternative1, alternative2)
        self.difficultyLevel = difficultyLevel((alternative1, alternative2))
        self.covector = covectorOfPairWiseInformationWith2Levels((alternative1, alternative2))

        self.MinMaxRegretList = list()
        self.is_a_disjointed_pair = self.o.is_disjointed()

    def addMinMaxRegretList(self, tupleOfValues):
        self.MinMaxRegretList.append(tupleOfValues)

    def showMinMaxRegretHistory(self):
        s = str(self) + "\n"
        for tvalues in self.MinMaxRegretList:
            s += str(tvalues) + "\n"
        print(s)

    def _nUpgrade(self, v):
        """Méthode traduisant le passage de l'information de NonPI à N.
        Elle est privée et appelée lorsque le termN de l'information (property)
        est modifié (accès par écriture)."""
        if isinstance(self.o, NInformation):
            return
        # try:
        NonPI().remove(self)
        # except :
        #     print('???', self.o.__class__, self.o.alternative1, self.o.alternative2)
        self.o = NInformation(self, self.alternative1, self.alternative2)
        self.o.termN = v

    def _aUpdate(self, v):
        """Méthode traduisant le passage de l'information vers A().
        Elle est privée et appelée lorsque le termA de l'information (property)
        est modifié  (accès par écriture)."""

        oldO = self.o
        if isinstance(oldO, PInformation): # deja conteste par le DM
            CommitmentStore().add(DMToldCommitment(self, v))
            return
        elif isinstance(oldO, NInformation): # en attente d'etre confirme
            CommitmentStore().add(GuaranteeCommitment(self, v))
            return

        self.o = AInformation(self, self.alternative1, self.alternative2)
        self.o.termA = v

        if isinstance(oldO, PairwiseInformation):
            NonPI().remove(self)
            CommitmentStore().add(AssumedCommitment(self, v))
        elif isinstance(oldO, AInformation):
            CommitmentStore().add(AssumedCommitment(self, v))
        else:
            print("class", oldO.__class__)
            raise Exception("a Update from somewhere else")


    def _pUpgrade(self, v):
        """Méthode traduisant le passage de l'information vers PI.
        Elle est privée et appelée lorsque le termP de l'information (property)
        est modifié  (accès par écriture)."""

        if isinstance(self.o, PInformation):
            CommitmentStore().add(DMToldCommitment(self, v))
            return

        oldO = self.o
        if isinstance(oldO, AInformation):
            A().remove(self)
            if self.difficultyLevel > 2:
                if not(oldO.termA is v):
                    # Retour dans NonPI
                    self.o = PairwiseInformation(self, self.alternative1, self.alternative2)
                    CommitmentStore().add(AskWhyAboutAssumedCommitment(self, oldO.termA))
                    raise AskWhyException(oldO.dominanceObject)
                else:
                    self.o = PInformation(self, self.alternative1, self.alternative2)
                    CommitmentStore().add(ValidationOfAssumedCommitment(self, v))
            else:
                # Transfert dans PI
                self.o = PInformation(self, self.alternative1, self.alternative2)
                self.o.termP = v
                if not(oldO.termA is v):
                    CommitmentStore().add(InvalidationOfAssumedCommitment(self, oldO.termA))
                    raise DMdoesntValidateAElementException(oldO.dominanceObject)
                CommitmentStore().add(ValidationOfAssumedCommitment(self, v))


        self.o = PInformation(self, self.alternative1, self.alternative2)
        self.o.termP = v

        if isinstance(oldO, NInformation):
            N().remove(self)
            # À COMMENTER
            # PI().remove(self) # CREER_UN SYSTEME INTERMEDIAIRE
            if not(oldO.termN is v): # DM ne valide pas la valeur inférée
                CommitmentStore().add(InvalidationCommitment(self, oldO.termN))
                raise DMdoesntValidateNElementException(oldO.dominanceObject)
            CommitmentStore().add(ValidationCommitment(self, v))

        elif isinstance(oldO, PairwiseInformation):
            NonPI().remove(self)
            CommitmentStore().add(AnswerCommitment(self, v))


    def _downgrade(self):
        """Méthode traduisant le retour de l'information dans Non PI.
        Elle est privée et appelée lorsque le termP ou le termN ou le termA de l'information (property)
        est supprimé."""
        if isinstance(self.o, PInformation):
            # print("here")
            PI().remove(self)
        elif isinstance(self.o, NInformation):
            N().remove(self)
        elif isinstance(self.o, AInformation):
            A().remove(self)
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

    def howEnteringPI(self):
        return CommitmentStore().getWayOfIntroduction(self)

    def getGenericTerm(self):
        return self.o.term

    def setTermA(self, v):
        self._aUpdate(v)

    def getTermA(self):
        return self.o.termA

    id = property(getId)
    termN = property(fset=setTermN, fdel=deleteTerm)
    termP = property(fget=getTermP, fset=setTermP, fdel=deleteTerm)
    termA = property(fget=getTermA, fset=setTermA, fdel=deleteTerm)
    last_commit_date = property(fget=lastCommitDate)
    how_entering_pi = property(fget=howEnteringPI)
    alternative1 = property(fget=getAlternative1)
    alternative2 = property(fget=getAlternative2)

    term = property(fget=getGenericTerm)

    def __str__(self):
        return self.o.__str__()

    def __hash__(self):
        return self._id

