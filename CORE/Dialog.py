class Dialog:
    """Classe modélisant un 'élément' d'interaction entre le DM et le DA
     sous la forme d'un dialogue. Au cours de celui-ci, une information est
     présentée, sur laquelle le DM se prononce. La prise en compte de cette
     évaluation se fait par via la méthode madeWith et par effet de bord."""

    # NB : attribut static de la classe renseignant sur le nombre de sollicitations du DM
    NB = 0

    def __init__(self, info):
        Dialog.NB += 1
        self.info = info

    def madeWith(self, dm):
        dm.evaluate(self.info)
