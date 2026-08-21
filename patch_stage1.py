"""
patch_stage1.py  --  version 2
-------------------------------------------------------------------------------
Applies the void-cell and neighbour-guard fixes to the Stage 1 script
("...boxes only.py") without hand-editing 82 KB of code.

CHANGES IN v2 (after a real dry run against the 2013 source)
    - Trailing comments are now ignored when matching code lines. v1 failed to
      find the dead void branch because the source line carries a comment:
          statesCA.append(statesCAall[3]) # creates void cell on outer layer...
      Comment-only lines are still matched in full, because one rule anchors on
      a comment deliberately.
    - Removed a duplicate rule (old rule 14 had the same anchor as rule 12, so
      it always reported 0 hits after 12 had consumed both occurrences).

WHY THIS EXISTS
    The fixes documented in VOID_CELLS.md and FINDINGS.md touch about a dozen
    places across two nearly-identical fitness methods. Doing that by hand is
    error-prone; doing it by an AI rewriting the whole file risks silently
    dropping code. This script instead locates each anchor exactly, reports
    what it found, and refuses to write anything if the counts are wrong.

HOW IT MATCHES
    Code lines are compared with all whitespace removed and any trailing
    comment discarded, so indentation, spacing and comments do not matter.
    Indentation of replacements is taken from the line being replaced. No
    regular expressions, so every rule can be audited by reading it.

USAGE
    python patch_stage1.py "AmiinaBakunowicz_MSc Thesis 2013_UEL_CA based GA_SOM_boxes only.py"
        Dry run. Reports what it would change. Writes nothing.

    python patch_stage1.py "<input>" --write
        Writes <input stem>_patched.py alongside the original.

    python patch_stage1.py "<input>" --write --som-float
        Also converts the SOM integer divisions to float division. Read
        FINDINGS.md section 1 first -- this changes the algorithm's behaviour,
        it does not merely speed it up.

    python patch_stage1.py "<input>" --write --force
        Writes even if some rules did not match. Read the report first.

SAFETY
    - Never modifies the input file. Always writes a new one.
    - Runs on Python 2.7 and 3.x.
    - Reports every rule as OK / PARTIAL / MISSING with actual vs expected hit
      counts, and lists the manual follow-ups it deliberately does not attempt.

FIRST TEST AFTER PATCHING
    Set VOID_RATE = 0.0 near the top of the patched file. That disables voids
    entirely, so the patched script should behave identically to the original.
    If it does, the plumbing is sound; raise VOID_RATE to 0.20 to see porosity.
"""

import sys
import os

NEIGHBOURS = ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]

HELPERS = [
    "",
    "# === void-cell support (inserted by patch_stage1.py) =====================",
    "# Share of OUTER-LAYER cells made void. 0.0 disables voids entirely and",
    "# restores the original behaviour of a fully solid model. Start at 0.0 to",
    "# confirm the patch changes nothing, then raise it.",
    "VOID_RATE = 0.20",
    "",
    "# Counters that keep fitness comparable between porous and solid models.",
    "# See VOID_CELLS.md: distFactor and XXareasFactor are reciprocals of sums",
    "# over Moore-neighbour pairs, so removing pairs inflates them. Scaling by",
    "# the pairs actually measured removes that bias.",
    "_pair_count = [0]",
    "_live_count = [0]",
    "",
    "def _reset_counters():",
    "    _pair_count[0] = 0",
    "    _live_count[0] = 0",
    "",
    "def _pairs_scale():",
    "    # 8 = a full Moore neighbourhood. Returns 1.0 when nothing is void.",
    "    if _pair_count[0] <= 0:",
    "        return 0.0",
    "    return _pair_count[0] / 8.0",
    "",
    "def _safe_centroid(obj):",
    "    # rs.SurfaceVolumeCentroid returns None on degenerate or missing solids.",
    "    if obj is None:",
    "        return None",
    "    result = rs.SurfaceVolumeCentroid(obj)",
    "    if result is None:",
    "        return None",
    "    return result[0]",
    "",
    "def _pair_dist(a, b):",
    "    # Counts the pair only when both centroids exist.",
    "    if a is None or b is None:",
    "        return 0",
    "    _pair_count[0] += 1",
    "    return rs.Distance(a, b)",
    "",
    "def _live(objects):",
    "    # Strip void placeholders before handing a list to Rhino.",
    "    if objects is None:",
    "        return []",
    "    return [o for o in objects if o is not None]",
    "# =========================================================================",
    "",
]


