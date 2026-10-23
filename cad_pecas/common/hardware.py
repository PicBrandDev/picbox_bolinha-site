"""Corpos de referencia das pecas compradas: so para checagem (interferencia, folga, furacao).
Nunca exportados para impressao. Cotas tagueadas # CATALOGO <fonte> ou # ESTIMADO.

Os corpos do eixo estao no referencial LOCAL do eixo (ver maquina_a/layout.py):
x ao longo do trilho, y=0 centro do trilho, z=0 meio da altura do trilho, patim por cima.
"""
import math

import cadquery as cq

from .features import caixa, cilindro

# ------------------------------------------------------------------ MGN12 / MGN12H  (CATALOGO HIWIN MGN12)
TRILHO_L = 12.0          # CATALOGO HIWIN W_R
TRILHO_H = 8.0           # CATALOGO HIWIN H_R
PATIM_W = 27.0           # CATALOGO HIWIN W (MGN12H)
PATIM_L = 45.4           # CATALOGO HIWIN L (MGN12H)
PATIM_H = 13.0           # CATALOGO HIWIN H (base do trilho ao topo do patim)
PATIM_H1 = 3.0           # CATALOGO HIWIN H1 (folga sob o patim)
PATIM_FUROS = (20.0, 20.0)   # CATALOGO HIWIN B x C, M3
PATIM_ROSCA = 3.5        # CATALOGO HIWIN profundidade util da rosca

# ------------------------------------------------------------------ perfil 2020 V-slot
PERFIL_LADO = 20.0       # CATALOGO serie 20
PERFIL_FENDA = 6.2       # CATALOGO
PERFIL_FENDA_PROF = 6.0  # CATALOGO (aprox.)
PERFIL_R = 1.5           # CATALOGO raio dos cantos externos

# ------------------------------------------------------------------ NEMA 17 (17HS4401)
NEMA_A = 42.3            # CATALOGO NEMA 17
NEMA_L = 40.0            # CATALOGO 17HS4401
NEMA_FUROS = 31.0        # CATALOGO
NEMA_BOSS = 22.0         # CATALOGO
NEMA_BOSS_H = 2.0        # CATALOGO
NEMA_EIXO = 5.0          # CATALOGO
NEMA_EIXO_L = 24.0       # CATALOGO (da face do flange, inclui o ressalto)
NEMA_ROSCA = 4.5         # CATALOGO profundidade dos furos M3

# ------------------------------------------------------------------ GT2
GT2_20T_PASSO_R = 20 * 2 / (2 * math.pi)   # CATALOGO 6,37
POLIA_20T_FLANGE = 16.0  # CATALOGO
POLIA_20T_L = 16.0       # CATALOGO
TENSORA_D = 18.0         # CATALOGO polia tensora 20T c/ rolamento
TENSORA_L = 8.5          # CATALOGO
CORREIA_6_L = 6.0        # CATALOGO
CORREIA_ESP = 1.38       # CATALOGO GT2 (total)

# ------------------------------------------------------------------ fim de curso mecanico (modulo de impressora 3D)
FC_PLACA = (40.0, 16.0, 1.6)   # ESTIMADO medir
FC_FUROS = (-16.0, 2.0)        # ESTIMADO medir (ao longo dos 40 mm, a partir do centro)
FC_CORPO = (6.0, 18.8, 6.5)    # ESTIMADO medir (inicio, fim, altura)
FC_DOBRA = (6.5, 8.1)          # ESTIMADO medir
FC_ALAV = 15.5                 # ESTIMADO medir
FC_ANG = 11.0                  # ESTIMADO medir

# ------------------------------------------------------------------ parafusos (DIN 912 / ISO 7380)
DIN912 = {"M2": (3.8, 2.0), "M3": (5.5, 3.0), "M4": (7.0, 4.0), "M5": (8.5, 5.0)}   # CATALOGO (d cabeca, h)
ISO7380 = {"M3": (5.7, 1.65), "M4": (7.6, 2.2), "M5": (9.5, 2.75)}                 # CATALOGO
D_NOMINAL = {"M2": 2.0, "M3": 3.0, "M4": 4.0, "M5": 5.0}


