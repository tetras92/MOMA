class Dialog:
    NB = 0
    def __init__(self, ao):
        Dialog.NB += 1
        self.ao = ao

    def madeWith(self, dm):
        dm.evaluate(self.ao)