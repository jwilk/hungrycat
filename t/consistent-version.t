#!/usr/bin/env perl

# Copyright © 2017-2020 Jakub Wilk <jwilk@jwilk.net>
# SPDX-License-Identifier: MIT

no lib '.';  # CVE-2016-1238

use autodie;
use strict;
use warnings;

use v5.14;

use FindBin ();
use Test::More tests => 2;

my $pdir = "$FindBin::Bin/..";

my $path = "$pdir/doc/changelog";
open(my $fh, '<', $path);
my $line = <$fh>;
close($fh);
my ($changelog_version) = $line =~ m/[(]([\d.]+)[)]/a;
my $configure_ac_version = 'NONE';
$path = "$pdir/configure.ac";
open($fh, '<', $path);
while (<$fh>) {
    if (/^AC_INIT[(].*\[([\d.]+)\]/a) {
        $configure_ac_version = $1;
        last;
    }
}
close($fh);
is($configure_ac_version, $changelog_version, 'configure.ac version == changelog version');
my $manpage_version = 'NONE';
$path = "$pdir/doc/manpage.rst";
open($fh, '<', $path);
while (<$fh>) {
    if (/^:version: \S+ ([\d.]+)$/a) {
        $manpage_version = $1;
        last;
    }
}
close($fh);
is($manpage_version, $changelog_version, 'manpage version == changelog version')

# vim:ts=4 sts=4 sw=4 et
