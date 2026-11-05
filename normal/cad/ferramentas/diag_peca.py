"""Diagnostico de uma peca: faces em overhang (posicao na maquina) e, para a A16, pontos do caminho da bola que colidem.
Uso: python ferramentas/diag_peca.py A15 [var]"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402

from common import fab  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402


def overhang(mod, var):
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    mesa = mod.impressao(var).val()
    maq = mod.build(None, var).val()
    z0 = mesa.BoundingBox().zmin
    lim = -math.cos(math.radians(45)) - 0.02
    for fm, fq in zip(mesa.Faces(), maq.Faces()):
        if fm.geomType() == "CYLINDER" and BRepAdaptor_Surface(fm.wrapped).Cylinder().Radius() * 2 <= fab.TEARDROP_ACIMA_DE + 0.2:
            continue
        v, t = fm.tessellate(0.05, 0.2)
        if not t:
            continue
        P = np.array([p.toTuple() for p in v])
        T = np.array(t)
        a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
        cr = np.cross(b - a, c - a)
        ar = np.linalg.norm(cr, axis=1)
        ok = ar > 1e-12
        nz = np.zeros(len(T))
        nz[ok] = cr[ok, 2] / ar[ok]
        cz = (a[:, 2] + b[:, 2] + c[:, 2]) / 3
        sel = ok & (nz < lim) & (nz >= -0.999) & (cz > z0 + 0.05)
        A = ar[sel].sum() / 2
        if A > 1:
            print(f"  overhang {A:7.1f} mm2  {fm.geomType():9s} centro na maquina {[round(x, 1) for x in fq.Center().toTuple()]}")


def caminho():
    import cadquery as cq
    from common import hardware as hw
    from common.checks import c7_interferencia
    from maquina_a import magazine as M
    from maquina_a.pecas import A17_balancim as A17
    apoios = dict(MT.corpos_magazine())
    outros = MT.corpos_contexto_caminho()
    for k in [k for k in outros if "A11" in k]:
        apoios[k] = outros.pop(k)
    outros.pop("A17.-", None)
    for i, c in enumerate(M.pontos_bola(6.0)):
        b1 = hw.bola((c[0], c[1], c[2] + 0.4), 2 * M.R_B)
        b2 = hw.bola((c[0], c[1], c[2] + 0.4), 2 * (M.R_B + fab.FOLGA_BOLA_RADIAL))
        r1 = c7_interferencia(b1, apoios)["colisoes"]
        r2 = c7_interferencia(b2, outros)["colisoes"]
        if r1 or r2:
            print(f"  ponto {i:3d} {[round(x, 1) for x in c]} apoios={r1} outros={r2}")


if __name__ == "__main__":
    pid = sys.argv[1]
    mod = MT.modulo(pid)
    var = sys.argv[2] if len(sys.argv) > 2 else MT.var_principal(mod)
    print(pid, var)
    overhang(mod, var)
    if pid == "A16" or "--caminho" in sys.argv:
        caminho()
