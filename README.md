# Quickly make custom debian repository

This will create the local debian package folder structure and necessary boilerplate for apt/apt-get to work.

## Installation

quickdebrepo is hosted on pypi, and requires python2.

    sudo apt-get install python2.7 python-apt
    pip install quickdebrepo

## Usage

Place your deb files in /path/to/debs, and run the following to import them and generate
necessary apt metadata:

    python qdr.py -p /var/www/html/ubuntu -c main -s trusty -a amd64 --newpackages /path/to/debs

You can then add a line to your sources.list file like the following, and apt-get will *just work*
with the exception of GPG signed packages, so you will get signing/authentication warnings.

    deb [arch=amd64] http://apt.yourdomain.com/ubuntu trusty main

All this assuming `apt.yourdomain.com` is a web server serving /var/www/html/ as the docroot.

## TODO

- GPG signing
- Python 3.x support
- more flexibility
- if any demand exists, S3/etc support
- put this on cheese factory so you can get it with `pip`

## Why?

Previously I used [PRM](https://github.com/dnbert/prm), but that project is dead and has a few issues which break support for
ubuntu xenial: incorrect date format in Release file, and massive memory usage when
computing package checksums. It also has a lot of functionality I don't need, such as S3 and
RPM. It's also Ruby and I felt I could make something more efficient in Python.

## Meta
- License: MIT
- Author: Joe Gillotti <joe@u13.net>
