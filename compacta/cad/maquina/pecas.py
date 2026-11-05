"""Gera as STLs (e STEPs) de TODAS as pecas impressas da maquina completa, a partir do mesmo modelo checado.

  python pecas.py            # tudo
  python pecas.py Base Anel  # so algumas

Cada peca = uniao das caixas/cilindros/aneis dela no modelo (layout.geometria)
           - pecas compradas que entram nela (motor, fim de curso, correia, eixo da tensora...) com 0,25 mm de folga
           - furos dos parafusos (passante, piloto para rosquear no PETG, rebaixo e corredor da chave na propria peca)
           - detalhes que o modelo de caixas nao tem (dentes das presilhas, pinos, rasgos, orelhas do servo...).
Depois gira para a posicao de impressao, assenta em Z 0 e exporta. Saida: saida/stl/<peca>__xN.stl e saida/step/.
Checa cada malha: fechada, um corpo so, cabe na mesa, area em balanco (precisa de suporte?), volume e horas.
"""
import json
import math
import re
import sys
import time
from pathlib import Path

import numpy as np
import cadquery as cq

import layout as L

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "saida"
FOLGA_COMPRADA = 0.25
LASCAS = {}

PASSANTE = {"M2": 2.4, "M3": 3.4, "M5": 5.5, "madeira": 4.0}
PILOTO = {"M2": 1.8, "M3": 2.7, "M5": 4.2, "madeira": 2.8}
CABECA = {"M2": (4.4, 2.3), "M3": (6.2, 3.3), "M5": (9.2, 5.3), "madeira": (7.6, 3.6)}

# como cada peca vai na mesa: (rotacao maquina -> mesa, quantidade, observacao de suporte)
POS = {
    "Base": ("Z", 1, "nao"),
    "Guia impressa inferior": ("+Y", 1, "nao (aba do T de 2 mm sem suporte)"),
    "Guia impressa superior": ("+Y", 1, "nao"),
    "Cabine": ("Z", 1, "so embaixo do bloco da correia"),
    "Espacador": ("+Y", 1, "nao"),
    "Suporte do motor": ("Z-", 1, "nao"),
    "Tubo inferior": ("+Y", 1, "nao"),
    "Tubo superior": ("+Y", 1, "nao"),
    "Fila": ("Z", 1, "nao (nervuras embaixo do piso)"),
    "Rampa": ("Z", 1, "nao (piso macico)"),
    "Suporte do servo": ("Z", 1, "nao"),
    "Braco da comporta": ("Z-", 3, "nao"),
    "Fila esquerda": ("Z", 1, "nao (nervuras embaixo do piso)"),
    "Bloco esquerdo": ("-X", 2, "nao"),
    "Bloco direito": ("+X", 2, "nao"),
    "Suporte do NEMA de cima": ("-X", 1, "nao"),
    "Suporte do NEMA de baixo": ("-X", 1, "nao"),
    "Carro A": ("-X", 1, "sim: embaixo da presilha, da prateleira e da nervura"),
    "Carro B": ("+Y", 1, "nao"),
    "Anel": ("Z-", 1, "nao"),
    "Bandeja esquerda": ("-Y", 1, "nao (impressa em pe, frente na mesa)"),
    "Bandeja do meio": ("-Y", 1, "nao (impressa em pe, frente na mesa)"),
    "Bandeja direita": ("-Y", 1, "nao (impressa em pe, frente na mesa)"),
    "Prateleira da esteira": ("Z", 1, "nao"),
    "Gancho da prateleira": ("-X", 3, "nao"),
    "Ponta fixa da esteira": ("Z", 1, "nao"),
}
# pecas iguais: so a instancia do eixo A vira STL (a do B e a mesma, contada em POS)
SO_EIXO_A = {"Bloco esquerdo", "Bloco direito"}
# instancias que viram arquivos separados (mesmo nome de peca, formas diferentes)
SEPARAR = {"Prateleira da esteira": ("prat_estA_0", "prat_estA_0_fora", "prat_aba_0") +
           tuple(f"prat_estA_0_trav_{j}" for j in range(5)), "Ponta fixa da esteira": ("est_fixaA",)}
