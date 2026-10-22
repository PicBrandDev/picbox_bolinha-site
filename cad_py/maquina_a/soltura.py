"""Geometria compartilhada da soltura (alcapao duplo simetrico) no carro A.

Coordenadas da MAQUINA (Z up), com o carro A em x=0. A placa do carro A05 fica por cima: a face da carga
(virada para baixo no eixo A) esta em z = Z_EIXO_A - A05.Z1.

Conceito (usuario: alcapao duplo simetrico): a bola de 38 mm fica num "V" de 120 graus formado por duas
portinholas articuladas em eixos paralelos a X, a +-22,5 mm do centro. As portinholas tem setores de
engrenagem (m1,5, 30 dentes, raio primitivo 22,5) que engrenam no centro: abrem exatamente iguais. O solenoide
puxa uma alavanca de 9,5 mm na portinhola de tras: 9,5 mm de curso = 60 graus. A bola entra rolando pelo lado
-X (calha de carga do magazine, carro em x=-140) e para no batente do lado +X.
"""
import math

from maquina_a import layout as L
from maquina_a.parts import A05_placa_carro as P

Y_C = L.Y_JOGO                         # CENA -57
Z_C = L.Z_BOLA_SOLTURA                 # PARAMS 1470
R_B = L.BOLA_R                         # MEDIDO 19
Z_FACE_CARRO = L.Z_EIXO_A - P.Z1       # 1515 face da carga da placa A05 (virada para baixo)

ANG_CONTATO = 30.0                     # ESTIMADO V de 120 graus (contato a 30 graus da vertical)
MODULO, DENTES = 1.5, 34               # ESTIMADO engrenagem impressa; raio 25,5 deixa o no fora da bola (2,5 mm)
R_PRIM = MODULO * DENTES / 2           # 22,5 = distancia do eixo ao centro (y)
E_PORT = 3.0                           # FAB espessura da portinhola (E_FINA arredondada)
D_NO = 7.0                             # ESTIMADO diametro do no da articulacao (furo M3, parede 1,8)
Y_OFF_BORDA = 1.0                      # ESTIMADO meia-fenda entre as bordas internas fechadas

X_PORT = (-20.5, 21.0)                 # ESTIMADO comprimento util da portinhola (bola no meio, 2 mm de folga em x)
X_ENGR = (21.0, 25.0)                  # ESTIMADO plano dos setores de engrenagem
X_BOCH_E = (-24.0, -21.0)              # ESTIMADO bochecha da entrada (3 mm: a cabeca do M3 da placa em x=-27 passa ao lado)
X_BOCH_D = (25.5, 29.5)                # ESTIMADO bochecha do batente/solenoide (solenoide ate x=54,5: 1,3 mm do pe A01 no fim do curso)

ABERTURA = 60.0                        # ESTIMADO rotacao de cada portinhola ao abrir
R_ALAV = 9.5                           # ESTIMADO alavanca: 9,5 mm de curso vertical = 60 graus (-30 -> +30)
ANG_ALAV_FECHADO = -30.0               # graus, a partir de +y, no plano (y, z)


def z_superficie(y_off):
    """Topo da portinhola fechada (linha de contato), em funcao da distancia ao centro em y."""
    a = math.radians(ANG_CONTATO)
    y_ct, z_ct = R_B * math.sin(a), Z_C - R_B * math.cos(a)
    return z_ct + (y_off - y_ct) * math.tan(a)


Z_EIXO = z_superficie(R_PRIM) - (E_PORT / 2) / math.cos(math.radians(ANG_CONTATO))   # eixo no meio da espessura
Y_EIXO = {"t": Y_C + R_PRIM, "f": Y_C - R_PRIM}      # tras (+y) e frente (-y)
SENTIDO_ABRE = {"t": +1, "f": -1}                    # rotacao positiva em torno de +x abre a de tras


def pino_alavanca(angulo_abertura=0.0):
    """Centro do pino da alavanca (portinhola de tras), no plano (y, z)."""
    a = math.radians(ANG_ALAV_FECHADO + angulo_abertura)
    return (Y_EIXO["t"] + R_ALAV * math.cos(a), Z_EIXO + R_ALAV * math.sin(a))


Y_PINO, Z_PINO_FECHADO = pino_alavanca(0.0)
Z_PINO_ABERTO = pino_alavanca(ABERTURA)[1]
CURSO_PINO = Z_PINO_ABERTO - Z_PINO_FECHADO          # ~9,5

# solenoide (ESTIMADO): face de fixacao na bochecha +X, embolo vertical para baixo sobre o pino
X_SOL_FACE = X_BOCH_D[1]
X_EMBOLO = X_SOL_FACE + 25.0 / 2
GARFO_H = 8.0                                        # ESTIMADO altura do garfo no embolo
Z_SOL_BASE = Z_PINO_FECHADO + GARFO_H / 2 + CURSO_PINO + 0.5   # face do embolo do solenoide
