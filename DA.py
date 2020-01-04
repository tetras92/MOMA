import csv
import itertools as it
from Alternative import *
from AppreciationObject import PairwiseComparisonObject
from InformationStore import *
from Tools import attribute_creator


@singleton
class DA:
    def __init__(self, criteriaFileName="", performanceTableFileName="", NonPI_AOPicker=None, stopCriterion=None):

        self._criteriaFileName = criteriaFileName
        self._performanceTableFileName = performanceTableFileName
        self._alternativesDict = dict()
        self._set_up()
        # Initialization of the InformationStore Objects
        NonPI(NonPI_AOPicker)
        PI()
        N()
        # End
        self._generate_PCO()
        self._stopCriterion = stopCriterion

        self._generate_list_of_list_of_ordered_criterion_attributes()
    def _set_up(self):
        self._set_up_criteria()
        self._set_up_alternatives()
        self._remove_dominated_alternatives()

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
                #print("{} < {}".format(self._alternativesDict[i].attributeLevelsList, self._alternativesDict[j].attributeLevelsList))
                dominatedAlternativeIdSet.add(i)
        print("{} alternatives removed".format(len(dominatedAlternativeIdSet)))
        for id in dominatedAlternativeIdSet:
            del self._alternativesDict[id]
        print("{} alternatives remained".format(len(self._alternativesDict)))

    def _generate_PCO(self):
        for coupleOfAltId in list(it.combinations(self._alternativesDict.keys(), 2)):
            C = list(coupleOfAltId)
            C.sort()
            C = [self._alternativesDict[elt] for elt in C]
            PairwiseComparisonObject(*C)

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
        print(self._list_of_list_of_ordered_criterion_attributes)
    def process(self):
        while not self._stopCriterion.stop():
            pco = NonPI().pick()
            Dialog(pco).madeWith(WS_DM())


from StopCriterion import *
from AOPicker import *
from DM import WS_DM
if __name__ == "__main__" :
    WS_DM("CSVFILES/DM_Utility_Function.csv")
    DA(criteriaFileName="CSVFILES/criteria.csv", performanceTableFileName="CSVFILES/fullPerfTableTruncated.csv", NonPI_AOPicker=RandomPicker(0),
       stopCriterion=DialogDurationStopCriterion(6))

    DA().process()