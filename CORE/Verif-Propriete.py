from gurobipy import *
from CORE.Tools import EPSILON
M = Model()

x1 = M.addVar(vtype=GRB.CONTINUOUS, lb=0.0)
x2 = M.addVar(vtype=GRB.CONTINUOUS, lb=0.0)
x3 = M.addVar(vtype=GRB.CONTINUOUS, lb=0.0)
x4 = M.addVar(vtype=GRB.CONTINUOUS, lb=0.0)
x5 = M.addVar(vtype=GRB.CONTINUOUS, lb=0.0)
x6 = M.addVar(vtype=GRB.CONTINUOUS, lb=0.0)
x7 = M.addVar(vtype=GRB.CONTINUOUS, lb=0.0)
x8 = M.addVar(vtype=GRB.CONTINUOUS, lb=0.0)
x9 = M.addVar(vtype=GRB.CONTINUOUS, lb=0.0)



M.update()
M.addConstr(x1 + x2 + EPSILON <= x4 + x5)
M.addConstr(x1 + EPSILON <= x6)
M.addConstr(x2 + EPSILON <= x6)
M.addConstr(x3 + EPSILON <= x4 + x5)
M.addConstr(x3 + EPSILON <= x5 + x6)
M.addConstr(x3 + EPSILON <= x4 + x6)
M.addConstr(x1 + x7 >= x4 + x8 + EPSILON)
M.addConstr(x2 + x8 >= x5 + x9 + EPSILON)
M.addConstr(x3 + x9 >= x6 + x7 + EPSILON)

M.addConstr(x1 + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9 == 1)
# M.addConstr(x1 + x2 + x3 + x4 + x5 + x6 == 1)

# M.addConstr(x4 + x5 + x6 + EPSILON <= x1 + x2 + x3)
# M.addConstr(x4 + x5 + x6 >= x1 + x2 + x3 + EPSILON)
M.addConstr(x2 >= x5 + x6 + EPSILON)
M.update()

# M.setObjective(x4 + x5 + x6 - x1 - x2 - x3, GRB.MAXIMIZE)
# M.setObjective(x4 + x5 + x6 - x1 - x2 - x3, GRB.MAXIMIZE)
M.update()
M.optimize()
print(M.display())

print(M.status == GRB.INFEASIBLE)
print(M.objVal)
