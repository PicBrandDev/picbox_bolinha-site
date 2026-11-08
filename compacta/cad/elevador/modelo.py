"""Elevador de cabine da PICBOX compacta (R0.2): geometria unica para checagem, simulacao e visualizacao.

Referencial da maquina (mm): X direita do jogador, Y para o fundo (tela em Y 200), Z para cima, piso em Z 0.

Principio: a cabine sobe e desce num trilho MGN9. A correia GT2 6 e ABERTA e as duas pontas ficam presas
na propria cabine, entao nada rigido passa pelas polias. A cabine nunca chega perto das polias (checado).
Embaixo, a comporta e uma lamina na ponta de um braco girado por um servo MG90S. Sequencia: cabine no
fundo, lamina baixa, UMA bola rola para o berco; o servo levanta a lamina no vao entre essa bola e a
seguinte; so entao a cabine sobe. O pivo fica na altura do topo da lamina, entao o empurrao da fila passa
quase pelo eixo e nao forca o servo. O braco nunca encosta na cabine em nenhuma combinacao (checado).
(A versao passiva com contrapeso foi reprovada: a bola seguinte avancava antes da lamina subir.)
"""
import math
from dataclasses import dataclass

import numpy as np

R_BOLA = 12.7

# peca -> (tipo, material/modelo, etapa de montagem, como fixa)
PECAS = {
    "Base": ("impressa", "PETG preto", 1, "4 parafusos de madeira na bancada (ou no piso do gabinete); 2 M3x12 de baixo prendem a espinha"),
    "Espinha inferior": ("impressa", "PETG preto", 1, "assenta na base; 2 M3x12 por baixo + o trilho por cima amarra com a superior"),
    "Espinha superior": ("impressa", "PETG preto", 1, "apoiada na inferior; o trilho, com 19 M3x10, une as duas"),
    "Batente": ("impressa", "parte da base", 1, "impresso junto com a base"),
    "Trilho MGN9": ("comprada", "MGN9 cortado em 380 mm", 2, "19 M3x10 pela frente em insertos M3 na espinha, a cada 20 mm"),
    "Patim MGN9H": ("comprada", "vem montado no trilho", 2, "corre no trilho; nunca tirar do trilho (as esferas caem)"),
    "Cabine": ("impressa", "PETG preto", 3, "4 M3x6 pela frente, passando por furos de acesso no fundo do berco, nos furos roscados do patim"),
    "Polia de baixo": ("comprada", "polia tensora GT2 20T furo 3", 4, "parafuso M3x35 por tras da espinha, espacador, polia e porca autotravante"),
    "Espacador": ("impressa", "PETG", 4, "no parafuso da polia de baixo"),
    "Suporte do motor": ("impressa", "PETG preto", 5, "2 M3x12 de cima, dentro de rebaixos na perna, em insertos no topo da espinha"),
    "Motor N20": ("comprada", "N20 12 V 100 rpm com encoder", 5, "abracado pelo suporte; 2 M2 na face da caixa de reducao"),
    "Polia do motor": ("comprada", "GT2 20T furo 3", 5, "no eixo do N20 com o parafuso sem cabeca no lado chato do eixo"),
    "Correia": ("comprada", "GT2 6 mm aberta, 830 mm", 6, "as duas pontas nas presilhas da cabine; tensao dada na presilha de cima"),
    "Tubo inferior": ("impressa", "PETG transparente", 7, "encaixa pela frente; 4 M3x8 cabeca chata pelas laterais na espinha"),
    "Tubo superior": ("impressa", "PETG transparente", 7, "encaixa pela frente; 4 M3x8 cabeca chata pelas laterais na espinha"),
    "Fila": ("impressa", "PETG preto", 8, "parafusada na bancada; na maquina vem da bandeja"),
    "Suporte do servo": ("impressa", "PETG preto", 8, "parafusado na bancada com furos oblongos: ajuste de +-2 mm em X para centrar a lamina entre as bolas"),
    "Servo": ("comprada", "MG90S engrenagem metalica", 8, "2 parafusos do proprio servo no suporte"),
    "Braco da comporta": ("impressa", "PETG preto", 8, "aparafusado no chifre do servo (2 parafusos do chifre)"),
    "Rampa": ("impressa", "PETG preto", 8, "apoiada no topo da parede da frente + 2 pes na bancada"),
}


# guia barata: 2 eixos de 8 mm + 2 LM8UU no lugar do trilho MGN9 (o resto igual)
PECAS_EIXOS = dict(PECAS)
for _k in ("Espinha inferior", "Espinha superior", "Trilho MGN9", "Patim MGN9H", "Espacador"):
    PECAS_EIXOS.pop(_k)
