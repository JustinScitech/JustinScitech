#!/usr/bin/env python3
"""Builds assets/readme-{light,dark}.svg: a README that looks like plain markdown until two
stick figures wander in, react to each line of experience, and stretch "2027" until it's huge.

GitHub strips inline <svg> from markdown, so README.md shows this through a <picture> tag,
one variant per GitHub theme. Edit the text or the choreography here and re-run:

    python3 scripts/build_svgs.py
"""
import math
from html import escape
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
PERIOD = 36                     # seconds per loop; every timestamp below is a percentage of this
HALF_STEP = .26 / PERIOD * 100  # one stride, as a percentage

THEMES = {
    "dark": dict(fg="#f0f6fc", bg="#0d1117", border="#3d444db3",
                 heart="#f85149", spark="#e3b341", cash="#3fb950", sweat="#79c0ff"),
    "light": dict(fg="#1f2328", bg="#ffffff", border="#d1d9e0b3",
                  heart="#cf222e", spark="#bf8700", cash="#1a7f37", sweat="#0969da"),
}

# Advance widths at 100px for ASCII 32..126 in -apple-system, regular and semibold. Each text
# run also gets a textLength, so other system fonts are spaced to the same layout.
_ADV = {
    400: "20.5,26.7,40.3,60.4,60.4,80.8,66.9,25.4,32.2,32.2,40.0,60.4,21.5,42.9,21.5,27.9,60.6,44.3,56.6,59.2,"
         "60.4,58.5,61.7,54.7,60.0,61.7,21.5,21.5,60.4,60.4,60.4,48.9,87.5,63.5,60.4,68.6,67.9,55.2,52.8,70.7,"
         "69.9,22.5,49.5,60.1,52.4,83.1,69.9,73.1,57.8,73.1,59.9,59.3,58.1,69.6,63.1,92.4,63.5,61.2,61.7,32.2,"
         "27.9,32.2,60.4,52.7,50.0,50.2,55.4,50.1,55.4,51.2,30.4,54.9,53.9,20.6,20.5,48.5,20.4,80.3,52.7,53.1,"
         "54.9,54.9,30.8,46.5,30.1,52.7,48.3,71.5,46.8,48.6,46.8,32.2,21.6,32.2,60.4",
    600: "20.0,30.0,43.8,62.7,63.3,86.3,69.1,26.5,36.2,36.2,43.3,63.3,23.2,43.7,23.2,29.5,63.9,46.8,59.1,61.7,"
         "63.3,61.2,64.1,56.3,63.2,64.1,23.2,23.2,63.3,63.3,63.3,51.9,88.3,67.3,62.8,70.4,69.3,56.6,54.2,72.0,"
         "71.9,25.1,53.7,63.6,53.7,85.1,70.9,74.6,60.4,74.5,62.6,61.9,59.5,70.4,66.3,95.2,66.8,64.7,62.6,36.2,"
         "29.5,36.2,63.3,56.0,50.0,53.2,58.3,53.0,58.2,54.1,33.8,57.8,56.9,22.9,22.9,52.1,22.9,84.3,56.0,55.9,"
         "57.9,57.8,34.5,49.8,33.7,56.0,51.3,76.5,50.8,52.1,49.3,36.2,23.3,36.2,63.3",
}
ADV = {w: dict(zip(map(chr, range(32, 127)), map(float, s.split(",")))) for w, s in _ADV.items()}

# Layout mirrors GitHub's markdown-body: h1 32px/40px with a 1px rule, 16px/24px body text,
# 16px block margins, 4px between list items, list text indented 32px.
W = 830
TOP = 14
H1_BASE = TOP + 31
RULE = TOP + 50
LI = [TOP + 84.3 + 28 * k for k in range(5)]
P_BASE = TOP + 236.3
HEIGHT = P_BASE + 12

