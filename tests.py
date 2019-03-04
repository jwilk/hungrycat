# encoding=UTF-8

# Copyright © 2012-2018 Jakub Wilk <jwilk@jwilk.net>
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

import contextlib
import io
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

import nose
from nose.tools import (
    assert_equal,
    assert_false,
)

b = b''  # Python >= 2.6 is required

if sys.version_info >= (3,):
    def random_string(size):
        return bytes(
            random.randint(0, 0xFF)
            for i in range(0, size)
        )
else:
    range = xrange  # pylint: disable=undefined-variable
    def random_string(size):
        return ''.join(
            chr(random.randint(0, 0xFF))
            for i in range(0, size)
        )

random_blob = random_string(1 << 17)

@contextlib.contextmanager
def mktemp():
    tmpdir = tempfile.mkdtemp(prefix='hungrycat.', suffix='.tmp')
    try:
        yield tmpdir + '/file'
    finally:
        shutil.rmtree(tmpdir)

def run_hungrycat_with_file(options, path):
    child = subprocess.Popen(
        ['./hungrycat'] + [str(o) for o in options] + [path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (output, errors) = child.communicate()
    errors = errors.splitlines()
    rc = child.wait()
    if rc == 0:
        assert_false(os.path.exists(path))
    elif os.path.exists(path):
        os.unlink(path)
    return output, errors, rc

def run_hungrycat(options, data):
    with mktemp() as path:
        with open(path, 'wb') as fp:
            fp.write(data)
        return run_hungrycat_with_file(options, path)

def _standard_test_ftruncate(size, block_size):
    data = random_blob[:size]
    output, errors, rc = run_hungrycat(['-s', block_size], data)
    assert_equal(len(output), len(data))
    assert_equal(errors, [])
    assert_equal(rc, 0)
    assert_equal(output, data)

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
    data = random_blob[:size]
    output, errors, rc = run_hungrycat(['-s', block_size, '-P'], data)
    if _errors_operation_not_supported(errors, fallback=True):
        pass
    else:
        assert_equal(errors, [])
    assert_equal(rc, 0)
    assert_equal(output, data)

def _standard_test_force_fallocate(size, block_size):
    data = random_blob[:size]
    output, errors, rc = run_hungrycat(['-s', block_size, '-P', '-P'], data)
    if _errors_operation_not_supported(errors, fallback=False):
        raise nose.SkipTest
    else:
        assert_equal(errors, [])
    assert_equal(rc, 0)
    assert_equal(output, data)

def _standard_test(testfn, min_block_size=1):
    for block_size in range(1, 5):
        if block_size < min_block_size:
            continue
        for size in range(0, block_size * 7 + 3):
            yield testfn, size, block_size
    for block_size in 5, 10, 100, 1000, 10000:
        if block_size < min_block_size:
            continue
        for n in range(0, 8):
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

def test_sparse_fallocate():
    with mktemp() as path:
        with open(path, 'wb') as fp:
            fp.truncate(20000)
        output, errors, rc = run_hungrycat_with_file(['-P', '-P', '-s', 8192], path)
        if _errors_operation_not_supported(errors, fallback=False):
            raise nose.SkipTest
        assert_equal(errors, [])
        assert_equal(rc, 0)
        assert_equal(output, b'\0' * 20000)

here = os.path.dirname(__file__)

def test_versions():
    path = os.path.join(here, 'doc', 'changelog')
    with io.open(path, 'rt', encoding='UTF-8') as file:
        line = file.readline()
    changelog_version = line.split()[1].strip('()')
    configure_ac_version = None
    path = os.path.join(here, 'configure.ac')
    with io.open(path, 'rt', encoding='UTF-8') as file:
        for line in file:
            match = re.match(r'^AC_INIT[(].*\[([0-9.]+)\]', line)
            if match is not None:
                configure_ac_version = match.group(1)
                break
    assert_equal(configure_ac_version, changelog_version)
    manpage_version = None
    path = os.path.join(here, 'doc', 'manpage.rst')
    with io.open(path, 'rt', encoding='UTF-8') as file:
        for line in file:
            match = re.match(r'^:version: \S+ ([0-9.]+)$', line)
            if match is not None:
                manpage_version = match.group(1)
                break
    assert_equal(manpage_version, changelog_version)

if __name__ == '__main__':
    nose.main()

# vim:ts=4 sts=4 sw=4 et
