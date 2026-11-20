#!/usr/bin/env python3
"""Write cantilever (shear-locking) decks for CalculiX and DLEARN.

Usage:  python3 make_beam_decks.py NX NY [ELTYPE]
        e.g.  python3 make_beam_decks.py 40 4 CPE4R
Writes  beam_<eltype>_<NX>x<NY>.inp   (CalculiX)
        beam_dlearn_<NX>x<NY>.dat      (DLEARN, full 2x2 integration)
Units: N, mm, MPa.  Plane strain, unit thickness, tip load P spread over the end nodes.
"""
import sys
L, H, E, NU, P = 100.0, 10.0, 210000.0, 0.3, 100.0

def tip_loads(NY):
    """Consistent nodal forces for a uniform end shear: P/(2NY) at the corners, P/NY inside."""
    return [P/NY if 0 < k < NY else P/(2.0*NY) for k in range(NY+1)]

def calculix(path, NX, NY, etype):
    nb = NX + 1
    s = ["** Cantilever, plane strain, %dx%d %s. Units: N, mm, MPa." % (NX, NY, etype),
         "** Reference tip deflection: about 1.74 mm.",
         "*HEADING", "Cantilever, plane strain, %dx%d %s" % (NX, NY, etype),
         "** ---- model data: nodes (number, x, y), elements, material, section ----",
         "*NODE, NSET=NALL"]
    for j in range(NY+1):
        for i in range(NX+1):
            s.append("%d, %.5g, %.5g" % (j*nb+i+1, L*i/NX, H*j/NY))
    s.append("*ELEMENT, TYPE=%s, ELSET=EALL" % etype)
    e = 0
    for j in range(NY):
        for i in range(NX):
            e += 1; n1 = j*nb+i+1
            s.append("%d, %d, %d, %d, %d" % (e, n1, n1+1, n1+nb+1, n1+nb))
    s += ["*MATERIAL, NAME=STEEL", "*ELASTIC", "%.1f, %.1f" % (E, NU),
          "*SOLID SECTION, ELSET=EALL, MATERIAL=STEEL", "1.0",
          "** ---- node sets: WALL = clamped end, TIP = loaded end ----"]
    wall = [j*nb+1 for j in range(NY+1)]; tip = [j*nb+nb for j in range(NY+1)]
    s += ["*NSET, NSET=WALL", ", ".join(map(str, wall)), "*NSET, NSET=TIP", ", ".join(map(str, tip)),
          "** ---- step: clamp the wall, apply the tip load, request output ----",
          "*STEP", "*STATIC", "*BOUNDARY", "WALL, 1, 2",
          "** consistent nodal forces of the end shear (negative = downward)", "*CLOAD"]
    for n, f in zip(tip, tip_loads(NY)): s.append("%d, 2, %.6g" % (n, -f))
    s += ["*NODE PRINT, NSET=TIP", "U",
          "** total reaction at the clamped end: expect Fy = +100 N",
          "*NODE PRINT, NSET=WALL, TOTALS=ONLY", "RF",
          "*EL PRINT, ELSET=EALL", "COORD", "S",
          "*NODE FILE", "U, RF", "*EL FILE", "S, E", "*END STEP"]
    open(path, "w").write("\n".join(s) + "\n")

def dlearn(path, NX, NY):
    nb = NX + 1; nn = nb*(NY+1)
    s = ["    0", "Cantilever beam, plane strain, %dx%d Q4 elements" % (NX, NY),
         "%5d"*15 % (1,1,0,0,0,0,1,0,2,nn,2,1,1,1,1),
         "%5d%5d%5d%5d%5d%5d%10.2f%10.2f%10.2f%10.2f" % (1,1,1,1,0,1,0.0,1.0,0.0,1.0)]
    for j in range(NY+1):
        for i in range(NX+1):
            s.append("%5d%5d%10.3f%10.3f" % (j*nb+i+1, 0, L*i/NX, H*j/NY))
    s.append("")
    for j in range(NY+1): s.append("%5d%5d%5d%5d%5d" % (j*nb+1, 0, 0, 1, 1))
    s.append("")
    for k, f in enumerate(tip_loads(NY)): s.append("%5d%5d%10.3f%10.3f" % ((k+1)*nb, 0, 0.0, -f))
    s += ["", "%10.2f%10.2f" % (1.0, 1.0),
          "%5d"*13 % (1, NX*NY, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0),
          "%5d%5s%10.1f%10.3f%10.2f%10.2f%10.2f%10.2f" % (1, "", E, NU, 0.0, 0.0, 0.0, 1.0),
          "%10.2f%10.2f" % (0.0, 0.0)]
    e = 0
    for j in range(NY):
        for i in range(NX):
            e += 1; n1 = j*nb+i+1
            s.append("%5d%5d%5d%5d%5d%5d%5d" % (e, 1, n1, n1+1, n1+nb+1, n1+nb, 0))
    s += ["", "*end"]
    open(path, "w").write("\n".join(s) + "\n")

if __name__ == "__main__":
    NX, NY = int(sys.argv[1]), int(sys.argv[2])
    et = sys.argv[3].upper() if len(sys.argv) > 3 else "CPE4"
    calculix("beam_%s_%dx%d.inp" % (et.lower(), NX, NY), NX, NY, et)
    dlearn("beam_dlearn_%dx%d.dat" % (NX, NY), NX, NY)
    print("written")
