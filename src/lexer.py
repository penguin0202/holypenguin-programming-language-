from TOKEN_TYPES import *
from dataclasses import dataclass, field
from copy import copy

# I am not caring about tab size right now regarding position tracking

@dataclass
class Position(): 
    row: int = 1
    col: int = 1
    def __str__(self):
        return f"(row: {self.row}, col: {self.col})"
    def __repr__(self): 
        return self.__str__()

@dataclass
class Token: 
    type: TokenType
    value: str|None
    position: Position
    def __str__(self):
        return f"type: {self.type.name}, value: {self.value}, position: {self.position}"
    def __repr__(self): 
        return self.__str__()

@dataclass
class Lexer(): 
    code: str # inputted
    i: int = 0
    position: Position = field(default_factory=Position)
    temp_token_position: Position = field(default_factory=Position)
    def store_token_position(self): 
        self.temp_token_position = copy(self.position)
    def EOF(self): 
        return self.i >= len(self.code)
    def peek(self) -> str|None: 
        return self.code[self.i] if not self.EOF() else None
    def advance(self) -> None: 
        self.i+=1
        self.position.col+=1
    def advance_line(self) -> None: 
        self.position.col=1
        self.position.row+=1
    def make_token(self, type: TokenType, value: str|None) -> Token: 
        return Token(type, value, copy(self.temp_token_position))
    def next_token(self) -> Token: 
        if self.EOF(): return self.make_token(TokenType.EOF, None)
        c: str = ' '
        while self.i < len(self.code): 
            c = self.peek()
            if c == ' ': 
                self.advance()
                continue
            if c == '\n': 
                self.advance()
                self.advance_line()
                continue
            if c == '/': 
                self.store_token_position()
                self.advance()

                if (c := self.peek()) == '/': 
                    # havent taken into account new line to end the comment or for the entire file
                    self.advance()
                    while self.i < len(self.code) and (c := self.peek()) != '\n': self.advance()
                    self.advance()
                    self.advance_line()
                    continue

                return self.make_token(TokenType.DIV, None)
            
            break

        if c in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ": 
            self.store_token_position()
            word: str = c
            self.advance()
            while (c := self.peek()) in "0123456789_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                word += c
                self.advance()
            match word: 
                case "if": return self.make_token(TokenType.KEYWORD_IF, None)
                case "else": return self.make_token(TokenType.KEYWORD_ELSE, None)
                case "while": return self.make_token(TokenType.KEYWORD_WHILE, None)
                case "break": return self.make_token(TokenType.KEYWORD_BREAK, None)
                # fn, return, continue, extern

                case "int": return self.make_token(TokenType.DATATYPE_INT, None)
                case "bool": return self.make_token(TokenType.DATATYPE_BOOL, None)

                case "true": return self.make_token(TokenType.LITERAL_BOOL, "true")
                case "false": return self.make_token(TokenType.LITERAL_BOOL, "false")

            return self.make_token(TokenType.IDENTIFIER, word)

        if c in "0123456789": # i dont care about floats anymore
            self.store_token_position()
            number = c
            self.advance()
            while (c := self.peek()) in "0123456789":
                number += c
                self.advance()
            return self.make_token(TokenType.LITERAL_INT, number)

        match c: 
            case '+': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.ADD, None)
            case '-': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.SUB, None)
            case '*': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.MUL, None)
            case '%': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.MOD, None)

            case '&': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.AND, None)
            case '?': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.OR, None)

            # blockers: function, while, if-else, dictionary, struct
            # blocker -> creates blocks / block makers
            case '{': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.L_BRACKET, None)
            case '}': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.R_BRACKET, None)

            # paren has expression grouper and function caller and function arger and possibly arrayer
            # expression grouper, function args grouper(func call too), possibly array
            case '(': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.L_PAREN, None)
            case ')': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.R_PAREN, None)
            
            case ';': 
                self.store_token_position()
                self.advance()
                return self.make_token(TokenType.SEMICOLON, None)
            
            case '<': 
                self.store_token_position()
                self.advance()
                if (c := self.peek()) == '=': 
                    self.advance()
                    return self.make_token(TokenType.LESS_THAN_OR_EQUAL_TO, None)
                return self.make_token(TokenType.LESS_THAN, None)

            case '>': 
                self.store_token_position()
                self.advance()
                if (c := self.peek()) == '=': 
                    self.advance()
                    return self.make_token(TokenType.GREATER_THAN_OR_EQUAL_TO, None)
                return self.make_token(TokenType.GREATER_THAN, None)

            case '!': 
                self.store_token_position()
                self.advance()
                if (c := self.peek()) == '=': 
                    self.advance()
                    return self.make_token(TokenType.NOT_EQUAL_TO, None)
                return self.make_token(TokenType.NOT, None)

            case '=': 
                self.store_token_position()
                self.advance()
                if (c := self.peek()) == '=': 
                    self.advance()
                    return self.make_token(TokenType.EQUAL_TO, None)
                return self.make_token(TokenType.ASSIGNER, None)

        raise SystemExit(f"IllegalCharError: {repr(c)} @ {self.position}")













