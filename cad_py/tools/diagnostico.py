"""Localiza paredes finas e pontes numa STL de impressao: python tools/diagnostico.py <stl> [min_parede]"""
import sys
from collections import Counter

import numpy as np
import trimesh

m = trimesh.load(sys.argv[1])
mn = float(sys.argv[2]) if len(sys.argv) > 2 else 2.4
pts, idx = trimesh.sample.sample_surface_even(m, 3000, seed=1)
nrm = m.face_normals[idx]
o = pts - nrm * 1e-3
loc, ri, _ = m.ray.intersects_location(o, -nrm, multiple_hits=False)
d = np.full(len(pts), np.inf)
d[ri] = np.linalg.norm(loc - o[ri], axis=1)
fino = d < mn * 0.9
print("paredes finas (mesa, celula de 4 mm): espessura min / n")
c = Counter()
dm = {}
for p, dd in zip(pts[fino], d[fino]):
    k = tuple((np.round(p / 4) * 4).astype(int))
    c[k] += 1
    dm[k] = min(dm.get(k, 9), dd)
for k, n in c.most_common(12):
    print(" ", k, round(dm[k], 2), n)
z0 = m.bounds[0][2]
pl = (m.face_normals[:, 2] < -0.999) & (m.triangles_center[:, 2] > z0 + 0.05)
if pl.any():
    sub = m.submesh([np.where(pl)[0]], append=True)
    print("pontes (centro, vao, z):")
    for comp in sub.split(only_watertight=False):
        _, ext = trimesh.bounds.oriented_bounds_2D(comp.vertices[:, :2])
        if min(ext) > 6:
            print(" ", comp.centroid.round(1), round(min(ext), 1), round(max(ext), 1))
print("bounds", m.bounds.round(1).tolist())
