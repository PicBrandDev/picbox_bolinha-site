"""Corte da cabeca A27: guia de transferencia e caminho da bola ate a saida. Uso: python ferramentas/render_guia.py <pasta>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq  # noqa: E402
import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

from common import hardware as hw  # noqa: E402
from common import render as R  # noqa: E402
from common.features import caixa  # noqa: E402
from common.malha import para_trimesh  # noqa: E402
from maquina_a import elevador as E  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402
from maquina_a.pecas import A25_saida_elevador as A25, A27_cabeca_elevador as A27  # noqa: E402

pasta = Path(sys.argv[1])
cx, cy = E.C
corte = caixa(cx + 2, 400, -400, 400, 0, 3000)            # tira a metade do lado da camera (frente-direita)
a27 = A27.build().cut(corte.rotate((cx, cy, 0), (cx, cy, 1), -45))
trilho = E.hardware()["elev_trilho"]
z_guia = [1440, 1480, 1510, 1540, 1570, 1595, E.ZC_SAI]
g = E.giro_para_bola(1510)
p = pv.Plotter(off_screen=True, window_size=(1500, 1600))
p.set_background("white")
p.add_mesh(R._pv(para_trimesh(a27, 0.15, 0.3)), color="#9fd3e8")
p.add_mesh(R._pv(para_trimesh(trilho, 0.2, 0.4)), color="#555555")
for k in range(3):
    p.add_mesh(R._pv(para_trimesh(E.fuso_maquina(k, g), 0.3, 0.5)), color="#2a5bd2", opacity=0.25)
p.add_mesh(R._pv(para_trimesh(A25.build(), 0.2, 0.4)), color="#f0c419", opacity=0.6)
cores = ["#ffffff", "#ffe9a0", "#ffd84d", "#ffc000", "#ff9d00", "#ff7a00", "#e04e00"]
for z, cor in zip(z_guia, cores):
    p.add_mesh(R._pv(para_trimesh(hw.bola(E.p(E.R_BOLA, E.ang_bola(z), z), 38.0), 0.3, 0.5)), color=cor, specular=0.4)
fora = A25.caminho()[6][0]
p.add_mesh(R._pv(para_trimesh(hw.bola(fora, 38.0), 0.3, 0.5)), color="#c03000")
rot = [(E.p(E.R_BOLA, E.ANG_BOLA, 1440 + 22), "1 sobe no trilho de aluminio (280 graus)"),
       (E.p(E.R_TRILHO, E.ang_guia(1525), 1525), "2 guia helicoidal (A27): gira 130 graus subindo 110 mm"),
       (E.p(E.R_BOLA, E.ang_bola(1595), 1595 + 22), "3 trilho de cima (120): bola a 150, de frente para o campo"),
       (fora, "4 sai rolando pela janela para o piso da A25")]
p.add_point_labels(np.array([r[0] for r in rot], float), [r[1] for r in rot], font_size=15, point_size=9, point_color="#dd2222",
                   text_color="black", shape_color="#fff7d6", shape_opacity=0.92, always_visible=True)
c = np.array([cx - 10, cy + 10, 1530.0])
d = np.array([1.0, -1.0, 0.3]); d /= np.linalg.norm(d)
p.camera.focal_point = c; p.camera.position = c + d * 600; p.camera.up = (0, 0, 1)
p.camera.parallel_projection = True; p.camera.parallel_scale = 115
p.add_text("Cabeca A27 em corte: a bola nunca fica solta (cores = subindo)", font_size=13, color="black")
p.screenshot(str(pasta / "elevador_guia_corte.png"))
print("ok")
