"""A36 — Garfo do embolo do solenoide (carro A).

Intencao:
- Funcao: liga o embolo do solenoide (vertical) ao pino da alavanca da portinhola de tras: rasgo horizontal
  deixa o pino correr em y enquanto o embolo sobe 9,5 mm (abre 60 graus).
- Interfaces: embolo Ø7,4 (furo justo + pino M2 transversal, ESTIMADO medir), pino M3 da alavanca.
Impressao: em pe, embolo para cima.
"""
import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import soltura as S

ID = "A36"
NOME = "garfo"
TITULO = "Garfo do embolo do solenoide"
QTD = {"A": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
MOVEL = True
COORD_MAQUINA = True
EIXO = "A"
CONTATO_ESPERADO = ("solenoide",)

LARG = (11.0, 12.0)                   # ESTIMADO x, y
D_EMBOLO = 7.4 + 2 * fab.ENCAIXE_JUSTO


def local(var="A", abertura=0.0):
    zp = S.pino_alavanca(abertura)[1]
    z0, z1 = zp - S.GARFO_H / 2, zp + S.GARFO_H / 2
    x0, x1 = S.X_EMBOLO - LARG[0] / 2, S.X_EMBOLO + LARG[0] / 2
    g = caixa(x0, x1, S.Y_PINO - LARG[1] / 2, S.Y_PINO + LARG[1] / 2, z0, z1).edges("|Z").fillet(fab.R_EXTERNO)
    g = g.union(cilindro(D_EMBOLO + 5.0, 6.0, (S.X_EMBOLO, S.Y_PINO, z1 - 0.1), (0, 0, 1)))
    g = g.cut(cilindro(D_EMBOLO, 8.0, (S.X_EMBOLO, S.Y_PINO, z1), (0, 0, 1)))
    g = g.cut(cilindro(2.2, 20.0, (S.X_EMBOLO, S.Y_PINO - 10.0, z1 + 3.0), (0, 1, 0)))       # pino M2 transversal
    d = fab.FURO_PASSANTE["M3"] + 0.2
    g = g.cut(cq.Workplane("YZ", origin=(x0 - 1, 0, 0)).center(S.Y_PINO, zp).slot2D(d + 3.0, d, 0).extrude(LARG[0] + 2))
    return g


def build(p=None, var="A"):
    return local(var)


def impressao(var="A"):
    sh = local(var).val()
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="A"):
    return []


FICHA = dict(orientacao="em pe", suporte="nao", perimetros=4, infill="100%", camada=0.16,
             montagem="encaixar no embolo e travar com pino M2x12 (ou arame Ø2); rasgo no pino da alavanca.")
