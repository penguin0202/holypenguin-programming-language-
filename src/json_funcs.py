import json

def read_from_json(filename): 
    with open(filename, "r") as file: 
        return json.load(file)

def write_to_json(filename, data): 
    with open(filename, "w") as file: 
        json.dump(data, file, indent=4)