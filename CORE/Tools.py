from termcolor import colored
COLOR = "blue"
attribute_creator = lambda criterion, attribute_value : '{}:{}'.format(criterion,attribute_value)
colored_character = lambda c, o, color : colored(c, color) if c == o else c
colored_expression = lambda alternative1, alternative2 : ("".join([colored_character(alternative1[i], alternative2[i], COLOR) for i in range(len(alternative1))]),
                                                          "".join([colored_character(alternative2[i], alternative1[i], COLOR) for i in range(len(alternative1))]))
EPSILON = 0.000001                      #
CONSTRAINTSFEASIBILITYTOL = 0.000000001 # borne min dans Gurobi 1e-9
