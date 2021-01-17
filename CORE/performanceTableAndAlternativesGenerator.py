import csv
import itertools as it
def generate(criteriaFileName, performanceTableName):
    # L : List[List[str]] Liste des listes d'attributs
    L = list()
    # LCritName : List[str]
    LCritName = list()
    if not type(criteriaFileName) is int :
        with open(criteriaFileName) as critFile:
            reader = csv.DictReader(critFile)
            print(reader.fieldnames)
            for row in reader:
                LA = [row['attribute1'], row['attribute2']]
                LCritName.append(row['name'])
                L.append(LA)
    else:
        n = int(criteriaFileName)
        name = f'CSVFILES/ijcai_criteria{n}.csv'
        with open(name, 'w') as criteriaFile:
            fieldnames = ['idAlt', 'name','attribute1','level1','symbol1','attribute2','level2','symbol2']
            writer = csv.DictWriter(criteriaFile, fieldnames=fieldnames)
            writer.writeheader()
            for criterionId in range(1, n+1):
                writer.writerow({'idAlt' : criterionId,
                                 'name' : f'var{criterionId}',
                                 'attribute1':'NO',
                                 'level1' : 0,
                                 'symbol1': '-',
                                 'attribute2': "YES",
                                 'level2':1,
                                 'symbol2':'+'})
        generate(name, performanceTableName)
        return

    with open(performanceTableName, 'w') as perfFile:
        fieldnames = ['idAlt'] + LCritName
        writer = csv.DictWriter(perfFile, fieldnames=fieldnames)
        writer.writeheader()
        # LTR : List[tuple[str]]]
        LTR = list(it.product(*L))
        # print(LTR)
        for elt in enumerate(LTR):
            indice, T = elt
            #indice += 1
            T_l = list(T)
            T_l.reverse()
            D = {fieldnames[0] : indice}
            for i in range(1, len(fieldnames)):
                D[fieldnames[i]] = T_l[i-1]
            writer.writerow(D)

if __name__ == "__main__" :
    for i in range(3, 4):
        generate(i, "CSVFILES/ijcai_fullPerfTable{}.csv".format(i))
