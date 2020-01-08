#!/usr/bin/env perl

# Copyright © 2012-2020 Jakub Wilk <jwilk@jwilk.net>
# SPDX-License-Identifier: MIT

no lib '.';  # CVE-2016-1238

use autodie;
use strict;
use warnings;

use v5.14;

use File::Temp 0.23 ();
use FindBin ();
use Test::More tests => 2332;

use IPC::Run ();

my $pdir = "$FindBin::Bin/..";

sub random_string
{
    my ($len) = @_;
    my $s = '';
    for my $i (1..$len) {
        $s .= chr(rand(0x100));
    }
    return $s;
}

my $random_blob = random_string(1 << 17);

sub mkdtemp
{
    return File::Temp->newdir(
        TEMPLATE => 'hungrycat.test.XXXXXX',
        TMPDIR => 1,
    );
}

sub run_hungrycat_with_file
{
    my ($path, $options) = @_;
    my ($stdout, $stderr);
    my $proc = IPC::Run::start(
        ["$pdir/hungrycat", @{$options}, $path],
        '>', \$stdout,
        '2>', \$stderr,
    );
    $proc->finish();
    my @stderr = split /\n/, $stderr;
    my $rc = $proc->result;
    if (-f $path) {
        if ($rc == 0) {
            die "$path still exists";
        }
        unlink "$path";
    }
    return ($stdout, [@stderr], $rc);
}

sub run_hungrycat
{
    my ($data, $options) = @_;
    my $tmpdir = mkdtemp();
    my $path = "$tmpdir/file";
    open(my $fh, '>', $path);
    print {$fh} "$data";
    close($fh);
    return run_hungrycat_with_file($path, $options);
}

sub are_errors_notsup
{
    my ($errors, $fallback) = @_;
    my @errors = @{$errors};
    if (scalar @{$errors} != 2) {
        return;
    }
    my ($message_notsupp, $message_fallback) = @errors;
    my $fallback_suffix = qr/\Q; falling back to ftruncate()\E/ x $fallback;
    return (
        $message_notsupp =~ m/: Operation not supported$/ and
        $message_fallback =~ m/\b\Qfallocate() failed\E$fallback_suffix$/
    )
}

sub _test_ftruncate
{
    my ($size, $blk_size) = @_;
    my $data = substr($random_blob, 0, $size);
    my ($out, $err, $rc) = run_hungrycat($data, ['-s', $blk_size]);
    my $ctx = "ftruncate(), data-size=$size, blk-size=$blk_size";
    is_deeply($err, [], "$ctx: errors");
    is($rc, '', "$ctx: status");
    is(length $out, length $data, "$ctx: data length");
    is($out, $data, "$ctx: data");
    return;
}


sub _test_fallocate
{
    my ($size, $blk_size) = @_;
    my $data = substr($random_blob, 0, $size);
    my ($out, $err, $rc) = run_hungrycat($data, ['-s', $blk_size, '-P']);
    my $ctx = "fallocate(), data-size=$size, blk-size=$blk_size";
    if (are_errors_notsup($err, 1)) {
        ok(1, "$ctx: errors");
    } else {
        is_deeply($err, [], "$ctx: errors");
    }
    is($rc, '', "$ctx: status");
    is(length $out, length $data, "$ctx: data length");
    is($out, $data, "$ctx: data");
    return;
}

sub _test_force_fallocate
{
    my ($size, $blk_size) = @_;
    my $data = substr($random_blob, 0, $size);
    my ($out, $err, $rc) = run_hungrycat($data, ['-s', $blk_size, '-P', '-P']);
    SKIP: {
        my $ctx = "force fallocate(), data-size=$size, blk-size=$blk_size";
        if (are_errors_notsup($err, 1)) {
            skip("$ctx: fallocate() is not supported", 4);
        }
        is_deeply($err, [], "$ctx: errors");
        is($rc, '', "$ctx: status");
        is(length $out, length $data, "$ctx: data length");
        is($out, $data, "$ctx: data");
    }
    return;
}

sub test_main
{
    for my $blk_size (1..4) {
        for my $size (0..($blk_size * 7 + 2)) {
            _test_ftruncate($size, $blk_size);
            _test_fallocate($size, $blk_size);
        }
    }
    for my $blk_size (5, 10, 100, 1_000, 10_000) {
        for my $n (0..7) {
            for my $delta (-2, -1, 0, 1, 2) {
                my $size = $n * $blk_size + $delta;
                if ($size >= 0) {
                    _test_ftruncate($size, $blk_size);
                    _test_fallocate($size, $blk_size);
                    if ($blk_size >= 8192) {
                        _test_force_fallocate($size, $blk_size);
                    }
                }
            }
        }
    }
    return;
}
test_main();

sub test_sparse_fallocate
{
    my $tmpdir = mkdtemp();
    my $path = "$tmpdir/file";
    open(my $fh, '>', $path);
    my $len = 20_000;
    truncate($fh, $len);
    close($fh);
    my ($out, $err, $rc) = run_hungrycat_with_file($path, ['-P', '-P', '-s', 8192]);
    SKIP: {
        my $ctx = 'sparse fallocate';
        if (are_errors_notsup($err, 0)) {
            skip("$ctx: fallocate() is not supported", 4);
        }
        is_deeply($err, [], "$ctx: errors");
        is($rc, '', "$ctx: status");
        is(length $out, $len, "$ctx: data length");
        like($out, qr/\A\0{$len}\z/, "$ctx: data");
    }
    return;
}
test_sparse_fallocate();

# vim:ts=4 sts=4 sw=4 et
