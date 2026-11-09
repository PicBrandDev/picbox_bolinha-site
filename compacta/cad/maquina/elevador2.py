"""Elevador R2 da PICBOX compacta: TORRE em 2 pecas (de baixo e de cima) no lugar de base + 2 guias + 2 tubos +
suporte do motor + espacador + batente.

Referencial da maquina (mm): X para a direita do jogador, Y para o fundo (tela em Y 230), Z para cima, piso em Z 0.
Gabinete R2: 440 x 430 x 230 livres (paredes em X -220 / 220, teto em Z 430).

Cada torre e UMA peca impressa em pe e ja tem: pe no piso, paredes, trilhos em T (um em cada parede lateral),
frente do tubo, pilares da rampa, orelhas da parede direita, canaleta de cabos atras e o lugar dos sensores.
  * de baixo (Z 0..210): pe com 2 parafusos de madeira no piso, orelha com 2 na parede direita, polia de baixo num
    eixo M5 em balanco na placa de tras (rasgo de 6 mm para esticar), sensor optico de fenda de baixo.
  * de cima (Z 210..429, impressa de cabeca para baixo): motor N20 preso pela face (2 M2) num berco fechado,
    polia do motor, sensor optico de fenda de cima, pilares da rampa, orelha com 2 parafusos na parede.
  * as duas se encaixam por 3 pinos e 4 parafusos M3 (abas por fora, atras e a esquerda).
Cabine: desliza nos 2 trilhos em T com 1 mm de folga por lado (C de 50 mm de altura). A correia GT2 6 aberta
prende num bloco atras da cabine com o FIXADOR DE ALUMINIO 40 x 9 x 5 (o mesmo dos carros): as 2 pontas se
encontram no meio do fixador, a face dentada dele aperta a face dentada da correia contra a parede lisa do bloco,
1 M3x14 entra pela direita e rosca numa porca presa atras do fixador.
Sensores: 2 modulos LM393 de fenda 5 mm (baixo e topo). A "bandeira" e um parafuso M3x25 rosqueado na cabine: girar
o parafuso ajusta a altura exata em que a cabine para (com contra-porca).
"""
import math
from dataclasses import dataclass

import numpy as np

R_BOLA = 12.7
GX = 220.0          # paredes do gabinete em X +-220
GY = 230.0          # tela em Y 230
GZ = 430.0          # teto

# peca -> (tipo, material/modelo, etapa de montagem, como fixa)
PECAS = {
    "Gabinete": ("existente", "piso, paredes e teto de MDF", 0, "recebem os parafusos de madeira"),
    "Torre inferior": ("impressa", "PETG preto", 1,
                       "pe, trilhos, frente do tubo, polia de baixo e sensor de baixo numa peca so; 2 parafusos de madeira "
                       "3,5x16 no piso (aba da frente) e 2 na parede direita (orelha)"),
    "Torre superior": ("impressa", "PETG preto", 3,
                       "encaixa na de baixo por 3 pinos; 2 M3x8 atras e 2 M3x8 na esquerda; motor, sensor de cima e pilares "
                       "da rampa na mesma peca; 2 parafusos de madeira 3,5x16 na parede direita (orelha)"),
    "Cabine": ("impressa", "PETG preto", 2, "2 C deslizam nos trilhos em T (folga 1 mm por lado); entra por cima da torre de baixo"),
    "Fixador da cabine": ("comprada", "fixador de correia GT2 de aluminio 40 x 9 x 5 (o mesmo dos carros)", 4,
                          "em pe no bolso de tras da cabine, dentes na correia; M3x14 pela direita + porca presa atras dele"),
    "Correia": ("comprada", "GT2 6 mm aberta, ~850 mm", 4,
                "as 2 pontas no fixador da cabine (se encontram no meio dele); estica no rasgo da polia de baixo"),
    "Polia de baixo": ("comprada", "polia lisa/tensora GT2 20T furo 5 com rolamento (a da maquina antiga)", 1,
                       "eixo M5x30 em balanco na placa de tras: cabeca atras, porca na frente da placa, arruela, polia, "
                       "arruela e porca de nylon"),
    "Motor N20": ("comprada", "N20 12 V 100 rpm (sem encoder)", 3, "face da caixa de reducao com 2 M2x6 na placa do topo"),
    "Polia do motor": ("comprada", "GT2 20T furo 5 + bucha impressa 5 -> 3 mm em D", 3,
                       "no eixo do N20; o parafuso sem cabeca da polia aperta a bucha no lado chato do eixo"),
    "Sensor de fenda": ("comprada", "modulo LM393 com sensor optico de fenda 5 mm (FC-03 / H206), 2 unidades", 1,
                        "deitado na prateleira, 1 M3x8 + porca no rasgo (desliza para alinhar a fenda com a bandeira)"),
    "Bandeira": ("comprada", "parafuso M3x25 + porca (2 conjuntos)", 2,
                 "rosqueado no ressalto da cabine: girar ajusta a parada; travar com a porca"),
    "Servo": ("comprada", "SG90 (o que voce ja tem)", 8, "2 parafusos do proprio servo no suporte"),
    "Braco da comporta": ("impressa", "PETG preto", 8, "aparafusado no chifre do servo (2 parafusos do chifre)"),
    "Bolas de aco 1 pol": ("comprada", "8 bolas de aco de 25,4 mm", 8, "6 na fila, 1 na cabine e 1 no carro A"),
}