SEPARAR_NOME = {"Prateleira da esteira": ("esquerda", "direita"), "Ponta fixa da esteira": ("A (prateleira)", "B (piso)")}


def rot_mesa(k):
    return {"Z": np.eye(3), "Z-": L.rot(rx=180), "+X": L.rot(ry=90), "-X": L.rot(ry=-90),
            "+Y": L.rot(rx=-90), "-Y": L.rot(rx=90)}[k]


def local(R, t):
    """Location que leva o referencial local (caixa centrada) para a maquina: plano com X = R[:,0] e Z = R[:,2]."""
    R = np.asarray(R, float)
    u, _, vt = np.linalg.svd(R)
    R = u @ vt
    pl = cq.Plane(origin=tuple(float(v) for v in t), xDir=tuple(float(v) for v in R[:, 0]),
                  normal=tuple(float(v) for v in R[:, 2]))
    return cq.Location(pl)


def q2R(q):
    from cena_m import q2R as f
    return f(q)


def solido(e, cresce=0.0):
    t = e["tipo"]
    h = np.array(e["meio"], float)
    if t == "box":
        h = h + cresce
        s = cq.Solid.makeBox(2 * h[0], 2 * h[1], 2 * h[2], pnt=cq.Vector(-h[0], -h[1], -h[2]))
    elif t == "cylinder":
        r, hl = h[0] + cresce, h[1] + cresce
        s = cq.Solid.makeCylinder(r, 2 * hl, pnt=cq.Vector(0, 0, -hl), dir=cq.Vector(0, 0, 1))
    elif t == "anel":
        r0, r1, hz = h
        s = (cq.Workplane("XY").workplane(offset=-hz).circle(r1 + cresce).circle(max(0.1, r0 - cresce))
             .extrude(2 * hz).val())
    else:
        raise ValueError(t)
    return s.moved(local(q2R(e["quat"]), e["pos"]))


def mundo(m: L.M):
    """Geometria na pose de referencia (cabine no fundo, comporta em 0, carros em 0), em coordenadas da maquina."""
    el = m.el
    out = []
    for e in L.geometria(m):
        e = dict(e)
        p = np.array(e["pos"], float)
        if e["corpo"] == "carro":
            p = p + [0, 0, el.zc_min]
        elif e["corpo"] == "alavanca":
            p = p + np.array(el.piv)
        e["pos"] = p.tolist()
        out.append(e)
    return out


def aabb(e):
    R = q2R(e["quat"])
    h = np.array(e["meio"], float)
    if e["tipo"] == "box":
        ext = np.abs(R) @ h
    elif e["tipo"] == "cylinder":
        ax = R[:, 2]
        ext = np.abs(ax) * h[1] + h[0] * np.sqrt(np.clip(1 - ax ** 2, 0, 1))
    else:
        ext = np.array([h[1], h[1], h[2]])
    c = np.array(e["pos"])
    return c - ext, c + ext


def bitola(tipo):
    t = tipo.lower()
    if t.startswith("madeira"):
        return "madeira"
    return re.match(r"(m\d)", t).group(1).upper()


def cilindro(d, p0, dirv, t0, t1):
    dirv = np.array(dirv, float)
    a = np.array(p0) + dirv * t0
    return cq.Solid.makeCylinder(d / 2, t1 - t0, pnt=cq.Vector(*a), dir=cq.Vector(*dirv))


def varrer(sol, v, n=8):
    """Une copias deslocadas (rasgo)."""
    v = np.array(v, float)
    out = sol
    for i in range(1, n + 1):
        out = out.fuse(sol.translate(cq.Vector(*(v * i / n))))
    return out


