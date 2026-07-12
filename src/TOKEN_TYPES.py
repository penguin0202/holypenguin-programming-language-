from enum import Enum, auto

class TokenType(Enum): 
    DEV_ERROR = auto(),
    DEV_PLACEHOLDER = auto(),
    EOF = auto(),
    UNKNOWN = auto(), 

    SEMICOLON = auto()

    KEYWORD_IF = auto(),
    KEYWORD_ELSE = auto(),
    KEYWORD_WHILE = auto(),
    KEYWORD_BREAK = auto(),

    DATATYPE_INT = auto(),
    DATATYPE_BOOL = auto(),

    LITERAL_BOOL_TRUE = auto(),
    LITERAL_BOOL_FALSE = auto()
    LITERAL_INT = auto(),
    LITERAL_STRING = auto(), # temporary to show that a string of characters exist, not an actual type

    IDENTIFIER = auto(), # can be a custom datatype
    ADD = auto(),
    SUB = auto(),
    MUL = auto(),
    DIV = auto(),
    MOD = auto(),
    
    ASSIGNER = auto(), 
    COMMA = auto(),
    L_BRACKET = auto(),
    R_BRACKET = auto(),
    L_PAREN = auto(),
    R_PAREN = auto(),
    
    GREATER_THAN = auto(),
    GREATER_THAN_OR_EQUAL_TO = auto(),
    LESS_THAN = auto(),
    LESS_THAN_OR_EQUAL_TO = auto(),
    EQUAL_TO = auto(),
    NOT_EQUAL_TO = auto(),
    NOT = auto(),
    AND = auto(),
    OR = auto(),