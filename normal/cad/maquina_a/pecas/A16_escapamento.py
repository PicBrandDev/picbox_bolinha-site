"""A16 — Escapamento: travessia em V com o servo que solta uma bola por vez (fixa na lateral esquerda).

Intencao:
- Funcao: leva a fila do magazine para a frente (em -y, x=-184,5, por baixo do pe do bloco do tensor A) e a segura no
  escapamento (servo SG90 + balancim A17), soltando UMA bola por vez para a entrada do berco A26.
- Cargas: peso da fila; servo. Fixa na lateral esquerda (2x M4 + porca-garra).
- Interfaces: saida A15 em y=40 e entrada A26 em y=-34 (2 pinos Ø4 em cada junta), SG90 (2 postes com furos para os
  parafusos das orelhas), lateral x=-207.
Impressao: deitada na face da parede (x=-207): V na vertical, sem suporte.
"""
import math

import cadquery as cq

from common import fab, hardware as hw
from common.features import caixa, cilindro
from maquina_a import magazine as M
from maquina_a import soltura as S
from maquina_a.pecas import A15_saida_magazine as A15
from maquina_a.pecas import A17_balancim as A17

ID = "A16"
NOME = "escapamento"
TITULO = "Escapamento (travessia + servo)"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("A15", "sg90", "A17", "A26")
VISTA = (1.2, -1.0, 0.9)

X_PAREDE = M.X_PAREDE
Z_PLACA = (M.Z_PIVO - 10.0, M.Z_PIVO + 9.0)   # placa na parede, abaixo do canal
POSTE = 6.0                            # ESTIMADO largura dos postes das orelhas do servo


def _servo():
    return hw.sg90(X_PAREDE, M.Y_PIVO, M.Z_PIVO, +1)


def local(var="-"):
    yj = M.Y_JUNTA_B
    p = M.canal_reto((M.X_TRAV, M.Y_CURVA1, M.Z_CURVA1), (M.X_TRAV, yj, M.z_trav(yj)), neg="guarda", pos="v", u_neg=M.U_PAREDE)
    # bloco da junta com a A26 (y=-34, pinos para -y)
    p = p.union(bloco_junta(yj, +1))
    # bloco da junta com a A15 (espelha o da A15, do lado de ca de y=40)
    z = M.Z_CURVA1
    p = p.union(caixa(M.X_TRAV - 18.0, M.X_TRAV + 14.0, M.Y_CURVA1 - 10.0, M.Y_CURVA1, z + A15.Z_PINO - 5.0,
                      z - M.H_VERTICE - M.E_CALHA + 0.5))
    # placa na parede, sob o canal, ligada a travessia e ao trecho final
    p = p.union(caixa(X_PAREDE, X_PAREDE + fab.E_GROSSA, yj, M.Y_CURVA1 - 2.0, Z_PLACA[0], M.z_trav(yj) - M.H_VERTICE))
    # postes das orelhas do servo
    sv = hw.SG90
    xo = X_PAREDE + sv["orelha_h"]
    for (pt, _) in hw.furos_sg90(X_PAREDE, M.Y_PIVO, M.Z_PIVO, +1):
        y = pt[1]
        p = p.union(caixa(X_PAREDE, xo, y - POSTE / 2, y + POSTE / 2, M.Z_PIVO - sv["W"] / 2, M.Z_PIVO + sv["W"] / 2 + 6.0))
        p = p.cut(cilindro(1.8, 10, (xo + 0.01, y, M.Z_PIVO), (-1, 0, 0)))
    p = p.cut(_servo())
    # a parede e a guarda de fora: nada passa de x=-207
    p = p.intersect(caixa(X_PAREDE, 0, -300, 300, 0, 3000))
    # rasgos dos dedos: varredura do dedo de -20 a +20 graus com folga
    for a in range(-17, 18, 1):
        p = p.cut(A17.dedos(a, 0.8))
    # pinos da junta (furos na face y=40)
    for u in A15.PINOS_U:
        p = p.cut(cilindro(A15.PINO[0] + 2 * fab.ENCAIXE_JUSTO, A15.PINO[1], (M.X_TRAV + u, M.Y_CURVA1 + 0.01, M.Z_CURVA1 + A15.Z_PINO),
                           (0, -1, 0)))
    p = p.cut(pinos_junta(yj))
    # 2x M4 na parede
    for y in FUROS_Y:
        p = p.cut(cilindro(fab.FURO_PASSANTE["M4"], 20, (X_PAREDE - 1, y, Z_PLACA[0] + 6.0), (1, 0, 0)))
    return p


