# Copyright © 2014-2018 Jakub Wilk <jwilk@jwilk.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