def trilho(comprimento=400.0):
    return caixa(-comprimento / 2, comprimento / 2, -TRILHO_L / 2, TRILHO_L / 2, -TRILHO_H / 2, TRILHO_H / 2)


def perfil(comprimento=400.0, zc=-14.0):
    h = PERFIL_LADO / 2
    p = caixa(-comprimento / 2, comprimento / 2, -h, h, zc - h, zc + h).edges("|X").fillet(PERFIL_R)
    f, d = PERFIL_FENDA / 2, PERFIL_FENDA_PROF
    for corte in (caixa(-comprimento, comprimento, -f, f, zc + h - d, zc + h + 1),
                  caixa(-comprimento, comprimento, -f, f, zc - h - 1, zc - h + d),
                  caixa(-comprimento, comprimento, h - d, h + 1, zc - f, zc + f),
                  caixa(-comprimento, comprimento, -h - 1, -h + d, zc - f, zc + f)):
        p = p.cut(corte)
    return p


def patim(x=0.0):
    zb = -TRILHO_H / 2 + PATIM_H1          # fundo do patim
    zt = -TRILHO_H / 2 + PATIM_H           # topo (z=9)
    l, w = PATIM_L / 2, PATIM_W / 2
    topo = caixa(x - l, x + l, -w, w, TRILHO_H / 2 + 0.2, zt)
    abas = caixa(x - l, x + l, -w, w, zb, TRILHO_H / 2 + 0.2).cut(
        caixa(x - l - 1, x + l + 1, -TRILHO_L / 2 - 0.2, TRILHO_L / 2 + 0.2, zb - 1, TRILHO_H / 2 + 0.2))
    p = topo.union(abas)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = p.cut(cilindro(3.0, PATIM_ROSCA + 0.01, (x + sx * PATIM_FUROS[0] / 2, sy * PATIM_FUROS[1] / 2, zt - PATIM_ROSCA), (0, 0, 1)))
    return p


def furos_patim(x=0.0):
    zt = -TRILHO_H / 2 + PATIM_H
    return [((x + sx * PATIM_FUROS[0] / 2, sy * PATIM_FUROS[1] / 2, zt), (0, 0, 1))
            for sx in (-1, 1) for sy in (-1, 1)]


def nema17(xc, yface, zc=0.0, sentido=1):
    """Motor com a face do flange em y=yface, corpo para +y*sentido, eixo para -y*sentido."""
    a = NEMA_A / 2
    s = sentido
    y0, y1 = sorted((yface, yface + s * NEMA_L))
    corpo = caixa(xc - a, xc + a, y0, y1, zc - a, zc + a).edges("|Y").chamfer(3.6)
    boss = cilindro(NEMA_BOSS, NEMA_BOSS_H, (xc, yface, zc), (0, -s, 0))
    eixo = cilindro(NEMA_EIXO, NEMA_EIXO_L, (xc, yface, zc), (0, -s, 0))
    m = corpo.union(boss).union(eixo)
    for k, (dx, dz) in enumerate(_quadrado(NEMA_FUROS)):
        m = m.cut(cilindro(3.0, NEMA_ROSCA, (xc + dx, yface, zc + dz), (0, s, 0)))
    return m


def furos_nema17(xc, yface, zc=0.0, sentido=1):
    return [((xc + dx, yface, zc + dz), (0, sentido, 0)) for dx, dz in _quadrado(NEMA_FUROS)]


def _quadrado(lado):
    h = lado / 2
    return [(-h, -h), (h, -h), (h, h), (-h, h)]


def polia_20t(xc, y0, zc=0.0):
    """Polia GT2 20T furo 5, de y0 ate y0+16 (flanges Ø16)."""
    return cilindro(POLIA_20T_FLANGE, POLIA_20T_L, (xc, y0, zc), (0, 1, 0))


