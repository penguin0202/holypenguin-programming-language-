from lexer import Token, Position
from TOKEN_TYPES import *
from StatementTypes import *
from ExpressionTypes import *
from dataclasses import dataclass
from copy import copy

# there is not variable_initialization function because that would require context

# if you worry about pointers at any point in time during the developmental phase of this project, i will slime you out taiwanigga

PRECEDENCE = {
    TokenType.ASSIGNER: 1,

    TokenType.OR: 2,
    TokenType.AND: 2,

    TokenType.EQUAL_TO: 3,
    TokenType.NOT_EQUAL_TO: 3,

    TokenType.LESS_THAN: 4,
    TokenType.GREATER_THAN: 4,
    TokenType.LESS_THAN_OR_EQUAL_TO: 4,
    TokenType.GREATER_THAN_OR_EQUAL_TO: 4,

    TokenType.ADD: 5,
    TokenType.SUB: 5,
    TokenType.MUL: 6,
    TokenType.DIV: 6,
    TokenType.MOD: 6, 

    #TokenType.L_PAREN: 100, function call is an operator
}

"""    "+=": 1,
    "-=": 1,
    "*=": 1,

    "/=": 1,

    "|=": 1,
    "%=": 1,
    
    #"~=": 1,

    "++": 1,
    "--": 1,

    "!!": 1,
    
    "&?": 2,
    "|": 6,
        #"~": 6, 
    
    """
    
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

class Parser(): 
    def __init__(self, tokens) -> None: 
        self.tokens:list[Token] = tokens
        self.i:int = 0
        self.e_pos = Position()
        self.s_pos = Position()
        """self.e_row = 1
        self.e_col = 1 # expression row
        self.s_row = 1
        self.s_col = 1 # statement column"""
    def EOT(self): return self.i >= len(self.tokens)
    def peek(self) -> Token: return self.tokens[self.i] if self.tokens else Token.EOF()
    def advance(self) -> Token: self.i+=1
    def match(self, t: Token, expected_tokentype: TokenType, error_location): 
        # error location: expression_statement, if_Statement, expression inside int var declaration, while_Statement, while, etc
        if t.type != expected_tokentype: 
            raise Exception(f"Expected {expected_tokentype.name} in {error_location} @ {t.position}; got {t.type.name} instead")
    """def store_expression_position(self, t: Token): 
        self.e_row, self.e_col = t.row, t.col
    def store_statement_position(self, t: Token): 
        self.s_row, self.s_col = t.row, t.col"""

    def parse_atom(self) -> Expression:
        assert not self.EOT(), "Expected value, instead EOF"
        t = self.peek()
        self.e_pos = copy(t.position)
        
        if t.type == TokenType.LITERAL_INT: 
            self.advance()
            return IntLiteralExpression(t.value, self.e_pos)
        
        if t.type == TokenType.LITERAL_BOOL: 
            self.advance()
            return BoolLiteralExpression(t.value, self.e_pos)
        
        if t.type == TokenType.IDENTIFIER: 
            self.advance()
            return IdentifierExpression(t.value, self.e_pos)
        
        if t.type == TokenType.SUB: 
            self.advance()
            inner_atom = self.parse_atom()
            return NegateExpression(inner_atom, self.e_pos)
        
        if t.type == TokenType.NOT: 
            self.advance()
            inner_atom = self.parse_atom()
            return NotExpression(inner_atom, self.e_pos)

        if t.type == TokenType.L_PAREN: 
            self.advance()
            inner_expression = self.parse_expression()
            # consume RPAREN
            return inner_expression

        raise Exception(f"Unexpected token for parse_atom: {t} @ {self.e_pos}")
    
    def parse_expression(self, min_precedence=0, allow_assignment=False) -> Expression: 
        left = self.parse_atom()

        while not self.EOT(): 
            t = self.peek() # t must be an operator from now on

            if t.type not in PRECEDENCE.keys(): break # for example, if you get a "}" here, this will eject
            precedence = PRECEDENCE.get(t.type, -1) # im thinking of doing if precedence == -1, eject (same as above), but Ill sleep on it
            if precedence < min_precedence: break # forgot what this does

            if t.type == TokenType.ASSIGNER: 
                assert allow_assignment, "AssignmentInExpression"
                self.advance()
                right = self.parse_expression(precedence+1)
                # consume semicolon
                left = AssignmentExpression(left, right)
            elif t.type in [TokenType.ADD, TokenType.SUB, TokenType.MUL, TokenType.DIV, TokenType.MOD
                          , TokenType.OR, TokenType.AND, TokenType.EQUAL_TO, TokenType.NOT_EQUAL_TO
                          , TokenType.LESS_THAN, TokenType.GREATER_THAN, TokenType.LESS_THAN_OR_EQUAL_TO, TokenType.GREATER_THAN_OR_EQUAL_TO]: 
                self.advance()
                right = self.parse_expression(precedence+1)
                left = BinaryExprExpression(t, left, right)

        return left

    def parse_block(self) -> Block: 
        block: Block = Block()
        while not self.EOT(): 
            if self.match(T_TYPES.DELIMITER, "}"): break
            block.add(self.parse_statement())
            assert not self.EOT(), "Expected } (eof)"
        self.advance(T_TYPES.DELIMITER, "}")
        return block

    def parse_statement(self) -> Statement: 
        if self.EOT(): return EOFStatement()

        t: Token = self.peek()

        if t.type == TokenType.DATATYPE_INT: 
            self.advance()
            if (t := self.peek()).type == TokenType.IDENTIFIER: 
                variable_name = copy(t)
                self.advance()
                if (t := self.peek()).type == TokenType.SEMICOLON: 
                    self.advance()
                    return IntVarDeclStatement(variable_name)
                return Exception("Expected semicolon") # +row+col
            return Exception("Expected identifier") # + row and column information
        
        if t.type == TokenType.DATATYPE_BOOL: 
            self.advance()
            if (t := self.peek()).type == TokenType.IDENTIFIER: 
                variable_name = copy(t)
                self.advance()
                if (t := self.peek()).type == TokenType.SEMICOLON: 
                    self.advance()
                    return BoolVarDeclStatement(variable_name)
                return Exception("Expected semicolon") # +row+col
            return Exception("Expected identifier") # + row and column information

        if t.type == TokenType.L_BRACKET: 
            self.advance()
            return BlockStatement(self.parse_block())
        
        if t.type == TokenType.KEYWORD_IF: 
            self.advance()
            # consume LPAREN -- yep I'm doing this
            if_condition = self.parse_expression() # make sure checking for expressions ignore the RPAREN if not paired with a LPAREN
            # consume RPAREN
            if_statement = self.parse_statement() # peek() will not return the next free token
            if (t := self.peek()).type == TokenType.KEYWORD_ELSE: 
                self.advance()
                else_statement = self.parse_statement()
                return IfElseStatement(if_condition, if_statement, else_statement)
            return IfStatement(if_condition, if_statement)

        if t.type == TokenType.KEYWORD_WHILE: 
            self.advance()
            if (t := self.peek()).type == TokenType.L_PAREN: 
                self.advance()
                if (t := self.peek()).type == TokenType.R_PAREN: 
                    self.advance()
                    while_condition = self.parse_expression()
                    # consume RPAREN
                    while_statement = self.parse_statement()
                    return WhileStatement(while_condition, while_statement)
                raise Exception("wanted RPAREN in this while statement") # r, c
            raise Exception("Wanted LPAREN in this while statement") #r, c

        if t.type == TokenType.KEYWORD_BREAK: 
            self.advance()
            if (t := self.peek()).type == TokenType.SEMICOLON: 
                self.advance()
                return BreakStatement()
            raise Exception("wanted semicolon") #rowcol
        
        expression_statement = self.parse_expression(allow_assignment=True)
        if (t := self.peek()).type == TokenType.SEMICOLON: 
            self.advance()
            return ExpressionStatement(expression_statement)
        raise Exception("expected semicolon in expression_Statement") #rc
        










