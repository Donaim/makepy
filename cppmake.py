
import makepy_lib as mp
import re
from os import path

include_re_m = re.compile(r'^\s*#include\s*[<"].+[>"].*$')
include_re_g = re.compile(r'[<"].+[>"]')

class IncludeFile:
    def __init__(self, rel_path: str, abs_path: str, include_dir: mp.IncludeDir):
        self.rel_path = rel_path
        self.abs_path = abs_path
        self.include_dir = include_dir
        
        if self.abs_path is None:
            self.type = 'implicit'      # not found or precompiled (like <stdio.h>, <stdlib.h>, ...)
        elif self.include_dir is None:
            self.type = 'abs'
        else:
            self.type = 'rel'

        self.dependencies = None

    def collect_dependencies(self, include_dirs: list) -> None:
        if not self.dependencies is None: return
        if self.type == 'implicit': 
            self.dependencies = []
            return
        self.dependencies = scan_file_include_files(self.abs_path, include_dirs)        

    @staticmethod
    def from_include_statement(line: str, include_dirs: list):
        name = get_filename_from_include_statement(line)
        return IncludeFile.from_filename(name, include_dirs)
    @staticmethod
    def from_filename(name, include_dirs: list):
        if path.isabs(name):
            if path.exists(name):
                return IncludeFile(name, name, None)
        else:
            for d in include_dirs:
                if d.is_my_rel_member(name):
                    abs_path = d.get_abs_path(name)
                    return IncludeFile(name, abs_path, d)

        return IncludeFile(name, None, None)

def is_include_statement(line: str) -> bool:
    return bool(include_re_m.match(line))
def get_filename_from_include_statement(line: str) -> str:
    return include_re_g.search(line).group(0)[1:-1]

def scan_text_include_names(text: str) -> iter:
    for line in text.split('\n'):
        if is_include_statement(line):
            yield get_filename_from_include_statement(line)

def scan_file_include_names(filepath: str) -> iter:
    with open(filepath) as r:
        text = r.read()
        return scan_text_include_names(text)

def scan_file_include_files(filepath: str, include_dirs: list) -> list:
    names = scan_file_include_names(filepath)
    files = map( lambda name: IncludeFile.from_filename(name, include_dirs), names )
    return list(files)

def get_all_dependencies(include_file: IncludeFile, include_dirs: list) -> iter:
    include_file.collect_dependencies(include_dirs)
    for d in include_file.dependencies:
        yield d
        for DD in get_all_dependencies(d, include_dirs):
            yield DD
def get_all_make_dependencies(include_file: IncludeFile, include_dirs: list) -> list:
    return list( map( lambda d: d.abs_path, filter( lambda d: not d.abs_path is None, get_all_dependencies(include_file, include_dirs) ) ) )
