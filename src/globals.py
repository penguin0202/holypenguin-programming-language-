class Symbols(): 
    DOUBLE_QUOTES = "\""
    SINGLE_QUOTES = "\'"
    NEWLINE = "\n"
    TAB = "\t"
    MINUS = "-"
    ADD = "+"
    EQUALS = "="
    DIV = "/"
    STAR = "*"
    AND = "&"
    QUESTION = "?"
    PERCENT = "%"
    DOUBLE_DIV = "//"
    NOTHING = ""
    SMALLER_THAN = "<"
    BIGGER_THAN = ">"
    EXCLAMATION = "!"
    TILDA = "~"
    DOT = "."
    SEMICOLON = ";"
    COMMA = ","
    UNDERSCORE = "_"
    SPACE = " "
    COLON = ":"
    AT = "@"
    PIPE = "|"
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_CURLY = "{"
    RIGHT_CURLY = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"

LOWERCASE_ALPHABETS = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE_ALPHABETS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALL_ALPHABETS = LOWERCASE_ALPHABETS + UPPERCASE_ALPHABETS
NUMBERS = "0123456789"
WHITESPACES = Symbols.SPACE + Symbols.NEWLINE + Symbols.TAB
BRACKETS = "()[]{}"



BASIC_TYPES = ["int", "bool", "str"]
GENERAL_KEYWORDS = ["if", "else", "while", "return", "break", "continue", "switch", "do", "extern", "defer"] # prune
TYPE_KEYWORDS = ["fn", "int", "str", "bool", "char", "void", "enum", "arr"]
builtin_fn = ["print", "input"]
NUM_OPERATORS = "+-*/%"
BOOL_OPERATORS = "!?&"
COMPARISON_OPERATORS = "<>"

ALLOWED_IN_NAMING = ALL_ALPHABETS + NUMBERS + Symbols.UNDERSCORE

ALLOWED = ALL_ALPHABETS + NUMBERS + WHITESPACES + Symbols.UNDERSCORE + BRACKETS + NUM_OPERATORS + BOOL_OPERATORS + COMPARISON_OPERATORS + "~`\"\':;,.|\\=^$#@"