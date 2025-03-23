from functools import partial

import mpl_visual_context.patheffects as pe
from mpl_visual_context.patheffects_shadow import ShadowPath

# from mpl_skia_pathops import PathOpsPathEffect
from . import PathOpsPathEffect

# a helper function that retrieves the path from the clipboard.
def get_path_from_cb(cb):
    path = cb["tpath"]
    affine = cb["affine"]
    return affine.transform_path(path)


# Using the path that contourf creates for this purpose turns out to be quite
# difficult as it actually creates contour patches as a list of donuts with holes inside.
# Because of this holes, it is not possible to use the path directly to create a patch.
# So, we rerun QuadContourSet with the levels specified.


def SkiaShadow(offset=2.5, angle=135):

    cb = pe.Clipboard()

    patheffect = (
        cb.copy()
        | ShadowPath(angle, offset)
        | PathOpsPathEffect.difference(partial(get_path_from_cb, cb), invert=False)
    )

    return patheffect

def make_shadow_patheffects(
        fc_white="w",
        fc_black="0.2",
        alpha=0.5,
        offset=2.5,
        angle=135):

    patheffects = [
        (SkiaShadow(offset, angle)
         | pe.FillColor(fc_black)
         | pe.GCModify(alpha=alpha)),
        (SkiaShadow(offset, 180+angle)
         | pe.FillColor(fc_white)
         | pe.GCModify(alpha=alpha)),
    ]

    return patheffects


def main():
    import matplotlib.pyplot as plt
    from matplotlib.patheffects import Normal


    fig, ax = plt.subplots(1, 1, num=1, clear=True)

    ax.set_aspect(1)

    patheffects = make_shadow_patheffects(fc_black="k", offset=2, angle=45, alpha=0.8)

    t = ax.text(0.5, 0.5, "A", fontsize=30, color="y")
    t.set_path_effects(patheffects)

    ax.patch.set_fc("gold")

    plt.show()

if __name__ == '__main__':
    main()
