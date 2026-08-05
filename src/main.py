# this is where I will combine the lexer, parser, semantic analyzer, CFG-IR? thingies
from lexer import *
from parser import Parser, EOFStatement, ModuleStatement
from semantic_checker import SemanticAnalyzer
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

#pprint(tokens, indent=4)

parser = Parser(tokens)

ast = ModuleStatement({}, [], Position())
while not isinstance(statement := parser.parse_statement(), EOFStatement): 
    ast.code.append(statement)

#pprint(ast, indent=1)

semantic_analyzer = SemanticAnalyzer()
semantic_analyzer.analyze_statement(ast, -1)