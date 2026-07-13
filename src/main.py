# this is where I will combine the lexer, parser, semantic analyzer, CFG-IR? thingies
from lexer import *
#from parser import *
#import semantic_checker
import os
from pprint import pprint

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "test.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "lexed.txt")

code = ""
with open(INPUT_FILENAME, "r") as file: 
    code = file.read()

lexer = Lexer(code)

tokens: list[Token] = []
while (token := lexer.next_token()).type != TokenType.EOF: 
    tokens.append(token)

pprint(tokens, indent=4)

"""parser = Parser(tokens)

statement_module = ModuleStatement()
Block

statements: list[Statement] = []
while isinstance(statement := parser.parse_statement(), EOFStatement): 
    statements.append(statement)






ast = ModuleStatement(block=Block())
while parser.peek() != Token.EOF(): # check if there is still a token, which means there is still a statement to be parsed
    ast.block.add(parser.parse_statement())"""