=========
hungrycat
=========

cat & rm in a single tool
=========================

:Date: 2013-01-26
:Manual section: 1

Synoposis
---------

**hungrycat** [-f] [-P] [-s *BLOCK_SIZE*] *FILE*...

Description
-----------
**hungrycat** is a tool that prints contents of a file on the standard output,
while simultaneously freeing disk space occupied by the file.

It can be useful if you need to process a large file, but:

- you don't have enough space to store the output file and
- you wouldn't need the input file afterwards.

Options
-------

-f               Force processing even if the file has multiple links.

-P               Use **fallocate**\(2) with FALLOC_FL_PUNCH_HOLE, instead of
                 shuffling the file contents and using **ftruncate**\(2). This
                 might ease file recovery if the program was interrupted in the
                 middle of processing.

                 If the **fallocate**\(2) system call is not supported by the
                 underlying filesystem the program will fall back to the
                 “classic” implementation. You can disable the fall-back
                 behavior by specifying the option twice.

-s BLOCK_SIZE    Set block size to *BLOCK_SIZE*.
                 The default is the filesystem block size.

See also
--------
**cat**\(1), **rm**\(1), **truncate**\(1)
