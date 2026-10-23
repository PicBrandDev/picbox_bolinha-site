"""A07 — Presilha dentada da correia (4 por maquina: 2 por carro, A e B iguais).

Intencao:
- Funcao: aperta uma ponta da GT2 6 mm contra o fundo da garra da placa A05; nervuras no passo 2 entram nos dentes.
- Cargas: tracao da correia (~30 N) em cisalhamento nas nervuras.
- Interfaces: A05 (2x M3x12, porca embutida em cima da placa), correia (dentes para baixo no ramo de cima).
Impressao: deitada nas costas, nervuras para cima.
"""
import cadquery as cq

from common import fab, hardware as hw
from common.features import caixa, cilindro
from maquina_a import eixo as E
from maquina_a.pecas import A05_placa_carro as P

ID = "A07"
NOME = "presilha"
TITULO = "Presilha dentada da correia"
QTD = {"B": 2, "A": 2}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = "eixo_presilha"
MOVEL = True
CONTATO_ESPERADO = ("correia",)
JUSTIFICATIVA = "presilha mais longa (12) e larga"
PAREDE_MINIMA = 0.7                   # FAB excecao: nervuras sao os dentes GT2 (0,8); a base tem 3 mm

E_PRES = 3.0                          # FAB
COMP_X = 12.0                         # ESTIMADO ao longo da correia
LARG_Y = P.Y_PRES[1] - P.Y_PRES[0] + 8.0   # cobre os 2 parafusos
PASSO = 2.0                           # CATALOGO GT2
DENTE = (1.0, 0.75)                   # CATALOGO largura, altura do dente GT2 (aprox.)


def _uma(xc):
    z1 = P.CORREIA_DENTE
    y0, y1 = P.Y_PRES[0] - 4.0, P.Y_PRES[1] + 4.0
    p = caixa(xc - COMP_X / 2, xc + COMP_X / 2, y0, y1, z1 - E_PRES, z1).edges("|Z").fillet(fab.R_EXTERNO)
    # nervuras nos vaos dos dentes, so na largura da correia
    w = hw.CORREIA_6_L / 2
    n = int(COMP_X // PASSO)
    for k in range(n):
        x = xc - COMP_X / 2 + PASSO / 2 + k * PASSO
        p = p.union(caixa(x - DENTE[0] / 2 * 0.8, x + DENTE[0] / 2 * 0.8, P.Y_CORREIA - w, P.Y_CORREIA + w, z1 - 0.01, z1 + DENTE[1] * 0.8))
    for y in P.Y_PRES:
        p = p.cut(cilindro(fab.FURO_PASSANTE["M3"], E_PRES + 2, (xc, y, z1 - E_PRES - 1), (0, 0, 1)))
    return p


def local(eixo="B", lado=1):
    return _uma(lado * P.X_PRES)


def build(p=None, eixo="B"):
    a = E.para_maquina(local(eixo, 1), eixo).val()
    b = E.para_maquina(local(eixo, -1), eixo).val()
    return cq.Workplane("XY").add(cq.Compound.makeCompound([a, b]))


def impressao(eixo="B"):
    sh = _uma(0.0).val()
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


ESPERADO_SOLIDOS = 2


def fixadores(var="B"):
    return []


FICHA = dict(orientacao="deitada nas costas, nervuras para cima", suporte="nao", perimetros=4, infill="100%", camada=0.16,
             montagem="ponta da correia no canal da garra (dentes para baixo), presilha por baixo, 2x M3x12 (ver A05).")
