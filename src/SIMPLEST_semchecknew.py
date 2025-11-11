from json_funcs import *

INPUT_FILE = "parsed.txt"
OUTPUT_FILE = "sem_checked.txt"

statements = read_from_json(INPUT_FILE)
symbol_table = [{}]

def assert_numerical(thing, msg): 
    thing_type = expression_type(thing)
    if thing_type not in ["int", "float"]: error(msg)
    return thing_type

def assert_int(thing, msg): 
    thing_type = expression_type(thing)
    if thing_type != "int": error(msg)
    return thing_type

def assert_float(thing, msg): 
    thing_type = expression_type(thing)
    if thing_type != "float": error(msg)
    return thing_type

def assert_bool(thing, msg): 
    thing_type = expression_type(thing)
    if thing_type != "bool": error(msg)
    return thing_type

def assert_text(thing, msg): 
    thing_type = expression_type(thing)
    if thing_type not in ["str", "char"]: error(msg)
    return thing_type

def assert_str(thing, msg): 
    thing_type = expression_type(thing)
    if thing_type != "str": error(msg)
    return thing_type

def assert_variable(symbol, msg): 
    if symbol["kind"] != "variable": error(msg)
    return symbol

def assert_function(symbol, msg): 
    if symbol["kind"] != "function": error(msg)
    return symbol

# check if value is assignable
# expression is 
def lvalue_assert(expression, msg): 
    type = expression["type"]
    # next is array access
    # then next is dereferencing (also a function that returns a pointer)
    # if its member access, check every name
    # if its identifier, check if its a function, and then check if its toplevel
    if type != "identifier": error(msg)
    return expression
    
# holy fucking shit there is a lot of caveats
# ok, so void function arent a thing yet...... FUCK

# BTW, OVERFLOW ERRORS FROM ASSIGNING VALUES TO VARIABLES WILL BE HANDLED IN LATER STAGES OR AT RUNTIME
# dont worry about it here my love

# chatgpt recommends instead of just a marker, add function names (and my own thinking because of function overloading: and function parameters) - 
# to identify what function is being returned
# marker/function_context now looks like this: 
# [ {"name": name, "params": params}, {"name": name, "params": params}, ...]
function_context = [] # it is a stack instead of just a global bit flag because you need the return datatype later on for every single inner function
def enter_function(name, param_datatypes, param_names, returns): function_context.append({"name": name, "parameter_datatypes": param_datatypes, "parameter_names": param_names, "returns": returns})
def exit_function(): function_context.pop(-1)
def current_function(): return function_context[-1]
def is_inside_function(): return len(function_context) > 0

# did not make a loop_context because i dont think i need to store any metadata regarding the loop
# other than that I am in one so i can validate breka and continue statements

in_loop = False

#if i change my mind
#here, my love: 
'''loops_context = []
def enter_while_loop(): loops_context.push(0)
def exit_while_loop(): loops_context.pop()
def is_inside_while_loop(): return len(loops_context) > 0'''

def add_variable_symbol(name, datatype): 
    if not symbol_table: error("Cannot add symbol, no scope exists")
    current_scope = symbol_table[-1]
    if name in current_scope: error(f"Symbol ({name["kind"]}) with this name already exists in your current scope!")
    symbol_table[-1][name] = {"kind": "variable", "datatype": datatype}
    # right now, symbol tables only store datatypes, no values, so during compilation, if sem check is the only
    # step that stores variable data, then there will be no code that can check for overflows at compile time
    # or div by 0 by that matter

def grab_datatypes_from_parameters(param_list): 
    list_of_datatypes = []
    for param in param_list: 
        if "datatype" not in param.keys(): error("dev error, whoever called this function did not provide an actual parameter list")
        list_of_datatypes.append(param["datatype"])

# this also checks for duplicate parameter names
def grab_fn_signature(parsed_fn): 
    #guard
    type = parsed_fn["type"]
    if type not in ["fn_decl", "external_function_declaration"]: error("expected a parsed function dictionary")
    
    name = parsed_fn["name"]
    returns = parsed_fn["returns"]
    parameter_datatypes = parsed_fn["param_datatypes"]
    parameter_names = parsed_fn["param_names"]
    # code = parsed_fn["block"]

    # PARAM CHECK----------
    seen_parameter_names = []

    for name in parameter_names: 
        # does not care about type of duplicate name
        if name in seen_parameter_names: error(f"duplicate parameter '{name}'")
        seen_parameter_names.append(name)
    # PARAM CHECK DONE -------

    return name, returns, parameter_datatypes, parameter_names #, code

