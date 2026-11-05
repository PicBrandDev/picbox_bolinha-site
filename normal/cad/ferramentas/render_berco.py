"""Imagens do conjunto da soltura (fechado e aberto). python ferramentas/render_berco.py <pasta>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pyvista as pv

from common import render as R
from common.malha import para_trimesh
from maquina_a import montagem as MT
from maquina_a import soltura as S
from maquina_a.pecas import A05_placa_carro as A5, A10_berco as B, A11_portinhola as P, A36_garfo as G

pasta = sys.argv[1]


def cena(ab, cam, nome):
    p = pv.Plotter(off_screen=True, window_size=(1100, 900))
    p.set_background("white")
    p.add_mesh(R._pv(para_trimesh(B.build(), 0.05, 0.2)), color=R.COR_PECA)
    for lado in "tf":
        p.add_mesh(R._pv(para_trimesh(P.local(lado, ab), 0.05, 0.2)), color=R.COR_MOVEL)
    p.add_mesh(R._pv(para_trimesh(G.local("A", ab), 0.05, 0.2)), color="#33aa77")
    p.add_mesh(R._pv(para_trimesh(A5.build(None, "A"), 0.1, 0.3)), color="#ccaa77", opacity=0.6)
    for v in MT.hardware_carro("A").values():
        p.add_mesh(R._pv(para_trimesh(v, 0.1, 0.3)), color=R.COR_HW)
    zc = S.Z_C if ab == 0 else S.Z_C - 40
    p.add_mesh(pv.Sphere(radius=S.R_B, center=(0, S.Y_C, zc)), color="white", specular=0.5)
    c = np.array([10, -50, 1475.0])
    d = np.array(cam, float)
    d /= np.linalg.norm(d)
    p.camera.focal_point = c
    p.camera.position = c + d * 400
    p.camera.up = (0, 0, 1)
    p.camera.parallel_projection = True
    p.camera.parallel_scale = 62
    p.add_text("fechado" if ab == 0 else "aberto 60 graus", font_size=11, color="black")
    p.screenshot(f"{pasta}/{nome}.png")
    p.close()


cena(0, (-1, -1.6, 0.5), "soltura_fechada")
cena(S.ABERTURA, (-1, -1.6, 0.5), "soltura_aberta")
cena(0, (1.2, -1.0, -0.4), "soltura_fechada_lado_solenoide")
