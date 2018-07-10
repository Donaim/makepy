
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

$(BUILD)$(MAKEPY_TARGET): $(BUILD)testproj/src/main.o $(BUILD)testproj/src/print.o
	$(CL) $(LFLAGS) -o $@    $^

make_dirs: 
	mkdir -p '$(BUILD)testproj/src'

INCL0=  -I testproj/include1 -I testproj/include2 -I testproj/src

$(BUILD)testproj/src/main.o: testproj/src/main.c testproj/include1/hello.h testproj/outer.h testproj/src/help.h testproj/include1/bbb/kek.h
	$(CC) $(CFLAGS) -o $@ -c $< $(INCL0)

$(BUILD)testproj/src/print.o: testproj/src/print.c testproj/include1/hello.h
	$(CC) $(CFLAGS) -o $@ -c $< $(INCL0)



.PHONY: clean
.PHONY: all