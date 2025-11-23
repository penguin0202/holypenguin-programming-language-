from json_funcs import *
import os
import pprint

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "parsed.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "semantically-analyzed.txt")

# tuples are used for hash-ability

statements = read_from_json(INPUT_FILENAME)
symbol_table = []

BOOL = "bool"
STR = "str"
FLOAT = "float"
INT = "int"
CHAR = "char"

# this also checks for duplicate parameter names
def grab_fn_signature(parsed_fn) -> tuple: 
    #guard
    type = parsed_fn["type"]
    assert type in ["fn_decl", "external_function_declaration"], "expected a parsed function dictionary"
    
    name = parsed_fn["name"]
    returns = parsed_fn["returns"]
    parameter_datatypes = parsed_fn["param_datatypes"]
    parameter_names = parsed_fn["param_names"]

    # PARAM CHECK----------
    seen_parameter_names = []

    for name in parameter_names: 
        # does not care about type of duplicate name
        assert name not in seen_parameter_names, f"duplicate parameter '{name}'"
        seen_parameter_names.append(name)
    # PARAM CHECK DONE -------

    return name, returns, parameter_datatypes, parameter_names

# check if expression (not the datatype of it) is assignable
# variables
# array accesses (in the future)
# member accesses (in the future)
# function calls (if pointers are added, in the future)
def is_lvalue(expression):
    type = expression["type"]
    # next is array access
    # then next is dereferencing (also a function that returns a pointer)
    # if its member access, check every name
    # if its identifier, check if its a function, and then check if its toplevel
    if type == "identifier": 
        return True
    return False

def is_variable():
    raise Exception("Dev error, not implemented")

# chatgpt recommends instead of just a marker, add function names (and my own thinking because of function overloading: and function parameters) - 
# to identify what function is being returned
# marker/function_context now looks like this: 
# [ {"name": name, "params": params}, {"name": name, "params": params}, ...]
function_context = [] # it is a stack instead of just a global bit flag because you need the return datatype later on for every single inner function
def enter_function(name, param_datatypes, param_names, returns): function_context.append({"name": name, "parameter_datatypes": param_datatypes, "parameter_names": param_names, "returns": returns})
def exit_function() -> None: function_context.pop(-1)
def current_function() -> dict: return function_context[-1]
def is_in_function() -> bool: return len(function_context) > 0

# did not make a loop_context because i dont think i need to store any metadata regarding the loop
# other than that I am in one so i can validate breka and continue statements
in_loop = False
def enter_loop(): global in_loop; in_loop = True
def exit_loop(): global in_loop; in_loop = False
def is_in_loop(): return in_loop

def add_variable_symbol(name, datatype) -> None: 
    assert symbol_table, "Cannot add symbol, no scope exists"
    current_scope_symbols = symbol_table[-1]["symbols"]
    assert name not in current_scope_symbols, f"Symbol ({name["kind"]}) with this name already exists in your current scope!"
    current_scope_symbols[name] = {"kind": "variable", "datatype": datatype}
    # overflows/underflows/div_by_0 will be runtime errors, as symbols only store name and datatypes

def add_function_symbol(name, param_datatypes, param_names, returns) -> None: # {'type': 'fn_decl', "returns": datatype, 'name': name, 'args': parameters, "block": parse_block()}
    assert symbol_table, "Cannot add symbol, no scope exists"
    current_scope_symbols = symbol_table[-1]["symbols"]
    if name in current_scope_symbols: 
        # if name is a symbol that exists, but is not a function, then we can't "overload" a variable
        func = current_scope_symbols[name]
        assert func["kind"] == "function", "symbol already exists not as a function"

        # generate, from all keys inside the "set" of the function, a list containing all existing param lists
        # no conflicts, good job david *pats head*

        existing_datatypes_S = []
        for i_dont_know_what_to_name_this in current_scope_symbols[name]["set"]: 
            existing_datatypes_S.append(i_dont_know_what_to_name_this["datatypes"])

        assert param_datatypes not in existing_datatypes_S, "duplicate function signature, where datatypes coincide"

        # if code executes here, it means both of the following
        # 1. param_datatypes is not in existing_datatypes_S, that means we can append it!
        # 2. past you (one who called this function) guranteed that names don't coincide
        # btw, the checking of the return types is handled by the function context
        current_scope_symbols[name]["set"].append({
            "datatypes": param_datatypes,
            "names": param_names, 
            "returns": returns
        })
    else: # if no function set already exists, create new one!
        current_scope_symbols[name] = {
            "kind": "function",
            "set": [{
                    "datatypes": param_datatypes,
                    "names": param_names, 
                    "returns": returns # btw, return values can be different across the sets (duh)
            }]
        }

