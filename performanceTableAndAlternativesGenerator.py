import csv
import itertools as it
def generate(criteriaFileName, performanceTableName):
    # L : List[List[str]] Liste des listes d'attributs
    L = list()
    # LCritName : List[str]
    LCritName = list()
    with open(criteriaFileName) as critFile:
        reader = csv.DictReader(critFile)
        print(reader.fieldnames)
        for row in reader:
            LA = [row['attribute1'], row['attribute2']]
            LCritName.append(row['name'])
            L.append(LA)

    with open(performanceTableName, 'w') as perfFile:
        fieldnames = ['idAlt'] + LCritName
        writer = csv.DictWriter(perfFile, fieldnames=fieldnames)
        writer.writeheader()
        # LTR : List[tuple[str]]]
        LTR = list(it.product(*L))
        for elt in enumerate(LTR):
            indice, T = elt
            #indice += 1
            D = {fieldnames[0] : indice}
            for i in range(1, len(fieldnames)):
                D[fieldnames[i]] = T[i-1]
            writer.writerow(D)

if __name__ == "__main__" :
    generate("criteria.csv", "fullPerfTable.csv")