# Segments are (text, weight) or (text, weight, id); ids become CSS classes the figures react to.
HEADING = [("Hi, I'm Justin Lau", 600)]
BULLETS = [
    [("waterloo ECE student", 400)],
    [("currently @ ", 400), ("LiveKit", 600, "livekit"), (", prev @ ", 400), ("Databricks", 400, "databricks"),
     (", ", 400), ("Tesla", 400, "tesla"), (", ", 400), ("Voldex", 400, "voldex"), (", ", 400),
     ("SPS Commerce", 400, "sps")],
    [("built out ", 400), ("Toona.io", 600, "toona"), (" ", 400), ("(VC backed, 100k users)", 400, "vc")],
    [("Roblox game studio owner (", 400), ("Legion Studios", 600, "legion"),
     (", 12k followers), prev Driving Empire developer", 400)],
    [("looking for new grad opportunities in ", 400), ("2027", 600, "y2027")],
]
CLOSER = "Contact me through my personal website for any inquiries or requests!"

STRETCH = 3    # how big "2027" gets
CROUCH = .56   # squat height that fits a figure under the line of text above


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def width(s, size, weight):
    return sum(ADV[weight][ch] for ch in s) * size / 100


def text_run(segments, x, y, size, fill):
    """Lays segments out left to right. Returns markup and {id: (x0, x1)} for tagged segments."""
    out, spans = [], {}
    for seg in segments:
        s, weight = seg[0], seg[1]
        body = s.strip(" ")
        bx = x + width(s[:len(s) - len(s.lstrip(" "))], size, weight)
        bw = width(body, size, weight)
        if body:
            cls = f' class="{seg[2]}"' if len(seg) > 2 else ""
            fit = f' textLength="{fmt(bw)}" lengthAdjust="spacing"' if len(body) > 1 else ""
            out.append(f'<text{cls} x="{fmt(bx)}" y="{fmt(y)}" font-size="{size}" font-weight="{weight}" '
                       f'fill="{fill}"{fit}>{escape(body)}</text>')
        if len(seg) > 2:
            spans[seg[2]] = (bx, bx + bw)
        x += width(s, size, weight)
    return "".join(out), spans


class Anim:
    """Collects @keyframes plus the class rules that play them on the shared loop."""

    def __init__(self):
        self.css = []

    def add(self, cls, frames, origin=None, timing="ease-in-out"):
        times = [t for t, _ in frames]
        assert times == sorted(times) and len(set(times)) == len(times), f"{cls}: keyframes out of order {times}"
        name = cls.replace("-", "_")
        steps = " ".join(f"{fmt(t)}% {{ {decl} }}" for t, decl in frames)
        self.css.append(f"@keyframes {name} {{ {steps} }}")
        o = f"transform-origin: {fmt(origin[0])}px {fmt(origin[1])}px; " if origin else ""
        self.css.append(f".{cls} {{ {o}animation: {name} {PERIOD}s {timing} infinite; }}")


def rot(deg):
    # Limbs are drawn hanging straight down; positive swings them forward (toward +x).
    return f"transform: rotate({fmt(-deg)}deg)"


def star(cx, cy, r, fill):
    k = r * .3
    return (f'<path d="M{fmt(cx)} {fmt(cy - r)} L{fmt(cx + k)} {fmt(cy - k)} L{fmt(cx + r)} {fmt(cy)} '
            f'L{fmt(cx + k)} {fmt(cy + k)} L{fmt(cx)} {fmt(cy + r)} L{fmt(cx - k)} {fmt(cy + k)} '
            f'L{fmt(cx - r)} {fmt(cy)} L{fmt(cx - k)} {fmt(cy - k)} Z" fill="{fill}"/>')


def heart(cx, cy, fill):
    return (f'<path transform="translate({fmt(cx)} {fmt(cy)}) scale(1.5)" d="M0 1.8 C-3.2 -.6 -2.6 -3.4 -.9 -3.2 '
            f'C-.3 -3.1 0 -2.6 0 -2.3 C0 -2.6 .3 -3.1 .9 -3.2 C2.6 -3.4 3.2 -.6 0 1.8 Z" fill="{fill}"/>')


