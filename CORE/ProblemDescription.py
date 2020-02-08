import csv
import itertools as it

from gurobipy import *

from CORE.Alternative import Alternative
from CORE.AppreciationObject import SwapObject, TransitiveObject
from CORE.Information import Information
from CORE.Tools import attribute_creator, CONSTRAINTSFEASIBILITYTOL, symbol


class ProblemDescription:
    """Classe modélisant la description du problème MCDA dans son ensemble.
        Elle s'initialise à l'aide de 2 fichiers de configuration décrivant
        d'une part les critères et l'ensemble de la table de performance."""

    def __init__(self, criteriaFileName="", performanceTableFileName=""):
        self._criteriaFileName = criteriaFileName
        self._performanceTableFileName = performanceTableFileName
        self._alternativesDict = dict()
        self._fictious_pairs_of_alternatives = dict()
        self._set_up()


    def _set_up(self):
        """Méthode de set-up général"""
        self._set_up_criteria()
        self._set_up_alternatives()
        self._remove_dominated_alternatives()
        self._generate_Information()
        self._generate_list_of_list_of_ordered_criterion_attributes()
        self._generate_dict_of_fictious_pairs_of_alternatives()

    def _set_up_alternatives(self):
        """Instanciation des alternatives à partir de la table de performance."""
        with open(self._performanceTableFileName) as perfFile:
            reader = csv.DictReader(perfFile)
            for row in reader:
                altId = int(row[reader.fieldnames[0]])
                altListOfAttributes = [attribute_creator(criterion, row[criterion.lower()])
                                       for criterion in self._criteriaOrderedList]
                altListOfAttributeLevels = [self._criterionLevelsDict[criterion][
                                                self._criterionAtrributesDict[criterion].index(row[criterion.lower()])]
                                            for criterion in self._criteriaOrderedList]
                altListOfSymbols = [self._criterionSymbolsDict[criterion][
                                                self._criterionAtrributesDict[criterion].index(row[criterion.lower()])]
                                            for criterion in self._criteriaOrderedList]
                self._register_alternative(Alternative(altId, altListOfAttributes, altListOfAttributeLevels, altListOfSymbols))

    def _set_up_criteria(self):
        """Récupération de la description des critères"""
        self._criterionAtrributesDict = dict()
        self._criterionLevelsDict = dict()
        self._criteriaOrderedList = list()
        self._criterionSymbolsDict = dict()
        with open(self._criteriaFileName) as critFile:
            reader = csv.DictReader(critFile)
            for row in reader:
                self._criterionAtrributesDict[row[reader.fieldnames[1]].upper()] = \
                    [row[reader.fieldnames[i]] for i in range(2, len(reader.fieldnames), 3)]
                self._criterionLevelsDict[row[reader.fieldnames[1]].upper()] = \
                    [int(row[reader.fieldnames[i + 1]]) for i in range(2, len(reader.fieldnames), 3)]
                self._criterionSymbolsDict[row[reader.fieldnames[1]].upper()] = \
                    [row[reader.fieldnames[i + 2]] for i in range(2, len(reader.fieldnames), 3)]
                self._criteriaOrderedList.append(row[reader.fieldnames[1]].upper())

    def _register_alternative(self, alternative):
        self._alternativesDict[alternative.id] = alternative

    def _remove_dominated_alternatives(self):
        """Suppression des alternatives dominées;
           Et leur stockage"""
        dominatedAlternativeIdSet = set()
        for i, j in list(it.permutations(self._alternativesDict.keys(), 2)):
            if (j not in dominatedAlternativeIdSet) and (i not in dominatedAlternativeIdSet) and \
                    self._alternativesDict[i] < self._alternativesDict[j]:
                dominatedAlternativeIdSet.add(i)
        print("{} alternatives removed".format(len(dominatedAlternativeIdSet)))
        self._dominatedAlternativeList = list()
        for id in dominatedAlternativeIdSet:
            self._dominatedAlternativeList.append(self._alternativesDict[id])
            del self._alternativesDict[id]
        print("{} alternatives remained".format(len(self._alternativesDict)))

    def _generate_Information(self):
        """Génération de tous les objets de type Information correspondant
            aux alternatives du front de Pareto"""
        self._list_of_information = list()
        for coupleOfAltId in list(it.combinations(self._alternativesDict.keys(), 2)):
            C = list(coupleOfAltId)
            C.sort()
            C = [self._alternativesDict[elt] for elt in C]
            self._list_of_information.append(Information(*C))

    def _generate_list_of_list_of_ordered_criterion_attributes(self):
        """Génération d'une liste ordonnée des attributs pour chacun des critères.
        Sert notamment à la génération du corps d'un programme linéaire type prenant
        en considération le sens de l'optimisation sur chacun des critères."""
        L = list()
        D = dict()
        for criterion in self._criteriaOrderedList:
            LA = list()
            for attribute, level in \
                    list(zip(self._criterionAtrributesDict[criterion], self._criterionLevelsDict[criterion])):
                D[attribute_creator(criterion, attribute)] = level
                LA.append(attribute_creator(criterion, attribute))
            L.append(LA)
        for NSL in L:
            NSL.sort(key=lambda x : D[x])
        self._list_of_list_of_ordered_criterion_attributes = L


    def _generate_dict_of_fictious_pairs_of_alternatives(self):
        def fictious_alternative(j):
            levels_list = list()
            for k in range(len(self._criteriaOrderedList)):
                if k == j:
                    levels_list.append(0)
                else :
                    levels_list.append(1)
            return Alternative(float("inf"), None, levels_list, list())
        for i in range(len(self._criteriaOrderedList)):
            for j in range(len(self._criteriaOrderedList)):
                if i != j:
                    self._fictious_pairs_of_alternatives[(i, j)] = \
                        (fictious_alternative(j), fictious_alternative(i))


    def generate_basic_gurobi_model_and_its_varDict(self, modelName):
        """Retourne un programme linéaire de base prenant en considération le sens
        d'optimisation sur chacun des critères. Celui-ci sera étoffé par les éléments de PI
        pour le calcul de la relation nécessaire.
        """
        listOfListOfOrderedCriterionAttributesCopy = [L.copy() for L in self._list_of_list_of_ordered_criterion_attributes]
        for criterion, i in list(zip(self._criteriaOrderedList, range(len(listOfListOfOrderedCriterionAttributesCopy)))):
            listOfListOfOrderedCriterionAttributesCopy[i].append(attribute_creator(criterion, "BETA"))
            listOfListOfOrderedCriterionAttributesCopy[i] = [attribute_creator(criterion, "ALPHA")] + \
                                                            listOfListOfOrderedCriterionAttributesCopy[i]

        gurobi_model = Model(modelName)
        gurobi_model.setParam('OutputFlag', False)
        gurobi_model.Params.FeasibilityTol = CONSTRAINTSFEASIBILITYTOL
        # print("FEASABILITY TOL", gurobi_model.Params.FeasibilityTol)
        VarDict = {varname: gurobi_model.addVar(vtype=GRB.CONTINUOUS, lb=0., ub=1., name=varname)
                   for L in listOfListOfOrderedCriterionAttributesCopy for varname in L}
        gurobi_model.update()

        cst = LinExpr()
        for LOCA in listOfListOfOrderedCriterionAttributesCopy:
            for i in range(1, len(LOCA)):
                gurobi_model.addConstr(VarDict[LOCA[i]] >= VarDict[LOCA[i - 1]])
            gurobi_model.addConstr(VarDict[LOCA[0]] == 0)
            cst += VarDict[LOCA[-1]]
        gurobi_model.addConstr(cst == 1)

        return gurobi_model, VarDict

    def generate_kb_basic_gurobi_model_and_its_VarM(self, modelName):
        """Retourne le programme linéaire de base prenant en considération le sens
        d'optimisation sur chacun des critères selon la version de la thèse de KB.
        Celui-ci sera étoffé par les éléments de PI pour le calcul de la relation nécessaire.
        """
        gurobi_model = Model(modelName)
        gurobi_model.setParam('OutputFlag', False)

        # gurobi_model.Params.IntFeasTol = CONSTRAINTSFEASIBILITYTOL
        # gurobi_model.Params.FeasibilityTol = CONSTRAINTSFEASIBILITYTOL
        # gurobi_model.Params.DualReductions = 0   # indispensable pour discriminer entre PL InFeasible or unBounded
        # Borne sup choisie arbitrairement égale à 1 (UTA GMS).

        VarM = [gurobi_model.addVar(vtype=GRB.INTEGER, lb=0, name="M_{}".format(criterion))
                   for criterion in self._criteriaOrderedList]

        # VarM = [gurobi_model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="M_{}".format(criterion))
        #            for criterion in self._criteriaOrderedList]
        gurobi_model.update()

        return gurobi_model, VarM

    def __str__(self):
        s = ""
        # for alt in self._alternativesDict.values():
        #     s += str(alt) + "\n"
        for info in self._list_of_information:
            s += str(info) + "\n"
        return s

    def __getitem__(self, item):
        return self._alternativesDict[item]

    def getNumberOfAlternatives(self):
        return len(self._alternativesDict)

    def getNumberOfInformation(self):
        return len(self._list_of_information)

    def getFictiousPairsOfAlternatives(self):
        return self._fictious_pairs_of_alternatives

    numberOfAlternatives = property(getNumberOfAlternatives)
    numberOfInformation = property(getNumberOfInformation)
    fictiousPairsOfAlternatives = property(getFictiousPairsOfAlternatives)

    def getCorrespondingAlternative(self, alternative):
        for alt in self._alternativesDict.values():
            if alternative == alt:
                return alt

        return alternative

    def getSwapObject(self, alternative, edge):
        attributeLevelsList = alternative.attributeLevelsList.copy()
        i, j = edge
        attributeLevelsList[i] = (attributeLevelsList[i] + 1)%2
        attributeLevelsList[j] = (attributeLevelsList[j] + 1)%2
        alt_suc = Alternative(float("inf"), None, attributeLevelsList, list())
        corr_alt_suc = self.getCorrespondingAlternative(alt_suc)
        if alt_suc is corr_alt_suc:
            # absence de l'alternative dans le jeu considéré
            corr_alt_suc = Alternative("--", None, attributeLevelsList,
                                       "".join([symbol(v) for v in attributeLevelsList]))
        return SwapObject(alternative, corr_alt_suc)

    def getTransitiveObject(self, alternativeD, alternatived):
        return TransitiveObject(alternativeD, alternatived)
