"""A05 — Placa do carro com garra da correia integrada (eixos A e B).

Intencao:
- Funcao: liga o patim MGN12H a carga (boca A09 no B, berco A10 no A); prende as duas pontas da GT2 6 mm
  (garra integrada, presilhas A07 por baixo); as pontas da placa acionam a alavanca do fim de curso de home (sem batente).
- Movimento: anda com o carro, +-140 em jogo, ate +-144,2 (clique do FC).
- FC: ponta da placa em x=+-32 encosta na alavanca em x carro = 141 (clique em 143).
- Interfaces: patim (4x M3x6, 20x20), carga (4x M3 com porca embutida por baixo, fora do patim), presilhas A07
  (2x M3x12 cada, porca embutida por cima), correia no plano y=23,5. Antes separada (A06 garra), agora uma peca so.
Impressao: deitada na face de cima (a da carga) — face lisa na mesa; garra sobe.
"""
import cadquery as cq

from common import fab, hardware as hw
from common.features import caixa, cilindro, bolsao_porca
from maquina_a import layout as L
from maquina_a import eixo as E

ID = "A05"
NOME = "placa_carro"
TITULO = "Placa do carro (com garra da correia)"
QTD = {"B": 1, "A": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = "eixo_placa_carro"
ESTRUTURAL = True
MOVEL = True
CONTATO_ESPERADO = ("correia",)
JUSTIFICATIVA = ("placa mais larga (+-32) para as porcas da carga ficarem fora do patim e mais robusta para a boca com bola "
                 "de 60 g; garra da correia integrada (antes A06); lingua de tras estreita para nao alcancar as polias")

# ------------------------------------------------------------------ cotas (local do eixo, B)
Z0 = L.PATIM_TOPO_Z                   # CATALOGO 9 topo do patim = fundo da placa
E_PL = fab.E_PLACA                    # FAB 6
Z1 = Z0 + E_PL                        # 15 face da carga
FRENTE = (-32.0, 32.0, -32.0, 13.5)   # ESTIMADO x0, x1, y0, y1 da parte da frente
LINGUA = (-16.0, 16.0, 34.5)          # ESTIMADO x0, x1, y1 da lingua da garra (1 mm da placa do motor no fim do curso)
R_CANTO = 6.0                         # FAB

Y_CORREIA = L.Y_CORREIA               # CENA 23,5
CORREIA_COSTAS = hw.GT2_20T_PASSO_R - 0.4 + hw.CORREIA_ESP   # 7,35 costas da correia (ramo de cima)
CORREIA_DENTE = hw.GT2_20T_PASSO_R - 0.4                     # 5,97 lado dos dentes
CANAL_W = hw.CORREIA_6_L + 2 * 0.2    # FAB canal da correia (6,4)
GUIA_H = 1.0                          # FAB altura das guias laterais da correia
Y_PRES = (Y_CORREIA - 6.0, Y_CORREIA + 5.5)   # ESTIMADO parafusos das presilhas, 1 de cada lado da correia
GUIA_X = 3.0                          # ESTIMADO guias da correia so no meio, entre as duas pontas
X_PRES = 9.0                          # ESTIMADO centro de cada presilha (uma ponta da correia de cada lado)

PATIM_FUROS = hw.PATIM_FUROS          # CATALOGO 20x20
CARGA_FUROS = [(sx * 27.0, y) for sx in (-1, 1) for y in (-24.0, -8.0)]   # ESTIMADO fora do patim (|x|>22,7+3,4); chave livre da aba da boca

CIMA_IMPRESSAO = (0, 0, -1)           # impressa de cabeca para baixo


def local(eixo="B"):
    x0, x1, y0, y1 = FRENTE
    sk = (cq.Sketch().push([((x0 + x1) / 2, (y0 + y1) / 2)]).rect(x1 - x0, y1 - y0)
          .push([(0, (y1 - R_CANTO + LINGUA[2]) / 2)]).rect(LINGUA[1] - LINGUA[0], LINGUA[2] - y1 + R_CANTO)
          .clean().reset().vertices().fillet(R_CANTO))
    p = cq.Workplane("XY", origin=(0, 0, Z0)).placeSketch(sk).extrude(E_PL)
    # bloco da garra: desce ate as costas da correia, so na lingua (atras do patim)
    g = caixa(LINGUA[0], LINGUA[1], y1 + 1.5, LINGUA[2], CORREIA_COSTAS, Z0 + 0.5)
    g = g.edges("|Z").fillet(fab.R_EXTERNO)
    # guias laterais da correia
    w = CANAL_W / 2
    for s in (-1, 1):
        g = g.union(caixa(-GUIA_X, GUIA_X, Y_CORREIA + s * w + (0 if s > 0 else -fab.PAREDE_MIN), Y_CORREIA + s * w + (fab.PAREDE_MIN if s > 0 else 0),
                          CORREIA_COSTAS - GUIA_H, CORREIA_COSTAS + 0.1))
    p = p.union(g)
    try:
        p = p.faces(">Z").edges().chamfer(fab.CHANFRO_BASE)    # face que vai na mesa
    except Exception:
        pass
    # patim: 4x M3 com rebaixo por cima
    d_reb, h_reb = fab.REBAIXO_DIN912["M3"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = (sx * PATIM_FUROS[0] / 2, sy * PATIM_FUROS[1] / 2)
            p = p.cut(cilindro(fab.FURO_PASSANTE["M3"], E_PL + 2, (*c, Z0 - 1), (0, 0, 1)))
            p = p.cut(cilindro(d_reb, h_reb + 1, (*c, Z1 - h_reb), (0, 0, 1)))
    # carga: 4x M3 passante + porca embutida por baixo
    for c in CARGA_FUROS:
        p = p.cut(cilindro(fab.FURO_PASSANTE["M3"], E_PL + 2, (*c, Z0 - 1), (0, 0, 1)))
        p = p.cut(bolsao_porca("M3", (*c, Z0), (0, 0, 1), angulo=30.0, extra_saida=0.5))
    # presilhas: M3 de baixo para cima, porca embutida por cima
    for sx in (-1, 1):
        for y in Y_PRES:
            c = (sx * X_PRES, y)
            p = p.cut(cilindro(fab.FURO_PASSANTE["M3"], 20, (*c, CORREIA_COSTAS - 2), (0, 0, 1)))
            p = p.cut(bolsao_porca("M3", (*c, Z1 - fab.BOLSAO_PORCA["M3"][1]), (0, 0, 1), angulo=30.0, extra_saida=0.5))
    return p


def build(p=None, eixo="B"):
    return E.para_maquina(local(eixo), eixo)


def impressao(eixo="B"):
    sh = local(eixo).val()
    if eixo == "A":
        sh = sh.mirror("XY")          # espelhada, a face da carga ja fica em baixo
    else:
        sh = sh.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="B"):
    f = []
    h_reb = fab.REBAIXO_DIN912["M3"][1]
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.append(dict(nome="patim", tipo="DIN912", bitola="M3", comp=6,
                          ponto=(sx * PATIM_FUROS[0] / 2, sy * PATIM_FUROS[1] / 2, Z1 - h_reb), dir=(0, 0, -1),
                          antes_de=("A09", "A10", "boca", "berco"), extra=""))
    for sx in (-1, 1):
        for y in Y_PRES:
            f.append(dict(nome="presilha", tipo="DIN912", bitola="M3", comp=12,
                          ponto=(sx * X_PRES, y, CORREIA_DENTE - 3.0), dir=(0, 0, 1), chave=30,
                          extra="porca M3 no bolsao de cima da placa"))
    return f


def pares_furos(var):
    pares = []
    for k, (pa, da) in enumerate(hw.furos_patim(0.0)):
        mine = (pa[0], pa[1], Z1 - fab.REBAIXO_DIN912["M3"][1])
        pares.append((f"patim {k + 1}", (E.ponto_para_maquina(mine, var), E.dir_para_maquina((0, 0, -1), var)),
                      (E.ponto_para_maquina(pa, var), E.dir_para_maquina(da, var))))
    return pares


FICHA = dict(orientacao="de cabeca para baixo (face da carga na mesa)", suporte="nao", perimetros=4,
             infill="40% gyroid (estrutural)", camada=0.20,
             montagem=("1) porcas M3: 4 da carga por baixo e 4 das presilhas por cima; 2) placa no patim, 4x M3x6; "
                       "3) pontas da correia no canal da garra, presilhas A07 por baixo, 4x M3x12; 4) carga por cima, 4x M3x16."))