def furos(m, peca, fx, el):
    """Cortadores dos parafusos que tocam a peca."""
    cut = []
    for f in fx:
        p0 = np.array(f["p0"], float)
        if f["corpo"] == "carro":
            p0[2] += el.zc_min
        d = np.array(f["dir"], float)
        b = bitola(f["tipo"])
        Lm = f["L"]
        envolve = peca in (f["prende"], *f["atravessa"]) or (peca == f["rosca"] and f["prende"] != f["rosca"])
        if not envolve and peca != f["rosca"]:
            continue
        porca = "porca" in f["tipo"] or "martelo" in f["tipo"]
        auto = f.get("insert") if f.get("insert") is not None else (
            L.PECAS.get(f["rosca"], ("?",))[0] == "impressa" and not porca)
        rasgo = None
        if f["nome"] == "eixo_polia_baixo" and peca in ("Guia impressa inferior", "Base"):
            rasgo = (0, 0, -2.0)                   # esticador da correia: o parafuso desce 2 mm
        if f["nome"].startswith("eixo_tens_") and peca == "Bloco direito":
            rasgo = (-6.0, 0, 0)                  # esticador: a tensora anda 6 mm para a esquerda
        if peca == f["rosca"] and auto and peca != f["prende"]:
            c = cilindro(PILOTO[b], p0, d, 0, Lm + 0.6)
        else:
            c = cilindro(PASSANTE[b], p0, d, -0.5, Lm + 0.5)
        if rasgo:
            c = varrer(c.translate(cq.Vector(*(-np.array(rasgo) * 0))), rasgo)
        cut.append(c)
        if peca == f["prende"]:
            dc, hc = CABECA[b]
            corr = f.get("corredor", 60.0) if f["nome"].startswith("band_") else 40.0
            cab = cilindro(dc, p0, d, -corr, 0.0)
            if rasgo:
                cab = varrer(cab, rasgo)
            cut.append(cab)
        if f["nome"] == "eixo_polia_baixo" and peca == "Base":
            # porca M3 presa na bochecha: sextavado de 5,9 entre faces, aberto para cima (a porca entra de cima)
            pz = p0 + d * (Lm - 3.6)
            hexa = (cq.Workplane(cq.Plane(origin=tuple(pz), xDir=(1, 0, 0), normal=tuple(d)))
                    .polygon(6, 5.9 / math.cos(math.pi / 6)).extrude(2.8).val())
            fenda = cq.Solid.makeBox(5.9, 2.8, 20, pnt=cq.Vector(pz[0] - 2.95, pz[1] - 2.8, pz[2] - 2.0))
            cut.append(varrer(hexa.fuse(fenda), (0, 0, -2.0)))
    return cut


def dentes(x0, x1, y_face, sentido, z0, z1, eixo="x"):
    """Ranhuras GT2 (passo 2, 1,1 de largura, 0,8 de fundo) numa parede da fenda da correia."""
    out = []
    a = x0 + 0.5
    while a + 1.1 <= x1 - 0.3:
        if eixo == "x":
            ya, yb = sorted((y_face, y_face + sentido * 0.8))
            out.append(cq.Solid.makeBox(1.1, yb - ya, z1 - z0, pnt=cq.Vector(a, ya, z0)))
        else:            # dentes ao longo de Z numa parede em X (cabine)
            xa, xb = sorted((y_face, y_face + sentido * 0.8))
            out.append(cq.Solid.makeBox(xb - xa, z1 - z0, 1.1, pnt=cq.Vector(xa, z0, a)))
        a += 2.0
    return out


