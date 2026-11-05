import cadquery as cq
import numpy as np
import trimesh

import layout as L
import pecas as PC

m = L.M()
geo = PC.mundo(m)
fx = L.fixadores(m)
sol = PC.construir(m, "Cabine", None, fx, geo)
print("solidos", len(sol.Solids()), "shells", len(sol.Shells()), "vol", sol.Volume() / 1000)
for sh in sol.Shells():
    bb = sh.BoundingBox()
    print("  shell", round(bb.xmin, 1), round(bb.xmax, 1), round(bb.ymin, 1), round(bb.ymax, 1), round(bb.zmin, 1), round(bb.zmax, 1))
cq.exporters.export(cq.Workplane().add(sol), "saida/_cab.stl", tolerance=0.03, angularTolerance=0.15)
me = trimesh.load("saida/_cab.stl")
for p in me.split(only_watertight=False):
    print("  pedaco", round(abs(p.volume) / 1000, 3), p.bounds.round(1).tolist())