"""case "\"": 
                string = ""
                while (char := self.advance()) != "\"":
                    if char != "\\": string += char
                    else: 
                        match char := self.advance(): 
                            case "": raise SystemExit("UnterminatedStringLiteral")
                            case "n": string += "\n"
                            case "t": string += "\t"
                            case "\\": string += "\\"
                            case "\"": string += "\""
                            case "\'": string += "\'"
                            # case "u" -> unicode: "\u2890"
                            case _: raise SystemExit("InvalidEscapeSequence")
                return Token(T_TYPES.LITERAL, string, "str")

            case "\'": 
                character = ""
                match char := self.advance(): 
                    case "": raise SystemExit("UnterminatedCharLiteral")
                    case "\'": raise SystemExit("EmptyCharLiteral")
                    case "\\": 
                        match char := self.advance():
                            case "": raise SystemExit("escape sequence started in a char, but eof (both escape sequence terminated, and char terminated because end ' not found)")
                            case "n": character += "\n"
                            case "t": character += "\t"
                            case "\\": character += "\\"
                            case "\"": character += "\""
                            case "\'": character += "\'"
                            # case "u" -> unicode: "\u2890"
                            case _: raise SystemExit("T_TYPES.INVALIDEscapeSequence")
                    case _: character += char
                assert not self.EOF(), "UnterminatedCharLiteral"
                assert self.advance() == "\'", "CharTooLong"
                return Token(T_TYPES.LITERAL, character, "char")"""

"""case "\\": raise SystemExit("Unexpected backslash outside of a string or char")
            case "#": raise SystemExit("NotImplementedError(dereference operator, but i dont want to deal with it right now)")
            case "@": raise SystemExit("NotImplementedError(address-of operator, but i dont want to deal with it right now)")

            case "$": raise SystemExit("NotImplementedError(idk what to do about ts right now)")
            case "^": raise SystemExit("NotImplementedError(idk what to do about ts right now)")
            case "`": raise SystemExit("NotImplementedError(idk what to do about ts right now)")
            case ":": raise SystemExit("NotImplementedError(i think this is going to be used in dictionaries, and in function named parameters)")"""

"""case ",": return Token(T_TYPES.DELIMITER, ",")"""

"""# squares have list-maker (accessor is using :, not [])
            # also int[64], 
            case "[": return Token(T_TYPES.DELIMITER, "[")
            case "]": return Token(T_TYPES.DELIMITER, "]")"""

"""case ".": raise Exception("NotImplementedError(used to be member access, but i scraped that)")"""

"""for strings: 

            case "~": 
                if self.peek() == "=": 
                    self.advance()
                    return Token(T_TYPES.OPERATOR, "~=")
                return Token(T_TYPES.OPERATOR, "~")"""