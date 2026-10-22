"""Imagem geral da Maquina A: pecas impressas novas (laranja), compradas (cinza), gabinete em transparencia.
Uso: python tools/render_maquina.py <saida.png>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

from common import render as R  # noqa: E402
from common.malha import para_trimesh  # noqa: E402
from maquina_a import assembly as AS  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402

p = pv.Plotter(off_screen=True, window_size=(1400, 1600))
p.set_background("white")
for nome, w in AS.pecas():
    p.add_mesh(R._pv(para_trimesh(w, 0.2, 0.4)), color=R.COR_PECA)
for nome, w in AS.compradas().items():
    p.add_mesh(R._pv(para_trimesh(w, 0.3, 0.5)), color=R.COR_HW)
for nome, w in MT.hardware_fixo().items():
    p.add_mesh(R._pv(para_trimesh(w, 0.3, 0.5)), color="#9fd3e8" if nome == "tubo" else R.COR_HW, opacity=0.5 if nome == "tubo" else 1)
for nome, w in MT.corpos_bandeja().items():
    p.add_mesh(R._pv(para_trimesh(w, 0.5, 0.5)), color="#c8a878" if nome != "bandeja_eva" else "#333333", opacity=0.35)
c = np.array([0, -20, 1330.0])
d = np.array([-0.9, -1.4, 0.6])
d /= np.linalg.norm(d)
p.camera.focal_point = c
p.camera.position = c + d * 2500
p.camera.up = (0, 0, 1)
p.camera.parallel_projection = True
p.camera.parallel_scale = 330
p.add_text("Maquina A - pecas impressas (laranja), compradas (cinza)", font_size=11, color="black")
p.screenshot(sys.argv[1])
p.close()
