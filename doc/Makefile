# Copyright © 2014-2018 Jakub Wilk <jwilk@jwilk.net>
# SPDX-License-Identifier: MIT

export LC_ALL=C

rst2man = $(notdir $(shell command -v rst2man || echo rst2man.py))
exe = hungrycat

.PHONY: all
all: $(exe).1

$(exe).1: manpage.rst
	$(rst2man) --input-encoding=UTF-8 < $(<) > $(@).tmp
	perl -pi -e 's/([a-z])\\[(]aq([a-z])/$$1\x27$$2/g' $(@).tmp  # prefer ' to \(aq when used as an apostrophe
	perl -ni -e 'print unless $$. > 1 and /^[.]\\"/' $(@).tmp
	mv $(@).tmp $(@)

.PHONY: clean
clean:
	rm -f $(exe).1 *.tmp

.error = GNU make is required

# vim:ts=4 sts=4 sw=4 noet
