import os, sys
from os import path

import abc

class DirParams:
    def __init__(self, dirpath: str, include_dirs: list):
        self.dirpath = dirpath
        self.include_dirs = include_dirs
    def create_with_same_include_dirs(dirpaths: list, include_dirs: list) -> list:
        return list( map( lambda d: DirParams(d, include_dirs), dirpaths ) )

class InitedDir:
    def __init__(self, params: DirParams, filter_rule):
        self.params = params
        self.files = dir_get_some_files(self.params.dirpath, filter_rule)

class Manager(abc.ABC):

    def generate_make_to(self, template_filepath: str, output_filepath: str, dir_params: list) -> None:
        with open(output_filepath, 'w+') as w:
            text = self.generate_make_by_params(template_filepath, dir_params)
            w.write(text)

    def generate_make_by_params(self, template_filepath: str, dir_params: list) -> str:
        def rule(filename): return self.filter_rule(filename)

        inited_dirs = list( map( lambda p: InitedDir(p, rule), dir_params ) )
        with open(template_filepath, 'r') as tf:
            template = tf.read()
            return self.generate_make(template, inited_dirs)
    
    @abc.abstractmethod
    def filter_rule(self, filename: str) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def generate_make(self, template: str, inited_dirs: list) -> str:
        raise NotImplementedError()

class IncludeDir:
    def __init__(self, dirpath):
        self.dirpath = dirpath
    
    def get_abs_path(self, file_relpath: str) -> str:
        file_abspath = path.join(self.dirpath, file_relpath)
        file_abspath = path.normpath(file_abspath)
        return file_abspath
    
    def is_my_rel_member(self, file_relpath: str) -> bool:
        file_abspath = self.get_abs_path(file_relpath)
        return path.exists(file_abspath)

def dir_get_all_files(dirpath: str):
    return [path.join(dp, f) for dp, dn, fn in os.walk(dirpath) for f in fn]
def dir_get_some_files(dirpath: str, rule):
    all = dir_get_all_files(dirpath)
    return list( filter( lambda f: rule(f), all ) )

def extension_rule(f: str, allowed_exts: str) -> bool:
    if allowed_exts is None: return True
    ext = f.split(path.extsep)[-1]
    return ext in allowed_exts
def dir_get_files_with_exts(dirpath: str, exts: list) -> list:
    def rule(f): return extension_rule(f, exts)
    return dir_get_some_files(dirpath, rule)

def make_make_rule(target: str, dependencies: list, commands: list) -> str:
    re = target + ':'
    for d in dependencies:
        re += ' ' + d

    for c in commands:
        re += '\n\t' + c

    return re

