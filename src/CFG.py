from json_funcs import *
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILENAME = os.path.join(SCRIPT_DIR, "semantically-analyzed.txt")
OUTPUT_FILENAME = os.path.join(SCRIPT_DIR, "cfg.txt")

annotated_ast = read_from_json(INPUT_FILENAME)
cfg = []

def new_block(): 
    block = {
        "statements": [],
        "symbol_table": [],
        "successors": [],
        "predeccessors": []
    }
    cfg.append(block)
    return block

