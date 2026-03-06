# this is where I will combine the lexer, parser, semantic analyzer, CFG-IR? thingies
from lexer import Code, Token
from parser import Tokens
import semantic_checker
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "test.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "lexed.txt")

code: Code = Code(INPUT_FILENAME)

tokens: Tokens = Tokens()
token: Token = code.next_token()
while token != Token.EOF: 
    tokens.add(token)
    token = code.next_token()