PECAS_EIXOS.update({
    "Base": ("impressa", "PETG preto", 1, "4 parafusos de madeira na bancada (ou no piso do gabinete); 2 M3x12 de baixo prendem o pe dos eixos"),
    "Pe dos eixos": ("impressa", "PETG preto", 1, "2 M3x12 de baixo pela base; os eixos entram justos e travam com parafuso sem cabeca M3"),
    "Eixos 8 mm": ("comprada", "2 eixos retificados 8 x 400 mm (sem cortar)", 2, "entram no pe e na cabeca; 1 parafuso sem cabeca M3 em cada ponta"),
    "Rolamentos LM8UU": ("comprada", "2 LM8UU", 2, "prensados nos alojamentos da cabine + 1 abracadeira de nylon cada"),
    "Cabine": ("impressa", "PETG preto", 2, "corre nos eixos pelos 2 LM8UU; entra junto com os eixos, antes da cabeca"),
    "Cabeca dos eixos": ("impressa", "PETG preto", 3, "encaixa no topo dos eixos; 2 parafusos sem cabeca travam os eixos"),
    "Polia de baixo": ("comprada", "polia tensora GT2 20T furo 3", 4, "M3x35 por tras do pe (cabeca no rebaixo), espacador, polia e porca autotravante"),
    "Espacador": ("impressa", "PETG", 4, "no parafuso da polia de baixo"),
    "Suporte do motor": ("impressa", "PETG preto", 5, "2 M3x25 de cima atravessando o suporte, em insertos na cabeca dos eixos"),
    "Motor N20": ("comprada", "N20 12 V 100 rpm SEM encoder (posicao pelos TCRT5000 e pelo batente)", 5, "abracado pelo suporte; 2 M2 na face da caixa de reducao"),
    "Tubo inferior": ("impressa", "PETG (o que tiver)", 7, "aba na frente com 2 M3x8 em insertos na base; 2 pinos impressos no tubo de cima"),
    "Tubo superior": ("impressa", "PETG (o que tiver)", 7, "2 blocos no topo; 2 M3x12 de cima pelo suporte do motor"),
    "Servo": ("comprada", "SG90 (o mais barato; mesmo tamanho do MG90S, que tem engrenagem de metal)", 8,
                    "2 parafusos do proprio servo no suporte"),
})

# guia 100% impressa: 2 trilhos em T impressos junto com o pe e a cabeca; a cabine abraca cada trilho com um C
PECAS_IMPRESSA = dict(PECAS_EIXOS)
for _k in ("Eixos 8 mm", "Rolamentos LM8UU", "Pe dos eixos", "Cabeca dos eixos"):
    PECAS_IMPRESSA.pop(_k)
PECAS_IMPRESSA.update({
    "Base": ("impressa", "PETG preto", 1, "2 M3x12 de baixo prendem a guia; depois 2 parafusos de madeira 3,5x16 na frente, no piso; "
                                          "janela embaixo da polia e bochecha com porca presa para o parafuso da polia"),
    "Gabinete": ("existente", "parede direita e piso do gabinete", 1, "recebem os parafusos de madeira"),
    "Guia impressa inferior": ("impressa", "PETG preto", 1, "pe + 2 trilhos em T ate Z 200, numa peca so; 2 M3x12 de baixo pela base"),
    "Cabine": ("impressa", "PETG preto", 2, "2 alojamentos em C deslizam nos trilhos em T (folga 0,5 mm por lado); entra pelo topo da guia de baixo"),
    "Guia impressa superior": ("impressa", "PETG preto", 3, "2 trilhos em T + cabeca, numa peca so; encaixa na de baixo por 2 pinos impressos e fica presa pelo suporte do motor"),
    "Suporte do motor": ("impressa", "PETG preto", 5, "2 M3x16 de cima atravessando o suporte, rosqueados no topo da guia de cima; "
                                                      "orelha na frente com 2 parafusos de madeira 3,5x16 na parede direita do gabinete"),
    "Fim de curso": ("comprada", "microchave KW10 (as que voce ja tem): 2 usadas, 1 de reserva", 1,
                     "uma num rebaixo do pe (fundo) e outra num rebaixo da cabeca (topo); 2 M2x12 de lado em cada"),
    "Polia do motor": ("comprada", "GT2 20T furo 5 mm + bucha impressa 5 -> 3 mm em D", 5,
                       "no eixo do N20; o parafuso sem cabeca da polia passa pelo rasgo da bucha e aperta no lado chato"),
    "Polia de baixo": ("comprada", "polia tensora GT2 20T furo 5 mm + calco impresso 5 -> 3,2 mm", 4,
                       "M3x40 por tras do pe, espacador, calco dentro do rolamento, polia e porca presa na bochecha da base; "
                       "o rasgo de 2 mm no pe e na bochecha estica a correia"),
    "Servo": ("comprada", "SG90 (o que voce ja tem)", 8, "2 parafusos do proprio servo no suporte"),
    "Bolas de aco 1 pol": ("comprada", "8 bolas de aco de 25,4 mm", 8, "6 na fila, 1 na cabine e 1 no carro A"),
})


