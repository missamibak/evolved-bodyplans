# Wiring the two stages together

Small, surgical edits to your two 2013 scripts so Stage 1's evolved blueprint
actually drives Stage 2's architectural detailing. Your existing logic is not
restructured — this adds an export at the end of Stage 1 and an import at the
start of Stage 2.

Place `blueprint_export.py` in the same folder as both scripts.

---

## The problem this fixes

Both scripts currently build `statesCA` themselves, near the top of `runGA()`:

```python
statesCA = []
for z in range (CAunitsZ):
    for y in range (CAunitsY):
        for x in range (CAunitsX):
            k = r.random()
            if k > 10 and (x == 0 or y == 0 or x == CAunitsX-1 or y == CAunitsY - 1):
                statesCA.append(statesCAall[3])
            else:
                s = r.randrange(0,3)
                statesCA.append(statesCAall[s])
```

So a Stage 2 run today dresses a **different random building** than whatever
Stage 1 evolved. The two scripts are similar but disconnected. Carrying the
genotype *and* `statesCA` across is what makes them one pipeline.

Incidentally, `statesCAall` has only three entries (indices 0–2), so the
`statesCAall[3]` branch would raise `IndexError` — it never fires because
`k > 10` can never be true for `r.random()`. Harmless dead code, but worth
knowing it was intended to create void cells on the outer layer and currently
does nothing.

---

## STAGE 1 — export the winners

### Edit 1 of 2: import at the top

After the existing imports:

```python
import rhinoscriptsyntax as rs
import random as r
import math as m
from itertools import permutations
import blueprint_export as bp          # <-- add
```

### Edit 2 of 2: save at the end of the run

In `runGA()`, the loop ends with the final-generation branch:

```python
                    if (g != GENERATIONS-1):
                        population = newPop[:]
                    else: EVOLUTION = False
```

Immediately **after** the `while(EVOLUTION == True)` loop finishes — at the same
indentation as the `bestPts` curve drawing near the end of `runGA()` — add:

```python
    # ---- export the best blueprints of this run ----
    grid = bp.grid_dict(CAunitsX, CAunitsY, CAunitsZ, widthCA, FLOORHEIGHT)
    written = bp.save_best_of_run(
        allIndivNeurons,
        statesCA,
        grid,
        top=5,
        generation=GENERATIONS,
        note="")
    for path in written:
        print "saved blueprint:", path
```

`allIndivNeurons` is the list your `showBest()` already ranks over, holding both
the GA individuals and the fit SOM neurons converted to individuals — so SOM-born
candidates are exportable too, which is the whole point of the map.

Saving the **top 5** rather than only the winner is deliberate, and matches your
own conclusion in the thesis: *"choosing the fittest ceases to be essential. A fit
enough model that looks acceptable to the eye of the designer becomes the
solution."* You pick by eye afterwards.

**Scope caveat:** `allIndivNeurons` and `statesCA` are local to `runGA()`, so
this must go inside `runGA()`, not in `main()`.

### Recording *why* a blueprint won

Optional but worth it. In `assessFitness()`, just before the threshold check,
stash the breakdown on the object:

```python
        self.components = {
            "distFactor": distFactor,
            "XXareasFactor": XXareasFactor,
            "totalAreaFactor": totalAreaFactor,
            "WRareaFactor": WRareaFactor,
            "RLareaFactor": RLareaFactor,
            "GSfactor": GSfactor,
        }
```

Then pass `components=getattr(c, "components", None)` through if you call
`save_blueprint` directly. A bare total of `412.7` won't tell you in six months
whether that blueprint won on proportion or on compactness.

---

## STAGE 2 — import a chosen blueprint

### Edit 1 of 3: import at the top

```python
import blueprint_export as bp
```

### Edit 2 of 3: pick the blueprint file

Alongside the existing `rs.GetInteger` prompts at the top:

```python
BLUEPRINT_PATH = rs.OpenFileName("Choose a blueprint to dress", "JSON (*.json)|*.json||")
```

Leaving the dialog cancelled returns `None`, which the next edit treats as
"behave exactly as before" — so the script stays usable standalone.

### Edit 3 of 3: use it instead of random genes

In `runGA()`, **replace** the `statesCA` generation block quoted above with:

