# DLEARN + CalculiX lab: patch test, integration order, shear locking

Units everywhere: N, mm, MPa. Plane strain, unit thickness. All results below were produced
with CalculiX 2.21 and DLEARN built from Hughes' Fortran sources (gfortran).

## Files
The files in the below table can be downloaded from (https://yeditepe-me477.github.io/2026-Fall/assignments/cw4.zip)
| File                                                 | Purpose                                                                      |
|------------------------------------------------------|------------------------------------------------------------------------------|
| `[patch_dlearn.dat]`                                   | Patch test, 5 Q4 elements, DLEARN (2x2 Gauss)                                |
| `patch_cpe4.inp`, `patch_cpe4r.inp`                  | Same problem, CalculiX full / reduced integration                            |
| `rankcheck_dlearn.dat`                               | Two stacked problems: 1 element, 2x2 Gauss vs one-point, with pivot printout |
| `beam_dlearn.dat`, `beam_cpe4.inp`, `beam_cpe4r.inp` | Slender cantilever (10 x 1 elements) for shear locking                       |
| `make_beam_decks.py`                                 | Writes the beam decks for any mesh: `python3 make_beam_decks.py 20 2 CPE4R`  |
| `template_calculix_blank.inp`                        | Annotated blank CalculiX deck for students                                   |

## Running
* **DLEARN** reads a file named `input.dat` and writes `output.dat` in the current folder.
  Copy the deck to `input.dat`, delete any old `output.dat` (the program stops with
  "file exists" otherwise), then run `./dlearn`. The last card must be lowercase `*end`.
  Input is fixed-column: do not re-align the numbers.
  This build has a fixed 50,000-word storage: 30x3 and 20x4 beam meshes run, 40x4 does not
  (`common a(50000)` and `mtot` in `DL.FOR` can be enlarged and recompiled).
* **CalculiX**: `ccx patch_cpe4` (no extension). Text results are in `patch_cpe4.dat`.

## Patch test
Rectangle 10 x 6 with four outer corner nodes and four inner nodes forming a tilted, skewed
interior element; five elements in all. Rollers: nodes 1, 4 (x fixed), nodes 1, 2 (y fixed).
Load: p = 10 MPa on the right edge, applied as 30 N at nodes 2 and 3. E = 1000, nu = 0.3.

Exact solution (uniform state): sx = 10, sy = 0, sz = nu*sx = 3 (plane strain),
ux = 0.0091 x, uy = -0.0039 y, left-wall reaction -60 N in total.

| Node | ux exact = DLEARN = CPE4 | uy exact = DLEARN = CPE4 | ux CPE4R | uy CPE4R |
|------|--------------------------|--------------------------|----------|----------|
| 2    | 0.09100                  | 0                        | 0.08892  | 0        |
| 3    | 0.09100                  | -0.02340                 | 0.08931  | -0.02299 |
| 5    | 0.02821                  | -0.00702                 | 0.02693  | -0.00666 |
| 7    | 0.06188                  | -0.01638                 | 0.06129  | -0.01594 |

* DLEARN and CPE4 reproduce the uniform field to round-off: the element passes the patch test.
* CPE4R (one integration point + hourglass control) does **not** reproduce it on this distorted
  patch: stresses scatter, sxx = 9.54 to 10.15 and syy up to 0.14 instead of 10 and 0.
* DLEARN with `IBBAR=1` (B-bar) also passes. B-bar addresses volumetric locking, not shear locking.
## Integration order, seen in DLEARN
Run `rankcheck_dlearn.dat`. Printed pivots of one unrestrained element (8 equations):
2x2 Gauss gives **3** zero pivots (rigid-body modes); one-point gives **5** (two extra
hourglass modes). Setting `NICODE=1` in `patch_dlearn.dat` (and `IRANK=1`) stops the static
run with "zero and/or negative pivots": the one-point element cannot be solved unstabilized.

## Shear locking (cantilever, L = 100, h = 10, P = 100 N)
Reference tip deflection about 1.74 mm (fine quadratic mesh; Timoshenko beam 1.748 mm).

| Mesh   | CPE4 / DLEARN | CPE4R |
|--------|---------------|-------|
| 10 x 1 | 1.110 (64 %)  | 1.565 |
| 10 x 2 | 1.230         | 1.670 |
| 20 x 2 | 1.517         | 2.107 |
| 40 x 4 | 1.678         | 1.846 |
| 80 x 8 | 1.725         | 1.769 |

Full integration is too stiff and converges slowly from below (locking); reduced integration is
much better on the coarsest mesh but overshoots (hourglass flexibility) and approaches from above.
DLEARN matches CPE4 exactly on 10x1, 10x2 and 20x2 (the meshes that fit its storage).

## Comparing the two output files (and checking the AI)
* CalculiX prints 8 integration points per CPE4 element (two layers of 4) because it expands the
  element to a brick; DLEARN prints 4. With `COORD` in `*EL PRINT`, match points by coordinates.
  DLEARN points 1, 2, 3, 4 correspond to CalculiX points 1, 2, 4, 3 (and 5, 6, 8, 7).
* Compare stresses at integration points only. The `.frd` file holds values extrapolated to
  the nodes and will not match DLEARN's Gauss-point values.
* Plane strain has sz not equal to zero: DLEARN prints it as stress 33.
* In `*NODE PRINT, RF`, a node with a free dof reports the applied load there, not a reaction.
* Student protocol: first write the expected values from the exact solution, then ask the AI for
  a side-by-side table with differences, then verify at least three numbers in the raw files.
