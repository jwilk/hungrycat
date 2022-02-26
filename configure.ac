dnl | Copyright © 2012-2022 Jakub Wilk <jwilk@jwilk.net>
dnl | SPDX-License-Identifier: MIT

AC_PREREQ([2.61])
AC_INIT([hungrycat], [0.4.2], [https://github.com/jwilk/hungrycat/issues])

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

AC_CONFIG_HEADERS([autoconf.h])
AC_CONFIG_FILES([Makefile])
AC_OUTPUT

dnl vim:ts=4 sts=4 sw=4 et
