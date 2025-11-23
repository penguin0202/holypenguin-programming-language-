import json

def read_from_json(filename): 
    with open(filename, "r") as file: 
        return json.load(file)

def write_to_json(filename, data): 
    with open(filename, "w") as file: 
        json.dump(data, file, indent=4)

def to_plain_string(obj):
    """
    Recursively converts any Python object (dict, list, tuple, set, etc.)
    into a plain string representation.
    """
    # Fallback: manual recursive conversion
    if isinstance(obj, dict):
        return "{" + ", ".join(f"{to_plain_string(k)}: {to_plain_string(v)}" for k, v in obj.items()) + "}"
    elif isinstance(obj, (list, tuple, set)):
        open_bracket, close_bracket = ("[", "]") if isinstance(obj, list) else ("(", ")") if isinstance(obj, tuple) else ("{", "}")
        return open_bracket + ", ".join(to_plain_string(item) for item in obj) + close_bracket
    else:
        return str(obj)