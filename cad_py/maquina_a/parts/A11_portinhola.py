"""A11 — Portinholas do alcapao (par: frente 'f' e tras 't'), carro A.

Intencao:
- Funcao: formam o V que segura a bola; abrem juntas (setores de engrenagem engrenados) e a bola cai reta.
- Cargas: peso da bola (0,6 N) e o golpe do solenoide; giram 60 graus num M3 (eixo).
- Interfaces: berco A10 (M3x55 como eixo, furo 3,4 = giro livre), setor de engrenagem da outra portinhola,
  alavanca (so na de tras) com pino M3x25 que entra no garfo A36 do solenoide.
Impressao: em pe sobre a face do setor de engrenagem (x=23,5); placa e no sobem na vertical, sem suporte.
"""
import math

import cadquery as cq

from common import fab
from common.engrenagem import setor
from common.features import cilindro, bolsao_porca
from maquina_a import soltura as S

ID = "A11"
NOME = "portinhola"
TITULO = "Portinhola do alcapao (frente / tras)"
QTD = {"t": 1, "f": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
MOVEL = True
COORD_MAQUINA = True
EIXO = "A"
CONTATO_ESPERADO = ("A11",)
PAREDE_MINIMA = 1.0                   # FAB excecao: ponta dos dentes da engrenagem m1,5 (~1 mm); placa 3 mm, no 1,8
VISTA = (-1.0, -1.4, 0.8)


def _placa(lado):
    """Portinhola fechada, sem o setor, em coordenadas da maquina."""
    s = 1 if lado == "t" else -1
    yo0, yo1 = S.Y_OFF_BORDA, S.R_PRIM
    a = math.radians(S.ANG_CONTATO)
    n = (math.sin(a), -math.cos(a))          # normal para baixo da superficie (em y_off, z)
    e = S.E_PORT
    pts_off = [(yo0, S.z_superficie(yo0)), (yo1, S.z_superficie(yo1)),
               (yo1 + n[0] * e, S.z_superficie(yo1) + n[1] * e), (yo0 + n[0] * e, S.z_superficie(yo0) + n[1] * e)]
    pts = [(S.Y_C + s * y, z) for y, z in pts_off]
    if s < 0:
        pts = list(reversed(pts))
    x0, x1 = S.X_PORT[0], S.X_ENGR[1]
    pl = cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts).close().extrude(x1 - x0)
    try:
        pl = pl.edges("|X").fillet(fab.R_DETALHE)
    except Exception:
        pass
    no = cilindro(S.D_NO, x1 - x0, (x0, S.Y_EIXO[lado], S.Z_EIXO), (1, 0, 0))
    return pl.union(no)


def local(lado="t", angulo=0.0):
    yh = S.Y_EIXO[lado]
    plano = cq.Plane(origin=(S.X_ENGR[0], yh, S.Z_EIXO), xDir=(0, 1, 0), normal=(1, 0, 0))
    if lado == "t":
        g = setor(S.MODULO, S.DENTES, S.X_ENGR[1] - S.X_ENGR[0], plano, 110, 200, S.D_NO / 2 + 1, fase_graus=180.0)
    else:
        g = setor(S.MODULO, S.DENTES, S.X_ENGR[1] - S.X_ENGR[0], plano, -20, 70, S.D_NO / 2 + 1,
                  fase_graus=360.0 / S.DENTES / 2)
    p = _placa(lado).union(g)
    if lado == "t":
        # alavanca do solenoide no plano da engrenagem, com bolsao para a porca do pino
        yp, zp = S.Y_PINO, S.Z_PINO_FECHADO
        dy, dz = yp - yh, zp - S.Z_EIXO
        braco = (cq.Workplane(plano).center(dy / 2, dz / 2)
                 .slot2D(math.hypot(dy, dz) + 10.0, 10.0, math.degrees(math.atan2(dz, dy)))
                 .extrude(S.X_ENGR[1] - S.X_ENGR[0]))
        p = p.union(braco)
        p = p.cut(cilindro(fab.FURO_PASSANTE["M3"], 10, (S.X_ENGR[0] - 1, yp, zp), (1, 0, 0)))
        p = p.cut(bolsao_porca("M3", (S.X_ENGR[1], yp, zp), (-1, 0, 0), angulo=30.0, extra_saida=0.5))
    p = p.cut(cilindro(fab.FURO_PASSANTE["M3"], 80, (S.X_PORT[0] - 10, yh, S.Z_EIXO), (1, 0, 0)))
    if angulo:
        sh = p.val().rotate((0, yh, S.Z_EIXO), (1, yh, S.Z_EIXO), S.SENTIDO_ABRE[lado] * angulo)
        p = cq.Workplane("XY").add(sh)
    return p


def build(p=None, var="t"):
    return local(var)


def impressao(var="t"):
    sh = local(var).val().rotate((0, 0, 0), (0, 1, 0), 90)      # +x (face do setor) para baixo
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="t"):
    if var != "t":
        return []
    return [dict(nome="pino da alavanca", tipo="DIN912", bitola="M3", comp=25, ponto=(S.X_ENGR[0], S.Y_PINO, S.Z_PINO_FECHADO),
                 dir=(1, 0, 0), chave=10, extra="porca M3 no bolsao da alavanca; a ponta e o pino do garfo A36")]


FICHA = dict(orientacao="em pe sobre a face do setor de engrenagem", suporte="nao", perimetros=4, infill="40% gyroid",
             camada=0.16, montagem="engrenar as duas com as bordas internas juntas (fechado); M3x55 em cada eixo pelo berco.")
