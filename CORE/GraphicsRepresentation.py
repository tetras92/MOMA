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
import numpy


def histogramme(D):
    ax = plt.subplot(111)
    x = sorted(D.keys())
    y = [D[a] for a in sorted(D.keys())]
    up = 0.1
    ax.bar(x, y, width=1.5, color='red')
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

# cpt = 0
# nb = 0
# with open("QuestionSimulation6.csv") as qSim:
#     reader = csv.DictReader(qSim)
#     for row in reader:
#         # if int(row['number_of_non_explainable']) + int(row['minimal_number_of_queries']) != int(row['all_explainable_minimal_number_of_queries']):
#         # if int(row['all_explainable_minimal_number_of_queries']) - int(row['minimal_number_of_queries']) >= int(row['minimal_number_of_queries']):
#         nb += 1
#         if int(row['critical_length']) == int(row['minimal_number_of_queries']):
#             cpt += 1
#             print(row['model'])
# print(cpt, "/", nb)
# model11446.csv # Ancien model11446.csv,10,6,1,8 # Nouveau model11446.csv,10,7,0,7
# model11083.csv # Ancien model11083.csv,10,7,1,7 # Nouveau model11083.csv,10,7,0,7
# model6815.csv  # Ancien model6815.csv,11,6,3,10 # Nouveau model6815.csv,11,7,2,9

# Modele with BCR = C
#  n = 4
# model1.csv : [('4', '123'), ('3', '12'), ('2', '1')]
# model2.csv [('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
# model7.csv [('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
# model8.csv [('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]


# n = 5
# model1.csv  [('5', '1234'), ('4', '123'), ('3', '12'), ('2', '1')]
# model2.csv  [('1234', '5'), ('5', '234'), ('4', '123'), ('3', '12'), ('2', '1')]
# model31.csv [('5', '1234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
# model32.csv [('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
# model230.csv [('5', '1234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
# model231.csv [('1234', '5'), ('5', '234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
# model256.csv [('5', '1234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]
# model257.csv [('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]

# n = 6
# model1.csv       [('6', '12345'), ('5', '1234'), ('4', '123'), ('3', '12'), ('2', '1')]
# model2.csv       [('12345', '6'), ('6', '2345'), ('5', '1234'), ('4', '123'), ('3', '12'), ('2', '1')]
# model315.csv     [('6', '12345'), ('1234', '5'), ('5', '234'), ('4', '123'), ('3', '12'), ('2', '1')]
# model316.csv     [('12345', '6'), ('6', '2345'), ('1234', '5'), ('5', '234'), ('4', '123'), ('3', '12'), ('2', '1')]
# model10691.csv   [('6', '12345'), ('5', '1234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
# model10692.csv   [('12345', '6'), ('6', '2345'), ('5', '1234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
# model10875.csv   [('6', '12345'), ('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
# model10876.csv   [('12345', '6'), ('6', '2345'), ('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('3', '12'), ('2', '1')]
# model58518.csv   [('6', '12345'), ('5', '1234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
# model58519.csv   [('12345', '6'), ('6', '2345'), ('5', '1234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
# model58704.csv   [('6', '12345'), ('1234', '5'), ('5', '234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
# model58705.csv   [('12345', '6'), ('6', '2345'), ('1234', '5'), ('5', '234'), ('4', '123'), ('12', '3'), ('3', '2'), ('2', '1')]
# model64282.csv   [('6', '12345'), ('5', '1234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]
# model64283.csv   [('12345', '6'), ('6', '2345'), ('5', '1234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]
# model64462.csv   [('6', '12345'), ('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]
# model64463.csv   [('12345', '6'), ('6', '2345'), ('1234', '5'), ('5', '234'), ('123', '4'), ('4', '23'), ('12', '3'), ('3', '2'), ('2', '1')]


# SERIES = list()
# with open("QuestionSimulation6.csv") as qSim:
#     reader = csv.DictReader(qSim)
#     for row in reader:
#         # SERIES.append(round(100 * int(row['minimal_number_of_queries']) / int(row['critical_length']), 2))
#         SERIES.append(int(row['minimal_number_of_queries']))
#
# SERIES.sort()
# # print("Minimum", min(SERIES), "%", "1er quartile", SERIES[len(SERIES)//4], "%", "Median", SERIES[len(SERIES)//2], "%","3e quartile", SERIES[3*len(SERIES)//4],"%", "Maximum", max(SERIES), "%",)
# print("Minimum", min(SERIES), "questions", "1er quartile", SERIES[len(SERIES)//4], "questions", "Median", SERIES[len(SERIES)//2], "questions","3e quartile", SERIES[3*len(SERIES)//4],"questions", "Maximum", max(SERIES), "questions", numpy.mean(SERIES))
#

