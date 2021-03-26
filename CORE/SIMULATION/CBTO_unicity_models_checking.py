import os
from CORE.SIMULATION.CBTOprocessing import regenerateCBTOfromModel

n = 5
# directory = f'SAMPLE-CBTO{n}'
directory = f'CoherentBooleanTermOrders{n}'

nbFile = os.listdir(directory)

CBTO_ALL_ORDERS = [None] + [regenerateCBTOfromModel(directory+f'/model{i}.csv', n) for i in range(1, len(os.listdir(directory))+1)]

print("c'est parti!", len(CBTO_ALL_ORDERS) - 1)
for i in range(1, len(CBTO_ALL_ORDERS)-1):
    if (i -1) % 1000 == 0: print(i)
    for j in range(i + 1, len(CBTO_ALL_ORDERS)):
        if CBTO_ALL_ORDERS[i] == CBTO_ALL_ORDERS[j]:
            print(f'Model {i} == {j} Model')


print("checked")
