import warnings
from typing import Literal, Tuple

import numpy as np
from pathops import (
    Path as Path,
    OpBuilder,
    PathOp,
    PathOpsError,
    LineCap,
    LineJoin
)
from pathops._pathops import SegmentPenIterator

from matplotlib.path import Path as MPath
from matplotlib.patches import Patch


def _mpl2skia(mpl_path, transform=None):
    """Convert Matplotlib Path to Skia Path.

    mpl_path: MPL's path instance or Patch instance. In case of Patch, it will retrieve
              its path with patch_transform applied.
    """

    if isinstance(mpl_path, Patch):
        mpl_path = mpl_path.get_patch_transform().transform_path(mpl_path.get_path())

    if transform is not None:
        mpl_path = transform.transform_path(mpl_path)

    ci = iter(mpl_path.codes)
    vi = iter(mpl_path.vertices)

    path = Path()
    pen = path.getPen()

    for c in ci:
        if c == MPath.MOVETO:
            pen.moveTo(next(vi))
        elif c == MPath.LINETO:
            pen.lineTo(next(vi))
        elif c == MPath.CURVE3:
            pen.qCurveTo(next(vi), next(vi))
            next(ci)
        elif c == MPath.CURVE4:
            pen.curveTo(next(vi), next(vi), next(vi))
            next(ci)
            next(ci)
        elif c == MPath.CLOSEPOLY:
            pen.closePath()
            next(vi)

    return path


def skia2mpl(skia_path):
    """Convert Skia Path to Matplotlib Path.
    """

    codes = []
    verts = []

    # segments iterator does some simplification, which make things more complicated.
    # We use SegmentPenIterator, instead.
    for s, cc in list(SegmentPenIterator(skia_path)):

        if s == "moveTo":
            codes.extend([MPath.MOVETO] * len(cc))
            verts.extend(cc)
        elif s == "lineTo":
            codes.extend([MPath.LINETO] * len(cc))
            verts.extend(cc)
        elif s == "qCurveTo":
            if len(cc) == 2:
                codes.extend([MPath.CURVE3, MPath.CURVE3])
                verts.extend(cc)
            elif len(cc) > 2:
                # if len(c) > 2, multiple quad curve points are returned with
                # midpoints skipped and concatenated.
                ccc = []
                for i in range(0, len(cc)-2):
                    cc1 = cc[i]
                    cc2 = cc[i+1]
                    cc12 = 0.5*(np.array(cc1) + np.array(cc2)) # make midpoint
                    ccc.extend([cc1, cc12])
                ccc.extend(cc[-2:])

                verts.extend(ccc)
                codes.extend([MPath.CURVE3] * len(ccc))

        elif s == "curveTo":
            codes.extend([MPath.CURVE4] * len(cc))
            verts.extend(cc)
        elif s == "closePath":
            codes.append(MPath.CLOSEPOLY)
            verts.extend([(0, 0)])

    if len(verts) == 0:
        verts = np.array([]).reshape((0, 2))

    p = MPath(verts, codes=codes)

    return p


def union(path1, path2,
          fix_winding=True, keep_starting_points=False):
    "return the union of two Skia paths"
    builder = OpBuilder(fix_winding=fix_winding,
                        keep_starting_points=keep_starting_points)
    builder.add(path1, PathOp.UNION)
    builder.add(path2, PathOp.UNION)
    result = builder.resolve()

    return result


def union_all(pathlist,
              fix_winding=True, keep_starting_points=False):
    "return the union of Skia paths"
    builder = OpBuilder(fix_winding=fix_winding,
                        keep_starting_points=keep_starting_points)
    for path in pathlist:
        builder.add(path, PathOp.UNION)
    result = builder.resolve()

    return result


def intersection(path1, path2,
                 fix_winding=True, keep_starting_points=False):
    "return the intersection of two Skia paths"
    builder = OpBuilder(fix_winding=fix_winding,
                        keep_starting_points=keep_starting_points)
    builder.add(path1, PathOp.UNION)
    builder.add(path2, PathOp.INTERSECTION)
    result = builder.resolve()

    return result

def difference(path1, path2,
               fix_winding=True, keep_starting_points=False):
    "return the difference of two Skia paths"
    builder = OpBuilder(fix_winding=fix_winding,
                        keep_starting_points=keep_starting_points)
    builder.add(path1, PathOp.UNION)
    builder.add(path2, PathOp.DIFFERENCE)
    result = builder.resolve()

    return result

def xor(path1, path2,
        fix_winding=True, keep_starting_points=False):
    "return the xor of two Skia paths"
    builder = OpBuilder(fix_winding=fix_winding,
                        keep_starting_points=keep_starting_points)
    builder.add(path1, PathOp.UNION)
    builder.add(path2, PathOp.XOR)
    result = builder.resolve()

    return result


_TO_SKIA_LINE_CAP = {
    "butt": LineCap.BUTT_CAP,
    "round": LineCap.ROUND_CAP,
    "square": LineCap.SQUARE_CAP,
}

_TO_SKIA_LINE_JOIN = {
    "miter": LineJoin.MITER_JOIN,
    "round": LineJoin.ROUND_JOIN,
    "bevel": LineJoin.BEVEL_JOIN,
    # No arcs or miter-clip
}


