from dataclasses import dataclass

@dataclass
class LiteralExpression(): 
    datatype: str
    value: str

@dataclass
class IdentifierExpression(): 
    name: str

@dataclass
class NegateExpression(): 
    operand: "Expression"

@dataclass
class NotExpression(): 
    operand: "Expression"

@dataclass
class FnCallExpression(): 
    name: "Expression"
    args: list["Expression"]

@dataclass
class UnaryAssignmentExpression(): 
    operator: str
    variable: "Expression"

@dataclass
class BinaryAssignmentExpression(): 
    operator: str
    variable: "Expression"
    value: "Expression"

@dataclass
class BinaryExprExpression(): 
    operator: str
    left: "Expression"
    right: "Expression"

Expression = LiteralExpression | IdentifierExpression | NegateExpression | NotExpression | FnCallExpression\
    | UnaryAssignmentExpression | BinaryAssignmentExpression | BinaryExprExpression