# trilhos e folgas
FOLGA_GUIA = 1.0


@dataclass
class P:
    r_bola: float = R_BOLA
    y_bola: float = 130.0 + R_BOLA     # bola na cabine encosta na frente do tubo (Y 130)
    zf_fim: float = 20.0               # piso da fila no fim (onde a bola entra na cabine)
    x_fila_fim: float = 174.0
    x_fila_ini: float = 20.0
    incl_fila: float = 5.0
    larg_fila: float = 26.5
    x_berco_ini: float = 180.0
    x_parede_dir: float = 203.5        # parede direita do berco (a bola encosta nela)
    y_berco: tuple = (131.5, 157.5)    # 1,5 mm da frente do tubo
    incl_berco_y: float = 8.0
    incl_berco_x: float = 2.0
    degrau: float = 1.5                # berco 1,5 mm abaixo do fim da fila (a bola sempre desce)
    z_rampa: float = 357.5
    incl_rampa: float = 6.0
    folga_topo: float = 1.0            # berco 1 mm acima do inicio da rampa no topo (a bola sempre desce)
    desce_espera: float = 20.0
    piv: tuple = (100.0, 121.0, 27.0)
    lamina_dx: float = -0.3
    lamina_topo: float = 7.0
    ponta_h: float = 2.0
    ponta_e: float = 0.8
    ang_baixa: float = 7.5
    # torre
    z_junta: float = 210.0
    x_polia: float = 191.0
    y_correia: tuple = (189.0, 195.0)
    z_polia_baixo: float = 10.5
    z_polia_cima: float = 419.0
    r_pitch: float = 40 / (2 * math.pi)
    r_polia: float = 9.0               # raio externo (abas) das 2 polias
    folga_guia: float = FOLGA_GUIA
    guia: str = "torre"

    # ------------------------------------------------------------ alturas
    @property
    def x_bola(self):
        return self.x_parede_dir - self.r_bola

    @property
    def x_contato(self):
        return self.x_bola - self.r_bola

    def z_piso_berco(self, x, y):
        return (y - self.y_bola) * math.tan(math.radians(self.incl_berco_y)) \
            - (x - self.x_bola) * math.tan(math.radians(self.incl_berco_x))

    @property
    def zc_min(self):
        return self.zf_fim - self.degrau - self.z_piso_berco(self.x_berco_ini, self.y_bola)

    @property
    def zc_topo(self):
        return self.z_rampa + self.folga_topo - self.z_piso_berco(self.x_bola, self.y_berco[0])

    @property
    def zc_max(self):              # o sensor de cima para a cabine na entrega
        return self.zc_topo

    @property
    def zc_espera(self):
        return self.zc_topo - self.desce_espera

    @property
    def zc_max_guia(self):
        return self.zc_max

    @property
    def curso(self):
        return self.zc_max - self.zc_min

    # bloco do fixador na cabine (Z relativo): cabe entre as 2 polias nos 2 extremos com a mesma folga
    H_FIX = 44.0                   # fixador 40 + 2 em cima e embaixo

    @property
    def fix_z(self):
        lo = self.z_polia_baixo + self.r_polia - self.zc_min
        hi = self.z_polia_cima - self.r_polia - self.zc_max - self.H_FIX
        k = (lo + hi) / 2
        return (k, k + self.H_FIX)

    @property
    def folga_polias(self):
        lo = self.z_polia_baixo + self.r_polia - self.zc_min
        hi = self.z_polia_cima - self.r_polia - self.zc_max - self.H_FIX
        return (hi - lo) / 2

    @property
    def x_ida(self):               # ramo preso na cabine (direita)
        return self.x_polia + self.r_pitch

    @property
    def x_volta(self):             # ramo livre (esquerda)
        return self.x_polia - self.r_pitch

    @property
    def yc(self):
        return sum(self.y_correia) / 2

    # sensores (feixe) e bandeiras
    Z_FEIXE_BAIXO = 14.6
    Z_FEIXE_CIMA = 415.4

    @property
    def bandeira_baixo(self):      # (ponta, cabeca) Z relativo; a ponta passa 1 mm do feixe na parada
        return (self.Z_FEIXE_BAIXO - 1.0 - self.zc_min)

    @property
    def bandeira_cima(self):
        return (self.Z_FEIXE_CIMA + 1.0 - self.zc_max)