```python
    BLUEPRINT = None
    if BLUEPRINT_PATH:
        grid = bp.grid_dict(CAunitsX, CAunitsY, CAunitsZ, widthCA, FLOORHEIGHT)
        BLUEPRINT = bp.load_blueprint(BLUEPRINT_PATH, expected_grid=grid)
        print bp.describe(BLUEPRINT)

    if BLUEPRINT:
        statesCA = BLUEPRINT["statesCA"]
    else:
        statesCA = []
        for z in range (CAunitsZ):
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    s = r.randrange(0,3)
                    statesCA.append(statesCAall[s])
```

Then, where the generation is drawn:

```python
                        for i in range(newPopcount):
                            population[i].decode()
                            population[i].drawBodyplan(i, g, finished, statesCA, BetwGens)
```

change to:

```python
                        for i in range(newPopcount):
                            if BLUEPRINT and i == 0:
                                # dress the evolved blueprint rather than random genes
                                population[i].values = BLUEPRINT["genotype"]["values"][:]
                                if BLUEPRINT["genotype"]["chromosome"]:
                                    population[i].chromosome = BLUEPRINT["genotype"]["chromosome"][:]
                            else:
                                population[i].decode()
                            population[i].drawBodyplan(i, g, finished, statesCA, BetwGens)
```

Individual 0 becomes the evolved blueprint; any further individuals stay random,
so you can place the chosen design beside fresh variants for comparison. Set the
population prompt to 2 (its minimum) and ignore individual 1, or raise it when
you want that comparison.

---

## Grid mismatch — the expected case

Stage 1 explores cheaply at `3 x 3 x 1`. Stage 2 builds at `4 x 4 x 24`. That
mismatch is a feature of your workflow, not a bug, and `load_blueprint` will
print a warning rather than fail.

Two ways to handle it:

**Match the grids.** Set Stage 1's `CAunitsX/Y/Z` to Stage 2's values before the
exploratory run. Slower to evolve, but the blueprint transfers exactly. Best when
the vertical arrangement matters to the design.

**Adapt.** Keep exploring small and stretch the result upward:

```python
    if BLUEPRINT:
        target = bp.grid_dict(CAunitsX, CAunitsY, CAunitsZ, widthCA, FLOORHEIGHT)
        if bp.compare_grids(BLUEPRINT["grid"], target):
            BLUEPRINT = bp.adapt_blueprint_to_grid(BLUEPRINT, target, floor_mode="tile")
```

Read `adapt_blueprint_to_grid`'s docstring before relying on this. `values[0..5]`
— the three unit-type dimensions, which carry most of the design intent — are
grid-independent and transfer cleanly. Per-cell offsets and `statesCA` are not,
so they get retiled: `"tile"` repeats floors cyclically, `"stretch"` maps
proportionally to preserve a vertical gesture. Plan grids (X and Y) cannot be
adapted at all, since widening would mean inventing cells with no evolved basis.

Adaptation invalidates the binary chromosome, so the function empties it and sets
`meta.adapted_from.chromosome_invalidated`. An adapted blueprint can be dressed
but not bred from. Re-run Stage 1 at the target grid if you need to keep evolving.

---

## Inspecting blueprints outside Rhino

```python
import blueprint_export as bp
for row in bp.list_blueprints():
    print row["fitness"], row["grid"], row["path"], row["note"]
```

Sorted best-first. Handy for choosing what to dress without launching Rhino.

---

## The workflow this gives you

1. Run Stage 1 small and fast — modest grid, many individuals, many generations.
   Top 5 blueprints land in `exports/`.
2. Inspect them with `list_blueprints()`, or open the JSON directly.
3. Run Stage 2, choose a blueprint in the file dialog, get the full
   architectural model — ellipse units, walls, slabs, bridges, tower skin,
   centreline.
4. Repeat step 3 for other blueprints, or with different Stage 2 parameters, at
   no cost to the Stage 1 work.

Because Stage 2 no longer evolves anything, you can push `CAunitsZ` higher or add
per-unit detail freely — it runs once per chosen blueprint, not once per
individual per generation per SOM cycle. That headroom is precisely what
separating the stages buys you.

---

## Untested

These edits are written against the code as read, but have not been run in Rhino.
Test with a small grid and 2 generations before committing to a real project run.
The two 2013 scripts in this repository are the untouched originals — work on
copies.
