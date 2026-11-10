"""Checagens da maquina completa. Grava validacao.json (e imprime um resumo).

  python checagem.py

 1. interferencias entre pecas paradas (todas as duplas de pecas diferentes)
 2. carros A e B no curso inteiro x tudo; cabine e comporta do elevador x pecas novas; esteiras x tudo
 3. bola: bolso, chegada do ima, bola presa indo da pega ate a casa, queda em todo o curso, anel, bandeja ate a fila
 4. parafusos: atravessa, pega, nao fura, parede em volta da rosca, chave chega na etapa
 5. envelope 440 x 430 x 230 e janela da tela
"""
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

import layout as L
from cena_m import Cena

AQUI = Path(__file__).resolve().parent
FOLGA = 1.0          # folga minima entre o que anda e o resto (R2: era 0,5)
FOLGA_IMA = 0.5      # o ima chega perto da bola de proposito (gap da pega)
GX, GY, GZ = L.GX, L.GY, L.GZ

SOBREPOSICAO_PREVISTA = {
    frozenset(("Torre superior", "Motor N20")): "o berco da torre abraca o motor",
    frozenset(("Torre inferior", "Polia de baixo")): "a polia desce na janela do pe; o eixo passa na placa de tras",
    frozenset(("Torre inferior", "Sensor de fenda")): "a placa do sensor passa pela janela da placa de tras",
    frozenset(("Torre superior", "Sensor de fenda")): "a placa do sensor passa pela janela da placa de tras",
    frozenset(("Polia de baixo", "Correia")): "a correia abraca a polia",
    frozenset(("Polia do motor", "Correia")): "a correia abraca a polia",
    frozenset(("Servo", "Fila")): "o servo entra no suporte (impresso junto com a fila)",
    frozenset(("Torre superior", "Polia do motor")): "a polia do motor passa por uma janela no teto da torre",
}
PREVISTO = {frozenset(k) for k in SOBREPOSICAO_PREVISTA}
for k in ("A", "B"):
    PREVISTO |= {frozenset(p) for p in [
        (f"NEMA 17 {k}", f"Bloco esquerdo {'de cima' if k == 'A' else 'de baixo'}"),
        (f"Polia GT2 20T {k}", f"Correia {k}"), (f"Polia tensora {k}", f"Correia {k}"),
        (f"Polia tensora {k}", "Bloco direito"), (f"Polia GT2 20T {k}", f"NEMA 17 {k}"),
        (f"Esteira {k}", "Ponta fixa da esteira"), (f"Esteira {k}", "Prateleira da esteira"),
    ]}
PREVISTO.add(frozenset(("Rampa", "Sensor do bolso")))       # o sensor fica num bolsao da rampa
PREVISTO |= {frozenset(("EVA 5 mm", p)) for p in ("Bandeja esquerda", "Bandeja do meio", "Bandeja direita", "Rampa")}
# contatos de carros/esteiras que sao a funcao da peca
CONTATO_MOVEL = {
    ("presilha_A", "correia_tras_A"): "as costas da correia ficam apertadas contra a parede da presilha",
    ("presilha_B", "correia_tras_B"): "as costas da correia ficam apertadas contra a parede da presilha",
    ("presilha_A", "fdc_alav_A"): "fim de curso do eixo A: a presilha aperta a alavanca na casa",
    ("presilha_B", "fdc_alav_B"): "fim de curso do eixo B: a presilha aperta a alavanca na casa",
    ("presilha_piso_A", "fdc_alav_A"): "fim de curso do eixo A: a presilha aperta a alavanca na casa",
    ("presilha_piso_B", "fdc_alav_B"): "fim de curso do eixo B: a presilha aperta a alavanca na casa",
    ("presilha_piso_A", "correia_tras_A"): "a correia apoia no piso da presilha, entrando no fixador",
    ("presilha_piso_B", "correia_tras_B"): "a correia apoia no piso da presilha, entrando no fixador",
    ("fixador_A", "correia_tras_A"): "os dentes do fixador apertam a face dentada da correia",
    ("fixador_B", "correia_tras_B"): "os dentes do fixador apertam a face dentada da correia",
}
CONTATO_MOVEL.update({
    ("alav_chifre", "servo"): "chifre montado no eixo do servo",
    ("presilha_A", "fdc_dir_alav_A"): "fim de curso de seguranca: 0,8 mm da alavanca com o carro A na pega (so aperta se passar)",
    ("presilha_piso_A", "fdc_dir_alav_A"): "fim de curso de seguranca do eixo A",
    ("batedorB", "fdc_dir_alav_B"): "fim de curso de seguranca do eixo B: o batedor aperta a alavanca no limite",
})
CONTATO_MOVEL.update({
    ("alav_braco", "servo"): "o braco vai no chifre do servo e gira com ele, 0,5 mm acima do corpo (igual R1)",
    ("alav_braco", "suporte_servo"): "o braco vai no chifre do servo e gira com ele (igual R1)",
    ("alav_chifre", "suporte_servo"): "chifre do proprio servo",
})
for _s in ("baixo", "cima"):
    for _b in ("braco1", "braco2", "fundo"):
        CONTATO_MOVEL[(f"bandeira_{_s}", f"sensor_{_s}_{_b}")] = "a bandeira (M2) entra na fenda do sensor (1,5 mm de cada lado)"
