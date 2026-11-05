"""A12 — Calcos da bandeja (6, alturas diferentes).

Intencao:
- Funcao: apoiam a placa de MDF 6 da bandeja sobre a divisoria e dao as duas inclinacoes (3,5 graus para +x,
  3 graus para a frente); o topo de cada calco e o plano de baixo da placa.
- Interfaces: divisoria (z=1100), placa de MDF (parafuso de madeira 3,5x40 de cima, atravessa placa e calco).
Impressao: em pe, na base plana.
"""
import math

import cadquery as cq

from common import fab
from common.features import cilindro
from maquina_a import bandeja as B

ID = "A12"
NOME = "calco"
TITULO = "Calco da bandeja"
QTD = {str(k): 1 for k in range(len(B.CALCOS))}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["B"]
CONTATO_ESPERADO = ("bandeja_mdf", "divisoria")
D = 30.0                               # ESTIMADO


def _plano_mdf():
    """Semi-espaco acima do plano de baixo da placa de MDF."""
    x, y = 0.0, -100.0
    z = B.z_mdf_baixo(x, y)
    n = cq.Vector(math.tan(B.INCL_X), -math.tan(B.INCL_Y), 1.0).normalized()
    return cq.Workplane(cq.Plane(origin=(x, y, z), xDir=(1, 0, -math.tan(B.INCL_X)), normal=n.toTuple())).rect(2000, 2000).extrude(500)


def local(var="0"):
    x, y = B.CALCOS[int(var)]
    c = cilindro(D, 80.0, (x, y, B.Z_DIVISORIA), (0, 0, 1)).cut(_plano_mdf())
    c = c.cut(cilindro(4.0, 100.0, (x, y, B.Z_DIVISORIA - 1), (0, 0, 1)))
    try:
        c = c.faces("<Z").edges().chamfer(fab.CHANFRO_BASE)
    except Exception:
        pass
    return c


def altura(var):
    x, y = B.CALCOS[int(var)]
    return B.z_mdf_baixo(x, y) - B.Z_DIVISORIA


def build(p=None, var="0"):
    return local(var)


def impressao(var="0"):
    sh = local(var).val()
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="0"):
    return []


FICHA = dict(orientacao="em pe, base plana", suporte="nao", perimetros=4, infill="40%", camada=0.20,
             montagem=("marcar as posicoes na divisoria (gabarito pela placa); calco no lugar, placa por cima, "
                       "parafuso de madeira 3,5x40 de cima atravessando placa e calco."))
