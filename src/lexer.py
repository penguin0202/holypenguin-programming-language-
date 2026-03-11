from json_funcs import write_to_json
import os
from TOKEN_TYPES import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "test.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "lexed.txt")

# I am not caring about tab size right now regarding position tracking

class Token: 
    def __init__(self, type:int, value:str, datatype:str=None): 
        self._type = type
        self._value = value
        self._datatype = datatype
    
    @classmethod
    def EOF(cls): 
        return Token(T_TYPES.INVALID, "EOF")
    
    @property # read-only property
    def type(self):
        return self._type 
    @property
    def value(self): 
        return self._value
    @property
    def datatype(self): 
        return self._datatype
    
    def __str__(self) -> str: 
        return 
    
    def __eq__(self, other: "Token"): 
        return self.type == other.type and self.value == other.value and self.datatype == other.datatype

class Lexer(): 
    def __init__(self, filename:str) -> None: 
        self.tokens: list[Token] = []
        self.index: int = 0
        with open(filename, "r") as file: 
            self.code:list[str] = file.read()
    def __str__(self) -> str: 
        return self.code
    def EOF(self) -> bool: 
        return self.index >= len(self.code)
    def peek(self) -> str: 
        return "" if self.EOF() else self.code[self.index]
    def advance(self) -> str: 
        char = self.peek()
        self.index+=1
        return char
    def next_token(self) -> Token: 
        match char := self.advance(): 
            case "": return Token.EOF()
            case "+":
                if self.peek() == "+": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "++")
                elif self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "+=")
                return Token(T_TYPES.OPERATOR, "+") # None because eof, or next char is not compatable
            
            case "-":
                if self.peek() == "-": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "--")
                elif self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "-=")
                return Token(T_TYPES.OPERATOR, "-")
            
            case "*": 
                if self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "*=")
                return Token(T_TYPES.OPERATOR, "*")
                
            case "/": 
                if self.peek() == "/": 
                    self.advance()                     
                    while self.peek() not in ["\n", None]: self.advance()
                elif self.peek() == "*": 
                    self.advance()
                    while True: 
                        assert not self.EOF(), "started to do a multi-line comment, but ended because eof"
                        if self.advance() == "*" and self.advance() == "/": break
                        # can eat everything in its path because it must end in those two characters
                        #, and we don't care about what the comment actually says
                elif self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "/=")
                return Token(T_TYPES.OPERATOR, "/")
            
            case "%": 
                if self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "%=")
                return Token(T_TYPES.OPERATOR, "%")

            case "<": 
                if self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "<=")
                return Token(T_TYPES.OPERATOR, "<")
            
            case ">": 
                if self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, ">=")
                return Token(T_TYPES.OPERATOR, ">")

            case "&": 
                if self.peek() == "?": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "&?")
                return Token(T_TYPES.OPERATOR, "&")

            case "?": return Token(T_TYPES.OPERATOR, "?")

            case "!": 
                if self.peek() == "!": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "!!")
                elif self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "!=")
                return Token(T_TYPES.OPERATOR, "!")

            case "~": 
                if self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "~=")
                return Token(T_TYPES.OPERATOR, "~")

            case "=": 
                if self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "==")
                return Token(T_TYPES.OPERATOR, "=")

            case ";": return Token(T_TYPES.DELIMITER, ";")
            case ",": return Token(T_TYPES.DELIMITER, ",")

            # paren has expression grouper and function caller and function arger and possibly arrayer
            # expression grouper, function args grouper(func call too), possibly array
            case "(": return Token(T_TYPES.DELIMITER, "(")
            case ")": return Token(T_TYPES.DELIMITER, ")")
            # squares have list-maker (accessor is using :, not [])
            # also int[64], 
            case "[": return Token(T_TYPES.DELIMITER, "[")
            case "]": return Token(T_TYPES.DELIMITER, "]")
            # blockers: function, while, if-else, dictionary, struct
            # blocker -> creates blocks / block makers
            case "{": return Token(T_TYPES.DELIMITER, "{")
            case "}": return Token(T_TYPES.DELIMITER, "}")

            case ".": raise Exception("NotImplementedError(used to be member access, but i scraped that)")

            case "\n" | "\t" | " ": return self.next_token()

            case "\"": 
                string = ""
                while (char := self.advance()) != "\"":
                    if char != "\\": string += char
                    else: 
                        match char := self.advance(): 
                            case "": raise Exception("UnterminatedStringLiteral")
                            case "n": string += "\n"
                            case "t": string += "\t"
                            case "\\": string += "\\"
                            case "\"": string += "\""
                            case "\'": string += "\'"
                            # case "u" -> unicode: "\u2890"
                            case _: raise Exception("InvalidEscapeSequence")
                return Token(T_TYPES.LITERAL, string, "str")

            case "\'": 
                character = ""
                match char := self.advance(): 
                    case "": raise Exception("UnterminatedCharLiteral")
                    case "\'": raise Exception("EmptyCharLiteral")
                    case "\\": 
                        match char := self.advance():
                            case "": raise Exception("escape sequence started in a char, but eof (both escape sequence terminated, and char terminated because end ' not found)")
                            case "n": character += "\n"
                            case "t": character += "\t"
                            case "\\": character += "\\"
                            case "\"": character += "\""
                            case "\'": character += "\'"
                            # case "u" -> unicode: "\u2890"
                            case _: raise Exception("T_TYPES.INVALIDEscapeSequence")
                    case _: character += char
                assert not self.EOF(), "UnterminatedCharLiteral"
                assert self.advance() == "\'", "CharTooLong"
                return Token(T_TYPES.LITERAL, character, "char")
            
            case "\\": raise Exception("Unexpected backslash outside of a string or char")
            case "#": raise Exception("NotImplementedError(dereference operator, but i dont want to deal with it right now)")
            case "@": raise Exception("NotImplementedError(address-of operator, but i dont want to deal with it right now)")

            case "$": raise Exception("NotImplementedError(idk what to do about ts right now)")
            case "^": raise Exception("NotImplementedError(idk what to do about ts right now)")
            case "`": raise Exception("NotImplementedError(idk what to do about ts right now)")
            case ":": raise Exception("NotImplementedError(i think this is going to be used in dictionaries, and in function named parameters)")

            case _: 
                if char in "0123456789": # i dont care about floats anymore
                    number = char
                    while True:
                        char = self.peek()
                        if char not in "0123456789": break # None because eof or some other character
                        number += self.advance()
                    return Token(T_TYPES.LITERAL, number, datatype="int")
                elif char in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ": # name = keyword+identifier
                    # identifiers (variables, functions), keywords, literal:bools
                    name = char
                    while self.peek() in "0123456789_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ": name += self.advance()
                    if name in ["fn", "if", "else", "while", "return", "break", "continue", "extern"]: return Token(T_TYPES.KEYWORD, name)
                    elif name in ["int", "bool"]: return Token(T_TYPES.DATATYPE, name)
                    elif name in ["true", "false"]: return Token(T_TYPES.LITERAL, name, datatype="bool")
                    return Token(T_TYPES.IDENTIFIER, name)
                raise Exception("IllegalCharError: " + repr(char))