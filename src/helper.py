ALPHABETS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUMBERS = "0123456789"
WHITESPACES = " \n\t"

BASIC_TYPES = ["int", "bool", "str"]

ALLOWED_IN_NAMING = ALPHABETS + "_" + NUMBERS

ALLOWED = ALPHABETS + NUMBERS + WHITESPACES + "_" + "()[]{}" + "~`\"\':;,.|\\=^$#@"