from gurobipy import *

from CORE.ProblemDescription import ProblemDescription
from CORE.Tools import CONSTRAINTSFEASIBILITYTOL, covectorOfPairWiseInformationWith2Levels

gurobi_model = Model("Test")


gurobi_model.setParam('OutputFlag', False)
gurobi_model.Params.FeasibilityTol = CONSTRAINTSFEASIBILITYTOL
gurobi_model.Params.DualReductions = 0   # indispensable pour discriminer entre PL InFeasible or unBounded
# Borne sup choisie arbitrairement égale à 1 (UTA GMS).
VarList = [gurobi_model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=0.5)
           for i in range(6)]
gurobi_model.update()

mcda_problem_description = ProblemDescription(criteriaFileName="CSVFILES/criteria.csv",
                                                  performanceTableFileName="CSVFILES/PerfTable4+.csv")

print(mcda_problem_description)
gurobi_model.addConstr(quicksum(covectorOfPairWiseInformationWith2Levels((mcda_problem_description[15], mcda_problem_description[58]))
                       * VarList) >= 0)

gurobi_model.addConstr(quicksum(covectorOfPairWiseInformationWith2Levels((mcda_problem_description[58], mcda_problem_description[53]))
                       * VarList) >= 0)

gurobi_model.addConstr(quicksum(covectorOfPairWiseInformationWith2Levels((mcda_problem_description[60], mcda_problem_description[46]))
                       * VarList) >= 0)

gurobi_model.addConstr(quicksum(covectorOfPairWiseInformationWith2Levels((mcda_problem_description[23], mcda_problem_description[27]))
                       * VarList) >= 0)

gurobi_model.setObjective(quicksum(covectorOfPairWiseInformationWith2Levels((mcda_problem_description[15], mcda_problem_description[53]))
                       * VarList), GRB.MINIMIZE)
gurobi_model.update()

gurobi_model.optimize()

print("OptSOl", gurobi_model.objVal)