@dataclass
class P:
    r_bola: float = R_BOLA
    y_bola: float = 130.0 + R_BOLA
    zf_fim: float = 20.0
    x_fila_fim: float = 174.0
    x_fila_ini: float = 20.0
    incl_fila: float = 4.0
    larg_fila: float = 26.5
    x_berco_ini: float = 180.0
    x_parede_dir: float = 203.5
    incl_berco_y: float = 8.0
    incl_berco_x: float = 2.0
    degrau: float = 0.8
    z_rampa: float = 352.0
    incl_rampa: float = 6.0
    folga_topo: float = 0.5
    desce_espera: float = 20.0
    piv: tuple = (100.0, 121.0, 27.0)
    lamina_dx: float = -0.3            # lamina 0,3 mm para o lado da fila (o berco fica mais baixo)
    lamina_topo: float = 7.0
    ponta_h: float = 2.0               # altura da ponta fina da lamina (era 3)
    ponta_e: float = 0.8               # espessura da ponta
    ang_baixa: float = 7.5             # angulo do servo com a lamina baixa (graus)
    z_polia_baixo: float = 12.5
    z_polia_cima: float = 405.0
    x_polia: float = 191.0
    y_correia: tuple = (165.5, 171.5)
    z_trilho: tuple = (16.0, 401.0)
    r_pitch: float = 40 / (2 * math.pi)
    guia: str = "mgn9"                 # "mgn9", "eixos" ou "impressa"
    x_eixos: tuple = (181.5, 199.5)
    y_eixos: float = 182.5
    z_pe: float = 20.0                 # topo do pe dos eixos
    z_cabeca: float = 388.5            # fundo da cabeca dos eixos

    folga_guia: float = 0.5            # folga por lado entre o C da cabine e o T impresso

    @property
    def alt_caixa(self):          # altura dos alojamentos: maior na guia impressa para nao travar (efeito gaveta)
        return 40.0 if self.guia == "impressa" else 28.0

    @property
    def caixa_z(self):            # alojamentos relativos a Zc: 1 mm acima do pe no fundo
        z0 = self.z_pe + 1.0 - self.zc_min
        return (z0, z0 + self.alt_caixa)

    @property
    def fundo_cabeca(self):       # 1,1 mm acima dos alojamentos com a cabine no topo
        return self.z_cabeca if self.guia == "eixos" else self.zc_max_guia + self.caixa_z[1] + 1.1

    @property
    def topo_cabeca(self):
        return 402.0 if self.guia == "eixos" else 413.0

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
        return self.z_rampa + self.folga_topo - self.z_piso_berco(self.x_bola, 130.5)

    @property
    def zc_espera(self):
        return self.zc_topo - self.desce_espera

    @property
    def zc_max_guia(self):        # limite de cima usado para desenhar a cabeca da guia e o rebaixo do fim de curso
        return self.zc_topo + 3.0

    @property
    def zc_max(self):             # onde a cabine para: o fim de curso de cima dispara 0,5 mm acima do ponto de entrega
        return self.zc_topo + 0.5     # (antes disparava em zc_topo + 3 e a bola caia 3,5 mm na rampa)

    @property
    def batente_fdc(self):        # quanto o C direito sobe acima dos outros para apertar a alavanca mais cedo
        return self.zc_max_guia - self.zc_max

    @property
    def patim_z(self):            # faixa do patim relativa a Zc: no fundo o patim encosta no inicio do trilho
        z0 = self.z_trilho[0] + 3.0 - self.zc_min   # 3 mm de trilho sobrando no fundo
        return (z0, z0 + 39.9)

    @property
    def x_ida(self):              # ramo da correia preso na cabine
        return self.x_polia + self.r_pitch

    @property
    def x_volta(self):            # ramo livre
        return self.x_polia - self.r_pitch


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


