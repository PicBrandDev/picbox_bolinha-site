"""Sequencia da carga: fila esperando no escapamento, servo solta UMA bola, bola entra no berco (carro A na carga).
Sem gabinete. Uso: python ferramentas/render_carga.py <pasta>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq  # noqa: E402
import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

from common import hardware as hw  # noqa: E402
from common import render as R  # noqa: E402
from common.malha import para_trimesh  # noqa: E402
from maquina_a import magazine as M  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402
from maquina_a.pecas import A16_escapamento as A16, A17_balancim as A17, A26_entrada_berco as A26  # noqa: E402

pasta = Path(sys.argv[1])
pasta.mkdir(parents=True, exist_ok=True)
fixos = [(A16.build(), "#e8b04a", 0.4), (A26.build(), "#d9534f", 0.55), (MT.modulo("A15").build(None, "-"), "#c9c9c9", 1.0),
         (MT.hardware_fixo()["sg90"], "#2a5bd2", 1.0), (MT.hardware_fixo()["tubo"], "#9fd3e8", 0.35)]
carro = []
for k, w in MT.corpos_carro("A").items():
    sh = (w.val() if isinstance(w, cq.Workplane) else w).translate((M.X_CARGA, 0, 0))
    if k.startswith(("A10", "A11")):
        carro.append((cq.Workplane("XY").add(sh), "#e8892b", 0.3))
fila = [(M.X_TRAV, M.Y_BOLA1 + k * 2 * M.R_B, None) for k in range(0, 2)]
fila = [(x, y, M.z_trav(y)) for x, y, _ in fila]
tubo = [M.eixo_tubo(x)[:2] + (M.z_tubo(x),) for x in (M.X_TUBO[0] + 25, M.X_TUBO[0] + 63)]
tubo = [(x, M.Y_MAG, z) for x, _, z in tubo]
curva = [c for c in M.pontos_bola(3.0) if c[1] < M.Y_CURVA_B0 and c[0] < M.X_LINGUA - 1]


def cena(nome, titulo, ang, bolas, rot, cam=(0.9, -0.55, 1.1), escala=88, com_carro=True):
    p = pv.Plotter(off_screen=True, window_size=(1500, 1250))
    p.set_background("white")
    for w, cor, op in fixos + (carro if com_carro else []):
        p.add_mesh(R._pv(para_trimesh(w, 0.15, 0.4)), color=cor, opacity=op)
    p.add_mesh(R._pv(para_trimesh(A17.local("-", ang), 0.1, 0.3)), color="#14c43c")
    for c, cor in bolas:
        p.add_mesh(R._pv(para_trimesh(hw.bola(c, 38.0), 0.2, 0.4)), color=cor, specular=0.5)
    p.add_point_labels(np.array([r[0] for r in rot], float), [r[1] for r in rot], font_size=15, point_size=9,
                       point_color="#dd2222", text_color="black", shape_color="#fff7d6", shape_opacity=0.92, always_visible=True)
    c = np.array([-168.0, -10.0, 1465.0])
    d = np.array(cam, float)
    d /= np.linalg.norm(d)
    p.camera.focal_point = c
    p.camera.position = c + d * 600
    p.camera.up = (0, 0, 1)
    p.camera.parallel_projection = True
    p.camera.parallel_scale = escala
    p.add_text(titulo, font_size=13, color="black")
    p.screenshot(str(pasta / nome))
    p.close()


BR, AM = "white", "#ffd84d"           # bola da vez em amarelo
d1 = (M.X_TRAV + 3, M.Y_DEDO1, M.z_trav(M.Y_DEDO1) - 14)
d2 = (M.X_TRAV + 3, M.Y_DEDO2, M.z_trav(M.Y_DEDO2) - 14)
cena("carga_1_espera.png", "1) Espera: o dedo de baixo segura a fila (servo -15 graus)", -M.ANG_ESCAPE,
     [(fila[0], AM), (fila[1], BR)] + [(t, BR) for t in tubo],
     [(fila[0], "bola da vez (parada no dedo de baixo)"), (d1, "dedo de baixo EM CIMA"), (d2, "dedo de cima embaixo"),
      (tubo[0], "fila no tubo do magazine")], com_carro=False)
cena("carga_2_solta.png", "2) Carro A parado na carga (x=-140): servo vai a +15 graus e solta UMA bola", M.ANG_ESCAPE,
     [((M.X_TRAV, -22.0, M.z_trav(-22.0)), AM), (fila[1], BR)] + [(t, BR) for t in tubo],
     [((M.X_TRAV, -22.0, M.z_trav(-22.0) + 22), "bola da vez rolando (3 graus)"), (d2, "dedo de cima SOBE e segura a 2a bola"),
      (d1, "dedo de baixo desce")], com_carro=True)
cena("carga_3_curva.png", "3) A bola faz a curva da A26 e entra no berco pelas linguas", M.ANG_ESCAPE,
     [(curva[len(curva) // 2], AM), (fila[1], BR)] + [(t, BR) for t in tubo],
     [(curva[len(curva) // 2], "curva em V R18,5"), ((M.X_LINGUA, M.Y_CANTO, M.Z_FIM - 20), "linguas dentro do furo do berco")])
cena("carga_4_berco.png", "4) Bola no berco (para no batente). Servo volta a -15: a fila desce uma posicao", -M.ANG_ESCAPE,
     [((M.X_CARGA, M.Y_CANTO, M.Z_FIM), AM), (fila[0], BR)] + [(tubo[0], BR)],
     [((M.X_CARGA, M.Y_CANTO, M.Z_FIM + 22), "bola no berco: carro A pode sair para o jogo"),
      (fila[0], "proxima bola ja esperando no dedo de baixo")])
print("ok")
