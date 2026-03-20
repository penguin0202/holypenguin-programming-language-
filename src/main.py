# this is where I will combine the lexer, parser, semantic analyzer, CFG-IR? thingies
from lexer import Lexer, Token
from parser import *
import semantic_checker
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "test.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "lexed.txt")

lexer: Lexer = Lexer(INPUT_FILENAME)

parser: Parser = Parser()
token: Token = lexer.next_token()
while token != Token.EOF(): 
    parser.add(token)
    token = lexer.next_token()

ast = ModuleStatement(block=Block())
while parser.peek() != Token.EOF(): # check if there is still a token, which means there is still a statement to be parsed
    ast.get("block").add(parser.parse_statement())

