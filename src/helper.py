from globals import *

def Operator(on_datatype, operator): return {"type": "operator", "on_datatype": on_datatype, "thingy": operator}
def Accessor(): return {"type": "accessor"}
def Assigner(on_datatype, assigner): return {"type": "assigner", "on_datatype": on_datatype, "thingy": assigner}
def Mutator(on_datatype, mutator): return {"type": "mutator", "on_datatype": on_datatype, "thingy": mutator}
def Comparator(on_datatype, comparator): return {"type": "comparator", "on_datatype": on_datatype, "thingy": comparator}
def Literal(datatype, value): return {"type": "literal", "datatype": datatype, "value": value}
def Identifier(name): return {"type": "identifier", "value": name}
def Keyword(name): return {"type": "keyword", "value": name}
def Datatype(name): return {"type": "datatype", "value": name}
def Other(thing): return {"type": thing}

def get_datatype_of_numerical_operation(types_tuple): 
    if types_tuple in [("int", "float"), ("float", "int"), ("float", "float")]: return "float"
    elif types_tuple == ("int", "int"): return "int" # int div int = int (round down/round to 0)
    else: raise Exception(f"cannot add/sub/mul/div on {types_tuple}")

def get_datatype_of_numerical_comparison(types_tuple): 
    if types_tuple in [("int", "int"), ("int", "float"), ("float", "float"), ("float", "int")]: return "bool"
    raise Exception(f"cannot compare numerically: {types_tuple}")

def get_datatype_of_general_comparison(types_tuple): 
    if types_tuple in [("int", "float"), ("float", "int"), ("int", "int"), ("float", "float"), ("str", "str"), ("bool", "bool")]: return "bool"
    raise Exception(f"cannot generally compare a {types_tuple}")

def is_numerical_comparator(op): return op in ["smaller_than", "larger_than", "smaller_than_or_equal_to", "larger_than_or_equal_to"]
def is_general_comparator(op): return op in ["equals_to", "not_equals"]
def is_basic_4_numerical_operator(op): return op in ["add", "sub", "mul", "div"]

ASSIGNER_NUM_NORMAL = ["assigner:num:normal:add", "assigner:num:normal:sub", "assigner:num:normal:mul", "assigner:num:normal:div", "assigner:num:normal:mod"]

def determine_name(name): 
    if name in ["if", "else", "while", "return", "break", "continue", "extern"]: return Keyword(name)
    elif name in ["fn", "int", "str", "bool", "char"]: return Datatype(name)
    elif name in ["true", "false"]: return Literal("bool", name)
    return Identifier(name)

def split_on(datalist, ofdata, delimeter): 
    full = []
    small = []
    for item in datalist: 
        try: 
            if item[ofdata] != delimeter: small.append(item)
            else: 
                full.append(small)
                small = []
        except: raise Exception(f'ofdata of item inside datalist does not exist: item={item}')
    if small: full.append(small)
    return full

MUTATORS = ["++", "--", "!!"]
ASSIGNERS = ["=", "+=", "-=", "*=", "/=", "%=", "~="]