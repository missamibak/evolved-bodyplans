# Evolving 3D Cellular Automata Architectural Model

**Genetic Algorithm + Neural Self-Organising Maps, in Rhino/Python**

Original research and algorithm by **Amiina Bakunowicz**, MSc Thesis, School of
Architecture, Computing and Engineering, University of East London, September 2013.

---

## What this does

The algorithm gives form to a building from a predetermined functional and spatial
arrangement, without fixing the geometry in advance. A cellular automata model
defines a grid of units, each in one of three functional states — `living`,
`working`, `resting`. A genetic algorithm parameterises and evolves the sizes and
positions of those units. A Kohonen self-organising map is trained on each
generation to expand, classify and cluster the search space, countering the
local-optima problem that a plain GA suffers from.

The designer stays in the loop: fitness is multi-criteria and deliberately
non-absolute, so "fit enough and acceptable to the eye" is the stopping condition,
not "fittest".

### Fitness criteria

| Component | Measures |
|---|---|
| `GSfactor` | Closeness of each unit's width/length ratio to the golden section (1.618) |
| `distFactor` | Tightness of centroid distances across the Moore neighbourhood |
| `XXareasFactor` | Penalty on solid intersection between neighbouring units |
| `ellipsesXXfactor` | Penalty on overlap between elliptical floor plates |
| `centrCrvFactor` | Reward for a short, straight structural centreline |

Any single component falling below a co-evolving threshold zeroes total fitness.
This was the thesis's Stage 5 answer to the algorithm gaming one criterion at the
expense of the others.

### Selection options

1. **Goldberg roulette wheel** — probability proportional to fitness
2. **Optimised random by clusters** — filter by minimum fitness, pair randomly
3. **Artificial selection** — the designer picks parents from the viewport

---

## Repository contents

### `ca_ga_som_evolved_architecture.py`

A 2026 merge of the two surviving 2013 scripts, updated to Python 3 so it runs in
the Rhino 8 ScriptEditor under either engine.

### Source scripts (2013)

- **`..._boxes-only.py`** — the complete GA + SOM evolutionary engine. Evolves
  across generations, trains the map, clusters, selects, crosses over. Renders
  simple coloured boxes.
- **`..._evolved-bodyplan_1st-gen-only-no-SOM.py`** — the complete architectural
  geometry layer: elliptical unit volumes oriented radially about a floor
  centroid, walls, floor and ceiling slabs, inter-unit bridges, a lofted tower
  skin, railings, structural centreline, all on named layers. The SOM, selection
  and crossover block is commented out and `EVOLUTION` forced `False`, so it
  produced a single generation only.

The two were complementary halves: one evolved, one built.

---

## The merge

The reason evolution was switched off in the architectural version is cost. At
4 x 4 x 24 units, each individual requires 384 ellipse constructions, extrusions,
planar surfaces and boolean intersections — multiplied by a map of
`(population x 1.5)^2` neurons, retrained every cycle until convergence, every
generation. Infeasible on 2013 hardware.

The merge resolves this with **two levels of geometric detail**. SOM neurons
render as cheap boxes during training, since they only need to exist as parameter
vectors to be clustered and scored. GA individuals and selected parents receive
the full architectural treatment. Controlled by `NEURON_DETAIL` and
`INDIVIDUAL_DETAIL`.

### Other changes from the originals

- IronPython 2 to Python 3: print functions, explicit float division
- Defensive `None` checks around `rs.BooleanIntersection` and
  `rs.SurfaceVolumeCentroid`, which were a likely cause of intermittent failures
  on degenerate geometry
- Geometry bookkeeping encapsulated per object so cleanup is reliable
- Moore-neighbour indexing extracted into a helper, replacing eight repeated
  inline index calculations in each of four places

---

## Running it

Requires Rhino with `rhinoscriptsyntax`. Open in the ScriptEditor and run.

You will be prompted for population size, generation count and selection method.

**Start small.** Try 2 individuals, 2 generations, and reduce `CAunitsZ` to 3
before attempting a 24-floor tower. Fitness history is written to
`fitnessHistory.txt` in the working directory.

Geometry is organised onto layers: `grid`, `boxes`, `walls`, `slabs`, `bridges`,
`railing`, `tower`, `centreline`, `XXareas`, `fitness curves`.

---

## Further development

Directions the thesis identified, plus newer options:

- **Parameterisation of the body-plan** beyond purely geometrical genes
- **Co-evolution instead of fixed fitness criteria**, to prevent populations
  becoming stuck in local optima
- **Weighted fitness components**, assigning explicit importance per criterion
- **Multiple neural maps per generation**, each clustering by different criteria
- **NumPy for the SOM vector maths**, now possible under Rhino 8 CPython — the
  training loop is currently pure-Python and dominates runtime
- **Rhino.Inside.Revit output**, turning evolved massing into native Revit
  geometry for documentation

---

## Licence and citation

Research and original implementation by Amiina Bakunowicz, 2013.
If you build on this, please cite the thesis.
