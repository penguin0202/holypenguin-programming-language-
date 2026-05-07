from dataclasses import dataclass
from parser import Expression, Block, FnSignature

@dataclass
class ModuleStatement(): 
    block: Block

@dataclass
class BlockStatement(): 
    block: Block

@dataclass
class VarDeclStatement(): 
    name: str
    datatype: str

@dataclass
class FnDeclStatement(): 
    fn_signature: FnSignature
    block: Block

@dataclass
class ExternFnStatement(): 
    fn_signature: FnSignature

@dataclass
class BreakStatement(): 
    pass

@dataclass
class ContinueStatement(): 
    pass

@dataclass
class ReturnStatement(): 
    value: Expression

@dataclass
class WhileStatement(): 
    condition: Expression
    block: Block

@dataclass
class IfElseStatement(): 
    condition: Expression
    then_block: Block
    else_block: Block

@dataclass
class IfStatement(): 
    condition: Expression
    block: Block

@dataclass
class ExpressionStatement(): 
    expression: Expression

Statement = BlockStatement | VarDeclStatement | FnDeclStatement | ExternFnStatement\
    | BreakStatement | ContinueStatement | ReturnStatement | WhileStatement | IfElseStatement\
    | ExpressionStatement | ModuleStatement | IfStatement