def add_function_symbol(name, param_datatypes, param_names, returns): # {'type': 'fn_decl', "returns": datatype, 'name': name, 'args': parameters, "block": parse_block()}
    if not symbol_table: error("Cannot add symbol, no scope exists")
    current_scope = symbol_table[-1]
    if name in current_scope: 
        # i mean if symbol already exists as not-a-function, that would be a big problemo
        assert_function(current_scope[name], "symbol already exists not as a function")

        # generate, from all keys inside the "set" of the function, a list containing all existing param lists
        existing_datatypes_S = current_scope[name]["set"].keys() # no conflicts, good job david *pats head*
        if param_datatypes in existing_datatypes_S: error("duplicate function signature, where datatypes coincide")

        # if here, that means given_datatypes is not, in fact, in existing_datatypes_s, that means we can add it!!!
        # youre so smart david i love u
        # adding it here: 
        # btw, past you (whoever called this function) already made sure names do not coincide, so here you only
        # had to check if datatypes coincide (good job david! keep it up)
        # idk why this thought popped into my head, but do we have to check if "returns" is valid somewhere?
        # or does the lexer, or ig the parser too, already distinguish that? you ask some really good questions david
        # it auto-adds, albeit seems like im accessing an item that doesnt exist
        current_scope[name]["set"][tuple(param_datatypes)] = {
            "names": param_names, 
            "returns": returns
        }

        # check parameters allowed here at the top
        # function overloading lesgo!!! im so excited!
        # caveat: produce compiler error if when overloading, function has the same parameter types
        # cuz what the fuck am I supposed to do with
        # 'fn void print(str text) {System.out.println(text)}'
        # and 'fn str print(str text) {return text}'
        # how do i tell them apart?
    else: 
        # if no function set already exists, create new one!
        symbol_table[-1][name] = {
            "kind": "function",
            "set": { # "ADD A SET WHERE THE KEY IS THE PARAMETERS AND THE VALUE AS ITS CODE AND RETURN VALUES (BTW RETURN VALUES CAN BE DIFFERENT ACROSS SETS)"
                tuple(param_datatypes): {
                    "names": param_names, 
                    "returns": returns
                }
            }
        }
        # key of inside set is an tuple, because those are hashable or something idfk fucking python

def symbol_exists(name): 
    for scope in reversed(symbol_table): 
        if name in scope: return True
    return False

def lookup_symbol(name): 
    for scope in reversed(symbol_table): 
        if name in scope: return scope[name]
    error("symbol does not exist anywhere")

def error(text): raise Exception(text)

def push_scope(): symbol_table.append({})
def pop_scope(): 
    if not symbol_table: error("cannot pop scope if symbol table is empty")
    symbol_table.pop() # popped last item, aka last inserted item
    return # you can return the popped scope by putting the above here, but right now i have no sue of debugging yet (sue? i meant use)