"""op_tok: Token = self.peek()
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
                    while not self.EOT(): 
                        if self.match(T_TYPES.DELIMITER, ")"): break
                        arguments.append(self.parse_expression())
                        if self.match(T_TYPES.DELIMITER, ")"): break
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
                    left = BinaryExprExpression(operator, left, self.parse_expression(precedence+1))"""

"""    def parse_fn_signature(self) -> FnSignature: 
        datatype: Token = self.advance(T_TYPES.DATATYPE)
        name: Token = self.advance(T_TYPES.IDENTIFIER)
        self.advance(T_TYPES.DELIMITER, "(")
        parameter_datatypes: list[str] = []
        parameter_names: list[str] = []
        while not self.EOT(): 
            if self.match(T_TYPES.DELIMITER, ")"): break
            datatype: Token = self.advance(T_TYPES.DATATYPE)
            name: Token = self.advance(T_TYPES.IDENTIFIER)
            parameter_datatypes.append(datatype.value)
            parameter_names.append(name.value)
            if self.match(T_TYPES.DELIMITER, ")"): break
            self.advance(T_TYPES.DELIMITER, ",") # allows trailing commas for no particular reason
        self.advance(T_TYPES.DELIMITER, ")")
        # function overloading, a name of a function will be a set with keys of an array of its parameters 
        # and the value of another table containing the code and the return type
        return FnSignature(name.value, datatype.value, parameter_names, parameter_datatypes)"""





"""if t.type == T_TYPES.DATATYPE: 
    self.advance()
    name: Token = self.advance(T_TYPES.IDENTIFIER)
    self.advance(T_TYPES.DELIMITER, ";")
    return VarDeclStatement(name.value, t.value) # no variable declaration an dinitialization in the same place
if t.type == T_TYPES.KEYWORD: 
    self.advance()
    match t.value: 
        case "fn": 
            fn_signature: FnSignature = self.parse_fn_signature()
            self.advance(T_TYPES.DELIMITER, "{")
            return FnDeclStatement(fn_signature, self.parse_block())
        case "extern": # right now this only works with functions, not any variables, plz add functionality
            self.advance(T_TYPES.KEYWORD, "fn")
            return ExternFnStatement(self.parse_fn_signature())
        case "continue": return ContinueStatement()
        case "else": raise Exception("what is ts doing here dawg") # not a "top-level" statement starter, only can use in conjunction of if in front
        case "return": 
            exp = self.parse_expression()
            self.advance(T_TYPES.DELIMITER, ";")
            return ReturnStatement(exp)
    raise Exception("keyword not keyword, dev error")
else: 
    # allows function calls, and something like x + 5;, variable reassigning, disallows single semicolon, throws unexpected token instead inside the parse_atom func inside parse_expression
    expr: Expression = self.parse_expression(allow_assignment=True)
    self.advance(T_TYPES.DELIMITER, ";")
    return ExpressionStatement(expr)"""

""" for initialization if want to add this
            if (t := self.peek()).type == TokenType.ASSIGNER: 
                    self.advance()
                    if (t := self.peek()).type == TokenType.LITERAL_INT: 
                        integer_value = copy(t)
                        self.advance()"""

"""@dataclass
class FnSignature(): 
    name: str
    returns: str
    param_names: list[str]
    param_datatypes: list[str]"""