class DMdoesntValidateNElementException(Exception):
    """Classe modélisant une Exception correspondant à la rupture de calcul
    souhaitée lorsque le DM conteste un élément de la relation nécessaire."""
    def __init__(self, dominanceObject):
        Exception.__init__(self, "DM doesn't validate {}.".format(dominanceObject))
        self.dominanceObject = dominanceObject

    def __str__(self):
        return Exception.__str__(self)
