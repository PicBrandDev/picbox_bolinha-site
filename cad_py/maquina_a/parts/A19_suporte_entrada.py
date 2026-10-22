"""A19 — Suporte da entrada do magazine (lateral direita, por baixo da entrada e do motor do eixo A).

Intencao:
- Funcao: segura a entrada A18 (e a ponta direita do tubo) na lateral direita. O braco passa por baixo do motor do
  bloco A01 do eixo A (z<1509) e por fora do pe e do braco do FC dele (y>=61).
- Interfaces: lateral direita x=207 (2x M4 + porca-garra), fundo plano da A18 (2x M3x12 de baixo para cima).
Impressao: em pe na face da parede (x=207), braco subindo na vertical.
"""
import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import layout as L
from maquina_a import magazine as M
from maquina_a.parts import A18_entrada_magazine as A18

ID = "A19"
NOME = "suporte_entrada"
TITULO = "Suporte da entrada do magazine"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("A18",)
ESTRUTURAL = True

Y = (62.0, 78.0)                       # ESTIMADO braco (y>=61: fora do pe do A01 A, que vai ate y=58)
Y_PAREDE = (61.0, 95.0)                # ESTIMADO placa da parede
X_PAREDE = L.PAREDE_X
E = fab.E_PLACA                        # 6
X0 = 100.0                             # ESTIMADO inicio do braco (sob o fundo da A18)


def z_fundo_a18():
    a = M.eixo_tubo(M.X_ENTRADA[0])
    b = M.eixo_tubo(M.X_ENTRADA[1])
    return min(a[2], b[2]) - (M.TUBO_D / 2 + A18.E)


Z_BRACO = (z_fundo_a18() - 12.0, z_fundo_a18())
Z_PAREDE = (Z_BRACO[0] - 30.0, Z_BRACO[1])
FUROS_PAREDE = ((88.0, Z_PAREDE[0] + 8.0), (88.0, Z_PAREDE[1] - 6.0))


def local(var="-"):
    braco = caixa(X0, X_PAREDE, Y[0], Y[1], Z_BRACO[0], Z_BRACO[1])
    parede = caixa(X_PAREDE - E, X_PAREDE, Y_PAREDE[0], Y_PAREDE[1], Z_PAREDE[0], Z_PAREDE[1])
    mf = (cq.Workplane("XZ", origin=(0, Y[1], 0)).polyline([(X_PAREDE - E, Z_BRACO[0]), (X_PAREDE - E, Z_PAREDE[0]),
                                                             (X_PAREDE - E - 30.0, Z_BRACO[0])]).close().extrude(Y[1] - Y[0]))
    p = braco.union(parede).union(mf)
    try:
        p = p.edges("|Y").fillet(fab.R_EXTERNO)
    except Exception:
        pass
    for x, y in A18.FUROS_FUNDO:
        p = p.cut(cilindro(fab.FURO_PASSANTE["M3"], 20, (x, y, Z_BRACO[0] - 1), (0, 0, 1)))
    for y, z in FUROS_PAREDE:
        p = p.cut(cilindro(fab.FURO_PASSANTE["M4"], E + 2, (X_PAREDE - E - 1, y, z), (1, 0, 0)))
    return p


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val().rotate((0, 0, 0), (0, 1, 0), 90)     # face da parede (x=207) para baixo
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    f = [dict(nome="parede", tipo="DIN912", bitola="M4", comp=25, ponto=(X_PAREDE - E, y, z), dir=(1, 0, 0), chave=40,
              extra="porca-garra M4 cravada por fora da lateral direita") for y, z in FUROS_PAREDE]
    f += [dict(nome="entrada", tipo="DIN912", bitola="M3", comp=12, ponto=(x, y, Z_BRACO[0]), dir=(0, 0, 1), chave=30,
               extra="porca M3 no rasgo lateral do fundo da A18") for x, y in A18.FUROS_FUNDO]
    return f


FICHA = dict(orientacao="em pe na face da parede", suporte="nao", perimetros=4, infill="40% gyroid (estrutural)", camada=0.20,
             montagem="parafusar na lateral direita (2x M4x25); apoiar a entrada A18 em cima e prender por baixo (2x M3x12).")
