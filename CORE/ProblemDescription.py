import csv
import itertools as it

from gurobipy import *

from CORE.Alternative import Alternative
from CORE.Information import Information
from CORE.Tools import attribute_creator


class ProblemDescription:
    def __init__(self, criteriaFileName="", performanceTableFileName=""):
        self._criteriaFileName = criteriaFileName
        self._performanceTableFileName = performanceTableFileName
        self._alternativesDict = dict()
        self._set_up()


    def _set_up(self):
        self._set_up_criteria()
        self._set_up_alternatives()
        self._remove_dominated_alternatives()
        self._generate_Information()
        self._generate_list_of_list_of_ordered_criterion_attributes()

    def _set_up_alternatives(self):
        with open(self._performanceTableFileName) as perfFile:
            reader = csv.DictReader(perfFile)
            for row in reader:
                altId = int(row[reader.fieldnames[0]])
                altListOfAttributes = [attribute_creator(criterion, row[criterion.lower()])
                                       for criterion in self._criteriaOrderedList]
                altListOfAttributeLevels = [self._criterionLevelsDict[criterion][
                                                self._criterionAtrributesDict[criterion].index(row[criterion.lower()])]
                                            for criterion in self._criteriaOrderedList]
                self._register_alternative(Alternative(altId, altListOfAttributes, altListOfAttributeLevels))
                #print(altListOfAttributes, altListOfAttributeLevels, sep="\n")

    def _set_up_criteria(self):
        self._criterionAtrributesDict = dict()
        self._criterionLevelsDict = dict()
        self._criteriaOrderedList = list()
        with open(self._criteriaFileName) as critFile:
            reader = csv.DictReader(critFile)
            for row in reader:
                self._criterionAtrributesDict[row[reader.fieldnames[1]].upper()] = \
                    [row[reader.fieldnames[i]] for i in range(2, len(reader.fieldnames), 2)]
                self._criterionLevelsDict[row[reader.fieldnames[1]].upper()] = \
                    [int(row[reader.fieldnames[i + 1]]) for i in range(2, len(reader.fieldnames), 2)]
                self._criteriaOrderedList.append(row[reader.fieldnames[1]].upper())

    def _register_alternative(self, alternative):
        self._alternativesDict[alternative.id] = alternative

    def _remove_dominated_alternatives(self):
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
        for coupleOfAltId in list(it.combinations(self._alternativesDict.keys(), 2)):
            C = list(coupleOfAltId)
            C.sort()
            C = [self._alternativesDict[elt] for elt in C]
            Information(*C)

    def _generate_list_of_list_of_ordered_criterion_attributes(self):
        L = list()
        D = dict()
        for criterion in self._criteriaOrderedList:
            LA = list()
            for attribute, level in list(zip(self._criterionAtrributesDict[criterion], self._criterionLevelsDict[criterion])):
                D[attribute_creator(criterion, attribute)] = level
                LA.append(attribute_creator(criterion, attribute))
            L.append(LA)
        for NSL in L:
            NSL.sort(key=lambda x : D[x])
        self._list_of_list_of_ordered_criterion_attributes = L

    def generate_basic_gurobi_model_and_its_varDict(self, modelName):
        listOfListOfOrderedCriterionAttributesCopy = [L.copy() for L in self._list_of_list_of_ordered_criterion_attributes]
        for criterion, i in list(zip(self._criteriaOrderedList, range(len(listOfListOfOrderedCriterionAttributesCopy)))):
            listOfListOfOrderedCriterionAttributesCopy[i].append(attribute_creator(criterion, "BETA"))
            listOfListOfOrderedCriterionAttributesCopy[i] = [attribute_creator(criterion, "ALPHA")] + \
                                                            listOfListOfOrderedCriterionAttributesCopy[i]

        gurobi_model = Model(modelName)
        gurobi_model.setParam('OutputFlag', False)
        VarDict = {varname: gurobi_model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=varname)
                   for L in listOfListOfOrderedCriterionAttributesCopy for varname in L}

        cst = LinExpr()
        for LOCA in listOfListOfOrderedCriterionAttributesCopy:
            for i in range(1, len(LOCA)):
                gurobi_model.addConstr(VarDict[LOCA[i]] >= VarDict[LOCA[i - 1]])
            gurobi_model.addConstr(VarDict[LOCA[0]] == 0)
            cst += VarDict[LOCA[-1]]
        gurobi_model.addConstr(cst == 1)

        return gurobi_model, VarDict

    def __str__(self):
        s = ""
        for alt in self._alternativesDict.values():
            s += str(alt) + "\n"
        return s

    def __getitem__(self, item):
        return self._alternativesDict[item]

    def getNumberOfAlternatives(self):
        return len(self._alternativesDict)

    numberOfAlternatives = property(getNumberOfAlternatives)