#!/usr/bin/env python

# Joe Gillotti - 7/25/2017
# Because https://github.com/dnbert/prm has unresolved issues and I wanted
# something lean and fast.

import os
import gzip
import argparse
import shutil
import hashlib
import sys
from email.Utils import formatdate

try:
    from apt.debfile import DebPackage
except ImportError:
    print 'Please run apt-get install python-apt (or run this outside of a venv)'
    sys.exit(1)

subpath_format = 'dists/{suite}/{category}/{arch}'


def get_digest(path, kind):
    digest = kind()

    with open(path) as h:
        while True:
            buff = h.read(1024)
            if buff == '':
                break
            digest.update(buff)

    return digest.hexdigest()


def pathstrip(path, tostrip):
    if path.find(tostrip) == 0:
        path = path[len(tostrip) + 1:]
    return path


def get_debs(root):
    for filename in os.listdir(root):
        path = os.path.join(root, filename)
        if path.endswith('.deb'):
            yield path


def generate_package_block(path, filename):
    parts = []
    parts.append(DebPackage(path).control_content('control').strip())
    parts.append('Filename: %s' % filename)
    parts.append('MD5sum: %s' % get_digest(path, hashlib.md5))
    parts.append('SHA1: %s' % get_digest(path, hashlib.sha1))
    parts.append('SHA256: %s' % get_digest(path, hashlib.sha256))
    parts.append('Size: %s' % os.path.getsize(path))
    return '\n'.join(parts)


def generate_indexes(path, suite, category, arch, newpackages=None):
    arch = 'binary-%s' % arch

    subpath = os.path.join(path, subpath_format.format(suite=suite, category=category, arch=arch))

    if not os.path.exists(subpath):
        os.makedirs(subpath)

    if newpackages and os.path.exists(newpackages):
        for filename in os.listdir(newpackages):
            if not filename.endswith('.deb'):
                continue
            old_path = os.path.join(newpackages, filename)
            dest_path = os.path.join(subpath, filename)
            if os.path.exists(dest_path):
                print 'Skipping already found package %s' % old_path
            else:
                print 'Moving %s to %s' % (old_path, dest_path)
                try:
                    shutil.move(old_path, dest_path)
                except (IOError, OSError) as e:
                    print 'Failed moving %s. Just copying instead. %s' % (old_path, e)
                    try:
                        shutil.copyfile(old_path, dest_path)
                    except (IOError, OSError) as e:
                        print 'Failed copying %s to %s: %s' % (old_path, dest_path, e)

    packages_file = os.path.join(path, 'dists', suite, category, arch, 'Packages')
    packages_file_gz = packages_file + '.gz'

    release_file = os.path.join(path, 'dists', suite, 'Release')
    release_trimto = os.path.join(path, 'dists', suite)

    print 'Generating %s' % packages_file
    with open(packages_file, 'w') as h:
        for deb in get_debs(subpath):
            print 'Processing %s' % deb
            filename = pathstrip(deb, path)
            try:
                data = generate_package_block(deb, filename)
            except (IOError, SystemError) as e:
                print '%s failed: %s. Skipping.' % (deb, e)
                continue
            h.write(data)
            h.write('\n\n')

    print 'Generating %s' % packages_file_gz
    with open(packages_file, 'r') as source:
        with gzip.open(packages_file_gz, 'wb') as dest:
            while True:
                buff = source.read(1024)
                if buff == '':
                    break
                dest.write(buff)

    print 'Generating %s' % release_file
    release_sources = [packages_file, packages_file_gz]
    hashes = (('MD5Sum', hashlib.md5), ('SHA1', hashlib.sha1), ('SHA256', hashlib.sha256))
    with open(release_file, 'w') as h:
        h.write('Date: %s\n' % formatdate())
        h.write('Suite: %s\n' % suite)

        for label, kind in hashes:
            h.write('%s:\n' % label)
            for filename in release_sources:
                size = os.path.getsize(filename)
                h.write(' %-64s %s %s\n' % (get_digest(filename, kind), size, pathstrip(filename, release_trimto)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--suite', help='eg: trusty', required=True)
    parser.add_argument('-c', '--category', help='eg: main', required=True)
    parser.add_argument('-a', '--arch', help='amd64', required=True)
    parser.add_argument('-p', '--path', help='path to debian repo', required=True)
    parser.add_argument('-n', '--newpackages', help='path to folder full of new debs. (omit to just regenerate indexes)')
    args = parser.parse_args()
    generate_indexes(**dict(args._get_kwargs()))


if __name__ == '__main__':
    main()
