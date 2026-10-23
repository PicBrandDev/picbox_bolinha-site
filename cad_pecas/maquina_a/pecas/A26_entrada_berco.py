"""A26 — Entrada do berco: curva em V de 90 graus (da travessia para o berco) e linguas que entram no berco.

Intencao:
- Funcao: recebe a bola solta pelo escapamento A16 (vindo em -y, x=-184,5) e vira 90 graus numa curva em V (R18,5,
  ~7,7 graus de descida, guarda por fora; a lateral esquerda e a guarda no comeco), sem degrau e sem batente, entrando
  no berco A10 (carro A em x=-140) em +x, no plano e na altura dele (y=-57, z=1470).
- Linguas: 2 trilhos sob os flancos do V (u=7..14, 2,6 mm) que entram 3,5 mm no furo R23 do berco: a bola passa da
  calha para a portinhola sem degrau. Ponta chanfrada (guia o berco se o carro chegar 1 mm fora).
- Interfaces: A16 em y=-34 (2 pinos Ø4), lateral esquerda x=-207 (2x M4 + porca-garra), berco A10 (so a lingua entra;
  o corpo para em x=-166, 1 mm da bochecha com o carro no limite -141).
Impressao: deitada na face da parede (x=-207), como a A16: V na vertical, sem suporte.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import magazine as M
from maquina_a import soltura as S
from maquina_a.pecas import A16_escapamento as A16

ID = "A26"
NOME = "entrada_berco"
TITULO = "Entrada do berco (curva em V + linguas)"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("A16",)
VISTA = (1.2, -1.0, 0.9)

X_PAREDE = M.X_PAREDE
LINGUA_U = (7.0, 14.0)                 # ESTIMADO faixa do flanco que entra no berco (raio <= 21,7: 1,3 do furo R23)
LINGUA_E = 2.6                         # FAB espessura da lingua sob o flanco (antes 5 x 2,5 mm; agora 7 x 2,6 mm)
CHANFRO_LINGUA = 1.5                   # FAB ponta chanfrada
FUROS_Y = (-74.0, -50.0)               # ESTIMADO 2x M4 na parede
Y_PLACA = (-80.0, M.Y_JUNTA_B)
Z_FUNDO = A16.Z_PLACA[0] + 11.0        # fundo do bloco (a chave dos M4 da placa passa por baixo)


def _lingua():
    """Dois trilhos (flancos do V perto das linhas de contato) de x=-168 ate a ponta, com a ponta chanfrada por baixo."""
    t = math.tan(math.radians(M.ANG_V))
    out = None
    x0, x1 = M.X_LINGUA - 2.0, M.X_PONTA
    for s in (-1, 1):
        u0, u1 = LINGUA_U
        pts = [(s * u0, -M.H_VERTICE + u0 * t), (s * u1, -M.H_VERTICE + u1 * t),
               (s * u1, -M.H_VERTICE + u1 * t - LINGUA_E), (s * u0, -M.H_VERTICE + u0 * t - LINGUA_E)]
        pts = [(S.Y_C + y, M.Z_FIM + z) for y, z in pts]
        if s < 0:
            pts = list(reversed(pts))
        r = cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts).close().extrude(x1 - x0)
        try:
            r = r.faces(">X").edges("not |X").chamfer(CHANFRO_LINGUA * 0.6)
        except Exception:
            pass
        out = r if out is None else out.union(r)
    return out


def local(var="-"):
    """Bloco (lateral ate x=-166, y=-80,5..-34) menos o espaco da bola: as superficies do V vem so da cavidade."""
    yj = M.Y_JUNTA_B
    z_topo = M.Z_CURVA_B0 - 2.0                             # guardas: 2 mm abaixo do centro da bola no comeco da curva
    corpo = caixa(X_PAREDE, M.X_LINGUA, M.Y_CANTO - M.GUARDA_IN - M.E_CALHA, yj, Z_FUNDO, z_topo)
    corpo = corpo.union(caixa(X_PAREDE, X_PAREDE + fab.E_GROSSA, Y_PLACA[0], Y_PLACA[1], A16.Z_PLACA[0], Z_FUNDO + 1.0))
    p = corpo
    for c in _cavidade():                                  # cortes separados (a uniao das duas varreduras falha no OCC)
        p = p.cut(c)
    p = p.union(_lingua())
    p = p.cut(A16.pinos_junta(yj))
    for y in FUROS_Y:
        p = p.cut(cilindro(fab.FURO_PASSANTE["M4"], 20, (X_PAREDE - 1, y, A16.Z_PLACA[0] + 6.0), (1, 0, 0)))
    return p


def _cavidade():
    """Espaco acima das superficies do V (reta da junta + curva), com sobra para os lados."""
    t = math.tan(math.radians(M.ANG_V))
    g, a = M.GUARDA_IN, M.V_ABERTO + 8.0
    cav = [(-g, -M.H_VERTICE + g * t), (0, -M.H_VERTICE), (a, -M.H_VERTICE + a * t), (a, 60.0), (-g, 60.0)]   # u-: guarda
    yj = M.Y_JUNTA_B
    reta = M.canal_reto((M.X_TRAV, yj + 1, M.z_trav(yj + 1)), (M.X_TRAV, M.Y_CURVA_B0, M.Z_CURVA_B0), perfil=cav)
    # na curva o lado de dentro so vai ate 1 mm do centro (R18,5): alem disso a varredura se cruza
    ai = M.R_CURVA_B - 1.0
    cav_c = [(-g, -M.H_VERTICE + g * t), (0, -M.H_VERTICE), (ai, -M.H_VERTICE + ai * t), (ai, 60.0), (-g, 60.0)]
    curva = M.canal_curva_berco(perfil=[(-u, v) for u, v in reversed(cav_c)])   # varrida contra o fluxo: u troca de lado
    cx, cy = M.C_CURVA_B
    z_c = M.Z_FIM - M.H_VERTICE + ai * t                    # o centro da curva fica livre acima do flanco de dentro
    centro = cilindro(8.0, 100.0, (cx, cy, z_c), (0, 0, 1))
    return [reta, curva, centro]


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val().rotate((0, 0, 0), (0, 1, 0), -90)
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    return [dict(nome="parede", tipo="DIN912", bitola="M4", comp=25, ponto=(X_PAREDE + fab.E_GROSSA, y, A16.Z_PLACA[0] + 6.0),
                 dir=(-1, 0, 0), chave=30, extra="porca-garra M4 cravada por fora da lateral esquerda") for y in FUROS_Y]


def checa_bola(var="-"):
    """Mesmo caminho da A16 (magazine ate o berco, nas duas fases do escapamento)."""
    return A16.checa_caminho()


FICHA = dict(orientacao="deitada na face da parede", suporte="nao", perimetros=4, infill="20% gyroid", camada=0.20,
             montagem=("1) pinos Ø4 na junta com a A16; 2) encostar na lateral esquerda e parafusar (2x M4x25); 3) com o carro A "
                       "parado na carga (x=-140), conferir que as linguas entram no furo do berco sem encostar."))
