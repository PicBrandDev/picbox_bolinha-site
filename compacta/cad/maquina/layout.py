"""PICBOX compacta R2: maquina completa (elevador em torre + eixos, carros, anel, bandeja, fila e esteiras).

Referencial (mm): X para a direita do jogador, Y para o fundo (tela em Y 230), Z para cima, piso do gabinete em Z 0.
Espaco livre 440 x 430 x 230: paredes em X -220 / 220, teto em Z 430. O elevador (elevador2.py) e uma torre de 2 pecas
em X 160..220; a rampa sobe e desce em rasgos na frente da torre (ajuste da pega).

Arquitetura (decisoes de 05/11/2026, com o que o usuario ja tem: 2 jogos MGN12 + perfil 2020 + NEMA 17):
  * eixo A (em cima) e eixo B (embaixo): perfil 2020 x 400 na FRENTE (Y 8..28), trilho MGN12 x 400 (sem cortar) na
    face de tras do perfil, patim MGN12H; correia GT2 6 aberta num plano horizontal logo abaixo do perfil, NEMA 17 com
    o eixo para cima no canto esquerdo da frente e polia tensora no bloco da direita.
  * carro A: placa no patim + prateleira que leva o eletroima P20/15 ate o plano da bola (Y 73,7). Pega a bola no
    bolso da rampa do elevador (X 192,3) a 1 mm de distancia e solta no curso de jogo (+-120).
  * carro B: placa no patim + braco + anel (furo 38, passagem limpa +-6,3) com barreira IR (LED + fototransistor 5 mm).
  * bandeja impressa em 3 placas com EVA 5 mm por cima, caindo para o fundo (4 graus) e para a esquerda (2,5 graus);
    entrega a bola na fila por cima de um labio de 10 mm, so em X < 40 (longe da comporta).
  * esteiras porta-cabo 7x7: A deitada atras do carro, numa prateleira pendurada no teto; B em pe na frente, no piso.
"""
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
import elevador2 as EL  # noqa: E402

R = EL.R_BOLA
GX, GY, GZ = EL.GX, EL.GY, EL.GZ
# inclinacoes R2 (1 grau a mais em tudo): fila 5 (direita) e 4 (esquerda); bandeja 5 para o fundo,
# 3,5 para a esquerda no meio/direita e 4 na parte da esquerda
I_FILA_D, I_FILA_E, I_BAND_Y, I_BAND_X, I_BAND_XE = 5.0, 4.0, 5.0, 3.5, 4.0
T_FD, T_FE, T_BY, T_BX, T_BXE = (math.tan(math.radians(a)) for a in (I_FILA_D, I_FILA_E, I_BAND_Y, I_BAND_X, I_BAND_XE))