def detalhes(m, peca, el):
    """(somar, cortar): o que o modelo de caixas nao tem."""
    add, cut = [], []
    zc = el.zc_min
    if peca in ("Carro A", "Carro B"):
        k = peca[-1]
        zp = m.zpA if k == "A" else m.zpB
        zcor = zp + m.dz_correia
        yr = m.y_correia + 20 * 2 / (2 * math.pi)
        cut += dentes(-8, 8, yr - 0.95, -1, zcor - 3.3, zcor + 3.3)
    if peca == "Cabine":
        # presilhas da correia no bloco da direita: fenda de 1,9 mm no ramo preso (x_ida), dentes do lado da polia
        xi = el.x_ida
        y0, y1 = el.y_correia[0] - 0.3, el.y_correia[1] + 0.3
        for z0, z1 in ((9.5, 21.0), (29.0, 37.5)):         # abertas embaixo e em cima do bloco (Z 10..37)
            cut.append(cq.Solid.makeBox(1.9, y1 - y0, z1 - z0, pnt=cq.Vector(xi - 0.95, y0, zc + z0)))
            for d in dentes(z0 + zc, z1 + zc, xi - 0.95, -1, y0, y1, eixo="z"):
                cut.append(d)
    if peca == "Guia impressa inferior":
        for x in (178.0, 204.0):
            add.append(cq.Solid.makeCylinder(2.0, 6.0, pnt=cq.Vector(x, 195.5, 200.0)))
    if peca == "Guia impressa superior":
        for x in (178.0, 204.0):
            cut.append(cq.Solid.makeCylinder(2.25, 7.0, pnt=cq.Vector(x, 195.5, 199.5)))
    if peca in ("Tubo inferior", "Tubo superior"):
        for x in (181.0, 199.0):
            if peca == "Tubo inferior":
                add.append(cq.Solid.makeBox(6, 4, 10, pnt=cq.Vector(x, 124.0, 190.0)))
                add.append(cq.Solid.makeCylinder(1.4, 5.0, pnt=cq.Vector(x + 3, 126.0, 200.0)))
            else:
                add.append(cq.Solid.makeBox(6, 4, 10, pnt=cq.Vector(x, 124.0, 200.0)))
                cut.append(cq.Solid.makeCylinder(1.65, 6.0, pnt=cq.Vector(x + 3, 126.0, 199.5)))
    if peca == "Suporte do servo":
        for xa, xb, xh in ((84.0, 88.5, 86.1), (111.5, 116.0, 113.9)):
            add.append(cq.Solid.makeBox(xb - xa, 7.9, 12.0, pnt=cq.Vector(xa, 96.0, 21.0)))
            cut.append(cq.Solid.makeCylinder(0.9, 9.0, pnt=cq.Vector(xh, 104.5, 27.0), dir=cq.Vector(0, -1, 0)))
    if peca == "Braco da comporta":
        for x in (104.0, 107.0):
            cut.append(cq.Solid.makeCylinder(0.75, 12.0, pnt=cq.Vector(x, 115.0, 25.0), dir=cq.Vector(0, 1, 0)))
    if peca == "Anel":
        for x in (-10.0, 10.0):              # cabecas dos M3x8 do patim ficam embaixo das costas
            for z in (m.zpB - 10, m.zpB + 10):
                cut.append(cq.Solid.makeCylinder(3.6, 5.0, pnt=cq.Vector(x, 45.5, z), dir=cq.Vector(0, 1, 0)))
        cut.append(cq.Solid.makeCylinder(1.5, 46.0, pnt=cq.Vector(-23.0, m.y_bola, m.zb - 14.5), dir=cq.Vector(1, 0, 0)))
    if peca == "Rampa":
        sx, sy = L.SENSOR_BOLSO
        zt = m.z_rampa(sx, sy)
        zb0 = el.z_rampa - 70 * math.tan(math.radians(el.incl_rampa)) - 6
        # janela do sensor no piso do bolso e canal dos fios ate embaixo da rampa
        cut.append(cq.Solid.makeBox(4.8, 9.4, 12.0, pnt=cq.Vector(sx - 2.4, sy - 4.7, zt - 8.0)))
        cut.append(cq.Solid.makeBox(4.0, 6.0, 40.0, pnt=cq.Vector(sx - 2.0, sy - 3.0, zb0 - 5.0)))
    if peca == "Suporte do NEMA de cima":     # furo do cabo do motor (aba e parede)
        cut.append(cq.Solid.makeCylinder(5.0, 10.0, pnt=cq.Vector(-212.0, m.y_correia, 312.0), dir=cq.Vector(1, 0, 0)))
    if peca == "Suporte do NEMA de baixo":    # furo do cabo do motor e do fim de curso de baixo
        cut.append(cq.Solid.makeCylinder(4.0, 10.0, pnt=cq.Vector(-212.0, m.y_correia + 25.3, 25.0), dir=cq.Vector(1, 0, 0)))
    if peca == "Base":
        for x in (186.0, 196.0):          # cabecas dos M3x12 da guia ficam embutidas por baixo
            cut.append(cq.Solid.makeCylinder(3.1, 4.3, pnt=cq.Vector(x, 195.5, -1.0)))
    return add, cut