FUROS_Y = (-27.0, 33.0)                # ESTIMADO fora do servo e dos postes (y de -15 a 26)


PINOS_U_B = (-14.0, -7.5)              # ESTIMADO pinos da junta A16/A26 do lado da parede (fora do braco do A17)


def bloco_junta(yj, lado):
    """Bloco sob o V na junta yj, do lado +y (lado=+1) ou -y (lado=-1) da junta."""
    z = M.z_trav(yj)
    y0, y1 = sorted((yj, yj + 10.0 * lado))
    return caixa(M.X_TRAV - 18.0, M.X_TRAV - 2.5, y0, y1, z + A15.Z_PINO - 5.0, z - M.H_VERTICE - M.E_CALHA + 0.5)   # so do lado da parede (o braco do A17 passa do outro lado)


def pinos_junta(yj):
    """Furos dos 2 pinos Ø4 da junta (8 mm de cada lado)."""
    out = None
    for u in PINOS_U_B:
        c = cilindro(A15.PINO[0] + 2 * fab.ENCAIXE_JUSTO, 2 * A15.PINO[1], (M.X_TRAV + u, yj - A15.PINO[1], M.z_trav(yj) + A15.Z_PINO),
                     (0, 1, 0))
        out = c if out is None else out.union(c)
    return out


def build(p=None, var="-"):
    return local(var)


def impressao(var="-"):
    sh = local(var).val().rotate((0, 0, 0), (0, 1, 0), -90)
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    f = [dict(nome="parede", tipo="DIN912", bitola="M4", comp=25, ponto=(X_PAREDE + fab.E_GROSSA, y, Z_PLACA[0] + 6.0),
              dir=(-1, 0, 0), chave=30, extra="porca-garra M4 cravada por fora da lateral esquerda") for y in FUROS_Y]
    return f


def checa_bola(var="-"):
    """Caminho inteiro do magazine ao berco (carro A na carga): bola com folga contra tudo o que nao e apoio."""
    return checa_caminho()


def checa_caminho():
    """Fase 1: fila ate o dedo de baixo (balancim +20). Fase 2: bola solta do dedo ate o berco (balancim -20)."""
    from common.checks import c7_interferencia
    from maquina_a import montagem as MT
    from maquina_a.pecas import A17_balancim as A17
    pts = M.pontos_bola(6.0)
    y_seg = M.Y_BOLA1                                           # centro da bola parada no dedo de baixo
    fila = [c for c in pts if c[1] >= y_seg]
    solta = [c for c in pts if c[1] <= y_seg]
    bola = lambda c, r: hw.bola((c[0], c[1], c[2] + 0.6), 2 * r)
    junta = lambda cs, r: cq.Workplane("XY").add([bola(c, r).val() for c in cs])
    apoios = dict(MT.corpos_magazine())
    outros = MT.corpos_contexto_caminho()
    for k in [k for k in outros if "A11" in k]:            # portinholas do berco sao apoio (a bola anda em cima delas)
        apoios[k] = outros.pop(k)
    outros.pop("A17.-", None)
    res = {}
    for nome, cs, ang in (("fila", fila, -M.ANG_ESCAPE), ("solta", solta, M.ANG_ESCAPE)):
        o = dict(outros, A17=A17.local("-", ang))
        r1 = c7_interferencia(junta(cs, M.R_B), apoios)
        r2 = c7_interferencia(junta(cs, M.R_B + fab.FOLGA_BOLA_RADIAL), o)
        res[nome] = dict(ok=r1["ok"] and r2["ok"], apoios=r1["colisoes"], maquina=r2["colisoes"], pontos=len(cs))
    return dict(ok=all(v["ok"] for v in res.values()), **res,
                nota="carro A na carga (x=-140); bola levantada 0,6 mm contra os apoios, 1,5 mm de folga contra o resto")


FICHA = dict(orientacao="deitada na face da parede", suporte="nao", perimetros=4, infill="20% gyroid", camada=0.20,
             montagem=("1) servo SG90 entre os postes, encostado na lateral, 2 parafusos das orelhas; 2) balancim A17 no braco "
                       "do servo (servo a 90 graus = dedos nivelados); 3) pinos Ø4 na junta com a A15; 4) parafusar na "
                       "lateral esquerda (2x M4x25); 5) entrada A26 encaixada nos pinos da junta de baixo."))
