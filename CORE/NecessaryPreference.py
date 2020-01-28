import numpy as np
from gurobipy import *

from CORE.Tools import covectorOfPairWiseInformationWith2Levels


class NecessaryPreference:
    @staticmethod
    def adjudicate(mcda_problemDescription=None, Relation=list(), object=(None, None)):
        if object in Relation: return True
        elmt1, elmt2 = object
        if (elmt2, elmt1) in Relation :  return False # Dois-on prendre garde à l'équivalence?
        model, VarMList = mcda_problemDescription.generate_kb_basic_gurobi_model_and_its_VarM("MOMA Necessary Preference")

        LCovPIList = [covectorOfPairWiseInformationWith2Levels(coupleAlt) for coupleAlt in Relation]
        VarMArray = np.array(VarMList)
        varL = [model.addVar(vtype=GRB.INTEGER, lb=0, name="L_pi_".format(i)) for i in range(len(Relation))]
        varN = model.addVar(vtype=GRB.INTEGER, lb=1, name="N")
        model.update()
        varLDup = [np.array([vl]*len(VarMArray)) for vl in varL]
        varLDupCovPI = [varLDup[i] * LCovPIList[i] for i in range(len(LCovPIList))]
        L2_1 = [quicksum([elm[i] for elm in varLDupCovPI]) for i in range(len(VarMArray))]
        L2_2 = VarMArray

        object_covector = covectorOfPairWiseInformationWith2Levels(object)
        L1 = object_covector * np.array([varN]*len(object_covector))

        for i in range(len(object_covector)):
            model.addConstr(L1[i] == L2_1[i] + L2_2[i])

        model.update()
        model.optimize()
        return model.status == GRB.OPTIMAL
