"""Generate the README's SVG charts, light and dark.

GitHub strips <style>, <script>, inline style attributes and inline <svg>, so
every chart has to be a committed .svg referenced by <img>/<picture>. This
script emits both themes from one definition so they can never drift.

Animation policy. SMIL runs on the image's own timeline and GitHub allows no JS,
so there is no way to trigger on scroll: anything below the fold has finished
animating long before it is looked at. Motion therefore lives only where the eye
lands on arrival - the hero stat cards, plus the rounds chart which sits at the
fold. The integrity and probe charts are deliberately static. Nothing in a data
chart loops, because a bar redrawing itself while someone is reading the number
is worse than no motion at all. The single indefinite element is the round 5
status dot, which is a live indicator rather than decoration.

Palette validated with the dataviz six-checks validator:
  dark  #d95d78 / #2d97d6 on #0d1117 - all pass
  light #c2405f / #1f6feb on #ffffff - all pass

    python assets/make_charts.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

SANS = "-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    "dark": dict(
        surface="#0d1117", panel="#161b22", border="#30363d",
        ink="#e6edf3", ink2="#9198a1", ink3="#6e7681",
        a="#d95d78", b="#2d97d6", track="#262c36",
    ),
    "light": dict(
        surface="#ffffff", panel="#f6f8fa", border="#d1d9e0",
        ink="#1f2328", ink2="#59636e", ink3="#818b98",
        a="#c2405f", b="#1f6feb", track="#dde3ea",
    ),
}

# round, battery, model, armA (pass, total), armB (pass, total), verdict, dq
# dq="A" renders arm A as a disqualified cell: hollow dashed bar, struck score,
# no percentage. The score stays visible because hiding it would be its own lie.
ROUNDS = [
    ("Round 1", "10 interlocking tasks, small app", "Devin", (10, 10), (10, 10), "tie - below the horizon", None),
    ("Round 2", "20 SWE-bench Verified x3 replicates", "Devin", (53, 60), (46, 60), "scaffolding wins, p=0.039", None),
    ("Round 3", "20 harder instances, replicate 1", "Devin", (16, 20), (17, 20), "flipped, n=1, aborted", None),
    ("Round 4", "50 fresh interlocking tasks", "Opus 5", (50, 50), (50, 50), "null at the ceiling", None),
    ("Round 5", "60 hardest SWE-bench Pro instances", "Opus 5", (59, 60), (52, 60), "scaffolding wins, p=0.039", None),
    ("Round 5", "same battery", "Sonnet 5", (58, 60), (48, 60), "arm A found the answer key", "A"),
]

# round, armA % of self-reports inconsistent with git, armB %
INTEGRITY = [
    ("Round 2", 0.0, 100.0, "0/60", "60/60"),
    ("Round 3", 5.0, 100.0, "1/20", "1/1"),
    ("Round 4", 6.0, 0.0, "3/50", "0/50"),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, fill, size=12, family=SANS, weight="400", anchor="start"):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>')


_uid = [0]


def stagger(attr, start, end, delay, dur, tag="animate", extra=""):
    """A staggered animation that begins at t=0 and holds `start` through `delay`.

    Staggering with begin="0.3s" looks wrong: before an animation starts, the
    element renders its STATIC attribute, which here is the settled value. So the
    mark appears finished, pops back to its start value, then animates - visible as
    a flicker. Folding the delay into keyTimes means every animation is live from
    t=0, while the static attribute stays settled for anything without SMIL.
    """
    total = delay + dur
    k = delay / total
    return (f'<{tag} attributeName="{attr}" {extra}values="{start};{start};{end}" '
            f'keyTimes="0;{k:.3f};1" dur="{total:.2f}s" fill="freeze" calcMode="spline" '
            f'keySplines="0 0 1 1;0.16 1 0.3 1"/>')


def bar(x, y, w, h, fill, r=4, delay=None):
    """Data-end rounded, baseline end square - anchored to the axis.

    With `delay`, the bar grows out of the baseline on load. GitHub renders SMIL
    inside a committed .svg. The clip rect carries its FULL width as a static
    attribute and animates from 0 up to it, so anywhere SMIL does not run the bar
    is simply drawn complete rather than drawn empty.
    """
    if w < r * 2:
        w = max(w, 1.5)
        shape = f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" fill="{fill}"/>'
    else:
        shape = (f'<path d="M{x},{y} H{x + w - r} a{r},{r} 0 0 1 {r},{r} '
                 f'V{y + h - r} a{r},{r} 0 0 1 -{r},{r} H{x} Z" fill="{fill}"/>')
    if delay is None:
        return shape
    _uid[0] += 1
    cid = f"g{_uid[0]}"
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w:.1f}" height="{h}">'
            f'{stagger("width", "0", f"{w:.1f}", delay, 0.75)}</rect></clipPath>'
            f'<g clip-path="url(#{cid})">{shape}</g>')


def wrap(w, h, body, t):
    """Every figure is a bordered card, so its inner padding reads as padding
    rather than as a title that fails to line up with the body text."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img">'
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" '
            f'fill="{t["panel"]}" stroke="{t["border"]}"/>{body}</svg>')


