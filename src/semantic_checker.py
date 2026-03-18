from json_funcs import *
import os
from lexer import *
from parser import *
from SymbolTypes import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "parsed.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "semantically-analyzed.txt")

# tuples are used for hash-ability

statements = read_from_json(INPUT_FILENAME)
symbol_table = {}

BOOL = "bool"
INT = "int"

next_scope_id = 0

# chatgpt recommends instead of just a marker, add function names (and my own thinking because of function overloading: and function parameters) - 
# to identify what function is being returned
# marker/function_context now looks like this: 
# [ {"name": name, "params": params}, {"name": name, "params": params}, ...]
class FunctionContext(): 
    def __init__(self): 
        self.context: list[FnSignatureThing] = [] # it is a stack instead of just a global bit flag because you need the return datatype later on for every single inner function
    def enter_function(self, fn_signature: FnSignatureThing): 
        self.context.append(fn_signature)
    def exit_function(self) -> FnSignatureThing: 
        assert self.is_in_function(), "no function present"
        return self.context.pop(-1)
    def is_in_function(self) -> bool: 
        return len(self.context) > 0
    def current_function(self): 
        assert self.is_in_function(), "no function present"
        return self.context[-1]
functions: FunctionContext = FunctionContext()

# did not make a loop_context because i dont think i need to store any metadata regarding the loop
# other than that I am in one so i can validate breka and continue statements
# wait what if a loop is inside another loop nvm I solved it below
class LoopContext(): 
    def __init__(self): 
        self.counter = 0
    def enter_one(self): 
        self.counter+=1
    def exit_one(self): 
        assert self.counter > 0, "How the hell can you exit a loop when there isn't one"
        self.counter-=1
    def is_in_one(self) -> bool: 
        return self.counter > 0
loops: LoopContext = LoopContext()

class Scope(): 
    def __init__(self, parent_id): 
        self.symbols: dict = {}
        self.parent_id = parent_id
    def symbol_exists(self, name) -> bool: 
        return name in self.symbols.keys()
    
    def get_function_symbol(self, name:str) -> FnSymbol: 
        assert self.symbol_exists(name), "function does not exist yet?"
        possible_function = self.symbols[name]
        assert isinstance(possible_function, FnSymbol), "symbol already exists not as a function"
        return possible_function
    
    def get_variable_symbol(self, name) -> VarSymbol: 
        assert self.symbol_exists(name), "function does not exist yet?"
        possible_variable = self.symbols[name]
        assert isinstance(possible_variable, VarSymbol), "symbol already exists not as a variable"
        return possible_variable
    
    def add_variable_symbol(self, name, datatype) -> None: 
        assert not self.symbol_exists(name), f"Symbol ({name["kind"]}) with this name already exists in your current scope!" # shadowing present
        self.symbols[name] = VarSymbol(datatype)
        # overflows/underflows/div_by_0 will be runtime errors, as symbols only store name and datatypes

    def add_function_symbol(self, fn_signature: FnSignatureThing) -> None: # {'type': 'fn_decl', "returns": datatype, 'name': name, 'args': parameters, "block": parse_block()}
        # check duplicate parameter names
        seen_names: list[str] = []
        for param_name in fn_signature.param_names: 
            assert param_name not in seen_names, f"duplicate parameter '{param_name}'"
            seen_names.append(param_name)

        if self.symbol_exists(fn_signature.name): 
            # if name is a symbol that exists, but is not a function, then we can't "overload" a variable
            fn: FnSymbol = self.get_function_symbol()

            # generate, from all keys inside the "set" of the function, a list containing all existing param lists
            # no conflicts, good job david *pats head*

            for overload in fn.overloads: 
                assert fn_signature.param_datatypes != overload.datatypes, "duplicate function signature, where datatypes coincide"

            # if code executes here, it means both of the following
            # 1. the new param_datatypes don't coincide with existing ones
            # 2. names dont coincide
            # btw, the checking of the return types is handled by the function context
            fn.add_overload(fn_signature.param_datatypes, fn_signature.param_names, fn_signature.returns)

        else: # if no function set already exists, create new one!
            self.symbols[fn_signature.name] = FnSymbol(fn_signature.param_datatypes, fn_signature.param_names, fn_signature.returns) # btw, return values can be different across the sets (duh)

