from StatementTypes import *

class Transpiler(): 
    def transpile_statement(self, statement: Statement) -> str: 
        match statement: 
            case ModuleStatement(): 
                pycode = ""
                