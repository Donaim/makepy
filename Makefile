
CC= gcc
CFLAGS= -Wall -O1
CL= gcc
LFLAGS= 

MAKEPY_TARGET= template.exe




$(MAKEPY_TARGET): testproj/src/main.o testproj/src/print.o
	$(CL) $(LFLAGS) -o $@    $^

INCL0=  -I testproj/include1 -I testproj/include2 -I testproj/src

testproj/src/main.o: testproj/src/main.c testproj/include1/hello.h testproj/outer.h testproj/src/help.h testproj/include1/bbb/kek.h
	$(CC) $(CFLAGS) -o $@ -c $< $(INCL0)

testproj/src/print.o: testproj/src/print.c testproj/include1/hello.h
	$(CC) $(CFLAGS) -o $@ -c $< $(INCL0)