def tensora(xc, yc, zc=0.0):
    return (cilindro(TENSORA_D, TENSORA_L, (xc, yc - TENSORA_L / 2, zc), (0, 1, 0))
            .cut(cilindro(5.0, TENSORA_L + 2, (xc, yc - TENSORA_L / 2 - 1, zc), (0, 1, 0))))


def correia_eixo(x0, x1, yc, zc=0.0, r=GT2_20T_PASSO_R):
    """Dois ramos retos da GT2 6 mm entre polias de raio primitivo r centradas em x0 e x1."""
    w = CORREIA_6_L / 2
    ri, re = r - 0.4, r - 0.4 + CORREIA_ESP
    a, b = min(x0, x1), max(x0, x1)
    return (caixa(a, b, yc - w, yc + w, zc + ri, zc + re)
            .union(caixa(a, b, yc - w, yc + w, zc - re, zc - ri)))


def fim_de_curso(x_costas, zc, sentido=-1, yc=0.0):
    """Modulo FC em pe: costas da placa em x=x_costas, componentes para x*sentido, alavanca para baixo.
    Ao longo dos 40 mm: z = zc - bx (bx coordenada da placa)."""
    w, d, e = FC_PLACA
    s = sentido
    xa, xb = sorted((x_costas, x_costas + s * e))
    placa = caixa(xa, xb, yc - d / 2, yc + d / 2, zc - w / 2, zc + w / 2)
    xf = x_costas + s * e                          # face dos componentes
    c0, c1, ch = FC_CORPO
    xc0, xc1 = sorted((xf, xf + s * ch))
    corpo = caixa(xc0, xc1, yc - 2.9, yc + 2.9, zc - c1, zc - c0)
    hx, hz = FC_DOBRA
    a = math.radians(FC_ANG)
    tip_bx, tip_h = hx + FC_ALAV * math.cos(a), hz + FC_ALAV * math.sin(a)
    # alavanca: fita de aco 4 x 0,5 da dobra ate a ponta, poligono no plano XZ
    (xa1, za1), (xb1, zb1) = (xf + s * hz, zc - hx), (xf + s * tip_h, zc - tip_bx)
    alav = (cq.Workplane("XZ").polyline([(xa1, za1), (xb1, zb1), (xb1 + s * 0.5, zb1), (xa1 + s * 0.5, za1)])
            .close().extrude(-2, both=True).translate((0, yc, 0)))
    m = placa.union(corpo).union(alav)
    for bx in FC_FUROS:
        m = m.cut(cilindro(3.2, 10, (x_costas - 5, yc, zc - bx), (1, 0, 0)))
    return m


def furos_fim_de_curso(x_costas, zc, yc=0.0):
    return [((x_costas, yc, zc - bx), (1, 0, 0)) for bx in FC_FUROS]


def ponta_alavanca_fc(x_costas, zc, sentido=-1):
    a = math.radians(FC_ANG)
    tip_bx = FC_DOBRA[0] + FC_ALAV * math.cos(a)
    tip_h = FC_DOBRA[1] + FC_ALAV * math.sin(a)
    return (x_costas + sentido * (FC_PLACA[2] + tip_h), zc - tip_bx)


def parafuso_din912(bitola, comprimento, ponto, direcao):
    """Cabeca apoiada em 'ponto', haste ao longo de 'direcao'."""
    dc, hc = DIN912[bitola]
    n = cq.Vector(*direcao).normalized()
    cab = cilindro(dc, hc, (cq.Vector(*ponto) - n * hc).toTuple(), n.toTuple())
    haste = cilindro(D_NOMINAL[bitola], comprimento, ponto, n.toTuple())
    return cab.union(haste)


def parafuso_iso7380(bitola, comprimento, ponto, direcao):
    dc, hc = ISO7380[bitola]
    n = cq.Vector(*direcao).normalized()
    cab = cilindro(dc, hc, (cq.Vector(*ponto) - n * hc).toTuple(), n.toTuple())
    haste = cilindro(D_NOMINAL[bitola], comprimento, ponto, n.toTuple())
    return cab.union(haste)