class SymbolTable(): 
    def __init__(self): 
        self.next_scope_id = 0
        self.current_scope_id = -1
        self.symbol_table: dict[int, Scope] = []
    def current_scope(self) -> Scope: 
        return self.symbol_table[self.current_scope_id]
    def push_scope(self, parent_id): 
        self.current_scope_id = self.next_scope_id
        self.next_scope_id+=1
        self.symbol_table[self.current_scope_id] = Scope(parent_id)
        return self.current_scope_id
    def leave_scope(self): # DO NOT POP; current scope will now refer to the parent scope of the current scope
        self.current_scope_id = self.current_scope().parent_id

    # check if expression (not the datatype of it) is assignable
    # variables
    # array accesses (in the future)
    # member accesses (in the future)
    # function calls (if pointers are added, in the future)
    def is_lvalue(expression: Expression) -> bool: 
        # next is array access
        # then next is dereferencing (also a function that returns a pointer)
        # if its member access, check every name
        # if its identifier, check if its a function, and then check if its toplevel
        if type(expression) is IdentifierExpression:  
            return True
        return False

    def is_variable() -> bool:
        raise Exception("Dev error, not implemented")

    # this symbol exists is unlike the Scope's symbol_exists
    # this one goes through every parent scope starting from the current scope
    # then finds stuff
    def symbol_exists(name) -> bool: 



        
        # build a reverse list of the symbol_table
        for scope in reversed(symbol_table): 
            if name in scope["symbols"]: return True
        return False

    def lookup_symbol(name) -> dict: 
        for scope in symbol_table.values(): 
            if name in scope["symbols"]: return scope[name]
        raise Exception("symbol does not exist anywhere")

    def push_scope(parent_id=-1) -> None: 
        global next_scope_id, symbol_table
        scope_id = next_scope_id
        next_scope_id += 1

        # if parent_id is guard value, then parent_id will be the last, or rather, the biggest id, which will be the last-put-on-the-stack
        if parent_id == -1:
            parent_id = next_scope_id - 1 # global scope will have a parent of -1 if i dont pass None

        symbol_table[scope_id] = {
            "symbols" : {},
            "parent": parent_id,
        }

        return scope_id

    def expression_datatype(expression: Expression) -> str | None: # None possibly, because of assignments, i dont know what to return from them
        # also handles assignment; the parser already checked that expressions can have - 
        # at most 1 assignment, and its position is going to be in expr_stmnt s
        match expression: 
            case LiteralExpression(datatype, value):
                return datatype

            case FnCallExpression(name, args): # {"type": "fn_call", "name": left, "args": parse_function_arguments()}
                # check if function exists
                # then check if parameters are correct-o
                # name = expression["name"]["value"] # im not sure about the ["value"] placement
                # if not symbol_exists(name): error("Function undeclared")
                # fn = assert_function(lookup_symbol(name), "eh... calling a non-function as a function much?")
                # grab datatypes from arguments
                # check if parameters work
                # given_datatypes = []
                # for exp in expression["args"]: 
                #    given_datatypes.append(expression_datatype(exp))
                # given_datatypes = tuple(given_datatypes)
                # now, given_datatypes is a list of strings, each string represents its corresponding -
                # argument's resulting datatype

                # existing_datatypes_S = fn["set"].keys()
                # if given_datatypes not in existing_datatypes_S: error(f"function '{fn} does not have '{given_datatypes}' as a function signature parameters?")

                # i assumey-sume that if block executes to this line, it means that every has gone smoothly ->
                # function exists, and the datatypes of the arguments match one of the 
                # possible list of datatypes inside the set of the function
                # i think i just have ot return the datatype of the function now!!!! yay im so proud of you!!! :)
                # return fn["set"][given_datatypes]["returns"]

                # ignoring named arguments because WHY THE FUCK DID YOU THINK I CAN DO THIS TAIWANGA
                # then, get the datatypes of given parameters
                # use that to get the return inside the set of a function
                pass

            case IdentifierExpression(name): 
                assert symbol_exists(name), "Variable undeclared"
                variable = lookup_symbol(name)
                assert is_variable(variable), "name referenced is not a variable, most likely its a function"
                return variable["datatype"]
            
            case NegateExpression(operand):
                assert expression_datatype(operand) == INT
                return INT # return itself, and since itself is either going to be int or float (the assert helped us narrow it down), itll just..work
            
            case NotExpression(operand):
                assert expression_datatype(operand) == BOOL
                return BOOL
            
            case UnaryAssignmentExpression(operator, variable):
                assert is_lvalue(variable), "must be lvalue"
                vt = expression_datatype(variable)
                match operator:
                    case "!!": assert vt == BOOL
                    case "++" | "--": assert vt == INT

            case BinaryAssignmentExpression(operator, lvalue, rvalue): # "=" | "+=" | "-=" | "*=" | "/=" | "%=": 
                assert is_lvalue(lvalue), "must be lvalue" # from now on, lvalues are already checked for actual lvalue
                lt = expression_datatype(lvalue)
                rt = expression_datatype(rvalue)
                match operator: 
                    case "=": 
                        # check l-value
                        # (the symbol of the variable (can be member_access) is already gotten using expression_datatype (function returns variable's datatype, is stored in val_datatype))
                        # check ^ datatype -- is it the same as val_datatype (done below)
                        # if expression_datatype(lvalue) != expression_datatype(rvalue): error(f"datatyps not compatable in variable assigning: expected '{lvalue_datatype}', got '{rvalue_datatype}'")
                        # i am not toooo sure about assigning 1 to a float variable, maybe i could promote it
                        # same with char into a string variable
                        assert lt == rt
                    
                    case "+=" | "-=" | "*=" | "/=" | "%=": 
                        # lvalue must be int or float
                        # if lvalue has a datatype of integer, then the rvalues can only result to an integer, because i cannot assign floats to an int
                        # if rvalue is a float though, then rvalue is anything goes, by anything goes i mean numerical thingies

                        assert lt == INT
                        assert rt == INT

                        # variable must be float type, because this is true division that results in floats every time, even if it's 6/2
                        # catch phrase is "as accurately as possible, while guranteeing uniformity"

            case BinaryExprExpression(operator, left, right):
                lt = expression_datatype(left)
                rt = expression_datatype(right)

                match operator: 
                    case "==" | "!=":
                        return BOOL # dont need to check types?

                    case "&" | "?" | "&?": 
                        assert lt == BOOL
                        assert rt == BOOL
                        return BOOL
                    
                    case "<" | ">" | "<=" | ">=": 
                        assert lt == INT
                        assert rt == INT
                        return BOOL
                    
                    case "+" | "-" | "*" | "/" | "%": 
                        assert lt == INT
                        assert rt == INT
                        return INT
                    
                    # this is true division, so result will always be a float, even if it's 6 / 2, itll result in 3.0
                    # for integer division, we can make it an operator, or just a function (for "a INT_DIV b", itll result in "toInt(a / b)")
                    # toInt will either round towards 0, or to negative Infinity idkyet, make separate functions
                    # good job thinking of solutions!
                    # to be consistent, division will always result in floats, but inputs can be any num

                    # modulo/remainder must have integer inputs (and integer output ofc too)
                    # modulo or remainder question unanswered

    # will modify statements (aka, the ast) in-place
    def analyze_statementS(statementS) -> None: 
        for statement in statementS:
            analyze_statement(statement)

    def analyze_statement(statement: Statement) -> None: 
        # IfStatement | BlockStatement | VarDeclStatement | FnDeclStatement | ExternFnStatement | BreakStatement
        #  | ContinueStatement | ReturnStatement | WhileStatement | IfElseStatement | ExpressionStatement
        match statement:
            case IfStatement(condition, block): 
                push_scope(block)
                analyze_statementS(block.code)
                pop_scope()

            case VarDeclStatement(name, datatype):
                add_variable_symbol(name, datatype)

            case BlockStatement(block):
                push_scope(block)
                analyze_statementS(block.code)
                pop_scope()

            case FnDeclStatement(fn_signature, block):
                                                                    # duplicate names already checked here
                self.current_scope().add_function_symbol(fn_signature)

                push_scope(block)
                functions.enter_function(fn_signature)

                # add parameters into the function (same 'pool' as the local variables)
                for param_name, param_datatype in zip(fn_signature.param_names, fn_signature.param_datatypes): 
                    add_variable_symbol(param_name, param_datatype)

                analyze_statementS(block.code)
                # add parameters into that scope -> make them appear initialized
                # elaborating on my previous comment, after i have all done you know, scope issues, i will move on to - 
                # solving uninitialized issues, where every variable (and function if i allow undefined functions that has a signature) - 
                # will have an additional flag called "initialized". Every initialization will start with this flag being false. -
                # In the case of parameters, the flag will be set to true because it techinically will be *actually initilized* when it's used
                functions.exit_function()
                pop_scope()

            case IfStatement(condition, block): 
                # no need to have a context/stack/a single global (bit) flag for a selection statement
                # because there isnt anything you cant do outside
                # of an if block you can only do inside an if block (e.g. while loops have break and continue
                # ; and functions have return statements)
                assert expression_datatype(condition) == BOOL

                push_scope(block)
                analyze_statementS(block.code)
                pop_scope()

            case IfElseStatement(condition, then_block, else_block):
                # hello, past you here, no need to have a context/stack/a single global (bit) flag
                # because there isnt anything you cant do outside
                # of an if block you can only do inside an if block (e.g. while loops have break and continue
                # ; and functions have return statements)
                assert expression_datatype(condition) == BOOL
                
                push_scope(then_block) # the if part starts
                analyze_statementS(then_block.code)
                pop_scope() # the if part ends

                push_scope(else_block) # the else part starts
                analyze_statementS(else_block.code)
                pop_scope() # the else part ends

            case WhileStatement(condition, block):
                assert expression_datatype(condition) == BOOL
                
                push_scope(block)
                loops.enter_one()
                analyze_statementS(block.code)
                loops.exit_one()
                pop_scope()

            case ReturnStatement(value):
                # no void functions :sad:
                assert functions.is_in_function(), "return EXPRESSION statements can only be used inside functions!" # though i dont know what I am currently in

                # expected type is the type the function, that the return statement here lives in, is supposed to return
                fn: FnSignatureThing = functions.current_function()

                assert expression_datatype(value) == fn.returns, f"Cannot return the datatype '{value}' from function '{fn.name}', because it is supposed to return '{fn.returns}'"

            case ContinueStatement(): assert loops.is_in_one(), "continue statements can only be used inside loops"
            case BreakStatement(): assert loops.is_in_one(), "break statements can only be used inside loops"
                
            case ExternFnStatement(fn_signature):
                # in contrast to normal functions, DO NOT NEED TO PUSH SCOPE lesgo!!!!
                add_function_symbol(fn_signature)
                # congrats, love
            
            case ExpressionStatement(expression):
                expression_datatype(expression) # i dont need the type, i just need it to check validity

push_scope(None)
analyze_statementS(statements)

write_to_json(OUTPUT_FILENAME, statements) # can't do this 