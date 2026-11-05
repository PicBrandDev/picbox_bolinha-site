"""Espessura de parede de cada STL: raios para dentro a partir de pontos da superficie.

  python teste_paredes.py [peca.stl ...]   ->  teste_paredes.json
Parede < 0,8 mm (2 linhas de bico 0,4) sai falhada; < 0,45 mm o fatiador nem imprime.
"""
import json
import sys
from pathlib import Path

import numpy as np
import trimesh

AQUI = Path(__file__).parent


def espessuras(me, n=6000):
    pts, fi = trimesh.sample.sample_surface_even(me, n, seed=2)
    nor = me.face_normals[fi]
    orig = pts - nor * 0.01
    loc, ri, _ = me.ray.intersects_location(orig, -nor, multiple_hits=False)
    esp = np.full(len(pts), np.inf)
    esp[ri] = np.linalg.norm(loc - orig[ri], axis=1)
    return pts, esp


def main():
    arqs = [Path(a) for a in sys.argv[1:]] or sorted((AQUI / "saida" / "stl").glob("*.stl"))
    res = []
    for f in arqs:
        me = trimesh.load(str(f), force="mesh")
        pts, esp = espessuras(me)
        fino = esp < 0.45
        res.append(dict(stl=f.name, menor_mm=round(float(esp.min()), 2), pct_abaixo_0_8=round(100 * float((esp < 0.8).mean()), 2),
                        pct_abaixo_0_45=round(100 * float(fino.mean()), 2),
                        pontos_finos=[p.round(1).tolist() for p in pts[fino][:5]]))
        print(f"{f.name:42s} <0,8 mm: {res[-1]['pct_abaixo_0_8']:5.2f}%   <0,45 mm: {res[-1]['pct_abaixo_0_45']:5.2f}%   "
              f"menor {res[-1]['menor_mm']:.2f}", flush=True)
    if not sys.argv[1:]:
        (AQUI / "teste_paredes.json").write_text(json.dumps(res, indent=1), encoding="utf8")


if __name__ == "__main__":
    main()
