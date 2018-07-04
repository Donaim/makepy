
import makepy_lib as mp
import re
from os import path

include_re_m = re.compile(r'^\s*#include\s*[<"].+[>"].*$')
include_re_g = re.compile(r'[<"].+[>"]')

def is_include_statement(line: str) -> bool:
    return bool(include_re_m.match(line))
def get_filename_from_include_statement(line: str) -> str:
    return include_re_g.search(line).group(0)[1:-1]

def get_full_filename_from_include_statement(line: str, include_dirs: list):
    name = get_filename_from_include_statement(line)

    if path.isabs(name):
        if path.exists(name):
            return name
    else:
        for d in include_dirs:
            if d.is_my_rel_member(name):
                return d.get_abs_path(name)

    return None
