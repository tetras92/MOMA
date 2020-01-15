class DMdoesntValidateNElementException(Exception):
    def __init__(self, info):
        Exception.__init__(self, "DM doesn't validate {}.".format(info))

    def __str__(self):
        return Exception.__str__(self)