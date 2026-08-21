"""
blueprint_export.py
-------------------------------------------------------------------------------
Shared data contract between the two stages of the CA / GA / SOM pipeline.

    STAGE 1  "..._boxes-only.py"          evolves the BLUEPRINT of the form
    STAGE 2  "..._evolved-bodyplan..."    DRESSES a chosen blueprint

Stage 1 explores cheaply and evolves. Stage 2 details expensively, once, on a
blueprint you have already chosen. This module is the handoff: Stage 1 writes,
Stage 2 reads.

Original research and algorithm:
    Amiina Bakunowicz, MSc Thesis, University of East London, 2013

WHY statesCA MATTERS
    Both scripts currently generate statesCA randomly at the start of a run.
    That means a Stage 2 run today dresses a DIFFERENT building than whatever
    Stage 1 evolved. Carrying statesCA across is what connects the two stages.

DEPENDENCIES
    json, os, datetime only. No Rhino calls. Works under IronPython 2.7 and
    CPython 3.x.
"""

import json
import os
import datetime


EXPORT_DIR = "exports"
FORMAT_VERSION = 1


# ============================================================
# WRITING  (call from Stage 1)
# ============================================================

def save_blueprint(individual, statesCA, grid, path=None,
                   generation=None, components=None, note=""):
    """
    Serialise one evolved individual as a reusable blueprint.

    individual  needs .chromosome, .values, .fitness, .id, .colour.
                Geometry GUIDs are deliberately NOT saved -- they are
                meaningless outside the Rhino session that made them.
    statesCA    the flat list of CA cell states used for this run.
    grid        build it with grid_dict() below.
    components  optional fitness breakdown dict. Worth passing -- a total
                alone won't tell you WHY a blueprint won.
    note        free text. "client liked the twist at floor 14" beats any
                number here.

    Returns the path written.
    """
    if grid is None:
        raise ValueError("grid is required -- use grid_dict() to build it")

    fitness = float(getattr(individual, "fitness", 0) or 0)
    ident = getattr(individual, "id", 0)

    payload = {
        "format_version": FORMAT_VERSION,
        "meta": {
            "saved": datetime.datetime.now().isoformat(),
            "generation": generation,
            "individual_id": ident,
            "colour": _plain_list(getattr(individual, "colour", None)),
            "note": note,
            "source": "stage1_evolve_blueprint",
        },
        "grid": dict(grid),
        "genotype": {
            "chromosome": _plain_list(individual.chromosome),
            "values": _plain_list(individual.values),
        },
        "statesCA": list(statesCA),
        "fitness": {
            "total": round(fitness, 2),
            "components": _plain_dict(components) if components else {},
        },
    }

    _validate(payload)

    if path is None:
        if not os.path.isdir(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)
        name = "blueprint_gen{}_id{}_fit{}.json".format(
            generation if generation is not None else "x",
            ident,
            int(round(fitness)))
        path = os.path.join(EXPORT_DIR, name)

    with open(path, "w") as f:
        json.dump(payload, f, indent=2)

    return path


def save_best_of_run(candidates, statesCA, grid, top=1,
                     generation=None, note=""):
    """
    Save the top N candidates from a finished run.

    Pass allIndivNeurons -- the list showBest() already ranks over, holding
    both GA individuals and fit SOM neurons converted to individuals, so
    SOM-born candidates are exportable too.

    Saving the top 5 rather than only rank 1 matches the thesis: "choosing
    the fittest ceases to be essential. A fit enough model that looks
    acceptable to the eye of the designer becomes the solution."

    Returns a list of paths written.
    """
    scored = [c for c in candidates if getattr(c, "fitness", 0)]
    scored.sort(key=lambda c: c.fitness, reverse=True)
    written = []
    for c in scored[:top]:
        written.append(save_blueprint(
            c, statesCA, grid, generation=generation, note=note))
    return written


# ============================================================
# READING  (call from Stage 2)
# ============================================================

