import unittest

import makepy_lib
import cppmake

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
        re1 = cppmake.get_full_filename_from_include_statement('   #include <hello.h>   //some comment', self.idirs)
        self.assertEqual('testproj/include1/hello.h', re1)
        
        re2 = cppmake.get_full_filename_from_include_statement('   #include <bbb/kek.h>   //some comment', self.idirs)
        self.assertEqual('testproj/include1/bbb/kek.h', re2)
        
        re2 = cppmake.get_full_filename_from_include_statement('   #include <hehe.h>   //some comment', self.idirs)
        self.assertEqual('testproj/include2/hehe.h', re2)

        re2 = cppmake.get_full_filename_from_include_statement('   #include <../outer.h>   //some comment', self.idirs)
        self.assertEqual('testproj/outer.h', re2)


