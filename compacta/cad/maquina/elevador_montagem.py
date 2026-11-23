"""Montagem do elevador passo a passo em 3D (pagina HTML de arquivo unico).

  python elevador_montagem.py  ->  compacta/pagina/PICBOX_elevador_montagem.html
Cada peca tem o passo em que entra, de onde ela vem (vetor em mm) e onde fica em cada passo (a torre de cima e montada
na bancada, levantada, e desce no passo do encaixe; a cabine recebe as bandeiras em cima e desce nos trilhos).
"""
import base64
import json
from pathlib import Path

import numpy as np
import pyvista as pv

import layout as L
import render_m as R

AQUI = Path(__file__).resolve().parent
TPL = AQUI / "elevador_montagem_tpl.html"
SAIDA = AQUI.parents[1] / "pagina" / "PICBOX_elevador_montagem.html"
CENTRO = np.array([190.0, 150.0, 215.0])
PRIM = ("Adaptador N20-M5", "Espacador da parede", "Arruela impressa")
UP = 230.0      # torre de cima levantada enquanto e montada na bancada
CAB = 240.0     # cabine levantada enquanto recebe as bandeiras

# passos: (titulo, linhas)
PASSOS = [
    ("Torre de baixo", ["Comece pela torre de baixo (impressa), em pé na bancada.",
                        "Os passos 1 a 5 são todos nela."]),
    ("Polia de baixo", ["Eixo M5x30 de trás para a frente pela placa de trás (rasgo de 6 mm).",
                        "Porca na frente da placa, arruela, polia, arruela e porca de nylon.",
                        "Deixe frouxo, no ALTO do rasgo: a correia estica no passo 14."]),
    ("Sensor de baixo", ["Sensor de fenda com a fenda para cima, orelhas no pé.",
                         "2 M3x10 pelos furos das orelhas, porcas por baixo do pé.",
                         "Pernas pelo furo do pé; fios pelo canal até a canaleta de trás."]),
    ("Bandeiras na cabine", ["Rosqueie as 2 bandeiras (M2x25) nos ressaltos atrás da cabine, cada uma com 1 porca de trava.",
                             "A de baixo com a ponta para baixo, a de cima com a ponta para cima.",
                             "Girar a bandeira ajusta a altura em que a cabine para."]),
    ("Cabine nos trilhos", ["Desça a cabine por cima da torre de baixo, um C em cada trilho.",
                            "Ela tem que descer sozinha, sem prender (1 mm de folga por lado)."]),
    ("Torre de cima: cortar a tira", ["Agora a torre de cima, na bancada (aqui ela aparece levantada).",
                                      "Corte a tira VERMELHA do teto: entre o encaixe da frente e a janela, 4,5 mm, na largura da janela.",
                                      "O cubo de 16 mm da polia bate ali."]),
    ("Motor N20 + adaptador", ["Na mão: adaptador no eixo do N20 até o fundo (o furo é em D).",
                               "Aperte o M3 sem cabeça no chato do eixo.",
                               "Deslize o motor no berço pela frente, com o adaptador para trás."]),
    ("Rolamento", ["Rolamento 625ZZ por trás, na sede, até encostar no degrau.",
                   "Uma gota de cola só na pista de FORA."]),
    ("Polia e espaçador", ["Pela janela do teto: a polia, com o cubo virado para o motor, encostada no flange do adaptador.",
                           "O espaçador de 6,8 entre a polia e o rolamento (atravessa o furo de 7 da parede)."]),
    ("Parafuso M5 por trás", ["M5x45 com a arruela impressa, por trás: atravessa rolamento, espaçador e polia.",
                              "Rosqueie no adaptador e aperte firme: vira um bloco só.",
                              "Dentes da polia no meio da correia; aperte o parafusinho da polia no M5.",
                              "Gire com a mão: tem que girar liso, sem raspar no teto."]),
    ("Sensor de cima", ["Sensor de fenda no teto, fenda para baixo.",
                        "2 M3x10 com porca por cima do teto. Fios pela janela de trás."]),
    ("Encaixar as torres", ["Desça a torre de cima nos 3 pinos da de baixo.",
                            "Aperte 2 M3x8 atrás e 2 na esquerda."]),
    ("Correia na cabine", ["A correia é um laço: o ramo da ESQUERDA passa livre; o da DIREITA prende na cabine.",
                           "Uma ponta desce da polia do motor, a outra sobe da polia de baixo; as duas se encontram no meio do bolso de trás da cabine.",
                           "Fixador de alumínio por cima, dentes nos dentes da correia; porca M3 na fenda atrás; M3x14 pela janela da parede direita."]),
    ("Esticar a correia", ["Puxe a polia de baixo para baixo no rasgo até a correia ficar esticada.",
                           "Aperte a porca do eixo."]),
    ("Pronto: teste", ["Gire o motor: a cabine sobe e desce lisa, e as bandeiras passam no meio das fendas dos sensores.",
                       "Depois: torre no gabinete (2 parafusos no piso, 2 em cada orelha), comporta e rampa."]),
]