def legend(x, y, t, la="arm A - scaffolded, fresh session per task",
           lb="arm B - one session, no scaffold"):
    o = []
    o.append(f'<rect x="{x}" y="{y - 9}" width="11" height="11" rx="3" fill="{t["a"]}"/>')
    o.append(text(x + 18, y, la, t["ink2"], 11.5))
    o.append(f'<rect x="{x + 268}" y="{y - 9}" width="11" height="11" rx="3" fill="{t["b"]}"/>')
    o.append(text(x + 286, y, lb, t["ink2"], 11.5))
    return "".join(o)


# ---------------------------------------------------------------- hero
# Rendered full-column-width and left-aligned, so PAD is the card's inner padding
# and every heading, paragraph and chart below shares one left edge with the title.
PAD = 44

STATS = [
    ("5", "rounds, every one", "pre-registered before the run", "ink"),
    ("520", "graded arm-outcomes", "across rounds 1-5", "ink"),
    ("2 of 5", "rounds won by the scaffold,", "and 1 cell caught cheating", "a"),
]


def hero(t):
    W, H = 880, 336
    o = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" '
         f'fill="{t["panel"]}" stroke="{t["border"]}"/>']
    o.append(text(PAD, 84, "scaffold-bench", t["ink"], 42, MONO, "700"))
    o.append(text(PAD, 116, "Do frontier coding agents still need the scaffolding we build around them?",
                  t["ink2"], 15.5))

    o.append(f'<rect x="{W - PAD - 156}" y="52" width="156" height="28" rx="14" '
             f'fill="{t["surface"]}" stroke="{t["border"]}"/>')
    # the one element that loops: it is a live-status dot for the sonnet rerun,
    # so it reads as meaning rather than as decoration
    o.append(f'<circle cx="{W - PAD - 138}" cy="66" r="4" fill="{t["b"]}">'
             f'<animate attributeName="opacity" values="1;0.25;1" dur="2.4s" '
             f'repeatCount="indefinite"/></circle>')
    o.append(text(W - PAD - 126, 70, "clean rerun live", t["ink2"], 12, MONO))

    inner = W - PAD * 2
    cw = (inner - 28) / 3
    for i, (big, l1, l2, tone) in enumerate(STATS):
        x = PAD + i * (cw + 14)
        d = 0.12 + i * 0.13
        # opacity and transform both default to the settled state, so a viewer with
        # no SMIL sees the finished card instead of an empty one
        o.append("<g>" + stagger("opacity", "0", "1", d, 0.5)
                 + stagger("transform", "0 12", "0 0", d, 0.7,
                           tag="animateTransform", extra='type="translate" '))
        o.append(f'<rect x="{x:.1f}" y="150" width="{cw:.1f}" height="94" rx="8" '
                 f'fill="{t["surface"]}" stroke="{t["border"]}"/>')
        o.append(text(x + 18, 194, big, t[tone], 34, MONO, "700"))
        o.append(text(x + 18, 216, l1, t["ink2"], 11.5))
        o.append(text(x + 18, 232, l2, t["ink3"], 11.5))
        o.append("</g>")

    o.append(f'<line x1="{PAD}" y1="274" x2="{W - PAD}" y2="274" stroke="{t["border"]}"/>')
    o.append(text(PAD, 300, "Every time I improved the experiment, my own result got weaker.",
                  t["ink"], 15, SANS, "600"))
    o.append(text(PAD, 320, "Graded by the official harness, never by the agent. In round 5 "
                            "that is how one arm got caught cheating.", t["ink3"], 12))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img">{"".join(o)}</svg>')