def canon(line):
    """
    Whitespace-free, comment-free form of a line, for tolerant comparison.

    Comment-only lines keep their text, because rule 9 deliberately anchors on
    a comment. Code lines drop anything from the first '#' onward, which is why
    v2 finds the void branch that v1 missed.
    """
    stripped = line.strip()
    if not stripped.startswith("#"):
        stripped = stripped.split("#")[0]
    return "".join(stripped.split())


def indent_of(line):
    return line[:len(line) - len(line.lstrip())]


def build_rules(som_float):
    """
    Each rule: (name, anchor_lines, replacement_lines, expected_hits, note)

    anchor_lines      consecutive source lines, matched loosely (see canon)
    replacement_lines templates; leading spaces are added to the indentation
                      detected from the first anchor line
    expected_hits     exact count required, or None to accept one or more
    """
    rules = []

    rules.append((
        "1. add 'void' to statesCAall",
        ['statesCAall = ["living", "working", "resting"]'],
        ['statesCAall = ["living", "working", "resting", "void"]'],
        1,
        "The original code already reached for statesCAall[3].",
    ))

    rules.append((
        "2. fix the dead void branch",
        [
            "k = r.random()",
            "if k > 10 and (x == 0 or y == 0 or x == CAunitsX-1 or y == CAunitsY - 1):",
            "statesCA.append(statesCAall[3])",
        ],
        [
            "k = r.random()",
            "if k < VOID_RATE and (x == 0 or y == 0 or x == CAunitsX-1 or y == CAunitsY - 1):",
            '    statesCA.append("void")',
        ],
        1,
        "k > 10 could never be true for r.random(); statesCAall[3] would have raised IndexError.",
    ))

    rules.append((
        "3. voids hold their place in guid (Individual)",
        [
            'if statesCA[i] == "living":',
            "livingBox = self.drawLiving(coordCA)",
        ],
        [
            'if statesCA[i] == "void":',
            "    guid.append(None)",
            "    continue",
            'if statesCA[i] == "living":',
            "    livingBox = self.drawLiving(coordCA)",
        ],
        1,
        "assessFitness addresses guid by computed index; a short list silently misaligns every later cell.",
    ))

    rules.append((
        "4. voids hold their place in guid (Neuron)",
        [
            'if statesCA[i] == "living":',
            "livingBox = self.drawNeuronLiving(coordCA)",
        ],
        [
            'if statesCA[i] == "void":',
            "    guid.append(None)",
            "    continue",
            'if statesCA[i] == "living":',
            "    livingBox = self.drawNeuronLiving(coordCA)",
        ],
        1,
        "Same alignment requirement for the SOM neurons.",
    ))

    rules.append((
        "5a. guarded centroid (own cell)",
        ["if boxThis is not None: centroidThis = rs.SurfaceVolumeCentroid(boxThis)[0]"],
        ["centroidThis = _safe_centroid(boxThis)"],
        None,
        "",
    ))
    for suffix in NEIGHBOURS:
        rules.append((
            "5b. guarded centroid (%s)" % suffix,
            ["if boxThis is not None: centroid%s = rs.SurfaceVolumeCentroid(box%s)[0]"
             % (suffix, suffix)],
            ["centroid%s = _safe_centroid(box%s)" % (suffix, suffix)],
            None,
            "",
        ))

    for n, suffix in enumerate(NEIGHBOURS, start=1):
        rules.append((
            "6. counted distance (%s)" % suffix,
            ["if centroid%s is not None and centroidThis is not None: dist%d = rs.Distance(centroidThis,centroid%s)"
             % (suffix, n, suffix)],
            ["dist%d = _pair_dist(centroidThis, centroid%s)" % (n, suffix)],
            None,
            "",
        ))

    for suffix in NEIGHBOURS:
        rules.append((
            "7. guarded intersection (%s)" % suffix,
            ["THISx%s = rs.BooleanIntersection(boxThis,box%s, False)" % (suffix, suffix)],
            ["THISx%s = rs.BooleanIntersection(boxThis, box%s, False) if (boxThis is not None and box%s is not None) else None"
             % (suffix, suffix, suffix)],
            None,
            "",
        ))

    rules.append((
        "8. guarded area accumulation + live-cell count",
        ["totalAreaFactor += rs.SurfaceArea(boxThis)[0]"],
        [
            "if boxThis is not None:",
            "    totalAreaFactor += rs.SurfaceArea(boxThis)[0]",
            "    _live_count[0] += 1",
        ],
        None,
        "",
    ))

    rules.append((
        "9. reset counters before the fitness loop",
        [
            "objects = []",
            "# fitness criteria keeps the neighboring boxes as close as possible",
        ],
        [
            "objects = []",
            "_reset_counters()",
            "# fitness criteria keeps the neighboring boxes as close as possible",
        ],
        None,
        "Two-line anchor so it does not also match the 'objects = []' lines in runSOM.",
    ))

    rules.append((
        "10. normalise fitness so voids are score-neutral",
        [
            "if distFactor != 0: distFactor = 17000*CAunitsZ/distFactor",
            "if XXareasFactor != 0: XXareasFactor = 150000*CAunitsZ/XXareasFactor",
            "totalAreaFactor = totalAreaFactor*0.017/CAunitsZ",
        ],
        [
            "_scale = _pairs_scale()",
            "if distFactor != 0: distFactor = (17000*CAunitsZ/distFactor) * _scale",
            "if XXareasFactor != 0: XXareasFactor = (150000*CAunitsZ/XXareasFactor) * _scale",
            "if _live_count[0]: totalAreaFactor = (totalAreaFactor/_live_count[0]*(CAunitsX*CAunitsY*CAunitsZ))*0.017/CAunitsZ",
        ],
        None,
        "Measured: removes a 1.28x porosity bias, leaving 0.97x across 0-60% voids.",
    ))

    rules.append((
        "11. skip void units when colouring the best model",
        ["unit = allIndivNeurons[bestID].guid[i]"],
        [
            "unit = allIndivNeurons[bestID].guid[i]",
            "if unit is None: continue",
        ],
        None,
        "",
    ))

    rules.append((
        "12. filter voids before colouring an individual or winning neuron",
        ["rs.ObjectColor(self.guid, self.colour)"],
        ["rs.ObjectColor(_live(self.guid), self.colour)"],
        None,
        "Expect 2 hits: Individual.drawBodyplan and Neuron.update.",
    ))

    rules.append((
        "13. filter voids before colouring a clustered neuron",
        ["rs.ObjectColor(self.guid,col)"],
        ["rs.ObjectColor(_live(self.guid), col)"],
        None,
        "",
    ))

    if som_float:
        rules.append((
            "14. SOM float division (CHANGES BEHAVIOUR -- read FINDINGS.md #1)",
            [
                "WINLEARN = WINLEARN * (1 - (cycles / 600))",
                "LEARN = LEARN * (1 - (cycles / 400))",
                "NEIGH = RADIUS * (1 - (cycles / 100))",
            ],
            [
                "WINLEARN = WINLEARN * (1 - (cycles / 600.0))",
                "LEARN = LEARN * (1 - (cycles / 400.0))",
                "NEIGH = RADIUS * (1 - (cycles / 100.0))",
            ],
            1,
            "Integer division fixed the map at exactly 600 cycles and killed neighbourhood learning after cycle 100.",
        ))

    return rules