def geometria(p: P):
    g = []
    tf = math.tan(math.radians(p.incl_fila))
    yc = sum(p.y_correia) / 2
    # ------------------------------------------------ etapa 1: base e espinha
    caixa(g, "chao", "mundo", -40, 260, 20, 230, -18, 0, "fixa", "Bancada", "chao")
    caixa(g, "parede_dir", "mundo", 210, 228, 20, 200, 0, 420, "fixa", "Gabinete", "transp")
    # base com janela embaixo da polia de baixo (polia de 18 mm desce ate Z 1,5 com o esticador no fim)
    caixa(g, "base", "mundo", 172, 210, 174, 199, 0, 5, "fixa", "Base", "preto")
    caixa(g, "base_esq", "mundo", 172, 181, 158, 174, 0, 5, "fixa", "Base", "preto")
    caixa(g, "base_dir", "mundo", 200.5, 210, 158, 174, 0, 5, "fixa", "Base", "preto")
    caixa(g, "base_meio", "mundo", 181, 200.5, 158, 163.5, 0, 5, "fixa", "Base", "preto")
    caixa(g, "base_frente", "mundo", 188, 210, 112, 158, 0, 5, "fixa", "Base", "preto")
    # bochecha: segura a frente do parafuso da polia (porca presa dentro, rasgo vertical de 2 mm)
    caixa(g, "bochecha", "mundo", 185, 197, 159.5, 163.5, 5, 19, "fixa", "Base", "preto")
    caixa(g, "batente", "mundo", 200.5, 203.5, 159, 172, 5, p.zc_min + 10, "visual", "Batente", "acento")
    caixa(g, "batente_reforco", "mundo", 203.5, 205.5, 162, 169, 5, 18, "visual", "Batente", "acento")
    E = p.guia in ("eixos", "impressa")
    I = p.guia == "impressa"
    ye = p.y_eixos
    if I:
        gi, gs = "Guia impressa inferior", "Guia impressa superior"
        caixa(g, "pe_eixos", "mundo", 174.5, 207.5, 176.5, 199, 5, p.z_pe, "visual", gi, "preto")
        caixa(g, "cabeca_eixos", "mundo", 174.5, 207.5, 176.5, 199, p.fundo_cabeca, p.topo_cabeca, "visual", gs, "preto")
        for seg, z0, z1, pc in (("inf", 5, 200, gi), ("sup", 200, p.topo_cabeca, gs)):
            caixa(g, f"placa_{seg}", "mundo", 174.5, 207.5, 192, 199, z0, z1, "visual", pc, "preto")
            for lado, xr in zip(("esq", "dir"), p.x_eixos):
                caixa(g, f"trilho_{lado}_{seg}", "mundo", xr - 4, xr + 4, ye - 4, ye + 4, z0, z1, "visual", pc, "preto")
                caixa(g, f"pescoco_{lado}_{seg}", "mundo", xr - 2, xr + 2, ye + 4, 192, z0, z1, "visual", pc, "preto")
        # fins de curso: microchave KW10 (19,8 x 6,4 x 10,2) num rebaixo do pe e da cabeca, a alavanca toca o C direito
        hz0, hz1 = p.caixa_z
        z_alav_b = p.zc_min + hz0 + 0.6            # 0,6 mm acima do fundo do C com a cabine no batente
        z_alav_c = p.zc_max_guia + hz1 - 0.4       # alavanca onde sempre esteve (a guia de cima nao muda)
        caixa(g, "fdc_baixo", "mundo", 200, 206.4, 177, 196.8, 8.5, 18.7, "visual", "Fim de curso", "metal")
        caixa(g, "fdc_baixo_alav", "mundo", 204.4, 206, 179, 186, 18.7, z_alav_b, "visual", "Fim de curso", "metal")
        caixa(g, "fdc_cima", "mundo", 200, 206.4, 177, 196.8, 401.8, 412.0, "visual", "Fim de curso", "metal")
        caixa(g, "fdc_cima_alav", "mundo", 204.4, 206, 179, 186, z_alav_c, 401.8, "visual", "Fim de curso", "metal")
    elif E:
        caixa(g, "pe_eixos", "mundo", 174.5, 207.5, 176.5, 199, 5, p.z_pe, "visual", "Pe dos eixos", "preto")
        caixa(g, "cabeca_eixos", "mundo", 174.5, 207.5, 176.5, 199, p.fundo_cabeca, p.topo_cabeca, "visual", "Cabeca dos eixos", "preto")
        for lado, xr in zip(("esq", "dir"), p.x_eixos):
            cilindro(g, f"eixo_{lado}", "mundo", (xr, p.y_eixos, 202), 4.0, 200, "z", "visual", "Eixos 8 mm", "metal")
    else:
        caixa(g, "espinha_inf", "mundo", 177.5, 206, 188, 196, 5, 200, "visual", "Espinha inferior", "preto")
        caixa(g, "espinha_sup", "mundo", 177.5, 206, 188, 196, 200, 396, "visual", "Espinha superior", "preto")
        # ------------------------------------------------ etapa 2: trilho
        caixa(g, "trilho", "mundo", 186.5, 195.5, 181.5, 188, p.z_trilho[0], p.z_trilho[1], "visual", "Trilho MGN9", "metal")
    # ------------------------------------------------ etapa 3: cabine (relativa a Zc)
    Rb = rot(rx=p.incl_berco_y, ry=p.incl_berco_x)
    xb0, xb1 = p.x_berco_ini, p.x_parede_dir
    xbm, ybm = (xb0 + xb1) / 2, (130.5 + 156.5) / 2
    placa(g, "berco_piso", "carro", xb0, xb1, 130.5, 156.5, 3, Rb, p.z_piso_berco(xbm, ybm), "carro", "Cabine", "acento")
    caixa(g, "berco_dir", "carro", xb1, xb1 + 2, 130.5, 158.5, -1, 22, "carro", "Cabine", "acento")
    caixa(g, "berco_fundo", "carro", xb0, xb1 + 2, 156.5, 158.5, -1, 22, "carro", "Cabine", "acento")
    pz0, pz1 = p.patim_z
    caixa(g, "alma_esq", "carro", 178, 180.5, 158.5, 173, 10, 37, "carro", "Cabine", "acento")
    caixa(g, "bloco_dir", "carro", 188, 203.5, 158.5, 173, 10, 37, "carro", "Cabine", "acento")
    if I:
        hz0, hz1 = p.caixa_z
        c, w = p.folga_guia, 2.5
        a0, a1 = 4 + c, 4 + c + w            # face interna e externa do C
        caixa(g, "costas", "carro", 178, 203.5, 173, ye - a1 + 0.0, hz0, hz1, "carro", "Cabine", "acento")
        for lado, xr in zip(("esq", "dir"), p.x_eixos):
            caixa(g, f"aloj_{lado}_a", "carro", xr - a1, xr - a0, ye - a1, ye + a1, hz0, hz1, "carro", "Cabine", "acento")
            # o C direito (lado de fora) sobe 2,5 mm: aperta a alavanca do fim de curso de cima com a bola na altura da rampa
            hb = hz1 + (p.batente_fdc if lado == "dir" else 0.0)
            caixa(g, f"aloj_{lado}_b", "carro", xr + a0, xr + a1, ye - a1, ye + a1, hz0, hb, "carro", "Cabine", "acento")
            caixa(g, f"aloj_{lado}_c", "carro", xr - a1, xr + a1, ye - a1, ye - a0, hz0, hz1, "carro", "Cabine", "acento")
            caixa(g, f"aloj_{lado}_d", "carro", xr - a1, xr - 2 - c, ye + a0, ye + a1, hz0, hz1, "carro", "Cabine", "acento")
            caixa(g, f"aloj_{lado}_e", "carro", xr + 2 + c, xr + a1, ye + a0, ye + a1, hz0, hz1, "carro", "Cabine", "acento")
    elif E:
        hz0, hz1 = p.caixa_z
        for lado, xr in zip(("esq", "dir"), p.x_eixos):
            caixa(g, f"aloj_{lado}_a", "carro", xr - 9.5, xr - 7.5, ye - 9.5, ye + 9.5, hz0, hz1, "carro", "Cabine", "acento")
            caixa(g, f"aloj_{lado}_b", "carro", xr + 7.5, xr + 9.5, ye - 9.5, ye + 9.5, hz0, hz1, "carro", "Cabine", "acento")
            caixa(g, f"aloj_{lado}_c", "carro", xr - 9.5, xr + 9.5, ye - 9.5, ye - 7.5, hz0, hz1, "carro", "Cabine", "acento")
            caixa(g, f"aloj_{lado}_d", "carro", xr - 9.5, xr + 9.5, ye + 7.5, ye + 9.5, hz0, hz1, "carro", "Cabine", "acento")
            cilindro(g, f"bucha_{lado}", "carro", (xr, ye, hz0 + 14), 7.5, 12, "z", "carro_vis", "Rolamentos LM8UU", "metal")
    else:
        caixa(g, "costas", "carro", 178, 203.5, 173, 178, pz0, pz1, "carro", "Cabine", "acento")
        caixa(g, "patim", "carro", 181, 201, 178, 186, pz0, pz1, "carro_vis", "Patim MGN9H", "metal")
    # ------------------------------------------------ etapa 4: polia de baixo
    cilindro(g, "polia_baixo", "mundo", (p.x_polia, yc, p.z_polia_baixo), 9.0, 4.0, "y", "visual", "Polia de baixo", "metal")
    y_esp = 176.5 if E else 188
    cilindro(g, "espacador", "mundo", (p.x_polia, (172.5 + y_esp) / 2, p.z_polia_baixo), 2.5 if E else 3.0,
             (y_esp - 172.5) / 2, "y", "visual", "Espacador", "preto")
    # ------------------------------------------------ etapa 5: motor no topo
    zt = p.z_polia_cima
    if E:
        caixa(g, "sup_placa", "mundo", 172, 209, 127, 199, 415, 419, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_perna", "mundo", 174.5, 207.5, 176.5, 199, p.topo_cabeca, 415, "visual", "Suporte do motor", "preto")
        # orelha na parede direita (2 parafusos de madeira), presa na placa por um braco em cima e 2 almas de lado
        # que deixam livre o caminho da chave dos parafusos
        caixa(g, "sup_orelha", "mundo", 205, 210, 106, 135, 397, 419, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_orelha_baixo", "mundo", 205, 210, 106, 129.5, 393, 397, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_braco_orelha", "mundo", 199, 209, 106, 135, 413, 419, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_alma_orelha_0", "mundo", 201, 205, 106, 110, 395, 413, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_alma_orelha_1", "mundo", 201, 205, 123, 127, 395, 413, "visual", "Suporte do motor", "preto")
        # reforcos embaixo da placa (a placa de 4 mm torcia ao apertar os parafusos): faixa da frente com 10 mm,
        # travessa atras do motor e nervuras de 12 mm dos lados ate a cabeca da guia (fora da polia e da correia)
        caixa(g, "sup_frente", "mundo", 172, 209, 127, 140, 409, 415, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_travessa", "mundo", 172, 209, 150, 155.5, 410.5, 415, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_nervura_esq", "mundo", 172, 176, 150, 176.5, 403, 415, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_nervura_dir", "mundo", 205, 209, 150, 176.5, 403, 415, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_nervura_esq_f", "mundo", 172, 176, 127, 140, 403, 409, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_nervura_dir_f", "mundo", 205, 209, 127, 140, 403, 409, "visual", "Suporte do motor", "preto")
    else:
        caixa(g, "sup_placa", "mundo", 183, 199, 127, 196, 415, 419, "visual", "Suporte do motor", "preto")
        caixa(g, "sup_perna", "mundo", 183, 199, 188, 196, 396, 415, "visual", "Suporte do motor", "preto")
    caixa(g, "sup_abraco", "mundo", 182.0, 200.0, 127, 155, zt - 6.5, 415, "visual", "Suporte do motor", "preto")   # paredes de 3 mm
    caixa(g, "motor", "mundo", 185, 197, 124.5, 157, zt - 5, zt + 5, "visual", "Motor N20", "metal")
    cilindro(g, "polia_cima", "mundo", (p.x_polia, yc, zt), 9.0, 4.0, "y", "visual", "Polia do motor", "metal")
    cilindro(g, "cubo_cima", "mundo", (p.x_polia, 161.0, zt), 4.5, 3.5, "y", "visual", "Polia do motor", "metal")
    # ------------------------------------------------ etapa 6: correia (ramo livre fixo; o ramo preso anda com a cabine)
    caixa(g, "correia_volta", "mundo", p.x_volta - 0.7, p.x_volta + 0.7, p.y_correia[0], p.y_correia[1],
          p.z_polia_baixo, zt, "visual", "Correia", "correia")
    # ------------------------------------------------ etapa 7: tubo (frente transparente + laterais)
    zr = p.z_rampa
    yt = 172.5 if E else 196          # com eixos o tubo para antes dos alojamentos da cabine
    if E:
        caixa(g, "aba_tubo", "mundo", 188, 206, 121, 128, 5, 9, "fixa", "Tubo inferior", "transp")
        for lado, x0, x1, xw0, xw1 in (("esq", 172, 180, 175.5, 177.5), ("dir", 201, 209, 206, 208)):
            caixa(g, f"bloco_tubo_{lado}", "mundo", x0, x1, 140, 150, 404, 415, "fixa", "Tubo superior", "transp")
            caixa(g, f"haste_tubo_{lado}", "mundo", xw0, xw1, 140, 150, 396, 404, "fixa", "Tubo superior", "transp")
    for seg, z0, z1 in (("inf", 5, 200), ("sup", 200, 396)):
        peca = "Tubo inferior" if seg == "inf" else "Tubo superior"
        if seg == "inf":
            caixa(g, "frente_b", "mundo", 179.5, 208.0, 128, 130, z0, z1, "fixa", peca, "transp")
            caixa(g, "frente_c", "mundo", 175.5, 179.5, 128, 130, 25, z1, "fixa", peca, "transp")
            caixa(g, "esq_inf_tras", "mundo", 175.5, 177.5, 156.5, yt, z0, z1, "fixa", peca, "transp")
            caixa(g, "esq_inf_cima", "mundo", 175.5, 177.5, 130, 156.5, 50, z1, "fixa", peca, "transp")
        else:
            caixa(g, "frente_sup", "mundo", 175.5, 208.0, 128, 130, z0, zr, "fixa", peca, "transp")
            caixa(g, "esq_sup", "mundo", 175.5, 177.5, 130, yt, z0, z1, "fixa", peca, "transp")
        caixa(g, f"dir_{seg}", "mundo", 206.0, 208.0, 130, yt, z0, z1, "fixa", peca, "transp")
    # ------------------------------------------------ etapa 8: fila, comporta e rampa (bancada)
    Rf = rot(ry=p.incl_fila)
    xm = (p.x_fila_ini + p.x_fila_fim) / 2
    placa(g, "fila_piso", "mundo", p.x_fila_ini, p.x_fila_fim, 130, 130 + p.larg_fila, 3, Rf,
          p.zf_fim + (p.x_fila_fim - xm) * tf, "fixa", "Fila", "preto")
    caixa(g, "fila_frente", "mundo", p.x_fila_ini, 175.5, 128, 130, 25, 62, "fixa", "Fila", "transp")
    caixa(g, "fila_frente_baixo", "mundo", p.x_fila_ini, 171.5, 128, 130, 3, 25, "fixa", "Fila", "transp")
    caixa(g, "fila_fundo", "mundo", p.x_fila_ini, 171.5, 130 + p.larg_fila, 132 + p.larg_fila, 3, 62, "fixa", "Fila", "preto")
    caixa(g, "fila_fundo_fim", "mundo", 171.5, 175.5, 130 + p.larg_fila, 132 + p.larg_fila, 5.5, 62, "fixa", "Fila", "preto")
    caixa(g, "fila_inicio", "mundo", p.x_fila_ini - 2, p.x_fila_ini, 128, 158.5, 3, 62, "fixa", "Fila", "preto")
    Rr = rot(rx=p.incl_rampa)
    tr = math.tan(math.radians(p.incl_rampa))
    placa(g, "rampa", "mundo", 177.5, 206.0, 60, 128, 3, Rr, zr - (128 - 94) * tr, "fixa", "Rampa", "preto")
    caixa(g, "rampa_esq", "mundo", 175.5, 177.5, 58, 128, zr - 70 * tr - 4, zr + 22, "fixa", "Rampa", "transp")
    caixa(g, "rampa_dir", "mundo", 206.0, 208.0, 58, 128, zr - 70 * tr - 4, zr + 22, "fixa", "Rampa", "transp")
    caixa(g, "rampa_fim", "mundo", 177.5, 206.0, 58, 60, zr - 70 * tr - 4, zr + 22, "fixa", "Rampa", "acento")
    caixa(g, "suporte_servo", "mundo", 84, 116, 88, 116.5, 0, 21, "visual", "Suporte do servo", "preto")
    caixa(g, "servo", "mundo", 88.6, 111.4, 88, 116.5, 21, 33, "visual", "Servo", "metal")
    px, py, pz = p.piv
    L = lambda x0, x1, y0, y1, z0, z1: (x0 - px, x1 - px, y0 - py, y1 - py, z0 - pz, z1 - pz)
    xl = p.x_contato + p.lamina_dx
    ztl = p.zf_fim + p.lamina_topo
    A = "Braco da comporta"
    caixa(g, "alav_chifre", "alavanca", *L(92, 108, 116.5, 119, 23, 31), "alavanca", "Servo", "metal")
    caixa(g, "alav_braco", "alavanca", *L(95, xl + 0.75, 117, 125, 23, 27), "alavanca", A, "comporta")
    caixa(g, "alav_ponte", "alavanca", *L(175, xl + 0.75, 117, 132, 14, 23), "alavanca", A, "comporta")
    caixa(g, "alav_barra", "alavanca", *L(175.5, xl + 0.75, 117, 155, 11, 14), "alavanca", A, "comporta")
    # topo da lamina em chanfro (1,5 -> 0,8 em 2 mm), modelado em 2 degraus que cobrem o chanfro
    caixa(g, "alav_lamina", "alavanca", *L(xl - 0.75, xl + 0.75, 132, 152, 14, ztl - p.ponta_h), "alavanca", A, "comporta")
    caixa(g, "alav_ponta2", "alavanca", *L(xl - 0.6, xl + 0.6, 132, 152, ztl - p.ponta_h, ztl - p.ponta_h / 2),
          "alavanca", A, "comporta")
    caixa(g, "alav_ponta", "alavanca", *L(xl - p.ponta_e / 2 - 0.2, xl + p.ponta_e / 2 + 0.2, 132, 152, ztl - p.ponta_h / 2, ztl - 0.5),
          "alavanca", A, "comporta")
    caixa(g, "alav_ponta_topo", "alavanca", *L(xl - p.ponta_e / 2, xl + p.ponta_e / 2, 132, 152, ztl - 0.5, ztl),
          "alavanca", A, "comporta")
    return g


def fixadores(p: P):
    """Cada parafuso: onde a cabeca apoia (p0), direcao de entrada, comprimento util, quem prende quem,
    em que etapa entra e por quais furos de acesso a chave passa."""
    f = []

    def add(nome, tipo, p0, dir_, L, prende, rosca, etapa, acesso=(), insert=True, cab=5.5, atravessa=(), corpo="mundo"):
        f.append(dict(nome=nome, tipo=tipo, p0=list(p0), dir=list(dir_), L=L, prende=prende, rosca=rosca,
                      etapa=etapa, acesso=list(acesso), insert=insert, cab=cab, atravessa=list(atravessa), corpo=corpo))

    if p.guia in ("eixos", "impressa"):
        return fixadores_eixos(p, add) or f
    for i, x in enumerate((183.0, 200.5)):
        add(f"base_espinha_{i}", "M3x12", (x, 192.0, 0.0), (0, 0, 1), 12, "Base", "Espinha inferior", 1)
    z = p.z_trilho[0] + 10
    i = 0
    while z < p.z_trilho[1]:
        rosca = "Espinha inferior" if z < 200 else "Espinha superior"
        add(f"trilho_{i}", "M3x10", (191.0, 184.5, z), (0, 1, 0), 10, "Trilho MGN9", rosca, 2, acesso=("Patim MGN9H",))
        z += 20
        i += 1
    pz0, pz1 = p.patim_z
    zm = (pz0 + pz1) / 2
    for i, (x, dz) in enumerate(((183.5, -8), (198.5, -8), (183.5, 8), (198.5, 8))):
        add(f"cabine_patim_{i}", "M3x6", (x, 175.5, zm + dz), (0, 1, 0), 5.5, "Cabine", "Patim MGN9H", 3,
            acesso=("Cabine",), insert=False, corpo="carro")
    add("eixo_polia_baixo", "M3x35", (p.x_polia, 196.0, p.z_polia_baixo), (0, -1, 0), 35, "Espinha inferior",
        "Polia de baixo", 4, insert=False,
        atravessa=("Espacador",))
    for i, x in enumerate((186.0, 196.0)):
        add(f"suporte_espinha_{i}", "M3x12", (x, 192.0, 400.0), (0, 0, -1), 12, "Suporte do motor", "Espinha superior", 5,
            acesso=("Suporte do motor",))
    for lado, x0, d in (("esq", 175.5, 1), ("dir", 208.0, -1)):
        for i, z in enumerate((30, 160, 240, 380)):
            peca = "Tubo inferior" if z < 200 else "Tubo superior"
            esp = "Espinha inferior" if z < 200 else "Espinha superior"
            add(f"tubo_{lado}_{i}", "M3x8 chata", (x0, 192.0, z), (d, 0, 0), 8, peca, esp, 7, cab=6.0)
    return f


def fixadores_eixos(p: P, add):
    if p.guia == "impressa":
        gi, gs = "Guia impressa inferior", "Guia impressa superior"
        for i, x in enumerate((186.0, 196.0)):
            add(f"base_guia_{i}", "M3x12", (x, 195.5, 0.0), (0, 0, 1), 12, "Base", gi, 1)
        for i, x in enumerate((193.0, 205.0)):
            add(f"base_chao_{i}", "madeira 3,5x16", (x, 116.0, 5.0), (0, 0, -1), 16, "Base", "Bancada", 1, insert=False,
                cab=7.0)
        add("eixo_polia_baixo", "M3x40", (p.x_polia, 196.0, p.z_polia_baixo), (0, -1, 0), 40, gi,
            "Base", 4, insert=False, atravessa=("Espacador", "Polia de baixo"))
        for i, x in enumerate((186.0, 196.0)):
            add(f"suporte_guia_{i}", "M3x16", (x, 195.5, 419.0), (0, 0, -1), 16.0, "Suporte do motor", gs, 5)
        for i, z in enumerate((399.0, 409.0)):
            add(f"orelha_parede_{i}", "madeira 3,5x16", (205.0, 116.5, z), (1, 0, 0), 16, "Suporte do motor", "Gabinete", 5,
                insert=False, cab=7.0)
        for nome, z, pc, et in (("fdc_baixo", 13.6, gi, 1), ("fdc_cima", 406.9, gs, 3)):
            for i, y in enumerate((182.15, 191.65)):
                add(f"{nome}_{i}", "M2x12", (207.5, y, z), (-1, 0, 0), 12.0, "Fim de curso", pc, et, insert=False,
                    cab=3.8, acesso=(pc, "Gabinete"))     # na bancada, antes de a guia ir para o gabinete
        for i, x in enumerate((176.0, 205.0)):
            add(f"suporte_tubo_{i}", "M3x12", (x, 145.0, 419.0), (0, 0, -1), 12, "Suporte do motor", "Tubo superior", 7)
        for i, x in enumerate((192.0, 201.5)):
            add(f"tubo_base_{i}", "M3x10", (x, 124.5, 9.0), (0, 0, -1), 10, "Tubo inferior", "Base", 7)
        return None
    for i, x in enumerate((179.0, 203.0)):
        add(f"base_pe_{i}", "M3x12", (x, 190.0, 0.0), (0, 0, 1), 12, "Base", "Pe dos eixos", 1)
    for lado, xr in zip(("esq", "dir"), p.x_eixos):
        add(f"trava_pe_{lado}", "M3x10 sem cabeca", (xr, 197.0, 12.5), (0, -1, 0), 10.6, "Pe dos eixos", "Pe dos eixos", 2,
            atravessa=("Eixos 8 mm",), cab=3.0)
        add(f"trava_cabeca_{lado}", "M3x10 sem cabeca", (xr, 197.0, 395.0), (0, -1, 0), 10.6, "Cabeca dos eixos",
            "Cabeca dos eixos", 3, atravessa=("Eixos 8 mm",), cab=3.0)
    add("eixo_polia_baixo", "M3x35", (p.x_polia, 196.0, p.z_polia_baixo), (0, -1, 0), 35, "Pe dos eixos",
        "Polia de baixo", 4, insert=False, atravessa=("Espacador",))
    for i, x in enumerate((179.0, 203.0)):
        add(f"suporte_cabeca_{i}", "M3x25", (x, 190.0, 419.0), (0, 0, -1), 25, "Suporte do motor", "Cabeca dos eixos", 5)
    for i, x in enumerate((176.0, 205.0)):
        add(f"suporte_tubo_{i}", "M3x12", (x, 145.0, 419.0), (0, 0, -1), 12, "Suporte do motor", "Tubo superior", 7)
    for i, x in enumerate((192.0, 202.0)):
        add(f"tubo_base_{i}", "M3x8", (x, 124.5, 9.0), (0, 0, -1), 8, "Tubo inferior", "Base", 7)
    return None


def ancoras(p: P):
    return {"zc_min": p.zc_min, "zc_espera": p.zc_espera, "zc_topo": p.zc_topo, "zc_max": p.zc_max,
            "x_bola": p.x_bola, "x_contato": p.x_contato}
