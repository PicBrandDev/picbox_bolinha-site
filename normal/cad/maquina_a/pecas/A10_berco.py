"""A10 — Berco da soltura (alcapao duplo), carro A.

Intencao:
- Funcao: estrutura que pendura sob a placa do carro A: articula as duas portinholas A11, segura o solenoide,
  tem a entrada da bola pelo lado -X (calha de carga) e o batente do lado +X que centra a bola em x=0.
- Cargas: bola de 60 g, golpe do solenoide; em balanco de ~60 mm a frente da placa (bochechas, teto e tampo).
- Interfaces: placa do carro A05 (3x M3x12 nas porcas embutidas), portinholas (2x M3x55 como eixo),
  solenoide JF-0826B (2x M3 em rasgos verticais de ajuste, ESTIMADO), calha de carga do magazine (entrada).
- Visivel ao jogador: frente aberta (a bola aparece), arestas R3.
Impressao: apoiada na frente (y=-96): bochechas, teto e tampo sobem na vertical; furo da entrada em gota.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro, teardrop, bolsao_porca
from maquina_a import layout as L
from maquina_a import soltura as S
from maquina_a.pecas import A05_placa_carro as P

ID = "A10"
NOME = "berco"
TITULO = "Berco da soltura (alcapao duplo)"
QTD = {"A": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = {"A": "soltura_berco"}
ESTRUTURAL = True
MOVEL = True
COORD_MAQUINA = True
EIXO = "A"
VISTA = (-1.2, -1.5, 0.7)
JUSTIFICATIVA = "conceito novo (usuario): alcapao duplo simetrico no lugar da pinca lateral"

Y0, Y1 = -96.0, -16.0                  # ESTIMADO extensao das bochechas (eixos a +-25,5, rasgo do pino)
Y1_SOL = S.Y_PINO + 22.0 / 2 + 1.0     # ESTIMADO bochecha +X estendida para o solenoide
Z_BAIXO = S.Z_EIXO - 6.0               # material em volta dos eixos
Z_TETO = (S.Z_C + S.R_B + 3.0, S.Z_C + S.R_B + 3.0 + fab.E_GROSSA)   # 3 mm acima da bola
E_MONT = 5.2                           # ESTIMADO placa de montagem
MONT = (-32.0, S.X_BOCH_D[1], -33.0, -6.0)   # ESTIMADO x0, x1, y0, y1
FUROS_MONT = [(-27.0, -24.0), (-27.0, -8.0), (27.0, -8.0)]   # subconjunto de A05.CARGA_FUROS (o 4o cai na bochecha)
R_ENTRADA = 23.0                       # ESTIMADO furo de entrada: bola + folga e os trilhos-lingua da calha de carga A16 (raio 19..22,5)
BATENTE = (S.R_B * math.cos(math.asin(8.0 / S.R_B)) + 0.25, 8.0)   # face em x (contato na aresta de baixo), z acima do centro
CIMA_IMPRESSAO = (0.0, 1.0, 0.0)       # impresso apoiado na frente (y=-96): +y sobe


def local(var="A"):
    zf = S.Z_FACE_CARRO
    xe0, xe1 = S.X_BOCH_E
    xd0, xd1 = S.X_BOCH_D
    boch_e = caixa(xe0, xe1, Y0, Y1, Z_BAIXO, zf)
    boch_d = caixa(xd0, xd1, Y0, Y1, Z_BAIXO, zf).union(caixa(xd0, xd1, Y0, Y1_SOL, S.Z_SOL_BASE, zf))
    for b in (boch_e, boch_d):
        pass
    teto = caixa(xe0, xd1, Y0, Y1, Z_TETO[0], Z_TETO[1])
    # tampo: a placa de montagem corre ate a frente (impressa apoiada na frente: tudo sobe na vertical, sem ponte)
    mont = caixa(MONT[0], MONT[1], Y0, MONT[3], zf - E_MONT, zf)
    frente = caixa(xe0, xd1, Y0, Y0 + 6.0, Z_TETO[0], zf)
    # batente: pendurado no teto, face de baixo inclinada a 45 graus para a frente (imprime sem suporte, livre das engrenagens)
    zb0, zb1 = S.Z_C + BATENTE[1], Z_TETO[0] + 0.5
    yb1 = S.Y_C + 5.0
    bat = (cq.Workplane("YZ", origin=(BATENTE[0], 0, 0))
           .polyline([(yb1, zb0), (yb1, zb1), (yb1 - 6.0 - (zb1 - zb0), zb1), (yb1 - 6.0, zb0)]).close()
           .extrude(xd0 + 0.5 - BATENTE[0]))
    corpo = boch_e.union(boch_d).union(teto).union(mont).union(frente).union(bat)
    # arestas ao longo de y (verticais na impressao): base das bochechas e laterais do tampo, R3 (peca visivel)
    for caixa_sel in (((-60, Y0 - 1, Z_BAIXO - 1), (60, Y1_SOL + 1, Z_BAIXO + 1)),
                      ((-60, Y0 - 1, zf - 1), (60, MONT[3] + 1, zf + 1)),
                      ((-60, Y0 - 1, S.Z_SOL_BASE - 1), (60, Y1_SOL + 1, S.Z_SOL_BASE + 1))):
        try:
            corpo = corpo.edges("|Y").edges(cq.selectors.BoxSelector(*caixa_sel)).fillet(fab.R_VISIVEL)
        except Exception:
            pass
    try:
        corpo = corpo.faces("<Y").edges().chamfer(fab.CHANFRO_BASE)     # face da frente vai na mesa
    except Exception:
        pass
    # entrada da bola (-X): furo redondo no eixo da bola
    corpo = corpo.cut(teardrop(2 * R_ENTRADA, xe1 - xe0 + 2, (xe0 - 1, S.Y_C, S.Z_C), (1, 0, 0), CIMA_IMPRESSAO))
    # eixos das portinholas
    for lado in ("t", "f"):
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"], xd1 - xe0 + 2, (xe0 - 1, S.Y_EIXO[lado], S.Z_EIXO), (1, 0, 0)))
        corpo = corpo.cut(bolsao_porca("M3", (xd1, S.Y_EIXO[lado], S.Z_EIXO), (-1, 0, 0), angulo=30.0, extra_saida=0.5))
    # rasgo em arco para o pino da alavanca (abre 0..60 graus, com folga)
    for k in range(-3, 24):
        y, z = S.pino_alavanca(k * 3.0)
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"] + 1.0, xd1 - xd0 + 2, (xd0 - 1, y, z), (1, 0, 0)))
    # solenoide: 2x M3 em rasgos verticais (ajuste +-1,5 da posicao fechada)
    for dz in (8.5, 18.5):
        zc = S.Z_SOL_BASE + dz
        corpo = corpo.cut(cq.Workplane("YZ", origin=(xd0 - 1, 0, 0)).center(S.Y_PINO, zc)
                          .slot2D(3.0 + fab.FURO_PASSANTE["M3"], fab.FURO_PASSANTE["M3"], 90).extrude(xd1 - xd0 + 2))
    # montagem na placa do carro
    for x, y in FUROS_MONT:
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"], E_MONT + 2, (x, y, zf - E_MONT - 1), (0, 0, 1)))
    return corpo


def build(p=None, var="A"):
    return local(var)


def impressao(var="A"):
    sh = local(var).val().rotate((0, 0, 0), (1, 0, 0), 90)      # frente (y=-96) para baixo
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="A"):
    zf = S.Z_FACE_CARRO
    f = [dict(nome="carro", tipo="DIN912", bitola="M3", comp=12, ponto=(x, y, zf - E_MONT), dir=(0, 0, 1), chave=20,
              extra="nas porcas embutidas da placa A05") for x, y in FUROS_MONT]
    for lado in ("t", "f"):
        f.append(dict(nome="eixo portinhola", tipo="DIN912", bitola="M3", comp=55, ponto=(S.X_BOCH_E[0], S.Y_EIXO[lado], S.Z_EIXO),
                      dir=(1, 0, 0), chave=30, extra="porca M3 no bolsao da bochecha +X"))
    for dz in (8.5, 18.5):
        f.append(dict(nome="solenoide", tipo="DIN912", bitola="M3", comp=6, ponto=(S.X_BOCH_D[0], S.Y_PINO, S.Z_SOL_BASE + dz),
                      dir=(1, 0, 0), chave=8, antes_de=("A11",), extra="na rosca do corpo do solenoide (ESTIMADO)"))
    return f


def pares_furos(var="A"):
    from common.checks import _dist_retas
    zf = S.Z_FACE_CARRO
    return [(f"carro {k + 1}", ((x, y, zf - E_MONT), (0, 0, 1)), ((x, y, zf), (0, 0, 1))) for k, (x, y) in enumerate(FUROS_MONT)]


def checa_bola(var="A"):
    """Entrada rolando (-X ate o centro), bola parada, e queda com as portinholas abertas."""
    from common.checks import c7_interferencia
    from common import hardware as hw
    from maquina_a.pecas import A11_portinhola as A11
    frame = build(None, var)
    bola = lambda x, r=S.R_B: hw.bola((x, S.Y_C, S.Z_C + 0.05), 2 * r)
    rolando = cq.Workplane("XY").add([bola(x).val() for x in range(-60, 1, 4)])
    # a bola rola apoiada nas portinholas; folga so contra o berco (sem o batente, que e contato)
    r1 = c7_interferencia(frame, {"bola_rolando": cq.Workplane("XY").add([bola(x, S.R_B + 1.0).val() for x in range(-60, -4, 4)])})
    abertas = {l: A11.local(l, S.ABERTURA) for l in ("t", "f")}
    rb = S.R_B + fab.FOLGA_BOLA_RADIAL
    queda = cilindro(2 * rb, 130, (0, S.Y_C, S.Z_C - 130), (0, 0, 1))   # do centro da bola parada para baixo
    r2 = c7_interferencia(queda, {"berco": frame, **{f"A11.{k}": v for k, v in abertas.items()}})
    parada = c7_interferencia(bola(0), {"berco": frame})
    return dict(ok=r1["ok"] and r2["ok"], entrada=r1, queda_aberta=r2, parada_contato_batente=parada["colisoes"],
                curso_pino_mm=round(S.CURSO_PINO, 2))


FICHA = dict(orientacao="apoiada na face da frente", suporte="nao", perimetros=4, infill="40% gyroid (estrutural)", camada=0.20,
             montagem=("1) porcas M3 nos bolsoes dos eixos; 2) portinholas engrenadas fechadas, M3x55 pelos eixos; "
                       "3) pino M3x25 na alavanca; 4) solenoide com o garfo A36, 2x M3x6 nos rasgos (ajustar fechado); "
                       "5) berco na placa do carro A, 3x M3x12."))
