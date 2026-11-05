"""Balancim A17 (pecinha verde) em corte: vista pelo lado do campo, metade da A16 cortada no vertice do V.
Uso: python ferramentas/render_balancim.py <pasta>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

from common import hardware as hw  # noqa: E402
from common import render as R  # noqa: E402
from common.features import caixa  # noqa: E402
from common.malha import para_trimesh  # noqa: E402
from maquina_a import magazine as M  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402
from maquina_a.pecas import A16_escapamento as A16, A17_balancim as A17  # noqa: E402

pasta = Path(sys.argv[1])
pasta.mkdir(parents=True, exist_ok=True)
corte = caixa(-300, M.X_TRAV, -300, 300, 0, 3000)          # so a metade do lado da parede (o V aparece em corte)
a16 = A16.build().intersect(corte)
servo = MT.hardware_fixo()["sg90"]


def cena(nome, titulo, ang, bolas, rot):
    p = pv.Plotter(off_screen=True, window_size=(1500, 1000))
    p.set_background("white")
    p.add_mesh(R._pv(para_trimesh(a16, 0.1, 0.3)), color="#e8b04a", opacity=0.9)
    p.add_mesh(R._pv(para_trimesh(servo, 0.1, 0.3)), color="#2a5bd2", opacity=0.5)
    p.add_mesh(R._pv(para_trimesh(A17.local("-", ang), 0.05, 0.2)), color="#14c43c")
    for c, cor in bolas:
        p.add_mesh(R._pv(para_trimesh(hw.bola(c, 38.0), 0.2, 0.4)), color=cor, specular=0.4)
    p.add_point_labels(np.array([r[0] for r in rot], float), [r[1] for r in rot], font_size=16, point_size=10,
                       point_color="#dd2222", text_color="black", shape_color="#fff7d6", shape_opacity=0.92, always_visible=True)
    c = np.array([M.X_TRAV, 0.0, 1458.0])
    p.camera.focal_point = c
    p.camera.position = c + np.array([600.0, 0, 0])
    p.camera.up = (0, 0, 1)
    p.camera.parallel_projection = True
    p.camera.parallel_scale = 48
    p.add_text(titulo, font_size=13, color="black")
    p.screenshot(str(pasta / nome))
    p.close()


x = M.X_TRAV + 30
b1 = (M.X_TRAV, M.Y_BOLA1, M.z_trav(M.Y_BOLA1))
b2 = (M.X_TRAV, M.Y_BOLA1 + 38.0, M.z_trav(M.Y_BOLA1 + 38.0))
eixo = (x, M.Y_PIVO, M.Z_PIVO)
cena("balancim_segura.png", "Servo a -15 graus: dedo de baixo em cima, segura a fila (frente da maquina a esquerda)", -M.ANG_ESCAPE,
     [(b1, "#ffd84d"), (b2, "white")],
     [((x, M.Y_DEDO1, M.z_trav(M.Y_DEDO1) - 16), "dedo de baixo (sobe ~10 mm acima do fundo do V)"),
      ((x, M.Y_DEDO2, M.z_trav(M.Y_DEDO2) - 28), "dedo de cima (abaixo do fundo do V)"),
      (eixo, "eixo do servo SG90"), ((x, b1[1], b1[2] + 21), "bola da vez"), ((x, b2[1], b2[2] + 21), "resto da fila")])
cena("balancim_solta.png", "Servo a +15 graus: dedo de cima sobe e segura a 2a bola; dedo de baixo desce e a 1a sai", M.ANG_ESCAPE,
     [((M.X_TRAV, -40.0, M.z_trav(-40.0)), "#ffd84d"), (b2, "white")],
     [((x, M.Y_DEDO2, M.z_trav(M.Y_DEDO2) - 16), "dedo de cima em cima"),
      ((x, M.Y_DEDO1, M.z_trav(M.Y_DEDO1) - 28), "dedo de baixo desceu"),
      ((x, -40.0, M.z_trav(-40.0) + 21), "bola da vez rolando para o berco")])
print("ok")
