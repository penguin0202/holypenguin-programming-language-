from dataclasses import dataclass
from ExpressionTypes import Expression
from lexer import Token, Position
from datatypes import DATATYPE

@dataclass
class BlockStatement(): 
    symbol_table: dict[str, DATATYPE]
    code: list["Statement"]
    position: Position

@dataclass
class EOFStatement(): 
    pass

@dataclass
class IntVarDeclStatement(): 
    name: Token
    position: Position

@dataclass
class BoolVarDeclStatement(): 
    name: Token
    position: Position
    
@dataclass
class BreakStatement(): 
    position: Position

@dataclass
class WhileStatement(): 
    condition: Expression
    statement: "Statement"
    position: Position

@dataclass
class IfElseStatement(): 
    condition: Expression
    if_statement: "Statement"
    else_statement: "Statement"
    position: Position

@dataclass
class IfStatement(): 
    condition: Expression
    statement: "Statement"
    position: Position

@dataclass
class ExpressionStatement(): 
    expression: Expression
    position: Position

Statement = BlockStatement | EOFStatement | IntVarDeclStatement | BoolVarDeclStatement \
    | BreakStatement | WhileStatement | IfElseStatement | IfStatement | ExpressionStatement

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