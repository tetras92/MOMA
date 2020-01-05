import csv
import itertools as it

from CORE.Alternative import *
from CORE.AppreciationObject import PairwiseComparisonObject
from CORE.InformationStore import *
from CORE.Tools import attribute_creator


@singleton
class DA:
    EPSILON = 0.0000001
    def __init__(self, criteriaFileName="", performanceTableFileName="", NonPI_AOPicker=None, N_AOPicker=None,stopCriterion=None):

        self._criteriaFileName = criteriaFileName
        self._performanceTableFileName = performanceTableFileName
        self._alternativesDict = dict()
        self._set_up()
        # Initialization of the InformationStore Objects
        NonPI(NonPI_AOPicker)
        PI()
        N(N_AOPicker)
        # End
        self._generate_PCO()
        self._stopCriterion = stopCriterion

        self._generate_list_of_list_of_ordered_criterion_attributes()
        self._generate_gurobi_model_and_its_varDict()

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


    def _generate_gurobi_model_and_its_varDict(self):
        for criterion, i in list(zip(self._criteriaOrderedList, range(len(self._list_of_list_of_ordered_criterion_attributes)))):
            self._list_of_list_of_ordered_criterion_attributes[i].append(attribute_creator(criterion, "BETA"))
            self._list_of_list_of_ordered_criterion_attributes[i] = [attribute_creator(criterion, "ALPHA")] + self._list_of_list_of_ordered_criterion_attributes[i]

        gurobi_model = Model("MOMA_MCDA")
        gurobi_model.setParam('OutputFlag', False)
        VarDict = {varname : gurobi_model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=varname)
                    for L in self._list_of_list_of_ordered_criterion_attributes for varname in L}

        cst = LinExpr()
        for LOCA in self._list_of_list_of_ordered_criterion_attributes:
            for i in range(1, len(LOCA)):
                gurobi_model.addConstr(VarDict[LOCA[i]] >= VarDict[LOCA[i-1]])
            gurobi_model.addConstr(VarDict[LOCA[0]] == 0)
            cst += VarDict[LOCA[-1]]
        gurobi_model.addConstr(cst == 1)

        for linexpr, term in PI().get_linear_expr_and_term_of_preference_information_stored(VarDict):
            if term == ComparisonTerm.IS_LESS_PREFERRED_THAN:
                gurobi_model.addConstr(linexpr <= - DA().EPSILON)
            elif term == ComparisonTerm.IS_PREFERRED_TO:
                gurobi_model.addConstr(linexpr >= DA().EPSILON)
            elif term == ComparisonTerm.IS_INDIFERRENT_TO:
                gurobi_model.addConstr(linexpr == 0)
            else :
                raise Exception("Error in PI")

        #print(self._list_of_list_of_ordered_criterion_attributes)
        return gurobi_model, VarDict

    def process(self):
        while not self._stopCriterion.stop():
            model, varDict = self._generate_gurobi_model_and_its_varDict()
            N().update(varDict, model)
            N_initial_empty_state = N().is_empty()
            while not N().is_empty():
                pco = N().pick()
                Dialog(pco).madeWith(WS_DM())

            if not N_initial_empty_state :
                continue
            pco = NonPI().pick()
            Dialog(pco).madeWith(WS_DM())


from CORE.StopCriterion import *
from CORE.AOPicker import *
from CORE.DM import WS_DM


if __name__ == "__main__" :
    WS_DM("CSVFILES/DM_Utility_Function.csv")
    DA(criteriaFileName="CSVFILES/criteria.csv", performanceTableFileName="CSVFILES/fullPerfTableTruncated.csv", NonPI_AOPicker=RandomPicker(0),
       stopCriterion=DialogDurationStopCriterion(6), N_AOPicker=RandomPicker(0))

    DA().process()