def rot(rx=0.0, ry=0.0, rz=0.0):
    a, b, c = (math.radians(v) for v in (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rz @ Rx @ Ry


def quat(Rm):
    """Matriz -> quaternio (w, x, y, z), estavel tambem perto de 180 graus (Shepperd)."""
    m = np.asarray(Rm, float)
    t = np.trace(m)
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        q = [0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = math.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        q = [(m[2, 1] - m[1, 2]) / s, 0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s]
    elif m[1, 1] > m[2, 2]:
        s = math.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        q = [(m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s]
    else:
        s = math.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        q = [(m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s]
    return [float(v) for v in q]


EL.quat = quat          # o elevador usa a mesma (a dele falhava em 180 graus)


@dataclass
class M:
    # eixos
    zpA: float = 410.0                 # centro do perfil de cima
    zpB: float = 81.0                  # centro do perfil de baixo
    y_perfil: tuple = (8.0, 28.0)
    L_perfil: float = 400.0
    dz_correia: float = -22.0          # plano da correia em relacao ao centro do perfil
    y_correia: float = 22.0            # centro da correia (ramos em y +- r_pitch)
    x_motor: float = -194.0            # 10 mm mais perto da parede (gabinete mais largo)
    x_tensora: float = 195.0
    dA: float = 26.0                   # eletroima a direita do centro do patim
    curso: float = 120.0               # curso de jogo dos dois carros: +-120 (bola e anel)
    c_casa: float = -146.0             # centro do patim no fim de curso da esquerda (os dois eixos)
    arruela_e: float = 2.0             # arruela de aco M10 (20 x 10,5 x 2) colada na face do ima
    arruela_furo: float = 10.5
    # bola, pega e queda
    x_pega: float = 191.8              # eixo do eletroima na pega (1,5 mm a esquerda da bola no bolso; R2: era 1)
    y_bola: float = 74.2               # plano da bola (eixo do eletroima; 1,5 mm atras da bola no bolso; R2: era 1)
    gap_pega: float = 0.6              # face de baixo da arruela ate o topo da bola no bolso
    queda: float = 250.0               # centro da bola presa ate o topo do anel
    folga_limpa: float = 6.3
    r_flange: float = 26.0
    r_tubo: float = 23.5
    h_anel: float = 22.0
    incl_rampa_x: float = 1.5          # rampa cai para a parede da direita (a bola encosta nela)
    # bandeja e fila
    lip: float = 10.0
    x_entrada: float = 40.0            # a bola so entra na fila em X < 40
    eva: float = 5.0
    e_placa: float = 4.0
    y_bandeja: tuple = (51.0, 127.5)
    x_juntas: tuple = (-217.0, -30.0, 120.0, 213.5)
    # esteiras (7x7): largura 10 (pino), altura 11
    est_h: float = 11.0
    est_w: float = 10.0
    RcA: float = 19.5
    RcB: float = 18.0

    @property
    def el(self):
        return EL.P()

    @property
    def dZ(self):                      # quanto o eixo de cima subiu em relacao a R1 (prateleira, ganchos, esteira)
        return self.zpA - 405.0

    # ---------------------------------------------------------------- pega (bolso da rampa)
    def plano_rampa(self):
        e = self.el
        Rr = rot(rx=e.incl_rampa, ry=self.incl_rampa_x)
        n = Rr @ np.array([0, 0, 1.0])
        tr = math.tan(math.radians(e.incl_rampa))
        pt = np.array([191.75, 94.0, e.z_rampa - (128 - 94) * tr])     # topo da rampa, como no elevador
        return Rr, n, pt

    def z_rampa(self, x, y):
        _, n, pt = self.plano_rampa()
        return pt[2] - (n[0] * (x - pt[0]) + n[1] * (y - pt[1])) / n[2]

    @property
    def bola_bolso(self):
        _, n, pt = self.plano_rampa()
        x, y = 206.0 - R, 60.0 + R
        z = pt[2] + (R - n[0] * (x - pt[0]) - n[1] * (y - pt[1])) / n[2]
        return np.array([x, y, z])

    @property
    def face_ima(self):
        return float(self.bola_bolso[2] + R + self.gap_pega)

    @property
    def assento(self):                 # quanto o topo da bola entra no furo da arruela
        a = self.arruela_furo / 2
        return R - math.sqrt(R * R - a * a)

    @property
    def zs(self):                      # centro da bola presa (encaixada no furo da arruela)
        return self.face_ima + self.assento - R

    @property
    def zb(self):                      # topo do anel
        return self.zs - self.queda

    @property
    def r_furo(self):
        return R + self.folga_limpa

    # ---------------------------------------------------------------- fila e bandeja
    def f_fila(self, x):               # piso da fila (onde a bola encosta)
        e = self.el
        if x >= -30:
            return e.zf_fim + (e.x_fila_fim - min(x, e.x_fila_fim)) * T_FD
        return e.zf_fim + (e.x_fila_fim + 30) * T_FD + (-30 - x) * T_FE

    def z_labio(self, x):
        return self.f_fila(x) + self.lip

    def s_bandeja(self, x, y):         # topo do EVA
        s0 = self.z_labio(-30) + 1.0
        yb = self.y_bandeja[1]
        if x < -30:
            return s0 + (-30 - x) * T_BXE + (yb - y) * T_BY
        return s0 + (x + 30) * T_BX + (yb - y) * T_BY

    # ---------------------------------------------------------------- curso dos carros
    @property
    def cA(self):                      # (min, max) do centro do patim A
        return (self.c_casa, self.x_pega - self.dA)

    @property
    def cB(self):
        return (self.c_casa, self.curso)

    @property
    def x_fdc_dir(self):               # alavanca do fim de curso da direita (0,8 mm alem da presilha do carro A na pega)
        return self.cA[1] + FIX[1] + 2 + 0.8

    @property
    def cB_seg(self):                  # ate onde o carro B pode ir: batedor 2 mm alem da alavanca do fim de curso
        return self.x_fdc_dir + 1.5 - BATEDOR_B[1]


# ===================================================================== geometria
def caixa(g, nome, corpo, x0, x1, y0, y1, z0, z1, peca, cor, R=None, grupo="fixa"):
    c = [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]
    g.append(dict(nome=nome, corpo=corpo, tipo="box", meio=[(x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2],
                  pos=c, quat=EL.quat(R if R is not None else np.eye(3)), grupo=grupo, peca=peca, cor=cor))


def placa_plano(g, nome, corpo, x0, x1, y0, y1, esp, Rm, ztopo, peca, cor):
    """Placa cujo topo passa por ztopo(x, y) (plano) no centro."""
    n = Rm @ np.array([0, 0, 1.0])
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    c = np.array([xm, ym, ztopo(xm, ym)]) - n * esp / 2
    g.append(dict(nome=nome, corpo=corpo, tipo="box", meio=[(x1 - x0) / 2, (y1 - y0) / 2, esp / 2],
                  pos=c.tolist(), quat=EL.quat(Rm), grupo="fixa", peca=peca, cor=cor))


def cil(g, nome, corpo, c, r, meio, eixo, peca, cor):
    Rm = {"y": rot(rx=90), "x": rot(ry=90), "z": np.eye(3)}[eixo]
    g.append(dict(nome=nome, corpo=corpo, tipo="cylinder", meio=[r, meio], pos=list(c), quat=EL.quat(Rm),
                  grupo="fixa", peca=peca, cor=cor))


def anel(g, nome, corpo, c, r0, r1, z0, z1, peca, cor):
    g.append(dict(nome=nome, corpo=corpo, tipo="anel", meio=[r0, r1, (z1 - z0) / 2], pos=[c[0], c[1], (z0 + z1) / 2],
                  quat=[1, 0, 0, 0], grupo="fixa", peca=peca, cor=cor))


BASE_CABINE = 10.0    # a cabine e impressa em pe sobre uma base plana em Z -10 (relativo a Zc)

# o que sai do modelo do elevador (substituido aqui)
TIRAR = {"chao", "parede_dir", "rampa", "rampa_esq", "rampa_dir", "rampa_fim",
         "fila_piso", "fila_frente", "fila_frente_baixo", "fila_fundo", "fila_fundo_fim", "fila_inicio"}


def geometria(m: M):
    e = m.el
    g = [d for d in EL.geometria(e) if d["nome"] not in TIRAR]
    for d in g:
        d.setdefault("grupo", "fixa")
    # ------------------------------------------------ gabinete (so para checar; nao aparece nas imagens)
    caixa(g, "piso", "mundo", -GX, GX, 0, GY, -18, 0, "Gabinete", "chao")
    caixa(g, "parede_esq", "mundo", -GX - 18, -GX, 0, GY, 0, GZ, "Gabinete", "transp")
    caixa(g, "parede_dir", "mundo", GX, GX + 18, 0, GY, 0, GZ, "Gabinete", "transp")
    caixa(g, "teto", "mundo", -GX, GX, 0, GY, GZ, GZ + 18, "Gabinete", "transp")
    caixa(g, "tela", "mundo", -GX, GX, GY, GY + 5, 0, GZ, "Tela", "tela")

    rampa(g, m)
    fila(g, m)
    for eixo in ("A", "B"):
        eixo_linear(g, m, eixo)
    carro_a(g, m)
    carro_b(g, m)
    bandeja(g, m)
    suporte_esteira(g, m)
    return g


X_BOLSO = 186.0      # borda de fora do piso do bolso (era 189: a bola ficava no limite de cair)


def rampa(g, m: M):
    e = m.el
    Rr, n, pt = m.plano_rampa()
    zr = e.z_rampa
    tr = math.tan(math.radians(e.incl_rampa))
    zt = lambda x, y: m.z_rampa(x, y)
    # piso inteiro de Y 88 a 128; no bolso (Y 60..88) so de X 186 a 206 (a bola sai pela esquerda, por cima, presa no ima)
    zb0 = zr - 70 * tr - 6
    # piso macico (impresso em pe sem suporte): embaixo da placa do piso, ate a base da rampa
    placa_plano(g, "rampa", "mundo", 177.0, 206.6, 88, 127.7, 3, Rr, zt, "Rampa", "preto")
    placa_plano(g, "rampa_bolso", "mundo", X_BOLSO, 206.6, 60, 88, 3, Rr, zt, "Rampa", "preto")
    # macico com o topo seguindo o piso (0,1 mm dentro dele); o STL corta embaixo em Z = zb0 (base plana)
    for nm, x0, x1, y0, y1 in (("rampa_macico", 177.0, 206.6, 88, 126.8), ("rampa_macico_bolso", X_BOLSO, 206.6, 60, 88.5),
                               ("rampa_macico_fim", X_BOLSO, 206.6, 54.6, 60.5)):
        topo = (lambda x, y: m.z_rampa(x, y) - 2.9) if nm != "rampa_macico_fim" else (lambda x, y: m.z_rampa(x, y) - 4.5)
        esp = max(topo(x, y) for x in (x0, x1) for y in (y0, y1)) - zb0
        placa_plano(g, nm, "mundo", x0, x1, y0, y1, esp, Rr, topo, "Rampa", "preto")
    caixa(g, "rampa_esq", "mundo", 175.5, 177.5, 88, 128, zb0, zr + 22, "Rampa", "transp")
    caixa(g, "rampa_dir", "mundo", 206.0, 208.0, 58, 128, zb0, zr + 22, "Rampa", "transp")
    caixa(g, "rampa_fim", "mundo", X_BOLSO, 206.0, 51, 55, zb0, zr + 22, "Rampa", "acento")
    caixa(g, "eva_bolso", "mundo", X_BOLSO, 206.0, 55, 60, m.z_rampa(197, 60) - 2, zr + 14, "EVA 5 mm", "eva")
    caixa(g, "rampa_fim_lado", "mundo", 206.0, 208.0, 51, 58, zb0, zr + 22, "Rampa", "transp")
    # abas de tras: 2 M3 em rasgos verticais em cada pilar da torre (a rampa sobe/desce +-4 mm para acertar a pega)
    caixa(g, "rampa_aba_esq", "mundo", 165.0, 177.5, 125.0, 128.0, zb0, zr + 22, "Rampa", "preto")
    caixa(g, "rampa_aba_dir", "mundo", 206.0, 217.0, 125.0, 128.0, zb0, zr + 22, "Rampa", "preto")
    zs_top = m.z_rampa(SENSOR_BOLSO[0], SENSOR_BOLSO[1]) - 1.0
    caixa(g, "sensor_bolso", "mundo", SENSOR_BOLSO[0] - 2.9, SENSOR_BOLSO[0] + 2.9, SENSOR_BOLSO[1] - 5.1,
          SENSOR_BOLSO[1] + 5.1, zs_top - 7.0, zs_top, "Sensor do bolso", "metal")


Z_PAREDE_ALTA = 80.0
ENTALHE = (30.0, 42.0, 9.0)       # passagem de cabos no piso, por baixo da fila (X 30..42, ate Z 9)
SENSOR_BOLSO = (198.5, 72.7)     # TCRT5000: 3,7 mm a direita de onde a bola encosta no piso (fica 1 mm abaixo da bola)


def fila(g, m: M):
    """Fila da direita (X -30..175,5: a do elevador, mais comprida) e da esquerda (X -217..-30)."""
    e = m.el
    Rf4, Rf3 = rot(ry=I_FILA_D), rot(ry=I_FILA_E)
    y0, y1 = 130.0, 130.0 + e.larg_fila
    # ---- direita
    placa_plano(g, "fila_piso", "mundo", -30, e.x_fila_fim, y0, y1, 3, Rf4,
                lambda x, y: m.f_fila(x), "Fila", "preto")
    _entalhada(g, "fila_fundo", -30, 171.5, y1, y1 + 1.6, 0, 105, "Fila", "preto")
    caixa(g, "fila_fundo_fim", "mundo", 171.5, 175.5, y1, y1 + 2, 5.5, 105, "Fila", "preto")
    _entalhada(g, "fila_frente_baixo", m.x_entrada, 171.5, 128, 130, 0, 25, "Fila", "transp")
    caixa(g, "fila_frente", "mundo", m.x_entrada, 175.5, 128, 130, 25, Z_PAREDE_ALTA, "Fila", "transp")
    lab_min = m.z_labio(m.x_entrada)
    _entalhada(g, "fila_labio_base", -30, m.x_entrada, 128, 130, 0, lab_min - 3, "Fila", "transp")
    placa_plano(g, "fila_labio", "mundo", -29.4, m.x_entrada, 128, 130, 10, Rf4, lambda x, y: m.z_labio(x), "Fila", "transp")
    for i, x0 in enumerate((-28.0, 150.0)):
        caixa(g, f"fila_pe_{i}", "mundo", x0, x0 + 12, y1 + 1.5, y1 + 10, 0, 4, "Fila", "preto")
    for i, x in enumerate(np.arange(-24.0, 169.0, 24.0)):
        caixa(g, f"fila_nerv_{i}", "mundo", x - 0.8, x + 0.8, y0, y1, 0, m.f_fila(x + 1) - 2.6, "Fila", "preto")
    # ---- esquerda
    placa_plano(g, "filaE_piso", "mundo", -217, -30, y0, y1, 3, Rf3, lambda x, y: m.f_fila(x), "Fila esquerda", "preto")
    caixa(g, "filaE_fundo", "mundo", -217, -30, y1, y1 + 1.6, 0, 105, "Fila esquerda", "preto")
    caixa(g, "filaE_inicio", "mundo", -219, -217, 128, y1 + 2, 0, 105, "Fila esquerda", "preto")
    lab_e = m.z_labio(-30)
    caixa(g, "filaE_labio_base", "mundo", -217, -30, 128, 130, 0, lab_e - 3, "Fila esquerda", "transp")
    placa_plano(g, "filaE_labio", "mundo", -217, -30.6, 128, 130, 14, Rf3, lambda x, y: m.z_labio(x), "Fila esquerda",
                "transp")
    for i, x0 in enumerate((-210.0, -55.0)):
        caixa(g, f"filaE_pe_{i}", "mundo", x0, x0 + 12, y1 + 1.5, y1 + 10, 0, 4, "Fila esquerda", "preto")
    for i, x in enumerate(np.arange(-210.0, -35.0, 24.0)):
        caixa(g, f"filaE_nerv_{i}", "mundo", x - 0.8, x + 0.8, y0, y1, 0, m.f_fila(x + 1) - 2.6, "Fila esquerda", "preto")


def _entalhada(g, nome, x0, x1, y0, y1, z0, z1, pc, cor, ent=None):
    """Caixa com a passagem de cabos (entalhe embaixo, em X ENTALHE) quando ela cruza a caixa."""
    ex0, ex1, ez = ent or ENTALHE
    if x1 <= ex0 or x0 >= ex1 or z0 >= ez:
        caixa(g, nome, "mundo", x0, x1, y0, y1, z0, z1, pc, cor)
        return
    if x0 < ex0:
        caixa(g, nome + "_a", "mundo", x0, ex0, y0, y1, z0, z1, pc, cor)
    caixa(g, nome + "_b", "mundo", max(x0, ex0), min(x1, ex1), y0, y1, ez, z1, pc, cor)
    if x1 > ex1:
        caixa(g, nome + "_c", "mundo", ex1, x1, y0, y1, z0, z1, pc, cor)


def eixo_linear(g, m: M, k):
    """Perfil, trilho, blocos de ponta, motor com suporte, polias, correia e fim de curso de um eixo."""
    zp = m.zpA if k == "A" else m.zpB
    zc = zp + m.dz_correia
    ya, yb = m.y_perfil
    h = m.L_perfil / 2
    rp = 20 * 2 / (2 * math.pi)
    caixa(g, f"perfil_{k}", "mundo", -h, h, ya, yb, zp - 10, zp + 10, f"Perfil 2020 {k}", "metal")
    caixa(g, f"trilho_{k}", "mundo", -h, h, yb, yb + 8, zp - 6, zp + 6, f"Trilho MGN12 {k}", "metal")
    # blocos de ponta: corpo na parede + luva em volta do perfil (frente, cima e baixo; atras fica o trilho)
    for lado, s in (("esq", -1), ("dir", 1)):
        pc = "Bloco esquerdo" if s < 0 else "Bloco direito"
        x_par, x_ini = GX * s, 200 * s
        xa, xb = sorted((x_par, x_ini))
        y_fim = 46.0 if s < 0 else 44.0
        caixa(g, f"bloco_{lado}_{k}", "mundo", xa, xb, 4, y_fim, zp - 14, zp + 14, pc, "preto")
        xl0, xl1 = sorted((x_ini, 188 * s))
        caixa(g, f"luva_frente_{lado}_{k}", "mundo", xl0, xl1, 4, ya, zp - 14, zp + 14, pc, "preto")
        caixa(g, f"luva_cima_{lado}_{k}", "mundo", xl0, xl1, ya, yb, zp + 10, zp + 14, pc, "preto")
        caixa(g, f"luva_baixo_{lado}_{k}", "mundo", xl0, xl1, ya, yb, zp - 14, zp - 10, pc, "preto")
        if s < 0:
            # fim de curso da CASA: KW10 de pe (19,8 em Z), 10,2 em X com a alavanca para +X, 6,4 em Y; a face
            # esquerda da presilha do carro (X c-28) aperta a alavanca na casa (c = -146)
            xe = m.c_casa + FIX[0] - 2                    # face esquerda da presilha na casa (X -174)
            caixa(g, f"bloco_braco_{k}", "mundo", -GX, xe - 2.0, 38.4, 44.4, zp - 30, zp - 10, pc, "preto")
            caixa(g, f"fdc_{k}", "mundo", xe - 12.2, xe - 2.0, 32, 38.4, zp - 30, zp - 10.2, "Fim de curso", "metal")
            caixa(g, f"fdc_alav_{k}", "mundo", xe - 2.0, xe + 0.5, 33, 37, zp - 24, zp - 21, "Fim de curso", "metal")
        else:
            # bracos da polia tensora (eixo vertical M5), com rasgo de 6 mm em X para esticar
            caixa(g, f"tens_alma_{k}", "mundo", 200, GX, 13, 30, zc - 11.0, zp - 14, pc, "preto")
            caixa(g, f"tens_cima_{k}", "mundo", 185, 200, 13, 30, zc + 5.0, zc + 8.0, pc, "preto")
            caixa(g, f"tens_baixo_{k}", "mundo", 185, 200, 13, 30, zc - 11.0, zc - 5.5, pc, "preto")
            # fim de curso de SEGURANCA (fim do trilho): a face direita da presilha passa 0,8 mm da alavanca na pega
            # e aperta a alavanca se o carro passar dela (nunca no jogo normal)
            xd = m.x_fdc_dir
            caixa(g, f"bloco_braco_dir_{k}", "mundo", xd + 2.5, GX, 38.4, 44.4, zp - 35, zp - 17, pc, "preto")
            caixa(g, f"bloco_braco_dir_liga_{k}", "mundo", 210.0, GX, 30, 38.4, zp - 35, zp - 14, pc, "preto")
            caixa(g, f"fdc_dir_{k}", "mundo", xd + 2.5, xd + 12.7, 32, 38.4, zp - 35, zp - 15.2, "Fim de curso", "metal")
            caixa(g, f"fdc_dir_alav_{k}", "mundo", xd, xd + 2.5, 33, 37, zp - 29, zp - 26, "Fim de curso", "metal")
    # motor (eixo para cima) + suporte
    xm = m.x_motor
    zf = zc - 15.0                       # face do motor
    caixa(g, f"motor_{k}", "mundo", xm - 21.15, xm + 21.15, m.y_correia - 21.15, m.y_correia + 21.15, zf - 40, zf,
          f"NEMA 17 {k}", "metal")
    cil(g, f"polia_{k}", "mundo", (xm, m.y_correia, zc), 8.0, 8.0, "z", f"Polia GT2 20T {k}", "metal")
    cil(g, f"eixo_motor_{k}", "mundo", (xm, m.y_correia, zf + 4), 2.5, 4.0, "z", f"NEMA 17 {k}", "metal")
    pc = f"Suporte do NEMA {'de cima' if k == 'A' else 'de baixo'}"
    caixa(g, f"sup_nema_placa_{k}", "mundo", -215.5, -172, m.y_correia - 21.15, m.y_correia + 21.15, zf, zf + 4, pc, "preto")
    if k == "A":
        caixa(g, f"sup_nema_aba_{k}", "mundo", -GX, -215.5, m.y_correia - 21.15, m.y_correia + 21.15, zf - 72, zf + 4, pc,
              "preto")
        caixa(g, f"sup_nema_nerv_{k}", "mundo", -215.5, -180, m.y_correia + 21.15, m.y_correia + 25.0, zf - 30, zf + 4, pc,
              "preto")
    else:
        caixa(g, f"sup_nema_aba_{k}", "mundo", -GX, -215.5, m.y_correia - 21.15, m.y_correia + 21.15, 0, zf + 4, pc, "preto")
        caixa(g, f"sup_nema_pe_{k}", "mundo", -215.5, -175, m.y_correia + 21.15, m.y_correia + 29.5, 0, 4, pc, "preto")
        caixa(g, f"sup_nema_aba2_{k}", "mundo", -GX, -215.5, m.y_correia + 21.15, m.y_correia + 28.5, 0, zf + 4, pc,
              "preto")
    # tensora
    cil(g, f"tensora_{k}", "mundo", (m.x_tensora, m.y_correia, zc), 9.0, 4.25, "z", f"Polia tensora {k}", "metal")
    cil(g, f"eixo_tens_{k}", "mundo", (m.x_tensora, m.y_correia, zc), 2.5, 9.5, "z", f"Polia tensora {k}", "metal")
    # correia (ramo de tras preso no carro: desenhada fixa, a presilha entra nela)
    for ramo, yr in (("frente", m.y_correia - rp), ("tras", m.y_correia + rp)):
        caixa(g, f"correia_{ramo}_{k}", "mundo", xm, m.x_tensora, yr - 0.7, yr + 0.7, zc - 3, zc + 3, f"Correia {k}",
              "correia")


def patim(g, corpo, zp, k):
    caixa(g, f"patim_topo_{k}", corpo, -22.7, 22.7, 36.2, 41, zp - 13.5, zp + 13.5, f"Patim MGN12H {k}", "metal")
    caixa(g, f"patim_fl1_{k}", corpo, -22.7, 22.7, 31, 36.2, zp + 6.4, zp + 13.5, f"Patim MGN12H {k}", "metal")
    caixa(g, f"patim_fl2_{k}", corpo, -22.7, 22.7, 31, 36.2, zp - 13.5, zp - 6.4, f"Patim MGN12H {k}", "metal")


FIX = (-26.0, 14.0)              # fixador de correia (aluminio 40 x 9 x 5, face 40 x 9 dentada) em X do carro
FIX_E = 5.0                      # espessura do fixador (Y)
BATEDOR_B = (FIX[1] + 2, 37.0)    # batedor do carro B (X relativo ao patim)


def presilha(g, corpo, zc, k, pc):
    """Presilha da correia embaixo do patim, para o fixador de aluminio 40 x 9 x 5 (comprado). O fixador fica EM PE,
    com a face dentada direto na face dentada do ramo de tras da correia; 1 M3x16 atravessa o fixador (entre as duas
    pontas da correia, que se encontram no meio) e a porca presa na presilha puxa tudo: a correia fica apertada entre
    os dentes de aluminio e a parede lisa da presilha."""
    yr = 22.0 + 20 * 2 / (2 * math.pi)                  # ramo de tras (Y 28,37): dentes para -Y, costas para +Y
    yp = yr + 0.7                                       # parede = costas da correia
    caixa(g, f"presilha_piso_{k}", corpo, FIX[0] - 2, FIX[1] + 2, 17.5, yp, zc - 8.5, zc - 4.8, pc, "acento")
    caixa(g, f"presilha_{k}", corpo, FIX[0] - 2, FIX[1] + 2, yp, 41, zc - 8.5, zc + 5.0, pc, "acento")
    caixa(g, f"ponte_{k}", corpo, -8, 8, yp, 41, zc + 5.0, zc + 8.1, pc, "acento")
    caixa(g, f"fixador_{k}", corpo, FIX[0], FIX[1], yr - 0.7 - FIX_E, yr - 0.7, zc - 4.5, zc + 4.5, "Fixador de correia",
          "metal")


def carro_a(g, m: M):
    """Corpo 'carroA' no referencial do centro do patim (x = 0)."""
    zp, f = m.zpA, m.face_ima
    pc = "Carro A"
    patim(g, "carroA", zp, "A")
    e = m.arruela_e
    caixa(g, "placaA", "carroA", -22, 30, 41, 46, f + e + 15, zp + 13.5, pc, "acento")
    caixa(g, "prateleiraA", "carroA", m.dA - 12, m.dA + 12, 46, m.y_bola + 12.3, f + e + 15, f + e + 20, pc, "acento")
    caixa(g, "nervuraA", "carroA", m.dA - 14, m.dA - 10.5, 46, 62, f + e + 3, f + e + 15, pc, "acento")
    # copo: abraca o ima e a arruela; o fundo dele fica no mesmo plano da arruela (nada desce alem dela)
    anel(g, "copoA", "carroA", (m.dA, m.y_bola), 10.2, 11.9, f, f + e + 15, pc, "acento")
    anel(g, "arruela", "carroA", (m.dA, m.y_bola), m.arruela_furo / 2, 10.0, f, f + e, "Arruela M10 de aco", "metal")
    presilha(g, "carroA", zp + m.dz_correia, "A", pc)
    caixa(g, "ponta_estA", "carroA", -22, -14, 46, 46 + m.est_h + 1, 401 + m.dZ, 400.5 + m.dZ + m.est_w, pc, "acento")
    cil(g, "ima", "carroA", (m.dA, m.y_bola, f + m.arruela_e + 7.5), 10.0, 7.5, "z", "Eletroima P20/15", "metal")


def carro_b(g, m: M):
    zp = m.zpB
    zb = m.zb
    yb = m.y_bola
    pc = "Carro B"
    patim(g, "carroB", zp, "B")
    caixa(g, "placaB", "carroB", -22, 22, 41, 46, 49, zb - 6, pc, "acento")
    pa = "Anel"
    caixa(g, "bracoB", "carroB", -12, 12, 46, yb - m.r_tubo + 1.0, zb - m.h_anel, zb - 6, pa, "anel")
    caixa(g, "costasB", "carroB", -20, 20, 46, 50, 50, zb, pa, "anel")
    anel(g, "anel_flange", "carroB", (0, yb), m.r_furo, m.r_flange, zb - 6, zb, pa, "anel")
    anel(g, "anel_tubo", "carroB", (0, yb), m.r_furo, m.r_tubo, zb - m.h_anel, zb - 6, pa, "anel")
    for lado, s in (("esq", -1), ("dir", 1)):
        x0, x1 = sorted((s * (m.r_tubo - 1.0), s * 31.0))
        caixa(g, f"ir_{lado}", "carroB", x0, x1, yb - 5, yb + 5, zb - 21, zb, pa, "anel")
        cil(g, f"led_{lado}", "carroB", (s * 27.5, yb, zb - 14.5), 2.5, 3.5, "x", "LED IR / fototransistor 5 mm", "metal")
    presilha(g, "carroB", zp + m.dz_correia, "B", pc)
    # barra ate a esteira de baixo (Y 1..11, ramo de cima em Z 36,5..47,5)
    caixa(g, "barra_estB", "carroB", 12, 20, 1, 41, 49, 54.5, pc, "acento")
    caixa(g, "ponta_estB", "carroB", 12, 20, 1, 41, 36.5 - 0.5, 49, pc, "acento")
    # batedor do fim de curso de seguranca: o bloco direito e igual nos 2 eixos, entao o carro B (que para em +120)
    # aperta a mesma alavanca 21 mm antes, longe da tensora
    zc = zp + m.dz_correia
    caixa(g, "batedorB", "carroB", FIX[1] + 2, BATEDOR_B[1], 31.0, 40.0, zc - 8.5, zc + 2.0, pc, "acento")


def bandeja(g, m: M):
    """Placas em pe na impressao: frente ate o piso, nervuras-parede ate o piso (sem pes soltos), laterais."""
    ya, yb = m.y_bandeja
    yf = ya + 2.0                              # face de tras da parede da frente
    nomes = ("Bandeja esquerda", "Bandeja do meio", "Bandeja direita")
    xs = m.x_juntas
    for i, pc in enumerate(nomes):
        x0, x1 = xs[i], xs[i + 1]
        ax = -T_BXE if x1 <= -30 else T_BX    # dS/dx
        top = lambda x, y, s=m: s.s_bandeja(x, y) - s.eva
        n = np.array([-ax, T_BY, 1.0])          # normal do plano S
        Rm = _R_normal(n / np.linalg.norm(n))
        placa_plano(g, f"band_placa_{i}", "mundo", x0 + 0.25, x1 - 0.25, yf, yb, m.e_placa, Rm, top, pc, "preto")
        placa_plano(g, f"band_eva_{i}", "mundo", x0 + 0.25, x1 - 0.25, yf, yb, m.eva, Rm,
                    lambda x, y, s=m: s.s_bandeja(x, y), "EVA 5 mm", "eva")
        # labio da frente: da placa ate 18 mm acima do EVA (segura o quique para a frente)
        s_f = [m.s_bandeja(x, ya) for x in (x0, x1)]
        caixa(g, f"band_frente_{i}", "mundo", x0 + 0.25, x1 - 0.25, ya, yf, min(s_f) - m.eva - m.e_placa - 1.0,
              max(s_f) + 18.0, pc, "transp")
        for j, x in enumerate(NERVURAS[i]):
            _nervura(g, m, f"band_nerv_{i}_{j}", x, ya, yb, pc)
        for j, x in enumerate(ABAS_BANDEJA[i]):
            caixa(g, f"band_aba_{i}_{j}", "mundo", x - 2, x + 10, ya, yf + 9, 0, 4, pc, "preto")
    _nervura(g, m, "band_lado_esq", xs[0] - 0.75, ya, yb, "Bandeja esquerda", larg=2.5, topo=100)
    # a direita, de Y 112 em diante quem segura a bola e a orelha da torre
    _nervura(g, m, "band_lado_dir", xs[-1] + 1.0, ya, EL.Y_ORELHA[0] - 0.5, "Bandeja direita", larg=2.5, topo=100)


def _nervura(g, m, nome, x, y0, y1, pc, larg=1.6, topo=None):
    """Parede em X = x, do piso ate embaixo da placa (topo segue a placa), com recortes onde ha coisa no piso."""
    trechos = [(y0, y1, 0.0)]
    if x < -164:                               # pe do suporte do NEMA de baixo (Y ate 51,5, Z ate 4)
        trechos = [(y0, 52.0, 4.5), (52.0, y1, 0.0)]
    if 82 <= x <= 181:                         # servo, chifre e braco da comporta
        trechos = [(y0, 86.0, 0.0), (86.0, y1, 35.0)]
    if x >= 186:                               # pe da torre (aba da frente com 2 parafusos)
        trechos = [(y0, 110.0, 0.0), (110.0, y1, 9.5)]
    if ENTALHE[0] - 1 <= x <= ENTALHE[1] + 1:  # passagem de cabos no piso
        trechos = [(a, b, max(z, ENTALHE[2])) for a, b, z in trechos]
    for k, (ya, yb, z0) in enumerate(trechos):
        zbaixo = min(m.s_bandeja(x, y) for y in (ya, yb)) - m.eva - m.e_placa
        nm = f"{nome}_{k}" if len(trechos) > 1 else nome
        if topo is None:
            caixa(g, nm, "mundo", x - larg / 2, x + larg / 2, ya, yb, z0, zbaixo - 1.0, pc, "preto")
            Rm = rot(rx=-math.degrees(math.atan(T_BY)))
            placa_plano(g, nm + "_topo", "mundo", x - larg / 2, x + larg / 2, ya + 0.6, yb, 6.0, Rm,
                        lambda xx, yy, s=m, xc=x: s.s_bandeja(xc, yy) - s.eva - s.e_placa + 0.4, pc, "preto")
        else:
            caixa(g, nm, "mundo", x - larg / 2, x + larg / 2, ya, yb, z0, topo, pc, "transp")


NERVURAS = ((-185.0, -150.0, -115.0, -80.0, -36.0),
            (-24.0, 12.0, 48.0, 84.0, 116.0),
            (124.0, 160.0, 183.0, 201.0))
# abas no piso: cada uma nasce numa nervura (x da nervura); o parafuso fica 5 mm a direita dela
ABAS_BANDEJA = ((-150.0, -80.0), (12.0, 84.0), (124.0, 183.0))


GANCHOS = (-175.0, 0.0, 150.0)


def _R_normal(n):
    """Rotacao que leva Z em n mantendo X no plano XZ (placas da bandeja)."""
    z = n / np.linalg.norm(n)
    x = np.array([1.0, 0, 0]) - z[0] * z
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return np.stack([x, y, z], 1)


def suporte_esteira(g, m: M):
    """Prateleira da esteira A (pendurada no teto) e pontas fixas das duas esteiras."""
    xa, xb = -185.0, 185.0
    d = m.dZ
    # dois trilhos (um embaixo de cada ramo da esteira) + travessas a cada ~46 mm
    for i, (x0, x1) in enumerate(((xa, 0), (0, xb))):
        caixa(g, f"prat_estA_{i}", "mundo", x0, x1, 47, 60, 397 + d, 400 + d, "Prateleira da esteira", "preto")
        caixa(g, f"prat_estA_{i}_fora", "mundo", x0, x1, 84, 98, 397 + d, 400 + d, "Prateleira da esteira", "preto")
        for j, x in enumerate(np.linspace(x0 + 3, x1 - 3, 5)):
            caixa(g, f"prat_estA_{i}_trav_{j}", "mundo", x - 3, x + 3, 60, 84, 397 + d, 400 + d, "Prateleira da esteira", "preto")
    for i, (x0, x1) in enumerate(((xa, 0), (0, xb))):
        caixa(g, f"prat_aba_{i}", "mundo", x0, x1, 98, 104, 397 + d, 410 + d, "Prateleira da esteira", "preto")
    for i, x in enumerate(GANCHOS):
        caixa(g, f"gancho_{i}", "mundo", x - 8, x + 8, 104, 108, 397 + d, GZ, "Gancho da prateleira", "preto")
        caixa(g, f"gancho_pe_{i}", "mundo", x - 7.5, x + 7.5, 108, 119, GZ - 4, GZ, "Gancho da prateleira", "preto")
    xf = esteira_fixos(m)
    caixa(g, "est_fixaA", "mundo", xf["A"] - 12, xf["A"], 98 - m.est_h - 1, 98, 400.5 + d, 400.5 + d + m.est_w,
          "Ponta fixa da esteira", "acento")
    caixa(g, "est_fixaB", "mundo", xf["B"] - 12, xf["B"], 0.5, 11.5, 0, 0.5 + m.est_h + 1, "Ponta fixa da esteira",
          "acento")
    caixa(g, "est_fixaB_aba", "mundo", xf["B"] - 26, xf["B"] - 12, 0.5, 11.5, 0, 4, "Ponta fixa da esteira", "acento")


# ===================================================================== esteiras (dependem da posicao dos carros)
def esteira_fixos(m: M):
    mA = (m.cA[0] - 14, m.cA[1] - 14)
    mB = (m.cB[0] + 20, m.cB[1] + 20)
    return {"A": (mA[0] + mA[1]) / 2, "B": (mB[0] + mB[1]) / 2}


def esteira_caixas(m: M, k, c):
    """Caixas da esteira com o patim em c: ramo movel, ramo fixo e a curva (8 segmentos)."""
    xf = esteira_fixos(m)[k]
    if k == "A":
        lo, hi = m.cA[0] - 14, m.cA[1] - 14
        xm = c - 14
    else:
        lo, hi = m.cB[0] + 20, m.cB[1] + 20
        xm = c + 20
    kk = (hi - xf) / 2 + 5
    xu = (xf + xm) / 2 + kk
    out = []
    h, w = m.est_h, m.est_w
    if k == "A":
        Rc, z0 = m.RcA, 400.5 + m.dZ
        y_in, y_out = 47 + h / 2, 47 + h / 2 + 2 * Rc
        out.append(("est_movA", xm, xu, y_in - h / 2, y_in + h / 2, z0, z0 + w))
        out.append(("est_fixA", xf, xu, y_out - h / 2, y_out + h / 2, z0, z0 + w))
        yc = (y_in + y_out) / 2
        for i in range(8):
            a0, a1 = -math.pi / 2 + i * math.pi / 8, -math.pi / 2 + (i + 1) * math.pi / 8
            am = (a0 + a1) / 2
            px, py = xu + Rc * math.cos(am), yc + Rc * math.sin(am)
            out.append((f"est_curvaA_{i}", px, py, am, Rc * math.pi / 8 + 1, h, (z0, z0 + w), "xy"))
    else:
        Rc, y0 = m.RcB, 0.5
        z_in, z_out = 36.5 + h / 2, 36.5 + h / 2 - 2 * Rc
        out.append(("est_movB", xm, xu, y0, y0 + w, z_in - h / 2, z_in + h / 2))
        out.append(("est_fixB", xf, xu, y0, y0 + w, z_out - h / 2, z_out + h / 2))
        zc = (z_in + z_out) / 2
        for i in range(8):
            a0, a1 = -math.pi / 2 + i * math.pi / 8, -math.pi / 2 + (i + 1) * math.pi / 8
            am = (a0 + a1) / 2
            px, pz = xu + Rc * math.cos(am), zc + Rc * math.sin(am)
            out.append((f"est_curvaB_{i}", px, pz, am, Rc * math.pi / 8 + 1, h, (y0, y0 + w), "xz"))
    g = []
    for it in out:
        if len(it) == 7:
            nm, x0, x1, a, b, c0, c1 = it
            x0, x1 = sorted((x0, x1))
            caixa(g, nm, "esteira" + k, x0, x1, a, b, c0, c1, f"Esteira {k}", "correia")
        else:
            nm, p1, p2, am, comp, hh, (s0, s1), plano = it
            if plano == "xy":
                Rm = rot(rz=math.degrees(am) + 90)
                g.append(dict(nome=nm, corpo="esteira" + k, tipo="box", meio=[comp / 2, hh / 2, (s1 - s0) / 2],
                              pos=[p1, p2, (s0 + s1) / 2], quat=EL.quat(Rm), grupo="fixa", peca=f"Esteira {k}",
                              cor="correia"))
            else:
                Rm = rot(ry=-(math.degrees(am) + 90))
                g.append(dict(nome=nm, corpo="esteira" + k, tipo="box", meio=[comp / 2, (s1 - s0) / 2, hh / 2],
                              pos=[p1, (s0 + s1) / 2, p2], quat=EL.quat(Rm), grupo="fixa", peca=f"Esteira {k}",
                              cor="correia"))
    return g, dict(xf=xf, xu=xu, comprimento=2 * kk + math.pi * Rc)


# ===================================================================== pecas
PECAS_NOVAS = {
    # peca: (tipo, material/modelo, etapa, como fixa)
    "Tela": ("existente", "tela no fundo (Y 230)", 0, "nada encosta nela"),
    "Rampa": ("impressa", "PETG preto", 9, "2 abas atras com 4 M3x12 + porca presa nos pilares da torre; os furos sao rasgos "
                                         "de +-4 mm: suba ou desca a rampa ate a bola quase encostar na arruela do ima"),
    "Fila": ("impressa", "PETG preto", 8, "a do elevador, mais comprida ate X -30; 2 parafusos de madeira 3,5x16 nos pes de tras"),
    "Fila esquerda": ("impressa", "PETG preto", 14, "encosta na fila da direita em X -30; 2 parafusos de madeira 3,5x16 nos pes"),
    "Bloco esquerdo": ("impressa", "PETG preto", 9, "2 parafusos de madeira 3,5x16 na parede esquerda; 2 M5x10 + porca martelo no perfil; "
                                                     "fim de curso da casa (KW10) com 2 M2x12"),
    "Bloco direito": ("impressa", "PETG preto", 9, "2 parafusos de madeira 3,5x16 na parede direita; 2 M5x10 + porca martelo no perfil; "
                                                    "fim de curso de seguranca (KW10) com 2 M2x12"),
    "Perfil 2020 A": ("comprada", "perfil 2020 da maquina antiga, cortado em 400 mm", 10, "nas luvas dos blocos"),
    "Perfil 2020 B": ("comprada", "perfil 2020 da maquina antiga, cortado em 400 mm", 10, "nas luvas dos blocos"),
    "Trilho MGN12 A": ("comprada", "MGN12 de 400 mm da maquina antiga (sem cortar)", 10, "16 M3x8 + porca martelo M3 na fenda de tras"),
    "Trilho MGN12 B": ("comprada", "MGN12 de 400 mm da maquina antiga (sem cortar)", 10, "16 M3x8 + porca martelo M3 na fenda de tras"),
    "Patim MGN12H A": ("comprada", "vem no trilho", 10, "nunca tirar do trilho"),
    "Patim MGN12H B": ("comprada", "vem no trilho", 10, "nunca tirar do trilho"),
    "NEMA 17 A": ("comprada", "NEMA 17 da maquina antiga + TMC2209 (fora do gabinete)", 11, "4 M3x8 na placa do suporte"),
    "NEMA 17 B": ("comprada", "NEMA 17 da maquina antiga + TMC2209 (fora do gabinete)", 11, "4 M3x8 na placa do suporte"),
    "Suporte do NEMA de cima": ("impressa", "PETG preto", 11, "aba com 3 parafusos de madeira 3,5x16 na parede esquerda"),
    "Suporte do NEMA de baixo": ("impressa", "PETG preto", 8, "pe com 2 parafusos de madeira 3,5x16 no piso e 2 na parede"),
    "Polia GT2 20T A": ("comprada", "GT2 20T furo 5 (maquina antiga)", 11, "parafuso sem cabeca no lado chato do eixo"),
    "Polia GT2 20T B": ("comprada", "GT2 20T furo 5 (maquina antiga)", 11, "parafuso sem cabeca no lado chato do eixo"),
    "Polia tensora A": ("comprada", "tensora GT2 20T furo 5 com rolamento (maquina antiga)", 11, "M5x25 + porca nylon nos bracos do bloco direito"),
    "Polia tensora B": ("comprada", "tensora GT2 20T furo 5 com rolamento (maquina antiga)", 11, "M5x25 + porca nylon nos bracos do bloco direito"),
    "Correia A": ("comprada", "GT2 6 mm aberta, ~840 mm", 12, "as 2 pontas no fixador de aluminio do carro A"),
    "Correia B": ("comprada", "GT2 6 mm aberta, ~840 mm", 12, "as 2 pontas no fixador de aluminio do carro B"),
    "Carro A": ("impressa", "PETG preto", 12, "4 M3x8 no patim; eletroima no copo com 1 M3x8 por cima; arruela colada na face do ima; "
                                             "fixador de correia em pe, 1 M3x16 de frente + porca presa na presilha"),
    "Fixador de correia": ("comprada", "fixador de correia de aluminio 40 x 9 x 5 com dentes GT2, 1 por carro", 12,
                           "em pe, face dentada direto na face dentada da correia; 1 M3x16 de frente pelo furo do meio, porca M3 presa na presilha; a correia fica apertada contra a parede lisa"),
    "Arruela M10 de aco": ("comprada", "arruela lisa M10 de aco (DIN 125: 20 x 10,5 x 2), NAO inox", 12,
                           "colada (super cola ou epoxi) na face do eletroima, dentro do copo do carro A"),
    "Eletroima P20/15": ("comprada", "eletroima 12 V P20/15 (voces ja tem); a arruela de aco vai colada na face", 12,
                         "entra no copo do carro A por baixo; 1 M3x8 na rosca do topo"),
    "Carro B": ("impressa", "PETG preto", 12, "4 M3x8 no patim; o anel prende atras com 4 M3x12 + porca; fixador de correia em pe, 1 M3x16 de frente + porca presa na presilha"),
    "Anel": ("impressa", "PETG preto", 13, "costas com 4 M3x12 + porca na placa do carro B; LED IR e fototransistor de 5 mm nos furos laterais"),
    "LED IR / fototransistor 5 mm": ("comprada", "par de barreira infravermelha 5 mm com cabo (emissor + receptor com saida digital)", 12,
                                     "entram justos nos furos do anel, com uma gota de cola quente"),
    "Sensor do bolso": ("comprada", "TCRT5000 (so o componente, 10 x 6 x 7 mm) ou o modulo sem a placa", 9,
                        "entra por baixo no bolso da rampa, olhando para cima pela janela; uma gota de cola quente"),
    "Fim de curso": ("comprada", "microchave KW10: 4 (casa e seguranca em cada eixo)", 9, "2 M2x12 de lado no braco do bloco"),
    "Esteira A": ("comprada", "esteira porta-cabo 7x7, ~250 mm", 13, "ponta movel no carro A, ponta fixa na prateleira"),
    "Esteira B": ("comprada", "esteira porta-cabo 7x7, ~210 mm", 13, "ponta movel no carro B, ponta fixa no piso"),
    "Prateleira da esteira": ("impressa", "PETG preto", 13, "2 metades, 2 M3x10 em cada gancho"),
    "Gancho da prateleira": ("impressa", "PETG preto", 13, "2 parafusos de madeira 3,5x16 no teto"),
    "Ponta fixa da esteira": ("impressa", "PETG preto", 13, "A: 2 M3x16 + porca na prateleira; B: 2 parafusos de madeira no piso"),
    "Bandeja esquerda": ("impressa", "PETG preto", 14, "4 pes; 2 parafusos de madeira 3,5x16 no piso"),
    "Bandeja do meio": ("impressa", "PETG preto", 14, "5 pes; 2 parafusos de madeira 3,5x16 no piso"),
    "Bandeja direita": ("impressa", "PETG preto", 14, "4 pes; 2 parafusos de madeira 3,5x16 no piso"),
    "EVA 5 mm": ("comprada", "folha de EVA 5 mm: 3 pedacos por cima das placas da bandeja + 1 tira no batente do bolso",
                 14, "cola de contato"),
}
PECAS = dict(EL.PECAS)
PECAS.update(PECAS_NOVAS)


# ===================================================================== fixadores
def fixadores(m: M):
    e = m.el
    f = []

    def add(nome, tipo, p0, d, L, prende, rosca, etapa, acesso=(), insert=None, cab=5.5, atravessa=(), corpo="mundo",
            bancada=False, corredor=120.0, rasgo=None, rasgo_c=None):
        f.append(dict(nome=nome, tipo=tipo, p0=[float(v) for v in p0], dir=list(d), L=L, prende=prende, rosca=rosca,
                      etapa=etapa, acesso=list(acesso), insert=insert, cab=cab, atravessa=list(atravessa), corpo=corpo,
                      bancada=bancada, corredor=corredor, rasgo=rasgo, rasgo_c=rasgo_c))

    # elevador (tirando os que mudaram)
    for x in EL.fixadores(e):
        x = dict(x)
        x["rosca"] = "Gabinete" if x["rosca"] == "Bancada" else x["rosca"]
        x["acesso"] = [("Gabinete" if a == "Bancada" else a) for a in x["acesso"]]
        x.setdefault("bancada", False)
        f.append(x)
    # rampa nos pilares da torre: M3x12 de frente, porca presa no pilar, rasgo vertical de +-4 mm na aba da rampa
    zr = e.z_rampa
    for i, (x, dz) in enumerate(((170.0, -6.0), (170.0, 14.0), (212.0, -6.0), (212.0, 14.0))):
        add(f"rampa_torre_{i}", "M3x12 + porca", (x, 125.0, zr + dz), (0, 1, 0), 12, "Rampa", "Torre superior", 9,
            rasgo_c=(0, 0, 8.0), corredor=60)
    # filas no piso
    for i, x0 in enumerate((-28.0, 150.0)):
        add(f"fila_piso_{i}", "madeira 3,5x16", (x0 + 6, 162.5, 4.0), (0, 0, -1), 16, "Fila", "Gabinete", 8, cab=7.0)
    for i, x0 in enumerate((-210.0, -55.0)):
        add(f"filaE_piso_{i}", "madeira 3,5x16", (x0 + 6, 162.5, 4.0), (0, 0, -1), 16, "Fila esquerda", "Gabinete", 14,
            cab=7.0)
    for k, zp in (("A", m.zpA), ("B", m.zpB)):
        zc = zp + m.dz_correia
        # blocos nas paredes
        for lado, s in (("esq", -1), ("dir", 1)):
            pc = "Bloco esquerdo" if s < 0 else "Bloco direito"
            for i, dz in enumerate((-3.0, 9.0)):
                add(f"bloco_{lado}_{k}_{i}", "madeira 3,5x16", (213.0 * s, 39.0 if s < 0 else 37.0, zp + dz), (s, 0, 0), 16,
                    pc, "Gabinete", 9, cab=7.0)
            for i, x in enumerate((191.0, 197.0)):
                add(f"luva_{lado}_{k}_{i}", "M5x10 + martelo", (x * s, 4.0, zp), (0, 1, 0), 10, pc, f"Perfil 2020 {k}", 10,
                    cab=8.5)
        # trilho no perfil
        for i in range(16):
            x = -187.5 + 25 * i
            add(f"trilho_{k}_{i}", "M3x8 + martelo", (x, 33.0, zp), (0, -1, 0), 8, f"Trilho MGN12 {k}", f"Perfil 2020 {k}",
                10, bancada=True)
        # motor no suporte (bancada) e suporte na parede/piso
        pcs = f"Suporte do NEMA {'de cima' if k == 'A' else 'de baixo'}"
        zf = zc - 15
        for i, (dx, dy) in enumerate(((-15.5, -15.5), (15.5, -15.5), (15.5, 15.5), (-15.5, 15.5))):
            add(f"nema_{k}_{i}", "M3x8", (m.x_motor + dx, m.y_correia + dy, zf + 4), (0, 0, -1), 8, pcs, f"NEMA 17 {k}", 11,
                bancada=True)
        if k == "A":
            for i, (y, z) in enumerate(((8.0, zf - 62), (36.0, zf - 62), (22.0, zf - 50))):
                add(f"sup_nema_{k}_{i}", "madeira 3,5x16", (-215.5, y, z), (-1, 0, 0), 16, pcs, "Gabinete", 11, cab=7.0)
        else:
            for i, x in enumerate((-193.0, -180.0)):
                add(f"sup_nema_{k}_{i}", "madeira 3,5x16", (x, m.y_correia + 25.5, 4.0), (0, 0, -1), 16, pcs, "Gabinete",
                    8, cab=7.0)
            for i, z in enumerate((14.0, 36.0)):
                add(f"sup_nema_parede_{k}_{i}", "madeira 3,5x16", (-215.5, m.y_correia + 25.3, z), (-1, 0, 0), 16, pcs,
                    "Gabinete", 8, cab=7.0)
        # tensora
        add(f"eixo_tens_{k}", "M5x25 + porca nylon", (m.x_tensora, m.y_correia, zc + 8.0), (0, 0, -1), 25, "Bloco direito",
            "Bloco direito", 11, atravessa=(f"Polia tensora {k}",), cab=8.5, bancada=True)
        # fim de curso no braco do bloco esquerdo
        xe = m.c_casa + FIX[0] - 2
        for i, dz in enumerate((-4.75, 4.75)):
            add(f"fdc_{k}_{i}", "M2x12", (xe - 9.3, 32.0, zp - 20.1 + dz), (0, 1, 0), 12, "Fim de curso", "Bloco esquerdo", 9,
                cab=3.8, bancada=True)
            add(f"fdc_dir_{k}_{i}", "M2x12", (m.x_fdc_dir + 9.8, 32.0, zp - 25.1 + dz), (0, 1, 0), 12, "Fim de curso",
                "Bloco direito", 9, cab=3.8, bancada=True)
        # M3x16 de frente: cabeca no fixador, atravessa a correia entre as pontas, porca presa na presilha.
        # Aperta com a tensora solta (ramo da frente afastado com o dedo), depois estica na tensora.
        add(f"fixador_{k}", "M3x16 + porca", ((FIX[0] + FIX[1]) / 2, 22.0 + 20 * 2 / (2 * math.pi) - 0.7 - FIX_E,
                                             zp + m.dz_correia), (0, 1, 0), 16, "Fixador de correia", f"Carro {k}", 12,
            corpo="carro" + k, atravessa=(f"Correia {k}",), acesso=(f"Correia {k}",), corredor=15)
    # carros nos patins
    for k, zp in (("A", m.zpA), ("B", m.zpB)):
        for i, (dx, dz) in enumerate(((-10, -10), (10, -10), (10, 10), (-10, 10))):
            add(f"carro{k}_patim_{i}", "M3x8", (dx, 46.0, zp + dz), (0, -1, 0), 8, f"Carro {k}", f"Patim MGN12H {k}", 12,
                corpo="carro" + k, corredor=60)
    for i, (dx, z) in enumerate(((-16.0, 60.0), (16.0, 60.0), (-16.0, m.zb - 10.0), (16.0, m.zb - 10.0))):
        add(f"anel_placa_{i}", "M3x12 + porca", (dx, 50.0, z), (0, -1, 0), 12, "Anel", "Carro B", 13, corpo="carroB",
            corredor=40)
    add("ima", "M3x8", (m.dA, m.y_bola, m.face_ima + m.arruela_e + 20), (0, 0, -1), 8, "Carro A", "Eletroima P20/15", 12,
        corpo="carroA", bancada=True)
    # prateleira da esteira e ganchos
    for i, x in enumerate(GANCHOS):
        for j, dx in enumerate((-4.5, 4.5)):
            add(f"gancho_teto_{i}_{j}", "madeira 3,5x16", (x + dx, 113.5, GZ - 4), (0, 0, 1), 16, "Gancho da prateleira",
                "Gabinete", 13, cab=7.0, bancada=True)
            xs = x + dx                              # o do meio pega as duas metades (1 parafuso em cada)
            add(f"gancho_prat_{i}_{j}", "M3x10", (xs, 108.0, 403.5 + m.dZ), (0, -1, 0), 10, "Gancho da prateleira",
                "Prateleira da esteira", 13, corredor=60)
    xf = esteira_fixos(m)
    for j, dx in enumerate((-9.0, -3.0)):
        add(f"est_fixaA_{j}", "M3x16 + porca", (xf["A"] + dx, 92.0, 410.5 + m.dZ), (0, 0, -1), 16, "Ponta fixa da esteira",
            "Prateleira da esteira", 13, bancada=True)
    for j, dx in enumerate((-22.0, -16.0)):
        add(f"est_fixaB_{j}", "madeira 3,5x16", (xf["B"] + dx, 6.0, 4.0), (0, 0, -1), 16, "Ponta fixa da esteira",
            "Gabinete", 13, cab=7.0, corredor=60)
    # bandeja: 2 parafusos por placa, de cima pelos pes
    nomes = ("Bandeja esquerda", "Bandeja do meio", "Bandeja direita")
    for i, pc in enumerate(nomes):
        for j, x in enumerate(ABAS_BANDEJA[i]):
            add(f"band_{i}_{j}", "madeira 3,5x16", (x + 5, m.y_bandeja[0] + 6.5, 4.0), (0, 0, -1), 16, pc, "Gabinete", 14,
                cab=7.0, corredor=36)      # a chave entra pelo furo de 9 mm na placa (o EVA cobre depois)
    return [x for x in f if x is not None]
