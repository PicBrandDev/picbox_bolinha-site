"""Imagens da montagem com as malhas REAIS das pecas impressas (saida/malhas.json) + compradas simplificadas.

  python render_m.py  ->  saida/imagens/*.png
"""
import base64
import json
import math
from pathlib import Path

import numpy as np
import pyvista as pv

import layout as L
from cena_m import Cena

pv.OFF_SCREEN = True
AQUI = Path(__file__).parent
S = AQUI / "saida"
IMG = S / "imagens"
COR = dict(imp="#2f6fd6", anda="#e07a22", comp="#9aa3a8", eva="#3f8f5f", correia="#2a2d30", bola="#d9dde3",
           transp="#7fb3e6", sensor="#c23b6b")
ANDA = {"carro", "alavanca", "carroA", "carroB"}
CORPO_IMP = {"Cabine": "carro", "Braco da comporta": "alavanca", "Carro A": "carroA", "Carro B": "carroB", "Anel": "carroB"}


def malhas_impressas():
    out = []
    for o in json.loads((S / "malhas.json").read_text(encoding="utf8")):
        V = np.frombuffer(base64.b64decode(o["v"]), np.float32).reshape(-1, 3).astype(float)
        T = np.frombuffer(base64.b64decode(o["t"]), np.uint32).reshape(-1, 3)
        f = np.hstack([np.full((len(T), 1), 3), T]).astype(np.int64)
        out.append((o, pv.PolyData(V, f)))
    return out


def cena(m, zc, th, cA, cB):
    """Lista (malha, cor, opacidade, peca) na pose pedida."""
    el = m.el
    itens = []
    for o, me in IMPRESSAS:
        for d in o["copias"]:
            mm = me.copy()
            off = np.array(d, float)
            if o["corpo"] == "carro":
                off += [0, 0, zc - el.zc_min]
            elif o["corpo"] == "carroA":
                off += [cA, 0, 0]
            elif o["corpo"] == "carroB":
                off += [cB, 0, 0]
            if o["corpo"] == "alavanca" and th:
                mm.rotate_vector((0, 1, 0), -th, point=el.piv, inplace=True)
            mm.translate(off, inplace=True)
            cor = COR["transp"] if o["peca"] in ("Tubo inferior", "Tubo superior") else (
                COR["anda"] if o["corpo"] in ANDA else COR["imp"])
            itens.append((mm, cor, 0.45 if cor == COR["transp"] else 1.0, o["peca"]))
    c = Cena(m)
    c.pose(zc=zc, th=th, cA=cA, cB=cB)
    for n, i in c.id.items():
        pc = c.peca[n]
        tp = L.PECAS.get(pc, ("?",))[0]
        if tp == "impressa" or pc in ("Gabinete", "Tela", "Batente") or c.tipo[i] == "sphere":
            continue
        cc, R, h = c._c[i], c._R[i], c.meio[i]
        T = np.eye(4)
        T[:3, :3], T[:3, 3] = R, cc
        if c.tipo[i] == "box":
            me = pv.Box(bounds=(-h[0], h[0], -h[1], h[1], -h[2], h[2]))
        else:
            me = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), radius=h[0], height=2 * h[1], resolution=32)
        me = me.transform(T, inplace=False)
        cor = COR["eva"] if pc.startswith("EVA") else COR["correia"] if pc.startswith(("Correia", "Esteira")) else \
            COR["sensor"] if pc in ("Sensor do bolso", "LED IR / fototransistor 5 mm") else COR["comp"]
        itens.append((me, cor, 1.0, pc))
    return itens


def foto(nome, itens, foco, direcao, escala, bolas=(), rotulos=(), tam=(1600, 1100), titulo="", esconde=(), vidro=()):
    p = pv.Plotter(off_screen=True, window_size=tam)
    p.set_background("#f4f6f4")
    for me, cor, op, pc in itens:
        if any(pc.startswith(x) for x in esconde):
            continue
        if pc in vidro:
            op = 0.3
        p.add_mesh(me, color=cor, opacity=op, smooth_shading=True, specular=0.25, show_edges=False)
    for b in bolas:
        p.add_mesh(pv.Sphere(radius=L.R, center=b, theta_resolution=40, phi_resolution=30), color=COR["bola"],
                   smooth_shading=True, specular=0.9, specular_power=40)
    if rotulos:
        p.add_point_labels(np.array([r[1] for r in rotulos], float), [r[0] for r in rotulos], font_size=17,
                           point_size=9, point_color="#c23b6b", text_color="#111111", shape_color="#ffffff",
                           shape_opacity=0.85, always_visible=True)
    d = np.array(direcao, float)
    d /= np.linalg.norm(d)
    p.camera.focal_point = foco
    p.camera.position = np.array(foco) + d * 2000
    p.camera.up = (0, 0, 1)
    p.camera.parallel_projection = True
    p.camera.parallel_scale = escala
    if titulo:
        p.add_text(titulo, position="upper_left", font_size=13, color="#111111")
    p.enable_anti_aliasing("ssaa")
    p.screenshot(str(IMG / nome))
    p.close()


