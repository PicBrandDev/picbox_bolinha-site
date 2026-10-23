"""A15 — Saida do magazine: encaixe do tubo Ø50 + reta + curva de 90 graus (fixa na lateral esquerda).

Intencao:
- Funcao: recebe a ponta esquerda do tubo acrilico e vira a fila de bolas de -x para -y (para a frente).
- Cargas: peso das bolas na fila (~0,6 kg); fixada na lateral esquerda (2x M4 + porca-garra).
- Interfaces: tubo Ø50x44 (encaixe deslizante, 15 mm), calha de carga A16 em y=40 (2 pinos Ø4 + o V continuo),
  lateral esquerda x=-207 (a parede e a guarda de fora da curva).
- Bola: V de 120 graus, centro da bola continuo com o fundo do tubo; desce 3 graus.
Impressao: em pe, numa sola plana (z da maquina para cima): V abertos para cima, guardas na vertical, um "pe"
varrido junto com o canal apoia os fundos; furos do tubo em gota com telhado a 45 graus.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro, teardrop
from maquina_a import layout as L
from maquina_a import magazine as M

ID = "A15"
NOME = "saida_magazine"
TITULO = "Saida do magazine (encaixe do tubo + curva)"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("tubo", "A16")
VISTA = (1.0, -1.2, 0.9)

ENCAIXE = 15.0                         # ESTIMADO comprimento do tubo dentro da peca
E_ENC = fab.E_MEDIA                    # 3,2 parede do encaixe
PINO = (4.0, 8.0)                      # FAB pino Ø4, profundidade em cada peca
PINOS_U = (-12.0, 8.0)                 # ESTIMADO posicao lateral dos pinos (u, no plano da junta)
Z_PINO = -M.H_VERTICE - M.E_CALHA - 4.0    # abaixo do fundo do V (bloco da junta)
X_PAREDE = M.X_PAREDE
CIMA_IMPRESSAO = (1.0, 0.0, 0.0)


def eixo_tubo(x):
    return (x, M.Y_MAG, M.z_tubo(x) + M.QUEDA_TUBO)


Z_SOLA = M.Z_CURVA0 - 40.0             # ESTIMADO sola plana (fundo da placa da parede)


def _pe_perfil(u0, u1):
    """Retangulo sob o canal (u0..u1), do fundo do V ate bem abaixo da sola (cortado depois em z=Z_SOLA)."""
    vb = -M.H_VERTICE - M.E_CALHA + 0.3
    return [(u0, vb), (u1, vb), (u1, vb - 80.0), (u0, vb - 80.0)]


def _encaixe():
    x0 = M.X_TUBO[0]
    a = cq.Vector(*eixo_tubo(x0 - 3.0))
    b = cq.Vector(*eixo_tubo(x0 + ENCAIXE))
    n = (b - a).normalized()
    L = (b - a).Length
    r = M.TUBO_D / 2 + E_ENC
    ext = cilindro(2 * r, L, a.toTuple(), n.toTuple())
    ext = ext.union(caixa(a.x, b.x, M.Y_MAG - r, M.Y_MAG + r, Z_SOLA, max(a.z, b.z)))
    h_tel = (M.TUBO_D / 2 + fab.ENCAIXE_DESLIZANTE) * math.sqrt(2) + 2.4 * math.sqrt(2)   # 2,4 de parede normal a 45 graus
    tel = (cq.Workplane(cq.Plane(origin=a.toTuple(), xDir=(0, 1, 0), normal=n.toTuple()))
           .polyline([(-h_tel, 0), (0, h_tel), (h_tel, 0)]).close().extrude(L))
    ext = ext.union(tel.intersect(caixa(a.x - 5, b.x + 5, M.Y_MAG - r, M.Y_MAG + r, Z_SOLA, 3000)))
    return ext.intersect(caixa(a.x, b.x, -300, 300, Z_SOLA, 3000))      # pontas retas (o tubo e inclinado)


def _furos_tubo():
    """Encaixe do tubo e passagem Ø44 ate o canal, em gota com a ponta para cima."""
    x0 = M.X_TUBO[0]
    n = (cq.Vector(*eixo_tubo(x0 + 1)) - cq.Vector(*eixo_tubo(x0))).normalized()
    furo = teardrop(M.TUBO_D + 2 * fab.ENCAIXE_DESLIZANTE, ENCAIXE + 1, eixo_tubo(x0), n.toTuple(), (0, 0, 1))
    pas = teardrop(M.TUBO_DI, 10.0, (cq.Vector(*eixo_tubo(x0 - 8.0))).toTuple(), n.toTuple(), (0, 0, 1))
    return furo.union(pas)


def _junta():
    """Bloco sob o V no fim da curva (y=40) com os furos dos pinos."""
    z = M.Z_CURVA1
    return caixa(M.X_TRAV - 18.0, M.X_TRAV + 14.0, M.Y_CURVA1, M.Y_CURVA1 + 10.0, Z_SOLA, z - M.H_VERTICE - M.E_CALHA + 0.5)


FUROS_Y = (M.Y_CURVA1 + 16.0, M.Y_MAG + 18.0)
Z_FURO = Z_SOLA + 6.0               # ESTIMADO 2 mm de chao sob o canal da chave; ponta da gota abaixo do fundo do V


def local(var="-"):
    p_reta = ((M.X_TUBO[0] + 1.0, M.Y_MAG, M.z_tubo(M.X_TUBO[0] + 1.0)),
              (M.X_CURVA0 - 2.0, M.Y_MAG, M.Z_CURVA0 - 2.0 * math.tan(M.INCL)))
    reta = M.canal_reto(*p_reta, pos="v")
    pe_reta = M.canal_reto(*p_reta, perfil=_pe_perfil(-(M.GUARDA_IN + M.E_CALHA), M.V_ABERTO))
    curva = M.canal_curva()
    pe_curva = M.canal_curva(perfil=_pe_perfil(-M.V_ABERTO, M.GUARDA_IN + M.E_CALHA))
    pe = pe_reta.union(pe_curva, tol=1e-3).intersect(caixa(X_PAREDE, 0, -300, 300, Z_SOLA, 3000))
    # uniao com tolerancia: as guardas da reta e da curva se encontram quase coincidentes na emenda
    p = _encaixe().union(reta, tol=1e-3).union(curva, tol=1e-3).union(pe, tol=1e-3).union(_junta(), tol=1e-3)
    # placa na parede (embaixo do canal: a bola passa a 1,5 mm da guarda)
    zc = M.Z_CURVA0
    placa = caixa(X_PAREDE, X_PAREDE + fab.E_GROSSA, M.Y_CURVA1 + 2.0, M.Y_MAG + 26.0, Z_SOLA,
                  M.Z_CURVA1 - M.H_VERTICE - M.E_CALHA)
    p = p.union(placa, tol=1e-3)
    p = p.cut(_furos_tubo())
    for y in FUROS_Y:
        p = p.cut(cilindro(fab.FURO_PASSANTE["M4"], 20, (X_PAREDE - 1, y, Z_FURO), (1, 0, 0)))
        # canal para a cabeca e a chave atravessarem o pe ate a placa (gota: horizontal na impressao)
        p = p.cut(teardrop(8.0, 80.0, (X_PAREDE + fab.E_GROSSA, y, Z_FURO), (1, 0, 0), (0, 0, 1)))
    # a lateral do gabinete e a guarda de fora: nada passa de x=-207
    p = p.intersect(caixa(X_PAREDE, 0, -300, 300, Z_SOLA, 3000))
    # pinos da junta com a A16 (furos na face y=40)
    for u in PINOS_U:
        p = p.cut(cilindro(PINO[0] + 2 * fab.ENCAIXE_JUSTO, PINO[1], (M.X_TRAV + u, M.Y_CURVA1 - 0.01, M.Z_CURVA1 + Z_PINO), (0, 1, 0)))
    try:
        p = p.faces("<Z").edges().chamfer(fab.CHANFRO_BASE)
    except Exception:
        pass
    return p


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val()                                      # em pe, na sola
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    return [dict(nome="parede", tipo="DIN912", bitola="M4", comp=25, ponto=(X_PAREDE + fab.E_GROSSA, y, Z_FURO), dir=(-1, 0, 0),
                 chave=40, extra="porca-garra M4 cravada por fora da lateral esquerda; chave pelo canal do pe") for y in FUROS_Y]


FICHA = dict(orientacao="em pe, na sola plana", suporte="nao", perimetros=4, infill="20% gyroid", camada=0.20,
             montagem="2 pinos Ø4 na junta; encaixar na A16; parafusar na lateral esquerda (2x M4x25); encaixar o tubo.")
