"""Contexto do eixo linear (referencial local, ver layout.py) e passagem para a maquina."""
import cadquery as cq
import numpy as np

from common import fab, hardware as hw
from . import layout as L

Y_POLIA_MOTOR = L.Y_FACE_PLACA_MOTOR - 0.5 - hw.POLIA_20T_L   # CENA polia de y 19 a 35
Y_TENSORA = L.Y_CORREIA                                       # ESTIMADO tensora centrada no plano da correia (A02/A04)
# FC: a ponta da alavanca encosta direto na ponta da placa do carro (A05, meia-largura 32) em x carro = 141
# (CENA: livre 141, clique 143, fundo 144,2). Costas da placa = 141 + 32 + 1,6 + 11,06 (alavanca)
X_COSTAS_FC = 186.1                                           # ESTIMADO (antes 181,5 com batente na placa); toque em 141,0
Z_FC = 34.0                                                   # ESTIMADO ponta da alavanca em z=12,3, meio da ponta da placa


def para_maquina(obj, eixo):
    """Leva um Workplane/Shape do referencial do eixo para a maquina (A = espelho em z)."""
    sh = obj.val() if isinstance(obj, cq.Workplane) else obj
    if eixo == "A":
        sh = sh.mirror("XY").translate((0, 0, L.Z_EIXO_A))
    else:
        sh = sh.translate((0, 0, L.Z_EIXO_B))
    return cq.Workplane("XY").add(sh)


def ponto_para_maquina(p, eixo):
    T = L.eixo_para_maquina(eixo)
    return tuple((T @ np.array([*p, 1.0]))[:3])


def dir_para_maquina(d, eixo):
    T = L.eixo_para_maquina(eixo)
    return tuple(T[:3, :3] @ np.array(d))


def fixos(eixo, lado_fc=(1, -1)):
    """Compradas fixas do eixo no referencial local: nome -> Workplane."""
    c = {
        "perfil": hw.perfil(L.PERFIL_COMP, L.PERFIL_Z),
        "trilho": hw.trilho(L.TRILHO_COMP),
        "nema": hw.nema17(L.X_POLIA, L.Y_FACE_PLACA_MOTOR + fab.E_PLACA),
        "polia": hw.polia_20t(L.X_POLIA, Y_POLIA_MOTOR),
        "tensora": hw.tensora(-L.X_POLIA, Y_TENSORA),
        "correia": hw.correia_eixo(L.X_POLIA, -L.X_POLIA, L.Y_CORREIA),
    }
    for s in lado_fc:
        c[f"fc{'+' if s > 0 else '-'}"] = hw.fim_de_curso(s * X_COSTAS_FC, Z_FC, sentido=-s)
    return c


def lados_fc(eixo):
    # CENA: eixo B tem FC nas duas pontas; no A so na ponta do motor (a calha de carga passa no tensor)
    return (1, -1) if eixo == "B" else (1,)
