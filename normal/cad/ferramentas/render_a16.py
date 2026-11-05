"""Imagens anotadas da A16 (calha de carga) no contexto: A15, A17 + SG90, bloco do tensor A, carro A na carga.
Sem gabinete. Uso: python ferramentas/render_a16.py <pasta>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq  # noqa: E402
import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

from common import hardware as hw  # noqa: E402
from common import render as R  # noqa: E402
from common.malha import para_trimesh  # noqa: E402
from maquina_a import eixo as EX  # noqa: E402
from maquina_a import magazine as M  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402
from maquina_a.pecas import A16_escapamento as A16  # noqa: E402
from maquina_a.pecas import A26_entrada_berco as A26  # noqa: E402

pasta = Path(sys.argv[1])
pasta.mkdir(parents=True, exist_ok=True)
X_CARGA = M.X_CARGA

ctx = {}
for pid in ("A15", "A18"):
    ctx[pid] = (MT.modulo(pid).build(None, "-"), "#d8d8d8", 1.0)
ctx["A17"] = (MT.modulo("A17").local("-", -M.ANG_ESCAPE), "#4ab04a", 1.0)
ctx["A02 A (bloco do tensor)"] = (MT.modulo("A02").build(None, "A"), "#bbbbbb", 0.3)
ctx["A04 A"] = (MT.modulo("A04").build(None, "A"), "#bbbbbb", 0.3)
ctx["sg90"] = (MT.hardware_fixo()["sg90"], "#2a5bd2", 1.0)
ctx["tubo"] = (MT.hardware_fixo()["tubo"], "#9fd3e8", 0.4)
for k, w in EX.fixos("A", EX.lados_fc("A")).items():
    ctx[f"A.{k}"] = (EX.para_maquina(w, "A"), "#707070", 0.15)
for k, w in MT.corpos_carro("A").items():
    sh = (w.val() if isinstance(w, cq.Workplane) else w).translate((X_CARGA, 0, 0))
    cor = "#e8892b" if k.startswith(("A10", "A11")) else "#a0a0a0"
    ctx[f"carro {k}"] = (cq.Workplane("XY").add(sh), cor, 0.3)
parede = cq.Workplane("XY").box(2, 140, 120).translate((M.X_PAREDE - 1, -10, 1460))

# bolas: fila (3), primeira parada no dedo, uma no trecho final, uma no berco
bolas = [(M.X_TRAV, y, M.z_trav(y)) for y in (M.Y_BOLA1 + 2 * M.PASSO_DEDOS - 49.0, M.Y_BOLA1 + M.PASSO_DEDOS)]
_pc = [c for c in M.pontos_bola(4.0) if c[1] < M.Y_CURVA_B0 and c[0] < M.X_LINGUA - 1]
bolas += [(M.X_TRAV, M.Y_BOLA1, M.z_trav(M.Y_BOLA1)), _pc[len(_pc) // 2], (X_CARGA, M.Y_CANTO, M.Z_FIM)]


def cena(arquivo, direcao, escala, foco, titulo, rotulos, up=(0, 0, 1)):
    p = pv.Plotter(off_screen=True, window_size=(1600, 1500))
    p.set_background("white")
    p.add_mesh(R._pv(para_trimesh(A16.build(), 0.1, 0.3)), color="#e8b04a")
    p.add_mesh(R._pv(para_trimesh(A26.build(), 0.1, 0.3)), color="#d9534f")
    for nome, (w, cor, op) in ctx.items():
        p.add_mesh(R._pv(para_trimesh(w, 0.2, 0.4)), color=cor, opacity=op)
    p.add_mesh(R._pv(para_trimesh(parede, 0.5, 0.5)), color="#c8a878", opacity=0.25)
    for c in bolas:
        p.add_mesh(R._pv(para_trimesh(hw.bola(c, 38.0), 0.2, 0.4)), color="white", specular=0.6)
    p.add_point_labels(np.array([r[0] for r in rotulos], float), [r[1] for r in rotulos], font_size=14, point_size=9,
                       point_color="#dd2222", text_color="black", shape_color="#fff7d6", shape_opacity=0.92,
                       always_visible=True)
    c = np.array(foco)
    d = np.array(direcao, float)
    d /= np.linalg.norm(d)
    p.camera.focal_point = c
    p.camera.position = c + d * 3000
    p.camera.up = up
    p.camera.parallel_projection = True
    p.camera.parallel_scale = escala
    p.add_text(titulo, font_size=12, color="black")
    p.screenshot(str(pasta / arquivo))
    p.close()


z_t = M.z_trav
rot = [
    ((M.X_TRAV, 38.0, M.Z_CURVA1 + 5), "1 junta A15/A16 (y=40, 2 pinos)"),
    ((M.X_TRAV + 10, M.Y_JUNTA_B, M.z_trav(M.Y_JUNTA_B) - 28), "junta A16/A26 (y=-34, 2 pinos)"),
    ((M.X_TRAV, 15.0, z_t(15.0) + 22), "2 travessia em V, x=-184,5 (desce 3 graus para a frente)"),
    ((M.X_TRAV + 8, M.Y_DEDO2, z_t(M.Y_DEDO2) - 10), "3 dedo de cima (segura a 2a bola)"),
    ((M.X_TRAV + 8, M.Y_DEDO1, z_t(M.Y_DEDO1) - 10), "4 dedo de baixo (segura a fila)"),
    ((M.X_PAREDE + 12, M.Y_PIVO, M.Z_PIVO - 12), "5 SG90 deitado na parede + postes"),
    ((-182.0, -52.0, M.Z_FIM + 28), "6 A26: curva em V R18,5 (sem degrau, sem batente)"),
    ((M.X_LINGUA + 2, M.Y_CANTO, M.Z_FIM - 18), "7 linguas 8x2,8 entram no furo do berco"),
    ((M.X_PAREDE + 2, 0.0, A16.Z_PLACA[0] + 6), "8 placa A16 (2x M4)"),
    ((M.X_PAREDE + 2, -62.0, A16.Z_PLACA[0] + 6), "9 placa A26 (2x M4)"),
    ((-178.0, 25.0, 1535.0), "pe do bloco do tensor A (por cima)"),
    ((X_CARGA, M.Y_CANTO, M.Z_FIM + 30), "berco no carro A em x=-140"),
]
cena("A16_A26_iso.png", (1.0, -1.1, 0.75), 120, (-175, -10, 1470), "A16 escapamento (amarelo) + A26 entrada do berco (vermelho)", rot)
cena("A16_A26_cima.png", (0.0, 0.0, 1.0), 110, (-170, -10, 1470), "A16 vista de cima (frente da maquina = embaixo)", rot, up=(0, 1, 0))
cena("A16_A26_baixo.png", (0.9, -1.0, -0.6), 110, (-175, -10, 1465), "A16 vista de frente-direita, por baixo", rot)
cena("A16_A26_frente.png", (0.0, -1.0, 0.05), 100, (-175, -10, 1470), "A16 vista de frente", rot)
print("ok")
