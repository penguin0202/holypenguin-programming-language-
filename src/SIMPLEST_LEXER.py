from helper import *
from globals import *
from json_funcs import write_to_json, read_from_json
from Errors import *

INPUT_FILENAME = "test.txt"
OUTPUT_FILENAME = "lexed.txt"

# I am not caring about tab size right now regarding position tracking

def error(text): raise Exception(text)

def isDigit(thing): return thing in "0123456789"
# includes underscore
def isAlpha(thing): return thing in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

code = []
with open(INPUT_FILENAME, "r") as file:
    code = list(file.read())
if code == []: error("FileEmptySoTokenEmpty")
tokens = []

def EOF(): return len(code) == 0
def consume(): return None if EOF() else code.pop(0)
def peek(): return None if EOF() else code[0]
def push(token): tokens.append({"type": token})
def push_complicated(token): tokens.append(token)
def match(token): return peek() == token

while not EOF(): 
    match char := consume(): 
        case "+":
            if match("+"): 
                consume()
                push("++")
            elif match("="): 
                consume()
                push("+=")
            else: push("+") # None because eof, or next char is not compatable
        
        case "-":
            if match("-"): 
                consume()
                push("--")
            elif match("="): 
                consume()
                push("-=")
            else: push("-")
        
        case "*": 
            if match("="): 
                consume()
                push("*=")
            else: push("*")
            
        case "/": 
            if match("/"): 
                consume()                       
                while peek() not in ["\n", None]: consume()
            elif match("*"): 
                consume()
                while True: 
                    if EOF(): error("started to do a multi-line comment, but ended because eof")
                    if consume() == "*" and consume() == "/": break
            elif match("="): 
                consume()
                push("/=")
            # integer division
            # elif match("%"):
            #     consume()
            #     push("/%")
            else: push("/")
        
        case "%": 
            if match("="): 
                consume()
                push("%=")
            else: push("%")

        case "<": 
            if match("="): 
                consume()
                push("<=")
            else: push("<")
        
        case ">": 
            if match("="): 
                consume()
                push(">=")
            else: push(">")

        case "&": 
            if match("?"): 
                consume()
                push("&?")
            else: push("&")

        case "?": push("?")

        case "!": 
            if match("!"): 
                consume()
                push("!!")
            elif match("="): 
                consume()
                push("!=")
            else: push("!")

        case "~": 
            if match("="): 
                consume()
                push("~=")
            else: push("~")

        case "=": 
            if match("="): 
                consume()
                push("==")
            else: push("=")
        
        case "|": 
            if match("="): 
                consume()
                push("|=")
            else: push("|")

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

        case ".": error("NotImplementedError(used to be member access, but i scraped that)")

        case "\n" | "\t" | " ": pass

        case "\"": 
            string = ""
            while (char := consume()) != "\"":
                if char != "\\": string += char
                else: 
                    match char := consume(): 
                        case None: error("UnterminatedStringLiteral")
                        case "n": string += "\n"
                        case "t": string += "\t"
                        case "\\": string += "\\"
                        case "\"": string += "\""
                        case "\'": string += "\'"
                        # case "u" -> unicode: "\u2890"
                        case _: error("InvalidEscapeSequence")
            push_complicated(Literal("str", string))

        case "\'": 
            character = ""
            match char := consume(): 
                case None: error("UnterminatedCharLiteral")
                case "\'": error("EmptyCharLiteral")
                case "\\": 
                    match char := consume():
                        case None: raise Exception("escape sequence started in a char, but eof (both escape sequence terminated, and char terminated because end ' not found)")
                        case "n": character += "\n"
                        case "t": character += "\t"
                        case "\\": character += "\\"
                        case "\"": character += "\""
                        case "\'": character += "\'"
                        # case "u" -> unicode: "\u2890"
                        case _: error("InvalidEscapeSequence")
                case _: character += char
            if EOF(): error("UnterminatedCharLiteral")
            if consume() != "\'": error("CharTooLong")
            push_complicated(Literal("char", character))
        
        
        
        case "\\": error("Unexpected backslash outside of a string or char")
        case "#": error("NotImplementedError(dereference operator, but i dont want to deal with it right now)")
        case "@": error("NotImplementedError(address-of operator, but i dont want to deal with it right now)")

        case "$": error("NotImplementedError(idk what to do about ts right now)")
        case "^": error("NotImplementedError(idk what to do about ts right now)")
        case "`": error("NotImplementedError(idk what to do about ts right now)")
        case ":": error("NotImplementedError(i think this is going to be used in dictionaries, and in function named parameters)")

        case _: 
            if isDigit(char): # floats must have leading zeroes
                number = char
                dot_found = False
                while True:
                    char = peek()
                    if isDigit(char): number += consume()
                    elif char == ".":
                        if dot_found: error("TooManyFloatDots")
                        dot_found = True
                        number += consume()
                        if EOF(): raise Exception("no trailing numbers for floats because eof")
                        if not isDigit(peek()): raise Exception("no digits/numbers following the dot")
                    else: break # None because eof or some other character
                push_complicated(Literal("float" if dot_found else "int", number))
            elif isAlpha(char): # name = keyword+identifier
                # identifiers (variables, functions), keywords, literal:bools
                name = char
                while peek() in ALLOWED_IN_NAMING: name += consume()
                push_complicated(determine_name(name))
            else: error("IllegalCharError: " + repr(char))

write_to_json(OUTPUT_FILENAME, tokens)