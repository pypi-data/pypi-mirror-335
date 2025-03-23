from .mpl_skia_pathops import mpl2skia, skia2mpl, union, intersection, difference, xor

from mpl_visual_context.patheffects_base import ChainablePathEffect
import mpl_visual_context.patheffects  as pe

class PathOpsPathEffect(ChainablePathEffect):
    def __init__(self, pathops, op):
        assert op in pathops._operators
        self._pathops = pathops
        self._op = op

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        tpath2 = affine.transform_path(tpath)
        if self._op == "update_from":
            self._pathops._skia_path = mpl2skia(tpath2)
            return renderer, gc, tpath, affine, rgbFace
        else:
            pathops = self._pathops.operate(self._op, mpl2skia(tpath2))
            new_tpath = pathops.get_mpl_path()
            new_tpath = affine.inverted().transform_path(new_tpath)
            return renderer, gc, new_tpath, affine, rgbFace

# FIXME This is used to update the pathops._skia_path on the fly within the
# patheffects. There should be a better way to handle this.
def reset(path1, path2):
    return path2


class PathOps():
    _operators = dict(union=union, intersection=intersection, difference=difference, xor=xor,
                      update_from=reset)

    def __init__(self, skia_path=None):
        self._skia_path = skia_path

    def get_skia_path(self):
        return self._skia_path

    @classmethod
    def from_mpl_path(cls, mpl_path, transform=None):
        return PathOpsFromPath(mpl_path, transform=transform)

    @classmethod
    def from_mpl_patch(cls, mpl_patch):
        return PathOpsFromPatch(mpl_patch)

    @classmethod
    def from_func(cls, func):
        return PathOpsFromFunc(func)

    def get_mpl_path(self):
        return skia2mpl(self.get_skia_path())

    def operate(self, op, skia_path):
        skia_path = self._operators[op](self.get_skia_path(), skia_path)
        return PathOps(skia_path)

    def get_path_effect(self, op):
        return PathOpsPathEffect(self, op)


class PathOpsFromPath(PathOps):
    def __init__(self, mpl_path, transform=None):
        super().__init__()
        self._mpl_path = mpl_path
        self._transform = transform

    def get_skia_path(self):
        if self._transform is None:
            mpath = self._mpl_path
        else:
            mpath = self._transform.transform_path(self._mpl_path)

        return mpl2skia(mpath)

class PathOpsFromPatch(PathOps):
    def __init__(self, mpl_patch):
        super().__init__()
        self._mpl_patch = mpl_patch

    def get_skia_path(self):
        mpl_path = self._mpl_patch.get_path()
        tr = self._mpl_patch.get_transform()

        if tr is None:
            mpath = mpl_path
        else:
            mpath = tr.transform_path(mpl_path)

        return mpl2skia(mpath)

class PathOpsFromFunc(PathOps):
    def __init__(self, func):
        super().__init__()
        self._func = func

    def get_skia_path(self):
        mpath = self._func()
        return mpl2skia(mpath)


