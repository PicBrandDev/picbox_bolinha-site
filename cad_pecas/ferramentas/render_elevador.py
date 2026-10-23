"""Imagens do elevador modelado (A20..A25 + compradas), sem gabinete. Uso: python ferramentas/render_elevador.py <pasta>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq  # noqa: E402
import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

from common import render as R  # noqa: E402
from common.malha import para_trimesh  # noqa: E402
from maquina_a import assembly as AS  # noqa: E402
from maquina_a import bandeja as B  # noqa: E402
from maquina_a import elevador as E  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402
from maquina_a.pecas import A25_saida_elevador as A25  # noqa: E402

pasta = Path(sys.argv[1])
pasta.mkdir(parents=True, exist_ok=True)
ELEV = ("A20", "A21", "A22", "A23", "A24", "A25", "A27")
CORES = {"A20": "#e8892b", "A21": "#2a5bd2", "A22": "#d9534f", "A23": "#4ab04a", "A24": "#8e5bd2", "A25": "#f0c419", "A27": "#9fd3e8"}

# bolas: na bandeja junto do furo, subindo no trilho (2), girando no topo, no piso da saida, na calha
z_sobe = 1300.0
g = E.giro_para_bola(z_sobe)
x, y, _ = E.p(72.0, 135.0)
z_tr = (E.Z_TRANSF[0] + E.Z_TRANSF[1]) / 2
bolas = [(x, y, B.z_eva(x, y) + E.R_B), E.p(E.R_BOLA, E.ANG_BOLA, z_sobe), E.p(E.R_BOLA, E.ang_bola(z_tr), z_tr),
         E.p(E.R_BOLA, E.ANG_BOLA_TOPO, E.ZC_SAI), A25.caminho()[-3][0], (E.X_RAIA, 0.0, E.z_raia(0.0))]


def cena(arquivo, direcao, escala, foco, titulo, rotulos, mostrar_resto=True):
    p = pv.Plotter(off_screen=True, window_size=(1500, 1700))
    p.set_background("white")
    for _pid, _var, nome, w in AS.pecas():
        pid = nome[:3]
        if pid == "A21":
            continue
        if pid in ELEV:
            p.add_mesh(R._pv(para_trimesh(w, 0.2, 0.4)), color=CORES[pid])
        elif mostrar_resto:
            p.add_mesh(R._pv(para_trimesh(w, 0.3, 0.5)), color="#d8d8d8")
    for k in range(3):
        p.add_mesh(R._pv(para_trimesh(E.fuso_maquina(k, g), 0.2, 0.4)), color=CORES["A21"])
    hw = MT.hardware_fixo()
    for nome, w in {**(AS.compradas() if mostrar_resto else {}), **hw}.items():
        if not mostrar_resto and not nome.startswith("elev_"):
            continue
        vidro = nome in ("tubo", "elev_acrilico")
        p.add_mesh(R._pv(para_trimesh(w, 0.3, 0.5)), color="#9fd3e8" if vidro else "#707070", opacity=0.35 if vidro else 1)
    for nome, w in MT.corpos_bandeja().items():
        if nome == "divisoria":
            continue                                       # sem gabinete nas imagens (pedido do usuario)
        p.add_mesh(R._pv(para_trimesh(w, 0.5, 0.5)), color="#c8a878" if nome == "bandeja_mdf" else "#3a3a3a", opacity=0.3)
    for c in bolas:
        p.add_mesh(R._pv(para_trimesh(cq.Workplane("XY").sphere(E.R_B).translate(c), 0.2, 0.4)), color="white", specular=0.6)
    if rotulos:
        p.add_point_labels(np.array([r[0] for r in rotulos], float), [r[1] for r in rotulos], font_size=15, point_size=9,
                           point_color="#dd2222", text_color="black", shape_color="#fff7d6", shape_opacity=0.9,
                           always_visible=True)
    c = np.array(foco)
    d = np.array(direcao, float)
    d /= np.linalg.norm(d)
    p.camera.focal_point = c
    p.camera.position = c + d * 3000
    p.camera.up = (0, 0, 1)
    p.camera.parallel_projection = True
    p.camera.parallel_scale = escala
    p.add_text(titulo, font_size=13, color="black")
    p.screenshot(str(pasta / arquivo))
    p.close()


cx, cy = E.C
rot_geral = [((cx, cy, 1035.0), "A24 suporte + motor (embaixo da divisoria)"),
             ((cx - 40, cy + 40, 1090.0), "A20 base: piso + pe do tubo"),
             ((*E.p(50, 135)[:2], 1140.0), "furo de entrada no acrilico"),
             ((cx, cy, 1380.0), "A21 fuso (3 segmentos) + trilho Ø8"),
             ((cx, cy, 1650.0), "A22 tampa (presa na lateral direita)"),
             ((95.0, -150.0, 1615.0), "A25 saida"),
             ((E.X_RAIA, 0.0, 1610.0), "A23 calha (3 graus)"),
             ((112.0, 70.0, 1568.0), "funil do magazine (A18)")]
cena("elevador_iso.png", (-0.9, -1.3, 0.7), 330, (60, -60, 1350), "Elevador modelado (sem gabinete)", rot_geral)
cena("elevador_campo.png", (-1.0, 0.9, 0.35), 300, (cx, cy, 1350), "Elevador visto do campo (de tras-esquerda)", [
    ((*E.p(50, 135)[:2], 1140.0), "furo de entrada (35..232 graus)"),
    (E.p(E.R_TRILHO, E.ANG_TRILHO, 1450.0), "trilho-guia Ø8"),
    ((*E.p(52, 150)[:2], 1600.0), "janela de saida da A27 (126..175)"),
    (E.p(E.R_TRILHO, E.ang_bola(z_tr) - 30, z_tr), "guia helicoidal: leva a bola de 280 a 150 graus"),
    (E.p(E.R_BOLA, E.ANG_BOLA, z_sobe), "bola subindo no trilho")], mostrar_resto=False)
cena("elevador_pe.png", (-1.0, 0.35, 0.45), 130, (cx - 10, cy + 10, 1070), "Pe do elevador: bandeja, furo, piso, motor", [
    (bolas[0], "bola chegando"), ((cx, cy, 1102.0), "piso conico"), ((cx, cy, 995.0), "NEMA 17")], mostrar_resto=False)
cena("elevador_topo.png", (-1.0, 0.7, 0.8), 120, (cx - 25, cy + 5, 1605), "Topo: guia leva a bola ao trilho de cima; ela sai rolando pela janela", [
    (bolas[3], "bola saindo pela janela"), (bolas[4], "piso da saida"), ((E.X_RAIA, -80.0, E.z_raia(-80.0)), "calha")])
print("ok")
