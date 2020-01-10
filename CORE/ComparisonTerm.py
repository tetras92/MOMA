import inspect
class ComparisonTerm:
    NO_TERM = "?"
    IS_PREFERRED_TO = ">"
    IS_LESS_PREFERRED_THAN = "<"
    IS_INDIFERRENT_TO = "~"

    @classmethod
    def terms(cls):
       return {x[0] : x[1] for x in inspect.getmembers(cls) if x[0].isupper()}


#print(ComparisonTerm.terms())