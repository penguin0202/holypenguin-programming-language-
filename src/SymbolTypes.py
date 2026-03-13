from dataclasses import dataclass

@dataclass
class VarSymbol(): 
    datatype: str

class FnSymbol(): 
    def __init__(self): 
        self.set: list[] = []
    def add_set(self, datatype): 
        

@dataclass
class FnIndividualSymbol(): 
    datatypes: list[str]
    names: list[str]
    returns: str

Symbol = VarSymbol | FnSymbol