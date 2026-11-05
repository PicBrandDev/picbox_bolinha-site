"""Onde o solenoide entra no berco (carro A): imagens anotadas fechado e aberto. Uso: python ferramentas/render_solenoide.py <pasta>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

from common import render as R  # noqa: E402
from common.malha import para_trimesh  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402
from maquina_a import soltura as S  # noqa: E402
from maquina_a.pecas import A05_placa_carro as A5, A10_berco as B, A11_portinhola as P, A36_garfo as G  # noqa: E402

pasta = Path(sys.argv[1])
pasta.mkdir(parents=True, exist_ok=True)


def cena(ab, cam, nome, titulo, rot):
    p = pv.Plotter(off_screen=True, window_size=(1400, 1150))
    p.set_background("white")
    p.add_mesh(R._pv(para_trimesh(B.build(), 0.05, 0.2)), color="#e8b04a", opacity=0.55)
    for lado, cor in (("t", "#2a5bd2"), ("f", "#6f8fe0")):
        p.add_mesh(R._pv(para_trimesh(P.local(lado, ab), 0.05, 0.2)), color=cor)
    p.add_mesh(R._pv(para_trimesh(G.local("A", ab), 0.05, 0.2)), color="#33aa55")
    p.add_mesh(R._pv(para_trimesh(A5.build(None, "A"), 0.1, 0.3)), color="#cccccc", opacity=0.35)
    from common import hardware as hw
    exposto = S.Z_SOL_BASE - (S.Z_PINO_FECHADO + S.GARFO_H / 2) + 4.0 - (S.CURSO_PINO if ab else 0.0)   # embolo recolhe ao abrir
    p.add_mesh(R._pv(para_trimesh(hw.solenoide(S.X_SOL_FACE, S.Y_PINO, S.Z_SOL_BASE, exposto), 0.1, 0.3)), color="#d9534f")
    zc = S.Z_C if ab == 0 else S.Z_C - 40
    p.add_mesh(pv.Sphere(radius=S.R_B, center=(0, S.Y_C, zc)), color="white", specular=0.5)
    p.add_point_labels(np.array([r[0] for r in rot], float), [r[1] for r in rot], font_size=15, point_size=9,
                       point_color="#dd2222", text_color="black", shape_color="#fff7d6", shape_opacity=0.92, always_visible=True)
    c = np.array([15, -50, 1472.0])
    d = np.array(cam, float)
    d /= np.linalg.norm(d)
    p.camera.focal_point = c
    p.camera.position = c + d * 500
    p.camera.up = (0, 0, 1)
    p.camera.parallel_projection = True
    p.camera.parallel_scale = 70
    p.add_text(titulo, font_size=12, color="black")
    p.screenshot(str(pasta / nome))
    p.close()


xe = S.X_EMBOLO
rot = [((xe, S.Y_PINO, S.Z_SOL_BASE + 20), "SOLENOIDE (puxa 9,5 mm para cima)"),
       ((xe, S.Y_PINO, S.Z_PINO_FECHADO + 2), "garfo A36 no embolo"),
       ((S.X_ENGR[1], S.Y_PINO, S.Z_PINO_FECHADO), "pino da alavanca (portinhola de tras)"),
       ((S.X_BOCH_D[1], -60.0, 1490.0), "bochecha +X do berco: 2x M3 do solenoide"),
       ((S.X_ENGR[0], S.Y_C, S.Z_EIXO - 6), "engrenagens: as 2 portinholas abrem juntas"),
       ((0, S.Y_C, S.Z_C + 20), "bola parada no V das portinholas"),
       ((0, 0, S.Z_FACE_CARRO + 4), "placa do carro A (A05)")]
cena(0, (1.0, -1.3, 0.45), "solenoide_onde_fica.png", "Berco do carro A: onde fica o solenoide (vermelho), fechado", rot)
cena(S.ABERTURA, (1.0, -1.3, 0.45), "solenoide_aberto.png", "Solenoide puxou: portinholas abertas 60 graus, bola cai", rot[:3])
cena(0, (1.0, 0.0, 0.05), "solenoide_lado.png", "Vista pelo lado +X (lado do motor): solenoide em cima do pino", rot[:4])
print("ok")
