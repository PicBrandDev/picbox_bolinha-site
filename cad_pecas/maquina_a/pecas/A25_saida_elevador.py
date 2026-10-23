"""A25 — Saida do elevador: piso com guardas da janela da cabeca A27 ate a calha A23.

Intencao:
- Funcao: a bola sobe presa no trilho de cima da A27 (150 graus). Dentro da janela (126..175 graus) a borda do piso
  (r=47,3) faz de parede; quando a beira do filete passa da borda (z=1588,7 a 150 graus) a bola rola para fora pelo
  caimento do filete, cai no piso (6 graus para +y) entre a guarda esquerda (x=79,5) e a parede da frente, e entra na
  calha A23 em y=-90. Nada da A25 fica dentro do raio da bola subindo (sem soleira interna).
- Interfaces: fundo da janela da A27 (o fundo plano apoia nele), tampa A22 (2 postes, M3 de cima),
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
TITULO = "Saida do elevador (piso + guardas)"
QTD = {"-": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
EIXOS_CONTEXTO = ["A"]
CONTATO_ESPERADO = ("A27", "A22", "A23")
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
    # dentro da janela o piso vai ate r=47,3 (a borda faz de parede ate a bola sair); nada entra no raio da bola
    borda = E.setor(E.R_BORDA_SAIDA, R_FORA + 0.5, *E.ARCO_ENTALHE, Z0, Z0 + 40.0)
    corpo = corpo.union(borda.intersect(_abaixo(E.z_saida, 80.0, 160.0, -180.0, -90.0)))
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
    """Centros da bola: rola para fora na janela (150 graus) quando a beira do filete chega na borda do piso, e segue o
    piso ate a calha (centro, giro do fuso). A subida ate ali e checada na A27."""
    pts = []
    ang = E.ANG_BOLA_TOPO
    g = E.giro_para_bola(E.ZC_SAI, ang)
    zc = E.ZC_SAI
    def piso(rr):
        return E.z_saida(E.p(rr, ang)[1]) if rr >= E.R_BORDA_SAIDA else -1e9
    for r in range(int(E.R_BOLA), 72, 3):
        x, y, _ = E.p(r, ang)
        if r > E.R_BORDA_SAIDA - 3.0:                      # passou da beira do filete: apoia no ponto mais alto do piso
            alto = max(piso(r + d) + ((E.R_B + 0.5) ** 2 - d * d) ** 0.5 for d in range(-18, 19, 2))
            zc = min(zc, alto)
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
    for pid in ("A22", "A27"):
        if pid in MT.PECAS:
            fixos[pid] = MT.modulo(pid).build(None, "-")
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
                nota="bola saindo pela janela da A27 a 150 graus (filete parado no ponto de saida) e no piso ate a A23")


FICHA = dict(orientacao="em pe, fundo plano na mesa", suporte="nao", perimetros=4, infill="20% gyroid", camada=0.20,
             montagem=("1) porcas M3 nos rasgos dos postes; 2) encaixar a borda do piso na janela da cabeca A27 (fundo apoiado no "
                       "fundo da janela); 3) tampa A22 por cima (2x M3x20); 4) calha A23: orelhas por baixo, 2x M3x16 de cima."))
