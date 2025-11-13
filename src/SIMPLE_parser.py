from json_funcs import *

INPUT_FILENAME = "test/lexed.txt"
OUTPUT_FILENAME = "test/parsed.txt"

'''# there is not variable_initialization function because that would require context

def var_del(name): 
    return {"type": "var_del", "name": name}'''

# if you worry about pointers at any point in time during the developmental phase of this project, i will slime you out taiwanigga

def get_type(thing): return thing["type"]
def get_value(thing): return thing["value"]

def error(text): raise Exception(text)

PRECEDENCE = {
    "=": 1,

    "+=": 1,
    "-=": 1,
    "*=": 1,

    "/=": 1,

    "|=": 1,
    "%=": 1,
    
    "~=": 1,

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

    "~": 6, 

    "(": 100,
}

def RequireComma(): eat_thing(",", "Expected type:,")
def RequireSemicolon(): eat_thing(";", "Expected type:;")
def RequireStartingBrace(): eat_thing("{", "Expected type:{")
def RequireClosingBrace(): eat_thing("}", "Expected type:}")
def RequireStartingParen(): eat_thing("(", "Expected type:(")
def RequireEqualSign(): eat_thing("=", "Expected type:=")
def RequireClosingParen(): eat_thing(")", "Expected type:)")
def RequireStartingBracket(): eat_thing("[", "Expected type:[")
def RequireClosingBracket(): eat_thing("]", "Expected type:]")

def peek_is_fn(): return match("keyword") and get_value(peek()) == "fn"

tokens = read_from_json(INPUT_FILENAME)
ast = []

def consume_name():
    if not match("identifier"): error("Expected type:identifier")
    return get_value(consume())

def eat_thing(thing, err): 
    if not match(thing): error(err)
    consume()

def peek(): return tokens[0] if tokens else None
def consume(): return tokens.pop(0) if tokens else None
def match(thing): return get_type(peek()) == thing # peeks, doesnt consume, matches its type to the given thing

def parse_expression(min_precedence=0, allow_assignment=False) -> dict: 
    def parse_atom() -> dict:
        if not tokens: error("Expected value")
        match get_type(token := consume()): 
            case "literal": return token
            case "identifier": return token
            case "-": return {"type": "negate_expr", "operand": parse_atom()}
            case "!": return {"type": "not_expr", "operand": parse_atom()}
            case "(": 
                expr = parse_expression()
                RequireClosingParen()
                return expr
        error(f"Unexpected token: {token}")

    left = parse_atom()

    while tokens: 
        operator = get_type(peek())
        if operator not in PRECEDENCE.keys(): break
        precedence = PRECEDENCE.get(operator, -1)
        if precedence < min_precedence: break
        consume() # the operator

        match operator: 
            case "(": left = {"type": "fn_call", "name": left, "args": parse_function_arguments()}
            case "++" | "--" | "!!": 
                if not allow_assignment: error("AssignmentInExpression")
                left = {
                    "type": "unary_assignment", 
                    "operator": operator, 
                    "variable": left
                }
                RequireSemicolon()
                return left # immediate return cuz there should theoretically be nothing after a "i++;"
            case "=" | "+=" | "-=" | "*=" | "/=" | "%=" | "~=": 
                if not allow_assignment: error("AssignmentInExpression")
                left = {
                    "type": "binary_assignment",
                    "operator": operator, 
                    "variable": left,
                    "value": parse_expression(precedence+1),
                }
            # i used to have |= as appending to a list, but right now i am not working on lists (and thats okay!)
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
        if match(")"): break
        arguments.append(parse_expression())
        if match(")"): break
        RequireComma()
    RequireClosingParen()
    return arguments

def parse_block() -> list: 
    statements = []
    while tokens: 
        if match("}"): break
        statements.append(parse_statement())
        if not tokens: error("Expected } (eof)")
    RequireClosingBrace()
    return statements

def parse_fn() -> dict: 
    datatype = parse_datatype()
    name = consume_name()
    RequireStartingParen()
    parameters = parse_function_parameters() # already requires closing paren inside
    RequireStartingBrace()
    # function overloading, a name of a function will be a set with keys of an array of its parameters 
    # and the value of another table containing the code and the return type
    return {'type': 'fn_decl', "returns": datatype, 'name': name, "param_names": parameters["names"], "param_datatypes": parameters["datatypes"], "block": parse_block()}

def parse_function_parameters() -> list: 
    parameter_datatypes = []
    parameter_names = []
    parameters = {} # will hold { "datatypes": parameter_dsatatypes, "names": parameter_names }
    while tokens: 
        if match(")"): break
        parameter_datatypes.append(parse_datatype())
        parameter_names.append(consume_name())
        if match(")"): break
        RequireComma()
    RequireClosingParen()
    parameters["datatypes"] = parameter_datatypes
    parameters["names"] = parameter_names
    return parameters

# excludes fn, too complicated
def parse_datatype() -> str: 
    if not match("datatype"): error("Expected type:datatype")
    datatype = get_value(consume())
    return datatype

def parse_statement() -> dict: 
    if not tokens: error("i dont know what to say except: eof")
    token = peek()
    token_type = get_type(token)
    if token_type == "{": 
        consume() # {
        return {"type": "just_a_block", "code": parse_block()}
    if token_type == "datatype": 
        consume()
        datatype = token["value"] 
        name = consume_name()
        RequireSemicolon()
        return {"type": "var_decl", "name": name, "datatype": datatype}
        # no variable declaration an dinitialization in the same place
    if token_type == "keyword": 
        consume()
        match get_value(token): 
            case "fn": parse_fn()
            case "extern": # right now this only works with functions, not any variables, plz add functionality
                if not match("keyword") or get_value(peek()) != "fn": error("Expected type:datatype, value:fn")
                consume() # datatype:fn
                datatype = parse_datatype()
                name = consume_name()
                RequireStartingParen()
                parameters = parse_function_parameters()
                return {"type": "external_function_declaration", "name": name, "returns": datatype, "param_names": parameters["names"], "param_datatypes": parameters["datatypes"]}
            case "break": return {"type": "break_stmnt"}
            case "continue": return {"type": "continue_stmnt"}
            case "else": error("what is ts doing here dawg") # not a 'top-level' statement starter, only can use in conjunction of if in front
            case "return": 
                exp = parse_expression()
                RequireSemicolon()
                return {"type": "return_stmnt", "value": exp}
            case "while": 
                exp = parse_expression()
                RequireStartingBrace()
                return {'type': 'while_stmnt', 'condition': exp, 'while_block': parse_block()}
            case "if": 
                exp = parse_expression()
                RequireStartingBrace()
                if_block = parse_block()
                if not match("keyword") or get_value(peek()) != "else": 
                    return {'type': 'if_stmnt', 'condition': exp, 'if-then_block': if_block} # None/eof or its just not else
                else: 
                    consume() # keyword:else
                    RequireStartingBrace()
                    return {'type': 'if_else_stmnt', 'condition': exp, 'if-then_block': if_block, 'else_block': parse_block()}
            case _: error("keyword not keyword, dev error")

    # allows function calls, and something like x + 5;, variable reassigning, disallows single semicolon, throws unexpected token instead inside the parse_atom func inside parse_expression
    expr = parse_expression(allow_assignment=True)
    RequireSemicolon()
    return {"type": "expr_stmnt", "expression": expr}

while tokens: ast.append(parse_statement())

write_to_json(OUTPUT_FILENAME, ast)