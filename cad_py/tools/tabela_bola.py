"""Calcula o angulo da bola encostada no trilho/guia do elevador em cada altura (esfera tangente ao trilho de aluminio
e a guia da A27) e grava maquina_a/elevador_bola.json. Uso: python tools/tabela_bola.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq  # noqa: E402
import numpy as np  # noqa: E402

from common.checks import _vol_inter  # noqa: E402
from maquina_a import elevador as E  # noqa: E402
from maquina_a.parts import A27_cabeca_elevador as A27  # noqa: E402

guia = cq.Workplane("XY").add(A27._guia().val().translate((E.C[0], E.C[1], 0)))
trilho = E.hardware()["elev_trilho"]
obst = guia.union(trilho)
zs = list(np.arange(E.Z_TRANSF[0] - 25.0, E.Z_TRANSF[1] + 25.1, 5.0))
angs = []
for z in zs:
    lo = E.ang_guia(z) + 29.0               # encostando (interfere)
    hi = E.ang_guia(z) + 70.0               # longe (livre)
    for _ in range(18):
        m = (lo + hi) / 2
        b = cq.Workplane("XY").sphere(E.R_B).translate(E.p(E.R_BOLA, m, z))
        if _vol_inter(b, obst) > 0.01:
            lo = m
        else:
            hi = m
    angs.append(round(hi, 2))
    print(f"z {z:.0f}: guia {E.ang_guia(z):.1f}  bola {hi:.2f}  (+{hi - E.ang_guia(z):.1f})")
f = Path(E.__file__).resolve().parent / "elevador_bola.json"
f.write_text(json.dumps({"z": [float(z) for z in zs], "ang": angs,
                         "nota": "angulo do centro da bola (r=28) encostada no trilho/guia; gerado por tools/tabela_bola.py"},
                        indent=1), encoding="utf8")
print("gravado", f)
