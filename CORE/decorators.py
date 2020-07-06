def singleton(classe_definie):
    instances = {} # Dictionnaire de nos instances singletons
    def get_instance(*args, **kwargs):
        if classe_definie not in instances:
            # On crée notre premier objet de classe_definie
            instances[classe_definie] = classe_definie(*args, **kwargs)
        return instances[classe_definie]
    return get_instance

def counting(counter):

    def decorator(function_to_modify):
        def modify_function(*args, **kwargs):
            counter.count()
            return function_to_modify(*args, **kwargs)
        return modify_function
    return decorator