def twinkle(anim, cls, t0, t1, center, every=1.4, phase=0):
    frames, t = [(0, "transform: scale(0) rotate(0deg)")], t0 + phase
    while t + every <= t1:
        frames += [(t, "transform: scale(0) rotate(0deg)"), (t + every / 2, "transform: scale(1) rotate(45deg)"),
                   (t + every, "transform: scale(0) rotate(90deg)")]
        t += every * 1.2
    anim.add(cls, frames + [(100, "transform: scale(0) rotate(90deg)")], origin=center)


def floaters(anim, cls, t0, t1, xs, y, make, every=.9, life=2.6, rise=20):
    """Little things (hearts, $) that keep drifting up from a point between t0 and t1."""
    out, t, i = [], t0, 0
    while t + life <= t1 + .01:
        x = xs[i % len(xs)]
        drift = 4 if i % 2 else -4
        end = f"transform: translate({drift}px, -{rise}px) scale(1); opacity: 0"
        anim.add(f"{cls}{i}", [
            (0, "transform: translate(0px, 0px) scale(.4); opacity: 0"),
            (t, "transform: translate(0px, 0px) scale(.4); opacity: 0"),
            (t + .35, "transform: translate(0px, -3px) scale(1); opacity: 1"),
            (t + life, end), (100, end)], origin=(x, y))
        out.append(f'<g class="{cls}{i}">{make(x, y)}</g>')
        t, i = t + every, i + 1
    return "".join(out)


STAND = dict(arm1=12, arm2=-12, leg1=20, leg2=-20)