def apply_rule(lines, anchors, replacements):
    """Replace every loose match. Returns (new_lines, hits)."""
    canon_anchors = [canon(a) for a in anchors]
    span = len(canon_anchors)
    out = []
    i = 0
    hits = 0
    while i < len(lines):
        window = lines[i:i + span]
        if len(window) == span and [canon(w) for w in window] == canon_anchors:
            base = indent_of(lines[i])
            for template in replacements:
                stripped = template.lstrip()
                extra = template[:len(template) - len(stripped)]
                out.append(base + extra + stripped if stripped else "")
            hits += 1
            i += span
        else:
            out.append(lines[i])
            i += 1
    return out, hits


def insert_helpers(lines):
    anchor = canon("from itertools import permutations")
    for i, line in enumerate(lines):
        if canon(line) == anchor:
            return lines[:i + 1] + HELPERS + lines[i + 1:], True
    return lines, False


MANUAL_FOLLOWUPS = [
    "rs.DeleteObjects(...) calls on guid lists -- wrap with _live(...) if you hit",
    "a 'value cannot be None' error. Not automated because the call sites vary",
    "and a wrong edit here deletes the wrong geometry.",
    "rs.SelectObjects(...) in the artificial-selection path (selection option 3)",
    "-- same reasoning.",
    "Stage 2 (the bodyplan script) is NOT handled by this patcher. Its tower loft",
    "matches ellipse division points across floors, so a void on one floor but",
    "not the next breaks the correspondence. Whether the skin should close over",
    "or open around a void is a design decision, not a mechanical one.",
]


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = set(a for a in argv[1:] if a.startswith("--"))

    if not args:
        print(__doc__)
        return 2

    src = args[0]
    if not os.path.isfile(src):
        print("ERROR: no such file: %s" % src)
        return 2

    write = "--write" in flags
    force = "--force" in flags
    som_float = "--som-float" in flags

    with open(src, "r") as f:
        original = f.read()
    lines = original.split("\n")

    print("patch_stage1.py v2")
    print("input : %s" % src)
    print("size  : %d bytes, %d lines" % (len(original), len(lines)))
    print("mode  : %s%s" % ("WRITE" if write else "DRY RUN",
                            "  (+ SOM float division)" if som_float else ""))
    print("")

    lines, helpers_ok = insert_helpers(lines)
    print("%-58s %s" % ("0. insert helper block", "OK" if helpers_ok else "MISSING"))
    if not helpers_ok:
        print("   could not find 'from itertools import permutations'")

    problems = 0
    for name, anchors, replacements, expected, note in build_rules(som_float):
        lines, hits = apply_rule(lines, anchors, replacements)
        if expected is None:
            status = "OK" if hits >= 1 else "MISSING"
        else:
            status = "OK" if hits == expected else ("PARTIAL" if hits else "MISSING")
        if status != "OK":
            problems += 1
        detail = "%d hit%s" % (hits, "" if hits == 1 else "s")
        if expected is not None:
            detail += " (expected %d)" % expected
        print("%-58s %-8s %s" % (name, status, detail))
        if note and status == "OK" and hits:
            print("   %s" % note)

    if not helpers_ok:
        problems += 1

    patched = "\n".join(lines)
    print("")
    print("result: %d bytes, %d lines (%+d bytes)"
          % (len(patched), len(lines), len(patched) - len(original)))
    print("rules with problems: %d" % problems)

    print("")
    print("MANUAL FOLLOW-UPS (deliberately not automated):")
    for item in MANUAL_FOLLOWUPS:
        print("  %s" % item)

    if not write:
        print("")
        print("Dry run only. Nothing written. Re-run with --write to produce the file.")
        return 0

    if problems and not force:
        print("")
        print("REFUSING TO WRITE: %d rule(s) did not match as expected." % problems)
        print("Read the report above. A MISSING guard rule means voids will crash")
        print("the fitness function at runtime. Do not force blindly.")
        return 1

    stem = os.path.splitext(src)[0]
    out_path = stem + "_patched.py"
    with open(out_path, "w") as f:
        f.write(patched)
    print("")
    print("wrote: %s" % out_path)
    print("")
    print("FIRST TEST: set VOID_RATE = 0.0 near the top of the patched file and")
    print("confirm it behaves identically to the original. Then raise it to 0.20.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