def S(n):           # numero do passo pelo titulo (1..)
    return next(i + 1 for i, (t, _) in enumerate(PASSOS) if t.startswith(n))


def zc(b):
    return (b[4] + b[5]) / 2


# (chave, rotulo, teste(peca, bounds), quadros [(passo, dx, dy, dz)], vem, dy do rotulo, vidro)
TOPO = lambda p: [(p, 0, 0, UP), (S("Encaixar"), 0, 0, 0)]          # noqa: E731
PARTES = [
    ("torre_b", "Torre de baixo", lambda pc, b: pc == "Torre inferior", [(1, 0, 0, 0)], (0, 0, 0), 0, True),
    ("polia_b", "Polia de baixo (eixo M5x30)", lambda pc, b: pc == "Polia de baixo",
     [(S("Polia de baixo"), 0, 0, 4), (S("Esticar"), 0, 0, 0)], (0, -45, 0), 0, False),
    ("sensor_b", "Sensor de baixo", lambda pc, b: pc == "Sensor de fenda" and zc(b) < 200,
     [(S("Sensor de baixo"), 0, 0, 0)], (35, 0, 0), 0, False),
    ("cabine", "Cabine", lambda pc, b: pc == "Cabine",
     [(S("Bandeiras"), 0, 0, CAB), (S("Cabine nos"), 0, 0, 0)], (0, 0, 60), 0, False),
    ("band_b", "Bandeira de baixo", lambda pc, b: pc == "Bandeira" and zc(b) < 45,
     [(S("Bandeiras"), 0, 0, CAB), (S("Cabine nos"), 0, 0, 0)], (0, 0, -30), 14, False),
    ("band_c", "Bandeira de cima", lambda pc, b: pc == "Bandeira" and zc(b) >= 45,
     [(S("Bandeiras"), 0, 0, CAB), (S("Cabine nos"), 0, 0, 0)], (0, 0, 30), -14, False),
    ("torre_c", "Torre de cima", lambda pc, b: pc == "Torre superior", TOPO(S("Torre de cima")), (0, 0, 80), 0, True),
    ("tira", "CORTAR esta tira", lambda pc, b: pc == "TIRA", TOPO(S("Torre de cima")), (0, 0, 0), -18, False),
    ("motor", "Motor N20", lambda pc, b: pc == "Motor N20", TOPO(S("Motor")), (0, -60, 0), 24, False),
    ("adapt", "Adaptador (impresso)", lambda pc, b: pc == "Adaptador N20-M5", TOPO(S("Motor")), (0, -60, 0), 0, False),
    ("m3", "M3 sem cabeça", lambda pc, b: pc == "Parafuso sem cabeca M3", TOPO(S("Motor")), (0, -60, 0), -26, False),
    ("rol", "Rolamento 625ZZ", lambda pc, b: pc == "Rolamento 625ZZ", TOPO(S("Rolamento")), (0, 35, 0), 0, False),
    ("polia_c", "Polia de 16 mm", lambda pc, b: pc == "Polia do motor", TOPO(S("Polia e")), (0, 0, 45), -16, False),
    ("esp", "Espaçador 6,8 (impresso)", lambda pc, b: pc == "Espacador da parede", TOPO(S("Polia e")), (0, 0, 45), 16, False),
    ("arr", "Arruela (impressa)", lambda pc, b: pc == "Arruela impressa", TOPO(S("Parafuso M5")), (0, 70, 0), 16, False),
    ("m5", "M5 x 45", lambda pc, b: pc == "Parafuso M5 da polia", TOPO(S("Parafuso M5")), (0, 70, 0), -16, False),
    ("sensor_c", "Sensor de cima", lambda pc, b: pc == "Sensor de fenda" and zc(b) >= 200,
     TOPO(S("Sensor de cima")), (0, 0, -30), 0, False),
    ("correia", "Correia (laço)", lambda pc, b: pc == "Correia", [(S("Correia"), 0, 0, 0)], (0, 0, 0), 0, False),
    ("fixador", "Fixador de alumínio", lambda pc, b: pc == "Fixador da cabine", [(S("Correia"), 0, 0, 0)], (0, 0, 40), 0, False),
]
TRAS = (0.55, 1.0, 0.22)
DIR = {S("Motor"): (0.75, -1.0, 0.55), S("Rolamento"): (0.6, 1.0, 0.45), S("Polia e"): (0.55, 0.7, 1.0),
       S("Parafuso M5"): (0.6, 1.0, 0.45), S("Sensor de cima"): (1.0, 0.5, -0.3), S("Sensor de baixo"): (1.0, 0.5, 0.5)}
