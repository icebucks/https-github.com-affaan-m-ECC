"""Episode 1 (PLANNER vs. DOER) in the current series format: English, hook + series overlay,
v2 figures, motion blur. Reuses ep1.py's scene unchanged."""
import os, sys
os.environ.setdefault("VID_LANG", "en")
import lib
import ep1


def _fig(c, x, y_ground, p, s=0.78, facing=1, rot=0.0, body=(244, 244, 240), light=None, ground_mode="feet"):
    J = lib.figure(c, x, y_ground, p, s=s, facing=facing, rot=rot, body=body, mode="feet" if ground_mode == "feet" else "hip",
                   rim=((255, 200, 130), 0.45), light=(-1, -1))
    return J["head"]


ep1.draw_figure = _fig
_macher = ep1.macher
ep1.macher = lambda t: lib.smooth(_macher, t, w=0.08)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "still":
        lib.stills(lambda c, t: (ep1.frame(c, t + 0.6), lib.series_overlay(c, t, 1, "Still planning instead of doing?", 16.3, 640)),
                   [0.5, 3.0, 6.6, 9.0, 12.5, 16.5], "check/ep1en")
    else:
        lib.finish_v2("Folge1_Planner", ep1.frame, ep1.T_END, [list(e) for e in ep1.events()], ep1.T_TOP, 1,
                      "Still planning instead of doing?", 0.6, 16.9, follow_y=640)
