from CORE.PLNE_for_Delta11_decomposition import decompose as decompose_under_L0
from CORE.PLNE_for_Delta1m_decomposition import decompose as decompose_under_L1
from CORE.PLNE_for_Deltam1_decomposition import decompose as decompose_under_L2
from CORE.PLNE_for_Delta1m_m1_decomposition import decompose as decompose_under_L3


def recommendation_relaxation(AlternativesSubsetsList, Wdict, decomposition_function=None, kmax=2):
    SortedAlternativesSubsetsList = sorted(AlternativesSubsetsList,
                                           key=lambda alt: sum([Wdict[criterion] for criterion in alt]), reverse=True)
    print(SortedAlternativesSubsetsList)

    S = dict()
    k = 2
    while k <= kmax + 1:
        v = k
        while v <= len(SortedAlternativesSubsetsList):
            S[v] = dict()
            u = 1
            failure_uv = False
            while not failure_uv and u <= k - 1:
                proSet, conSet = SortedAlternativesSubsetsList[u - 1] - SortedAlternativesSubsetsList[v - 1], \
                                 SortedAlternativesSubsetsList[v - 1] - SortedAlternativesSubsetsList[u - 1]
                success_uv, Suv = decomposition_function(proSet, conSet, Wdict)
                print(SortedAlternativesSubsetsList[u - 1], "vs", SortedAlternativesSubsetsList[v - 1], "res", Suv)
                if not success_uv:
                    failure_uv = True
                    break
                S[v][u] = Suv
                u += 1
            if failure_uv:
                k += 1
                break
            v += 1
        if v <= len(SortedAlternativesSubsetsList):
            del S[v]
            continue

        return True, S

    return False, None


if __name__ == "__main__":
    # succ, R = recommendation_relaxation([{'b', 'f', 'g'}, {'c', 'd', 'e'}, {'a', 'd'}, {'c', 'e', 'g'}],
    #                                            {'a': 0.2462, 'b': 0.2423, 'c': 0.1480, 'd': 0.1135, 'e': 0.1,
    #                                             'f': 0.0788,
    #                                             'g': 0.0712}, decomposition_function=decompose_under_L0, kmax=2)
    succ, R = recommendation_relaxation([{'a', 'd', 'f'}, {'c', 'd', 'e', 'g'}, {'c', 'e', 'g'}, {'c', 'e', 'f'}],
                                        {'a': 128, 'b': 126, 'c': 77, 'd': 59, 'e': 52,
                                         'f': 41,
                                         'g': 37}, decomposition_function=decompose_under_L0, kmax=2)

    print(R)