# Faces are drawn on a head centred at (0, -33) with radius 6.5, looking toward +x.
def _lines(d, c):
    return (f'<path d="{d}" fill="none" stroke="{c["fg"]}" stroke-width="1.1" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


SMILE = "M1.8 -29.7 Q3.6 -28 5.4 -30.4"
FACES = {
    "normal": lambda c: f'<circle cx="2.6" cy="-33.5" r="1.15" fill="{c["fg"]}"/>',
    "happy": lambda c: _lines("M1.2 -33 L2.7 -34.9 L4.2 -33 " + SMILE, c),
    "shock": lambda c: (f'<circle cx="2.8" cy="-34.3" r="1.9" fill="{c["bg"]}" stroke="{c["fg"]}" stroke-width="1"/>'
                        f'<circle cx="3.3" cy="-34.3" r=".7" fill="{c["fg"]}"/>'
                        f'<ellipse cx="3.9" cy="-29.4" rx="1.1" ry="1.6" fill="{c["fg"]}"/>'
                        + _lines("M.8 -37.9 L4.6 -38.8", c)),
    "stars": lambda c: star(2.9, -33.9, 2.6, c["spark"]) + _lines(SMILE, c),
    "cash": lambda c: (f'<text x="2.9" y="-31.2" font-size="7" font-weight="800" text-anchor="middle" '
                       f'fill="{c["cash"]}">$</text>' + _lines(SMILE, c)),
    "dizzy": lambda c: _lines("M1.5 -35 L4.2 -32.3 M4.2 -35 L1.5 -32.3 M1.6 -29.6 q.9 -1 1.8 0 q.9 1 1.8 0", c),
    "strain": lambda c: _lines("M1.5 -35.2 L3.9 -33.7 L1.5 -32.2 M1.6 -29.8 L5.4 -29.8", c),
}


class Actor:
    """A stick figure drawn around its feet at (0, 0), facing +x. Methods are called in time
    order and record keyframes for its position, facing, lean, limbs, face and emotes."""

    def __init__(self, name, x, y, facing, s, extras):
        self.name, self.x, self.y, self.dir, self.s, self.extras = name, x, y, facing, s, extras
        self.tracks = {k: [] for k in ("move", "flip", "lean", "squash", "arm1", "arm2", "leg1", "leg2")}
        self.pose, self.tilt, self.k = dict(STAND), 0, 1
        self.faces, self.emotes = [(0, "normal")], []
        self._key("squash", 0, "transform: scaleY(1)")
        self.hold(0)

    def _key(self, track, t, decl, timing=None):
        frames = self.tracks[track]
        if timing:
            decl += f"; animation-timing-function: {timing}"
        if frames and frames[-1][0] == t:
            frames[-1] = (t, decl)
        else:
            frames.append((t, decl))

    def _place(self, t, timing=None):
        self._key("move", t, f"transform: translate({fmt(self.x)}px, {fmt(self.y)}px)", timing)

    def hold(self, t):
        """Pin position, facing, lean and pose at t, so the next change starts from here."""
        self._place(t)
        self._key("flip", t, f"transform: scaleX({self.dir})")
        self._key("lean", t, f"transform: rotate({fmt(self.tilt)}deg)")
        for limb, deg in self.pose.items():
            self._key(limb, t, rot(deg))

    def set(self, t, **pose):
        self.pose.update(pose)
        for limb in pose:
            self._key(limb, t, rot(self.pose[limb]))

    def turn(self, t, facing):
        self.dir = facing
        self._key("flip", t, f"transform: scaleX({facing})")

    def lean(self, t, deg):
        """Tip the whole body around the feet; positive leans forward, -90 is flat on its back."""
        self.tilt = deg
        self._key("lean", t, f"transform: rotate({fmt(deg)}deg)")

    def crouch(self, t, k):
        """Squat to k of full height. Crouched figures fit under the line of text above them."""
        self.k = k
        self._key("squash", t, f"transform: scaleY({k})")

    def face(self, t, name):
        self.faces.append((t, name))

    def emote(self, t0, t1, kind, at=None):
        """Show kind ("!", "?", "GG", hearts, cash, sparkles, sweat) by the head, or at (x, y)."""
        self.emotes.append((t0, t1, kind, at, self.k))

    def walk(self, t0, t1, x, arms=True):
        self.hold(t0)
        self._place(t0, "linear")
        n = max(2, round((t1 - t0) / HALF_STEP))
        for i in range(1, n):
            t, sw = t0 + (t1 - t0) * i / n, 26 if i % 2 else -26
            self.set(t, leg1=sw, leg2=-sw, **(dict(arm1=-sw * .8, arm2=sw * .8) if arms else {}))
        self.x = x
        self._place(t1)
        self.set(t1, leg1=STAND["leg1"], leg2=STAND["leg2"],
                 **({"arm1": STAND["arm1"], "arm2": STAND["arm2"]} if arms else {}))

    def jump(self, t0, t1, x, y, lift, arms=None):
        self.hold(t0)
        self._place(t0, "ease-out")
        mid = t0 + (t1 - t0) * .4
        peak = min(self.y, y) - lift
        self._key("move", mid, f"transform: translate({fmt((self.x + x) / 2)}px, {fmt(peak)}px)", "ease-in")
        self.x, self.y = x, y
        self._place(t1)
        if arms:
            self.set(mid, **arms)
            self.set(t1, arm1=STAND["arm1"], arm2=STAND["arm2"])
        self._key("squash", t1, f"transform: scaleY({self.k})")
        self._key("squash", t1 + .35, f"transform: scaleY({fmt(self.k * .8)})")
        self._key("squash", t1 + 1, f"transform: scaleY({self.k})")

    def clap(self, t0, t1, every=.45):
        t, closed = t0, True
        while t <= t1:
            self.set(t, arm1=82 if closed else 60, arm2=78 if closed else 40)
            t, closed = t + every, not closed
        self.set(t1 + .5, arm1=STAND["arm1"], arm2=STAND["arm2"])

    def render(self, anim, c):
        s, n = self.s, self.name
        shoulder, hip = (0, -23 * s), (0, -11 * s)
        for track, frames in self.tracks.items():
            frames = frames + [(100, frames[-1][1].split(";")[0])]
            origin = {"arm1": shoulder, "arm2": shoulder, "leg1": hip, "leg2": hip}.get(track, (0, 0))
            anim.add(f"{n}-{track}", frames, origin=None if track == "move" else origin,
                     timing="steps(1, end)" if track == "flip" else "ease-in-out")

        faces = []
        for name in sorted({f for _, f in self.faces}):
            frames = [(t, f"opacity: {1 if f == name else 0}") for t, f in self.faces]
            anim.add(f"{n}-face-{name}", frames + [(100, frames[-1][1])], timing="steps(1, end)")
            faces.append(f'<g class="{n}-face-{name}">{FACES[name](c)}</g>')

        emotes = []
        for i, (t0, t1, kind, at, k) in enumerate(self.emotes):
            cls = f"{n}-e{i}"
            ox, oy = at or (0, -42 * s * k)
            if kind == "hearts":
                emotes.append(floaters(anim, cls, t0, t1, (ox - 4, ox + 3, ox), oy, lambda x, y: heart(x, y, c["heart"]),
                                      rise=20 * k))
            elif kind == "cash":
                emotes.append(floaters(anim, cls, t0, t1, (ox - 6, ox + 6, ox), oy, lambda x, y: (
                    f'<text x="{fmt(x)}" y="{fmt(y)}" font-size="11" font-weight="800" text-anchor="middle" '
                    f'fill="{c["cash"]}" stroke="{c["bg"]}" stroke-width="3" paint-order="stroke">$</text>'), rise=20 * k))
            elif kind == "sparkles":
                for k, (dx, dy) in enumerate(((-12, -42), (14, -44), (-15, -24), (16, -26))):
                    center = (dx * s, dy * s * k)
                    twinkle(anim, f"{cls}s{k}", t0, t1, center, phase=k * .35)
                    emotes.append(f'<g class="{cls}s{k}">{star(*center, 3.6, c["spark"])}</g>')
            elif kind == "sweat":
                anim.add(cls, [(0, "transform: translate(0px, 0px); opacity: 0"),
                               (t0, "transform: translate(0px, 0px); opacity: 0"),
                               (t0 + .3, "transform: translate(0px, 0px); opacity: 1"),
                               (t1, "transform: translate(2px, 7px); opacity: 0"),
                               (100, "transform: translate(2px, 7px); opacity: 0")])
                emotes.append(f'<g class="{cls}"><path transform="translate({fmt(-9 * s)} {fmt(-38 * s * k)})" '
                              f'd="M0 -3 Q2.4 .6 0 1.6 Q-2.4 .6 0 -3 Z" fill="{c["sweat"]}"/></g>')
            else:
                # Crouched figures say things lower down, in the gap between two lines of text.
                x, y = at or (9 * s, -32 * s * k + (6 if k < 1 else 0))
                anim.add(cls, [(0, "transform: scale(0); opacity: 0"), (t0, "transform: scale(0); opacity: 0"),
                               (t0 + .4, "transform: scale(1.35); opacity: 1"), (t0 + .9, "transform: scale(1); opacity: 1"),
                               (t1 - .4, "transform: scale(1); opacity: 1"), (t1, "transform: scale(.6); opacity: 0"),
                               (100, "transform: scale(.6); opacity: 0")], origin=(x, y - 5))
                emotes.append(f'<g class="{cls}"><text x="{fmt(x)}" y="{fmt(y)}" font-size="14" font-weight="800" '
                              f'fill="{c["fg"]}" stroke="{c["bg"]}" stroke-width="4" paint-order="stroke" '
                              f'stroke-linejoin="round">{escape(kind)}</text></g>')

        def figure(stroke, weight, ink):
            def limb(cls, a, b):
                return (f'<g class="{n}-{cls}"><line x1="{fmt(a[0])}" y1="{fmt(a[1])}" '
                        f'x2="{fmt(b[0])}" y2="{fmt(b[1])}"/></g>')
            return (
                f'<g fill="none" stroke="{stroke}" stroke-width="{weight}" stroke-linecap="round" stroke-linejoin="round">'
                + limb("leg2", hip, (0, 0)) + limb("leg1", hip, (0, 0)) + limb("arm2", shoulder, (0, -11 * s))
                + f'<line x1="0" y1="{fmt(-26.5 * s)}" x2="0" y2="{fmt(hip[1])}"/>'
                + f'<circle cx="0" cy="{fmt(-33 * s)}" r="{fmt(6.5 * s)}" fill="{c["bg"]}"/>'
                + limb("arm1", shoulder, (0, -11 * s))
                + f'<g transform="scale({s})">{self.extras(c, stroke)}'
                + ("".join(faces) if ink else "") + "</g></g>")

        # Draw every stroke twice, a fat page-coloured halo first, so the figures stay readable
        # when they walk in front of README text.
        body = figure(c["bg"], 6, False) + figure(c["fg"], 2.2, True)
        return (f'<g class="{n}-move">{"".join(emotes)}<g class="{n}-flip"><g class="{n}-lean">'
                f'<g class="{n}-squash">{body}</g></g></g></g>')


def beanie(c, stroke):
    return (f'<path d="M-6.7 -33.8 A6.7 6.7 0 0 1 6.7 -33.8 Z" fill="{stroke}"/>'
            '<line x1="0" y1="-40.3" x2="0" y2="-43"/>'
            '<line class="a-prop" x1="-4.6" y1="-43.4" x2="4.6" y2="-43.4"/>')


def tuft(c, stroke):
    return '<path d="M-1 -39.3 q-.8 -3 2.8 -4"/><path d="M-5.6 -35 q-5 1 -5.5 6"/>'


def build(c):
    anim = Anim()
    heading, _ = text_run(HEADING, 0, H1_BASE, 32, c["fg"])
    lines, spans, ends = [], {}, []
    for k, line in enumerate(BULLETS):
        run, sp = text_run(line, 32, LI[k], 16, c["fg"])
        spans.update(sp)
        ends.append(32 + sum(width(s[0], 16, s[1]) for s in line))
        lines.append(f'<circle cx="18.5" cy="{fmt(LI[k] - 5)}" r="2.6" fill="{c["fg"]}"/>{run}')
    closer, _ = text_run([(CLOSER, 400)], 0, P_BASE, 16, c["fg"])

    def mid(key):
        return sum(spans[key]) / 2

    a = Actor("a", W + 30, LI[0], -1, 1.05, beanie)
    b = Actor("b", W + 30, LI[0], -1, 1, tuft)
    lit = {}  # word id -> (when it lights up, for how long)

    # --- A walks the gap above the job list, reading right to left, more amazed at every stop.
    stops = [("sps", 3, 9, "!", "happy"), ("voldex", 12.8, 14.8, "!!", "shock"),
             ("tesla", 18.4, 20, "sparkles", "stars"), ("databricks", 23.8, 25.4, "!!!", "shock")]
    for key, t0, t1, emote, face in stops:
        if t0 > 3:
            a.lean(t0 - .2, 0)
            a.face(t0 - .2, "normal")
        a.walk(t0, t1, mid(key))
        a.lean(t1 + .4, 20)
        a.face(t1 + .6, face)
        a.emote(t1 + .6, t1 + 3.4, emote)
        lit[key] = (t1 + .8, 2.6)
    a.lean(29, 0)
    a.face(29, "normal")
    # LiveKit sits under the end of line one, so A stops just past it, peers over, and loses it.
    a.walk(29.2, 30.8, ends[0] + 16)
    a.lean(31.2, 18)
    a.face(31.6, "shock")
    a.emote(31.6, 34.4, "!!!")
    lit["livekit"] = (31.8, 9.6)
    a.lean(32, 0)
    a.jump(32, 33.4, a.x, LI[0], 3, arms=dict(arm1=170, arm2=-170))
    a.lean(34.4, 0)
    a.lean(35.4, -90)                                   # faints backwards
    a.face(35.4, "dizzy")
    a.emote(35.8, 41.4, "hearts", at=(34 * a.s, -12))   # from where its head lies
    a.lean(41.6, -90)
    a.lean(43, 0)
    a.face(43, "normal")

    # --- B follows along the same gap, hops down to the Toona line, then down to Legion.
    # It crouches to inspect things, which keeps its head under the line of text above.
    b.walk(20.6, 27.6, spans["vc"][1] + 40)
    b.jump(28, 29.6, ends[2] + 13, LI[2], 8)
    b.lean(30, 16)
    b.crouch(30.8, CROUCH)
    b.face(30.8, "cash")                               # "VC backed"
    b.emote(30.8, 33.6, "cash")
    lit["vc"] = (30.8, 4.8)
    b.face(33.8, "shock")                              # "100k users"
    b.emote(33.8, 35.8, "!!")
    b.crouch(36, 1)
    b.lean(36, 0)
    b.face(36, "normal")
    b.walk(36.2, 38.6, spans["toona"][1] + 13)
    b.crouch(39, CROUCH)
    b.lean(39, 16)
    b.face(39.2, "stars")
    b.emote(39.2, 43, "sparkles")
    lit["toona"] = (39.4, 3.4)
    b.crouch(43.2, 1)
    b.lean(43.2, 0)
    b.face(43.2, "normal")
    b.turn(43.4, 1)
    b.jump(43.8, 45.6, spans["legion"][1] + 13, LI[3], 10)
    b.turn(45.8, -1)
    b.lean(46.2, 10)
    b.crouch(46.8, CROUCH)
    b.face(46.8, "happy")
    b.emote(46.8, 50, "GG")
    b.clap(47, 49.4)
    lit["legion"] = (47, 3.2)
    b.crouch(50.2, 1)
    b.lean(50.2, 0)
    b.face(50.2, "normal")

    # --- Both meet at "2027", grab it, and pull it out to STRETCH times its size.
    y0, y1 = spans["y2027"]
    big_end = y0 + (y1 - y0) * STRETCH
    b.turn(50.4, 1)
    b.jump(50.6, 52, y1 + 7, LI[4], 8)
    b.turn(52.2, -1)
    a.turn(43.4, 1)
    a.walk(43.6, 48, ends[1] + 20)
    a.jump(48.4, 51.4, y1 + 23, LI[4], 10)
    a.turn(51.6, -1)
    for actor in (a, b):
        actor.crouch(53.2, CROUCH)
        actor.emote(53.3, 54.8, "!")
    b.set(53.6, arm1=40)
    a.set(53.6, arm1=80, arm2=70)
    pull0, pull1 = 54.4, 61.4
    for actor, gap in ((b, 5), (a, 21)):
        actor.face(pull0, "strain")
        actor.walk(pull0, pull1, big_end + gap, arms=False)
        actor.lean(pull0 + 1, -14)
        actor.emote(pull0 + 1.2, pull1, "sweat")
    b.set(pull1, arm1=100)

    # Let go, walk out past the end of line four (nothing above them there), look back, celebrate.
    right = ends[3] + 30
    for actor in (a, b):
        actor.crouch(pull1 + .4, 1)
        actor.lean(pull1 + .4, 0)
        actor.face(pull1 + .4, "happy")
        actor.set(pull1 + .4, arm1=STAND["arm1"], arm2=STAND["arm2"])
        actor.turn(pull1 + .8, 1)
    b.walk(62.4, 66.2, right)
    a.walk(62.4, 66.6, right + 22)
    for actor in (a, b):
        actor.turn(67, -1)
        actor.jump(67.4, 69, actor.x, LI[4], 12, arms=dict(arm1=170, arm2=-170))
    b.emote(67.4, 70.4, "!!")
    a.emote(67.4, 71.6, "hearts")
    # High five, then wander off.
    b.turn(70.6, 1)
    for actor in (a, b):
        actor.hold(71)
        actor.set(71.7, arm1=150)
        actor.hold(72.6)
        actor.set(73.3, arm1=STAND["arm1"])
    five = ((a.x + b.x) / 2, LI[4] - 33)
    a.turn(73.8, 1)
    a.face(73.8, "normal")
    b.face(73.8, "normal")
    a.walk(74.2, 80, W + 60)
    b.walk(74.6, 82, W + 40)

    # --- Each word lights up while it's being admired.
    word_line = {seg[2]: k for k, line in enumerate(BULLETS) for seg in line if len(seg) > 2}
    for key, (t, hold) in lit.items():
        off, on = f"transform: scale(1); fill: {c['fg']}", f"fill: {c['spark']}"
        anim.add(key, [(0, off), (t, off), (t + .4, f"transform: scale(1.08); {on}"),
                       (t + 1.2, f"transform: scale(1); {on}"), (t + hold, on), (t + hold + .8, off), (100, off)],
                 origin=(mid(key), LI[word_line[key]] - 5))

    grow = [(0, "transform: scale(1, 1)"), (pull0, "transform: scale(1, 1); animation-timing-function: linear"),
            (pull1, f"transform: scale({STRETCH}, {STRETCH})"), (pull1 + .5, f"transform: scale({STRETCH * 1.06}, {STRETCH * .94})"),
            (pull1 + 1.2, f"transform: scale({STRETCH}, {STRETCH})"), (86, f"transform: scale({STRETCH}, {STRETCH})"),
            (87, "transform: scale(.82, .82)"), (87.8, "transform: scale(1.12, 1.12)"),
            (88.5, "transform: scale(.96, .96)"), (89.2, "transform: scale(1, 1)"), (100, "transform: scale(1, 1)")]
    anim.add("y2027", grow, origin=(y0, LI[4] - 5.6))
    sparkle_box = [(y0 - 8, LI[4] - 26), (big_end + 6, LI[4] - 24), (y0 + 30, LI[4] + 14), (big_end - 12, LI[4] + 13)]
    stars = []
    for k, center in enumerate(sparkle_box):
        twinkle(anim, f"big{k}", pull1 + 1, 85, center, every=1.8, phase=k * .45)
        stars.append(f'<g class="big{k}">{star(*center, 5, c["spark"])}</g>')
    anim.add("five", [(0, "transform: scale(0); opacity: 0"), (71.8, "transform: scale(0); opacity: 0"),
                      (72, "transform: scale(.5); opacity: 1"), (73.2, "transform: scale(1.6); opacity: 0"),
                      (100, "transform: scale(1.6); opacity: 0")], origin=five, timing="ease-out")
    rays = "".join(
        f'<line x1="{fmt(five[0] + 4 * math.cos(r))}" y1="{fmt(five[1] + 4 * math.sin(r))}" '
        f'x2="{fmt(five[0] + 10 * math.cos(r))}" y2="{fmt(five[1] + 10 * math.sin(r))}"/>'
        for r in (math.radians(d) for d in range(0, 360, 45)))

    figures = a.render(anim, c) + b.render(anim, c)
    alt = ("Hi, I'm Justin Lau. " + "; ".join("".join(s[0] for s in line) for line in BULLETS) + ". " + CLOSER
           + " (Two stick figures wander into the README, gasp at each job, faint at LiveKit, "
             "and stretch 2027 until it's huge.)")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {fmt(HEIGHT)}" width="{W}" height="{fmt(HEIGHT)}" font-family="{escape(FONT)}" role="img" aria-label="{escape(alt)}">
  <style>
    * {{ transform-box: view-box; }}
    {chr(10).join("    " + rule for rule in anim.css).strip()}
    .a-prop {{ transform-origin: 0px -43.4px; animation: prop .45s linear infinite; }}
    @keyframes prop {{ 0%, 100% {{ transform: scaleX(1) }} 50% {{ transform: scaleX(-1) }} }}
  </style>
  {heading}
  <line x1="0" y1="{fmt(RULE + .5)}" x2="{W}" y2="{fmt(RULE + .5)}" stroke="{c["border"]}" stroke-width="1"/>
  {"".join(lines)}
  {closer}
  {"".join(stars)}
  {figures}
  <g class="five" stroke="{c["spark"]}" stroke-width="2.2" stroke-linecap="round">{rays}</g>
</svg>
"""


def main():
    ASSETS.mkdir(exist_ok=True)
    for theme, colors in THEMES.items():
        path = ASSETS / f"readme-{theme}.svg"
        path.write_text(build(colors))
        print(f"wrote {path.relative_to(ASSETS.parent)}")


if __name__ == "__main__":
    main()
