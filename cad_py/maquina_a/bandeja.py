"""Bandeja da Maquina A (coordenadas da maquina).

Recolhe a bola que cai da boca (acerto ou erro) na frente do eixo B e leva ao canto frente-direita, onde o tubo do
elevador (maquina_a/elevador.py) atravessa a bandeja e a divisoria: a bola entra pelo furo do pe do tubo (soleira
abaixo do EVA). A bola de 38 mm nao passa por baixo do perfil do eixo B, entao a bandeja fica na frente dele,
limitada por um rodape (A13).
Placa de MDF 6 (corte) + EVA 3 (usuario) apoiadas em calcos impressos (A12) com o topo inclinado.

Inclinacao: o canto alto (tras-esquerda) fica limitado pela placa do carro B (z=1184): a bola ali passa com ~1,4 mm.
"""
import math

from maquina_a import layout as L

EVA = 3.0                              # usuario: forro de EVA 3 mm
MDF = 6.0                              # CENA placa da bandeja (MDF 6, corte)
Z_DIVISORIA = L.Z_DIVISORIA            # CENA 1100 topo da divisoria
CALCO_MIN = 3.0                        # FAB calco mais baixo
INCL_X = math.radians(3.5)             # ESTIMADO desce para +x
INCL_Y = math.radians(3.0)             # ESTIMADO desce para a frente (-y)
X_BAND = (-205.0, 205.0)               # ESTIMADO 2 mm das laterais
Y_BAND = (-205.0, -20.0)               # ESTIMADO da frente (painel) ate o rodape
Y_RODAPE = (-23.0, -20.0)              # ESTIMADO rodape (a bola nao chega na aba do berco do perfil B em y=-18)
X_RODAPE = (-194.0, 194.0)             # ESTIMADO livre das cabecas dos M4 dos pes dos eixos (x>=196)
H_RODAPE = 22.0                        # ESTIMADO acima do EVA (3 acima do centro da bola; topo ~16 mm abaixo da placa do carro B)
X_RECORTE = (199.0,)                   # ESTIMADO recorte 6 x 9 nos cantos de tras da placa e do EVA (pe dos blocos)
Y_RECORTE = -29.0
X_LOW, Y_LOW = X_BAND[1], Y_BAND[0]    # canto mais baixo
Z_EVA_LOW = Z_DIVISORIA + CALCO_MIN + MDF + EVA + 0.0   # 1112 topo do EVA no canto baixo


def z_eva(x, y):
    """Topo do EVA (onde a bola rola)."""
    return Z_EVA_LOW + (X_LOW - x) * math.tan(INCL_X) + (y - Y_LOW) * math.tan(INCL_Y)


def z_mdf_baixo(x, y):
    return z_eva(x, y) - EVA - MDF


# calcos: (x, y) dos centros; cada um tem altura propria
CALCOS = [(-185.0, -190.0), (-185.0, -40.0), (0.0, -190.0), (0.0, -40.0), (75.0, -195.0), (185.0, -40.0)]   # ESTIMADO (75: fora do tubo do elevador)