# SERIES = list()
# with open("XP_TotalOrderJustification5.csv") as qSim:
#     reader = csv.DictReader(qSim)
#     for row in reader:
#         SERIES.append(round(100 * int(row['non_trivial_deduced_critical_pairs']) / int(row['minimal_number_of_queries']), 2))
#         # SERIES.append(int(row['minimal_number_of_queries']))
#
# SERIES.sort()
# print("Minimum", min(SERIES), "%", "1er quartile", SERIES[len(SERIES)//4], "%", "Median", SERIES[len(SERIES)//2], "%","3e quartile", SERIES[3*len(SERIES)//4],"%", "Maximum", max(SERIES), "%",)
# # print("Minimum", min(SERIES), "questions", "1er quartile", SERIES[len(SERIES)//4], "questions", "Median", SERIES[len(SERIES)//2], "questions","3e quartile", SERIES[3*len(SERIES)//4],"questions", "Maximum", max(SERIES), "questions", numpy.mean(SERIES))


# SERIES = list()
# with open("Metrics-For-Dialog-Values-m1-Decomposition-6.csv") as qSim:
#     reader = csv.DictReader(qSim)
#     for row in reader:
#         SERIES.append(float(row['metric-value-percent']))
#
# # print(SERIES)
# SERIES.sort()
# print("Minimum", min(SERIES), "%", "1er quartile", SERIES[len(SERIES) // 4], "%", "Median", SERIES[len(SERIES) // 2],
#       "%", "3e quartile", SERIES[3 * len(SERIES) // 4], "%", "Maximum", max(SERIES), "%", )
# print("Minimum", min(SERIES), "questions", "1er quartile", SERIES[len(SERIES)//4], "questions", "Median", SERIES[len(SERIES)//2], "questions","3e quartile", SERIES[3*len(SERIES)//4],"questions", "Maximum", max(SERIES), "questions", numpy.mean(SERIES))


# m = 9
# barWidth = 0.1
# y0 = [44.7, 40.3, 37.9, 35.7, 33.1, 32.2, 30.8, 29.9]
# y1 = [71.9, 71.7, 71.1, 70.6, 69.7, 69.4, 68.7, 68.3]
# y2 = [59.9, 54.6, 51.3, 48.3, 45.4, 44.1, 42.4, 41.1]
# y12 = [85.6, 84.6, 83.3, 82.2, 81.0, 80.4, 79.5, 78.5]
# y3 = [91.8, 90.3, 89.0, 88.1, 87.4, 86.9, 86.3, 85.8]
#
# yt3 = [91.9, 90.6, 89.5, 88.8, 88.2, 87.9, 87.3, 86.9]
#
# r0 = range(3, 11)
# r1 = [x + barWidth for x in r0]
# r2 = [x + 2*barWidth for x in r0]
# r12 = [x + 3*barWidth for x in r0]
# r3 = [x + 4*barWidth for x in r0]
#
# plt.bar(r0, y0, width = barWidth, color = ['gray' for i in y0],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L0")
# plt.bar(r1, y1, width = barWidth, color = ['pink' for i in y1],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L1")
# plt.bar(r2, y2, width = barWidth, color = ['yellow' for i in y2],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L2")
# plt.bar(r12, y12, width = barWidth, color = ['cyan' for i in y12],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L1 xor L2")
# plt.bar(r3, y3, width = barWidth, color = ['red' for i in y3],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L3")
#
# plt.bar(r3, [yt3[i] - y3[i] for i in range(len(y3))], width = barWidth, color = ['white' for i in y3],
#            edgecolor = ['red' for i in y1], linewidth =0.5, label="with transitivity", bottom=y3, hatch='/')
#
# plt.xticks([3 + r + 2*barWidth for r in range(len(y1))], ["n = " + str(n) for n in r0], rotation=45)
# # plt.ylabel("%")
# plt.yticks([10*i for i in range(11)], [f'{p}%' for p in range(0, 101, 10)])
# plt.grid(axis='y', linestyle='-')
# plt.legend()
# plt.title(f'Proportion d\'instances positives en fonction du langage (m = {m} critères)')
# plt.show()



