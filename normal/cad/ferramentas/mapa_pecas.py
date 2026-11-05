"""Mapa da Maquina A: pecas com nome e o caminho da bola numerado (sem gabinete).
Uso: python ferramentas/mapa_pecas.py <pasta_saida>"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq  # noqa: E402
import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

from common import render as R  # noqa: E402
from common.features import cilindro  # noqa: E402
from common.malha import para_trimesh  # noqa: E402
from maquina_a import assembly as AS  # noqa: E402
from maquina_a import bandeja as B  # noqa: E402
from maquina_a import layout as L  # noqa: E402
from maquina_a import magazine as M  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402
from maquina_a import soltura as S  # noqa: E402

pasta = Path(sys.argv[1])

from maquina_a import elevador as EL  # noqa: E402

NOMES = {
    "A01": "A01 bloco do motor", "A02": "A02 bloco do tensor", "A04": "A04 deslizador do tensor",
    "A05": "A05 placa do carro", "A07": "A07 presilhas da correia", "A09": "A09 BOCA (buraco, sobe/desce com o carro B)",
    "A10": "A10 BERCO de soltura (pendurado no carro A)", "A11": "A11 portinholas do alcapao", "A36": "A36 garfo do solenoide",
    "A12": "A12 calcos da bandeja", "A13": "A13 rodape da bandeja",
    "A20": "A20 base do elevador (piso + rolamento)", "A21": "A21 fuso (3 segmentos)", "A22": "A22 tampa do elevador",
    "A23": "A23 calha ate o magazine", "A24": "A24 suporte do motor do elevador", "A25": "A25 saida do elevador",
    "A15": "A15 saida do magazine (curva)", "A16": "A16 escapamento (travessia + servo)", "A26": "A26 entrada do berco (curva + linguas)", "A17": "A17 balancim do escapamento",
    "A18": "A18 entrada do magazine (funil)", "A19": "A19 suporte da entrada",
}
UNICO = {"A01", "A02", "A04", "A05", "A07"}   # rotular uma vez por eixo
SO_UM = {"A21"}                                # rotular uma vez (varias variantes)


def cena(arquivo, direcao, escala, foco, titulo, rotulos):
    p = pv.Plotter(off_screen=True, window_size=(1700, 1900))
    p.set_background("white")
    for _pid, _var, nome, w in AS.pecas():
        p.add_mesh(R._pv(para_trimesh(w, 0.3, 0.5)), color=R.COR_PECA)
    for nome, w in {**AS.compradas(), **MT.hardware_fixo()}.items():
        vidro = nome in ("tubo", "elev_acrilico")
        p.add_mesh(R._pv(para_trimesh(w, 0.4, 0.5)), color="#9fd3e8" if vidro else R.COR_HW, opacity=0.45 if vidro else 1)
    for nome, w in MT.corpos_bandeja().items():
        if nome == "divisoria":
            continue                                   # sem gabinete nas imagens (pedido do usuario)
        p.add_mesh(R._pv(para_trimesh(w, 0.5, 0.5)), color="#c8a878", opacity=0.25)
    pts = np.array([r[0] for r in rotulos], float)
    p.add_point_labels(pts, [r[1] for r in rotulos], font_size=15, point_size=10, point_color="#dd2222",
                       text_color="black", shape_color="#fff7d6", shape_opacity=0.9, always_visible=True)
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


# rotulos das pecas: centro da caixa de cada peca (um por eixo nas pecas de eixo)
rot_pecas = []
vistos = set()
for pid, var, nome, w in AS.pecas():
    chave = (pid, var if pid in UNICO and pid not in SO_UM else "")
    if chave in vistos:
        continue
    vistos.add(chave)
    bb = w.val().BoundingBox()
    c = ((bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2, (bb.zmin + bb.zmax) / 2)
    txt = NOMES.get(pid, pid)
    if pid in UNICO:
        txt += f" (eixo {var})"
    rot_pecas.append((c, txt))
rot_pecas += [((0, 0, L.Z_EIXO_A), "EIXO A (de cima): leva a bola"), ((0, 0, L.Z_EIXO_B), "EIXO B (de baixo): leva o buraco"),
              (((M.X_TUBO[0] + M.X_TUBO[1]) / 2, M.Y_MAG, M.z_tubo(0) + 30), "tubo do magazine (~10 bolas)"),
              ((EL.C[0], EL.C[1], 1380.0), "ELEVADOR: tubo Ø100 + fuso + trilho")]

cena("mapa_pecas_iso.png", (0.9, -1.3, 0.8), 470, (0, 0, 1330), "Mapa das pecas (vista de frente-direita, de cima)", rot_pecas)
cena("mapa_pecas_frente.png", (0, -1, 0.05), 430, (0, 0, 1330), "Mapa das pecas (vista de frente, como o jogador ve)", rot_pecas)

# caminho da bola numerado
fluxo = [
    ((EL.p(70, 135)[0], EL.p(70, 135)[1], 1140), "1 bola rola na bandeja e entra pelo furo do pe do tubo"),
    ((EL.C[0], EL.C[1], 1380), "2 fuso gira e sobe a bola apoiada no trilho"),
    ((EL.X_RAIA, -20, EL.z_raia(-20) + 25), "3 sai no topo e desce a calha ate o funil"),
    ((0, M.Y_MAG, M.z_tubo(0) + 10), "4 fila no tubo do magazine (atras do eixo A)"),
    ((M.X_TRAV, 10, M.z_trav(10) + 25), "5 escapamento solta UMA bola"),
    ((M.X_TRAV + 20, M.Y_CANTO, M.Z_FIM + 25), "6 calha de carga leva ate o berco (carro A em x=-140)"),
    ((-140, S.Y_C, S.Z_C + 30), "7 berco segura a bola; carro A oscila"),
    ((0, S.Y_C, (S.Z_C + L.Z_BOCA) / 2), "8 jogador aperta: alcapao abre, queda de 250 mm"),
    ((0, S.Y_C, L.Z_BOCA + 10), "9 boca (carro B oscila): acertou se passa no furo"),
]
cena("caminho_da_bola.png", (0.9, -1.3, 0.8), 470, (0, 0, 1330), "Caminho da bola (1 a 9)", fluxo)
