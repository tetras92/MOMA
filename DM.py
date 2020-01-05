import csv

import numpy as np

from ComparisonTerm import *
from decorators import singleton


class DM:
    pass

@singleton
class WS_DM(DM):
    def __init__(self, utilityFunctionName):
        with open(utilityFunctionName) as utilityFile:
            reader = csv.DictReader(utilityFile)
            self.utilitiesList = list()
            for row in reader:
                for criterion in reader.fieldnames: # l'ordre d'initialisation des critères est le même que celui de leur évaluation dans utilityFunctionName
                    self.utilitiesList.append(float(row[criterion]))

    def evaluate(self, pco):
        U1 = np.vdot(np.array(self.utilitiesList), np.array(pco.alternative1.attributeLevelsList))
        U2 = np.vdot(np.array(self.utilitiesList), np.array(pco.alternative2.attributeLevelsList))
        if U1 < U2:
            pco.termP = ComparisonTerm.IS_LESS_PREFERRED_THAN
        elif U1 > U2:
            pco.termP = ComparisonTerm.IS_PREFERRED_TO
        else:
            pco.termP = ComparisonTerm.IS_INDIFERRENT_TO






