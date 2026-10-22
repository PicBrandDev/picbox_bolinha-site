"""Parametros de fabricacao e linguagem de forma. Nenhuma peca usa numero solto
de folga, raio ou espessura: tudo vem daqui (tag # FAB)."""

# ------------------------------------------------------------------ impressoras
# altura das 220 informada pelo usuario (250); a da 260 e a do build antigo (300)
IMPRESSORAS = {
    "260": (260.0, 260.0, 300.0),
    "220": (220.0, 220.0, 250.0),
}
MESA_PADRAO = "220"          # toda peca deve caber na menor, se possivel

PERFIL_IMPRESSAO = {
    "material": "PETG", "bico": 0.4, "camada": 0.20, "camada_fina": 0.16,
    "perimetros": 4, "infill": "20% gyroid", "infill_estrutural": "40% gyroid",
    "densidade_g_cm3": 1.27, "vazao_g_h": 11.0, "preparo_h": 0.2,
}

# ------------------------------------------------------------------ furos e fixadores
FURO_PASSANTE = {"M2": 2.4, "M3": 3.4, "M4": 4.5, "M5": 5.5}
FURO_AUTOATARRAXANTE = {"M2": 1.8, "M3": 2.6}
# porca sextavada: (entre faces do bolsao, profundidade)
BOLSAO_PORCA = {"M2": (4.4, 1.9), "M3": (5.9, 2.8), "M4": (7.4, 3.6), "M5": (8.4, 4.4)}
PORCA_NYLON_M5 = (8.4, 5.4)
# rebaixo de cabeca DIN 912: (diametro, profundidade)
REBAIXO_DIN912 = {"M2": (4.4, 2.3), "M3": (6.2, 3.3), "M4": (7.8, 4.3), "M5": (9.2, 5.3)}
# ISO 7380 (cabeca abaulada): (diametro, altura)
CABECA_ISO7380 = {"M3": (5.7, 1.65), "M4": (7.6, 2.2), "M5": (9.5, 2.75)}

ENCAIXE_DESLIZANTE = 0.30     # por lado
ENCAIXE_JUSTO = 0.15          # por lado
ROLAMENTO_PRENSADO = 0.10     # no diametro
TEARDROP_ACIMA_DE = 5.0       # furo horizontal maior que isso vira gota

# ------------------------------------------------------------------ paredes e impressao
PAREDE_MIN = 1.6
PAREDE_ESTRUTURAL = 2.4
FUNDO_BOLSAO = 1.2
OVERHANG_MAX_GRAUS = 45.0
PONTE_MAX = 10.0
CHANFRO_BASE = 0.5            # aresta que toca a mesa (nunca filete)
CHANFRO_ENTRADA = 1.0         # entrada de furo e de encaixe
TEXTO_ALTURA = 0.6
TEXTO_TRACO = 0.8

# ------------------------------------------------------------------ linguagem de forma
R_DETALHE = 0.5
R_EXTERNO = 1.5
R_VISIVEL = 3.0               # peca vista pelo jogador ou ponto de pega
R_INTERNO = 1.0
ESPESSURAS = (2.4, 3.2, 4.0, 6.0, 8.0)   # 6 e 8 so em placas estruturais
E_FINA, E_MEDIA, E_GROSSA = 2.4, 3.2, 4.0
E_PLACA, E_PLACA_GROSSA = 6.0, 8.0
NERVURA_FATOR = 0.7           # nervura = 0,6..0,8 x parede

# ------------------------------------------------------------------ bola
FOLGA_BOLA_RADIAL = 1.5       # canal: raio = raio da bola + isto
DEGRAU_MAX_BOLA = 0.2
ENTRADA_BOLA = 3.0            # raio/chanfro minimo na entrada de funil/boca

# ------------------------------------------------------------------ verificacao
TOL_LINEAR = 0.02
TOL_ANGULAR = 0.1
INTERFERENCIA_MAX_MM3 = 0.01
FOLGA_MOVIMENTO = 1.0
PASSO_VARREDURA = 5.0
EXCENTRICIDADE_MAX = 0.05
DELTA_INTENCAO = 2.0