ATE = {"tira": S("Torre de cima")}      # some depois deste passo (foi cortada)
# o que a camera enquadra / os nomes que aparecem em cada passo (padrao: as pecas que entram nele)
FOCO = {S("Encaixar"): ["torre_b", "torre_c"], S("Correia"): ["torre_b", "torre_c"], S("Pronto"): ["torre_b", "torre_c"],
        S("Torre de cima"): ["tira", "motor", "m5"], S("Esticar"): ["polia_b", "sensor_b"]}
NOMES = {S("Encaixar"): ["torre_c"], S("Esticar"): ["polia_b"], S("Pronto"): ["cabine", "motor", "sensor_b", "sensor_c"],
         S("Torre de cima"): ["torre_c", "tira"]}


def b64(a, tp):
    return base64.b64encode(np.ascontiguousarray(a, tp).tobytes()).decode()


def tri(me):
    t = me.triangulate()
    return np.asarray(t.points, float), t.faces.reshape(-1, 4)[:, 1:]


def off(q, p):
    o = q[0][1:]
    for k in q:
        if k[0] <= p:
            o = k[1:]
    return np.array(o, float)


def main():
    R.IMPRESSAS = R.malhas_impressas()
    m = L.M()
    el = m.el
    z0, z1 = el.zc_min, el.zc_max
    tira = pv.Box(bounds=(181.0, 201.0, 182.0, 186.5, 425.0, 429.4))
    A = R.cena(m, z0, el.ang_baixa, -40.0, 0.0, prim=PRIM) + [(tira, "#e0352b", 1.0, "TIRA")]
    B = R.cena(m, z1, el.ang_baixa, -40.0, 0.0, prim=PRIM) + [(tira, "#e0352b", 1.0, "TIRA")]
    assert len(A) == len(B)
    acc = {}
    for (ma, cor, _op, pc), (mb, *_r) in zip(A, B):
        b = ma.bounds
        parte = next((p for p in PARTES if p[2](pc, b)), None)
        if parte is None:
            continue
        pa, f = tri(ma)
        pb, _ = tri(mb)
        dv = (pb - pa) / (z1 - z0) if pa.shape == pb.shape else np.zeros_like(pa)
        g = acc.setdefault(parte[0], dict(cor=pv.Color(cor).hex_rgb, v=[], dv=[], t=[], n=0))
        g["v"].append(pa - CENTRO); g["dv"].append(dv); g["t"].append(f + g["n"]); g["n"] += len(pa)
    pecas, caixas = [], {}
    for chave, rot, _t, q, vem, dy, vidro in PARTES:
        g = acc[chave]
        v, dv = np.vstack(g["v"]), np.vstack(g["dv"])
        caixas[chave] = (v.min(0), v.max(0), q)
        d = dict(k=chave, nome=rot, cor=g["cor"], vidro=vidro, q=[list(map(float, x)) for x in q], vem=list(vem), dy=dy,
                 c=[round(x, 2) for x in (v.min(0) + v.max(0)) / 2], v=b64(v, np.float32), t=b64(np.vstack(g["t"]), np.uint32))
        if chave in ATE:
            d["ate"] = ATE[chave]
        if np.abs(dv).max() > 1e-6:
            d["dv"] = b64(dv, np.float32)
            d["dc"] = [round(x, 4) for x in dv.mean(0)]
        pecas.append(d)
    passos = []
    for i, (titulo, linhas) in enumerate(PASSOS):
        p = i + 1
        novas = [x[0] for x in PARTES if x[3][0][0] == p]
        foco = FOCO.get(p) or novas or [x[0] for x in PARTES if x[3][0][0] <= p]
        lo = np.min([caixas[k][0] + off(caixas[k][2], p) for k in foco], 0)
        hi = np.max([caixas[k][1] + off(caixas[k][2], p) for k in foco], 0)
        h = float(np.clip(np.linalg.norm(hi - lo) * 0.75 + 20, 55, 300))
        passos.append(dict(t=titulo, l=linhas, novas=novas, nomes=NOMES.get(p, novas),
                           alvo=[round(x, 1) for x in (lo + hi) / 2], h=round(h, 1), dir=DIR.get(p, TRAS)))
    dados = dict(pecas=pecas, passos=passos, z0=round(z0, 3), z1=round(z1, 3), cam=TRAS)
    html = TPL.read_text(encoding="utf8").replace("/*DADOS*/null", json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
    SAIDA.write_text(html, encoding="utf8")
    print("ok", SAIDA, round(len(html) / 1e6, 2), "MB", [(x["t"], x["h"]) for x in passos])


if __name__ == "__main__":
    main()
