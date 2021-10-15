from CORE.AppreciationObject import PairwiseInformation, NInformation, PInformation, AInformation, AtomicInformation
from CORE.Commitment import *
from CORE.Exceptions import DMdoesntValidateNElementException, DMdoesntValidateAElementException, AskWhyException
from CORE.InformationStore import NonPI, N, PI, A, AA
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
        oldO = self.o
        # if isinstance(self.o, NInformation):
        #     return

        if isinstance(self.o, AtomicInformation):
            AA().remove(self)
            CommitmentStore().add(GuaranteeCommitment(self, v))

        elif isinstance(self.o, PairwiseInformation):
            NonPI().remove(self)
            CommitmentStore().add(GuaranteeCommitment(self, v))

        elif isinstance(self.o, AInformation):
            A().remove(self)
            CommitmentStore().add(GuaranteeCommitment(self, v))

        else:
            print("class", oldO.__class__)
            raise Exception("a Update from somewhere else")

        self.o = NInformation(self, self.alternative1, self.alternative2)
        self.o.termN = v

    def _aUpdate(self, v):
        """Méthode traduisant le passage de l'information vers A().
        Elle est privée et appelée lorsque le termA de l'information (property)
        est modifié  (accès par écriture)."""

        oldO = self.o
        self.o = AInformation(self, self.alternative1, self.alternative2)
        self.o.termA = v

        if isinstance(oldO, PairwiseInformation):
            NonPI().remove(self)
            CommitmentStore().add(AssumedCommitment(self, v))

        else:
            print("class", oldO.__class__)
            raise Exception("a Update from somewhere else")

    def _atomicAUpdate(self, v):
        """Méthode traduisant le passage de l'information vers AA().
        Elle est privée et appelée lorsque le termAA de l'information (property)
        est modifié  (accès par écriture)."""

        # reflechir a la provenance
        oldO = self.o

        if isinstance(oldO, PairwiseInformation): # pas de remove car l'info est fictive
            CommitmentStore().add(BecauseAssumedAtomicCommitment(self, v))
            NonPI().remove(self)
            self.o = AtomicInformation(self, self.alternative1, self.alternative2)
            self.o.termAA = v
        else:
            print("class", oldO.__class__)
            raise Exception("a Update from somewhere else")

        # elif isinstance(oldO, AInformation):
        #     CommitmentStore().add(AssumedCommitment(self, v))
        # else:
        #     print("class", oldO.__class__)
        #     raise Exception("a Update from somewhere else")
        #
        # if isinstance(oldO, PInformation): # deja confirme par le DM
        #     CommitmentStore().add(DMToldCommitment(self, v))
        #     return
        # elif isinstance(oldO, NInformation): # en attente d'etre confirme
        #     CommitmentStore().add(GuaranteeCommitment(self, v))
        #     return


    def _pUpgrade(self, v):
        """Méthode traduisant le passage de l'information vers PI.
        Elle est privée et appelée lorsque le termP de l'information (property)
        est modifié  (accès par écriture)."""

        oldO = self.o

        # - Jeudi 14 octobre 2021 : tentative de maj de pUpdate : objectif : traiter indifféremment les comparaisons d'alternatives swaps natifs des comparaisons d'alternatives dont
        #                                                                   # la difficultyLevel est > 2.
        # A COMPLETER

        if isinstance(oldO, PInformation):
            if oldO.termP is v:
                CommitmentStore().add(DMConfirmStatementCommitment(self, v))
            else:
                raise Exception("cas non encore pris en charge")
            return

        if isinstance(oldO, AInformation):
            A().remove(self)
            if not(oldO.termA is v):
                # Retour systematique dans NonPI
                self.o = PairwiseInformation(self, self.alternative1, self.alternative2)
                CommitmentStore().add(AskWhyAboutAssumedCommitment(self, oldO.termA))
                raise AskWhyException(oldO.dominanceObject)
            else:
                # Transfert dans PI
                self.o = PInformation(self, self.alternative1, self.alternative2)
                self.o.termP = v
                CommitmentStore().add(ValidationOfAssumedCommitment(self, v))
            return

        if isinstance(oldO, AtomicInformation):
            self.o = PInformation(self, self.alternative1, self.alternative2)
            self.o.termP = v
            if not(oldO.termAA is v):
                CommitmentStore().add(InvalidationOfBecauseAssumedAtomicCommitment(self, oldO.termAA))
                raise DMdoesntValidateAElementException(oldO.dominanceObject)
            else:
                CommitmentStore().add(ValidationOfAssumedCommitment(self, v))
            return

        self.o = PInformation(self, self.alternative1, self.alternative2)
        self.o.termP = v

        if isinstance(oldO, NInformation):
            N().remove(self)
            # À COMMENTER
            # PI().remove(self) # CREER_UN SYSTEME INTERMEDIAIRE
            if not(oldO.termN is v): # DM ne valide pas la valeur inférée
                CommitmentStore().add(InvalidationCommitment(self, oldO.termN))
                raise DMdoesntValidateNElementException(oldO.dominanceObject)
            else:
                # print("=========================*")
                CommitmentStore().add(ValidationCommitment(self, v))

        elif isinstance(oldO, PairwiseInformation):
            NonPI().remove(self)
            CommitmentStore().add(AnswerCommitment(self, v))
        else:
            print("class", oldO.__class__)
            raise Exception("a Update from somewhere else")

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
        elif isinstance(self.o, AtomicInformation):
            AA().remove()
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

    def setTermAA(self, v):
        self._atomicAUpdate(v)

    def getTermAA(self):
        return self.o.termAA

    def confirmP(self):
        self._confirmPStatement()
        return True
    id = property(getId)
    termN = property(fset=setTermN, fdel=deleteTerm)
    termP = property(fget=getTermP, fset=setTermP, fdel=deleteTerm)
    termA = property(fget=getTermA, fset=setTermA, fdel=deleteTerm)
    termAA = property(fget=getTermAA, fset=setTermAA, fdel=deleteTerm)
    termPConfirm = property(fget=confirmP)
    last_commit_date = property(fget=lastCommitDate)
    how_entering_pi = property(fget=howEnteringPI)
    alternative1 = property(fget=getAlternative1)
    alternative2 = property(fget=getAlternative2)

    term = property(fget=getGenericTerm)

    def _confirmPStatement(self):
        CommitmentStore().add(DMToldCommitment(self, self.termP))

    def __str__(self):
        return self.o.__str__()

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self._id

    def __eq__(self, other):
        return self._id == other.id