# m = 8
# barWidth = 0.1
# y0 = [47.6, 44.8, 41.5, 39.1, 37.3, 36.7, 35.9, 35.1]
# y1 = [75.0, 74.9, 74.6, 74.1, 73.9, 73.5, 73.3, 73.1]
# y2 = [61.7, 57.7, 53.9, 51.0, 48.7, 47.6, 46.6, 45.3]
# y12 = [87.7, 86.9, 86.1, 85.1, 84.5, 83.7, 83.3, 82.6]
# y3 = [92.0, 90.7, 89.9, 89.2, 88.7, 88.2, 88.0, 87.4]
#
# yt3 = [92.1, 91.1, 90.5, 90.0, 89.6, 89.2, 89.1, 88.6]
#
# r0 = range(3, 11)
# r1 = [x + barWidth for x in r0]
# r2 = [x + 2*barWidth for x in r0]
# r12 = [x + 3*barWidth for x in r0]
# r3 = [x + 4*barWidth for x in r0]
#
# plt.bar(r0, y0, width = barWidth, color = ['gray' for i in y0],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L0")
# plt.bar(r1, y1, width = barWidth, color = ['pink' for i in y1],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L1")
# plt.bar(r2, y2, width = barWidth, color = ['yellow' for i in y2],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L2")
# plt.bar(r12, y12, width = barWidth, color = ['cyan' for i in y12],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L1 xor L2")
# plt.bar(r3, y3, width = barWidth, color = ['red' for i in y3],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L3")
#
# plt.bar(r3, [yt3[i] - y3[i] for i in range(len(y3))], width = barWidth, color = ['white' for i in y3],
#            edgecolor = ['red' for i in y1], linewidth =0.5, label="with transitivity", bottom=y3, hatch='/')
#
# plt.xticks([3 + r + 2*barWidth for r in range(len(y1))], ["n = " + str(n) for n in r0], rotation=45)
# # plt.ylabel("%")
# plt.yticks([10*i for i in range(11)], [f'{p}%' for p in range(0, 101, 10)])
# plt.grid(axis='y', linestyle='-')
# plt.legend()
# plt.title(f'Proportion d\'instances positives en fonction du langage (m = {m} critères)')
# plt.show()


# m = 7
# barWidth = 0.1
# y0 = [49.9, 48.0, 46.3, 43.5, 43.1, 42.9, 42.0, 42.4]
# y1 = [77.8, 78.7, 78.8, 78.4, 78.2, 78.3, 78.3, 78.3]
# y2 = [62.7, 59.4, 56.8, 53.6, 52.8, 52.7, 51.4, 51.4]
# y12 = [89.6, 89.5, 88.8, 88.0, 87.4, 87.6, 87.4, 87.0]
# y3 = [92.4, 91.9, 91.3, 90.7, 90.3, 90.5, 90.2, 89.9]
#
# yt3 = [92.5, 92.3, 92.0, 91.5, 91.2, 91.5, 91.3, 91.0]
#
# r0 = range(3, 11)
# r1 = [x + barWidth for x in r0]
# r2 = [x + 2*barWidth for x in r0]
# r12 = [x + 3*barWidth for x in r0]
# r3 = [x + 4*barWidth for x in r0]
#
# plt.bar(r0, y0, width = barWidth, color = ['gray' for i in y0],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L0")
# plt.bar(r1, y1, width = barWidth, color = ['pink' for i in y1],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L1")
# plt.bar(r2, y2, width = barWidth, color = ['yellow' for i in y2],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L2")
# plt.bar(r12, y12, width = barWidth, color = ['cyan' for i in y12],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L1 xor L2")
# plt.bar(r3, y3, width = barWidth, color = ['red' for i in y3],
#            edgecolor = ['black' for i in y1], linewidth =0.5, label="L3")
#
# plt.bar(r3, [yt3[i] - y3[i] for i in range(len(y3))], width = barWidth, color = ['white' for i in y3],
#            edgecolor = ['red' for i in y1], linewidth =0.5, label="with transitivity", bottom=y3, hatch='/')
#
# plt.xticks([3 + r + 2*barWidth for r in range(len(y1))], ["n = " + str(n) for n in r0], rotation=45)
# # plt.ylabel("%")
# plt.yticks([10*i for i in range(11)], [f'{p}%' for p in range(0, 101, 10)])
# plt.grid(axis='y', linestyle='-')
# plt.legend()
# plt.title(f'Proportion d\'instances positives en fonction du langage (m = {m} critères)')
# plt.show()