def expression_type(expression):
    # also handles assignment; the parser already checked that expressions can have - 
    # at most 1 assignment, and its position is going to be in expr_stmnt s
    match expression["type"]: 
        case "literal": return expression["datatype"]
        case "fn_call": # {"type": "fn_call", "name": left, "args": parse_function_arguments()}
            # check if function exists
            # then check if parameters are correct-o
            name = expression["name"]["value"] # im not sure about the ["value"] placement
            if not symbol_exists(name): error("Function undeclared")
            fn = assert_function(lookup_symbol(name), "eh... calling a non-function as a function much?")
            # grab datatypes from arguments
            # check if parameters work
            given_datatypes = []
            for exp in expression["args"]: 
                given_datatypes.append(expression_type(exp))
            given_datatypes = tuple(given_datatypes)
            # now, given_datatypes is a list of strings, each string represents its corresponding -
            # argument's resulting datatype

            existing_datatypes_S = fn["set"].keys()
            if given_datatypes not in existing_datatypes_S: error(f"function '{fn} does not have '{given_datatypes}' as a function signature parameters?")

            # i assumey-sume that if code executes to this line, it means that every has gone smoothly ->
            # function exists, and the datatypes of the arguments match one of the 
            # possible list of datatypes inside the set of the function
            # i think i just have ot return the datatype of the function now!!!! yay im so proud of you!!! :)
            return fn["set"][given_datatypes]["returns"]

            # ignoring named arguments because WHY THE FUCK DID YOU THINK I CAN DO THIS TAIWANGA
            # then, get the datatypes of given parameters
            # use that to get the return inside the set of a function
        case "identifier": 
            name = expression["value"]
            if not symbol_exists(name): error("Variable undeclared")
            variable = assert_variable(lookup_symbol(name), "unfortunately, the name you referenced is not a variable!")
            return variable["datatype"]
            # check if variable exists as a variable (AND NOT A FUNCTION!!!)
            # then get the datatype of it
        case "negate_expr": # {"type": "negate_expr", "operand": parse_atom()}
            operand = expression["operand"]
            operand_datatype = assert_numerical(operand, "negation can only work on int and float values")
            return operand_datatype # return itself, and since itself is either going to be int or float (the assert helped us narrow it down), itll just..work
        case "not_expr": # {"type": "not_expr", "operand": parse_atom()}
            operand = expression["operand"]
            assert_bool(operand, "not unary oepration can only work on boolean values")
            return "bool"
        case "unary_assignment": # left = {"type": "unary_assignment", "operator": operator, "variable": left}
            operator = expression["operator"]
            variable = lvalue_assert(expression["variable"])
            match operator:
                # hey, this is where l-values and r-values come into play, we can do this a little later, right? hehehhe
                # here, we can check if variable is numerical variable (int, float)
                # haven't checked l-values yet, only checks its type
                case "!!": assert_bool(variable, "variable must be a boolean")
                case "++" | "--": assert_numerical(variable, "variable must be int or float")
        case "binary_assignment": # "=" | "+=" | "-=" | "*=" | "/=" | "%=" | "~=": 
            operator = expression["operator"]
            lvalue = lvalue_assert(expression["variable"])
            # from now on, lvalues are already checked for actual lvalue
            rvalue = expression["value"]
            match operator: 
                case "=": 
                    # check l-value
                    # (the symbol of the variable (can be member_access) is already gotten using expression_type (function returns variable's datatype, is stored in val_datatype))
                    # check ^ datatype -- is it the same as val_datatype (done below)
                    # if expression_type(lvalue) != expression_type(rvalue): error(f"datatyps not compatable in variable assigning: expected '{lvalue_datatype}', got '{rvalue_datatype}'")
                    # i am not toooo sure about assigning 1 to a float variable, maybe i could promote it
                    # same with char into a string variable
                    pass
                
                case "+=" | "-=" | "*=": 
                    # lvalue must be int or float
                    # if lvalue has a datatype of integer, then the rvalues can only result to an integer, because i cannot assign floats to an int
                    # if rvalue is a float though, then rvalue is anything goes, by anything goes i mean numerical thingies

                    lvalue_datatype = assert_numerical(lvalue, "must be a numerical type")

                    # check l-value
                    if lvalue_datatype == "int": assert_int(rvalue, "if lvalue is an int, then rvalue must be too, because what do you mean add 3.5 to an integer variable")
                    if lvalue_datatype == "float": assert_numerical(rvalue, "if lvalue is a float, then rvalue can be anything, albeit numerical")

                case "/=": 
                    # variable must be float type, because this is true division that results in floats every time, even if it's 6/2
                    assert_float(lvalue, "l-value must be ints or floats")
                    assert_numerical(rvalue, "r-value must be ints or floats")
                
                case "|=": 
                    assert_int(lvalue, "lvalue must be an integer in an integer division")
                    assert_int(rvalue, "rvalue must be an integer in an integer division")
                case "%=": 
                    assert_int(lvalue, "l-value must be an integer in a modulus assignment")
                    assert_int(rvalue, "r-value must be an integer in a modulus assignment")

                case "~=": 
                    # check ^ datatype -- is it a string (if it is a char, then it can't concatenate, that would result in a string)
                    assert_str(lvalue, "l-value must be a string or a character")
                    assert_text(rvalue, "r-value must be a string or a character")
        case "binary_expr": # a general binary expression
            # to be consistent, division will always result in floats, but inputs can be any num
            # idk about modulo or remainder, they all have to be integers tho, keep that in mind, davide-o
            operator = expression["operator"]
            left = expression["left"]
            right = expression["right"]

            match operator: 
                case "==" | "!=": return "bool" # dont need to check types?

                case "&" | "?" | "&?": 
                    assert_bool(left, "logical operators must have boolean values on the left")
                    assert_bool(right, "logical operators must have boolean values on the right")
                    return "bool"
                
                case "<" | ">" | "<=" | ">=": 
                    assert_numerical(left, "left datatype must be an int or float for numerical comparisons")
                    assert_numerical(right, "right datatype must be an int or float for numerical comparisons")
                    return "bool"
                
                case "+" | "-" | "*": 
                    left_datatype = assert_numerical(left, "left datatype must be an int or float for numerical comparisons")
                    right_datatype = assert_numerical(right, "right datatype must be an int or float for numerical comparisons")
                    
                    if (left_datatype, right_datatype) == ("int", "int"): return "int"
                    return "float"
                
                # this is true division, so result will always be a float, even if it's 6 / 2, itll result in 3.0
                # for integer division, we can make it an operator, or just a function (for "a INT_DIV b", itll result in "toInt(a / b)")
                # toInt will either round towards 0, or to negative Infinity idkyet, make separate functions
                # good job thinking of solutions!
                case "/": 
                    assert_numerical(left, "left datatype must be numerical for division")
                    assert_numerical(right, "right datatype must be numerical for division")
                    return "float"

                # cannot work on floating point numbers
                case "|": 
                    assert_int(left, "left datatype must be an int for quotient-ding")
                    assert_int(right, "right datatype must be an int for quotient-ding")
                    return "int"
                # cannot work on floating point numbers, handle modulus vs remainder later, right now it checks integers, not >0 ints
                case "%": 
                    assert_int(left, "left datatype must be an int for mod-ding")
                    assert_int(right, "right datatype must be an int for mod-ding")
                    return "int"
                
                case "~": 
                    assert_text(left, "left datatype must be str or char")
                    assert_text(right, "right datatype must be str or char")
                    return "str" # no matter if it's char ~ char, it's going to be str regardless

