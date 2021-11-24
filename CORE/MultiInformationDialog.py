import random

from CORE.Exceptions import AskWhyException, DMdoesntValidateAtomicAssumedElementException
from CORE.InformationStore import *
from CORE.Dialog import *

class MultiInformationDialog:
    """Classe modélisant un 'élément' d'interaction entre le DM et le DA
     sous la forme d'un dialogue. Au cours de celui-ci, plusieurs information sont
     présentées, sur lesquelles le DM se prononce (completement, à moins qu'il y ait
     contestation sur l'une d'elles.""" # 20/10/2021

    # NB : attribut static de la classe renseignant sur le nombre de sollicitations du DM
    NB = 0

    def __init__(self, ListOfInfo):
        self.content = ListOfInfo
        # self.dmCouldAppliedStrategyOn = not(orderCount)

    def madeWith(self, dm):
        # prevoir ici comment le dm reordonnes les infos pour leur traitement. pour l'instant faisons aléatoire
        L = dm.strategy.list_order_values(self.content)
        finished = True
        for info in L:
            print("===> DM points {}\n".format(info))
            # print(A())
            # print("-------", info.o.__class__)
            try:
                Dialog(info).madeWith(dm)
                print()
            except AskWhyException as awe:
                for swap_info in info.cause:
                    # print("///////", info.o.__class__)
                    try:
                        Dialog(swap_info).madeWith(dm)
                    except DMdoesntValidateAtomicAssumedElementException as dma2:
                        finished = False

                if not finished:
                    N().clear()
                    break
                else:           # DM valide l'explication de info
                    # print("=========>>>>")
                    # print("A", A())
                    # print("PI", PI())
                    # print("N", N())
                    info.pi_integration_by_explanation()


        A().clear()

        return finished
