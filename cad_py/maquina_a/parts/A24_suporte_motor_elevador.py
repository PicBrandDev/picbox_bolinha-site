"""A24 — Suporte do motor do elevador (NEMA 17 em pe, embaixo da base A20, dentro do pedestal).

Intencao:
- Funcao: segura o motor com o eixo para cima, alinhado com a barra M8 do fuso; a gaiola tem janelas para apertar os
  dois parafusos do acoplamento 5x8.
- Interfaces: face do motor (4x M3x8 por dentro da gaiola, ANTES de prender na A20), A20 (4x M3x20 de baixo).
Impressao: em pe, placa do motor na mesa; janelas com topo em ponta; cone de 48 graus sob a flange.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import elevador as E
from maquina_a.parts import A20_base_elevador as A20

ID = "A24"
NOME = "suporte_motor_elevador"
TITULO = "Suporte do motor do elevador"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = []
CONTATO_ESPERADO = ("elev_nema17", "A20")
ESTRUTURAL = True
VISTA = (-1.0, -1.3, -0.6)

E_PLACA = fab.E_PLACA                  # 6
LADO = 46.0                            # ESTIMADO placa do motor
R_GAIOLA = (26.0, 30.0)                # ESTIMADO
R_FLANGE = 45.0                        # ESTIMADO
JANELA = (14.0, E.Z_MOTOR_FACE + E_PLACA + 3.0, E.Z_BASE0 - 12.0)   # largura, z0, z1 (topo em ponta acima)
Z0 = E.Z_MOTOR_FACE
Z1 = E.Z_BASE0
Z_FLANGE = Z1 - E_PLACA
Z_CABECA_FL = Z_FLANGE - 3.0           # assento da cabeca dos M3 da flange


def local(var="-"):
    x, y = E.C
    placa = caixa(x - LADO / 2, x + LADO / 2, y - LADO / 2, y + LADO / 2, Z0, Z0 + E_PLACA).edges("|Z").chamfer(6.0)
    gaiola = cilindro(2 * R_GAIOLA[1], Z1 - Z0, (x, y, Z0), (0, 0, 1))
    perfil = [(R_GAIOLA[1] - 0.01, Z_FLANGE - 1.1 * (R_FLANGE - R_GAIOLA[1])), (R_FLANGE, Z_FLANGE), (R_FLANGE, Z1),
              (R_GAIOLA[1] - 0.01, Z1)]
    flange = cq.Workplane("XZ").polyline(perfil).close().revolve(360, (0, 0, 0), (0, 1, 0))
    corpo = placa.union(gaiola).union(cq.Workplane("XY").add(flange.val().translate((x, y, 0))))
    corpo = corpo.cut(cilindro(2 * R_GAIOLA[0], Z1 - Z0 - E_PLACA + 1, (x, y, Z0 + E_PLACA), (0, 0, 1)))
    corpo = corpo.cut(cilindro(23.0, E_PLACA + 2, (x, y, Z0 - 1), (0, 0, 1)))          # ressalto do motor
    corpo = corpo.cut(cilindro(26.0, 20, (x, y, Z1 - 15), (0, 0, 1)))                  # porca e rolamento da A20
    w, za, zb = JANELA
    for ang in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(ang)
        d = (math.cos(a), math.sin(a), 0)
        lat = (-math.sin(a), math.cos(a), 0)
        pl = cq.Plane(origin=(x, y, za), xDir=lat, normal=d)
        jan = (cq.Workplane(pl).polyline([(-w / 2, 0), (w / 2, 0), (w / 2, zb - za), (0, zb - za + w / 2), (-w / 2, zb - za)])
               .close().extrude(R_FLANGE + 5))
        corpo = corpo.cut(jan)
    for fx, fy in E.furos_motor():                                                     # M3 no motor, cabeca por dentro
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"], E_PLACA + 2, (fx, fy, Z0 - 1), (0, 0, 1)))
        corpo = corpo.cut(cilindro(fab.REBAIXO_DIN912["M3"][0], 20, (fx, fy, Z0 + E_PLACA - fab.REBAIXO_DIN912["M3"][1]), (0, 0, 1)))
    for ang in A20.FUROS_A24:                                                          # M3 de baixo para a A20
        px, py, _ = E.p(A20.R_FURO_A24, ang)
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"], 20, (px, py, Z_CABECA_FL - 1), (0, 0, 1)))
        corpo = corpo.cut(cilindro(fab.REBAIXO_DIN912["M3"][0], Z_CABECA_FL - Z0 + 1, (px, py, Z0 - 1), (0, 0, 1)))
    try:
        corpo = corpo.faces("<Z").edges().chamfer(fab.CHANFRO_BASE)
    except Exception:
        pass
    return corpo


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val()
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    f = [dict(nome=f"motor{k}", tipo="DIN912", bitola="M3", comp=8, ponto=(fx, fy, Z0 + E_PLACA - fab.REBAIXO_DIN912["M3"][1]),
              dir=(0, 0, -1), chave=40, antes_de=("A20", "elev_608", "elev_barra", "elev_acoplamento"),
              extra="no motor, por dentro da gaiola, antes de prender o suporte na A20")
         for k, (fx, fy) in enumerate(E.furos_motor())]
    f += [dict(nome=f"base{k}", tipo="DIN912", bitola="M3", comp=20, comp_modelo=Z1 - Z_CABECA_FL,
               ponto=E.p(A20.R_FURO_A24, ang, Z_CABECA_FL), dir=(0, 0, 1), chave=60,
               extra="rosca no plastico da A20 (furo 2,6) ou inserto M3")
          for k, ang in enumerate(A20.FUROS_A24)]
    return f


FICHA = dict(orientacao="em pe, placa do motor na mesa", suporte="nao", perimetros=4, infill="40% gyroid (estrutural)",
             camada=0.20,
             montagem=("1) motor na placa (4x M3x8 por dentro); 2) acoplamento 5x8 no eixo do motor (janela); 3) subir o "
                       "conjunto ate a A20, barra M8 entrando no acoplamento; 4) 4x M3x20 de baixo; 5) apertar o "
                       "acoplamento na barra pela janela."))
