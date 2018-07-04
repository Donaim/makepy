import os, sys
from os import path

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

