CFLAGS = -std=c99 -O2 -g -Wall

.PHONY: all
all: hungrycat

.PHONY: test
test: hungrycat
	./run-tests $(test_args)

.PHONY: clean
clean:
	$(RM) hungrycat hungrycat.o

hungrycat: hungrycat.o
hungrycat.o: hungrycat.c config.h

# vim:ts=4 sw=4 noet
