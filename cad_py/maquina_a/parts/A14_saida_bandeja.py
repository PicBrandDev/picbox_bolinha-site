"""A14 — Saida da bandeja: tubo-funil do canto frente-direita ate o bolsao.

Intencao:
- Funcao: a bola rola ate o canto mais baixo e cai no tubo (Ø48 por dentro); o tubo atravessa a placa e a
  divisoria e solta a bola no bolsao A38, dentro da porta do pedestal.
- Interfaces: topo do tubo rente ao EVA (cortado no plano inclinado, borda R3 por dentro: sem degrau), furo Ø54,5
  no MDF (localiza), gola apoiada na divisoria, furo Ø65 na divisoria (o cone sob a gola entra nele).
Impressao: em pe, tubo para cima; cone de 45 graus sob a gola.
"""
import math

import cadquery as cq

from common import fab
from common.features import cilindro
from maquina_a import bandeja as B

ID = "A14"
NOME = "saida_bandeja"
TITULO = "Saida da bandeja (tubo-funil)"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["B"]
CONTATO_ESPERADO = ("bandeja_mdf", "bandeja_eva", "divisoria")
E = fab.E_GROSSA - 1.0                 # 3 parede do tubo
GOLA = 64.0                            # ESTIMADO diametro da gola sobre a divisoria
H_GOLA = 2.0                           # ESTIMADO


def _plano_eva():
    x, y = B.SAIDA
    z = B.z_eva(x, y)
    n = cq.Vector(math.tan(B.INCL_X), -math.tan(B.INCL_Y), 1.0).normalized()
    return cq.Workplane(cq.Plane(origin=(x, y, z), xDir=(1, 0, -math.tan(B.INCL_X)), normal=n.toTuple())).rect(400, 400).extrude(200)


def local(var="-"):
    x, y = B.SAIDA
    di, de = B.D_SAIDA, B.D_SAIDA + 2 * E
    z0 = B.Z_TUBO_FIM
    zg = B.Z_DIVISORIA
    tubo = cilindro(de, 140.0, (x, y, z0), (0, 0, 1))
    gola = cilindro(GOLA, H_GOLA, (x, y, zg), (0, 0, 1))
    cone = cq.Solid.makeCone(de / 2, GOLA / 2, (GOLA - de) / 2, cq.Vector(x, y, zg - (GOLA - de) / 2), cq.Vector(0, 0, 1))
    p = tubo.union(gola).union(cq.Workplane("XY").add(cone)).cut(_plano_eva())
    p = p.cut(cilindro(di, 200.0, (x, y, z0 - 1), (0, 0, 1)))
    try:
        p = p.faces(">Z").edges(cq.selectors.RadiusNthSelector(0)).fillet(fab.R_VISIVEL)
    except Exception:
        pass
    try:
        p = p.faces("<Z").edges().chamfer(fab.CHANFRO_BASE)
    except Exception:
        pass
    return p


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val()
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    return []


def checa_bola(var="-"):
    """Bola cai do canto da bandeja pelo tubo ate o bolsao."""
    from common.checks import c7_interferencia
    x, y = B.SAIDA
    rb = 19.0 + fab.FOLGA_BOLA_RADIAL
    queda = cilindro(2 * rb, B.z_eva(x, y) + 19.0 - (B.BOLSAO_Z_BORDA - 10.0), (x, y, B.BOLSAO_Z_BORDA - 10.0), (0, 0, 1))
    from maquina_a import montagem as MT
    outros = {k: v for k, v in MT.corpos_bandeja().items() if k != "bandeja_eva" and k != "bandeja_mdf"}
    outros["A14"] = build()
    r = c7_interferencia(queda, outros)
    return dict(ok=r["ok"], queda=r, folga_radial=round(B.D_SAIDA / 2 - 19.0, 1))


FICHA = dict(orientacao="em pe", suporte="nao", perimetros=4, infill="20%", camada=0.20,
             montagem=("furo Ø54,5 na placa de MDF e Ø65 na divisoria (canto frente-direita); encaixar o tubo por cima ate a "
                       "gola apoiar na divisoria; topo rente ao EVA (cortar o EVA em volta)."))
