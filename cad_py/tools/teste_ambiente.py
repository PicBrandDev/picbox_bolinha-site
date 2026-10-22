"""Fase 0: cubo com filete -> STEP + STL -> recarregar -> validar."""
import sys
import tempfile
from pathlib import Path

import cadquery as cq
import trimesh

d = Path(tempfile.mkdtemp())
peca = cq.Workplane("XY").box(30, 30, 30).edges("|Z").fillet(3).faces(">Z").hole(6)
cq.exporters.export(peca, str(d / "cubo.step"))
cq.exporters.export(peca, str(d / "cubo.stl"), tolerance=0.02, angularTolerance=0.1)

rel = cq.importers.importStep(str(d / "cubo.step"))
s = rel.val()
faces = {f.geomType() for f in s.Faces()}
m = trimesh.load(d / "cubo.stl")
ok = s.isValid() and len(rel.solids().vals()) == 1 and "CYLINDER" in faces and m.is_watertight and m.is_winding_consistent
print(f"cadquery {cq.__version__} | valido={s.isValid()} solidos={len(rel.solids().vals())} faces={sorted(faces)}")
print(f"stl watertight={m.is_watertight} winding={m.is_winding_consistent} tri={len(m.faces)} vol={m.volume:.1f} vs brep={s.Volume():.1f}")
print("OK" if ok else "FALHOU")
sys.exit(0 if ok else 1)
