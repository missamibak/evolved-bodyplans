# Findings log

Things discovered about the 2013 algorithm while bringing it back into use.
Recorded because several are not obvious from reading the code, and one of them
changes how the thesis results should be interpreted.

All findings below were established by running the algorithm **headlessly** --
the boxes-only stage uses nothing but axis-aligned boxes, so centroid, surface
area and boolean intersection were computed analytically rather than through
Rhino. Structure is faithful; exact figures should be confirmed in Rhino.

---

## 1. Integer division silently fixed the SOM at 600 cycles

`runSOM()` decays its learning parameters like this:

```python
WINLEARN = WINLEARN * (1 - (cycles / 600))
LEARN    = LEARN    * (1 - (cycles / 400))
NEIGH    = RADIUS   * (1 - (cycles / 100))
```

Under Python 2 -- which is what Rhino 5 ran, and therefore what produced the
thesis results -- these are **integer** divisions. Consequences:

- `cycles / 600` is `0` until cycle 600, so `WINLEARN` sits frozen at 0.98 and
  the convergence test never fires. The map runs **exactly 600 cycles** every
  time, regardless of whether it has converged.
- `NEIGH` reaches zero at **cycle 100** and goes negative after. From cycle 100
  onward the `dist <= NEIGH` test can never pass, so every neuron receives only
  inhibitory feedback. Neighbourhood learning -- the thing that makes a
  self-organising map self-organising -- is dead for the last 500 cycles.

Under Python 3 the same lines are true division: `WINLEARN` decays smoothly,
converges in **32 cycles**, and `NEIGH` shrinks gradually without going
negative.

Measured, population 3 (a 4x4 map), 5 generations, three seeds:

| | Python 2 division | Python 3 division |
|---|---|---|
| SOM cycles per 5-generation run | 3,000 | 215 |
| Fit candidates found | 43 | 192 |
| Neighbourhood learning | dead after cycle 100 | active throughout |

So the Python 3 behaviour is both ~14x cheaper and finds ~4.5x more viable
candidates.

**Why this matters beyond performance:** the thesis results came from the
600-cycle, inhibition-dominated behaviour. Porting to Python 3 does not
"fix a bug" -- it produces a *different algorithm* that no longer reproduces the
documented findings. Both are legitimate; they should be kept as separate
variants rather than one silently replacing the other.

It also retrospectively explains a thesis observation: "Even if all the
individuals in the generation have fitness of zero, a map can produce couple of
neurons with some sort of fitness." Sparse viable neurons are what the
inhibition-heavy regime produces.

**Recommendation:** when porting, write the divisor as a float so the intent is
explicit in either engine:

```python
WINLEARN = WINLEARN * (1 - (cycles / 600.0))
```

---

## 2. Void cells inflate fitness spuriously

See `VOID_CELLS.md` for the full study. Summary:

`distFactor` and `XXareasFactor` are reciprocals of sums taken over
Moore-neighbour pairs. Each void removes pairs from the sum, shrinking it and
inflating the reciprocal. A perforated model therefore scores **1.28x higher**
across a 0-60% void range without being better.

Normalising both by the number of pairs actually measured (`pairs / 8.0`), and
normalising `totalAreaFactor` by live cell count, reduces the bias to 0.97x --
effectively neutral.

---

## 3. Cell function is not evolvable

`statesCA` is generated **once per run**, before the generation loop, and shared
by every individual and every SOM neuron. So living / working / resting / void
is a fixed constraint. The GA only moves and resizes units within it.

This is consistent with the thesis treating the CA model as predetermined, but
it means porosity is something you impose rather than something evolution
discovers. Making it evolvable needs one extra gene per cell -- a real change,
belonging with "Parameterisation of the Body-Plan" in Further Research.

---

## 4. The neighbour guards test the wrong object

In `assessFitness()`, throughout the eight-neighbour block:

```python
boxS = self.guid[index-1]
if boxThis is not None: centroidS = rs.SurfaceVolumeCentroid(boxS)[0]
```

The guard checks `boxThis` while dereferencing `boxS`. Harmless while every cell
produces a box, but it becomes a live `TypeError` the moment voids introduce
`None` entries. Fix before enabling voids.

The same block also leaves `dist1..dist8` from the previous iteration in scope
when a guard fails, so stale distances can be summed. Accumulating into a
running total inside the neighbour loop avoids this.

---

## 5. Blueprint round trip is exact

Verified: a blueprint saved by Stage 1 and reloaded reproduces **bit-identical**
gene values, cell states, box centroids, surface areas and total fitness. Grid
adaptation also behaves as specified -- tile mode repeats floors periodically,
stretch mode maps three source floors across nine targets as
`[0,0,0,1,1,1,2,2,2]`, and both preserve `values[0..5]` while clearing the
chromosome to mark it unbreedable.

This is the correctness guarantee the two-stage pipeline depends on.
