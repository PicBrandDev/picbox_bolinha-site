"""A08 — Gabarito de centragem do trilho (ferramenta, nao fica na maquina).

Intencao:
- Funcao: abraca o perfil 2020 e o trilho MGN12 para o trilho ficar centrado no perfil enquanto se apertam os M3.
  Usar 2 ou 3 ao longo do trilho; retirar antes de montar o patim.
- Interfaces: perfil 20 (encaixe justo), trilho 12 (encaixe justo).
Impressao: deitada na face lateral (perfil em U na horizontal), sem suporte.
"""
import cadquery as cq

from common import fab, hardware as hw
from common.features import caixa
from maquina_a import layout as L
from maquina_a import eixo as E

ID = "A08"
NOME = "gabarito"
TITULO = "Gabarito de centragem do trilho (ferramenta)"
QTD = {"B": 2}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = None
NO_EIXO = False
FERRAMENTA = True
EIXOS_CONTEXTO = ["B"]
X_USO = -100.0                        # posicao de exemplo ao longo do trilho (so para checar o encaixe)
LARG = 12.0                           # ESTIMADO ao longo do trilho
E_G = fab.E_GROSSA


def local(var="B"):
    pm = hw.PERFIL_LADO / 2 + fab.ENCAIXE_JUSTO
    tm = hw.TRILHO_L / 2 + fab.ENCAIXE_JUSTO
    z_trilho = L.TRILHO_BASE_Z + hw.TRILHO_H          # topo do trilho (4)
    z_aba = z_trilho - 2.0                              # abas internas abracam 6 mm do trilho
    z_ponte = (z_trilho + 0.5, z_trilho + 0.5 + E_G)    # ponte acima do trilho, sem encostar
    z_baixo = L.PERFIL_Z - 4.0                          # desce 6 mm nas laterais do perfil
    g = caixa(-LARG / 2, LARG / 2, -pm - E_G, pm + E_G, z_baixo, z_ponte[1])
    g = g.cut(caixa(-LARG, LARG, -pm, pm, z_baixo - 1, L.TRILHO_BASE_Z))          # perfil
    g = g.cut(caixa(-LARG, LARG, -tm, tm, L.TRILHO_BASE_Z - 0.1, z_ponte[0]))    # trilho
    g = g.cut(caixa(-LARG, LARG, -pm, pm, z_aba, z_ponte[0]))                    # acima das abas
    return g.edges("|X").fillet(fab.R_DETALHE * 2).translate((X_USO, 0, 0))


def build(p=None, var="B"):
    return E.para_maquina(local(var), "B")


def impressao(var="B"):
    sh = local(var).val().rotate((0, 0, 0), (0, 1, 0), 90)
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="B"):
    return []


FICHA = dict(orientacao="deitada na face lateral", suporte="nao", perimetros=4, infill="40%", camada=0.20,
             montagem="encaixar sobre trilho e perfil, apertar os M3 do trilho, retirar.")
