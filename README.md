# Evolving 3D Cellular Automata Architectural Model

**Genetic Algorithm + Neural Self-Organising Maps, in Rhino/Python**

Original research and algorithm by **Amiina Bakunowicz**, MSc Thesis, School of
Architecture, Computing and Engineering, University of East London, September 2013.

---

## What this does

The algorithm gives form to a building from a predetermined functional and
spatial arrangement, without fixing the geometry in advance. A cellular automata
model defines a grid of units, each in one of three functional states --
`living`, `working`, `resting`. A genetic algorithm parameterises and evolves the
sizes and positions of those units. A Kohonen self-organising map is trained on
each generation to expand, classify and cluster the search space, countering the
local-optima problem a plain GA suffers from.

The designer stays in the loop. Fitness is multi-criteria and deliberately
non-absolute, so the stopping condition is "fit enough and acceptable to the
eye", not "fittest".

---

## A deliberate two-stage pipeline

The two scripts are **not** halves of one broken program. They are two stages,
run independently and as often as a project needs:

### Stage 1 -- find the blueprint of the form
`AmiinaBakunowicz_MSc Thesis 2013_UEL_CA based GA_SOM_boxes only.py`

The full GA + SOM evolutionary engine. Evolves across generations, trains the
map, clusters the search space, selects parents, crosses over, mutates. Renders
simple coloured boxes -- cheap, so you can explore widely.

### Stage 2 -- dress it up
`AmiinaBakunowicz_MSc Thesis 2013_UEL_CA based GA_SOM_evolved bodyplan_1st gen only no SOM.py`

The architectural geometry layer: elliptical unit volumes oriented radially
about each floor's centroid, walls, floor and ceiling slabs, inter-unit bridges,
a lofted tower skin, railings and a structural centreline -- all on named Rhino
layers. Expensive, so it runs once on a blueprint you have already chosen.

Stage 1 explores. Stage 2 details. Neither needs the other to be useful.

---

## Fitness criteria

| Component | Measures |
|---|---|
| `GSfactor` | Closeness of each unit's width/length ratio to the golden section (1.618) |
| `distFactor` | Tightness of centroid distances across the Moore neighbourhood |
| `XXareasFactor` | Penalty on solid intersection between neighbouring units |
| `totalAreaFactor` | Total floor area |
| `WRareaFactor` / `RLareaFactor` | Working:resting and resting:living area ratios |
| `ellipsesXXfactor` | *(Stage 2)* overlap between elliptical floor plates |
| `centrCrvFactor` | *(Stage 2)* reward for a short, straight structural core |

Any single component falling below a co-evolving threshold zeroes total fitness.
That was the thesis's Stage 5 answer to the algorithm gaming one criterion at
the expense of the others.

### Selection options

1. **Goldberg roulette wheel** -- probability proportional to fitness
2. **Optimised random by clusters** -- filter by minimum fitness, pair randomly
3. **Artificial selection** -- the designer picks parents from the viewport

---

## Repository contents

| File | Purpose |
|---|---|
| `..._boxes only.py` | Stage 1, untouched 2013 original |
| `..._evolved bodyplan_1st gen only no SOM.py` | Stage 2, untouched 2013 original |
| `blueprint_export.py` | Data contract connecting the stages |
| `PIPELINE_WIRING.md` | The exact edits to connect them |
| `VOID_CELLS.md` | Void-cell study, findings and patch |
| `FINDINGS.md` | What was discovered about the algorithm |

The two 2013 scripts are **byte-exact originals**. Work on copies.

---

## Connecting the stages

As written, both scripts generate `statesCA` randomly at the start of a run, so
Stage 2 dresses a *different* random building than whatever Stage 1 evolved.
`blueprint_export.py` closes that gap: Stage 1 writes the winning genotype plus
its cell states to JSON, Stage 2 reads one back.

```python
# Stage 1, at the end of runGA()
grid = bp.grid_dict(CAunitsX, CAunitsY, CAunitsZ, widthCA, FLOORHEIGHT)
bp.save_best_of_run(allIndivNeurons, statesCA, grid, top=5, generation=GENERATIONS)

# Stage 2, at the start of runGA()
BLUEPRINT = bp.load_blueprint(BLUEPRINT_PATH, expected_grid=grid)
statesCA  = BLUEPRINT["statesCA"]
```

Stage 1 typically explores at 3x3x1; Stage 2 builds at 4x4x24. That mismatch is
expected -- `adapt_blueprint_to_grid()` stretches a short blueprint upward, with
`tile` (repeat floors) or `stretch` (proportional) modes.

See `PIPELINE_WIRING.md` for the full set of edits.

---

## Status

**Verified without Rhino** -- the boxes-only stage uses only axis-aligned boxes,
so its geometry was reproduced analytically and the algorithm run headlessly:

- Blueprint save/load round trip is **bit-exact** across gene values, cell
  states, box centroids, surface areas and total fitness
- Grid adaptation behaves as specified in both tile and stretch modes
- Payload validation rejects malformed blueprints with clear errors
- The Python 2 / Python 3 division discrepancy is quantified (`FINDINGS.md` #1)
- The void-cell fitness bias is quantified and a correction verified
  (`VOID_CELLS.md`)

**Not yet run in Rhino.** Stage 2's NURBS work -- ellipse construction, the
tower loft, planar bridges -- has no analytic stand-in and needs the real thing.
Rhino-specific failure modes (functions returning `None`, boolean tolerances,
IronPython quirks) remain untested.

---

## Running it

Requires Rhino with `rhinoscriptsyntax`. Rhino 8 recommended -- it ships both
IronPython 2.7 and CPython 3, and the choice matters:

- **IronPython 2.7** reproduces 2013 behaviour exactly. Start here.
- **CPython 3** changes the SOM's convergence behaviour substantially. See
  `FINDINGS.md` #1 before porting.

Start small: 2-3 individuals, 2 generations, `CAunitsZ = 3`, selection option 1
(roulette avoids interactive prompts). Fitness history is written to
`fitnessHistory.txt`.

Geometry lands on layers: `grid`, `boxes`, `walls`, `slabs`, `bridges`,
`railing`, `tower`, `centreline`, `XXareas`, `fitness curves`.

---

## Roadmap

**Next**
- Run both stages in Rhino 8 under IronPython 2.7 and confirm 2013 behaviour
- Apply the void-cell patch with pair normalisation
- Decide whether the tower skin closes over or opens around a void

**Then**
- Python 3 variant, kept alongside the faithful Python 2 version
- NumPy for the SOM vector maths, now possible under Rhino 8 CPython -- the
  training loop is pure Python and dominates runtime
- Weighted fitness components, so importance is explicit rather than emergent
  from magnitude

**Further research, from the thesis**
- Parameterisation of the body-plan beyond geometry, making cell function
  evolvable
- Co-evolution instead of fixed fitness criteria
- Multiple neural maps per generation, each clustering by different criteria
- Site-aware fitness: import an existing Revit model as DWG/ACIS context and
  evolve against real constraints -- overshadowing, boundaries, clashes

**Interoperability**
- Rhino to Revit LT via IFC2x3, the only route available since Revit LT blocks
  SAT, 3DM and all add-ins
- Rhino.Inside.Revit if full Revit ever becomes available -- live Grasshopper to
  native Revit elements, no round trip

---

## Licence and citation

Research and original implementation by Amiina Bakunowicz, 2013.
If you build on this, please cite the thesis.
