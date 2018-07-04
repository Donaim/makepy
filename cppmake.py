
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
    yield include_file
    for d in include_file.dependencies:
        for DD in get_all_dependencies(d, include_dirs):
            yield DD
def get_all_make_dependencies(include_file: IncludeFile, include_dirs: list) -> list:
    return list( map( lambda d: d.abs_path, filter( lambda d: not d.abs_path is None, get_all_dependencies(include_file, include_dirs) ) ) )


class CppManager(mp.Manager):

    def filter_rule(self, filename: str) -> bool:
        return filename.endswith('.c') or filename.endswith('.cpp')

    CPPMAKEPY_COMPILE_COMMAND_RE = re.compile(r'^#+\s*MAKEPY_CPP_COMPILE_COMMAND:?\s*$')
    CPPMAKEPY_LINK_COMMAND_RE = re.compile(r'^#+\s*CPPMAKEPY_LINK_COMMAND:?\s*$')
    def get_command(self, text: str, reg):
        ret = []
        mode = True
        for line in text.split('\n'):
            if mode:
                if reg.match(line):
                    mode = False
            else:
                if line.startswith('# '):
                    ret.append(line[2:])
                else:
                    return ret
        raise Exception('{} not found in template'.format(reg))

    def generate_make(self, template: str, inited_dirs: list) -> str:
        CPPMAKEPY_COMPILE_COMMAND = self.get_command(template, CppManager.CPPMAKEPY_COMPILE_COMMAND_RE)
        CPPMAKEPY_LINK_COMMAND    = self.get_command(template, CppManager.CPPMAKEPY_LINK_COMMAND_RE)

        main_targets = '\n\n'

        all_files = []
        for d in inited_dirs:
            for f in d.files:
                all_files.append(f)
        link_deps = map( lambda f: f.replace('.c', '.o'), all_files)
        main_targets += mp.make_make_rule("$(MAKEPY_TARGET)", link_deps, CPPMAKEPY_LINK_COMMAND)
        main_targets += '\n\n'

        for d in inited_dirs:
            for f in d.files:
                ff = IncludeFile(f, f, None)
                deps = get_all_make_dependencies(ff, d.params.include_dirs)
                
                target = f.replace('.c', '.o')
                main_targets += mp.make_make_rule(target, deps, CPPMAKEPY_COMPILE_COMMAND)
                main_targets += '\n\n'

        return template + main_targets


