def singleton(classe_definie):
    instances = {} # Dictionnaire de nos instances singletons
    def get_instance(*args, **kwargs):
        if classe_definie not in instances:
            # On crée notre premier objet de classe_definie
            instances[classe_definie] = classe_definie(*args, **kwargs)
        return instances[classe_definie]
    return get_instance
