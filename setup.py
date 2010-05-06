#!/usr/bin/env python
# vim:filetype=python:fileencoding=utf-8
import sys

from setuptools import setup
from hgsshsign._meta import SETUP_ARGS


def main():
    setup(**SETUP_ARGS)
    return 0


if __name__ == '__main__':
    sys.exit(main())
