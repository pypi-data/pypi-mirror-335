"""
This module provide a helper class to us skia pathops as a patheffect in matplotlib.


"""

import warnings

from matplotlib.patches import Patch

from mpl_visual_context.patheffects_base import ChainablePathEffect
import mpl_visual_context.patheffects  as pe

from .mpl_skia_pathops_helper import mpl2skia, skia2mpl, union, intersection, difference, xor
from .mpl_skia_pathops_helper import stroke_to_fill


class PathOpsPathEffectBase(ChainablePathEffect):
    pass

from typing import Literal, Tuple

class PathOpsPathEffectStroke2Fill(PathOpsPathEffectBase):

    def __init__(self, linewidth: float | None =None,
                 joinstyle: Literal["miter", "round", "bevel"] | None =None,
                 linecap: Literal["butt", "round", "square"] | None =None,
                 dashes: Tuple[float | None, Tuple[float, float] | None] | None = None,
                 ):
        """
        if None, use values from the GC.
        """
        self._linewidth = linewidth
        self._linejoin = joinstyle
        self._linecap = linecap
        self._dashes = dashes

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):

        stroke_width = self._linewidth if self._linewidth is not None else gc.get_linewidth()
        if stroke_width == 0:
            warnings.warn("stroke width of 0. skipping the path effect.")
            return renderer, gc, tpath, affine, rgbFace

        linejoin = self._linejoin if self._linejoin is not None else gc.get_joinstyle()
        linecap = self._linecap if self._linecap is not None else gc.get_capstyle()

        dashes = self._dashes if self._dashes is not None else gc.get_dashes()

        path = skia2mpl(stroke_to_fill(mpl2skia(tpath),
                                       stroke_width=stroke_width,
                                       linecap=linecap,
                                       linejoin=linejoin,
                                       dashes=dashes
                                       ))

        return renderer, gc, path, affine, rgbFace



class PathOpsPathEffectBinary(PathOpsPathEffectBase):
    _operators = dict(union=union, intersection=intersection, difference=difference, xor=xor)

    def __init__(self, op, path, transform=None,
                 lazy=False, invert=False):
        assert op in self._operators

        self._op = self._operators[op]
        self._invert = invert

        if callable(path):
            lazy = True

        self._lazy = lazy

        if not lazy:
            self._path, self._transform = self._get_path_transform(path, transform)
        else:
            self._path, self._transform = path, transform

    def _get_path_transform(self, path, transform):
        _transform = transform

        if callable(path):
            path = path()

        if isinstance(path, Patch):
            _path = path.get_path()
            if _transform is None:
                _transform = path.get_transform()
        else:
            _path = path

        return _path, _transform

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):

        if self._lazy:
            _path, _transform = self._get_path_transform(self._path, self._transform)
        else:
            _path, _transform = self._path, self._transform

        if _transform is None:
            transform = affine.inverted()
        else:
            transform = _transform + affine.inverted()

        transformed_target_path = transform.transform_path(_path)

        if self._invert:
            path = skia2mpl(self._op(mpl2skia(transformed_target_path), mpl2skia(tpath)))
        else:
            path = skia2mpl(self._op(mpl2skia(tpath), mpl2skia(transformed_target_path)))

        return renderer, gc, path, affine, rgbFace


class PathOpsPathEffect(PathOpsPathEffectBinary, PathOpsPathEffectStroke2Fill):
    @classmethod
    def difference(cls, path, transform=None, invert=False, lazy=False):
        return cls("difference", path, transform,
                   invert=invert, lazy=lazy)

    @classmethod
    def union(cls, path, transform=None, invert=False, lazy=False):
        return cls("union", path, transform,
                   invert=invert, lazy=lazy)

    @classmethod
    def intersection(cls, path, transform=None, invert=False, lazy=False):
        return cls("intersection", path,
                   transform, invert=invert, lazy=lazy)

    @classmethod
    def xor(cls, path, transform=None, invert=False, lazy=False):
        return cls("xor", path, transform,
                   invert=invert, lazy=lazy)

    @classmethod
    def stroke2fill(cls, linewidth: float | None =None,
                    joinstyle: Literal["miter", "round", "bevel"] | None =None,
                    linecap: Literal["butt", "round", "square"] | None =None,
                    dashes: Tuple[float | None, Tuple[float]] | None = None,
                    ):

        return PathOpsPathEffectStroke2Fill(linewidth=linewidth, joinstyle=joinstyle,
                                            linecap=linecap, dashes=dashes)


class ContourSelector(ChainablePathEffect):

    def __init__(self, selector):
        """
        The selector should be a function of a following signature, where i is an index of
        the contour and c is the contour itself.

        def selector(i, c):
            pass



        """
        self._selector = selector

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        spath = mpl2skia(tpath)
        spath_new = type(spath)()
        pen = spath_new.getPen()
        for c in [c for i, c in enumerate(spath.contours) if self._selector(i, c)]:
            c.draw(pen)

        tpath2 = skia2mpl(spath_new)

        return renderer, gc, tpath2, affine, rgbFace
