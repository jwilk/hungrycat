CFLAGS = -std=c99 -O2 -g -Wall

.PHONY: all
all: hungrycat

.PHONY: test
test: hungrycat
	./run-tests $(test_args)

.PHONY: clean
clean:
	rm -f hungrycat hungrycat.o

.PHONY: distclean
distclean:
	rm -f config.log config.status config.h

hungrycat: hungrycat.o
hungrycat.o: hungrycat.c config.h

# vim:ts=4 sw=4 noet
