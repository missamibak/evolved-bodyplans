# Patch status -- Stage 1

21 August 2026

## Naming convention

Patched outputs carry a `_patchedDDMMYY` suffix. Each patch run produces a new
dated file rather than overwriting the last, so any result can be traced back to
the exact script that produced it. The 2013 originals are never modified.

    <original name>_patched210826.py    <- 21 August 2026

When adding a new patch run, append a section to this file rather than editing
the previous one.

## Committed files

| File | Bytes | Blob |
|---|---|---|
| `...boxes only.py` (original) | 82,422 | `a5840bd5` |
| `...boxes only_patched210826.py` | 83,414 | `e2e8f248` |
| `...evolved bodyplan_1st gen only no SOM.py` (original) | 91,113 | `ca2281ef` |

The original's blob hash is unchanged across every commit in this repo. That is
the recovery guarantee: whatever happens to the patched line, the 2013 code is
still exactly as it was.

---

# Run 1 -- 21 August 2026

Output file: `AmiinaBakunowicz_MSc Thesis 2013_UEL_CA based GA_SOM_boxes only_patched210826.py`

Produced by `patch_stage1.py` v2 against the untouched original.
All 13 rules matched. Patcher reported **0 rules with problems**.

| | value |
|---|---|
| input, as read in text mode | 80,741 bytes / 1,682 lines |
| output, as written in text mode | 81,680 bytes / 1,735 lines |
| output on disk and in Git (CRLF) | 83,414 bytes |
| `VOID_RATE` as shipped | `0.0` |

The on-disk figure exceeds the text-mode figure because the patcher reads and
writes in text mode: Windows `\r\n` collapses to `\n` on read and expands again
on write. 81,680 + 1,734 line endings = 83,414. Nothing is lost. The same
explains the input reading as 80,741 rather than its 82,422 bytes on disk.

## What it fixes

Six bugs, all of which would have crashed or silently skewed a run once void
cells existed.

1. **`"void"` added to `statesCAall`.** The 2013 code referenced a fourth state
   it never defined.
2. **Dead void branch revived.** `k > 10` could never fire against a 0-10
   random, and `statesCAall[3]` was out of range. Now `k < VOID_RATE`.
3. **Voids hold their index position.** `guid` stores `None` at a void's slot in
   both `Individual` and `Neuron`, so cell *i* always maps to `guid[i]`.
4. **Centroid and distance calls guarded.** The original tested `boxThis` for
   `None` while dereferencing the *neighbour*, so a void neighbour still raised.
   18 centroid and 16 distance call sites fixed across both `assessFitness` and
   `assessNeuronFitness`.
5. **Fitness normalised by live-neighbour count.** Without this, a cell beside a
   void scored roughly 1.28x higher purely from having fewer neighbours to sum,
   biasing selection toward the grid edge. See `FINDINGS.md`.
6. **Colour and intersection calls filtered** to live geometry only.

## Rules that matched

| Rule | Hits | Meaning |
|---|---|---|
| 1 `void` added to `statesCAall` | 1 | |
| 2 dead void branch fixed | 1 | `k > 10` -> `k < VOID_RATE`, `statesCAall[3]` -> `"void"` |
| 3, 4 voids hold their place in `guid` | 1 each | `Individual` and `Neuron` |
| 5a, 5b x8 guarded centroids | 2 each | 18 call sites across both fitness methods |
| 6 x8 counted distances | 2 each | 16 call sites |
| 7 x8 guarded intersections | 2 each | 16 call sites |
| 8 guarded area + live count | 2 | |
| 9 counters reset | 2 | |
| 10 fitness normalised | 2 | |
| 11, 12, 13 colour calls filtered | 1, 2, 1 | |

The consistent **2 hits** on rules 5-10 is the signature of both `assessFitness`
and `assessNeuronFitness` being patched, which is what the SOM path requires.

## Verified in the output

    _pair_dist        17   (1 definition + 16 calls)
    _safe_centroid    19   (1 definition + 18 calls)
    OLD pattern        0   ("is not None and centroidThis is not None")

The zero is the decisive one: every original guarded-distance line, which tested
`boxThis` while dereferencing a neighbour, has been replaced.

## Not yet done

The patched script has **never been executed**. It imports `rhinoscriptsyntax`
on line 1, so it only runs inside Rhino. Everything above verifies that the
edits landed, not that the algorithm behaves.

Outstanding, in order:

1. **Null test.** Run in Rhino with `VOID_RATE = 0.0`, grid 3x3x1, 3
   individuals, 2 generations, selection option 1. Output should match the
   untouched original. This separates "did the patch break anything" from "do
   voids work".
2. **Porosity test.** Set `VOID_RATE = 0.20` and compare.
3. **Manual follow-ups** if they surface: `rs.DeleteObjects` and
   `rs.SelectObjects` on `guid` lists may need wrapping in `_live(...)`. They
   were left alone deliberately -- the call sites vary and a wrong edit there
   deletes the wrong geometry.
4. **Stage 2 is unpatched.** Its tower loft matches ellipse division points
   across floors, so a void on one floor but not the next breaks the
   correspondence. Whether the skin should close over or open around a void is a
   design decision, not a bug fix.

## Expect it to be slow

Under IronPython 2.7 the integer division in `runSOM()` fixes the map at exactly
600 cycles per generation regardless of convergence, and neighbourhood learning
stops at cycle 100. See `FINDINGS.md` section 1. That is the 2013 behaviour, not
a hang.
