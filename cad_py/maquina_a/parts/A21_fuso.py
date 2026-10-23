"""A21 — Fuso do elevador (3 segmentos empilhados na barra M8).

Intencao:
- Funcao: gira no sentido horario (visto de cima); o filete (helice a direita, passo 70) levanta a bola segura pelo
  trilho-guia. Topo do filete cai 10 graus para fora (a bola fica contra a parede); por baixo, 52 graus (imprime sem
  suporte). Nucleo Ø14 com furo Ø8,4 para a barra M8.
- Interfaces: barra M8 (o pacote e apertado entre porca + arruela embaixo, no rebaixo do piso da A20, e porca +
  arruela em cima), 2 pinos Ø3x16 por junta (alinham a helice), A20 (base plana 0,5 acima do topo do piso).
Impressao: em pe, face da junta de baixo na mesa.
"""
import cadquery as cq

from common import fab
from maquina_a import elevador as E

ID = "A21"
NOME = "fuso"
TITULO = "Fuso do elevador (segmento)"
QTD = {"1": 1, "2": 1, "3": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["B"]
CONTATO_ESPERADO = ("elev_barra_m8", "A21")
VISTA = (-1.0, -1.3, 0.6)
PAREDE_MINIMA = 1.0                    # nas juntas o filete termina em cunha (continua no segmento vizinho)
OVERHANG_TOLERADO = (60.0, "triangulos da malha da BSPLINE varrida perto dos cortes; normal exata da parte de baixo: "
                     "nz = r / sqrt(r^2 (1 + K^2) + (passo/2pi)^2) <= 0,60 (< 0,707 = 45 graus) em todo o filete")
JUSTIFICATIVA = "cunha do filete nas juntas: a helice corta o plano da junta; o segmento vizinho completa o filete"


def build(p=None, var="1"):
    return E.fuso_maquina(int(var) - 1, 0.0)


def impressao(var="1"):
    sh = E.segmento_fuso(int(var) - 1).val()
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="1"):
    return []


def checa_bola(var="1"):
    """Bola subindo no trilho dentro deste segmento: fuso girado para o filete ficar embaixo dela, contra tubo,
    trilho, base, saida e os 3 segmentos (folga de 0,5 no apoio)."""
    import numpy as np
    from common.checks import c7_interferencia
    from maquina_a import montagem as MT
    k = int(var) - 1
    z0, z1 = E.JUNTAS[k], E.JUNTAS[k + 1]
    zc0 = E.z_piso(E.R_BOLA) + E.R_B + 0.5 if k == 0 else z0 + E.R_B
    zs = list(np.arange(zc0, min(z1, E.Z_TRILHO[1]) + E.R_B, 12.0))
    fixos = {kk: v for kk, v in E.hardware().items() if kk in ("elev_acrilico", "elev_trilho", "elev_barra_m8")}
    for pid in ("A20", "A22", "A25"):
        if pid in MT.PECAS:
            fixos[pid] = MT.modulo(pid).build(None, "-")
    col = {}
    for zc in zs:
        g = E.giro_para_bola(zc)
        corpos = dict(fixos)
        corpos.update({f"A21.{j + 1}": E.fuso_maquina(j, g) for j in range(3)})
        b = cq.Workplane("XY").sphere(E.R_B - 0.5).translate(E.p(E.R_BOLA, E.ANG_BOLA, zc))
        r = c7_interferencia(b, corpos)
        if not r["ok"]:
            col[f"{zc:.0f}"] = r["colisoes"]
    return dict(ok=not col, colisoes=col, alturas=[round(z, 1) for z in zs],
                nota="bola parada no trilho (255 graus), fuso girado ate o filete apoiar a bola; folga radial de 2 mm para o nucleo")


FICHA = dict(orientacao="em pe, junta de baixo na mesa", suporte="nao", perimetros=4, infill="20% gyroid", camada=0.20,
             montagem=("na bancada: porca + arruela na barra M8 (altura do rebaixo da A20); enfiar os segmentos 1, 2 e 3 "
                       "com 2 pinos Ø3x16 em cada junta (a helice continua); arruela + porca em cima, apertar. Descer o "
                       "conjunto pelo topo do tubo ate o rolamento de baixo."))