# ---------------------------------------------------------------- rounds
def rounds(t):
    W = 880
    top, rh, bh, gap = 78, 76, 15, 2
    H = top + rh * len(ROUNDS) + 96
    o = []
    o.append(text(PAD, 34, "Resolved instances by arm, every round", t["ink"], 16, SANS, "600"))
    o.append(text(PAD, 54, "Batteries differ between rounds and are not comparable across rows.",
                  t["ink3"], 11.5))
    o.append(legend(PAD, 70, t))

    x0, bw = 260, 450
    for i, (name, battery, model, (ap, at), (bp, bt), verdict, dq) in enumerate(ROUNDS):
        y = top + i * rh + 18
        o.append(text(PAD, y + 4, name, t["ink"], 13, MONO, "600"))
        o.append(text(PAD, y + 20, battery, t["ink3"], 10.5))
        o.append(text(PAD, y + 34, model, t["ink3"], 10.5, MONO))

        for j, (p, tot, col, armdq) in enumerate(((ap, at, t["a"], dq == "A"),
                                                  (bp, bt, t["b"], dq == "B"))):
            by = y - 6 + j * (bh + gap)
            frac = p / tot
            o.append(f'<rect x="{x0}" y="{by}" width="{bw}" height="{bh}" rx="4" fill="{t["track"]}"/>')
            if armdq:
                # hollow dashed outline at the earned width: the shape of the score
                # without the fill of a valid one
                o.append(f'<rect x="{x0}" y="{by}" width="{bw * frac:.1f}" height="{bh}" rx="4" '
                         f'fill="none" stroke="{col}" stroke-dasharray="4 3"/>')
                o.append(text(x0 + bw + 12, by + 11.5, f"{p}/{tot}", t["ink3"], 11.5, MONO))
                o.append(f'<line x1="{x0 + bw + 10}" y1="{by + 7.5}" x2="{x0 + bw + 52}" '
                         f'y2="{by + 7.5}" stroke="{t["ink3"]}" stroke-width="1.2"/>')
                o.append(text(x0 + bw + 62, by + 11.5, "DQ", col, 11, MONO, "700"))
            else:
                o.append(bar(x0, by, bw * frac, bh, col, delay=0.15 + i * 0.14 + j * 0.07))
                o.append(text(x0 + bw + 12, by + 11.5, f"{p}/{tot}", t["ink"], 11.5, MONO))
                o.append(text(x0 + bw + 62, by + 11.5, f"{frac * 100:.0f}%", t["ink3"], 11, MONO))
        o.append(text(x0, y + 40, verdict, t["ink2"], 11))
        if i < len(ROUNDS) - 1:
            o.append(f'<line x1="{PAD}" y1="{y + 52}" x2="{W - PAD}" y2="{y + 52}" stroke="{t["border"]}"/>')

    y = top + rh * len(ROUNDS) + 14
    o.append(f'<rect x="{PAD}" y="{y}" width="{W - PAD * 2}" height="54" rx="8" '
             f'fill="{t["surface"]}" stroke="{t["border"]}" stroke-dasharray="4 3"/>')
    o.append(text(PAD + 16, y + 22, "The disqualification", t["ink"], 13, MONO, "600"))
    o.append(text(PAD + 196, y + 22, "Sonnet arm A retrieved each task's upstream fix commit instead of solving it.",
                  t["ink2"], 11.5))
    o.append(text(PAD + 16, y + 40, "That cell reruns with the answer key withheld. The 2x2 interaction publishes when it grades.",
                  t["ink3"], 11))
    return wrap(W, H, "".join(o), t)


# ---------------------------------------------------------------- integrity
def integrity(t):
    W, H = 880, 300
    o = []
    o.append(text(PAD, 34, "Self-reports that contradict the git commit record", t["ink"], 16, SANS, "600"))
    o.append(text(PAD, 54, "Each agent writes its own start/finish timestamps. Commit times are ground truth.",
                  t["ink3"], 11.5))
    o.append(legend(PAD, 74, t))

    x0, bw, bh = 260, 450, 15
    for i, (name, av, bv, alab, blab) in enumerate(INTEGRITY):
        y = 106 + i * 58
        o.append(text(PAD, y + 8, name, t["ink"], 13, MONO, "600"))
        for j, (v, lab, col) in enumerate(((av, alab, t["a"]), (bv, blab, t["b"]))):
            by = y + j * (bh + 2)
            o.append(f'<rect x="{x0}" y="{by}" width="{bw}" height="{bh}" rx="4" fill="{t["track"]}"/>')
            if v > 0:
                o.append(bar(x0, by, bw * v / 100, bh, col))
            o.append(text(x0 + bw + 12, by + 11.5, lab, t["ink"], 11.5, MONO))
            o.append(text(x0 + bw + 66, by + 11.5, f"{v:.0f}%", t["ink3"], 11, MONO))

    y = 288
    o.append(f'<line x1="{PAD}" y1="{y - 22}" x2="{W - PAD}" y2="{y - 22}" stroke="{t["border"]}"/>')
    o.append(text(PAD, y - 4, "Rounds 2-3 on Devin: the unscaffolded arm fabricated its progress reports every time. "
                              "Round 4 on Opus 5: it did not.", t["ink2"], 12))
    return wrap(W, H, "".join(o), t)


