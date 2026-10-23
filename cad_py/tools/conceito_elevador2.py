"""Esboco 2 do elevador de fuso: tubo quase em pe no canto frente-direita (a frente da boca), furo no acrilico rente a
bandeja, motor + fixacao do fuso embaixo, caminho no topo ate o funil do magazine. So para conversar; nao e peca.
Sem gabinete nas imagens. Uso: python tools/conceito_elevador2.py <pasta>"""
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
from maquina_a import bandeja as B  # noqa: E402
from maquina_a import magazine as M  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402

pasta = Path(sys.argv[1])

# --- bandeja mais inclinada: ponto mais baixo no furo do tubo (EVA rebaixado no canto frente-direita)
B.INCL_X = B.INCL_Y = math.radians(6.5)
B.X_LOW, B.Y_LOW = 155.0, -155.0
B.Z_EVA_LOW = 1090.0

# --- tubo (eixo), furo de entrada, motor, caminho do topo
X, Y0, Y1 = 180.0, -180.0, -140.0      # eixo do tubo: canto frente-direita, inclina 40 mm para tras
Z0, Z1 = 1060.0, 1600.0                # pe (abaixo da divisoria) e topo
a, b = cq.Vector(X, Y0, Z0), cq.Vector(X, Y1, Z1)
n = (b - a).normalized()
L = (b - a).Length
incl = math.degrees(math.atan2(Z1 - Z0, abs(Y1 - Y0)))
z_bola_bandeja = B.Z_EVA_LOW + 19.0     # centro da bola no ponto baixo da bandeja
t = (z_bola_bandeja - 4 - Z0) / (Z1 - Z0)
c_furo = a + (b - a) * t                # centro do furo (bola entra caindo ~4 mm)
tubo = cilindro(50.0, L, a.toTuple(), n.toTuple()).cut(cilindro(44.0, L + 2, (a - n).toTuple(), n.toTuple()))
# furo: janela virada para a bandeja (-x e +y), um pouco maior que a bola
furo = cq.Workplane("XY").sphere(23.0).translate((c_furo.x - 22, c_furo.y + 6, c_furo.z + 2))
furo = furo.union(caixa(c_furo.x - 40, c_furo.x - 5, c_furo.y - 18, c_furo.y + 30, c_furo.z - 18, c_furo.z + 24))
tubo = tubo.cut(furo)
nucleo = cilindro(12.0, L - 10, (a + n * 5).toTuple(), n.toTuple())
hel = cq.Wire.makeHelix(45.0, L - 10, 15.0)
fil = cq.Workplane("XZ").center(15.0, 0).rect(10.0, 3.0).sweep(cq.Workplane().add(hel), isFrenet=True)
eixo_rot = cq.Vector(0, 0, 1).cross(n)
ang = math.degrees(math.acos(n.z))
fuso = cq.Workplane("XY").add(fil.val().rotate(cq.Vector(0, 0, 0), eixo_rot, ang).translate(a + n * 5)).union(nucleo)
motor = cq.Workplane("XY").add(caixa(-21.15, 21.15, -21.15, 21.15, -40.0, 0.0).val()
                                .rotate(cq.Vector(0, 0, 0), eixo_rot, ang).translate(a - n * 22))
mancal = cq.Workplane("XY").add(caixa(-28, 28, -28, 28, -20.0, 0.0).val().rotate(cq.Vector(0, 0, 0), eixo_rot, ang).translate(a))
# caminho do topo: sai do tubo para tras (junto a parede direita, por cima do eixo A) e vira para o funil
p_top = b + n * 5
p1 = cq.Vector(X, 60.0, Z1 - 10.0)
p2 = cq.Vector(M.X_FUNIL + 20, M.Y_MAG, M.Z_FUNIL_TOPO + 22.0)
calha = cilindro(44.0, (p1 - p_top).Length, p_top.toTuple(), (p1 - p_top).normalized().toTuple())
calha = calha.union(cilindro(44.0, (p2 - p1).Length, p1.toTuple(), (p2 - p1).normalized().toTuple()))
bola = cq.Workplane("XY").sphere(19.0).translate((c_furo.x - 30, c_furo.y + 8, z_bola_bandeja + 1))

conceito = {"tubo do elevador": tubo, "fuso": fuso, "motor": motor, "fixacao do fuso": mancal, "caminho ate o magazine": calha}

