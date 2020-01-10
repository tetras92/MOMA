class Dialog:
    NB = 0
    def __init__(self, info):
        Dialog.NB += 1
        self.info = info

    def madeWith(self, dm):
        #print("Dialog {} : \n\t{}".format(Dialog.NB, self.info))
        dm.evaluate(self.info)