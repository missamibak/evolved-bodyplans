# Void cells: study, findings and patch

The 2013 scripts contain a dead branch intended to create void cells on the
outer layer of the CA model. It has never once executed. This document records
what happens when it is switched on, tested headlessly (no Rhino) across 60
random genotypes per condition.

---

## The original bug

```python
k = r.random()
if k > 10 and (x == 0 or y == 0 or x == CAunitsX-1 or y == CAunitsY - 1):
    statesCA.append(statesCAall[3])
```

Two faults:

1. `r.random()` returns 0.0-1.0, so `k > 10` is never true.
2. `statesCAall` has three entries, so `statesCAall[3]` would raise
   `IndexError` if the branch ever fired.

The second fault is why the first was never noticed.

---

## Finding 1: voids inflate fitness spuriously

With the branch fixed and nothing else changed, mean fitness *rises* with void
rate:

| treatment | 0% voids | 15% | 30% | 45% | 60% | bias |
|---|---|---|---|---|---|---|
| raw (unchanged fitness) | 947.1 | 1110.3 | 1264.9 | 1269.0 | 1212.4 | **1.28x** |
| normalised | 947.1 | 1018.8 | 1073.3 | 977.5 | 922.7 | 0.97x |
| rewarded (target 20%) | 947.1 | 1083.9 | 1131.7 | 1004.4 | 943.1 | 1.00x |

The cause is in these two lines:

```python
if distFactor    != 0: distFactor    = 17000*CAunitsZ/distFactor
if XXareasFactor != 0: XXareasFactor = 150000*CAunitsZ/XXareasFactor
```

Both are reciprocals of a **sum over Moore-neighbour pairs**. A void removes
pairs from that sum, the sum shrinks, and the reciprocal grows. So a perforated
model scores better without being better. Left uncorrected, evolution would
learn to exploit voids as a scoring artefact rather than as a spatial idea.

Normalising each reciprocal by the number of pairs actually measured
(`pairs / 8.0`), and normalising `totalAreaFactor` by live cell count, removes
the bias almost exactly -- 0.97x across a 0-60% void range.

---

## Finding 2: voids are not currently evolvable

`statesCA` is generated **once per run**, before the generation loop, and shared
by every individual and every SOM neuron. Cell function -- living, working,
resting, void -- is therefore a fixed constraint, not part of the genotype. The
GA can only move and resize units within it.

So the question "will evolution delete the voids?" has no meaning as the code
stands: it cannot. Porosity is something you *impose*, and the algorithm then
finds the best form under that constraint.

This matches the thesis's own framing of the CA model as predetermined. If you
want porosity to evolve, void-ness must become genetic -- one extra gene per
cell -- which is a larger change and belongs with the "Parameterisation of the
Body-Plan" item in Further Research.

---

## Recommended patch

### 1. Add the fourth state

```python
statesCAall = ["living", "working", "resting", "void"]
VOID_RATE = 0.20        # share of outer-layer cells made void
```

### 2. Fix the generator

```python
statesCA = []
for z in range (CAunitsZ):
    for y in range (CAunitsY):
        for x in range (CAunitsX):
            isEdge = (x == 0 or y == 0 or
                      x == CAunitsX-1 or y == CAunitsY-1)
            if isEdge and r.random() < VOID_RATE:
                statesCA.append("void")
            else:
                statesCA.append(statesCAall[r.randrange(0,3)])
```

### 3. Keep the guid list index-aligned

`assessFitness` addresses boxes by computed index
(`self.guid[index-1]`). If a void appends nothing, every later index points at
the wrong cell. Voids must hold their place:

```python
if statesCA[i] == "void":
    guid.append(None)
elif statesCA[i] == "living":
    ...
```

### 4. Guard the neighbour loop and count pairs

The existing guards test the wrong object -- `if boxThis is not None` while
dereferencing `boxS`. Replace the eight-neighbour block with:

```python
boxThis = self.guid[index-1]
if boxThis is None:
    continue
centroidThis = rs.SurfaceVolumeCentroid(boxThis)[0]

for nIdx in neighbourIndices:          # the 8 computed indices
    neighbour = self.guid[nIdx]
    if neighbour is None:
        continue
    c = rs.SurfaceVolumeCentroid(neighbour)
    if c is None:
        continue
    distFactor += rs.Distance(centroidThis, c[0])
    pairs += 1
    inter = rs.BooleanIntersection(boxThis, neighbour, False)
    if inter:
        for piece in inter:
            XXareasFactor += rs.SurfaceArea(piece)[0]
            objects.append(piece)
```

### 5. Normalise, so voids are score-neutral

```python
scale = pairs / 8.0
if distFactor:    distFactor    = (17000*CAunitsZ/distFactor) * scale
if XXareasFactor: XXareasFactor = (150000*CAunitsZ/XXareasFactor) * scale
if liveCells:     totalAreaFactor = (totalAreaFactor/liveCells*NCELLS)*0.017/CAunitsZ
```

where `liveCells` counts non-None boxes and `NCELLS` is
`CAunitsX*CAunitsY*CAunitsZ`.

---

## Stage 2 consequence, not yet addressed

The architectural stage lofts the tower skin through matching ellipse division
points across floors. A void on one floor but not the next breaks that
correspondence and the loft will fail or skew.

The fix is to interpolate through void gaps rather than skip them -- but whether
the skin should close over a void or open around it is a design decision, not a
technical one. Decide it visually, after seeing a few porous blueprints.

---

## Caveat

These figures come from a headless reproduction of the algorithm: boxes are
axis-aligned, so centroid, surface area and boolean intersection were computed
analytically instead of through Rhino. The structure is faithful and the
direction of the results is reliable; the exact numbers should be confirmed in
Rhino. Treat the 1.28x bias as real and its precise magnitude as approximate.