# --- colisoes: pecas fixas (menos A14, A38, A19 que saem), compradas, e os DOIS carros no curso inteiro
fora = ("A14", "A38", "A19")
fora_img = fora + ("A12", "A13")      # calcos e rodape serao recalculados para a bandeja nova
outros = {k: w for k, w in AS.pecas() if not k.startswith(fora)}
outros.update({k: w for k, w in {**AS.compradas(), **MT.hardware_fixo()}.items() if "patim" not in k and "solenoide" not in k})
col = {k: c7_interferencia(w, outros)["colisoes"] for k, w in conceito.items()}
carros = {}
for e in ("A", "B"):
    c0, c1 = MT.CURSO[e]
    for xc in (c0, c0 / 2, 0.0, c1 / 2, c1):
        for k, w in MT.corpos_carro(e).items():
            carros[f"carro {e} {k} @{xc:+.0f}"] = cq.Workplane("XY").add((w.val() if isinstance(w, cq.Workplane) else w).translate((xc, 0, 0)))
col_carros = {k: c7_interferencia(w, carros)["colisoes"] for k, w in conceito.items()}
print(f"tubo {L:.0f} mm, {incl:.0f} graus (inclina {abs(Y1 - Y0):.0f} mm para tras); furo com centro em z={c_furo.z:.0f}")
for k in conceito:
    print(f"  {k}: fixas {col[k] or 'livre'} | carros {col_carros[k] or 'livre'}")


def cena(arquivo, direcao, escala, foco, titulo):
    p = pv.Plotter(off_screen=True, window_size=(1500, 1700))
    p.set_background("white")
    for nome, w in AS.pecas():
        if nome.startswith(fora_img):
            continue
        p.add_mesh(R._pv(para_trimesh(w, 0.3, 0.5)), color=R.COR_PECA)
    for nome, w in {**AS.compradas(), **MT.hardware_fixo()}.items():
        p.add_mesh(R._pv(para_trimesh(w, 0.4, 0.5)), color="#9fd3e8" if nome == "tubo" else R.COR_HW,
                   opacity=0.6 if nome == "tubo" else 1)
    corpos = MT.corpos_bandeja()
    for nome in ("bandeja_mdf", "bandeja_eva"):
        w = corpos[nome].cut(cilindro(54.0, 800, (X, Y0 - 60, Z0 - 300), n.toTuple()))
        p.add_mesh(R._pv(para_trimesh(w, 0.5, 0.5)), color="#c8a878" if nome == "bandeja_mdf" else "#3a3a3a", opacity=0.35)
    cores = {"tubo do elevador": "#6fb6e8", "fuso": "#2a5bd2", "motor": "#444444", "fixacao do fuso": "#e8892b",
             "caminho ate o magazine": "#4ab04a"}
    for k, w in conceito.items():
        p.add_mesh(R._pv(para_trimesh(w, 0.3, 0.5)), color=cores[k], opacity=0.45 if k == "tubo do elevador" else 1)
    p.add_mesh(R._pv(para_trimesh(bola, 0.3, 0.5)), color="white", specular=0.6)
    rot = [((X - 30, Y0 - 30, Z0 - 40), "motor + fixacao do fuso (embaixo)"),
           ((c_furo.x - 40, c_furo.y + 40, c_furo.z + 10), "furo no acrilico: a bola entra aqui"),
           ((X, (Y0 + Y1) / 2, (Z0 + Z1) / 2), "tubo acrilico + fuso girando"),
           ((X, 0.0, Z1), "caminho ate o magazine"),
           ((M.X_FUNIL, M.Y_MAG, M.Z_FUNIL_TOPO), "funil do magazine")]
    p.add_point_labels(np.array([r[0] for r in rot], float), [r[1] for r in rot], font_size=15, point_size=10,
                       point_color="#dd2222", text_color="black", shape_color="#fff7d6", shape_opacity=0.9, always_visible=True)
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


cena("elevador2_iso.png", (0.6, -1.3, 0.7), 430, (40, -40, 1330), "Elevador de fuso no canto frente-direita (sem gabinete)")
cena("elevador2_pe.png", (-1.0, 0.35, 0.75), 110, (c_furo.x - 10, c_furo.y, c_furo.z), "Pe do elevador: furo no acrilico e bandeja descendo ate ele")
cena("elevador2_frente.png", (0, -1, 0.02), 430, (40, -40, 1330), "Vista de frente (como o jogador ve)")
