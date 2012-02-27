#!/usr/bin/python
# encoding=UTF-8

# Copyright © 2012 Jakub Wilk <jwilk@jwilk.net>
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

import os
import random
import subprocess as ipc
import tempfile

import nose
from nose.tools import *

def random_string(size):
    return ''.join(
        chr(random.randint(0, 0xff))
        for i in xrange(0, size)
    )

random_blob = random_string(1 << 17)

def mkstemp():
    return tempfile.mkstemp(prefix='hungrycat.', suffix='.tmp')

def run_hungrycat_with_file(options, input_file):
    child = ipc.Popen(
        ['./hungrycat'] + map(str, options) + [input_file],
        stdout=ipc.PIPE,
        stderr=ipc.PIPE,
    )
    output = child.stdout.read()
    errors = child.stderr.read().splitlines()
    rc = child.wait()
    if rc == 0:
        assert_false(os.path.exists(input_file))
    else:
        if os.path.exists(input_file):
            os.unlink(input_file)
    return output, errors, rc

def run_hungrycat(options, input_):
    fd, input_file = mkstemp()
    os.write(fd, input_)
    os.close(fd)
    return run_hungrycat_with_file(options, input_file)

def _standard_test_ftruncate(size, block_size):
    input_ = random_blob[:size]
    output, errors, rc = run_hungrycat(['-s', block_size], input_)
    assert_equal(len(output), len(input_))
    assert_equal(errors, [])
    assert_equal(rc, 0)
    assert_equal(output, input_)

def _errors_buffer_to_small(errors):
    try:
        [message] = errors
    except ValueError:
        return
    return message.endswith(': buffer size too small for fallocate(); falling back to ftruncate()')

def _errors_operation_not_supported(errors, fallback):
    try:
        message_notsupp, message_fallback = errors
    except ValueError:
        return
    return (
        message_notsupp.endswith(': Operation not supported') and
        message_fallback.endswith('fallocate() failed' + ('; falling back to ftruncate()' if fallback else ''))
    )

def _standard_test_fallocate(size, block_size):
    input_ = random_blob[:size]
    output, errors, rc = run_hungrycat(['-s', block_size, '-P'], input_)
    if _errors_buffer_to_small(errors):
        pass
    elif _errors_operation_not_supported(errors, fallback=True):
        pass
    else:
        assert_equal(errors, [])
    assert_equal(rc, 0)
    assert_equal(output, input_)

def _standard_test_force_fallocate(size, block_size):
    input_ = random_blob[:size]
    output, errors, rc = run_hungrycat(['-s', block_size, '-P', '-P'], input_)
    if _errors_buffer_to_small(errors):
        raise nose.SkipTest
    elif _errors_operation_not_supported(errors, fallback=False):
        raise nose.SkipTest
    else:
        assert_equal(errors, [])
    assert_equal(rc, 0)
    assert_equal(output, input_)

def _standard_test(testfn, min_block_size=1):
    for block_size in xrange(1, 5):
        if block_size < min_block_size:
            continue
        for size in xrange(0, block_size * 7 + 3):
            yield testfn, size, block_size
    for block_size in 5, 10, 100, 1000, 10000:
        if block_size < min_block_size:
            continue
        for n in xrange(0, 8):
            for delta in -2, -1, 0, 1, 2:
                size = n * block_size + delta
                if size >= 0:
                    yield testfn, size, block_size

def test_standard_ftruncate():
    for item in _standard_test(_standard_test_ftruncate):
        yield item

def test_standard_fallocate():
    for item in _standard_test(_standard_test_fallocate):
        yield item

def test_standard_force_fallocate():
    for item in _standard_test(_standard_test_force_fallocate, min_block_size=8192):
        yield item

if __name__ == '__main__':
    nose.main()

# vim:ts=4 sw=4 et
