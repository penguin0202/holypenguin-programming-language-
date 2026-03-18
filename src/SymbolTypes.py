from dataclasses import dataclass

@dataclass
class VarSymbol(): 
    datatype: str

class FnSymbol(): 
    def __init__(self, datatypes, names, returns): 
        self.overloads: list[FnSetItem] = []
        self.add_overload(datatypes, names, returns)
    
    def add_overload(self, datatypes, names, returns): 
        self.overloads.append(FnSetItem(datatypes, names, returns))

@dataclass
class FnSetItem(): 
    datatypes: list[str]
    names: list[str]
    returns: str

Symbol = VarSymbol | FnSymbol