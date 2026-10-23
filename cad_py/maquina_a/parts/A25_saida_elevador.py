"""A25 — Saida do elevador: soleira dentro do entalhe do tubo e piso com guardas ate a calha A23.

Intencao:
- Funcao: no topo, a bola (girando com o fuso, ja acima do trilho) chega ao entalhe (122..175 graus), onde falta a
  parede; o filete cai 10 graus para fora e ela rola para a soleira (r>=38,5: fora do filete), depois para o piso
  (6 graus para +y) entre a guarda esquerda (x=79,5) e a parede da frente, e entra na calha A23 em y=-90.
- Interfaces: entalhe do acrilico (o fundo plano apoia no fundo do entalhe), tampa A22 (2 postes, M3 de cima),
  calha A23 (orelhas por baixo, 2x M3 de cima).
Impressao: em pe, fundo plano (z=1582) na mesa.
"""
import math

import cadquery as cq

from common import fab
from common.features import caixa, cilindro
from maquina_a import elevador as E

ID = "A25"
NOME = "saida_elevador"
TITULO = "Saida do elevador (soleira + piso)"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("elev_acrilico", "A22", "A23")
VISTA = (-1.0, 1.2, 0.9)

Z0 = E.Z_SAIDA_FUNDO
X_G = (E.X_RAIA - E.GUARDA[1], E.X_RAIA + E.GUARDA[1])   # 76,5 .. 123,5
Y0, Y1 = -170.0, E.Y_RAIA0             # ESTIMADO frente da saida (a bola entra em y~-157) e fim (-90)
Z_GUARDA = 1625.0                      # ESTIMADO topo das guardas (centro da bola ~1605 no piso)
POSTE = 10.0                           # parede de 2 mm em volta do rasgo da porca M3
E_ORELHA = 8.0
R_FORA = E.TUBO_D / 2 + E.FOLGA_TUBO   # 50,3


def _abaixo(zfun, x0, x1, y0, y1):
    """Solido de z=Z0 ate o plano z=zfun(y) (inclinado so em y)."""
    pts = [(y0, Z0), (y1, Z0), (y1, zfun(y1)), (y0, zfun(y0))]
    return cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts).close().extrude(x1 - x0)


def local(var="-"):
    x, y = E.C
    piso = _abaixo(E.z_saida, X_G[0], X_G[1], Y0, Y1)
    piso = piso.union(_abaixo(E.z_saida, X_G[1], E.POSTES[0][0] + POSTE / 2, E.POSTES[0][1] - POSTE / 2, Y1))
    for x0, x1 in E.ORELHAS:                                # apoios das orelhas da A23
        piso = piso.union(caixa(x0, x1, Y1 - 14.0, Y1, Z0, Z0 + E_ORELHA))
    g = E.GUARDA[1] - E.GUARDA[0]
    guardas = (caixa(X_G[0], X_G[0] + g, Y0, Y1, Z0, Z_GUARDA)
               .union(caixa(X_G[1] - g, X_G[1], -108.0, Y1, Z0, Z_GUARDA))   # comeca 10 mm depois do tubo: a bola sai do entalhe sem tocar
               .union(caixa(X_G[0], 105.5, Y0, Y0 + g, Z0, Z_GUARDA)))   # para 1,8 mm antes do tubo
    postes = cq.Workplane("XY")
    for px, py in E.POSTES:
        postes = postes.union(caixa(px - POSTE / 2, px + POSTE / 2, py - POSTE / 2, py + POSTE / 2, Z0, E.Z_TUBO1))
    corpo = piso.union(guardas).union(postes)
    corpo = corpo.cut(cilindro(2 * R_FORA, 200, (x, y, Z0 - 10), (0, 0, 1)))
    # soleira dentro do entalhe (revolucao 30 graus), do fundo plano ate o topo inclinado
    perfil = [(E.R_SOLEIRA, Z0), (R_FORA, Z0), (R_FORA, E.z_soleira(R_FORA)), (E.R_SOLEIRA, E.Z_SOLEIRA)]
    a0, a1 = E.ARCO_ENTALHE
    sol = cq.Workplane("XZ").polyline(perfil).close().revolve(a1 - a0, (0, 0, 0), (0, 1, 0))
    sh = sol.val().rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), a0).translate((x, y, 0))
    corpo = corpo.union(cq.Workplane("XY").add(sh))
    for px, py in E.POSTES:                                 # M3 de cima (da A22): porca num rasgo do poste
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"], 16, (px, py, E.Z_TUBO1 - 15), (0, 0, 1)))
        s3, h3 = fab.BOLSAO_PORCA["M3"]
        zp = E.Z_TUBO1 - 9.0
        corpo = corpo.cut(caixa(px - s3 / 2, px + 10, py - s3 / 2, py + s3 / 2, zp, zp + h3))
    for fx, fy in E.FUROS_ORELHA:                           # M3 de cima para as orelhas da A23
        corpo = corpo.cut(cilindro(fab.FURO_PASSANTE["M3"], 20, (fx, fy, Z0 - 1), (0, 0, 1)))
        corpo = corpo.cut(cilindro(fab.REBAIXO_DIN912["M3"][0], 20, (fx, fy, Z0 + E_ORELHA - 2.0), (0, 0, 1)))
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
    return [dict(nome=f"calha{k}", tipo="DIN912", bitola="M3", comp=16, ponto=(fx, fy, Z0 + E_ORELHA - 2.0), dir=(0, 0, -1),
                 chave=40, extra="porca M3 no bolsao de baixo da orelha da A23") for k, (fx, fy) in enumerate(E.FUROS_ORELHA)]


