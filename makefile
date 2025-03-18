exec = fpp.out
sources = $(wildcard D:/projects/Fpp2/*.c)
objects = $(sources:.c=.o)
flags = -g


$(exec): $(objects)
	gcc $(objects) $(flags) -o $(exec)

%.o: %.c include/%.h
	gcc -c $(flags) $< -o $@

install:
	make
	cp ./fpp.out /usr/local/bin/hello

clean:
	-rm *.out
	-rm *.o