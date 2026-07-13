from dataclasses import dataclass
from lexer import Token, TokenType
from parser import Position

@dataclass
class IntLiteralExpression(): 
    int_literal: str
    position: Position
    
@dataclass
class BoolLiteralExpression(): 
    t: Token
    position: Position

@dataclass
class IdentifierExpression(): 
    t: Token
    position: Position

@dataclass
class NegateExpression(): 
    operand: "Expression"
    position: Position

@dataclass
class NotExpression(): 
    operand: "Expression"
    position: Position

@dataclass
class AssignmentExpression(): 
    lvalue: "Expression"
    rvalue: "Expression"
    position: Position

@dataclass
class BinaryExprExpression(): 
    operator: TokenType
    left: "Expression"
    right: "Expression"
    position: Position

Expression = IntLiteralExpression | BoolLiteralExpression | IdentifierExpression | NegateExpression | NotExpression | AssignmentExpression \
    | BinaryExprExpression

"""@dataclass
class FnCallExpression(): 
    name: "Expression"
    args: list["Expression"]"""

"""@dataclass
class UnaryAssignmentExpression(): 
    operator: str
    variable: "Expression"

@dataclass
class BinaryAssignmentExpression(): 
    operator: str
    variable: "Expression"
    value: "Expression"""