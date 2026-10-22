"""A18 — Entrada do magazine: encaixe do tubo Ø50, canal Ø44 e funil de carga.

Intencao:
- Funcao: recebe a ponta direita do tubo; a bola colocada no funil (a mao, por enquanto; depois o elevador) cai no
  canal e rola para o tubo. Segura pelo suporte A19 na lateral direita (passa por cima do motor do eixo A).
- Interfaces: tubo (encaixe deslizante 15 mm), A19 por baixo (2x M3 de baixo para cima, porcas em rasgos laterais).
- Bola: canal Ø44 (folga radial 3), mesma inclinacao do tubo; boca do funil Ø74 com borda arredondada.
Impressao: em pe, fundo plano; furos horizontais em gota com a ponta para cima.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro, teardrop, bolsao_porca
from maquina_a import magazine as M

ID = "A18"
NOME = "entrada_magazine"
TITULO = "Entrada do magazine (encaixe + funil)"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("tubo",)
VISTA = (-1.0, -1.3, 0.8)

E = fab.E_MEDIA                        # 3,2
ENCAIXE = 15.0
D_FUNIL_TOPO = 74.0                    # ESTIMADO
FUROS_FUNDO = ((110.0, 70.0), (140.0, 70.0))   # ESTIMADO 2x M3 de baixo para cima (suporte A19 por baixo da entrada)
CIMA = (0, 0, 1)


def local(var="-"):
    x0, x3 = M.X_ENTRADA
    xt = M.X_TUBO[1]
    a = cq.Vector(*M.eixo_tubo(x0))
    b = cq.Vector(*M.eixo_tubo(x3))
    n = (b - a).normalized()
    L = (b - a).Length
    r_ext = M.TUBO_D / 2 + E
    corpo = cilindro(2 * r_ext, L, a.toTuple(), n.toTuple())
    zb = min(a.z, b.z) - r_ext
    corpo = corpo.union(caixa(x0, x3, M.Y_MAG - r_ext, M.Y_MAG + r_ext, zb, max(a.z, b.z)))
    # telhado a 45 graus por cima: envolve a ponta da gota dos furos horizontais (impressao sem suporte)
    h_tel = (M.TUBO_D / 2 + fab.ENCAIXE_DESLIZANTE) * math.sqrt(2) + 2.0
    tel = (cq.Workplane(cq.Plane(origin=a.toTuple(), xDir=(0, 1, 0), normal=n.toTuple()))
           .polyline([(-h_tel, 0), (0, h_tel), (h_tel, 0)]).close().extrude(L))
    corpo = corpo.union(tel.intersect(caixa(x0 - 5, x3 + 5, M.Y_MAG - r_ext, M.Y_MAG + r_ext, zb, 3000)))
    # funil
    xf = M.X_FUNIL
    zf0 = M.eixo_tubo(xf)[2]
    h = M.Z_FUNIL_TOPO - zf0
    cone_ext = cq.Solid.makeCone(M.TUBO_DI / 2 + E + 2, D_FUNIL_TOPO / 2 + E, h, cq.Vector(xf, M.Y_MAG, zf0), cq.Vector(0, 0, 1))
    corpo = corpo.union(cq.Workplane("XY").add(cone_ext))

    # furos: encaixe do tubo (gota), canal Ø44 (gota), funil
    corpo = corpo.cut(teardrop(M.TUBO_D + 2 * fab.ENCAIXE_DESLIZANTE, ENCAIXE + 4, (a - n * 4).toTuple(), n.toTuple(), CIMA))
    corpo = corpo.cut(teardrop(M.TUBO_DI, x3 - xt - 3.0, M.eixo_tubo(xt - 0.5), n.toTuple(), CIMA))
    z_cone = zf0 + M.TUBO_DI / 2 + 4.0                    # o cone comeca acima do canal
    cone_int = cq.Solid.makeCone(M.TUBO_DI / 2 + 0.5, D_FUNIL_TOPO / 2, M.Z_FUNIL_TOPO - z_cone + 0.01,
                                 cq.Vector(xf, M.Y_MAG, z_cone), cq.Vector(0, 0, 1))
    corpo = corpo.cut(cq.Workplane("XY").add(cone_int))
    corpo = corpo.cut(cilindro(M.TUBO_DI + 1.0, z_cone - zf0 + 1.0, (xf, M.Y_MAG, zf0), (0, 0, 1)))
    try:
        corpo = corpo.faces(">Z").edges(cq.selectors.RadiusNthSelector(0)).fillet(fab.R_VISIVEL)
    except Exception:
        pass
    try:
        corpo = corpo.faces("<Z").edges().chamfer(fab.CHANFRO_BASE)
    except Exception:
        pass
    corpo = corpo.intersect(caixa(x0, x3, -500, 500, 0, 3000))
    s3, h3 = fab.BOLSAO_PORCA["M3"]
    zp = zb + 3.0                                          # porca entra por um rasgo lateral (+y), 3 mm acima do fundo
    for x, y in FUROS_FUNDO:
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"], 6.0, (x, y, zb - 1), (0, 0, 1)))
        corpo = corpo.cut(caixa(x - s3 / 2, x + s3 / 2, y - s3 / 2 / 0.866, M.Y_MAG + r_ext + 1, zp, zp + h3))
    return corpo


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val()
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    return []


FICHA = dict(orientacao="em pe, fundo plano", suporte="nao", perimetros=4, infill="20% gyroid", camada=0.20,
             montagem="porcas M3 pelos rasgos laterais do fundo; encaixar o tubo; apoiar no suporte A19 e prender por baixo (2x M3x12).")
