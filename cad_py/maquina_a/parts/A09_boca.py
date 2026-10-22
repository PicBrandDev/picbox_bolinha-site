"""A09 — Boca do buraco (carro B).

Intencao:
- Funcao: abertura redonda Ø50 no plano z=1220 (queda de 250 a partir da soltura); garganta com barreira IR
  (LED IR333C + TIL78) que detecta a bola passando.
- Cargas: impacto da bola de 60 g a ~2,2 m/s na borda (pico de centenas de N); a garganta funciona como viga
  alta, ligada ao pe por duas costelas.
- Movimento: anda com o carro B (+-140, ate +-144,2).
- Interfaces: placa do carro A05 (4x M3x12 nas porcas embutidas da placa), LED/TIL78 Ø5 (furo justo + cola).
- Bola: passa reta pela garganta Ø50 e cai na bandeja; fundo da garganta fica acima da bola rolando na bandeja.
Impressao: em pe, apoiada no fundo plano (z=15); aba com cone de 50 graus por baixo, borda de cima arredondada.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro, teardrop
from maquina_a import layout as L
from maquina_a import eixo as E
from maquina_a.parts import A05_placa_carro as P

ID = "A09"
NOME = "boca"
TITULO = "Boca do buraco"
QTD = {"B": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = {"B": "boca_alvo"}
ESTRUTURAL = True
MOVEL = True
VISTA = (-0.9, -1.6, 1.0)
JUSTIFICATIVA = "abertura redonda Ø50 (usuario) no lugar de 78x60; garganta e costelas para a bola de 60 g; borda redonda"

# ------------------------------------------------------------------ cotas (local do eixo B, carro em x=0)
D_BOCA = L.BOCA_D                     # MEDIDO 50
Y_C = L.Y_JOGO                        # CENA -57
Z_TOPO = L.RECUO_BOCA                 # PARAMS 45 (= 1220 na maquina)
E_TOPO = fab.E_GROSSA                 # FAB 4 aba de cima
D_ABA = 76.0                          # ESTIMADO diametro externo da aba de cima (chave dos M3 do pe passa por fora)
PAREDE = fab.E_GROSSA                 # FAB 4 parede da garganta
Z_FUNDO = P.Z1                        # 15: fundo da garganta = topo da placa do carro
Z_FEIXE = Z_TOPO - 15.0               # CENA feixe IR 15 mm abaixo da face
D_LED = 5.0 + fab.ENCAIXE_JUSTO       # CATALOGO LED Ø5
BUCHA = (10.0, 6.0)                   # ESTIMADO diametro, comprimento da bucha do LED
R_BORDA = fab.R_EXTERNO               # FAB 1,5: borda do furo (decisao: R3 aumentaria a abertura efetiva)

PE = (-33.0, 33.0, -33.0, -6.0)       # ESTIMADO pe sobre a placa (x0, x1, y0, y1)
E_PE = fab.E_MEDIA + 2.0              # 5,2 ESTIMADO
COSTELA_X = 20.0                      # ESTIMADO plano das costelas (longe dos M3 do pe em x=+-27)
ANG_CONE = 50.0                       # FAB cone sob a aba (>45 graus: imprime sem suporte)
E_COSTELA = fab.E_GROSSA              # FAB 4
CIMA_IMPRESSAO = (0, 0, 1)


def local(eixo="B"):
    r_in = D_BOCA / 2
    r_out = r_in + PAREDE
    zf, zt = Z_FUNDO, Z_TOPO
    gar = cilindro(2 * r_out, zt - zf, (0, Y_C, zf), (0, 0, 1))
    aba = cilindro(D_ABA, E_TOPO, (0, Y_C, zt - E_TOPO), (0, 0, 1))
    h_cone = (D_ABA / 2 - r_out) * math.tan(math.radians(ANG_CONE))
    cone = cq.Solid.makeCone(r_out, D_ABA / 2, h_cone, cq.Vector(0, Y_C, zt - E_TOPO - h_cone), cq.Vector(0, 0, 1))
    aba = aba.union(cq.Workplane("XY").add(cone))
    pe = caixa(PE[0], PE[1], PE[2], PE[3], zf, zf + E_PE).edges("|Z").fillet(fab.R_VISIVEL)
    corpo = gar.union(aba).union(pe)
    # costelas: do pe ate a aba, abracando a garganta
    for s in (-1, 1):
        x0 = s * COSTELA_X - E_COSTELA / 2
        c = (cq.Workplane("YZ", origin=(x0, 0, 0))
             .polyline([(PE[3], zf + 0.1), (PE[3], zf + E_PE), (Y_C, zt - 0.1), (Y_C, zf + 0.1)]).close()
             .extrude(E_COSTELA))
        corpo = corpo.union(c)
    # parede de tras ligando garganta e pe, na largura do pe
    corpo = corpo.union(caixa(-COSTELA_X, COSTELA_X, Y_C, PE[3] - 8, zf, zf + E_PE))
    # postes do LED / fototransistor (feixe ao longo de x): sobem do fundo, sem overhang
    for s in (-1, 1):
        xa, xb = sorted((s * (r_in + 0.5), s * (r_out + BUCHA[1])))
        corpo = corpo.union(caixa(xa, xb, Y_C - BUCHA[0] / 2, Y_C + BUCHA[0] / 2, zf, Z_FEIXE + BUCHA[0] / 2)
                            .edges("|Z").fillet(fab.R_EXTERNO))
    # furo da boca com borda redonda
    corpo = corpo.cut(cilindro(D_BOCA, zt - zf + 2, (0, Y_C, zf - 1), (0, 0, 1)))
    try:
        corpo = corpo.faces(">Z").edges(cq.selectors.RadiusNthSelector(0)).fillet(R_BORDA)
    except Exception:
        pass
    try:
        corpo = corpo.faces(">Z").edges(cq.selectors.RadiusNthSelector(1)).fillet(fab.R_VISIVEL)
    except Exception:
        pass
    for s in (-1, 1):
        corpo = corpo.cut(teardrop(D_LED, BUCHA[1] + PAREDE + 4, (s * (r_in - 1), Y_C, Z_FEIXE), (s, 0, 0), CIMA_IMPRESSAO))
    try:
        corpo = corpo.faces("<Z").edges().chamfer(fab.CHANFRO_BASE)
    except Exception:
        pass
    # 4x M3 de fixacao na placa do carro (cabeca por cima do pe)
    for c in P.CARGA_FUROS:
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"], E_PE + 2, (*c, zf - 1), (0, 0, 1)))
    return corpo


def build(p=None, eixo="B"):
    return E.para_maquina(local(eixo), eixo)


def impressao(eixo="B"):
    sh = local(eixo).val()
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="B"):
    return [dict(nome="carro", tipo="DIN912", bitola="M3", comp=12, ponto=(*c, Z_FUNDO + E_PE), dir=(0, 0, -1),
                 extra="nas porcas embutidas da placa do carro A05") for c in P.CARGA_FUROS]


def pares_furos(var):
    return [(f"carro {k + 1}", (E.ponto_para_maquina((*c, Z_FUNDO + E_PE), var), E.dir_para_maquina((0, 0, -1), var)),
             (E.ponto_para_maquina((*c, P.Z1), var), E.dir_para_maquina((0, 0, -1), var))) for k, c in enumerate(P.CARGA_FUROS)]


def checa_bola(var="B"):
    """Queda reta pelo centro (Ø bola + folga) e bola rolando na bandeja por baixo da garganta."""
    from common import hardware as hw
    from common.checks import c7_interferencia
    rb = L.BOLA_R + fab.FOLGA_BOLA_RADIAL
    z0, z1 = L.Z_BOLA_SOLTURA, L.Z_BOCA - 120.0
    queda = cilindro(2 * rb, z0 - z1, (0, Y_C, z1), (0, 0, 1))
    r = c7_interferencia(build(None, var), {"queda": queda})
    # bandeja (pior ponto: carro em x=-140, eva de 3 mm): topo da bola rolando
    eva = 3.0                                        # usuario: forro de EVA 3 mm
    zb = 1150 - math.tan(math.radians(4.5)) * (-140 + 199) - math.tan(math.radians(3)) * (Y_C + 169.5) + eva   # CENA bandeja
    topo_bola = zb + L.BOLA_D
    fundo = L.Z_EIXO_B + Z_FUNDO
    folga = fundo - topo_bola
    return dict(ok=r["ok"] and folga >= 3.0, queda_livre=r["ok"], folga_radial_queda=round(D_BOCA / 2 - L.BOLA_R, 1),
                folga_bola_rolando_mm=round(folga, 1), nota="bandeja da cena antiga (A12-A14 ainda nao refeitas)")


FICHA = dict(orientacao="em pe, no fundo plano", suporte="nao", perimetros=4,
             infill="40% gyroid (estrutural)", camada=0.20,
             montagem="LED IR333C e TIL78 nas buchas (cola quente, fios para a esteira); boca no carro B, 4x M3x12.")
