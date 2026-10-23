"""Esboco do elevador de fuso inclinado (so para conversar o tracado, nao e peca).
Uso: python tools/conceito_elevador.py <pasta_saida> [y0 z0 y1 z1]"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq  # noqa: E402
import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

from common import render as R  # noqa: E402
from common.checks import c7_interferencia  # noqa: E402
from common.features import caixa, cilindro  # noqa: E402
from common.malha import para_trimesh  # noqa: E402
from maquina_a import assembly as AS  # noqa: E402
from maquina_a import magazine as M  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402
from maquina_a import verifica as V  # noqa: E402

pasta = Path(sys.argv[1])
X = float(__import__("os").environ.get("ELEV_X", "180.0"))   # eixo do tubo: 2 mm da lateral (raio 25); direita = +180
y0, z0, y1, z1 = (float(v) for v in sys.argv[2:6]) if len(sys.argv) >= 6 else (-180.0, 1010.0, 175.0, 1625.0)

a, b = cq.Vector(X, y0, z0), cq.Vector(X, y1, z1)
n = (b - a).normalized()
L = (b - a).Length
ang = math.degrees(math.atan2(z1 - z0, y1 - y0))
tubo = cilindro(50.0, L, a.toTuple(), n.toTuple()).cut(cilindro(44.0, L + 2, (a - n).toTuple(), n.toTuple()))
nucleo = cilindro(12.0, L, a.toTuple(), n.toTuple())
# helice indicativa (filete) dentro do tubo
passo = 45.0
hel = cq.Wire.makeHelix(passo, L, 15.0)
fil = cq.Workplane("XZ").center(15.0, 0).rect(10.0, 3.0).sweep(cq.Workplane().add(hel), isFrenet=True)
rot_ax = cq.Vector(0, 0, 1).cross(n)
ang_r = math.degrees(math.acos(n.z))
fil_sh = fil.val().rotate(cq.Vector(0, 0, 0), rot_ax, ang_r).translate(a)
motor = cq.Workplane("XY").add(caixa(-21.15, 21.15, -21.15, 21.15, -40.0, 0.0).val()
                                .rotate(cq.Vector(0, 0, 0), rot_ax, ang_r).translate(a - n * 2))
# calha de transferencia do topo ate o funil do magazine (A18)
topo = b + n * 0.0
funil = cq.Vector(M.X_FUNIL, M.Y_MAG, M.Z_FUNIL_TOPO + 25.0)
d = funil - topo
calha = cilindro(44.0, d.Length, topo.toTuple(), d.normalized().toTuple())

conceito = {"tubo do elevador": tubo, "nucleo do fuso": nucleo, "motor": motor, "calha de transferencia": calha}
# bola na janela de entrada do pe (vindo da bandeja)
_yb = float(__import__("os").environ.get("ELEV_BOLA_Y", "-150"))
_t = (_yb - y0) / (y1 - y0)
bola_entrada = cq.Workplane("XY").sphere(19.0).translate((X - 6.0, _yb, z0 + _t * (z1 - z0) - 3.0))

# colisoes com o que ja existe
outros = {}
for nome, w in AS.pecas():
    outros[nome] = w
for nome, w in {**AS.compradas(), **MT.hardware_fixo(), **MT.corpos_bandeja()}.items():
    outros[nome] = w
for nome, w in V.gabinete().items():
    outros[nome] = w
col = {}
for k, w in conceito.items():
    r = c7_interferencia(w, outros)
    col[k] = r["colisoes"]
print(f"tubo: {L:.0f} mm, inclinacao {ang:.0f} graus; base z={z0:.0f} (divisoria 1082-1100), topo z={z1:.0f}")
for k, v in col.items():
    print(" ", k, "->", v if v else "livre")

# imagens
cores = {"tubo do elevador": "#6fb6e8", "nucleo do fuso": "#2a5bd2", "motor": "#555555", "calha de transferencia": "#4ab04a"}


def cena(arquivo, direcao, escala, foco, titulo):
    p = pv.Plotter(off_screen=True, window_size=(1400, 1500))
    p.set_background("white")
    bate = {n for v in col.values() for n in v}
    for nome, w in AS.pecas():
        p.add_mesh(R._pv(para_trimesh(w, 0.3, 0.5)), color="#ff2a2a" if nome in bate else R.COR_PECA)
    for nome, w in {**AS.compradas(), **MT.hardware_fixo()}.items():
        p.add_mesh(R._pv(para_trimesh(w, 0.4, 0.5)), color=R.COR_HW)
    for nome, w in MT.corpos_bandeja().items():
        if nome == "divisoria":
            continue                                   # sem gabinete nas imagens (pedido do usuario)
        p.add_mesh(R._pv(para_trimesh(w, 0.5, 0.5)), color="#c8a878", opacity=0.3)
    for k, w in conceito.items():
        p.add_mesh(R._pv(para_trimesh(w, 0.3, 0.5)), color=cores[k], opacity=0.55 if k == "tubo do elevador" else 1)
    p.add_mesh(R._pv(para_trimesh(cq.Workplane("XY").add(fil_sh), 0.3, 0.5)), color="#2a5bd2")
    p.add_mesh(R._pv(para_trimesh(bola_entrada, 0.3, 0.5)), color="white", specular=0.6)
    c = np.array(foco)
    dd = np.array(direcao, float)
    dd /= np.linalg.norm(dd)
    p.camera.focal_point = c
    p.camera.position = c + dd * 3000
    p.camera.up = (0, 0, 1)
    p.camera.parallel_projection = True
    p.camera.parallel_scale = escala
    p.add_text(titulo, font_size=12, color="black")
    p.screenshot(str(pasta / arquivo))
    p.close()


cena("elevador_lado.png", (1, 0, 0), 420, (0, 0, 1330), "Vista pela direita: frente da maquina a ESQUERDA; vermelho = o que o tubo atravessa")
cena("elevador_iso.png", (0.9, -1.2, 0.7), 450, (0, 0, 1330), "Elevador de fuso (azul) na parede direita + calha ate o funil do magazine (verde); vermelho = conflito")
