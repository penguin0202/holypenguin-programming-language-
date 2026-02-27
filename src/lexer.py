from helper import *
from json_funcs import write_to_json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "test.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "lexed.txt")

# I am not caring about tab size right now regarding position tracking

def isDigit(thing) -> bool: return thing in NUMBERS
def isAlpha(thing) -> bool: return thing in ALLOWED_IN_NAMING # includes underscore AND NUMBERS? WHAT THE HELL WERE YOU THINKING

code = []
with open(INPUT_FILENAME, "r") as file:
    code = list(file.read())
if code == []: raise Exception("FileEmptySoTokenEmpty")
tokens = []

def EOF() -> bool: return len(code) == 0
def consume() -> dict: return None if EOF() else code.pop(0)
def peek() -> dict: return None if EOF() else code[0]
def push(token) -> None: tokens.append({"type": token})
def push_complicated(token) -> None: tokens.append(token)
def peek_is(token) -> bool: return peek() == token

while not EOF(): 
    match char := consume(): 
        case "+":
            if peek_is("+"): 
                consume()
                push("++")
            elif peek_is("="): 
                consume()
                push("+=")
            else: push("+") # None because eof, or next char is not compatable
        
        case "-":
            if peek_is("-"): 
                consume()
                push("--")
            elif peek_is("="): 
                consume()
                push("-=")
            else: push("-")
        
        case "*": 
            if peek_is("="): 
                consume()
                push("*=")
            else: push("*")
            
        case "/": 
            if peek_is("/"): 
                consume()                       
                while peek() not in ["\n", None]: consume()
            elif peek_is("*"): 
                consume()
                while True: 
                    assert not EOF(), "started to do a multi-line comment, but ended because eof"
                    if consume() == "*" and consume() == "/": break
            elif peek_is("="): 
                consume()
                push("/=")
            else: push("/")
        
        case "%": 
            if peek_is("="): 
                consume()
                push("%=")
            else: push("%")

        case "<": 
            if peek_is("="): 
                consume()
                push("<=")
            else: push("<")
        
        case ">": 
            if peek_is("="): 
                consume()
                push(">=")
            else: push(">")

        case "&": 
            if peek_is("?"): 
                consume()
                push("&?")
            else: push("&")

        case "?": push("?")

        case "!": 
            if peek_is("!"): 
                consume()
                push("!!")
            elif peek_is("="): 
                consume()
                push("!=")
            else: push("!")

        case "~": 
            if peek_is("="): 
                consume()
                push("~=")
            else: push("~")

        case "=": 
            if peek_is("="): 
                consume()
                push("==")
            else: push("=")

        case ";": push(";")
        case ",": push(",")

        # paren has expression grouper and function caller and function arger and possibly arrayer
        # expression grouper, function args grouper(func call too), possibly array
        case "(": push("(")
        case ")": push(")")
        # squares have list-maker (accessor is using :, not [])
        # also int[64], 
        case "[": push("[")
        case "]": push("]")
        # blockers: function, while, if-else, dictionary, struct
        # blocker -> creates blocks / block makers
        case "{": push("{")
        case "}": push("}")

        case ".": raise Exception("NotImplementedError(used to be member access, but i scraped that)")

        case "\n" | "\t" | " ": pass

        case "\"": 
            string = ""
            while (char := consume()) != "\"":
                if char != "\\": string += char
                else: 
                    match char := consume(): 
                        case None: raise Exception("UnterminatedStringLiteral")
                        case "n": string += "\n"
                        case "t": string += "\t"
                        case "\\": string += "\\"
                        case "\"": string += "\""
                        case "\'": string += "\'"
                        # case "u" -> unicode: "\u2890"
                        case _: raise Exception("InvalidEscapeSequence")
            push_complicated(Literal("str", string))

        case "\'": 
            character = ""
            match char := consume(): 
                case None: raise Exception("UnterminatedCharLiteral")
                case "\'": raise Exception("EmptyCharLiteral")
                case "\\": 
                    match char := consume():
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
            assert consume() == "\'", "CharTooLong"
            push_complicated(Literal("char", character))
        
        case "\\": raise Exception("Unexpected backslash outside of a string or char")
        case "#": raise Exception("NotImplementedError(dereference operator, but i dont want to deal with it right now)")
        case "@": raise Exception("NotImplementedError(address-of operator, but i dont want to deal with it right now)")

        case "$": raise Exception("NotImplementedError(idk what to do about ts right now)")
        case "^": raise Exception("NotImplementedError(idk what to do about ts right now)")
        case "`": raise Exception("NotImplementedError(idk what to do about ts right now)")
        case ":": raise Exception("NotImplementedError(i think this is going to be used in dictionaries, and in function named parameters)")

        case _: 
            if isDigit(char): # i dont care about floats anymore
                number = char
                while True:
                    char = peek()
                    if  not isDigit(char): break # None because eof or some other character
                    number += consume()
                push_complicated(Literal("int", number))
            elif isAlpha(char): # name = keyword+identifier
                # identifiers (variables, functions), keywords, literal:bools
                name = char
                while peek() in ALLOWED_IN_NAMING: name += consume()
                if name in ["fn", "if", "else", "while", "return", "break", "continue", "extern"]: push_complicated(Keyword(name))
                elif name in ["int", "bool"]: push_complicated(Datatype(name))
                elif name in ["true", "false"]: push_complicated(Literal("bool", name))
                else: push_complicated(Identifier(name))
            else: raise Exception("IllegalCharError: " + repr(char))

write_to_json(OUTPUT_FILENAME, tokens)