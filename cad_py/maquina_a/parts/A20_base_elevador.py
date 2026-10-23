"""A20 — Base do elevador: pe do tubo, piso conico e rolamento de baixo do fuso (embaixo da divisoria).

Intencao:
- Funcao: segura a ponta de baixo do tubo acrilico Ø100 (ressalto + anel por fora + tampao por dentro), faz o piso
  onde a bola cai (sobe 4 mm para o centro: a bola vai para a parede), guia o pe do trilho e leva o rolamento 608
  da barra M8 do fuso. A flange fica presa por baixo da divisoria; o suporte do motor A24 parafusa embaixo.
- Interfaces: divisoria (furo Ø101; 3 parafusos de madeira de cima, antes da bandeja), tubo, trilho Ø8 (encaixe 20 mm), 608ZZ
  (prensado de cima, no fundo do rebaixo do piso), barra M8 (arruela Ø14 + porca no rebaixo: o fuso apoia no 608), A24 (4x M3 de baixo).
Impressao: em pe, fundo plano; cone de 48 graus sob a flange.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import elevador as E

ID = "A20"
NOME = "base_elevador"
TITULO = "Base do elevador (pe do tubo + piso)"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = []
CONTATO_ESPERADO = ("divisoria", "elev_acrilico", "elev_608", "elev_trilho")
ESTRUTURAL = True
VISTA = (-1.0, -1.3, 0.9)

R_TAMPAO = E.R_TI - E.FOLGA_TUBO       # 46,7
R_ANEL0 = E.TUBO_D / 2 + E.FOLGA_TUBO  # 50,3
R_ANEL1 = R_ANEL0 + fab.E_GROSSA       # 54,3
R_FLANGE = 66.0                        # ESTIMADO
Z_FLANGE = E.Z_DIV_BAIXO - fab.E_PLACA  # 1076
D_REBAIXO = 26.0                       # FAB porca M8 + arruela embaixo do fuso
Z_REBAIXO = E.Z_REBAIXO
SETORES_PAREDE = ((-35.0, 35.0), (235.0, 305.0))   # sem anel/flange onde o tubo encosta nas paredes (2 mm)
FUROS_FLANGE = (60.0, 150.0, 220.0)    # angulos (r=60)
R_FURO_FLANGE = 60.0
FURO_PILOTO = 2.8                      # FAB parafuso de madeira 3,5 em plastico
FUROS_A24 = (45.0, 135.0, 225.0, 315.0)   # angulos (r=38): M3 de baixo vindos da A24
R_FURO_A24 = 38.0


def local(var="-"):
    zc = E.Z_PISO + E.CONE_PISO
    perfil = [(0, E.Z_BASE0), (R_ANEL1, E.Z_BASE0), (R_ANEL1, E.Z_BASE0 + 1.5),
              (R_FLANGE, E.Z_BASE0 + 1.5 + 1.1 * (R_FLANGE - R_ANEL1)),
              (R_FLANGE, E.Z_DIV_BAIXO), (R_ANEL0, E.Z_DIV_BAIXO), (R_ANEL0, E.Z_TUBO0), (R_TAMPAO, E.Z_TUBO0),
              (R_TAMPAO, E.z_piso(R_TAMPAO)), (0, zc)]
    corpo = cq.Workplane("XZ").polyline(perfil).close().revolve(360, (0, 0, 0), (0, 1, 0))
    corpo = cq.Workplane("XY").add(corpo.val().translate((E.C[0], E.C[1], 0)))
    for a0, a1 in SETORES_PAREDE:                          # junto das paredes fica so o fundo
        corpo = corpo.cut(E.setor(R_TAMPAO + 0.01, 90.0, a0, a1, E.Z_TUBO0, E.Z_DIV_BAIXO + 1))
    corpo = corpo.intersect(caixa(-500, L_PAREDE, -L_PAREDE, 500, 0, 3000))
    x, y = E.C
    corpo = corpo.cut(cilindro(E.D_ROLAMENTO[0] + fab.ROLAMENTO_PRENSADO, E.D_ROLAMENTO[1] + 1, (x, y, E.Z_608_BAIXO), (0, 0, 1)))
    corpo = corpo.cut(cilindro(9.0, 100.0, (x, y, E.Z_BASE0), (0, 0, 1)))
    corpo = corpo.cut(cilindro(D_REBAIXO, 30.0, (x, y, Z_REBAIXO), (0, 0, 1)))
    corpo = corpo.cut(cilindro(E.D_TRILHO + 0.3, 40.0, E.p(E.R_TRILHO, E.ANG_TRILHO, E.Z_TRILHO[0]), (0, 0, 1)))
    for a in FUROS_FLANGE:                                 # parafuso de madeira de cima (pela divisoria): furo piloto
        corpo = corpo.cut(cilindro(FURO_PILOTO, 12.0, E.p(R_FURO_FLANGE, a, E.Z_DIV_BAIXO - 12.0), (0, 0, 1)))
    for a in FUROS_A24:                                    # M3 com rosca no plastico (ou inserto)
        corpo = corpo.cut(cilindro(fab.FURO_AUTOATARRAXANTE["M3"], 12.0, E.p(R_FURO_A24, a, E.Z_BASE0 - 1), (0, 0, 1)))
    try:
        corpo = corpo.faces("<Z").edges().chamfer(fab.CHANFRO_BASE)
    except Exception:
        pass
    return corpo


L_PAREDE = 206.0                       # 1 mm das laterais


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val()
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    return [dict(nome=f"divisoria{k}", tipo="ISO7380", bitola="M4", comp=30, comp_modelo=E.Z_DIV_TOPO - E.Z_DIV_BAIXO,
                 ponto=E.p(R_FURO_FLANGE, a, E.Z_DIV_TOPO), dir=(0, 0, -1), chave=60, antes_de=("bandeja", "A12", "A13"),
                 extra="parafuso de madeira 3,5x30 cabeca chata (escarear a divisoria), de cima, antes da bandeja")
            for k, a in enumerate(FUROS_FLANGE)]


def checa_bola(var="-"):
    """Entrada: a bola desce da bandeja pelo furo do tubo ate o piso (fuso fora: ele gira e empurra a bola);
    tubo + trilho contra os dois carros no curso inteiro."""
    import numpy as np
    from common import hardware as hw
    from common.checks import c7_interferencia, c8_movimento
    from common.malha import para_trimesh
    from maquina_a import bandeja as B
    from maquina_a import montagem as MT
    from maquina_a import verifica as V
    r = E.R_B - 0.5                                        # 0,5 de contato permitido (piso, EVA, parede)
    obst = {"A20": build(), **{k: v for k, v in E.hardware().items() if k in ("elev_acrilico", "elev_trilho")}}
    obst.update({k: v for k, v in MT.corpos_bandeja().items()})
    res = {}
    for ang in (63.0, 100.0, 135.0, 180.0, 207.0):         # 63 e 207: cunhas da bola entre o tubo e as paredes
        pts = []
        for rr in np.arange(69.0, E.R_BOLA - 0.1, -4.0):   # rola para dentro na altura da bandeja
            x, y, _ = E.p(rr, ang)
            pts.append((x, y, max(B.z_eva(x, y), E.Z_FURO[0]) + E.R_B))
        x, y, _ = E.p(E.R_BOLA, ang)
        for z in np.arange(pts[-1][2], E.z_piso(E.R_BOLA) + E.R_B - 0.1, -4.0):
            pts.append((x, y, z))
        bolas = cq.Workplane("XY").add([hw.bola(c, 2 * r).val() for c in pts])
        res[f"{ang:.0f}"] = c7_interferencia(bolas, obst)["colisoes"]
    # tubo e trilho contra os carros (compradas: o c8 da peca nao cobre)
    corpos = {k: para_trimesh(v, 0.1, 0.3) for k, v in E.hardware().items() if k in ("elev_acrilico", "elev_trilho")}
    carros = {}
    for e in ("A", "B"):
        c0, c1 = MT.CURSO[e]
        xs = list(np.arange(c0, c1 + 1e-6, 5.0)) + [c1]
        carros[e] = c8_movimento(corpos, lambda xx, e=e: V.carro_em(e, xx), xs)
    ok = all(not v for v in res.values()) and all(c["ok"] for c in carros.values())
    return dict(ok=ok, entrada=res, carros={e: dict(ok=c["ok"], menor=c["menor"]) for e, c in carros.items()},
                nota="bola rola da bandeja (cunhas 63 e 207 graus e meio do arco) ate o piso; carros A e B no curso inteiro")


FICHA = dict(orientacao="em pe, fundo plano", suporte="nao", perimetros=4, infill="40% gyroid (estrutural)", camada=0.20,
             montagem=("1) prensar o 608 de cima no fundo do rebaixo; 2) cortar o furo Ø101 na divisoria (canto frente-direita) e "
                       "segurar a base por baixo e parafusar de cima (3 parafusos de madeira 3,5x30 cabeca chata); 3) descer o tubo (com o trilho ja "
                       "aparafusado) pelo furo da divisoria ate o ressalto, trilho no encaixe; 4) A24 + motor por baixo."))