def load_blueprint(path, expected_grid=None, strict=False):
    """
    Load a blueprint written by Stage 1.

    expected_grid  pass grid_dict() from the receiving script; any mismatch
                   is reported. Stops you silently dressing a 9-cell
                   blueprint with 384-cell geometry.
    strict         True raises on mismatch instead of warning.

    Read the result as:
        bp = load_blueprint("exports/blueprint_gen7_id2_fit412.json")
        values   = bp["genotype"]["values"]
        statesCA = bp["statesCA"]
    """
    with open(path, "r") as f:
        payload = json.load(f)

    _validate(payload)

    version = payload.get("format_version")
    if version != FORMAT_VERSION:
        print("[blueprint] note: file format v{}, module is v{}".format(
            version, FORMAT_VERSION))

    if expected_grid is not None:
        problems = compare_grids(payload["grid"], expected_grid)
        if problems:
            message = ("[blueprint] grid mismatch:\n  " +
                       "\n  ".join(problems))
            if strict:
                raise ValueError(message)
            print(message)
            print("[blueprint] see adapt_blueprint_to_grid() if intentional")

    return payload


def compare_grids(saved, expected):
    """Human-readable list of differences between two grid dicts."""
    problems = []
    for key in ("CAunitsX", "CAunitsY", "CAunitsZ", "widthCA", "FLOORHEIGHT"):
        a = saved.get(key)
        b = expected.get(key)
        if a is None or b is None:
            continue
        if a != b:
            problems.append("{}: blueprint {} vs script {}".format(key, a, b))
    return problems


def adapt_blueprint_to_grid(payload, target_grid, floor_mode="tile"):
    """
    Stretch a blueprint onto a different grid. Returns a NEW payload.

    THIS IS AN INTERPRETATION, NOT A CONVERSION. values[0..5] -- the three
    unit-type dimensions carrying most of the design intent -- are
    grid-independent and transfer cleanly. Per-cell offsets and statesCA are
    not, so they get repeated:

    floor_mode="tile"     repeat floors cyclically up the target height.
                          Predictable. Good default.
    floor_mode="stretch"  map each target floor proportionally onto the
                          nearest source floor. Preserves a vertical gesture
                          (taper, bulge) across a different floor count.

    X and Y must match -- widening the plan would mean inventing cells with
    no evolved basis. Run Stage 1 again at the target grid instead.
    """
    src = payload["grid"]
    if (src["CAunitsX"] != target_grid["CAunitsX"] or
            src["CAunitsY"] != target_grid["CAunitsY"]):
        raise ValueError(
            "cannot adapt across different plan grids "
            "({}x{} -> {}x{}). Run Stage 1 at the target grid.".format(
                src["CAunitsX"], src["CAunitsY"],
                target_grid["CAunitsX"], target_grid["CAunitsY"]))

    unitsPerFloor = src["CAunitsX"] * src["CAunitsY"]
    srcZ = src["CAunitsZ"]
    dstZ = target_grid["CAunitsZ"]

    srcStates = payload["statesCA"]
    newStates = []
    for z in range(dstZ):
        if floor_mode == "stretch" and dstZ > 1 and srcZ > 1:
            srcFloor = int(round(z * (srcZ - 1) / float(dstZ - 1)))
        else:
            srcFloor = z % srcZ
        start = srcFloor * unitsPerFloor
        newStates.extend(srcStates[start:start + unitsPerFloor])

    srcValues = payload["genotype"]["values"]
    header = srcValues[:6]
    offsets = srcValues[6:]
    newOffsets = []
    perFloorOffsets = unitsPerFloor * 2
    if offsets and perFloorOffsets:
        for z in range(dstZ):
            if floor_mode == "stretch" and dstZ > 1 and srcZ > 1:
                srcFloor = int(round(z * (srcZ - 1) / float(dstZ - 1)))
            else:
                srcFloor = z % srcZ
            start = srcFloor * perFloorOffsets
            chunk = offsets[start:start + perFloorOffsets]
            if len(chunk) < perFloorOffsets:
                chunk = chunk + [0] * (perFloorOffsets - len(chunk))
            newOffsets.extend(chunk)

    adapted = json.loads(json.dumps(payload))   # deep copy
    adapted["grid"] = dict(target_grid)
    adapted["statesCA"] = newStates
    adapted["genotype"]["values"] = header + newOffsets
    # The chromosome no longer matches the adapted values. Flag it rather
    # than fabricate a matching binary string.
    adapted["genotype"]["chromosome"] = []
    adapted["meta"]["adapted_from"] = {
        "grid": dict(src),
        "floor_mode": floor_mode,
        "chromosome_invalidated": True,
    }
    return adapted


