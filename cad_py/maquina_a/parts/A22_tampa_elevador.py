"""A22 — Tampa do elevador: segura o topo do tubo, o rolamento de cima do fuso e a saida A25; presa na lateral direita.

Intencao:
- Funcao: placa sobre o topo do tubo (saia por fora), 608 da barra M8 no centro; suporte descendo na lateral direita
  (2x M4 de fora da maquina, porcas por dentro); 2 abas por cima dos postes da saida A25 (M3 de cima).
- Interfaces: tubo (topo apoiado, saia com folga 0,3), 608ZZ (prensado por baixo), lateral direita x=207, A25.
Impressao: de cabeca para baixo (topo da placa na mesa); saia e suporte sobem.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro, teardrop
from maquina_a import elevador as E

ID = "A22"
NOME = "tampa_elevador"
TITULO = "Tampa do elevador (topo do tubo)"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("elev_acrilico", "elev_608", "lateral_dir", "A25")
ESTRUTURAL = True
VISTA = (-1.0, -1.3, 0.9)

Z0 = E.Z_TUBO1                         # 1640 fundo da placa (topo do tubo)
Z1 = Z0 + E.E_TAMPA                    # 1650
R_SAIA = (E.TUBO_D / 2 + E.FOLGA_TUBO, E.TUBO_D / 2 + E.FOLGA_TUBO + 3.0)
H_SAIA = 15.0                          # ESTIMADO
SEM_SAIA = ((-35.0, 35.0), (120.0, 177.0), (235.0, 305.0))   # paredes e saida da bola
X_PAREDE = 207.0
SUPORTE = (201.0, (-128.0, -104.0), 1600.0)   # x da face de dentro, faixa em y, z de baixo
FUROS_PAREDE = ((-116.0, 1612.0), (-116.0, 1630.0))
E_ABA = 9.0                            # ESTIMADO aba sobre cada poste da A25


def local(var="-"):
    x, y = E.C
    corpo = cilindro(2 * R_SAIA[1], Z1 - Z0, (x, y, Z0), (0, 0, 1))
    saia = cilindro(2 * R_SAIA[1], H_SAIA, (x, y, Z0 - H_SAIA), (0, 0, 1)).cut(
        cilindro(2 * R_SAIA[0], H_SAIA + 2, (x, y, Z0 - H_SAIA - 1), (0, 0, 1)))
    for a0, a1 in SEM_SAIA:
        saia = saia.cut(E.setor(R_SAIA[0] - 1, R_SAIA[1] + 1, a0, a1, Z0 - H_SAIA - 1, Z0))
    corpo = corpo.union(saia)
    for px, py in E.POSTES:                                 # abas por cima dos postes
        corpo = corpo.union(caixa(px - E_ABA, px + E_ABA, py - E_ABA, py + E_ABA, Z0, Z1))
    corpo = corpo.intersect(caixa(-500, X_PAREDE - 1.0, -X_PAREDE + 1.0, 500, 0, 3000))
    xs, (ys0, ys1), zs = SUPORTE
    sup = caixa(xs - 13.0, X_PAREDE, ys0, ys1, Z0, Z1).union(caixa(xs, X_PAREDE, ys0, ys1, zs, Z1))
    mf = (cq.Workplane("XZ", origin=(0, ys1, 0)).polyline([(xs, Z0), (xs, Z0 - 10.0), (xs - 10.0, Z0)]).close()
          .extrude(ys1 - ys0))                              # mao-francesa a 45 graus sob a placa
    corpo = corpo.union(sup).union(mf)
    try:
        corpo = corpo.faces(">Z").edges().chamfer(fab.CHANFRO_BASE)   # topo da placa = face na mesa
    except Exception:
        pass
    corpo = corpo.cut(cilindro(E.D_ROLAMENTO[0] + fab.ROLAMENTO_PRENSADO, E.D_ROLAMENTO[1] + 1, (x, y, Z0 - 1), (0, 0, 1)))   # por baixo
    corpo = corpo.cut(cilindro(9.0, 30, (x, y, Z0 - 10), (0, 0, 1)))
    for py, pz in FUROS_PAREDE:                             # M4 de fora; porca no bolsao da face de dentro
        corpo = corpo.cut(teardrop(fab.FURO_PASSANTE["M4"], X_PAREDE - xs + 2, (xs - 1, py, pz), (1, 0, 0), (0, 0, -1)))
        s4, h4 = fab.BOLSAO_PORCA["M4"]
        corpo = corpo.cut(caixa(xs - 1, xs + h4, py - s4 / 2, py + s4 / 2, pz - s4 / 2 / 0.866, pz + s4 / 2 / 0.866))
    for px, py in E.POSTES:                                 # M3 de cima para os postes da A25
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"], 20, (px, py, Z0 - 5), (0, 0, 1)))
    return corpo


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val().rotate((0, 0, 0), (1, 0, 0), 180)     # topo da placa na mesa
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    f = [dict(nome=f"parede{k}", tipo="DIN912", bitola="M4", comp=30, comp_modelo=L_FORA,
              ponto=(X_PAREDE + 18.0, py, pz), dir=(-1, 0, 0), chave=40,
              extra="de fora da lateral direita (furo 4,5 na lateral); porca M4 no bolsao da face de dentro do suporte")
         for k, (py, pz) in enumerate(FUROS_PAREDE)]
    f += [dict(nome=f"saida{k}", tipo="DIN912", bitola="M3", comp=20, ponto=(px, py, Z1), dir=(0, 0, -1), chave=40,
               extra="porca M3 no rasgo do poste da A25") for k, (px, py) in enumerate(E.POSTES)]
    return f


L_FORA = 18.0 + 6.0                    # haste modelada: lateral (18) + parede do suporte (6)


FICHA = dict(orientacao="de cabeca para baixo (topo da placa na mesa)", suporte="nao", perimetros=4,
             infill="40% gyroid (estrutural)", camada=0.20,
             montagem=("1) 608 prensado por baixo; 2) furar a lateral direita (2x Ø4,5) no gabarito do suporte; 3) com o fuso "
                       "e a saida A25 no lugar, assentar a tampa no tubo (barra no 608) e parafusar a saida (2x M3x20 de "
                       "cima); 4) 2x M4x30 de fora da lateral; 5) porca M8 por cima do 608."))
