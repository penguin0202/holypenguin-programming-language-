BOOL = "bool"
STR = "str"
FLOAT = "float"
INT = "int"
CHAR = "char"

def error(text) -> None: raise Exception(text)

def assert_variable(symbol, msg): 
    if symbol["kind"] != "variable": error(msg)
    return symbol

def assert_function(symbol, msg): 
    if symbol["kind"] != "function": error(msg)
    return symbol

# this also checks for duplicate parameter names
def grab_fn_signature(parsed_fn) -> tuple: 
    #guard
    type = parsed_fn["type"]
    if type not in ["fn_decl", "external_function_declaration"]: error("expected a parsed function dictionary")
    
    name = parsed_fn["name"]
    returns = parsed_fn["returns"]
    parameter_datatypes = parsed_fn["param_datatypes"]
    parameter_names = parsed_fn["param_names"]

    # PARAM CHECK----------
    seen_parameter_names = []

    for name in parameter_names: 
        # does not care about type of duplicate name
        if name in seen_parameter_names: error(f"duplicate parameter '{name}'")
        seen_parameter_names.append(name)
    # PARAM CHECK DONE -------

    return name, returns, parameter_datatypes, parameter_names