#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jae-Joon Lee.
# Distributed under the terms of the Modified BSD License.

# Must import __version__ first to avoid errors importing this file during the build process.
# See https://github.com/pypa/setuptools/issues/1724#issuecomment-627241822
from ._version import __version__

__all__ = ["mpl2skia", "skia2mpl", "union", "union_all", "intersection", "difference", "xor",
           "stroke_to_fill",
           "SkiaPath",
           "PathOpsPathEffect",
           "SkiaShadow", "make_shadow_patheffects"
           ]

from .mpl_skia_pathops_helper import (mpl2skia, skia2mpl, union, union_all,
                               intersection, difference, xor,
                               stroke_to_fill,
                               SkiaPath)
from .mpl_pe_pathops import (PathOpsPathEffect,)

from .pe_skia_shadow import (SkiaShadow, make_shadow_patheffects)