def caminho():
    """Centros da bola: gira com o fuso ate o entalhe, rola para fora, segue o piso ate a calha (z, giro do fuso)."""
    pts = []
    zc = E.Z_TRILHO[1] + E.R_B + 0.5                        # passou por cima do trilho
    for ang in range(int(E.ANG_TRILHO) - 3, int(E.ARCO_ENTALHE[1]) - 1, -6):
        pts.append((E.p(E.R_BOLA, ang, zc), E.giro_para_bola(zc, ang)))
    ang = sum(E.ARCO_ENTALHE) / 2                          # rola para fora no meio do entalhe (a bola ocupa +-24 graus)
    g = E.giro_para_bola(zc, ang)
    def apoio(rr):                                          # topo da soleira/piso no raio rr (ao longo do entalhe)
        if rr < E.R_SOLEIRA:
            return -1e9                                     # filete: a bola continua no apoio de cima (zc)
        return E.z_soleira(rr) if rr <= R_FORA else E.z_saida(E.p(rr, ang)[1])
    for r in range(int(E.R_BOLA), 70, 3):
        x, y, _ = E.p(r, ang)
        # centro apoiado no ponto mais alto embaixo da bola (amostras ao longo do raio)
        alto = max(apoio(r + d) + ((E.R_B + 0.5) ** 2 - d * d) ** 0.5 for d in range(-18, 19, 2))
        zc = min(zc, max(alto, -1e8)) if r > E.R_FILETE else zc
        if x < E.X_RAIA:
            break
        pts.append(((x, y, zc), g))
    x0, y0 = pts[-1][0][:2]
    n = 8
    for k in range(1, n + 1):
        xx = x0 + (E.X_RAIA - x0) * k / n
        yy = y0 + (Y1 - y0) * k / n
        pts.append(((xx, yy, E.z_saida(yy) + E.R_B + 0.5), g))
    return pts


def checa_bola(var="-"):
    from common.checks import c7_interferencia
    from maquina_a import montagem as MT
    fixos = {k: v for k, v in E.hardware().items() if k in ("elev_acrilico", "elev_trilho")}
    fixos["A25"] = build()
    if "A22" in MT.PECAS:
        fixos["A22"] = MT.modulo("A22").build(None, "-")
    col = {}
    pts = caminho()
    for (c, g) in pts:
        corpos = dict(fixos)
        corpos.update({f"A21.{j + 1}": E.fuso_maquina(j, g) for j in range(3)})
        b = cq.Workplane("XY").sphere(E.R_B - 0.5).translate(c)
        r = c7_interferencia(b, corpos)
        if not r["ok"]:
            col[f"({c[0]:.0f},{c[1]:.0f},{c[2]:.0f})"] = r["colisoes"]
    return dict(ok=not col, colisoes=col, pontos=len(pts),
                nota="bola acima do trilho girando com o fuso ate o entalhe, rolando para fora e no piso ate a A23")


FICHA = dict(orientacao="em pe, fundo plano na mesa", suporte="nao", perimetros=4, infill="20% gyroid", camada=0.20,
             montagem=("1) cortar o entalhe no topo do tubo (122..175 graus, 58 mm de altura); 2) porcas M3 nos rasgos dos "
                       "postes; 3) encaixar a soleira no entalhe (fundo apoiado no acrilico); 4) tampa A22 por cima (2x M3x20); "
                       "5) calha A23: orelhas por baixo, 2x M3x16 de cima."))
