"""Layout da Maquina A: cotas de montagem compartilhadas entre pecas.

Sistema CAD (ver common/coords.py): Z up, X direita do jogador, Y para o fundo, origem no centro do piso.
Cada constante tem UMA tag de origem. params.json e gerado de js/params.js; medidas.json
(valores informados pelo usuario) vale por cima dele e esta listado em PENDENCIAS.md.
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_P = json.loads((AQUI / "params.json").read_text(encoding="utf8"))["valores"]
_M = json.loads((AQUI / "medidas.json").read_text(encoding="utf8"))


def p(chave):
    if chave in _M:
        return _M[chave]["v"]
    return _P[chave]["v"]


# ------------------------------------------------------------------ bola e jogo
BOLA_D = p("ball.d")                    # MEDIDO (medidas.json) 38
BOLA_R = BOLA_D / 2
BOLA_MASSA_G = p("ball.m")              # MEDIDO 60
BOCA_D = p("boca.d")                    # MEDIDO (usuario) 50
QUEDA = p("geo.h")                      # PARAMS 250: centro da bola na soltura -> plano da boca
CURSO_A = p("A.stroke")                 # PARAMS 280
CURSO_B = p("B.stroke")                 # PARAMS 280
SEP_EIXOS = p("geo.sep")                # PARAMS 355

# ------------------------------------------------------------------ gabinete
GAB_LADO = p("geo.floor")               # PARAMS 450
GAB_ALTURA = p("geo.height")            # PARAMS 1700
MDF_GAB = 18.0                          # CENA (gabinete.mjs)
PAREDE_X = GAB_LADO / 2 - MDF_GAB       # PARAMS 207 = face interna das laterais (geo.inner 415 diverge: PENDENCIAS)
PAREDE_Y = GAB_LADO / 2 - MDF_GAB       # PARAMS 207
Z_DIVISORIA = 1100.0                    # CENA topo da divisoria do campo
Z_TESTEIRA = 1550.0                     # CENA

# ------------------------------------------------------------------ plano de jogo e eixos
Y_JOGO = -57.0                          # CENA plano vertical da bola e do centro da boca
Z_EIXO_B = 1175.0                       # CENA meio da altura do trilho B
Z_EIXO_A = Z_EIXO_B + SEP_EIXOS         # PARAMS 1530 (geo.sep; antes literal)
RECUO_SOLTURA = 60.0                    # CENA centro da bola abaixo do eixo A
Z_BOLA_SOLTURA = Z_EIXO_A - RECUO_SOLTURA   # 1470
Z_BOCA = Z_BOLA_SOLTURA - QUEDA         # PARAMS 1220 (queda 250 fixa, usuario)
RECUO_BOCA = Z_BOCA - Z_EIXO_B          # 45

# ------------------------------------------------------------------ eixo linear (referencial local do eixo)
# x ao longo do trilho (0 = meio), y=0 centro do trilho, z=0 meio da altura do trilho.
# Eixo B: local -> maquina = translacao z+Z_EIXO_B. Eixo A: espelho em z, depois z+Z_EIXO_A.
PERFIL_Z = -14.0                        # CENA centro do perfil 2020 (trilho apoiado no topo, z=-4)
PERFIL_COMP = 400.0                     # CENA
TRILHO_COMP = 400.0                     # CENA
TRILHO_BASE_Z = -4.0                    # CENA
PATIM_TOPO_Z = 9.0                      # CATALOGO MGN12H H=13 sobre a base do trilho
X_POLIA = 178.0                         # CENA centro do motor / polia tensora (+ motor, - tensor)
Y_CORREIA = 23.5                        # CENA plano medio da correia GT2 6 mm (atras do patim)
Y_FACE_PLACA_MOTOR = 35.5               # CENA face da frente da placa do motor (cubo da polia em 35)
X_PE = 200.0                            # CENA face interna do pe (perfil termina aqui)
CURSO_REF = 144.2                       # CENA curso ate o clique do fim de curso (home)
CURSO_JOGO = CURSO_A / 2                # PARAMS 140

# ------------------------------------------------------------------ espaco atras do eixo
Y_LIVRE_ATRAS_A = 40.5                  # CENA no eixo A nada atras disto no lado do tensor (magazine)


def eixo_para_maquina(eixo):
    """Matriz 4x4 (numpy) do referencial local do eixo para a maquina."""
    import numpy as np
    T = np.eye(4)
    if eixo == "B":
        T[2, 3] = Z_EIXO_B
    else:
        T[2, 2] = -1.0
        T[2, 3] = Z_EIXO_A
    return T