def stroke_to_fill(skpath, stroke_width: float,
                   fractional_tolerence: float = 0.1,
                   linejoin: Literal["miter", "round", "bevel"] ="round",
                   linecap: Literal["butt", "round", "square"] ="round",
                   fractional_miterlimit: float = 1.,
                   dashes: Tuple[float | None, Tuple[float, float] | None] = (None, None),
                   skip_fail=False
                   ):
    "convert stroke to fill"

    tolerance = stroke_width * fractional_tolerence
    miterlimit = stroke_width * fractional_miterlimit

    dash_offset, dash_array = dashes
    dash_offset = 0. if dash_offset is None else dash_offset
    dash_array = () if dash_array is None else dash_array

    skpath = Path(skpath)
    skpath.stroke(stroke_width,
                  _TO_SKIA_LINE_CAP[linecap],
                  _TO_SKIA_LINE_JOIN[linejoin],
                  miterlimit, dash_array, dash_offset)

    skpath.convertConicsToQuads(tolerance)

    backup = Path(skpath)
    try:
        skpath.simplify(fix_winding=True)
    except PathOpsError:
        # skip tricky paths that trigger PathOpsError
        # https://github.com/googlefonts/picosvg/issues/192
        if not skip_fail:
            raise
        warnings.warn("Failed to convert path.")
        skpath = backup

    return skpath


def mpl2skia(p, trans=None):
    return SkiaPath.from_path(_mpl2skia(p, trans))


class SkiaPath(Path):
    def __init__(self, *kl, **kw):
        super().__init__(self, *kl, **kw)
        self.set_boundary(None)

    @classmethod
    def from_path(cls, contour):
        "from skia path"
        # FIXME there should be a better way of doing this.
        path = cls()
        pen = path.getPen()
        contour.draw(pen)
        return path

    @classmethod
    def from_mpl_patch(cls, patch, trans=None):
        "from matplotlib patch. Only the patch_transform is applied by default."
        _path = patch.get_patch_transform().transform_path(patch.get_path())
        return cls.from_mpl_path_transform(_path, trans)

    @classmethod
    def from_mpl(cls, path, trans=None):
        "from matplotlib patch. Only the patch_transform is applied by default."
        # _path = path
        # if trans is not None:
        #     _path = trans.transform_path(_path)
        return cls.from_path(mpl2skia(path, trans))
        # return mpl2skia(_path)

    def to_mpl(self):
        return skia2mpl(self)

    def stroke(self, stroke_width: float,
               fractional_tolerence: float = 0.1,
               linejoin: Literal["miter", "round", "bevel"] ="round",
               linecap: Literal["butt", "round", "square"] ="round",
               fractional_miterlimit: float = 1.,
               dashes: Tuple[float | None, Tuple[float, float] | None] = (None, None),
               skip_fail=False
               ):

        return self.from_path(stroke_to_fill(self, stroke_width,
                                             fractional_tolerence,
                                             linejoin,
                                             linecap,
                                             fractional_miterlimit,
                                             dashes,
                                             skip_fail
                                             ))

    def set_boundary(self, boundary):
        self._boundary = boundary

    def dilate(self, stroke_width: float,
               fractional_tolerence: float = 0.1,
               linejoin: Literal["miter", "round", "bevel"] ="round",
               linecap: Literal["butt", "round", "square"] ="round",
               fractional_miterlimit: float = 1.,
               dashes: Tuple[float | None, Tuple[float, float] | None] = (None, None),
               skip_fail=False
               ):

        _p = stroke_to_fill(self, stroke_width,
                            fractional_tolerence=fractional_tolerence,
                            linejoin=linejoin,
                            linecap=linecap,
                            fractional_miterlimit=fractional_miterlimit,
                            dashes=dashes,
                            skip_fail=skip_fail
                            )
        return self.from_path(union(_p, self))

    def erode(self, stroke_width: float,
               fractional_tolerence: float = 0.1,
               linejoin: Literal["miter", "round", "bevel"] ="round",
               linecap: Literal["butt", "round", "square"] ="round",
               fractional_miterlimit: float = 1.,
               dashes: Tuple[float | None, Tuple[float, float] | None] = (None, None),
               skip_fail=False
               ):

        _p = stroke_to_fill(self, stroke_width,
                            fractional_tolerence=fractional_tolerence,
                            linejoin=linejoin,
                            linecap=linecap,
                            fractional_miterlimit=fractional_miterlimit,
                            dashes=dashes,
                            skip_fail=skip_fail
                            )
        return self.from_path(difference(self, _p))

    def __sub__(self, other):
        return self.from_path(difference(self, other))

    def __rsub__(self, other):
        return self.from_path(difference(other, self))

    def __xor__(self, other):
        return self.from_path(xor(self, other))

    def __or__(self, other):
        return self.from_path(union(self, other))

    def __ror__(self, other):
        return self.from_path(union(self, other))

    def __and__(self, other):
        return self.from_path(intersection(self, other))

    def __rand__(self, other):
        return self.from_path(intersection(self, other))

    def __invert__(self):
        if self._boundary is None:
            raise ValueError("invert requires boundary. please set it with set_boundary method")
        return self.from_path(difference(self._boundary, self))




if __name__ == '__main__':
    from matplotlib.text import TextPath
    p = TextPath((0, 0), "MA", size=20)

    skpath = mpl2skia(p)
