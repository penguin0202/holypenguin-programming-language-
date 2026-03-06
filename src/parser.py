from json_funcs import *
import os
from lexer import Token
from TOKEN_TYPES import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "lexed.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "parsed.txt")

"""# there is not variable_initialization function because that would require context

def var_del(name): 
    return {"type": "var_del", "name": name}"""

# if you worry about pointers at any point in time during the developmental phase of this project, i will slime you out taiwanigga

PRECEDENCE = {
    "=": 1,

    "+=": 1,
    "-=": 1,
    "*=": 1,

    "/=": 1,

    "|=": 1,
    "%=": 1,
    
    #"~=": 1,

    "++": 1,
    "--": 1,

    "!!": 1,

    "?": 2,
    "&": 2,
    "&?": 2,

    "==": 3,
    "!=": 3,

    "<": 4,
    ">": 4,
    "<=": 4,
    ">=": 4,

    "+": 5,
    "-": 5,
    "*": 6,
    "/": 6,
    "|": 6,
    "%": 6, 

    #"~": 6, 

    "(": 100,
}

tokens: list[Token] = read_from_json(INPUT_FILENAME)
ast = {
    "type": "module", 
    "block": {
        "code": []
    }
}

class Statement(): 
    def __init__(self, type, **kwargs): 
        self._type = type
        self._attributes = kwargs

    @property
    def type(self): 
        return self._type

    def get(self, key): 
        if key not in self._attributes: 
            raise Exception(key + " not in " + self.type + " statement")
        return self._attributes[key]

class Expression(): 
    def __init__(self, type) -> None: 
        self._type = type

class IfStatement(Statement): 
    # {"type": "if", "condition": exp, "block": {"code": if_block, "symbol_table": None}}
    def __init__(self, condition_param, block_param): 
        super().__init__("if", condition=condition_param, block=block_param)

class FnDeclStatement(Statement): 
    # {"type": "fn_decl", "returns": datatype.value, "name": name.value, "param_names": parameters["names"], "param_datatypes": parameters["datatypes"], "block": {"code": parse_block(), "symbol_table": None}}
    def __init__(self, returns_param, name_param, param_names_param, param_datatypes_param, block_param): 
        super().__init__("fn_decl", returns=returns_param, name=name_param, param_names=param_names_param, param_datatypes=param_datatypes_param, block=block_param)

class VarDeclStatement(Statement): 
    # {"type": "var_decl", "name": name.value, T_TYPES.DATATYPE: token.value}
    def __init__(self, name_param, datatype_param)
        super().__init__("var_decl", name=name_param, datatype=datatype_param)



class Block(): 


class Tokens(): 
    def __init__(self) -> None: 
        self.tokens:list[Token] = []
        self.index:int = 0
    def add(self, token: Token) -> None: 
        self.tokens.append(token)
    def peek(self) -> Token: return self.tokens[self.index] if self.tokens else Token.EOF()
    def peekis(self, type) -> bool: return self.peek().type == type
    def peekis(self, type, value) -> bool: 
        token = self.peek()
        if token.type != type: return False
        return token.value == value
    def advance(self) -> Token: 
        token = self.peek()
        self.index+=1
        return token
    def advance(self, type) -> Token:
        token = self.peek()
        assert token.type == type, "Expected type: " + type
        self.index+=1
        return token
    def advance(self, type, value) -> Token:
        token = self.peek()
        assert token.type == type, "Expected type: " + type
        assert token.value == value, "Expected value: " + value
        self.index+=1
        return token
    def __str__(self) -> str: 
        return ""

i = 0
def peek() -> Token: return tokens[i] if tokens else Token.EOF()
def peekis(type) -> bool: 
    return peek().type == type
def peekis(type, value) -> bool: 
    token = peek()
    if token.type != type: return False
    return token.value == value
def advance() -> Token: 
    token = peek()
    global i
    i+=1
    return token
def advance(type) -> Token:
    token = peek()
    assert token.type == type, "Expected type: " + type
    global i
    i+=1
    return token
def advance(type, value) -> Token:
    token = peek()
    assert token.type == type, "Expected type: " + type
    assert token.value == value, "Expected value: " + value
    global i
    i+=1
    return token

def parse_expression(min_precedence=0, allow_assignment=False) -> dict: 
    def parse_atom() -> dict:
        token: Token = advance()
        assert token != Token.EOF() , "Expected value, instead EOF"
        match token.type: 
            case T_TYPES.LITERAL: return token
            case T_TYPES.IDENTIFIER: return token
            case T_TYPES.OPERATOR: 
                match token.value: 
                    case "-": return {"type": "negate_expr", "operand": parse_atom()}
                    case "!": return {"type": "not_expr", "operand": parse_atom()}
                    case "(": 
                        expr = parse_expression()
                        advance(T_TYPES.OTHER, ")")
                        return expr
        raise Exception(f"Unexpected token: {token}")

    left = parse_atom()

    while tokens: 
        op_tok: Token = peek()
        if op_tok.type != T_TYPES.OPERATOR: break # must be an operator or some sort, not an identifier or whatnot
        operator = op_tok.value
        if operator not in PRECEDENCE.keys(): break
        precedence = PRECEDENCE.get(operator, -1)
        if precedence < min_precedence: break
        advance() # consume the operator

        match operator: 
            case "(": left = {"type": "fn_call", "name": left, "args": parse_function_arguments()}
            case "++" | "--" | "!!": 
                assert allow_assignment, "AssignmentInExpression"
                left = {
                    "type": "unary_assignment", 
                    "operator": operator, 
                    "variable": left
                }
                advance(T_TYPES.DELIMITER, ";")
                return left # immediate return cuz there should theoretically be nothing after a "i++;"
            case "=" | "+=" | "-=" | "*=" | "/=" | "%=" | "~=": 
                assert allow_assignment, "AssignmentInExpression"
                left = {
                    "type": "binary_assignment",
                    "operator": operator, 
                    "variable": left,
                    "value": parse_expression(precedence+1),
                }
            # operator for appending lists?
            case _: 
                left = {
                    "type": "binary_expr",
                    "operator": operator,
                    "left": left,
                    "right": parse_expression(precedence+1),
                }

    return left