def acesso_chave(bitola, ponto, direcao, comprimento=60.0, iso7380=False):
    """Volume livre que a chave precisa: cilindro do diametro da cabeca, saindo da cabeca para tras."""
    dc, hc = (ISO7380 if iso7380 else DIN912)[bitola]
    n = cq.Vector(*direcao).normalized()
    return cilindro(dc + 1.0, comprimento, (cq.Vector(*ponto) - n * (hc + 0.2)).toTuple(), (-n).toTuple())


# ------------------------------------------------------------------ bola
def bola(centro, d):
    return cq.Workplane("XY").sphere(d / 2).translate(centro)


# ------------------------------------------------------------------ solenoide JF-0826B (puxar) — ESTIMADO, medir
SOL_CORPO = (25.0, 22.0, 27.0)   # ESTIMADO x (profundidade a partir da face de fixacao), y, z (ao longo do embolo)
SOL_EMBOLO = 7.4                 # ESTIMADO diametro do embolo
SOL_CURSO = 10.0                 # ESTIMADO
SOL_FUROS = (8.5, 18.5)          # ESTIMADO furos M3 da face de fixacao, medidos da face do embolo


def solenoide(x_face, yc, z_base, embolo_exposto):
    """Corpo com a face de fixacao em x=x_face (corpo para +x), face do embolo em z=z_base (embolo para -z)."""
    dx, dy, dz = SOL_CORPO
    corpo = caixa(x_face, x_face + dx, yc - dy / 2, yc + dy / 2, z_base, z_base + dz)
    emb = cilindro(SOL_EMBOLO, embolo_exposto + 1, (x_face + dx / 2, yc, z_base + 1), (0, 0, -1))
    return corpo.union(emb)


# ------------------------------------------------------------------ servo SG90 — ESTIMADO, medir
SG90 = dict(L=22.8, W=12.2, H=22.7, orelha_h=15.9, orelha_e=2.5, orelha_L=32.2, furos=27.8, eixo_off=5.9, eixo_h=4.0)


def sg90(base_x, y_eixo, z_eixo, sentido=1):
    """Servo deitado: altura ao longo de x a partir de base_x (corpo para +x*sentido), eixo de saida em (y_eixo, z_eixo)
    apontando para +x*sentido. O eixo fica a eixo_off de uma ponta (lado -y)."""
    s = SG90
    x0, x1 = sorted((base_x, base_x + sentido * s["H"]))
    y0 = y_eixo - s["eixo_off"]
    corpo = caixa(x0, x1, y0, y0 + s["L"], z_eixo - s["W"] / 2, z_eixo + s["W"] / 2)
    xo = base_x + sentido * s["orelha_h"]
    xo0, xo1 = sorted((xo, xo + sentido * s["orelha_e"]))
    yc = y0 + s["L"] / 2
    orelha = caixa(xo0, xo1, yc - s["orelha_L"] / 2, yc + s["orelha_L"] / 2, z_eixo - s["W"] / 2, z_eixo + s["W"] / 2)
    eixo = cilindro(4.8, s["eixo_h"], (base_x + sentido * s["H"], y_eixo, z_eixo), (sentido, 0, 0))
    return corpo.union(orelha).union(eixo)


def furos_sg90(base_x, y_eixo, z_eixo, sentido=1):
    s = SG90
    yc = y_eixo - s["eixo_off"] + s["L"] / 2
    xo = base_x + sentido * s["orelha_h"]
    return [((xo, yc + k * s["furos"] / 2, z_eixo), (sentido, 0, 0)) for k in (-1, 1)]


def tubo(x0, x1, y, z0, z1, d=50.0, di=44.0):
    """Tubo acrilico entre dois centros de eixo (x0,y,z0) -> (x1,y,z1)."""
    a, b = cq.Vector(x0, y, z0), cq.Vector(x1, y, z1)
    n = (b - a).normalized()
    L = (b - a).Length
    return cilindro(d, L, a.toTuple(), n.toTuple()).cut(cilindro(di, L + 2, (a - n).toTuple(), n.toTuple()))
