import numpy as np
from gurobipy import *

from CORE.Tools import covectorOfPairWiseInformationWith2Levels
from CORE.Tools import CONSTRAINTSFEASIBILITYTOL

class SmallestSetOfPairs:
    @staticmethod
    def compute(mcda_problemDescription=None, Relation=None, APrioriSelected=None):
        model = Model("Smallest Set MOMBAL")
        model.setParam('OutputFlag', False)
        model.Params.FeasibilityTol = CONSTRAINTSFEASIBILITYTOL

        LCovPIList = [covectorOfPairWiseInformationWith2Levels(coupleAlt) for coupleAlt in Relation]
        BaseVectorVar = [model.addVar(vtype=GRB.BINARY, name="{}_in_base".format(i)) for i in range(len(Relation))]

        MatrixOfBoolVar = [[model.addVar(vtype=GRB.BINARY, name="b_{}_{}".format(i, j)) for i in range(len(Relation))] for j in range(len(Relation))]
        MatrixOfCoeffVar = [[model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="c_{}_{}".format(i, j)) for i in range(len(Relation))] for j in range(len(Relation))]

        MatrixOfVarE = [[model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="E_{}_{}".format(i, j)) for i in range(len(Relation))] for j in range(len(Relation))]
        MatrixOfVarM = [[model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="M_{}_{}".format(i, k)) for k in range(mcda_problemDescription.m)] for i in range(len(Relation))]

        for i in range(len(Relation)):
            object = Relation[i]
            object_covector = covectorOfPairWiseInformationWith2Levels(object)

            varL_i = MatrixOfVarE[i]
            varL_iDup = [np.array([vli] * mcda_problemDescription.m) for vli in varL_i]
            varL_iDupCovPI = [varL_iDup[i_] * LCovPIList[i_] for i_ in range(len(Relation))]
            Member_i_1 = [quicksum([elm[k] for elm in varL_iDupCovPI]) for k in range(mcda_problemDescription.m)]
            Member_i_2 = MatrixOfVarM[i]

            for k in range(mcda_problemDescription.m):
                model.addConstr(Member_i_1[k] + Member_i_2[k] == object_covector[k], name="KB_{}".format(i))
            model.update()

        Big_M = mcda_problemDescription.m + len(Relation)
        for i in range(len(Relation)):
            for j in range(len(Relation)):
                # https://www.leandro-coelho.com/linearization-product-variables/
                model.addConstr(MatrixOfVarE[i][j] <= Big_M * MatrixOfBoolVar[i][j], name="linearization_{}_{}_1".format(i, j))
                model.addConstr(MatrixOfVarE[i][j] <= MatrixOfCoeffVar[i][j], name="linearization_{}_{}_2".format(i, j))
                model.addConstr(MatrixOfVarE[i][j] >= MatrixOfCoeffVar[i][j] - (1 - MatrixOfBoolVar[i][j])*Big_M, name="linearization_{}_{}_2".format(i, j))
        model.update()

        for i in range(len(Relation)):
            for j in range(len(Relation)):
                model.addConstr(BaseVectorVar[i] >= MatrixOfBoolVar[j][i], name="not_in_base_{}_{}".format(i,j))

        if not(APrioriSelected is None):
            for i in range(len(Relation)):
                if APrioriSelected[i]:
                    model.addConstr(BaseVectorVar[i] == 1, name="selected_a_priori_{}".format(i))

        model.update()
        model.setObjective(quicksum(BaseVectorVar), GRB.MINIMIZE)
        model.optimize()

        # print of matrix (useful)
        # for i in range(len(Relation)):
        #     print(*[MatrixOfVarE[i][j].x for j in range(len(Relation))], sep=" ")
        # print("\n")

        return model.status == GRB.OPTIMAL, round(model.objVal), [i for i in range(len(Relation)) if round(BaseVectorVar[i].x) == 1]