def symbol_exists(name) -> bool: 
    for scope in reversed(symbol_table): 
        if name in scope["symbols"]: return True
    return False

def lookup_symbol(name) -> dict: 
    for scope in reversed(symbol_table): 
        if name in scope["symbols"]: return scope[name]
    raise Exception("symbol does not exist anywhere")

def push_scope(node) -> None: 
    # using python references (necessary evil)
    parent = symbol_table[-1] if symbol_table else None
    singular_symbol_table = {"symbols" : {}, "parent": parent}
    node["symbol_table"] = singular_symbol_table
    symbol_table.append(singular_symbol_table)

def pop_scope() -> None | dict: 
    assert symbol_table, "cannot pop scope if symbol table is empty"
    symbol_table.pop() # popped last item, aka last inserted item
    return # you can return the popped scope by putting the above here, but right now i have no sue of debugging yet (sue? i meant use)

def expression_type(expression) -> str | None: # None possibly, because of assignments, i dont know what to return from them
    # also handles assignment; the parser already checked that expressions can have - 
    # at most 1 assignment, and its position is going to be in expr_stmnt s
    match expression["type"]: 
        case "literal":
            return expression["datatype"]

        case "fn_call": # {"type": "fn_call", "name": left, "args": parse_function_arguments()}
            # check if function exists
            # then check if parameters are correct-o
            # name = expression["name"]["value"] # im not sure about the ["value"] placement
            # if not symbol_exists(name): error("Function undeclared")
            # fn = assert_function(lookup_symbol(name), "eh... calling a non-function as a function much?")
            # grab datatypes from arguments
            # check if parameters work
            # given_datatypes = []
            # for exp in expression["args"]: 
            #    given_datatypes.append(expression_type(exp))
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

        case "identifier": 
            name = expression["value"]
            assert symbol_exists(name), "Variable undeclared"
            variable = lookup_symbol(name)
            assert is_variable(variable), "name referenced is not a variable, most likely its a function"
            return variable["datatype"]
        
        case "negate_expr":
            operand = expression["operand"]
            assert expression_type(operand) == INT
            return INT # return itself, and since itself is either going to be int or float (the assert helped us narrow it down), itll just..work
        
        case "not_expr":
            operand = expression["operand"]
            assert expression_type(operand) == BOOL
            return BOOL
        
        case "unary_assignment":
            operator = expression["operator"]
            variable = expression["variable"]
            assert is_lvalue(variable), "must be lvalue"
            vt = expression_type(variable)
            match operator:
                case "!!": assert vt == BOOL
                case "++" | "--": assert vt == INT

        case "binary_assignment": # "=" | "+=" | "-=" | "*=" | "/=" | "%=": 
            operator = expression["operator"]
            lvalue = expression["variable"]
            assert is_lvalue(lvalue), "must be lvalue" # from now on, lvalues are already checked for actual lvalue
            rvalue = expression["value"]
            lt = expression_type(lvalue)
            rt = expression_type(rvalue)
            match operator: 
                case "=": 
                    # check l-value
                    # (the symbol of the variable (can be member_access) is already gotten using expression_type (function returns variable's datatype, is stored in val_datatype))
                    # check ^ datatype -- is it the same as val_datatype (done below)
                    # if expression_type(lvalue) != expression_type(rvalue): error(f"datatyps not compatable in variable assigning: expected '{lvalue_datatype}', got '{rvalue_datatype}'")
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

        case "binary_expr":
            operator = expression["operator"]
            left = expression["left"]
            right = expression["right"]
            lt = expression_type(left)
            rt = expression_type(right)

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

