import unittest

import makepy_lib
import cppmake

cppmake.NOTIFY_ABOUT_NOT_FOUND_FILES = True

class TestCustom(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCustom, self).__init__(*args, **kwargs)

        self.idirs = [ makepy_lib.IncludeDir('testproj/include1'), makepy_lib.IncludeDir('testproj/include2') ]

    def test_makerule(self):
        r = makepy_lib.make_make_rule('test.c', ['test.h', 'string.h', 'hello.h.h'], ['$(CC) -c $@', '@ echo compiled $@'])
        print('\n\n', r, '\n')

    def test_include(self):
        re1 = cppmake.is_include_statement('   #include <hello.h>   //some comment')
        self.assertEqual(re1, True)

        re2 = cppmake.is_include_statement('#include"hello.h"')
        self.assertEqual(re2, True)
        
        re3 = cppmake.is_include_statement('#include hello.h')
        self.assertEqual(re3, False)

    def test_get_include_file(self):
        re1 = cppmake.get_filename_from_include_statement('   #include <hello.h>   //some comment')
        self.assertEqual('hello.h', re1)
        
        re2 = cppmake.get_filename_from_include_statement('#include"hello.h"')
        self.assertEqual('hello.h', re2)

    def test_get_full_name(self):
        re1 = cppmake.IncludeFile.from_include_statement('   #include <hello.h>   //some comment', self.idirs)
        self.assertEqual('testproj/include1/hello.h', re1.abs_path)
        
        re2 = cppmake.IncludeFile.from_include_statement('   #include <bbb/kek.h>   //some comment', self.idirs)
        self.assertEqual('testproj/include1/bbb/kek.h', re2.abs_path)
        
        re3 = cppmake.IncludeFile.from_include_statement('   #include <hehe.h>   //some comment', self.idirs)
        self.assertEqual('testproj/include2/hehe.h', re3.abs_path)

        re4 = cppmake.IncludeFile.from_include_statement('   #include <../outer.h>   //some comment', self.idirs)
        self.assertEqual('testproj/outer.h', re4.abs_path)

    def test_scan_file_names(self):
        names = cppmake.scan_file_include_statements('testproj/src/main.c')
        names = list(names)
        print(names)
    def test_scan_file_includes(self):
        files = cppmake.scan_file_include_files('testproj/src/main.c', self.idirs)
        print( list( map( lambda f: f.abs_path, files ) ) )

    def test_get_file_makerule(self):
        file = cppmake.IncludeFile('testproj/src/main.c', 'testproj/src/main.c', makepy_lib.IncludeDir('testproj/src'))
        deps = list(cppmake.get_all_dependencies(file, self.idirs))

        names = list ( map( lambda f: f.abs_path , deps ) )
        # print(names)

        make_names = cppmake.get_all_make_dependencies(file, self.idirs)

        r = makepy_lib.make_make_rule(file.abs_path.replace('.c', '.o'), make_names, ["echo kek"])
        print(r)

    def test_generate_makefile(self):
        mgr = cppmake.CppGenerator()

        dir_params = [ makepy_lib.DirParams('testproj/src', self.idirs) ]
        r = mgr.generate_make_by_params('testproj/template.mk', dir_params)

        print(r)

    def test_write_makefile(self):
        mgr = cppmake.CppGenerator()

        # dir_params = [ makepy_lib.DirParams('testproj/src', self.idirs) ]
        # mgr.generate_make_to('testproj/template.mk', './Makefile', dir_params)
        mgr.generate_make_to_with_same_include_dirs('testproj/template.mk', './Makefile', ['testproj/src'], self.idirs)

