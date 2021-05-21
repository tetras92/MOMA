import csv
import matplotlib.pyplot as plt

# with open("QuestionSimulation5.csv") as qSim:
#     reader = csv.DictReader(qSim)
#     for row in reader:
#         if int(row['all_questions']) / int(row['criticalLength']) > 1.5 :
#             print(row['model'])

# model140.csv
# model141.csv
# model206.csv
# model435.csv
# model341.csv
# model144.csv
# model198.csv *
# model229.csv
# model145.csv
# model138.csv
# model136.csv
# model457.csv
# model139.csv
# model342.csv
# model200.csv
# model456.csv
# model137.csv
# model132.csv
# model11.csv
# model434.csv
# model134.csv
# model228.csv
# model208.csv
# model169.csv
# model168.csv

def histogramme(D):
    ax = plt.subplot(111)
    x = sorted(D.keys())
    y = [D[a] for a in sorted(D.keys())]
    up = 0.1
    ax.bar(x, y, width=1.5, color='red' )
    # Add text to bars
    for xi, yi, l in zip(*[x, y, list(map(str, y))]):
        ax.text(xi - len(l) * .02, yi + up, l,
                bbox=dict(alpha=.5))

    plt.xticks(sorted(D.keys()), [f'{a}%' for a in sorted(D.keys())], rotation=70)
    plt.xlabel('Pourcentages (%) de questions supplémentaires')
    plt.ylabel('Nombre de modèles')

    plt.show()

# M_4_n_5 = {0: 86, 12: 4, 14: 17, 16: 21, 20: 26, 25: 3, 28: 29, 33: 70, 40: 60, 42: 3, 50: 39, 60: 98, 66: 12, 75: 5, 80: 34, 100: 7, 125: 2}
# histogramme(M_4_n_5)
# M_4_n_6 = {0: 454, 7: 1, 9: 19, 10: 70, 11: 109, 12: 175, 14: 204, 15: 2, 16: 100, 18: 20, 20: 99, 22: 306, 23: 1, 25: 561, 27: 25, 28: 641, 30: 55, 33: 431, 36: 47, 37: 513, 40: 152, 41: 4, 42: 952, 44: 247, 45: 22, 50: 988, 53: 1, 54: 11, 55: 274, 57: 805, 58: 1, 60: 82, 61: 4, 62: 539, 63: 22, 66: 692, 69: 2, 70: 80, 71: 686, 72: 39, 75: 700, 76: 1, 77: 239, 80: 97, 81: 35, 83: 501, 84: 4, 85: 975, 87: 550, 88: 301, 90: 245, 91: 20, 92: 1, 100: 3367, 108: 15, 109: 93, 110: 355, 111: 641, 112: 904, 114: 1007, 115: 1, 116: 1066, 118: 63, 120: 340, 122: 758, 125: 1333, 127: 55, 128: 1235, 130: 290, 133: 1998, 136: 52, 137: 1659, 140: 241, 142: 1713, 144: 850, 145: 68, 150: 3022, 154: 42, 155: 782, 157: 2289, 160: 281, 162: 2305, 163: 20, 166: 1693, 170: 312, 171: 2918, 172: 5, 175: 2132, 177: 654, 180: 144, 183: 1231, 185: 3666, 187: 2077, 188: 920, 190: 58, 200: 8691, 210: 1, 211: 412, 212: 1807, 214: 3750, 216: 2596, 220: 10, 222: 178, 225: 2441, 228: 3644, 233: 3350, 237: 1919, 240: 14, 242: 3296, 244: 1, 250: 4423, 257: 3216, 260: 9, 262: 377, 266: 3466, 271: 4112, 275: 58, 280: 17, 283: 3272, 285: 2996, 287: 2, 300: 4046, 314: 523, 316: 2798, 320: 10, 328: 78, 333: 3364, 340: 19, 342: 1, 350: 2226, 360: 11, 366: 891, 380: 8, 383: 257, 400: 60, 416: 1, 420: 17, 440: 23, 460: 25, 480: 7, 500: 4}
# histogramme(M_4_n_6)


with open("QuestionSimulation6.csv") as qSim:
    reader = csv.DictReader(qSim)
    for row in reader:
        if int(row['number_of_non_explainable']) + int(row['minimal_number_of_queries']) != int(row['all_explainable_minimal_number_of_queries']):
            print(row['model'])

# model11446.csv # Ancien model11446.csv,10,6,1,8 # Nouveau model11446.csv,10,7,0,7
# model11083.csv # Ancien model11083.csv,10,7,1,7 # Nouveau model11083.csv,10,7,0,7
# model6815.csv  # Ancien model6815.csv,11,6,3,10 # Nouveau model6815.csv,11,7,2,9
