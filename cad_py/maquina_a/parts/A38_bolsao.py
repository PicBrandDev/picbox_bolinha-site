"""A38 — Bolsao de coleta (pedestal, atras da porta).

Intencao:
- Funcao: recebe as bolas do tubo da bandeja (A14); o operador recolhe pela porta do pedestal e devolve ao
  magazine (ate o elevador existir). Cabe ~10 bolas.
- Interfaces: lateral direita x=207 (2x M4 + porca-garra pela parede do bolsao), tubo A14 por cima.
Impressao: em pe, aberto para cima.
"""
import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import bandeja as B
from maquina_a import layout as L

ID = "A38"
NOME = "bolsao"
TITULO = "Bolsao de coleta"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = []
E = fab.E_MEDIA                        # 3,2


def caixa_externa():
    xi, yi, zi = B.BOLSAO_INT
    x1 = B.BOLSAO_X1
    x0 = x1 - xi - 2 * E
    y0 = B.BOLSAO_Y0
    y1 = y0 + yi + 2 * E
    z1 = B.BOLSAO_Z_BORDA
    z0 = z1 - zi - E
    return x0, x1, y0, y1, z0, z1


FUROS = ((-180.0, B.BOLSAO_Z_BORDA - 8.0), (-80.0, B.BOLSAO_Z_BORDA - 8.0))   # (y, z) na parede da lateral


def local(var="-"):
    x0, x1, y0, y1, z0, z1 = caixa_externa()
    b = caixa(x0, x1, y0, y1, z0, z1).edges("|Z").fillet(fab.R_VISIVEL)
    b = b.cut(caixa(x0 + E, x1 - E, y0 + E, y1 - E, z0 + E, z1 + 1).edges("|Z").fillet(fab.R_VISIVEL - 1.0))
    try:
        b = b.faces("<Z").edges().chamfer(fab.CHANFRO_BASE)
    except Exception:
        pass
    for y, z in FUROS:
        b = b.cut(cilindro(fab.FURO_PASSANTE["M4"], 2 * E, (x1 - 1.5 * E, y, z), (1, 0, 0)))
    return b


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val()
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    x1 = B.BOLSAO_X1
    return [dict(nome="parede", tipo="DIN912", bitola="M4", comp=25, ponto=(x1 - E, y, z), dir=(1, 0, 0), chave=60,
                 extra="porca-garra M4 cravada por fora da lateral direita") for y, z in FUROS]


FICHA = dict(orientacao="em pe, aberto para cima", suporte="nao", perimetros=3, infill="15%", camada=0.20,
             montagem="parafusar na lateral direita por dentro (2x M4x25), embaixo do tubo da bandeja.")