# no named arguments
def parse_function_arguments() -> list: 
    arguments = []
    # make it so that once a named parameter is, well, named, all consecutive parameter assignation must also be named
    # look at you using fancy words
    while tokens: 
        if peekis(T_TYPES.DELIMITER, ")"): break
        arguments.append(parse_expression())
        if peekis(T_TYPES.DELIMITER, ")"): break
        advance(T_TYPES.DELIMITER, ",")
    advance(T_TYPES.DELIMITER, ")")
    return arguments

def parse_block() -> list: 
    statements = []
    while tokens: 
        if peekis(T_TYPES.DELIMITER, "}"): break
        statements.append(parse_statement())
        assert tokens, "Expected } (eof)"
    advance(T_TYPES.DELIMITER, "}")
    return statements

def parse_fn() -> dict: 
    datatype: Token = advance(T_TYPES.DATATYPE)
    name: Token = advance(T_TYPES.IDENTIFIER)
    advance(T_TYPES.DELIMITER, "(")
    parameters = parse_function_parameters() # already requires closing paren inside
    advance(T_TYPES.DELIMITER, "{")
    # function overloading, a name of a function will be a set with keys of an array of its parameters 
    # and the value of another table containing the code and the return type
    return FnDeclStatement(datatype.value, name.value, parameters["names"], parameters["datatypes"], {"code": parse_block(), "symbol_table": None})

def parse_function_parameters() -> list: 
    parameter_datatypes = []
    parameter_names = []
    parameters = {} # will hold { "datatypes": parameter_dsatatypes, "names": parameter_names }
    while tokens: 
        if peekis(T_TYPES.DELIMITER, ")"): break
        datatype: Token = advance(T_TYPES.DATATYPE)
        name: Token = advance(T_TYPES.IDENTIFIER)
        parameter_datatypes.append(datatype.value)
        parameter_names.append(name.value)
        if peekis(T_TYPES.DELIMITER, ")"): break
        advance(T_TYPES.DELIMITER, ",")
    advance(T_TYPES.DELIMITER, ")")
    parameters["datatypes"] = parameter_datatypes
    parameters["names"] = parameter_names
    return parameters

def parse_statement() -> dict: 
    token = peek()
    assert token != Token.EOF(), "eof, want statement"
    if token.type == T_TYPES.DELIMITER and token.value == "{": 
        advance() # {
        return {"type": "block", "block": {"code": parse_block(), "symbol_table": None}}
    if token.type == T_TYPES.DATATYPE: 
        advance()
        name: Token = advance(T_TYPES.IDENTIFIER)
        advance(T_TYPES.DELIMITER, ";")
        return {"type": "var_decl", "name": name.value, T_TYPES.DATATYPE: token.value}
        # no variable declaration an dinitialization in the same place
    if token.type == T_TYPES.KEYWORD: 
        advance()
        match token.value: 
            case "fn": return parse_fn()
            case "extern": # right now this only works with functions, not any variables, plz add functionality
                advance(T_TYPES.KEYWORD, "fn")
                datatype: Token = advance(T_TYPES.DATATYPE)
                name: Token = advance(T_TYPES.IDENTIFIER)
                advance(T_TYPES.DELIMITER, "(")
                parameters = parse_function_parameters()
                return {"type": "external_fn", "name": name.value, "returns": datatype.value, "param_names": parameters["names"], "param_datatypes": parameters["datatypes"]}
            case "break": return {"type": "break"}
            case "continue": return {"type": "continue"}
            case "else": raise Exception("what is ts doing here dawg") # not a "top-level" statement starter, only can use in conjunction of if in front
            case "return": 
                exp = parse_expression()
                advance(T_TYPES.DELIMITER, ";")
                return {"type": "return", "value": exp}
            case "while": 
                exp = parse_expression()
                advance(T_TYPES.DELIMITER, "{")
                return {"type": "while", "condition": exp, "block": {"code": parse_block(), "symbol_table": None}}
            case "if": 
                exp = parse_expression()
                advance(T_TYPES.DELIMITER, "{")
                if_block = parse_block()
                if not peekis(T_TYPES.KEYWORD, "else"): # None/eof or its just not else
                    return IfStatement(exp, {"code": if_block, "symbol_table": None})
                else: 
                    advance() # keyword:else
                    advance(T_TYPES.DELIMITER, "{")
                    return {"type": "if_else", "condition": exp, "then-block": {"code": if_block, "symbol_table": None}, "else-block": {"code": parse_block(), "symbol_table": None}}
        raise Exception("keyword not keyword, dev error")
    else: 
        # allows function calls, and something like x + 5;, variable reassigning, disallows single semicolon, throws unexpected token instead inside the parse_atom func inside parse_expression
        expr = parse_expression(allow_assignment=True)
        advance(T_TYPES.DELIMITER, ";")
        return {"type": "expr", "expression": expr}

while tokens: 
    ast["block"]["code"].append(parse_statement())

write_to_json(OUTPUT_FILENAME, [ast])