"""A27 — Cabeca do elevador: trecho de cima do tubo, impresso, com a guia de transferencia e a janela de saida.

Intencao:
- Funcao: continua o tubo acrilico (mesmo Ø100 x 94) de z=1467 ate 1640. Por dentro tem uma guia helicoidal (perfil
  igual ao trilho Ø8) que comeca em cima da ponta do trilho de aluminio (250 graus) e gira 130 graus no sentido
  horario enquanto sobe 110 mm: a bola, empurrada contra ela pelo filete, sobe e vem do canto (280 graus) para o
  lado do campo (150 graus). Dali um trilho vertical impresso (120 graus) segura a bola ate 11 mm antes da saida;
  na janela (126..175 graus) a borda do piso da A25 segura a bola ate a beira do filete passar dela, e entao a bola
  rola para fora pelo caimento do filete (o trilho ja ficou para baixo, entao nao a empurra para dentro).
- Interfaces: acrilico (colar por fora, 15 mm, e flange no topo do acrilico), ponta do trilho de aluminio (encaixe
  de 3 mm na flange), tampa A22 (apoiada no topo), saida A25 (apoiada no fundo da janela, z=1582).
Impressao: em pe, colar na mesa (use brim); guia a 44 graus (sem suporte); a flange tem 3,3 mm de balanco em volta do colar.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import elevador as E

ID = "A27"
NOME = "cabeca_elevador"
TITULO = "Cabeca do elevador (guia de transferencia + janela)"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("elev_acrilico", "elev_trilho", "A22", "A25")
VISTA = (-1.0, 0.8, 0.6)
PONTE_TOLERADA = (110.0, "face de baixo da flange: anel de 3,3 mm em balanco em volta do colar (a medida de ponte usa o "
                         "diametro do anel, 100 mm); de cabeca para baixo a borda da janela viraria ponte real de 41 mm")

R0, R1 = E.R_TI, E.TUBO_D / 2           # parede 47..50 (igual ao acrilico)
R_COLAR = (R1 + E.FOLGA_TUBO, R1 + E.FOLGA_TUBO + 3.0)
H_COLAR = 15.0
Z_FLANGE = (E.Z_CABECA0, E.Z_CABECA0 + 3.0)
SEM_COLAR = ((-35.0, 35.0), (235.0, 305.0))   # junto das paredes da maquina (2 mm) fica so a parede
LARG_COSTAS = 6.0                      # FAB costas da guia (liga o perfil Ø8 na parede)


def _perfil(ang, z):
    """Perfil horizontal da guia (Ø8 em r=42,5 + costas ate a parede) no angulo 'ang', na altura z (eixo do tubo em 0,0)."""
    a = math.radians(ang)
    t = (-math.sin(a), math.cos(a))
    rc = E.R_TRILHO
    w = cq.Workplane("XY", origin=(0, 0, z)).moveTo(rc * math.cos(a), rc * math.sin(a)).circle(E.D_TRILHO / 2)   # torce em volta do eixo do tubo
    pts = []
    for r, s in ((rc, -1), (R0 + 0.3, -1), (R0 + 0.3, 1), (rc, 1)):
        pts.append((r * math.cos(a) + s * t[0] * LARG_COSTAS / 2, r * math.sin(a) + s * t[1] * LARG_COSTAS / 2))
    costas = cq.Workplane("XY", origin=(0, 0, z)).polyline(pts).close()
    return w, costas


def _guia():
    z0, z1 = E.Z_TRANSF
    giro = E.ANG_TRILHO_TOPO - E.ANG_TRILHO           # -130: horario subindo
    out = None
    for pf in _perfil(E.ANG_TRILHO, z0):
        s = pf.twistExtrude(z1 - z0, giro)
        out = s if out is None else out.union(s)
    for pf in _perfil(E.ANG_TRILHO_TOPO, z1):           # trilho vertical de cima
        out = out.union(pf.extrude(E.Z_TRILHO_TOPO1 - z1))
    return out


def local(var="-"):
    x, y = E.C
    parede = cilindro(2 * R1, E.Z_TUBO1 - E.Z_CABECA0, (0, 0, E.Z_CABECA0), (0, 0, 1)).cut(
        cilindro(2 * R0, E.Z_TUBO1 - E.Z_CABECA0 + 2, (0, 0, E.Z_CABECA0 - 1), (0, 0, 1)))
    colar = cilindro(2 * R_COLAR[1], H_COLAR + 3.0, (0, 0, E.Z_CABECA0 - H_COLAR), (0, 0, 1)).cut(
        cilindro(2 * R_COLAR[0], H_COLAR + 1.0, (0, 0, E.Z_CABECA0 - H_COLAR - 1), (0, 0, 1))).cut(
        cilindro(2 * R0, H_COLAR + 10.0, (0, 0, E.Z_CABECA0 - H_COLAR - 5), (0, 0, 1)))
    flange = cilindro(2 * R_COLAR[1], Z_FLANGE[1] - Z_FLANGE[0], (0, 0, Z_FLANGE[0]), (0, 0, 1)).cut(
        cilindro(2 * R0, 10, (0, 0, Z_FLANGE[0] - 1), (0, 0, 1)))
    # apoio da ponta do trilho de aluminio (setor do trilho, na altura da flange)
    a = E.ANG_TRILHO
    sap = math.degrees(LARG_COSTAS / 2 / E.R_TRILHO)      # meia luva: so atras do centro do trilho (nao entra no lado da bola)
    pad = cq.Workplane("XY").add(E.setor(E.R_TRILHO, R0 + 0.5, a - sap, a + sap, Z_FLANGE[0], Z_FLANGE[1]).val()
                                 .translate((-x, -y, 0)))
    corpo = parede.union(colar).union(flange).union(pad).union(_guia())
    corpo = cq.Workplane("XY").add(corpo.val().translate((x, y, 0)))
    for a0, a1 in SEM_COLAR:
        corpo = corpo.cut(E.setor(R1 + 0.01, 70.0, a0, a1, E.Z_CABECA0 - H_COLAR - 1, Z_FLANGE[1] + 0.01))
    corpo = corpo.cut(E.setor(R0 - 1.0, R1 + 1.0, *E.ARCO_ENTALHE, E.Z_ENTALHE0, E.Z_TUBO1 + 1))   # janela de saida
    # encaixe da ponta do trilho (3 mm) e chanfro de entrada da bola na emenda com o acrilico
    corpo = corpo.cut(cilindro(E.D_TRILHO + 0.3, 4.0, E.p(E.R_TRILHO, a, Z_FLANGE[0] - 1.0), (0, 0, 1)))
    corpo = corpo.intersect(caixa(-500, 206.0, -206.0, 500, 0, 3000))
    return corpo


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val()                                  # em pe: colar na mesa
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    return []


def caminho():
    """Centros da bola subindo no trilho de baixo, na guia de transferencia e no trilho de cima, ate a saida."""
    import numpy as np
    zs = list(np.arange(E.Z_TRANSF[0] - 30.0, E.ZC_SAI + 0.1, 4.0))
    return [(E.p(E.R_BOLA, E.ang_bola(z), z), E.giro_para_bola(z)) for z in zs]


def checa_bola(var="-"):
    """Bola na transferencia e no trilho de cima (fuso girado para apoiar a bola) contra a cabeca, a tampa, a saida,
    o acrilico, o trilho de aluminio e os 3 segmentos do fuso (0,5 mm de contato permitido)."""
    from common.checks import c7_interferencia
    from maquina_a import montagem as MT
    fixos = {k: v for k, v in E.hardware().items() if k in ("elev_acrilico", "elev_trilho", "elev_barra_m8")}
    fixos["A27"] = build()
    for pid in ("A22", "A25"):
        if pid in MT.PECAS:
            fixos[pid] = MT.modulo(pid).build(None, "-")
    col = {}
    pts = caminho()
    for c, g in pts:
        corpos = dict(fixos)
        corpos.update({f"A21.{j + 1}": E.fuso_maquina(j, g) for j in range(3)})
        r = c7_interferencia(cq.Workplane("XY").sphere(E.R_B - 0.5).translate(c), corpos)
        if not r["ok"]:
            col[f"({c[0]:.0f},{c[1]:.0f},{c[2]:.0f})"] = r["colisoes"]
    return dict(ok=not col, colisoes=col, pontos=len(pts),
                nota="bola encostada no trilho/guia: 280 graus ate z=1470, gira para 150 ate 1580, sobe a 150 ate sair")


FICHA = dict(orientacao="em pe, colar na mesa (brim de 8 mm)", suporte="nao", perimetros=4, infill="20% gyroid", camada=0.20,
             montagem=("na bancada: trilho de aluminio aparafusado no acrilico (ponta 3 mm acima do topo do acrilico); encaixar "
                       "a cabeca por cima (colar por fora, ponta do trilho no encaixe da flange); o fuso entra por cima."))
