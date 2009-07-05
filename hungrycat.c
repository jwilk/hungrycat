/* Copyright © 2009 Jakub Wilk
 *
 * This package is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 2 dated June, 1991.
 */

#define _FILE_OFFSET_BITS 64
#define _XOPEN_SOURCE 500

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

static void *buffer;
static size_t block_size = BUFSIZ;
static const char *argv0;
static int opt_force = 0;

static void show_usage()
{
  fprintf(stderr, "Usage: %s [-f] [-s BLOCK_SIZE] FILE...\n\n", argv0);
  return;
}

static void show_error(const char *context)
{
  fprintf(stderr, "hungrycat: ");
  perror(context);
}

static int eat(const char *filename)
{

#define fail_if(cond) \
  while (cond) \
  { \
    show_error(filename); \
    if (fd != -1) \
      close(fd); \
    return -1; \
  }

  const int fd = open(filename, O_RDWR);
  fail_if(fd == -1);
  const off_t file_size = lseek(fd, 0, SEEK_END);
  fail_if(file_size == -1);
  const off_t n_blocks = (file_size + block_size - 1) / block_size;

  int rc;
  off_t offset;
  ssize_t r_bytes, w_bytes;

  offset = lseek(fd, 0, SEEK_SET);
  fail_if(offset == -1);

  while (n_blocks <= 2)
  {
    r_bytes = read(fd, buffer, block_size);
    fail_if(r_bytes == -1);
    if (r_bytes == 0)
      goto done;
    w_bytes = write(STDOUT_FILENO, buffer, r_bytes);
    fail_if(w_bytes == -1);
  }

  struct stat stat;
  fstat(fd, &stat);
  if (stat.st_nlink > 1 && !opt_force)
  {
    errno = EMLINK;
    fail_if(1);
  }

  for (off_t i = 0; i < n_blocks / 2; i++)
  {
    r_bytes = read(fd, buffer, block_size);
    fail_if(r_bytes != block_size);
    w_bytes = write(STDOUT_FILENO, buffer, block_size);
    fail_if(r_bytes != block_size);
    offset = (n_blocks - i - 1) * block_size;
    r_bytes = pread(fd, buffer, offset, (n_blocks - i - 1) * block_size);
    fail_if(r_bytes == -1);
    w_bytes = pwrite(fd, buffer, r_bytes, i * block_size);
    fail_if(r_bytes != w_bytes);
    rc = ftruncate(fd, offset);
    fail_if(rc == -1);
  }

  if (n_blocks & 1 == 1)
  {
    r_bytes = read(fd, buffer, block_size);
    fail_if(r_bytes != block_size);
    w_bytes = write(STDOUT_FILENO, buffer, block_size);
    fail_if(r_bytes != block_size);
    rc = ftruncate(fd, (n_blocks / 2) * block_size);
    fail_if(rc == -1);
  }

  for (off_t i = (n_blocks / 2) - 1; i > 0; i--)
  {
    r_bytes = pread(fd, buffer, block_size, i * block_size);
    fail_if(r_bytes != block_size);
    w_bytes = write(STDOUT_FILENO, buffer, block_size);
    fail_if(w_bytes != block_size);
    rc = ftruncate(fd, i * block_size);
    fail_if(rc == -1);
  }

  if (n_blocks > 0)
  {
    r_bytes = pread(fd, buffer, 1 + (file_size - 1) % block_size, 0);
    fail_if(r_bytes == -1);
    w_bytes = write(STDOUT_FILENO, buffer, r_bytes);
    fail_if(w_bytes != r_bytes);
  }

done:
  rc = unlink(filename);
  fail_if(rc == -1);
  rc = close(fd);
  fail_if(rc == -1);
  return 0;

#undef fail_if

}

int main(int argc, char **argv)
{
  argv0 = argv[0];

  char opt;
  while ((opt = getopt(argc, argv, "fs:")) != -1)
  {
    switch (opt)
    {
      case 'f':
        opt_force = 1;
        break;
      case 's':
      {
        char *endptr;
        unsigned long value;
        errno = 0;
        value = strtoul(optarg, &endptr, 10);
        if (errno != 0)
          ;
        else if (endptr == optarg || *endptr != '\0')
          errno = EINVAL;
        else if (value == 0 || value > SIZE_MAX)
          errno = ERANGE;
        if (errno != 0)
        {
          show_error(NULL);
          show_usage();
          return EXIT_FAILURE;
        }
        block_size = value;
        break;
      }
      default:
        show_usage();
        return EXIT_FAILURE;
    }
  }
  if (optind >= argc)
  {
    show_usage();
    return EXIT_FAILURE;
  }
  buffer = malloc(block_size);
  if (buffer == NULL)
  {
    show_error(NULL);
    return 1;
  }

  int rc = 0;
  while (optind < argc)
  {
    rc |= eat(argv[optind]);
    optind++;
  }
  return rc == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}

/* vim:set ts=2 sw=2 et:*/
