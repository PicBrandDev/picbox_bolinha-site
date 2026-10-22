"""A13 — Rodape da bandeja (2 metades: esquerda 'e', direita 'd').

Intencao:
- Funcao: parede no fundo da bandeja (y=-23..-20): a bola nao entra embaixo do perfil e do carro do eixo B.
- Interfaces: placa de MDF (aba de tras com 3 parafusos de madeira 3,5x12 por metade), EVA encosta na frente.
Impressao: deitado na face da frente (a da bola), aba para cima.
"""
import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import bandeja as B

ID = "A13"
NOME = "rodape"
TITULO = "Rodape da bandeja"
QTD = {"e": 1, "d": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["B"]
CONTATO_ESPERADO = ("bandeja_mdf", "bandeja_eva", "A13")

ABA = (6.0, fab.E_MEDIA)               # ESTIMADO largura (para tras) e espessura da aba
E_PAREDE = B.Y_RODAPE[1] - B.Y_RODAPE[0]


def _secao(x0, x1):
    """Parede + aba entre x0 e x1, com a base no topo do MDF (inclinado em x)."""
    y0, y1 = B.Y_RODAPE
    ym = (y0 + y1) / 2
    za0, za1 = B.z_eva(x0, ym) - B.EVA, B.z_eva(x1, ym) - B.EVA
    # perfil no plano XZ (base inclinada, topo paralelo) extrudado em y
    parede = (cq.Workplane("XZ", origin=(0, y1, 0)).polyline([(x0, za0), (x1, za1), (x1, za1 + B.EVA + B.H_RODAPE),
                                                              (x0, za0 + B.EVA + B.H_RODAPE)]).close().extrude(E_PAREDE))
    aba = (cq.Workplane("XZ", origin=(0, y1 + ABA[0], 0)).polyline([(x0, za0), (x1, za1), (x1, za1 + ABA[1]), (x0, za0 + ABA[1])])
           .close().extrude(ABA[0]))
    return parede.union(aba)


def local(var="e"):
    x0, x1 = (B.X_RODAPE[0], 0.0) if var == "e" else (0.0, B.X_RODAPE[1])
    r = _secao(x0, x1)
    try:
        r = r.edges("|Y").fillet(fab.R_DETALHE * 2)
    except Exception:
        pass
    for k in range(3):
        x = x0 + (x1 - x0) * (k + 0.5) / 3
        r = r.cut(cilindro(fab.FURO_PASSANTE["M4"] - 0.5, 20, (x, B.Y_RODAPE[1] + ABA[0] / 2, B.z_eva(x, -20) - 15), (0, 0, 1)))
    return r


def build(p=None, var="e"):
    return local(var)


def impressao(var="e"):
    sh = local(var).val().rotate((0, 0, 0), (1, 0, 0), 90)     # face da frente (y=-23) para baixo
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="e"):
    return []


def checa_bola(var="e"):
    """Bola rolando em toda a bandeja (grade), com o carro B (boca) passando por cima em 5 posicoes."""
    import cadquery as cq
    from common import hardware as hw
    from common.checks import c7_interferencia
    from maquina_a import montagem as MT
    r = 19.0
    pts = [(x, y, B.z_eva(x, y) + r + 0.6) for x in range(-180, 181, 30) for y in range(-185, -42, 20)]
    bolas = cq.Workplane("XY").add([hw.bola(c, 2 * (r + fab.FOLGA_BOLA_RADIAL)).val() for c in pts])
    fixos = MT.corpos_contexto_bandeja()
    res = c7_interferencia(bolas, fixos)
    carro = {}
    for xc in (-144.2, -72.0, 0.0, 72.0, 144.2):
        for k, w in MT.corpos_carro("B").items():
            sh = (w.val() if isinstance(w, cq.Workplane) else w).translate((xc, 0, 0))
            carro[f"{k}@{xc:+.0f}"] = cq.Workplane("XY").add(sh)
    res2 = c7_interferencia(bolas, carro)
    return dict(ok=res["ok"] and res2["ok"], fixos=res["colisoes"], carro_b=res2["colisoes"], pontos=len(pts),
                nota="bola com 1,5 mm de folga em cada ponto da grade (30 x 20 mm) da bandeja")


FICHA = dict(orientacao="deitado na face da frente", suporte="nao", perimetros=4, infill="20%", camada=0.20,
             montagem="na placa de MDF antes do EVA: 3 parafusos de madeira 3,5x12 pela aba (por metade); EVA encosta na frente.")
