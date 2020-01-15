import csv

import numpy as np

from CORE.ComparisonTerm import *


class DM:
    pass

class NoisyWS_DM(DM):
    def __init__(self, utilityFunctionName, sigma):
        self._sigma = sigma
        with open(utilityFunctionName) as utilityFile:
            reader = csv.DictReader(utilityFile)
            self.utilitiesList = list()
            for row in reader:
                for criterion in reader.fieldnames: # l'ordre d'initialisation des critères est le même que celui de leur évaluation dans utilityFunctionName
                    self.utilitiesList.append(float(row[criterion]))

    def _evaluateAlternative(self, alternative):
        return np.vdot(np.array(self.utilitiesList), np.array(alternative.attributeLevelsList)) \
                                + np.random.normal(0, self._sigma)

    def evaluate(self, info):
        U1 = self._evaluateAlternative(info.alternative1)
        U2 = self._evaluateAlternative(info.alternative2)
        if U1 < U2:
            info.termP = ComparisonTerm.IS_LESS_PREFERRED_THAN
        elif U1 > U2:
            info.termP = ComparisonTerm.IS_PREFERRED_TO
        else:
            info.termP = ComparisonTerm.IS_INDIFERRENT_TO




class WS_DM(NoisyWS_DM):
    def __init__(self, utilityFunctionName):
        NoisyWS_DM.__init__(self, utilityFunctionName, 0)

    def evaluate(self, info):
        NoisyWS_DM.evaluate(self, info)


class VNoisyWS_DM(NoisyWS_DM):
    def __init__(self, utilityFunctionName, initialSigma, raisonLoiGeo):
        NoisyWS_DM.__init__(self, utilityFunctionName, initialSigma)
        self._raisonLoiGeo = raisonLoiGeo

    def evaluate(self, info):
        NoisyWS_DM.evaluate(self, info)
        self._sigma *= self._raisonLoiGeo