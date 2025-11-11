ALPHABETS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUMBERS = "0123456789"
WHITESPACES = " \n\t"

BASIC_TYPES = ["int", "bool", "str"]
GENERAL_KEYWORDS = ["if", "else", "while", "return", "break", "continue", "switch", "do", "extern", "defer"] # prune
TYPE_KEYWORDS = ["fn", "int", "str", "bool", "char", "void", "enum", "arr"]

ALLOWED_IN_NAMING = ALPHABETS + "_" + NUMBERS

ALLOWED = ALPHABETS + NUMBERS + WHITESPACES + "_" + "()[]{}" + "~`\"\':;,.|\\=^$#@"

def Literal(datatype, value): return {"type": "literal", "datatype": datatype, "value": value}
def Identifier(name): return {"type": "identifier", "value": name}
def Datatype(name): return {"type": "datatype", "value": name}

def determine_name(name): 
    if name in ["if", "else", "while", "return", "break", "continue", "extern"]: return Keyword(name)
    elif name in ["fn", "int", "str", "bool", "char"]: return Datatype(name)
    elif name in ["true", "false"]: return Literal("bool", name)
    return Identifier(name)