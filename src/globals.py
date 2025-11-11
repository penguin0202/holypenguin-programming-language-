ALPHABETS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUMBERS = "0123456789"
WHITESPACES = " \n\t"

BASIC_TYPES = ["int", "bool", "str"]
GENERAL_KEYWORDS = ["if", "else", "while", "return", "break", "continue", "switch", "do", "extern", "defer"] # prune
TYPE_KEYWORDS = ["fn", "int", "str", "bool", "char", "void", "enum", "arr"]

ALLOWED_IN_NAMING = ALPHABETS + "_" + NUMBERS

ALLOWED = ALPHABETS + NUMBERS + WHITESPACES + "_" + "()[]{}" + "~`\"\':;,.|\\=^$#@"