def rot(rx=0.0, ry=0.0):
    a, b = math.radians(rx), math.radians(ry)
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    return Rx @ Ry


def quat(R):
    w = math.sqrt(max(0.0, 1 + R[0, 0] + R[1, 1] + R[2, 2])) / 2
    return [w, (R[2, 1] - R[1, 2]) / (4 * w), (R[0, 2] - R[2, 0]) / (4 * w), (R[1, 0] - R[0, 1]) / (4 * w)]


def caixa(lst, nome, corpo, x0, x1, y0, y1, z0, z1, grupo, peca, cor, R=None):
    c = [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]
    lst.append(dict(nome=nome, corpo=corpo, tipo="box", meio=[(x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2],
                    pos=c, quat=quat(R if R is not None else np.eye(3)), grupo=grupo, peca=peca, cor=cor))


def placa(lst, nome, corpo, x0, x1, y0, y1, esp, R, z_topo_centro, grupo, peca, cor):
    n = R @ np.array([0, 0, 1.0])
    c = np.array([(x0 + x1) / 2, (y0 + y1) / 2, z_topo_centro]) - n * esp / 2
    lst.append(dict(nome=nome, corpo=corpo, tipo="box", meio=[(x1 - x0) / 2, (y1 - y0) / 2, esp / 2],
                    pos=c.tolist(), quat=quat(R), grupo=grupo, peca=peca, cor=cor))


def cilindro(lst, nome, corpo, c, r, meio, eixo, grupo, peca, cor):
    R = {"y": rot(rx=90), "x": rot(ry=90), "z": np.eye(3)}[eixo]
    lst.append(dict(nome=nome, corpo=corpo, tipo="cylinder", meio=[r, meio], pos=list(c), quat=quat(R),
                    grupo=grupo, peca=peca, cor=cor))


# ===================================================================== medidas da torre (X, Y)
X_PAR_E = (163.0, 168.0)        # parede esquerda (zona dos trilhos)
X_PAR_D = (214.0, 219.5)        # parede direita (0,5 mm da parede do gabinete)
Y_TRILHO = (159.0, 209.0)       # paredes laterais na zona dos trilhos
Y_FRENTE = (128.0, 130.0)       # frente do tubo (a bola encosta em Y 130)
X_TUBO_E = (175.5, 177.5)       # parede esquerda do tubo (com a entrada da fila embaixo)
Y_DEGRAU = (159.0, 161.0)       # liga a parede do tubo a parede dos trilhos
Y_PLACA = (203.0, 209.0)        # placa de tras
Y_CANAL = (209.0, 219.0)        # canaleta de cabos
X_CANAL = (199.0, 214.0)
Y_ORELHA = (112.0, 128.0)       # orelhas na frente da parede direita
# trilho em T: pescoco 5 x 6 saindo da parede, cabeca 4 x 14
TRILHO_Y_CAB = (166.0, 180.0)
TRILHO_Y_PESC = (170.0, 176.0)
X_TRILHO_E = dict(pesc=(168.0, 173.0), cab=(173.0, 177.0))
X_TRILHO_D = dict(pesc=(209.0, 214.0), cab=(205.0, 209.0))
Z_TRILHO = (5.0, 425.0)        # ate o teto (a ponta de cima nao fica em balanco na impressao)
Z_TETO_TORRE = (425.0, 429.0)
# cabine (Z relativo)
Z_C = (-10.0, 40.0)             # altura dos C (50 mm)
Y_C = (162.0, 184.0)            # C: lados de 3 mm em volta da cabeca do trilho (folga 1)
X_C_E = (169.0, 181.0)
X_C_D = (201.0, 213.0)
Y_ALMA = (162.0, 180.0)
X_ALMA = (181.0, 201.0)
# bloco do fixador
X_BLOCO = (186.8, 204.0)
Y_BLOCO = (180.0, 199.0)
X_FIXADOR = None                # calculado (5 mm a esquerda do ramo preso)
Y_FIXADOR = (187.5, 196.5)
# sensores e bandeiras
X_SENSOR = (200.0, 214.0)       # placa de 14 de largura
Y_SENSOR = (185.0, 223.0)       # 38 de comprimento: a fenda na frente, os pinos na canaleta
X_FENDA = (203.0, 211.0)
X_BANDEIRA = 207.0
Y_BANDEIRA = 192.0
Z_RESSALTO_B = (5.0, 13.0)      # ressaltos da bandeira (relativo)
Z_RESSALTO_C = (36.0, 46.0)
X_RESSALTO = (204.0, 210.0)
Y_RESSALTO = (188.0, 196.0)
# motor
Y_FACE_MOTOR = 177.5


def sensor(g, nome, z_placa, para_cima):
    """Modulo LM393 de fenda deitado: placa 38 x 14 x 1,6 e o sensor (2 bracos de 11 mm com fenda de 5 no meio)."""
    pc = "Sensor de fenda"
    y0f, y1f = Y_BANDEIRA - 2.5, Y_BANDEIRA + 2.5
    ya, yb = Y_BANDEIRA - 6.25, Y_BANDEIRA + 6.25
    if para_cima:
        zp0, zp1 = z_placa, z_placa + 1.6
        za, zb_ = zp1, zp1 + 11.0
        zf = (zp1, zp1 + 3.0)
    else:
        zp0, zp1 = z_placa - 1.6, z_placa
        za, zb_ = zp0 - 11.0, zp0
        zf = (zp0 - 3.0, zp0)
    caixa(g, f"{nome}_placa", "mundo", *X_SENSOR, *Y_SENSOR, zp0, zp1, "visual", pc, "metal")
    caixa(g, f"{nome}_braco1", "mundo", *X_FENDA, ya, y0f, za, zb_, "visual", pc, "metal")
    caixa(g, f"{nome}_braco2", "mundo", *X_FENDA, y1f, yb, za, zb_, "visual", pc, "metal")
    caixa(g, f"{nome}_fundo", "mundo", *X_FENDA, y0f, y1f, *zf, "visual", pc, "metal")


def geometria(p: P):
    g = []
    T1, T2 = "Torre inferior", "Torre superior"
    zj = p.z_junta
    zr = p.z_rampa
    yc = p.yc
    # ------------------------------------------------ torre: pe
    caixa(g, "pe", "mundo", X_PAR_E[0], X_PAR_D[1], Y_TRILHO[0], Y_CANAL[1], 0, 5, "fixa", T1, "preto")
    caixa(g, "pe_frente", "mundo", 188.0, X_PAR_D[1], Y_ORELHA[0], Y_TRILHO[0], 0, 5, "fixa", T1, "preto")
    # paredes laterais (zona dos trilhos) e trilhos em T, nas 2 metades
    for seg, z0, z1, pc in (("inf", 5.0, zj, T1), ("sup", zj, Z_TETO_TORRE[0], T2)):
        caixa(g, f"parede_esq_{seg}", "mundo", *X_PAR_E, *Y_TRILHO, z0, z1, "fixa", pc, "preto")
        caixa(g, f"parede_dir_{seg}", "mundo", *X_PAR_D, Y_ORELHA[1], Y_CANAL[1], z0, z1, "fixa", pc, "preto")
        caixa(g, f"placa_tras_{seg}", "mundo", X_PAR_E[1], X_PAR_D[0], *Y_PLACA, z0, z1, "fixa", pc, "preto")
        caixa(g, f"canal_esq_{seg}", "mundo", 197.0, X_CANAL[0], *Y_CANAL, z0, z1, "fixa", pc, "preto")
        for lado, xs in (("esq", X_CANAL[0]), ("dir", X_CANAL[1] - 4.0)):
            caixa(g, f"canal_labio_{lado}_{seg}", "mundo", xs, xs + 4.0, Y_CANAL[1] - 2, Y_CANAL[1], z0, z1, "fixa", pc, "preto")
        caixa(g, f"degrau_{seg}", "mundo", X_PAR_E[0], X_TUBO_E[1], *Y_DEGRAU, z0, z1, "fixa", pc, "preto")
        zt0, zt1 = max(z0, Z_TRILHO[0]), min(z1, Z_TRILHO[1])
        for lado, X in (("esq", X_TRILHO_E), ("dir", X_TRILHO_D)):
            caixa(g, f"trilho_pesc_{lado}_{seg}", "mundo", *X["pesc"], *TRILHO_Y_PESC, zt0, zt1, "fixa", pc, "preto")
            caixa(g, f"trilho_cab_{lado}_{seg}", "mundo", *X["cab"], *TRILHO_Y_CAB, zt0, zt1, "fixa", pc, "preto")
    # parede esquerda do tubo: entrada da fila embaixo (Y 130..156,5 abaixo de Z 50)
    caixa(g, "tubo_esq_tras", "mundo", *X_TUBO_E, 156.5, Y_DEGRAU[0], 5, zj, "fixa", T1, "preto")
    caixa(g, "tubo_esq_cima", "mundo", *X_TUBO_E, Y_FRENTE[1], 156.5, 50, zj, "fixa", T1, "preto")
    caixa(g, "tubo_esq_sup", "mundo", *X_TUBO_E, Y_FRENTE[1], Y_DEGRAU[0], zj, Z_TETO_TORRE[0], "fixa", T2, "preto")
    # frente do tubo: recorte embaixo a esquerda para o braco da comporta; em cima para na rampa (a bola sai)
    caixa(g, "frente_b", "mundo", 180.0, X_PAR_D[1], *Y_FRENTE, 5, zj, "fixa", T1, "preto")
    caixa(g, "frente_c", "mundo", X_TUBO_E[0], 180.0, *Y_FRENTE, 25, zj, "fixa", T1, "preto")
    caixa(g, "frente_sup", "mundo", X_TUBO_E[0], 207.5, *Y_FRENTE, zj, zr - 0.3, "fixa", T2, "preto")
    caixa(g, "frente_sup_dir", "mundo", 207.5, X_PAR_D[1], *Y_FRENTE, zj, Z_TETO_TORRE[0], "fixa", T2, "preto")
    # orelhas da parede direita (2 parafusos de madeira cada), na frente da torre
    caixa(g, "orelha_inf", "mundo", *X_PAR_D, *Y_ORELHA, 5, 150, "fixa", T1, "preto")
    caixa(g, "orelha_sup", "mundo", *X_PAR_D, *Y_ORELHA, zj, 300, "fixa", T2, "preto")
    # chanfro de 45 graus em cima da orelha de cima (a torre de cima e impressa de cabeca para baixo)
    Rw = rot(rx=45)
    lw = (Y_ORELHA[1] - Y_ORELHA[0]) / math.sqrt(2)          # meio lado do quadrado girado (meia diagonal = 16)
    g.append(dict(nome="orelha_sup_chanfro", corpo="mundo", tipo="box",
                  meio=[(X_PAR_D[1] - X_PAR_D[0]) / 2, lw, lw],
                  pos=[sum(X_PAR_D) / 2, Y_ORELHA[1], 300.0], quat=quat(Rw), grupo="fixa", peca=T2, cor="preto"))
    # pilares da rampa (porca presa, a rampa sobe e desce nos rasgos) - vao ate o teto da torre
    caixa(g, "pilar_esq", "mundo", 165.0, X_TUBO_E[0], Y_FRENTE[0], 142.0, zr - 25, Z_TETO_TORRE[0], "fixa", T2, "preto")
    caixa(g, "pilar_dir", "mundo", 207.5, X_PAR_D[0], Y_FRENTE[0], 142.0, zr - 25, Z_TETO_TORRE[0], "fixa", T2, "preto")
    # teto da torre
    caixa(g, "teto_torre", "mundo", X_PAR_E[0], X_PAR_D[1], Y_FRENTE[0], Y_CANAL[1], *Z_TETO_TORRE, "fixa", T2, "preto")
    # abas da emenda (da torre de cima, descem 20 mm por fora da de baixo)
    caixa(g, "aba_emenda_tras", "mundo", 166.0, 186.0, Y_CANAL[0], Y_CANAL[0] + 3, zj - 20, zj, "fixa", T2, "preto")
    caixa(g, "aba_emenda_esq", "mundo", X_PAR_E[0] - 3, X_PAR_E[0], 175.0, 205.0, zj - 20, zj, "fixa", T2, "preto")
    # ------------------------------------------------ polia de baixo (eixo M5 em balanco na placa de tras)
    pb = p.z_polia_baixo
    cilindro(g, "polia_baixo", "mundo", (p.x_polia, yc + 0.5, pb), p.r_polia, 4.5, "y", "visual", "Polia de baixo", "metal")
    cilindro(g, "porca_eixo_baixo", "mundo", (p.x_polia, 201.0, pb), 4.6, 2.0, "y", "visual", "Polia de baixo", "metal")
    cilindro(g, "nylon_eixo_baixo", "mundo", (p.x_polia, 185.5, pb), 4.6, 2.5, "y", "visual", "Polia de baixo", "metal")
    # ------------------------------------------------ motor no topo (face presa na placa, corpo no berco)
    zt = p.z_polia_cima
    fm = Y_FACE_MOTOR
    caixa(g, "motor", "mundo", 185, 197, fm - 32.5, fm, zt - 5, zt + 5, "visual", "Motor N20", "metal")
    caixa(g, "placa_motor", "mundo", 181.0, 201.0, fm, fm + 3.0, zt - 9.5, Z_TETO_TORRE[0], "fixa", T2, "preto")
    caixa(g, "berco_motor", "mundo", 183.0, 199.0, fm - 32.5, fm, zt - 7.0, Z_TETO_TORRE[0], "fixa", T2, "preto")
    cilindro(g, "polia_cima", "mundo", (p.x_polia, 192.0, zt), p.r_polia, 3.5, "y", "visual", "Polia do motor", "metal")
    cilindro(g, "cubo_cima", "mundo", (p.x_polia, 185.5, zt), 6.5, 3.0, "y", "visual", "Polia do motor", "metal")
    # ------------------------------------------------ correia: ramo livre (o preso anda com a cabine)
    caixa(g, "correia_volta", "mundo", p.x_volta - 0.7, p.x_volta + 0.7, *p.y_correia, pb, zt, "visual", "Correia", "correia")
    # ------------------------------------------------ sensores de fenda (deitados), com os calcos da placa
    sensor(g, "sensor_baixo", 7.0, True)
    sensor(g, "sensor_cima", Z_TETO_TORRE[0] - 2.0, False)
    for i, xs in enumerate((X_SENSOR[0], X_SENSOR[1] - 2)):
        caixa(g, f"calco_sensor_baixo_{i}", "mundo", xs, xs + 2, Y_SENSOR[0], Y_PLACA[0], 5, 7, "fixa", T1, "preto")
        caixa(g, f"calco_sensor_cima_{i}", "mundo", xs, xs + 2, Y_SENSOR[0], Y_PLACA[0], Z_TETO_TORRE[0] - 2, Z_TETO_TORRE[0],
              "fixa", T2, "preto")
    # ------------------------------------------------ cabine (Z relativo a Zc)
    Rb = rot(rx=p.incl_berco_y, ry=p.incl_berco_x)
    xb0, xb1 = p.x_berco_ini, p.x_parede_dir
    yb0, yb1 = p.y_berco
    xbm, ybm = (xb0 + xb1) / 2, (yb0 + yb1) / 2
    placa(g, "berco_piso", "carro", xb0, xb1, yb0, yb1, 3, Rb, p.z_piso_berco(xbm, ybm), "carro", "Cabine", "acento")
    caixa(g, "berco_dir", "carro", xb1, xb1 + 2.5, yb0, 160.0, -1, 22, "carro", "Cabine", "acento")
    caixa(g, "berco_fundo", "carro", xb0, xb1 + 2.5, yb1, 160.0, -1, 22, "carro", "Cabine", "acento")
    # macico embaixo do piso inclinado ate a base plana (Z -10) - a cabine e impressa em pe: caixa inclinada com o canto
    # mais baixo em Z -10 + caixa reta de Z -10 ate o canto mais alto da face de baixo (sem vao embaixo do berco)
    nb = Rb @ np.array([0, 0, 1.0])
    zb_top = lambda x, y: p.z_piso_berco(x, y) - 2.9
    meio_xy = np.array([(xb1 - xb0) / 2, (yb1 - yb0) / 2])
    desce = float(np.abs(Rb[2, :2]) @ meio_xy)           # quanto um canto desce em relacao ao centro (giro)
    zc_top = zb_top(xbm, ybm)
    esp = (zc_top - Z_C[0] - desce) / (Rb[2, 2] + 1e-12)   # canto mais baixo exatamente em Z -10
    c = np.array([xbm, ybm, zc_top]) - nb * esp / 2
    g.append(dict(nome="berco_macico", corpo="carro", tipo="box", meio=[meio_xy[0], meio_xy[1], esp / 2],
                  pos=c.tolist(), quat=quat(Rb), grupo="carro", peca="Cabine", cor="acento"))
    caixa(g, "berco_macico_base", "carro", xb0 + 0.3, xb1 - 0.3, yb0 + 0.3, yb1 - 0.3, Z_C[0], Z_C[0] + 2 * desce + 0.5,
          "carro", "Cabine", "acento")
    caixa(g, "costas", "carro", xb0, xb1 + 2.5, 160.0, Y_C[0], Z_C[0], 30.0, "carro", "Cabine", "acento")
    caixa(g, "alma", "carro", *X_ALMA, *Y_ALMA, 0.0, Z_C[1], "carro", "Cabine", "acento")
    f = p.folga_guia
    for lado, X in (("esq", X_TRILHO_E), ("dir", X_TRILHO_D)):
        cab, pesc = X["cab"], X["pesc"]
        s = -1 if lado == "esq" else 1          # lado da parede
        x_par = X_PAR_E[1] if lado == "esq" else X_PAR_D[0]
        xc = X_C_E if lado == "esq" else X_C_D
        face = (cab[1] + f, cab[1] + f + 3) if lado == "esq" else (cab[0] - f - 3, cab[0] - f)
        labio = (x_par + f, x_par + f + 3) if lado == "esq" else (x_par - f - 3, x_par - f)
        caixa(g, f"C_{lado}_face", "carro", *face, TRILHO_Y_CAB[0] - f, TRILHO_Y_CAB[1] + f, *Z_C, "carro", "Cabine", "acento")
        caixa(g, f"C_{lado}_lado1", "carro", *xc, Y_C[0], TRILHO_Y_CAB[0] - f, *Z_C, "carro", "Cabine", "acento")
        caixa(g, f"C_{lado}_lado2", "carro", *xc, TRILHO_Y_CAB[1] + f, Y_C[1], *Z_C, "carro", "Cabine", "acento")
        caixa(g, f"C_{lado}_labio1", "carro", *labio, TRILHO_Y_CAB[0] - f, TRILHO_Y_PESC[0] - f, *Z_C, "carro", "Cabine", "acento")
        caixa(g, f"C_{lado}_labio2", "carro", *labio, TRILHO_Y_PESC[1] + f, TRILHO_Y_CAB[1] + f, *Z_C, "carro", "Cabine", "acento")
    # bloco do fixador atras da alma
    k0, k1 = p.fix_z
    caixa(g, "bloco_fixador", "carro", *X_BLOCO, *Y_BLOCO, k0, k1, "carro", "Cabine", "acento")
    xf1 = p.x_ida - 0.7
    caixa(g, "fixador_cabine", "carro", xf1 - 5.0, xf1, *Y_FIXADOR, k0 + 2, k1 - 2, "carro_vis", "Fixador da cabine", "metal")
    caixa(g, "correia_presa", "carro", xf1, xf1 + 1.4, *p.y_correia, k0 - 3, k1 + 3, "carro_vis", "Correia", "correia")
    # ressaltos e bandeiras (parafuso M3x25 rosqueado: a ponta passa no feixe do sensor)
    for nm, (z0, z1) in (("b", Z_RESSALTO_B), ("c", Z_RESSALTO_C)):
        caixa(g, f"ressalto_{nm}", "carro", *X_RESSALTO, *Y_RESSALTO, z0, z1, "carro", "Cabine", "acento")
    zb = p.bandeira_baixo
    cilindro(g, "bandeira_baixo", "carro", (X_BANDEIRA, Y_BANDEIRA, (zb + zb + 25) / 2), 1.5, 12.5, "z", "carro_vis", "Bandeira", "metal")
    cilindro(g, "bandeira_baixo_cab", "carro", (X_BANDEIRA, Y_BANDEIRA, zb + 26.5), 2.75, 1.5, "z", "carro_vis", "Bandeira", "metal")
    zc_ = p.bandeira_cima
    cilindro(g, "bandeira_cima", "carro", (X_BANDEIRA, Y_BANDEIRA, zc_ - 12.5), 1.5, 12.5, "z", "carro_vis", "Bandeira", "metal")
    cilindro(g, "bandeira_cima_cab", "carro", (X_BANDEIRA, Y_BANDEIRA, zc_ - 26.5), 2.75, 1.5, "z", "carro_vis", "Bandeira", "metal")
    # ------------------------------------------------ comporta (igual a R1)
    # suporte do servo impresso junto com a fila (ponte no piso ate a frente da fila)
    caixa(g, "suporte_servo", "mundo", 84, 116, 88, 116.5, 0, 21, "visual", "Fila", "preto")
    caixa(g, "suporte_servo_ponte", "mundo", 84, 116, 116.5, 128.0, 0, 4, "visual", "Fila", "preto")
    for i, (x0, x1) in enumerate(((70.0, 84.0), (116.0, 130.0))):
        caixa(g, f"suporte_servo_aba_{i}", "mundo", x0, x1, 92, 112.5, 0, 4, "visual", "Fila", "preto")
    caixa(g, "servo", "mundo", 88.6, 111.4, 88, 116.5, 21, 33, "visual", "Servo", "metal")
    px, py, pz = p.piv
    L = lambda x0, x1, y0, y1, z0, z1: (x0 - px, x1 - px, y0 - py, y1 - py, z0 - pz, z1 - pz)
    xl = p.x_contato + p.lamina_dx
    ztl = p.zf_fim + p.lamina_topo
    A = "Braco da comporta"
    caixa(g, "alav_chifre", "alavanca", *L(92, 108, 116.5, 119, 23, 31), "alavanca", "Servo", "metal")
    caixa(g, "alav_braco", "alavanca", *L(95, xl + 0.75, 117, 125, 23, 27), "alavanca", A, "comporta")
    caixa(g, "alav_ponte", "alavanca", *L(175, xl + 0.75, 117, 132, 14, 23), "alavanca", A, "comporta")
    caixa(g, "alav_barra", "alavanca", *L(175.5, xl + 0.75, 117, 155, 11.5, 14), "alavanca", A, "comporta")
    caixa(g, "alav_lamina", "alavanca", *L(xl - 0.75, xl + 0.75, 132, 152, 14, ztl - p.ponta_h), "alavanca", A, "comporta")
    caixa(g, "alav_ponta2", "alavanca", *L(xl - 0.6, xl + 0.6, 132, 152, ztl - p.ponta_h, ztl - p.ponta_h / 2),
          "alavanca", A, "comporta")
    caixa(g, "alav_ponta", "alavanca", *L(xl - p.ponta_e / 2 - 0.2, xl + p.ponta_e / 2 + 0.2, 132, 152, ztl - p.ponta_h / 2,
                                         ztl - 0.5), "alavanca", A, "comporta")
    caixa(g, "alav_ponta_topo", "alavanca", *L(xl - p.ponta_e / 2, xl + p.ponta_e / 2, 132, 152, ztl - 0.5, ztl),
          "alavanca", A, "comporta")
    return g


def fixadores(p: P):
    """Cada parafuso: onde a cabeca apoia (p0), direcao, comprimento util, quem prende quem, etapa e acessos."""
    f = []

    def add(nome, tipo, p0, dir_, L, prende, rosca, etapa, acesso=(), insert=None, cab=5.5, atravessa=(), corpo="mundo",
            bancada=False, corredor=120.0, rasgo=None, rasgo_c=None, rasgo_em=None):
        f.append(dict(nome=nome, tipo=tipo, p0=list(p0), dir=list(dir_), L=L, prende=prende, rosca=rosca, etapa=etapa,
                      acesso=list(acesso), insert=insert, cab=cab, atravessa=list(atravessa), corpo=corpo,
                      bancada=bancada, corredor=corredor, rasgo=rasgo, rasgo_c=rasgo_c,
                      rasgo_em=rasgo_em))

    T1, T2 = "Torre inferior", "Torre superior"
    zj = p.z_junta
    # pe no piso (aba da frente) e orelhas na parede direita
    for i, x in enumerate((196.0, 207.0)):
        add(f"torre_piso_{i}", "madeira 3,5x16", (x, 120.0, 5.0), (0, 0, -1), 16, T1, "Gabinete", 1, cab=7.0, corredor=60)
    for i, z in enumerate((70.0, 130.0)):
        add(f"torre_parede_inf_{i}", "madeira 3,5x16", (X_PAR_D[0], 120.0, z), (1, 0, 0), 16, T1, "Gabinete", 1, cab=7.0)
    for i, z in enumerate((235.0, 280.0)):
        add(f"torre_parede_sup_{i}", "madeira 3,5x16", (X_PAR_D[0], 120.0, z), (1, 0, 0), 16, T2, "Gabinete", 3, cab=7.0)
    # emenda das torres (abas da de cima, rosca direto na de baixo)
    for i, x in enumerate((171.0, 181.0)):
        add(f"emenda_tras_{i}", "M3x8", (x, Y_CANAL[0] + 3, zj - 10), (0, -1, 0), 8, T2, T1, 3, bancada=True)
    for i, y in enumerate((183.0, 198.0)):
        add(f"emenda_esq_{i}", "M3x8", (X_PAR_E[0] - 3, y, zj - 10), (1, 0, 0), 8, T2, T1, 3, bancada=True)
    # eixo da polia de baixo: cabeca atras da placa, porca na frente (rasgo de 6 mm para cima para dar folga na correia)
    add("eixo_polia_baixo", "M5x30 + porcas", (p.x_polia, Y_PLACA[1], p.z_polia_baixo), (0, -1, 0), 30, T1, T1, 1,
        atravessa=("Polia de baixo",), cab=8.5, bancada=True, rasgo=(0, 0, 6.0))
    # motor: 2 M2x6 da placa na face da caixa de reducao
    for i, dx in enumerate((-4.5, 4.5)):
        add(f"motor_{i}", "M2x6", (p.x_polia + dx, Y_FACE_MOTOR + 3.0, p.z_polia_cima), (0, -1, 0), 6, T2, "Motor N20", 3,
            cab=3.8, bancada=True)
    # sensores: 1 M3 + porca no rasgo (a posicao do furo varia com o fornecedor; a placa desliza no calco)
    add("sensor_baixo", "M3x8 + porca", (X_BANDEIRA + 0.0, 205.0, 8.6), (0, 0, -1), 8, "Sensor de fenda", T1, 1,
        bancada=True, rasgo_c=(0, 16.0, 0), cab=5.5, rasgo_em=T1)
    add("sensor_cima", "M3x8 + porca", (X_BANDEIRA + 0.0, 205.0, Z_TETO_TORRE[0] - 3.6), (0, 0, 1), 8, "Sensor de fenda", T2, 3,
        bancada=True, rasgo_c=(0, 16.0, 0), cab=5.5, rasgo_em=T2)
    # fixador da correia na cabine: M3x14 pela direita, porca presa atras do fixador
    k0, k1 = p.fix_z
    add("fixador_cabine", "M3x14 + porca", (X_BLOCO[1] - 3.0, Y_BANDEIRA, (k0 + k1) / 2), (-1, 0, 0), 14, "Cabine", "Cabine", 4,
        corpo="carro", atravessa=("Fixador da cabine", "Correia"), bancada=True, corredor=12)
    # comporta: suporte do servo no piso (rasgos de +-3 mm em X)
    for i, x in enumerate((77.0, 123.0)):
        add(f"servo_piso_{i}", "madeira 3,5x16", (x, 102.25, 4.0), (0, 0, -1), 16, "Fila", "Gabinete", 8,
            cab=7.0, corredor=30)
    return f