def construir(m, peca, so=None, fx=None, geo=None):
    el = m.el
    geo = geo or mundo(m)
    fx = fx or L.fixadores(m)
    junta = {"Base": ("Base", "Batente")}.get(peca, (peca,))          # o batente e impresso junto com a base
    proprios = [e for e in geo if e["peca"] in junta and (so is None or e["nome"] in so)]
    if peca in SO_EIXO_A:
        proprios = [e for e in proprios if e["nome"].endswith("_A")]
    if peca == "Gancho da prateleira":          # os 3 sao iguais: so o primeiro
        proprios = [e for e in proprios if e["nome"].endswith("_0")]
    if not proprios:
        return None
    lo = np.min([aabb(e)[0] for e in proprios], 0) - 1
    hi = np.max([aabb(e)[1] for e in proprios], 0) + 1
    corpo = solido(proprios[0], 0.02)               # 0,02 mm a mais: faces encostadas viram sobreposicao (uniao limpa)
    outros = [solido(e, 0.02) for e in proprios[1:]]
    add, cut = detalhes(m, peca, el)
    if so is None or peca not in SEPARAR:
        outros += add
    if outros:
        corpo = corpo.fuse(*outros)
    # compradas que entram na peca
    for e in geo:
        tp = L.PECAS.get(e["peca"], ("?",))[0]
        if tp == "impressa" or e["peca"] in ("Gabinete", "Tela", "EVA 5 mm") or e["corpo"].startswith("esteira"):
            continue
        a, b = aabb(e)
        if np.all(b > lo) and np.all(a < hi):
            cut.append(solido(e, FOLGA_COMPRADA))
    cut += furos(m, peca, fx, el)
    if cut:
        corpo = corpo.cut(*cut)
    if peca == "Cabine":                          # base plana para a mesa (embaixo do macico do berco)
        corpo = corpo.intersect(cq.Solid.makeBox(400, 400, 300, pnt=cq.Vector(0, 0, el.zc_min - L.BASE_CABINE)))
    if peca == "Rampa":                           # base plana para a mesa
        zb0 = el.z_rampa - 70 * math.tan(math.radians(el.incl_rampa)) - 6
        corpo = corpo.intersect(cq.Solid.makeBox(400, 400, 200, pnt=cq.Vector(0, 0, zb0)))
    corpo = corpo.clean()
    # lascas soltas que os cortes deixam (dentes, rasgos): ficam de fora e entram no relatorio
    sols = sorted(corpo.Solids(), key=lambda x: -x.Volume())
    LASCAS[peca] = [round(x.Volume() / 1000, 3) for x in sols[1:]]
    return sols[0] if len(sols) > 1 else corpo


