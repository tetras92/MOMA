import csv

import numpy as np

from CORE.ComparisonTerm import *
from CORE.Tools import AS_LEAST_AS_GOOD_AS, NOT_AS_LEAST_AS_GOOD_AS

class DM:
    """Classe (de base) modélisant un DM. Différents modèles héritent de cette
    classe."""
    pass

class NoisyWS_DM(DM):
    """Classe modélisant un DM dont la fonction d'évaluation (une somme pondérée)
    d'une alternative est bruité. Le bruit à un moment de l'interaction est une réalisation d'une
    loi normale d'espérance nulle et d'écart-type sigma constant."""
    def __init__(self, utilityFunctionFileName, sigma):
        """str * float -> NoneType
        l'initialisation se fait à l'aide d'un fichier csv dans lequel on
        trouve les poids attribués à chaque critère.
         HYP : l'ordre (de gauche à droite) d'énumération des critères est le même
         que celui (du haut vers le bas) du fichier de description des critères."""
        self._sigma = sigma
        with open(utilityFunctionFileName) as utilityFile:
            reader = csv.DictReader(utilityFile)
            self.utilitiesList = list()
            for row in reader:
                for criterion in reader.fieldnames:
                    self.utilitiesList.append(float(row[criterion]))

    def _evaluateAlternative(self, alternative):
        """Alternative -> float
        retourne l'évaluation de l'alternative."""
        return np.vdot(np.array(self.utilitiesList), np.array(alternative.attributeLevelsList)) \
                                + np.random.normal(0, self._sigma)

    def evaluate(self, info):
        """Alternative -> float
        réalise (par effet de bord) l'évaluation de l'information."""
        U1 = self._evaluateAlternative(info.alternative1)
        U2 = self._evaluateAlternative(info.alternative2)
        if U1 >= U2:
            info.termP = AS_LEAST_AS_GOOD_AS()
        else:
            info.termP = NOT_AS_LEAST_AS_GOOD_AS()



class WS_DM(NoisyWS_DM):
    """Classe modélisant un DM dont la fonction d'évaluation (une somme pondérée)
    d'une alternative est non bruité."""
    def __init__(self, utilityFunctionFileName):
        NoisyWS_DM.__init__(self, utilityFunctionFileName, 0)

    def evaluate(self, info):
        NoisyWS_DM.evaluate(self, info)


class VNoisyWS_DM(NoisyWS_DM):
    """Classe modélisant un DM dont la fonction d'évaluation (une somme pondérée)
    d'une alternative est bruité. Le bruit à un moment de l'interaction est une réalisation d'une
    loi normale d'espérance nulle et d'écart-type sigma qui évolue au fil des interactions suivant une
    loi géométrique dont la raison est précisée à l'initialisation."""
    def __init__(self, utilityFunctionFileName, initialSigma, raisonLoiGeo):
        """str * float * float -> NoneType
        l'initialisation se fait à l'aide d'un fichier csv dans lequel on
        trouve les poids attribués à chaque critère.
        initialSigma : l'écart-type initial.
        raisonLoiGeo : raison de la loi géométrique.
         HYP : l'ordre (de gauche à droite) d'énumération des critères est le même
         que celui (du haut vers le bas) du fichier de description des critères."""
        NoisyWS_DM.__init__(self, utilityFunctionFileName, initialSigma)
        self._raisonLoiGeo = raisonLoiGeo

    def evaluate(self, info):
        NoisyWS_DM.evaluate(self, info)
        self._sigma *= self._raisonLoiGeo
