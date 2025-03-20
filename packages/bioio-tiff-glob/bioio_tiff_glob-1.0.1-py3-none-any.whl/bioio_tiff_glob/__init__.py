#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Top-level package for bioio_tiff_glob."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("bioio-tiff-glob")
except PackageNotFoundError:
    __version__ = "uninstalled"

__author__ = "bioio-devs"
__email__ = "brian.whitney@alleninstitute.org"

from .reader import Reader
from .reader_metadata import ReaderMetadata

__all__ = ["Reader", "ReaderMetadata"]
