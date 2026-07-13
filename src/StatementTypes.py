from dataclasses import dataclass
from parser import Expression, Block, FnSignature
from lexer import Token

@dataclass
class ModuleStatement(): 
    block: Block

@dataclass
class BlockStatement(): 
    block: Block

@dataclass
class EOFStatement(): 
    pass

@dataclass
class IntVarDeclStatement(): 
    name: Token

@dataclass
class BoolVarDeclStatement(): 
    name: Token
    
@dataclass
class BreakStatement(): 
    pass

@dataclass
class WhileStatement(): 
    condition: Expression
    statement: "Statement"

@dataclass
class IfElseStatement(): 
    condition: Expression
    if_statement: "Statement"
    else_statement: "Statement"

@dataclass
class IfStatement(): 
    condition: Expression
    statement: "Statement"

@dataclass
class ExpressionStatement(): 
    expression: Expression

Statement = BlockStatement | VarDeclStatement | FnDeclStatement | ExternFnStatement\
    | BreakStatement | ContinueStatement | ReturnStatement | WhileStatement | IfElseStatement\
    | ExpressionStatement | ModuleStatement | IfStatement

"""@dataclass
class FnDeclStatement(): 
    fn_signature: FnSignature
    block: Block

@dataclass
class ExternFnStatement(): 
    fn_signature: FnSignature"""

"""@dataclass
class ContinueStatement(): 
    pass"""

"""@dataclass
class ReturnStatement(): 
    value: Expression"""