m = 6
barWidth = 0.1
y0 = [54.3, 53.0, 52.7, 52.4, 52.6, 53.2, 54.3, 58.4]
y1 = [72.2, 74.3, 75.3, 75.7, 76.4, 77.6, 78.6, 81.0]
y2 = [71.2, 67.7, 66.9, 65.7, 65.4, 65.1, 65.8, 68.3]
y12 = [88.7, 88.8, 89.2, 88.8, 89.2, 89.4, 90.0, 90.8]
y3 = [90.2, 90.2, 90.5, 90.2, 90.5, 90.4, 90.9, 91.4]

# yt3 = [90.5, 90.9, 91.3, 91.2, 91.4, 91.3, 91.7, 92.0] # transitivity

y0_relax = [73.6, 64.7, 60.6, 58.4, 57.6, 57.7, 58.3, 61.9]
y1_relax = [89.2, 86.6, 85.3, 84.7, 84.6, 85.1, 85.5, 86.8]
y2_relax = [89.3, 81.4, 77.2, 74.2, 72.3, 71.1, 71.1, 72.7]
y12_relax = [97.7, 96.1, 95.4, 94.4, 93.9, 93.7, 93.6, 93.7]
y3_relax = [98.2, 97.0, 96.4, 95.7, 95.2, 94.7, 94.6, 94.3]

r0 = range(3, 11)
r1 = [x + barWidth for x in r0]
r2 = [x + 2 * barWidth for x in r0]
r12 = [x + 3 * barWidth for x in r0]
r3 = [x + 4 * barWidth for x in r0]

plt.bar(r0, y0, width=barWidth, color=['gray' for i in y0], edgecolor=['black' for i in y1], linewidth=0.5, label="L0")
plt.bar(r0, [y0_relax[i] - y0[i] for i in range(len(y0))], edgecolor=['black' for i in y1], width=barWidth, color=['magenta' for i in y0], linewidth=0.5, bottom=y0)

plt.bar(r1, y1, width=barWidth, color=['pink' for i in y1], edgecolor=['black' for i in y1], linewidth=0.5, label="L1")
plt.bar(r1, [y1_relax[i] - y1[i] for i in range(len(y0))], edgecolor=['black' for i in y1], width=barWidth, color=['magenta' for i in y0], linewidth=0.5, bottom=y1)

plt.bar(r2, y2, width=barWidth, color=['yellow' for i in y2], edgecolor=['black' for i in y1], linewidth=0.5, label="L2")
plt.bar(r2, [y2_relax[i] - y2[i] for i in range(len(y0))], edgecolor=['black' for i in y1], width=barWidth, color=['magenta' for i in y0], linewidth=0.5, bottom=y2)

plt.bar(r12, y12, width=barWidth, color=['cyan' for i in y12], edgecolor=['black' for i in y1], linewidth=0.5, label="L1 xor L2")
plt.bar(r12, [y12_relax[i] - y12[i] for i in range(len(y0))] , edgecolor=['black' for i in y1], width=barWidth, color=['magenta' for i in y0], linewidth=0.5, bottom=y12)

plt.bar(r3, y3, width=barWidth, color=['red' for i in y3], edgecolor=['black' for i in y1], linewidth=0.5, label="L3")
plt.bar(r3, [y3_relax[i] - y3[i] for i in range(len(y0))], edgecolor=['black' for i in y1], width=barWidth, color=['magenta' for i in y0], linewidth=0.5, bottom=y3, label="with relaxation")

# plt.bar(r3, [yt3[i] - y3[i] for i in range(len(y3))], width = barWidth, color = ['white' for i in y3],
#            edgecolor = ['red' for i in y1], linewidth =0.5, label="with transitivity", bottom=y3, hatch='/') # transitivity


plt.xticks([3 + r + 2 * barWidth for r in range(len(y1))], ["n = " + str(n) for n in r0], rotation=45)
# plt.ylabel("%")
plt.yticks([10 * i for i in range(11)], [f'{p}%' for p in range(0, 101, 10)])
plt.grid(axis='y', linestyle='-')
plt.legend()
plt.title(f'Proportion d\'instances positives en fonction du langage (m = {m} critères)')
plt.show()