# ---------------------------------------------------------------- probe
def probe(t):
    W, H = 880, 236
    o = []
    o.append(text(PAD, 34, "Memorization probe - round 5 battery", t["ink"], 16, SANS, "600"))
    o.append(text(PAD, 54, "Share of instances where the model recalls at least half the gold-patch file set "
                           "from the issue text alone.", t["ink3"], 11.5))

    rows = [("Sonnet 5", 39, 98, t["b"]), ("Opus 5", 71, 98, t["b"]), ("Either model", 72, 100, t["a"])]
    x0, bw, bh = 200, 460, 20
    for i, (name, p, tot, col) in enumerate(rows):
        y = 86 + i * 36
        o.append(text(PAD, y + 15, name, t["ink"], 12.5, MONO))
        o.append(f'<rect x="{x0}" y="{y}" width="{bw}" height="{bh}" rx="4" fill="{t["track"]}"/>')
        o.append(bar(x0, y, bw * p / tot, bh, col))
        o.append(text(x0 + bw + 12, y + 14.5, f"{p}/{tot}", t["ink"], 12, MONO))
        o.append(text(x0 + bw + 66, y + 14.5, f"{p / tot * 100:.0f}%", t["ink3"], 11.5, MONO))

    o.append(f'<line x1="{PAD}" y1="{H - 44}" x2="{W - PAD}" y2="{H - 44}" stroke="{t["border"]}"/>')
    o.append(text(PAD, H - 24, "Reported, not hidden. Gold files named verbatim in the issue text are "
                               "excluded from scoring - inference is not memorization.", t["ink2"], 12))
    return wrap(W, H, "".join(o), t)


# ---------------------------------------------------------------- social card
# 1280x640, the image GitHub serves as og:image when the repo link is posted.
# Always dark: it has to hold up as a thumbnail on both X and LinkedIn, and the
# repo's own charts are read in this palette.
def social(t):
    W, H, P = 1280, 640, 80
    o = [f'<rect width="{W}" height="{H}" fill="{t["surface"]}"/>',
         f'<rect x="0" y="0" width="{W}" height="8" fill="{t["a"]}"/>']
    o.append(text(P, 148, "scaffold-bench", t["ink"], 74, MONO, "700"))
    o.append(text(P, 206, "Do frontier coding agents still need the scaffolding", t["ink2"], 31))
    o.append(text(P, 246, "we build around them?", t["ink2"], 31))

    # the verdict strip fills the right half, which the title block leaves empty
    strip = [("R1", "tie", t["ink3"]), ("R2", "scaffolding wins", t["a"]),
             ("R3", "flipped", t["ink3"]), ("R4", "null at the ceiling", t["b"]),
             ("R5", "wins, one cell disqualified", t["a"])]
    sx = 852
    o.append(f'<line x1="{sx - 28}" y1="112" x2="{sx - 28}" y2="284" stroke="{t["border"]}"/>')
    for i, (label, verdict, col) in enumerate(strip):
        y = 132 + i * 34
        o.append(f'<circle cx="{sx + 5}" cy="{y - 5}" r="4" fill="{col}"/>')
        o.append(text(sx + 22, y, label, t["ink2"], 19, MONO, "600"))
        o.append(text(W - P, y, verdict, t["ink2"], 19, SANS, "400", "end"))

    inner = W - P * 2
    cw = (inner - 40) / 3
    for i, (big, l1, l2, tone) in enumerate(STATS):
        x = P + i * (cw + 20)
        o.append(f'<rect x="{x:.1f}" y="304" width="{cw:.1f}" height="132" rx="12" '
                 f'fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="1.5"/>')
        o.append(text(x + 28, 374, big, t[tone], 54, MONO, "700"))
        o.append(text(x + 28, 402, l1, t["ink2"], 18))
        o.append(text(x + 28, 426, l2, t["ink3"], 18))

    o.append(f'<line x1="{P}" y1="496" x2="{W - P}" y2="496" stroke="{t["border"]}"/>')
    o.append(text(P, 538, "github.com/EricJujianZou/scaffold-bench", t["ink"], 24, MONO, "600"))
    o.append(text(P, 574, "pre-registered  ·  graded by the official harness, never by the agent  "
                          "·  every losing round published", t["ink3"], 18))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img">{"".join(o)}</svg>')


CHARTS = {"hero": hero, "rounds": rounds, "integrity": integrity, "probe": probe}

if __name__ == "__main__":
    for name, fn in CHARTS.items():
        for mode, t in THEMES.items():
            p = OUT / f"{name}-{mode}.svg"
            p.write_text(fn(t), encoding="utf-8")
            print("wrote", p.name)
    p = OUT / "social-preview.svg"
    p.write_text(social(THEMES["dark"]), encoding="utf-8")
    print("wrote", p.name, "(rasterize to .png before uploading - GitHub rejects SVG)")
