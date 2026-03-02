from json_funcs import write_to_json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "test.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "lexed.txt")

# I am not caring about tab size right now regarding position tracking

code = []
with open(INPUT_FILENAME, "r") as file:
    code = list(file.read())
if code == []: raise Exception("FileEmptySoTokenEmpty")
tokens = []

i = 0

def EOF() -> bool: return i >= len(code)
def peek() -> str | None: return None if EOF() else code[i]
def advance() -> str | None: 
    char = peek()
    global i
    i+=1
    return char
def bare(token) -> dict: return {"type": token}

def next_token() -> dict: 
    match char := advance(): 
        case "+":
            if peek() == "+": 
                advance()
                return bare("++")
            elif peek() == "=": 
                advance()
                return bare("+=")
            return bare("+") # None because eof, or next char is not compatable
        
        case "-":
            if peek() == "-": 
                advance()
                return bare("--")
            elif peek() == "=": 
                advance()
                return bare("-=")
            return bare("-")
        
        case "*": 
            if peek() == "=": 
                advance()
                return bare("*=")
            return bare("*")
            
        case "/": 
            if peek() == "/": 
                advance()                     
                while peek() not in ["\n", None]: advance()
            elif peek() == "*": 
                advance()
                while True: 
                    assert not EOF(), "started to do a multi-line comment, but ended because eof"
                    if advance() == "*" and advance() == "/": break
                    # can eat everything in its path because it must end in those two characters
                    #, and we don't care about what the comment actually says
            elif peek() == "=": 
                advance()
                return bare("/=")
            return bare("/")
        
        case "%": 
            if peek() == "=": 
                advance()
                return bare("%=")
            return bare("%")

        case "<": 
            if peek() == "=": 
                advance()
                return bare("<=")
            return bare("<")
        
        case ">": 
            if peek() == "=": 
                advance()
                return bare(">=")
            return bare(">")

        case "&": 
            if peek() == "?": 
                advance()
                return bare("&?")
            return bare("&")

        case "?": return bare("?")

        case "!": 
            if peek() == "!": 
                advance()
                return bare("!!")
            elif peek() == "=": 
                advance()
                return bare("!=")
            return bare("!")

        case "~": 
            if peek() == "=": 
                advance()
                return bare("~=")
            return bare("~")

        case "=": 
            if peek() == "=": 
                advance()
                return bare("==")
            return bare("=")

        case ";": return bare(";")
        case ",": return bare(",")

        # paren has expression grouper and function caller and function arger and possibly arrayer
        # expression grouper, function args grouper(func call too), possibly array
        case "(": return bare("(")
        case ")": return bare(")")
        # squares have list-maker (accessor is using :, not [])
        # also int[64], 
        case "[": return bare("[")
        case "]": return bare("]")
        # blockers: function, while, if-else, dictionary, struct
        # blocker -> creates blocks / block makers
        case "{": return bare("{")
        case "}": return bare("}")

        case ".": raise Exception("NotImplementedError(used to be member access, but i scraped that)")

        case "\n" | "\t" | " ": return next_token()

        case "\"": 
            string = ""
            while (char := advance()) != "\"":
                if char != "\\": string += char
                else: 
                    match char := advance(): 
                        case None: raise Exception("UnterminatedStringLiteral")
                        case "n": string += "\n"
                        case "t": string += "\t"
                        case "\\": string += "\\"
                        case "\"": string += "\""
                        case "\'": string += "\'"
                        # case "u" -> unicode: "\u2890"
                        case _: raise Exception("InvalidEscapeSequence")
            return {"type": "literal", "datatype": "str", "value": string}

        case "\'": 
            character = ""
            match char := advance(): 
                case None: raise Exception("UnterminatedCharLiteral")
                case "\'": raise Exception("EmptyCharLiteral")
                case "\\": 
                    match char := advance():
                        case None: raise Exception("escape sequence started in a char, but eof (both escape sequence terminated, and char terminated because end ' not found)")
                        case "n": character += "\n"
                        case "t": character += "\t"
                        case "\\": character += "\\"
                        case "\"": character += "\""
                        case "\'": character += "\'"
                        # case "u" -> unicode: "\u2890"
                        case _: raise Exception("InvalidEscapeSequence")
                case _: character += char
            assert not EOF(), "UnterminatedCharLiteral"
            assert advance() == "\'", "CharTooLong"
            return {"type": "literal", "datatype": "char", "value": character}
        
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
                    char = peek()
                    if char not in "0123456789": break # None because eof or some other character
                    number += advance()
                return {"type": "literal", "datatype": "int", "value": number}
            elif char in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ": # name = keyword+identifier
                # identifiers (variables, functions), keywords, literal:bools
                name = char
                while peek() in "0123456789_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ": name += advance()
                if name in ["fn", "if", "else", "while", "return", "break", "continue", "extern"]: return {"type": "keyword", "value": name}
                elif name in ["int", "bool"]: return {"type": "datatype", "value": name}
                elif name in ["true", "false"]: return {"type": "literal", "datatype": "bool", "value": name}
                return {"type": "identifier", "value": name}
            raise Exception("IllegalCharError: " + repr(char))

while not EOF(): 
    tokens.append(next_token())

write_to_json(OUTPUT_FILENAME, tokens)