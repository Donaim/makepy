
CC= gcc
CFLAGS= -Wall -O1
CL= gcc
LFLAGS= 

MAKEPY_TARGET= template.exe
BUILD=./build/


all: make_dirs $(BUILD)$(MAKEPY_TARGET)
	@ echo "all finished"

clean: 
	- rm -rf "$(BUILD)"

LIBS=
LIBS_FMT=
LINK_DEPS=$(BUILD)testproj/src/main.o $(BUILD)testproj/src/print.o $(BUILD)testproj/src/help.o

$(BUILD)$(MAKEPY_TARGET): $(LINK_DEPS) $(LIBS)
	$(CL) $(LFLAGS) -o $@    $(LINK_DEPS)   $(LIBS_FMT)

make_dirs: 
	mkdir -p '$(BUILD)testproj/src'

INCL0=  -I testproj/include1 -I testproj/include2

$(BUILD)testproj/src/main.o: testproj/src/main.c testproj/include1/hello.h testproj/outer.h testproj/src/help.h testproj/include1/bbb/kek.h
	$(CC) $(CFLAGS) -o $@ -c $< $(INCL0)

$(BUILD)testproj/src/print.o: testproj/src/print.c testproj/include1/hello.h
	$(CC) $(CFLAGS) -o $@ -c $< $(INCL0)

$(BUILD)testproj/src/help.o: testproj/src/help.c testproj/src/help.h testproj/include1/bbb/kek.h
	$(CC) $(CFLAGS) -o $@ -c $< $(INCL0)



.PHONY: clean
.PHONY: all