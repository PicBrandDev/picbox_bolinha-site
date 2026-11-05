"""Diagnostico de uma STL: pedacos (volume e posicao) e bordas abertas."""
import sys

import numpy as np
import trimesh

for arq in sys.argv[1:]:
    me = trimesh.load(arq, force="mesh")
    print("==", arq, "fechada", me.is_watertight, "faces", len(me.faces))
    for p in me.split(only_watertight=False):
        print("   pedaco vol %.3f cm3  bbox %s .. %s" % (abs(p.volume) / 1000, p.bounds[0].round(1), p.bounds[1].round(1)))
    if not me.is_watertight:
        from collections import Counter
        e = Counter(map(tuple, np.sort(me.edges, axis=1)))
        abertas = [k for k, v in e.items() if v != 2]
        pts = me.vertices[np.array(abertas).ravel()] if abertas else np.zeros((0, 3))
        print("   bordas ruins", len(abertas), "regiao", pts.min(0).round(1) if len(pts) else "", pts.max(0).round(1) if len(pts) else "")
