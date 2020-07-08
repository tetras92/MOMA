import numpy as np
from gurobipy import *

from CORE.Tools import covectorOfPairWiseInformationWith2Levels


class NecessaryPreference:
    @staticmethod
    def adjudicate(mcda_problemDescription=None, Relation=None, object=(None, None)):
        if Relation is None:
            Relation = list()
        if object in Relation: return True
        elmt1, elmt2 = object

        if (elmt2, elmt1) in Relation: return False # Doit-on prendre garde à l'équivalence?       !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        model, VarMList = mcda_problemDescription.generate_kb_basic_gurobi_model_and_its_VarM("MOMA Necessary Preference")

        LCovPIList = [covectorOfPairWiseInformationWith2Levels(coupleAlt) for coupleAlt in Relation]
        VarMArray = np.array(VarMList)
        # varL = [model.addVar(vtype=GRB.INTEGER, lb=0, name="L_pi_".format(i)) for i in range(len(Relation))]
        varL = [model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="L_pi_".format(i)) for i in range(len(Relation))]

        # varN = model.addVar(vtype=GRB.INTEGER, lb=1, name="N")
        model.update()
        varLDup = [np.array([vl]*len(VarMArray)) for vl in varL]
        varLDupCovPI = [varLDup[i] * LCovPIList[i] for i in range(len(LCovPIList))]
        L2_1 = [quicksum([elm[i] for elm in varLDupCovPI]) for i in range(len(VarMArray))]
        L2_2 = VarMArray

        object_covector = covectorOfPairWiseInformationWith2Levels(object)
        # L1 = object_covector * np.array([varN]*len(object_covector))
        L1 = object_covector

        for i in range(len(object_covector)):
            # print(L1[i])
            # print(L2_1[i])
            # print(L2_2[i])
            model.addConstr(L2_1[i] + L2_2[i] == L1[i])
        # model.addConstr(varN == 1)
        model.update()
        model.optimize()
        # if model.status == GRB.OPTIMAL :
        #     xvarL = list()
        #     for va in varL :
        #         xvarL.append(va.x)
        #     xvarM = list()
        #     for va in VarMList:
        #         xvarM.append(va.x)
        #     if varN.x != 1: print("Boom", varN.x, object, "=", xvarL, xvarM)
            # print("NV", varN.x)

        # if (elmt1.id == 53 and elmt2.id == 15):
        #     print("========================================> FOund", model.status == GRB.OPTIMAL)
        #     if model.status == GRB.OPTIMAL :
        #         xvarL = list()
        #         for va in varL :
        #             xvarL.append(va.x)
        #         xvarM = list()
        #         for va in VarMList:
        #             xvarM.append(va.x)
        #         # if varN.x != 1: print("Boom", varN.x, object, "=", xvarL, xvarM)
        #         print("VarL", xvarL, "VarM", xvarM, "VarN", "covector", object_covector)
        # if (elmt1.id == 58 and elmt2.id == 23):
        #     print("========================================> FOundR", model.status == GRB.OPTIMAL)
            # if model.status == GRB.OPTIMAL :
            #     xvarL = list()
            #     for va in varL :
            #         xvarL.append(va.x)
            #     xvarM = list()
            #     for va in VarMList:
            #         xvarM.append(va.x)
            #     if varN.x != 1: print("Boom", varN.x, object, "=", xvarL, xvarM)
        return model.status == GRB.OPTIMAL
