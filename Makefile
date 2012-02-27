CFLAGS = -std=c99 -O2 -g -Wall

.PHONY: all
all: hungrycat

.PHONY: test
test: hungrycat
	python tests.py

.PHONY: doc
doc: doc/manpage.1

.PHONY: clean
clean:
	rm -f hungrycat hungrycat.o

.PHONY: distclean
distclean:
	rm -f config.log config.status config.h

hungrycat: hungrycat.o
hungrycat.o: hungrycat.c config.h

%.1: %.rst
	rst2man $(<) $(@)

# vim:ts=4 sw=4 noet
