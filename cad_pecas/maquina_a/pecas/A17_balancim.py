"""A17 — Balancim do escapamento (servo SG90).

Intencao:
- Funcao: dois dedos sobem alternadamente pelo vertice da travessia: -15 graus segura a fila (dedo de baixo em
  cima), +15 graus solta UMA bola (o dedo de cima sobe entre a 1a e a 2a bola e segura a fila).
- Interfaces: braco do SG90 (encaixe + parafuso do braco + 2 M2 autoatarraxantes), rasgos da calha A16.
Impressao: deitado na face do cubo (x), dedos na horizontal.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import magazine as M

ID = "A17"
NOME = "balancim"
TITULO = "Balancim do escapamento"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("sg90",)
PAREDE_MINIMA = 1.5                   # FAB rebaixo do braco do servo (1,8 de fundo)

X_BRACO = (M.X_EIXO_SERVO, M.X_EIXO_SERVO + 3.7)     # placa dos bracos, encostada no braco do servo
CUBO = (12.0, 5.0)                    # ESTIMADO diametro, espessura do cubo
BRACO_SERVO = (7.4, 5.4, 17.0, 1.8)   # ESTIMADO cubo Ø, largura, comprimento e espessura do braco do SG90 (rebaixo)
DESCE_BRACO = 2.0                     # FAB braco e ligacoes dos dedos 2 mm abaixo do eixo (folga >= 1,5 do fundo da A16 a +-15)


def _rot(obj, ang):
    sh = obj.val() if isinstance(obj, cq.Workplane) else obj
    return cq.Workplane("XY").add(sh.rotate((0, M.Y_PIVO, M.Z_PIVO), (1, M.Y_PIVO, M.Z_PIVO), ang))


def dedos(angulo=0.0, folga=0.0):
    """So os dois dedos (para os rasgos da A16), girados de 'angulo' em torno do eixo do servo."""
    dx, dy = M.DEDO_SEC
    f = folga
    out = None
    for y in (M.Y_DEDO1, M.Y_DEDO2):
        d = caixa(M.X_DEDO - dx / 2 - f, M.X_DEDO + dx / 2 + f, y - dy / 2 - f, y + dy / 2 + f,
                  M.Z_PIVO - 3.0, M.Z_PIVO + M.DEDO_H + f)
        out = d if out is None else out.union(d)
    return _rot(out, angulo)


def local(var="-", angulo=0.0):
    x0, x1 = X_BRACO
    yp, zp = M.Y_PIVO, M.Z_PIVO
    zb = zp - DESCE_BRACO                 # braco abaixo do eixo: a +-15 graus as pontas nao encostam no fundo da A16
    braco = (cq.Workplane("YZ", origin=(x0, 0, 0)).center((M.Y_DEDO1 + M.Y_DEDO2) / 2, zb)
             .slot2D(M.Y_DEDO2 - M.Y_DEDO1 + 6.0, 6.0, 0).extrude(x1 - x0))
    # mais alto so no meio, onde fica o braco do servo (nas pontas nao pode subir ate o fundo da calha)
    braco = braco.union(cq.Workplane("YZ", origin=(x0, 0, 0)).center(yp, zp).slot2D(BRACO_SERVO[2] + 6.0, 9.0, 0).extrude(x1 - x0))
    cubo = cilindro(CUBO[0], CUBO[1], (x0, yp, zp), (1, 0, 0))
    b = braco.union(cubo)
    dx, dy = M.DEDO_SEC
    for y in (M.Y_DEDO1, M.Y_DEDO2):
        b = b.union(caixa(M.X_DEDO - dx / 2, x1, y - dy / 2, y + dy / 2, zb - 3.0, zb + 3.0))
    b = b.union(dedos(0.0))
    try:
        b = b.edges("|X").fillet(fab.R_DETALHE)
    except Exception:
        pass
    # rebaixo do braco do servo (face -x do cubo/braco) e furo do parafuso do braco
    dc, w, comp, e = BRACO_SERVO
    b = b.cut(cilindro(dc, e, (x0 - 0.01, yp, zp), (1, 0, 0)))
    b = b.cut(cq.Workplane("YZ", origin=(x0 - 0.01, 0, 0)).center(yp, zp).slot2D(comp, w, 0).extrude(e))
    b = b.cut(cilindro(2.4, 20, (x0 - 1, yp, zp), (1, 0, 0)))
    for k in (-1, 1):
        b = b.cut(cilindro(1.6, 6, (x0 - 1, yp + k * 6.0, zp), (1, 0, 0)))
    return _rot(b, angulo) if angulo else b


def build(p=None, var="-"):
    return local(var, -M.ANG_ESCAPE)


def impressao(var="-"):
    sh = local(var).val().rotate((0, 0, 0), (0, 1, 0), 90)
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="-"):
    return []


def checa_giro(var="-"):
    """Folga do balancim girando de -17 a +17 graus (servo usa +-15) contra a A16, o SG90 e o resto em volta."""
    import numpy as np
    from common.malha import para_trimesh, para_manifold
    from maquina_a import montagem as MT
    mf = lambda w: para_manifold(para_trimesh(w, 0.03, 0.15))
    alvos = {"A16": MT.modulo("A16").build(None, "-"), "A15": MT.modulo("A15").build(None, "-")}
    if "A26" in MT.PECAS:
        alvos["A26"] = MT.modulo("A26").build(None, "-")
    A = {k: mf(v) for k, v in alvos.items()}
    piores = {}
    for ang in np.arange(-17.0, 17.01, 1.0):
        b = mf(local(var, float(ang)))
        for k, m in A.items():
            g = b.min_gap(m, 5.0)
            if k not in piores or g < piores[k][0]:
                piores[k] = (round(g, 2), float(ang))
    return dict(ok=all(g >= 0.5 for g, _ in piores.values()), folga_min=piores, exigida=0.5)


FICHA = dict(orientacao="deitado na face do cubo", suporte="nao", perimetros=4, infill="100%", camada=0.16,
             montagem="braco do SG90 no rebaixo; parafuso do braco pelo centro + 2 M2x6 autoatarraxantes; servo em 90 graus = dedos nivelados.")
