
CFLAGS= -Wall -O1

CC= g++

MAKEPY_TARGET= template.exe




$(MAKEPY_TARGET): testproj/src/main.o testproj/src/print.o
	@ echo linking $@ $^

testproj/src/main.o: testproj/src/main.c testproj/include1/hello.h testproj/outer.h testproj/src/help.h testproj/include1/bbb/kek.h
	@ echo compile
	@ echo $@ $^

testproj/src/print.o: testproj/src/print.c testproj/include1/hello.h
	@ echo compile
	@ echo $@ $^

