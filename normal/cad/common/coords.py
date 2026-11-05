"""Sistemas de coordenadas.

CAD (este projeto): Z para cima, mm. X = direita do jogador, Y = para o FUNDO
(a frente da maquina fica em -Y), origem no centro do piso do gabinete, z=0 no chao.

Three.js (simulacao, guia.json, GLB): Y para cima, mm (calibrado: maquina = 450 x 1700 x 468),
+Z aponta para o jogador. Matrizes de instancia do guia.json sao 4x4 coluna-maior.

    CAD(x, y, z) = three(x, -z, y)        three(x, y, z) = CAD(x, z, -y)
"""
import numpy as np

# leva um ponto three -> CAD
THREE_PARA_CAD = np.array([
    [1, 0, 0, 0],
    [0, 0, -1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
], dtype=float)
CAD_PARA_THREE = np.linalg.inv(THREE_PARA_CAD)


def matriz_guia(m16):
    """Matriz de instancia do guia.json (coluna-maior, three) -> 4x4 numpy (three)."""
    return np.array(m16, dtype=float).reshape(4, 4).T


def instancia_para_cad(m16):
    """Transformacao de uma malha GLB (coordenadas three locais) para o CAD da maquina."""
    return THREE_PARA_CAD @ matriz_guia(m16)
