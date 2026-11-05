"""Features reutilizaveis. Todas as folgas vem de fab.py."""
import math

import cadquery as cq

from . import fab


def caixa(x0, x1, y0, y1, z0, z1):
    """Solido retangular entre dois cantos."""
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cilindro(d, comprimento, origem, direcao):
    """Cilindro de diametro d a partir de 'origem' ao longo de 'direcao' (vetor unitario)."""
    return cq.Workplane(cq.Plane(origin=origem, xDir=_perp(direcao), normal=direcao)).circle(d / 2).extrude(comprimento)


def _perp(v):
    v = cq.Vector(*v)
    a = cq.Vector(0, 0, 1) if abs(v.z) < 0.9 else cq.Vector(1, 0, 0)
    return v.cross(a).normalized()


def teardrop(d, comprimento, origem, direcao, cima=(0, 0, 1)):
    """Furo horizontal em gota: circulo + ponta a 45 graus apontando para 'cima' (direcao de impressao).
    Usado acima de fab.TEARDROP_ACIMA_DE; abaixo disso devolve cilindro."""
    if d <= fab.TEARDROP_ACIMA_DE:
        return cilindro(d, comprimento, origem, direcao)
    n = cq.Vector(*direcao).normalized()
    up = cq.Vector(*cima)
    up = (up - n * up.dot(n)).normalized()      # 'cima' projetado no plano do furo
    xdir = up.cross(n).normalized()
    pl = cq.Plane(origin=origem, xDir=xdir, normal=n)
    r = d / 2
    # no plano: y local = up. Gota: arco de 225 graus + duas retas tangentes ate a ponta em y = r*sqrt(2)
    s = r / math.sqrt(2)
    ponta = r * math.sqrt(2)
    return (cq.Workplane(pl).moveTo(s, s).threePointArc((0, -r), (-s, s))
            .lineTo(0, ponta).close().extrude(comprimento))


def furo_passante(bitola, comprimento, origem, direcao, horizontal=False, cima=(0, 0, 1)):
    d = fab.FURO_PASSANTE[bitola]
    return teardrop(d, comprimento, origem, direcao, cima) if horizontal else cilindro(d, comprimento, origem, direcao)


def rebaixo(bitola, origem, direcao, extra=0.0, horizontal=False, cima=(0, 0, 1)):
    """Rebaixo de cabeca DIN 912, comecando em 'origem' (na face) e entrando ao longo de 'direcao'."""
    d, h = fab.REBAIXO_DIN912[bitola]
    o = cq.Vector(*origem) - cq.Vector(*direcao).normalized() * 5   # sobra para fora da face
    if horizontal:
        return teardrop(d, h + 5 + extra, o.toTuple(), direcao, cima)
    return cilindro(d, h + 5 + extra, o.toTuple(), direcao)


def bolsao_porca(bitola, origem, direcao, angulo=0.0, prof=None, extra_saida=0.0):
    """Bolsao sextavado (entre faces de fab) com a face de entrada em 'origem', entrando ao longo de 'direcao'.
    'angulo' gira o sextavado em torno do eixo; extra_saida estende para fora da face (abertura)."""
    s, h = fab.BOLSAO_PORCA[bitola]
    h = prof if prof is not None else h
    n = cq.Vector(*direcao).normalized()
    o = cq.Vector(*origem) - n * extra_saida
    pl = cq.Plane(origin=o.toTuple(), xDir=_perp(direcao), normal=n.toTuple())
    return (cq.Workplane(pl).transformed(rotate=(0, 0, angulo))
            .polygon(6, s / math.cos(math.pi / 6)).extrude(h + extra_saida))


def chanfro_base(peca, z_base, tamanho=None):
    """Chanfra as arestas que tocam a mesa (face plana em z=z_base, no referencial em que for chamado)."""
    t = tamanho or fab.CHANFRO_BASE
    try:
        return peca.faces(cq.selectors.NearestToPointSelector((0, 0, z_base - 1e3))).edges().chamfer(t)
    except Exception:
        return peca
