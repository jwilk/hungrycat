dnl | Copyright © 2012-2018 Jakub Wilk <jwilk@jwilk.net>
dnl |
dnl | Permission is hereby granted, free of charge, to any person obtaining a
dnl | copy of this software and associated documentation files (the
dnl | “Software”), to deal in the Software without restriction, including
dnl | without limitation the rights to use, copy, modify, merge, publish,
dnl | distribute, sublicense, and/or sell copies of the Software, and to
dnl | permit persons to whom the Software is furnished to do so, subject to
dnl | the following conditions:
dnl |
dnl | The above copyright notice and this permission notice shall be included
dnl | in all copies or substantial portions of the Software.
dnl |
dnl | THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
dnl | OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
dnl | MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
dnl | IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
dnl | CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
dnl | TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
dnl | SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

AC_PREREQ([2.61])
AC_INIT([hungrycat], [0.4.2], [https://github.com/jwilk/hungrycat/issues])

AC_PROG_CC_C99
AC_PROG_CPP

AC_MSG_CHECKING([for FALLOC_FL_PUNCH_HOLE])
AC_PREPROC_IFELSE([AC_LANG_SOURCE([[
        #define _GNU_SOURCE 1
        #include <linux/falloc.h>
        #ifndef FALLOC_FL_PUNCH_HOLE
        #error FALLOC_FL_PUNCH_HOLE is missing
        #endif
    ]])], [
        AC_MSG_RESULT([yes])
        AC_DEFINE([HAVE_FALLOC_FL_PUNCH_HOLE], [1], [Define if FALLOC_FL_PUNCH_HOLE is available.])
        AC_DEFINE([_GNU_SOURCE], [1], [Define to enable GNU extensions on systems that have them.])
    ], [
        AC_MSG_RESULT([no])
        AC_DEFINE([_XOPEN_SOURCE], [500], [Define to the level of X/Open that your system supports.])
    ]
)

AC_SYS_LARGEFILE

AC_CONFIG_HEADER([autoconf.h])
AC_CONFIG_FILES([Makefile])
AC_OUTPUT

dnl vim:ts=4 sts=4 sw=4 et
