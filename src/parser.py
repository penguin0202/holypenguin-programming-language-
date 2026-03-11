from json_funcs import *
import os
from lexer import Token
from TOKEN_TYPES import *
from StatementTypes import *
from ExpressionTypes import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "lexed.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "parsed.txt")

# there is not variable_initialization function because that would require context

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
    
class Block(): 
    def __init__(self): 
        self._symbol_table = None
        self._code: list[Statement] = []
    def add(self, statement:Statement): 
        self._code.append(statement)
    @property
    def symbol_table(self): 
        return self._symbol_table
    @property
    def code(self): 
        return self._code

class FnSignatureThing(): # {"type": "fn_decl", "returns": datatype.value, "name": name.value, "param_names": parameters["names"], "param_datatypes": parameters["datatypes"], "block": {"code": parse_block(), "symbol_table": None}}
    def __init__(self, name, returns, param_names, param_datatypes): 
        self._name = name
        self._returns = returns
        self._param_names = param_names
        self._param_datatypes = param_datatypes
    
    @property
    def name(self): return self._name
    @property
    def returns(self): return self._returns
    @property
    def param_names(self): return self._param_names
    @property
    def param_datatypes(self): return self._param_datatypes

class Parser(): 
    def __init__(self) -> None: 
        self.tokens:list[Token] = []
        self.index:int = 0
    def add(self, token: Token) -> None: 
        self.tokens.append(token)
    def EOF(self): 
        return self.index >= len(self.tokens)
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
    
    def parse_expression(self, min_precedence=0, allow_assignment=False) -> Expression: 
        def parse_atom() -> Expression:
            token: Token = self.advance()
            assert token != Token.EOF() , "Expected value, instead EOF"
            match token.type: 
                case T_TYPES.LITERAL: return Expression("literal", datatype=token.datatype, value=token.value)
                case T_TYPES.IDENTIFIER: return Expression("identifier", value=token.value)
                case T_TYPES.OPERATOR: 
                    match token.value: 
                        case "-": return NegateExpression(parse_atom())
                        case "!": return NotExpression(parse_atom())
                        case "(": 
                            expr = self.parse_expression()
                            self.advance(T_TYPES.OTHER, ")")
                            return expr
            raise Exception(f"Unexpected token: {token}")

        left = parse_atom()

        while not self.EOF(): 
            op_tok: Token = self.peek()
            if op_tok.type != T_TYPES.OPERATOR: break # must be an operator or some sort, not an identifier or whatnot
            operator = op_tok.value
            if operator not in PRECEDENCE.keys(): break
            precedence = PRECEDENCE.get(operator, -1)
            if precedence < min_precedence: break
            self.advance() # consume the operator

            match operator: 
                case "(": 
                    arguments: list[Expression] = [] # no named arguments (at least now yet)
                    # make it so that once a named parameter is, well, named, all consecutive parameter assignation must also be named
                    # look at you using fancy words
                    while not self.EOF(): 
                        if self.peekis(T_TYPES.DELIMITER, ")"): break
                        arguments.append(self.parse_expression())
                        if self.peekis(T_TYPES.DELIMITER, ")"): break
                        self.advance(T_TYPES.DELIMITER, ",")
                    self.advance(T_TYPES.DELIMITER, ")")
                    left = FnCallExpression(left, arguments)
                case "++" | "--" | "!!": 
                    assert allow_assignment, "AssignmentInExpression"
                    left = UnaryAssignmentExpression(operator, left)
                    self.advance(T_TYPES.DELIMITER, ";")
                    return left # immediate return cuz there should theoretically be nothing after a "i++;"
                case "=" | "+=" | "-=" | "*=" | "/=" | "%=" | "~=": 
                    assert allow_assignment, "AssignmentInExpression"
                    left = BinaryAssignmentExpression(operator, left, self.parse_expression(precedence+1))
                # operator for appending lists?
                case _: 
                    left = BinaryExprExpression(operator, left, self.parse_expression(precedence+1))

        return left

    def parse_block(self) -> Block: 
        block: Block = Block()
        while not self.EOF(): 
            if self.peekis(T_TYPES.DELIMITER, "}"): break
            block.add(self.parse_statement())
            assert not self.EOF(), "Expected } (eof)"
        self.advance(T_TYPES.DELIMITER, "}")
        return block

    def parse_fn_signature(self) -> FnSignatureThing: 
        datatype: Token = self.advance(T_TYPES.DATATYPE)
        name: Token = self.advance(T_TYPES.IDENTIFIER)
        self.advance(T_TYPES.DELIMITER, "(")
        parameter_datatypes = []
        parameter_names = []
        while not self.EOF(): 
            if self.peekis(T_TYPES.DELIMITER, ")"): break
            datatype: Token = self.advance(T_TYPES.DATATYPE)
            name: Token = self.advance(T_TYPES.IDENTIFIER)
            parameter_datatypes.append(datatype.value)
            parameter_names.append(name.value)
            if self.peekis(T_TYPES.DELIMITER, ")"): break
            self.advance(T_TYPES.DELIMITER, ",") # allows trailing commas for no particular reason
        self.advance(T_TYPES.DELIMITER, ")")
        # function overloading, a name of a function will be a set with keys of an array of its parameters 
        # and the value of another table containing the code and the return type
        return FnSignatureThing(name.value, datatype.value, parameter_names, parameter_datatypes)

    def parse_statement(self) -> Statement: 
        token = self.peek()
        assert token != Token.EOF(), "eof, want statement"
        if token.type == T_TYPES.DELIMITER and token.value == "{": 
            self.advance() # {
            return BlockStatement(self.parse_block())
        if token.type == T_TYPES.DATATYPE: 
            self.advance()
            name: Token = self.advance(T_TYPES.IDENTIFIER)
            self.advance(T_TYPES.DELIMITER, ";")
            return VarDeclStatement(name.value, token.value) # no variable declaration an dinitialization in the same place
        if token.type == T_TYPES.KEYWORD: 
            self.advance()
            match token.value: 
                case "fn": 
                    fn_signature: FnSignatureThing = self.parse_fn_signature()
                    self.advance(T_TYPES.DELIMITER, "{")
                    return FnDeclStatement(fn_signature, self.parse_block())
                case "extern": # right now this only works with functions, not any variables, plz add functionality
                    self.advance(T_TYPES.KEYWORD, "fn")
                    return ExternFnStatement(self.parse_fn_signature())
                case "break": return BreakStatement()
                case "continue": return ContinueStatement()
                case "else": raise Exception("what is ts doing here dawg") # not a "top-level" statement starter, only can use in conjunction of if in front
                case "return": 
                    exp = self.parse_expression()
                    self.advance(T_TYPES.DELIMITER, ";")
                    return ReturnStatement(exp)
                case "while": 
                    exp = self.parse_expression()
                    self.advance(T_TYPES.DELIMITER, "{")
                    return WhileStatement(exp, self.parse_block())
                case "if": 
                    exp = self.parse_expression()
                    self.advance(T_TYPES.DELIMITER, "{")
                    if_block: Block = self.parse_block()
                    if not self.peekis(T_TYPES.KEYWORD, "else"): # None/eof or its just not else
                        return IfStatement(exp, if_block)
                    else: 
                        self.advance() # keyword:else
                        self.advance(T_TYPES.DELIMITER, "{")
                        return IfElseStatement(exp, if_block, self.parse_block())
            raise Exception("keyword not keyword, dev error")
        else: 
            # allows function calls, and something like x + 5;, variable reassigning, disallows single semicolon, throws unexpected token instead inside the parse_atom func inside parse_expression
            expr: Expression = self.parse_expression(allow_assignment=True)
            self.advance(T_TYPES.DELIMITER, ";")
            return ExpressionStatement(expr)