def main():
    global IMPRESSAS
    IMG.mkdir(parents=True, exist_ok=True)
    IMPRESSAS = malhas_impressas()
    m = L.M()
    el = m.el
    bolso = tuple(m.bola_bolso)
    # 1. geral
    it = cena(m, el.zc_min + 160, el.ang_baixa, -40.0 - m.dA, 55.0)
    presa = (-40.0, m.y_bola, m.zs)
    fila = [(x, el.y_bola, m.f_fila(x) + L.R) for x in (150.0, 124.0, 98.0, 72.0)]
    bolas = [presa, bolso] + fila
    rot = [("Carro A + eletroima", (-40, 60, 395)), ("Anel no carro B", (55, m.y_bola, m.zb + 4)),
           ("Bandeja (EVA)", (-120, 90, 70)), ("Fila", (40, 145, 65)), ("Elevador", (192, 150, 250)),
           ("Bolso de pega", (193, 72, 380)), ("Motor eixo A", (-184, 22, 340)), ("Motor eixo B", (-184, 22, 20))]
    foto("01_geral.png", it, (0, 100, 210), (-0.75, -1.0, 0.62), 255, bolas, rot, titulo="Montagem completa (azul = impressa, laranja = impressa que anda, cinza = comprada)")
    foto("02_frente.png", it, (0, 100, 210), (0, -1, 0.0001), 228, bolas, (), titulo="De frente, como o jogador ve")
    foto("03_lado.png", it, (0, 100, 210), (1, 0, 0.0001), 228, bolas, (), titulo="Lado direito (a tela fica a direita da imagem)")
    # 2. pega no bolso
    it = cena(m, el.zc_max, el.ang_baixa, m.cA[1], 0.0)
    rot = [("Eletroima (1 mm acima da bola)", (m.x_pega, m.y_bola, m.face_ima + 7)), ("Bola no bolso", bolso),
           ("Batente com EVA", (197, 56, 362)), ("Sensor do bolso", (198.5, 72.7, 352)),
           ("Rampa (vem do elevador)", (192, 110, 360)), ("Carro A", (m.cA[1], 43, 400))]
    foto("04_pega.png", it, (192, 75, 365), (-0.45, -1.0, 0.35), 45, [bolso], rot, vidro=("Carro A",), titulo="Pega: o carro A para em cima do bolso e liga o ima (sem o perfil e o trilho de cima)",
         esconde=("Perfil 2020 A", "Trilho MGN12 A", "Patim MGN12H A", "Prateleira", "Esteira A", "Gancho", "Bloco direito", "Bloco esquerdo", "Correia A", "Polia tensora A", "Ponta fixa"))
    # 3. elevador no topo
    cab = (el.x_bola, el.y_bola, el.zc_max + el.z_piso_berco(el.x_bola, el.y_bola) + L.R)
    it = cena(m, el.zc_max, el.ang_baixa, -60.0, 0.0)
    rot = [("Cabine no topo (o berco inclina para a frente)", cab), ("Rampa ate o bolso", (192, 100, 352)),
           ("Motor N20", (191, 140, 405)), ("Tubo transparente", (178, 129, 300))]
    foto("05_elevador_topo.png", it, (190, 110, 360), (-1.0, -0.6, 0.7), 70, [cab, bolso], rot, titulo="Elevador no topo: a bola rola da cabine para a rampa (sem o perfil de cima e sem o tubo de cima)",
         esconde=("Perfil 2020 A", "Trilho MGN12 A", "Patim MGN12H A", "Prateleira", "Esteira A", "Gancho", "Bloco direito", "Bloco esquerdo", "Correia A", "Polia tensora A", "Ponta fixa", "Tubo superior", "Carro A", "Eletroima"))
    # 4. fila e comporta
    cab0 = (el.x_bola, el.y_bola, el.zc_min + el.z_piso_berco(el.x_bola, el.y_bola) + L.R)
    it = cena(m, el.zc_min, el.ang_baixa, -60.0, 0.0)
    rot = [("Lamina da comporta (servo)", (178, 142, 30)), ("Cabine embaixo", cab0), ("Fila", (120, 143, 50)),
           ("Servo", (100, 100, 30))]
    foto("06_comporta.png", it, (155, 135, 30), (-0.7, -1.0, 0.9), 62, [cab0] + fila, rot, titulo="Comporta: o servo deixa passar uma bola por vez para a cabine (sem a bandeja e o tubo de baixo)",
         esconde=("Bandeja", "EVA", "Tubo inferior", "Perfil 2020 B", "Trilho MGN12 B", "Correia B", "Carro B", "Anel", "Patim MGN12H B", "Esteira B", "Bloco direito", "LED"))
    # 5. carro B, anel e bandeja
    it = cena(m, el.zc_min, el.ang_baixa, -60.0, 0.0)
    rot = [("Anel (furo 38)", (0, m.y_bola, m.zb + 3)), ("LED / sensor IR", (27.5, m.y_bola, m.zb - 14.5)),
           ("Carro B", (0, 43, 81)), ("Esteira B", (60, 6, 45)), ("Bandeja + EVA", (-60, 100, 60))]
    foto("07_anel.png", it, (0, 70, 80), (-0.6, -1.0, 0.8), 80, [], rot, titulo="Carro B: o anel e a barreira infravermelha que conta o acerto",
         esconde=("Perfil 2020 A", "Trilho MGN12 A", "Prateleira", "Esteira A", "Gancho", "Carro A", "Patim MGN12H A", "Eletroima", "Correia A"))
    print(sorted(x.name for x in IMG.glob("*.png")))


if __name__ == "__main__":
    main()