for _k in ("A", "B"):
    for _p in ("patim_topo", "patim_fl1", "patim_fl2"):
        CONTATO_MOVEL[(f"{_p}_{_k}", f"trilho_{_k}")] = "o patim abraca o trilho"


def _fixos(c):
    return [n for n in c.id if c.corpo[n] == "mundo"]


# ------------------------------------------------------------------ 1
def interferencias(c: Cena):
    c.pose()
    fx = _fixos(c)
    ruins, prev, encostam = [], 0, 0
    for a, b in itertools.combinations(fx, 2):
        pa, pb = c.peca[a], c.peca[b]
        if pa == pb:
            continue
        d = c.dist(a, b, corte=1.0)
        if d >= -0.2:
            if d < 0.3:
                encostam += 1
            continue
        if frozenset((pa, pb)) in PREVISTO:
            prev += 1
            continue
        ruins.append(dict(a=c.pai[a], pa=pa, b=c.pai[b], pb=pb, entra=round(-d, 2)))
    return dict(ok=not ruins, ruins=ruins[:40], n_ruins=len(ruins), previstas=prev, encostam=encostam,
                pares=len(fx) * (len(fx) - 1) // 2)


# ------------------------------------------------------------------ 2
def varredura(c: Cena, passo=3.0):
    m, el = c.m, c.el
    fx = [n for n in _fixos(c) if c.peca[n] not in ("Gabinete", "Tela")] + [n for n in _fixos(c) if c.peca[n] in ("Gabinete", "Tela")]
    minimo = {}

    def guarda(a, b, est):
        d = c.dist(a, b, corte=8.0)
        k = (c.pai[a], c.pai[b])
        if k not in minimo or d < minimo[k][0]:
            minimo[k] = (d, est)

    A, B = c.nomes("carroA"), c.nomes("carroB")
    eA, eB = c.nomes("esteiraA"), c.nomes("esteiraB")
    t0 = time.time()
    xsA = np.arange(m.cA[0], m.cA[1] + 1e-6, passo).tolist() + [m.cA[1]]
    xsB = np.arange(m.cB[0], m.cB_seg + 1e-6, passo).tolist() + [m.cB_seg]     # ate o fim de curso da direita
    for i, ca in enumerate(xsA):
        cb = xsB[i % len(xsB)]
        c.pose(cA=ca, cB=cb)
        st = dict(cA=round(ca, 1), cB=round(cb, 1))
        for a in A + eA:
            for b in fx + B + eB:
                guarda(a, b, st)
        for a in eA:
            for b in A:
                if not a.startswith("est_movA") or True:
                    guarda(a, b, st)
    for i, cb in enumerate(xsB):
        ca = xsA[(i * 7) % len(xsA)]
        c.pose(cA=ca, cB=cb)
        st = dict(cA=round(ca, 1), cB=round(cb, 1))
        for a in B + eB:
            for b in fx + A + eA:
                guarda(a, b, st)
        for a in eB:
            for b in B:
                guarda(a, b, st)
    # cabine x tudo o que fica perto do elevador (torre, rampa, fila, sensores, polias, motor) em todo o curso
    c.pose()
    perto = []
    for n in fx:
        lo, hi = c.aabb(n)
        if hi[0] > 140 and hi[1] > 100 and c.peca[n] not in ("Tela",):
            perto.append(n)
    zcs = np.arange(el.zc_min, el.zc_max + 0.01, 2.0).tolist() + [el.zc_max]
    for zc in zcs:
        c.pose(zc=zc, cA=m.cA[1], cB=0)
        for a in c.nomes("carro"):
            for b in perto + A:
                guarda(a, b, dict(zc=round(zc, 1), cA=m.cA[1]))
    # comporta x tudo (todo o giro) e x cabine (cabine embaixo e subindo)
    for th in np.arange(0, el.ang_baixa + 0.01, 0.5):
        for zc in (el.zc_min, el.zc_min + 3, el.zc_min + 10):
            c.pose(th=th, zc=zc)
            for a in c.nomes("alavanca"):
                for b in fx + c.nomes("carro"):
                    if c.peca[b] in ("Servo",) and a == "alav_chifre":
                        continue
                    guarda(a, b, dict(th=th, zc=round(zc, 1)))
    linhas = []
    for (a, b), (d, st) in sorted(minimo.items(), key=lambda kv: kv[1][0]):
        prev = CONTATO_MOVEL.get((a, b)) or CONTATO_MOVEL.get((b, a))
        pa, pb = c.peca.get(a, c.peca.get(a + "#0", "?")), c.peca.get(b, c.peca.get(b + "#0", "?"))
        if prev is None and ((a.startswith("est_") and pb in ("Carro A", "Carro B", "Ponta fixa da esteira", "Prateleira da esteira")) or
                             (b.startswith("est_") and pa in ("Carro A", "Carro B", "Ponta fixa da esteira", "Prateleira da esteira"))):
            # esteira presa na ponta do carro / na ponta fixa: so o elo da ponta encosta
            if ("ponta" in a or "ponta" in b or "est_fixa" in a or "est_fixa" in b):
                prev = "elo da ponta da esteira preso no suporte"
        if prev is None and a.startswith("est_") and b.startswith("est_"):
            continue
        if prev is None and d > 0.5 and (a.startswith("est_") or b.startswith("est_")):
            prev = "esteira porta-cabo (flexivel, desenho aproximado)"
        if prev is None and (("est_" in a and "prat_estA" in b) or ("est_" in b and "prat_estA" in a)):
            prev = "a esteira A desliza deitada na prateleira" if d > -0.6 else None
        if prev is None and (("est_" in a and b == "piso") or ("est_" in b and a == "piso")):
            prev = "o ramo de baixo da esteira B fica no piso" if d > -0.6 else None
        ok = d >= FOLGA - 1e-6 or prev is not None
        if d < 3 or not ok:
            linhas.append(dict(a=a, pa=pa, b=b, pb=pb, folga=round(d, 2), onde=st, ok=bool(ok), nota=prev or ""))
    return dict(ok=all(l["ok"] for l in linhas), linhas=linhas, segundos=round(time.time() - t0, 1),
                posicoes=dict(A=len(xsA), B=len(xsB)))


# ------------------------------------------------------------------ 3. bola
def bola(c: Cena):
    m, el = c.m, c.el
    out = {}
    fx = _fixos(c)
    c.pose(cA=m.cA[0], cB=0)
    # a. bola parada no bolso: encosta no piso do bolso, na parede da direita e no batente da frente
    pb = m.bola_bolso
    ib = c.com_bola("bola", pb)
    toques = {n: round(c.dist("bola", n, 2), 2) for n in fx if c.dist("bola", n, 2) < 1.0}
    pen = {n: d for n, d in toques.items() if d < -0.05}
    out["bolso"] = dict(centro=pb.round(2).tolist(), toques=toques, ok=not pen and
                        {"rampa_bolso", "rampa_dir", "eva_bolso"} <= {n for n, d in toques.items() if abs(d) <= 0.05})
    # estabilidade: a bola desce para a direita e para a frente (encosta nos dois batentes)
    _, n, _ = m.plano_rampa()
    out["bolso"]["empurra_direita_N"] = round(0.067 * 9.81 * n[0] / n[2], 3)
    out["bolso"]["empurra_frente_N"] = round(0.067 * 9.81 * -n[1] / n[2] * -1, 3)
    # b. carro A chega na pega: ima a gap do topo da bola, resto do carro longe da bola e da rampa
    c.pose(cA=m.cA[1], cB=0)
    dists = {n: round(c.dist("bola", n, 5), 2) for n in c.nomes("carroA")}
    da = min(v for k, v in dists.items() if k.startswith("arruela"))
    resto = min(v for k, v in dists.items() if not k.startswith("arruela") and k != "ima")
    out["pega"] = dict(ima_ate_bola=da, gap_pedido=m.gap_pega, resto_min=resto,
                       ok=da >= FOLGA_IMA and resto >= FOLGA)    # o ima passa por cima sem encostar
    # c. bola presa (1 mm acima, 1 mm afastada dos batentes) indo da pega ate a casa
    pior = (99, None, None)
    for ca in np.arange(m.cA[1], m.cA[0] - 0.01, -1.0):
        c.pose(cA=ca, cB=0)
        c.com_bola("bola", (ca + m.dA, m.y_bola, m.zs))
        for nme in fx + c.nomes("esteiraA"):
            d = c.dist("bola", nme, 3)
            if d < pior[0]:
                pior = (d, nme, round(ca, 1))
    out["levando"] = dict(folga_min=round(pior[0], 2), com=pior[1], c=pior[2], ok=pior[0] >= FOLGA)
    # d. queda: o carro A anda em seno (+-120, 2,4 s; ate 314 mm/s no meio); a bola sai com a velocidade do carro.
    #    Todas as solturas de -120 a +120, para os dois lados: a parabola nao pode bater em nada parado antes da bandeja
    #    (o carro B fica de fora: acertar ou nao o anel e o jogo).
    w = 2 * math.pi / 2.4
    G = 9806.65
    ruins, pousos = [], []
    c.pose(cA=m.cA[0], cB=m.cB[0])
    fq = [nme for nme in fx if c.peca[nme] not in ("EVA 5 mm",)]
    for xr in np.arange(-m.curso, m.curso + 0.1, 5.0):
        for sgn in (1, -1):
            v = sgn * w * math.sqrt(max(0.0, m.curso ** 2 - xr ** 2))
            t = 0.0
            while True:
                x, z = xr + v * t, m.zs - G * t * t / 2
                if z <= m.s_bandeja(x, m.y_bola) + L.R:
                    pousos.append(x)
                    break
                c.com_bola("bola", (x, m.y_bola, z))
                bate = [nme for nme in fq if c.dist("bola", nme, 1) < 0]
                if bate:
                    ruins.append(dict(solta=round(xr, 1), v=round(v), x=round(x, 1), z=round(z, 1),
                                      bate=[c.pai[b] for b in bate][:3]))
                    break
                t += 0.004
    tv = math.sqrt(2 * (m.zs - m.s_bandeja(0, m.y_bola) - L.R) / G)
    out["queda"] = dict(pouso_x=[round(min(pousos), 1), round(max(pousos), 1)], voo_ms=round(tv * 1000),
                        v_max=round(w * m.curso), trajetorias=len(pousos) + len(ruins), ruins=ruins[:8], ok=not ruins)
    # e. anel: bola centrada e na borda da passagem limpa passa sem tocar; IR no caminho
    res = {}
    for dlt in (0.0, 3.0, m.folga_limpa - 0.05, m.folga_limpa + 1.0, 12.0, 20.0, 30.0):
        c.pose(cA=m.cA[0], cB=0.0)
        toca = None
        for z in np.arange(m.zb + L.R + 5, m.zb - m.h_anel - L.R - 1, -0.5):
            c.com_bola("bola", (dlt, m.y_bola, z))
            bate = [n for n in c.nomes("carroB") if c.dist("bola", n, 1) < 0]
            if bate:
                toca = (round(z, 1), c.pai[bate[0]])
                break
        res[str(dlt)] = "passa limpa" if toca is None else f"bate em {toca[1]} (Z {toca[0]})"
    out["anel"] = dict(casos=res, furo=round(2 * m.r_furo, 1), ir_z=round(m.zb - 14.5, 1),
                       ok=res["0.0"] == "passa limpa" and res[str(m.folga_limpa - 0.05)] == "passa limpa")
    # f. bandeja: abaixo do anel, juntas, labio, caminho ate a fila
    yr = (m.y_bola - m.r_flange, m.y_bola + m.r_flange)
    zr0 = m.zb - m.h_anel
    folga_anel = min(zr0 - (m.s_bandeja(x, y) + 2 * L.R)
                     for x in np.arange(m.cB[0] - m.r_flange, m.cB[1] + m.r_flange, 2.0) for y in yr)
    juntas = [round(abs(m.s_bandeja(x - 1e-6, y) - m.s_bandeja(x + 1e-6, y)), 3) for x in (-30, 120) for y in (50, 127)]
    labio = min(m.s_bandeja(x, m.y_bandeja[1]) - m.z_labio(x) for x in np.arange(m.x_juntas[0], m.x_entrada, 1.0))
    alta = min(L.Z_PAREDE_ALTA - (m.s_bandeja(x, m.y_bandeja[1]) + L.R) for x in np.arange(m.x_entrada, 175.5, 1.0))
    # rolar: desce pelo gradiente; parede da frente/lados param; atras: entra na fila (X < 40) ou corre ao longo dela
    falhas, entradas = [], []
    for x0 in np.arange(m.x_juntas[0] + 7, m.x_juntas[-1] - 2, 10.0):
        for y0 in np.arange(52, 126, 12.0):
            x, y = x0, y0
            for _ in range(4000):
                gx = (m.s_bandeja(x + 0.5, y) - m.s_bandeja(x - 0.5, y))
                gy = (m.s_bandeja(x, y + 0.5) - m.s_bandeja(x, y - 0.5))
                n = math.hypot(gx, gy)
                x, y = x - gx / n, y - gy / n
                x = min(max(x, m.x_juntas[0] + L.R * 0.3), m.x_juntas[-1] - L.R * 0.3)
                if y >= m.y_bandeja[1]:
                    if x < m.x_entrada:
                        entradas.append(x)
                        break
                    y = m.y_bandeja[1]
                    x -= 1.0
            else:
                falhas.append((x0, y0))
    out["bandeja"] = dict(folga_bola_anel=round(folga_anel, 2), juntas_mm=max(juntas), labio_min=round(labio, 2),
                          parede_alta_sobra=round(alta, 2), x_entrada_max=round(max(entradas), 1),
                          pontos=len(entradas) + len(falhas), falhas=falhas[:5],
                          ok=folga_anel >= 2 and max(juntas) < 0.05 and labio >= 1 and alta >= 2 and not falhas)
    # g. fila: piso sempre descendo para a direita; capacidade
    fs = [m.f_fila(x) for x in np.arange(m.x_juntas[0], 174, 1.0)]
    cap = int((el.x_contato - m.x_juntas[0]) / (2 * L.R + 0.5))
    out["fila"] = dict(sempre_desce=all(a > b for a, b in zip(fs, fs[1:])), capacidade_bolas=cap,
                       bolas_na_maquina=8, ok=all(a > b for a, b in zip(fs, fs[1:])) and cap >= 7)
    c.g.pop()
    return out


# ------------------------------------------------------------------ 4. parafusos
def _intervalo(c, i, p0, d, Lm, r):
    """Trecho [t0, t1] do segmento dentro da geometria i (caixa orientada; cilindro e esfera como caixa)."""
    cc, R, h, t = c._c[i], c._R[i], c.meio[i], c.tipo[i]
    if t == "sphere":
        h = np.full(3, h[0])
        R = np.eye(3)
    elif t == "cylinder":
        h = np.array([h[0], h[0], h[1]])
    q0, qd = R.T @ (p0 - cc), R.T @ d
    t0, t1 = 0.0, Lm
    for k in range(3):
        if abs(qd[k]) > 1e-6:
            a, b = sorted(((-h[k] - q0[k]) / qd[k], (h[k] - q0[k]) / qd[k]))
            if abs(qd[k]) < 0.5:
                infl = r * math.sqrt(max(0, 1 - qd[k] ** 2)) / abs(qd[k])
                a, b = a - infl, b + infl
            t0, t1 = max(t0, a), min(t1, b)
        else:
            if abs(q0[k]) >= h[k] + r - 1e-6:
                return None
    return (t0, t1) if t1 - t0 > 1e-6 else None


def _borda(c, i, p0, d):
    cc, R, h = c._c[i], c._R[i], c.meio[i]
    if c.tipo[i] != "box":
        return 99
    q0, qd = R.T @ (p0 - cc), R.T @ d
    return min(h[k] - abs(q0[k]) for k in range(3) if abs(qd[k]) < 0.5)


METAL = ("NEMA", "Patim", "Eletroima", "Perfil", "Motor N20", "Polia")


def parafusos(c: Cena):
    m = c.m
    etapa = {n: L.PECAS.get(c.peca[n], ("", "", 99))[2] for n in c.id}
    res = []
    for f in L.fixadores(m):
        cA = 0.0 if f["corpo"] != "carroA" else 0.0
        c.pose(zc=150.0, cA=0.0, cB=0.0)
        p0, d, Lm = np.array(f["p0"], float), np.array(f["dir"], float), f["L"]
        if f["corpo"] == "carro":
            p0[2] += 150.0
        problemas, notas = [], []
        dentro = {}
        for n, i in c.id.items():
            if c.corpo[n] == "bola":
                continue
            iv = _intervalo(c, i, p0, d, Lm, 1.4)
            if iv:
                dentro.setdefault(c.peca[n], []).append((n, iv))
        prende = sum(b - a for _, (a, b) in dentro.get(f["prende"], []))
        rosca = sum(b - a for _, (a, b) in dentro.get(f["rosca"], []))
        if f["prende"] == f["rosca"]:
            rosca = prende
        if prende < 1.0:
            problemas.append(f"nao atravessa {f['prende']} ({prende:.1f} mm)")
        tipo = f["tipo"]
        impressa = L.PECAS.get(f["rosca"], ("?",))[0] == "impressa"
        porca = "porca" in tipo or "martelo" in tipo or f["prende"] == f["rosca"]
        auto = f["insert"] if f["insert"] is not None else (impressa and not porca)   # rosca direto no PETG
        if f["rosca"] == "Gabinete":
            minimo = 8.0
        elif auto:
            minimo = 4.0 if tipo.startswith("M2") else 5.0
        elif porca:
            minimo = 1.0
        else:
            minimo = 1.0 if "Polia" in f["rosca"] else 2.5
        if rosca < minimo:
            problemas.append(f"pega so {rosca:.1f} mm em {f['rosca']} (minimo {minimo})")
        livres = {f["prende"], f["rosca"], *f["atravessa"], *f["acesso"]}
        for pc in dentro:
            if pc not in livres and pc != "Gabinete":
                problemas.append(f"fura {pc}")
        # parede em volta da rosca (rosca direto no PETG)
        if auto and dentro.get(f["rosca"]):
            ids = [c.id[n] for n in c.id if c.peca[n] == f["rosca"]]
            rr = (1.0 if tipo.startswith("M2") else 1.5) + 1.5
            u = np.cross(d, [0, 0, 1.0]) if abs(d[2]) < 0.9 else np.cross(d, [1.0, 0, 0])
            u /= np.linalg.norm(u)
            v = np.cross(d, u)
            ivs = [iv for _, iv in dentro[f["rosca"]]]
            t_a, t_b = min(a for a, _ in ivs), max(b for _, b in ivs)
            P = []
            for t in np.linspace(t_a + 0.6, t_b - 0.6, 4):
                for a in np.linspace(0, 2 * math.pi, 16, endpoint=False):
                    P.append(p0 + d * t + rr * (math.cos(a) * u + math.sin(a) * v))
            P = np.array(P)
            dentro_pts = np.zeros(len(P), bool)
            for i in ids:
                dentro_pts |= c.contem(i, P)
            frac = dentro_pts.mean()
            notas.append(f"parede de 1,5 mm em volta da rosca: {100 * frac:.0f}% cheia")
            if frac < 0.97:
                problemas.append(f"parede fina em volta da rosca em {f['rosca']} ({100 * frac:.0f}% do anel de 1,5 mm cheio)")
        # chave
        if not f.get("bancada"):
            rc = f["cab"] / 2 + 0.5
            for n, i in c.id.items():
                pc = c.peca[n]
                if pc in livres or pc in ("Gabinete", "Tela") or etapa[n] > f["etapa"] or c.corpo[n] in ("bola",):
                    continue
                if c.corpo[n] in ("carroA", "carroB", "esteiraA", "esteiraB") and pc not in livres:
                    if etapa[n] > f["etapa"]:
                        continue
                iv = _intervalo(c, i, p0, -d, f.get("corredor", 120.0), rc)
                if iv and iv[0] < f.get("corredor", 120.0) - 1:
                    problemas.append(f"chave bate em {pc} ({c.pai[n]}) a {iv[0]:.0f} mm da cabeca")
                    break
        res.append(dict(nome=f["nome"], tipo=tipo, etapa=f["etapa"], prende=f["prende"], rosca=f["rosca"],
                        pega=round(rosca, 1), ok=not problemas, problemas=problemas, notas=notas[:2],
                        p0=f["p0"], dir=f["dir"], L=Lm, corpo=f["corpo"]))
    return res


# ------------------------------------------------------------------ 5
def envelope(c: Cena):
    m = c.m
    lo_t, hi_t = np.full(3, 1e9), np.full(3, -1e9)
    fora = []
    for ca, cb, zc in ((m.cA[0], m.cB[0], c.el.zc_min), (m.cA[1], m.cB[1], c.el.zc_max)):
        c.pose(zc=zc, cA=ca, cB=cb)
        for n, i in c.id.items():
            if c.peca[n] in ("Gabinete", "Tela") or c.corpo[n] == "bola":
                continue
            lo, hi = c.aabb_i(i)
            lo_t, hi_t = np.minimum(lo_t, lo), np.maximum(hi_t, hi)
            if lo[0] < -GX - 0.01 or hi[0] > GX + 0.01 or lo[1] < -0.01 or hi[1] > GY + 0.01 or lo[2] < -0.01 or hi[2] > GZ + 0.01:
                fora.append(c.pai[n])
    return dict(min=lo_t.round(1).tolist(), max=hi_t.round(1).tolist(), fora=sorted(set(fora)), ok=not fora)


def janela(c: Cena):
    """Faixa da tela que so a bola atravessa: entre o topo do anel e a bola presa, sem nada parado na frente."""
    m = c.m
    c.pose()
    z0, z1 = m.zb, m.zs - L.R
    x0, x1 = -GX, 160.0
    bloqueia = []
    for n, i in c.id.items():
        if c.corpo[n] != "mundo" or c.peca[n] in ("Gabinete", "Tela"):
            continue
        lo, hi = c.aabb_i(i)
        if hi[2] > z0 + 0.5 and lo[2] < z1 - 0.5 and hi[0] > x0 and lo[0] < x1:
            bloqueia.append((c.pai[n], c.peca[n], lo.round(1).tolist(), hi.round(1).tolist()))
    xl = max([b[3][0] for b in bloqueia if b[3][0] < 0] + [x0])
    xr = min([b[2][0] for b in bloqueia if b[2][0] > 0] + [x1])
    return dict(z=[round(z0, 1), round(z1, 1)], x=[round(xl, 1), round(xr, 1)],
                tamanho=[round(xr - xl), round(z1 - z0)], bloqueia=sorted({b[1] for b in bloqueia}))


def main():
    t0 = time.time()
    m = L.M()
    c = Cena(m)
    val = {}
    val["interferencias"] = interferencias(c)
    print("INTERF", val["interferencias"]["n_ruins"], "ruins", val["interferencias"]["ruins"][:12],
          "previstas", val["interferencias"]["previstas"], f"{time.time() - t0:.0f}s", flush=True)
    val["parafusos"] = parafusos(c)
    ruins = [p for p in val["parafusos"] if not p["ok"]]
    print("PARAFUSOS", len(ruins), "ruins de", len(val["parafusos"]), f"{time.time() - t0:.0f}s")
    for p in ruins:
        print("   ", p["nome"], p["problemas"])
    val["bola"] = bola(c)
    for k, v in val["bola"].items():
        print("BOLA", k, v)
    val["envelope"] = envelope(c)
    val["janela"] = janela(c)
    print("ENVELOPE", val["envelope"], "\nJANELA", val["janela"], flush=True)
    if "--rapido" not in sys.argv:
        val["varredura"] = varredura(c)
        v = val["varredura"]
        print("VARREDURA ok" if v["ok"] else "VARREDURA RUIM", v["segundos"], "s", v["posicoes"])
        for l in v["linhas"][:40]:
            print("   ", l)
    (AQUI / "validacao.json").write_text(json.dumps(val, indent=1, ensure_ascii=False, default=float), encoding="utf8")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