def analyze_statementS(statementS): 
    for statement in statementS:
        analyze_statement(statement)

def analyze_statement(statement): 
    match statement["type"]:
        case "var_decl": # {"type": "var_decl", "name": name, "datatype": datatype}
            name = statement["name"]
            datatype = statement["datatype"]
            add_variable_symbol(name, datatype)
        case "just_a_block": # {"type": "just_a_block", "code": parse_block()}
            code = statement["code"]
            push_scope()
            # this part is looping through the "code" block inside the "just_a_block" and type checking everything inside IT
            analyze_statementS(code)
            pop_scope()
        case "fn_decl": # {'type': 'fn_decl', "returns": datatype, 'name': name, "param_names": parameters["names"], "param_datatypes": parameters["datatypes"], "block": parse_block()}
            # first, check every parameter name against each other or im graping you
            # this is because the parameters list will be used in two places, and i dont want to repeat code
            # the two places are: adding parameters into symbol
            # and adding parameters into the scope itself
            # so here, i will check parameter names against each other to avoid name duplication
            # and the function i will call will check parameters list agianst each other to avoid  func signature duplication
            # holy cow!!
                                                                  # duplicate names already checked here
            name, returns, parameter_datatypes, parameter_names = grab_fn_signature(statement)
            add_function_symbol(name, parameter_datatypes, parameter_names, returns)
            # congrats, love

            code = statement["block"]

            push_scope()
            enter_function(name, parameter_datatypes, parameter_names, returns)
            analyze_statementS(code)
            # HOLY FUCKING SHIT I DID IT
            # someone give me headpats right now
            # add parameters into that scope -> make them appear initialized
            # elaborating on my previous comment, after i have all done you know, scope issues, i will move on to - 
            # solving uninitialized issues, where every variable (and function if i allow undefined functions that has a signature) - 
            # will have an additional flag called "initialized". Every initialization will start with this flag being false, in the case of - 
            # "var_decl_and_init", it will set the flag to false, then immeidately true. In the case of parameters, the flag will be set - 
            # to true because it techinically will be *actually initilized* when it's used
            # heheheha dont worry about it tho, love, thatll be future you's (easy) job
            # type check everything inside function -> use function context to determine if return statements are valid!!!
            # ^ including the use of return statements
            exit_function()
            pop_scope()
        case "if_stmnt": # {'type': 'if_stmnt', 'condition': exp, 'if-then_block': parse_block()}
            # hello, past you here, no need to have a context/stack/a single global (bit) flag
            # because there isnt anything you cant do outside
            # of an if block you can only do inside an if block (e.g. while loops have break and continue
            # ; and functions have return statements)
            condition = statement["condition"]
            assert_bool(condition, "conditions (in an if) must be a boolean (what'd you expect)")
            # check condition here?
            code = statement["if-then_block"]
            push_scope()
            analyze_statementS(code)
            pop_scope()
        case "if_else_stmnt": # {'type': 'if_else_stmnt', 'condition': exp, 'if-then_block': if_block, 'else_block': parse_block()}
            # hello, past you here, no need to have a context/stack/a single global (bit) flag
            # because there isnt anything you cant do outside
            # of an if block you can only do inside an if block (e.g. while loops have break and continue
            # ; and functions have return statements)
            condition = statement["condition"]
            assert_bool(condition, "conditions (in an if-else) must be a boolean (what'd you expect)")\

            code_then = statement["if-then_block"]
            code_else = statement["else_block"]

            push_scope() # the if part starts
            analyze_statementS(code_then)
            pop_scope() # the if part ends
            push_scope() # the else part starts
            analyze_statementS(code_else)
            pop_scope() # the else part ends

        case "while_stmnt": # {'type': 'while_stmnt', 'condition': exp, 'while_block': parse_block()}
            # first off, check the condition - is boolean, makes sense, references exist, etc idk yet, its ok we can do it later
            condition = statement["condition"]
            assert_bool(condition, "conditions (in a while loop) must be a boolean (what'd you expect)")
            
            code = statement["while_block"]
            push_scope()
            is_loop = True
            analyze_statementS(code)
            is_loop = False
            pop_scope()
        case "return_stmnt": # {"type": "return_stmnt", "value": exp}
            # no void functions anywhere
            if not is_inside_function(): error("return EXPRESSION statements can only be used inside functions!") # though i dont know what I am currently in
            # check value against the returns of the current_function(), has to be same or else throw return mismatch error
            # dont worry about the previous comment yet, love
            # idk

            return_value = statement["value"]

            # expected type is the type the function, that the return statement here lives in, is supposed to return
            le_function = current_function()
            fn_name = le_function["name"]
            expected_type = le_function["returns"]
            if expression_type(return_value) != expected_type: error(f"Cannot return the datatype '{return_value}' from function '{fn_name}', because it is supposed to return '{expected_type}'")
            # IM SO PROUD OF YOU FOR USING THE FUNCTION CONTEXT!!!! <3333
        case "continue_stmnt": # {"type": "continue_stmnt"}
            if not is_loop: error("continue statements can only be used inside loops")
            # idk
        case "break_stmnt": # {"type": "break_stmnt"}
            if not is_loop: error("break statements can only be used inside loops")
            # idk
        case "external_function_declaration": # {"type": "external_function_declaration", "name": name, "returns": datatype, "param_names": parameters["names"], "param_datatypes": parameters["datatypes"]}
            # in contrast to normal functions, DO NOT NEED TO PUSH SCOPE lesgo!!!!
            name, returns, parameter_datatypes, parameter_names = grab_fn_signature(statement)
            add_function_symbol(name, parameter_datatypes, parameter_names, returns)
            # congrats, love
        
        case "expr_stmnt": # {"type": "expr_stmnt", "expression": expr}
            # firstly, before I get into any expression handling, do this first to get a feel, then get -
            # into inline expressions
            # first check if expression statement is an assignment statement
            # assignment statements will use the function of 'lookup_symbol' to do the things
            expression = statement["expression"]
            expression_type(expression) # i dont need the type, i just need it to check validity

analyze_statementS(statements)