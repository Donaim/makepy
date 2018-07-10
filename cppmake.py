
import makepy_lib as mp
import re
from os import path
from functools import *

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


class CppGenerator(mp.Generator):

    def __init__(self):
        self.compile_commands = ['$(CC) $(CFLAGS) -o $@ -c $<']
        self.link_commands =    ['$(CL) $(LFLAGS) -o $@    $(LINK_DEPS)   $(LIBS_FMT)']
        self.targets_prefix = '$(BUILD)'
        self.libs = []

    allowed_exts = ['.c', '.cpp', '.cxx', '.cc', '.c++']
    def filter_rule(self, filename: str) -> bool:
        return any( map( lambda ext: filename.endswith(ext), CppGenerator.allowed_exts ) )

    def __get_o_target(self, source_file: str) -> str:
        target, _ = path.splitext(source_file)
        target = target + '.o'
        target = self.targets_prefix + target
        return target
    def get_all_part(self, link_target: str) -> str:
        return mp.make_make_rule('all', ['make_dirs', link_target], ['@ echo "all finished"'])
    def get_clean_part(self):
        return mp.make_make_rule('clean', [''], ['- rm -rf "{}"'.format(self.targets_prefix)])
    def get_phony_part(self):
        return '\n'.join( ['.PHONY: clean', '.PHONY: all'] )
    def get_link_part(self, link_target: str, inited_dirs: list) -> str:
        re = ''
        
        re += 'LIBS=' + ' '.join(self.libs) + '\n'
        re += 'LIBS_FMT=' + ' -L '.join([''] + self.libs) + '\n\n'
        
        all_files = reduce(lambda acc, d: acc + d.files, inited_dirs, [])
        link_deps = list(map( self.__get_o_target, all_files))
        re += 'LINK_DEPS=' + ' '.join(link_deps) + '\n'
        re += mp.make_make_rule( link_target, ['$(LINK_DEPS)', '$(LIBS)'], self.link_commands)
        
        return re
    def get_compile_part(self, inited_dirs: list) -> str:
        compile_targets = ''
        make_dirs_list = set()

        for i, d in enumerate(inited_dirs):

            inclname = 'INCL' + str(i)
            incl = inclname + '= ' + reduce(lambda a, b: a + ' -I ' + b.dirpath, d.params.include_dirs, '')
            compile_targets += incl + '\n\n'
            
            ccommands = self.compile_commands
            ccommands[0] = ccommands[0] + ' $({})'.format(inclname)

            for f in d.files:
                ff = IncludeFile(f, f, None)
                deps = get_all_make_dependencies(ff, d.params.include_dirs)
                
                target = self.__get_o_target(f)
                target_dir = path.dirname(target)
                make_dirs_list.add(target_dir)
                
                compile_targets += mp.make_make_rule(target, deps, self.compile_commands)
                compile_targets += '\n\n'
        
        make_dirs_list_str = ' '.join(map(lambda x: "'" + x + "'", make_dirs_list ))
        makedirs_part = mp.make_make_rule('make_dirs', [''], ['mkdir -p {}'.format(make_dirs_list_str)])
        
        return makedirs_part + '\n\n' + compile_targets

    def generate_make_to_with_same_include_dirs(self, template_filepath: str, output_filepath: str, dirpaths: list, include_dirs: list) -> str:
        return self.generate_make_to(
            template_filepath=template_filepath,
            output_filepath=output_filepath,
            dir_params= mp.DirParams.create_with_same_include_dirs(dirpaths=dirpaths, include_dirs=include_dirs))
    def generate_make(self, template: str, inited_dirs: list) -> str:
        link_target = self.targets_prefix + '$(MAKEPY_TARGET)'

        all_part = self.get_all_part(link_target)
        link_part = self.get_link_part(link_target, inited_dirs)
        clean_part = self.get_clean_part()
        compile_part = self.get_compile_part(inited_dirs)
        phony_part = self.get_phony_part()

        return '\n\n'.join( [template, all_part, clean_part, link_part, compile_part, phony_part] )


