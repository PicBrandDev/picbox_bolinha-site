"""A23 — Calha do elevador ate o funil do magazine.

Intencao:
- Funcao: leva a bola da saida A25 (y=-90) ao longo de +y em x=100, descendo 3 graus por cima do eixo A, e solta
  a bola por um furo Ø42 sobre o funil da entrada A18 (a 12,6 mm do eixo do funil).
- Interfaces: A25 (orelhas por baixo dela, 2x M3), borda do funil da A18 (o fundo plano da calha apoia nela).
- Bola: canal em V de 120 graus (igual ao magazine), guardas a 1,5 mm da bola.
Impressao: em pe, fundo plano (z=1568) na mesa.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import elevador as E
from maquina_a import magazine as M

ID = "A23"
NOME = "calha_elevador"
TITULO = "Calha do elevador ate o magazine"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("A18", "A25")
VISTA = (1.0, -1.3, 0.9)

Z0 = M.Z_FUNIL_TOPO                    # 1568: fundo plano apoiado na borda do funil
Y_FIM = E.Y_RAIA1 + E.R_B + 1.5        # fim do canal (parede do fim a 1,5 da bola sobre o furo)
X_G = (E.X_RAIA - E.GUARDA[1], E.X_RAIA + E.GUARDA[1])
D_QUEDA = 2 * E.R_B + 4.0              # FAB furo de queda


def local(var="-"):
    y0, y1 = E.Y_RAIA0, Y_FIM + fab.E_MEDIA
    topo = lambda y: E.z_raia(y) - 2.0                      # guardas 2 mm abaixo do centro da bola
    pts = [(y0, Z0), (y1, Z0), (y1, topo(y1)), (y0, topo(y0))]
    corpo = cq.Workplane("YZ", origin=(X_G[0], 0, 0)).polyline(pts).close().extrude(X_G[1] - X_G[0])
    for x0, x1 in E.ORELHAS:
        corpo = corpo.union(caixa(x0, x1, y0 - 14.0, y0 + 4.0, Z0, E.Z_SAIDA_FUNDO))
    # cavidade: V de 120 graus + guardas verticais, ao longo do centro da bola
    t = math.tan(math.radians(M.ANG_V))
    g = E.GUARDA[0]
    cav = [(-g, -M.H_VERTICE + g * t), (0, -M.H_VERTICE), (g, -M.H_VERTICE + g * t), (g, 40.0), (-g, 40.0)]
    p0 = (E.X_RAIA, y0 - 5.0, E.z_raia(y0 - 5.0))
    p1 = (E.X_RAIA, Y_FIM, E.z_raia(Y_FIM))
    corpo = corpo.cut(M.canal_reto(p0, p1, perfil=cav))
    corpo = corpo.cut(cilindro(D_QUEDA, 60, (E.X_RAIA, E.Y_RAIA1, Z0 - 10), (0, 0, 1)))
    s3, h3 = fab.BOLSAO_PORCA["M3"]
    from common.features import bolsao_porca
    for fx, fy in E.FUROS_ORELHA:
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"], 30, (fx, fy, Z0 - 1), (0, 0, 1)))
        corpo = corpo.cut(bolsao_porca("M3", (fx, fy, Z0), (0, 0, 1), extra_saida=1.0))
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
    return []


def checa_bola(var="-"):
    """Bola rolando no V da calha e caindo pelo furo ate o funil, contra todas as pecas fixas e compradas."""
    import numpy as np
    from common.checks import c7_interferencia
    from maquina_a import montagem as MT
    outros = {f"{pid}.{v}": obj for pid, v, obj in MT.pecas_fixas() if pid not in ("A23",)}
    outros.update(MT.hardware_fixo())
    outros["A23"] = build()
    pts = [(E.X_RAIA, y, E.z_raia(y) + 0.5) for y in np.arange(E.Y_RAIA0 + 3.0, E.Y_RAIA1 + 0.1, 6.0)]
    pts += [(E.X_RAIA, E.Y_RAIA1, z) for z in np.arange(E.z_raia(E.Y_RAIA1), M.Z_FUNIL_TOPO - 2.0, -4.0)]
    bolas = cq.Workplane("XY").add([cq.Workplane("XY").sphere(E.R_B - 0.5).translate(c).val() for c in pts])
    r = c7_interferencia(bolas, outros)
    return dict(ok=r["ok"], colisoes=r["colisoes"], pontos=len(pts),
                nota="bola no V da calha (y=-90..66) e caindo pelo furo ate a borda do funil da A18")


FICHA = dict(orientacao="em pe, fundo plano na mesa", suporte="nao", perimetros=4, infill="20% gyroid", camada=0.20,
             montagem=("porcas M3 nos bolsoes de baixo das orelhas; apoiar o fundo na borda do funil da A18, orelhas por baixo "
                       "da saida A25; 2x M3x16 de cima."))
