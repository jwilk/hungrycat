CFLAGS = -std=c99 -O2 -g -Wall

.PHONY: all
all: hungrycat

.PHONY: test
test: hungrycat
	./run-tests

.PHONY: clean
clean:
	$(RM) hungrycat hungrycat.o

hungrycat: hungrycat.o

# vim:ts=4 sw=4 noet