# ============================================================
# HELPERS
# ============================================================

def grid_dict(CAunitsX, CAunitsY, CAunitsZ, widthCA, FLOORHEIGHT):
    """Build the grid dict from your script's globals, in this order."""
    return {
        "CAunitsX": CAunitsX,
        "CAunitsY": CAunitsY,
        "CAunitsZ": CAunitsZ,
        "widthCA": widthCA,
        "FLOORHEIGHT": FLOORHEIGHT,
    }


def list_blueprints(directory=EXPORT_DIR):
    """
    Inspect saved blueprints without opening Rhino. Returns dicts sorted by
    fitness, best first.
    """
    if not os.path.isdir(directory):
        return []
    rows = []
    for name in os.listdir(directory):
        if not name.endswith(".json"):
            continue
        full = os.path.join(directory, name)
        try:
            with open(full, "r") as f:
                p = json.load(f)
            g = p.get("grid", {})
            rows.append({
                "path": full,
                "fitness": p.get("fitness", {}).get("total", 0),
                "components": p.get("fitness", {}).get("components", {}),
                "generation": p.get("meta", {}).get("generation"),
                "grid": "{}x{}x{}".format(g.get("CAunitsX"),
                                          g.get("CAunitsY"),
                                          g.get("CAunitsZ")),
                "note": p.get("meta", {}).get("note", ""),
                "saved": p.get("meta", {}).get("saved", ""),
            })
        except (ValueError, IOError) as exc:
            print("[blueprint] skipping {}: {}".format(name, exc))
    rows.sort(key=lambda row: row["fitness"], reverse=True)
    return rows


def describe(payload):
    """One-line summary, for printing to the Rhino console."""
    g = payload.get("grid", {})
    meta = payload.get("meta", {})
    counts = {}
    for s in payload.get("statesCA", []):
        counts[s] = counts.get(s, 0) + 1
    mix = ", ".join("{} {}".format(v, k) for k, v in sorted(counts.items()))
    return "blueprint {}x{}x{} | gen {} | fitness {} | {} | {}".format(
        g.get("CAunitsX"), g.get("CAunitsY"), g.get("CAunitsZ"),
        meta.get("generation"),
        payload.get("fitness", {}).get("total"),
        mix,
        meta.get("note") or "no note")


def _validate(payload):
    """Fail loudly and early on a malformed blueprint."""
    for key in ("grid", "genotype", "statesCA"):
        if key not in payload:
            raise ValueError("blueprint missing '{}'".format(key))

    g = payload["grid"]
    for key in ("CAunitsX", "CAunitsY", "CAunitsZ"):
        if key not in g:
            raise ValueError("blueprint grid missing '{}'".format(key))

    expected = g["CAunitsX"] * g["CAunitsY"] * g["CAunitsZ"]
    actual = len(payload["statesCA"])
    if actual != expected:
        raise ValueError(
            "statesCA has {} entries but grid {}x{}x{} needs {}".format(
                actual, g["CAunitsX"], g["CAunitsY"],
                g["CAunitsZ"], expected))

    values = payload["genotype"].get("values") or []
    if len(values) < 6:
        raise ValueError(
            "blueprint needs at least 6 gene values (the three unit-type "
            "dimensions); found {}".format(len(values)))


def _plain_list(seq):
    """
    Coerce to JSON-safe numbers. Rhino/IronPython hands back Single, Int64
    and .NET colour types that json cannot serialise.
    """
    if seq is None:
        return None
    out = []
    for v in seq:
        try:
            f = float(v)
        except (TypeError, ValueError):
            out.append(str(v))
            continue
        out.append(int(f) if f == int(f) else round(f, 6))
    return out


def _plain_dict(d):
    out = {}
    for k, v in d.items():
        try:
            f = float(v)
            out[str(k)] = int(f) if f == int(f) else round(f, 6)
        except (TypeError, ValueError):
            out[str(k)] = str(v)
    return out