def analyze_statement(statement) -> None: 
    match statement["type"]:
        
        case "module": 
            block = statement["block"]
            push_scope(block)
            analyze_statementS(block["code"])
            pop_scope()

        case "var_decl":
            name = statement["name"]
            datatype = statement["datatype"]
            add_variable_symbol(name, datatype)

        case "block":
            block = statement["block"]
            push_scope(block)
            analyze_statementS(block["code"])
            pop_scope()

        case "fn_decl":     
                                                                # duplicate names already checked here
            name, returns, parameter_datatypes, parameter_names = grab_fn_signature(statement)
            add_function_symbol(name, parameter_datatypes, parameter_names, returns)

            block = statement["block"]

            push_scope(block)
            enter_function(name, parameter_datatypes, parameter_names, returns)

            # add parameters into the function (same 'pool' as the local variables)
            for param_name, param_datatype in zip(parameter_names, parameter_datatypes): 
                add_variable_symbol(param_name, param_datatype)

            analyze_statementS(block["code"])
            # add parameters into that scope -> make them appear initialized
            # elaborating on my previous comment, after i have all done you know, scope issues, i will move on to - 
            # solving uninitialized issues, where every variable (and function if i allow undefined functions that has a signature) - 
            # will have an additional flag called "initialized". Every initialization will start with this flag being false. -
            # In the case of parameters, the flag will be set to true because it techinically will be *actually initilized* when it's used
            exit_function()
            pop_scope()

        case "if":
            # no need to have a context/stack/a single global (bit) flag for a selection statement
            # because there isnt anything you cant do outside
            # of an if block you can only do inside an if block (e.g. while loops have break and continue
            # ; and functions have return statements)
            condition = statement["condition"]
            assert expression_type(condition) == BOOL

            block = statement["block"]
            push_scope(block)
            analyze_statementS(block["code"])
            pop_scope()

        case "if_else":
            # hello, past you here, no need to have a context/stack/a single global (bit) flag
            # because there isnt anything you cant do outside
            # of an if block you can only do inside an if block (e.g. while loops have break and continue
            # ; and functions have return statements)
            condition = statement["condition"]
            assert expression_type(condition) == BOOL

            then_block = statement["then-block"]
            else_block = statement["else-block"]
            
            push_scope(then_block) # the if part starts
            analyze_statementS(then_block["code"])
            pop_scope() # the if part ends

            push_scope(else_block) # the else part starts
            analyze_statementS(else_block["code"])
            pop_scope() # the else part ends

        case "while":
            condition = statement["condition"]
            assert expression_type(condition) == BOOL
            
            block = statement["block"]
            push_scope(block)
            enter_loop()
            analyze_statementS(block["code"])
            exit_loop()
            pop_scope()

        case "return":
            # no void functions :sad:
            assert is_in_function(), "return EXPRESSION statements can only be used inside functions!" # though i dont know what I am currently in

            return_value = statement["value"]

            # expected type is the type the function, that the return statement here lives in, is supposed to return
            le_function = current_function()
            fn_name = le_function["name"]
            expected_type = le_function["returns"]

            assert expression_type(return_value) == expected_type, f"Cannot return the datatype '{return_value}' from function '{fn_name}', because it is supposed to return '{expected_type}'"

        case "continue": assert is_in_loop(), "continue statements can only be used inside loops"
        case "break": assert is_in_loop(), "break statements can only be used inside loops"
            
        case "external_fn":
            # in contrast to normal functions, DO NOT NEED TO PUSH SCOPE lesgo!!!!
            name, returns, parameter_datatypes, parameter_names = grab_fn_signature(statement)
            add_function_symbol(name, parameter_datatypes, parameter_names, returns)
            # congrats, love
        
        case "expr":
            expression = statement["expression"]
            expression_type(expression) # i dont need the type, i just need it to check validity

analyze_statementS(statements)

write_to_json(OUTPUT_FILENAME, statements) # can't do this 