def exportar(peca, sol, rot_k, sufixo=""):
    import trimesh
    R = rot_mesa(rot_k)
    s = sol.moved(local(R, (0, 0, 0)))
    bb = s.BoundingBox()
    s = s.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    nome = re.sub(r"[^a-z0-9]+", "_", (peca + sufixo).lower()
                  .translate(str.maketrans("áàãâéêíóôõúç", "aaaaeeiooouc"))).strip("_")
    (SAIDA / "stl").mkdir(parents=True, exist_ok=True)
    (SAIDA / "step").mkdir(parents=True, exist_ok=True)
    q = POS[peca][1]
    arq = SAIDA / "stl" / f"{nome}{'__x' + str(q) if q > 1 else ''}.stl"
    cq.exporters.export(cq.Workplane().add(s), str(arq), tolerance=0.03, angularTolerance=0.15)
    cq.exporters.export(cq.Workplane().add(sol), str(SAIDA / "step" / f"{nome}.step"))
    # checagem da malha (solda vertices repetidos da triangulacao e regrava)
    me = trimesh.load(str(arq), force="mesh")
    if not me.is_watertight:
        me.merge_vertices(digits_vertex=3)
        me.update_faces(me.nondegenerate_faces())
        me.remove_unreferenced_vertices()
        trimesh.repair.fill_holes(me)
        trimesh.repair.fix_normals(me)
        me.export(str(arq))
    corpos = len(me.split(only_watertight=False))
    ext = me.bounds[1] - me.bounds[0]
    n = me.face_normals
    a = me.area_faces
    zc = me.triangles_center[:, 2]
    baixo = (n[:, 2] < -0.71) & (zc > 0.3)          # face virada para baixo a mais de 45 graus, fora da mesa
    balanco = float(a[baixo].sum())
    vol = float(me.volume) / 1000
    return dict(peca=peca + sufixo, arquivo=arq.name, lascas_cm3=LASCAS.get(peca, []), quantidade=q, posicao=rot_k, suporte=POS[peca][2],
                fechada=bool(me.is_watertight), corpos=corpos, mesa_mm=[round(float(x), 1) for x in sorted(ext[:2], reverse=True)],
                altura_mm=round(float(ext[2]), 1), vol_cm3=round(vol, 1), massa_g=round(vol * 1.27 * 0.75, 0),
                horas=round(q * (vol * 0.75 / 11 + 0.2), 1), balanco_cm2=round(balanco / 100, 1),
                valido=bool(sol.isValid()))


def cabe(l):
    out = []
    a, b = l["mesa_mm"]
    for nome, (X, Y, Z) in (("A 260", (260, 260, 250)), ("B 220", (220, 220, 250)), ("C 220", (220, 220, 250))):
        reto = a <= X - 10 and b <= Y - 10
        diag = (a + b) / math.sqrt(2) <= X - 10 and b <= X - 10
        if l["altura_mm"] <= Z - 5 and (reto or diag):
            out.append(nome if reto else nome + " (diagonal)")
    return out


def main():
    t0 = time.time()
    m = L.M()
    geo = mundo(m)
    fx = L.fixadores(m)
    pedidas = sys.argv[1:] or list(POS)
    res = []
    for peca in pedidas:
        try:
            if peca in SEPARAR:
                nomes = [e["nome"] for e in geo if e["peca"] == peca]
                grupo1 = [n for n in nomes if n in SEPARAR[peca]]
                grupo2 = [n for n in nomes if n not in SEPARAR[peca]]
                for g, suf in ((grupo1, SEPARAR_NOME[peca][0]), (grupo2, SEPARAR_NOME[peca][1])):
                    sol = construir(m, peca, set(g), fx, geo)
                    res.append(exportar(peca, sol, POS[peca][0], " " + suf))
            else:
                sol = construir(m, peca, None, fx, geo)
                if sol is None:
                    print("sem geometria:", peca)
                    continue
                res.append(exportar(peca, sol, POS[peca][0]))
        except Exception as ex:          # noqa: BLE001
            res.append(dict(peca=peca, erro=repr(ex)))
        l = res[-1]
        if "erro" not in l:
            l["cabe"] = cabe(l)
            l["ok"] = l["fechada"] and l["corpos"] == 1 and bool(l["cabe"]) and l["valido"]
        for x in res[-2:] if l.get("peca", "").startswith(("Prateleira", "Ponta")) else res[-1:]:
            if "erro" not in x and "cabe" not in x:
                x["cabe"] = cabe(x)
                x["ok"] = x["fechada"] and x["corpos"] == 1 and bool(x["cabe"]) and x["valido"]
            print(f"{time.time() - t0:6.0f}s", x, flush=True)
    SAIDA.mkdir(exist_ok=True)
    arq = SAIDA / "impressao.json"
    velho = json.loads(arq.read_text(encoding="utf8")) if arq.exists() and sys.argv[1:] else []
    novos = {l["peca"] for l in res}
    tudo = [l for l in velho if l["peca"] not in novos] + res
    arq.write_text(json.dumps(tudo, indent=1, ensure_ascii=False), encoding="utf8")


if __name__ == "__main__":
    main()
