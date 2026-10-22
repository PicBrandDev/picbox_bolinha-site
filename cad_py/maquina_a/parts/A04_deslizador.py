"""A04 — Deslizador da polia tensora (eixos A e B, mesma peca).

Intencao:
- Funcao: leva a polia tensora GT2 20T num M5 em balanco; corre na prateleira do A02 (lingua na canaleta).
- Cargas: tracao da correia (~30 N) -> ponta do M3 tensor; momento do M5 em balanco.
- Interfaces: tensora (M5x20 + 2 arruelas, porca autotravante embutida atras), A02 (lingua, M3 de trava com porca
  embutida, ponta do M3 tensor na face de dentro).
Impressao: deitada na face de tras (y=40,5), lingua de lado; sem suporte.
"""
import cadquery as cq

from common import fab
from common.features import caixa, cilindro, bolsao_porca, teardrop
from maquina_a import layout as L
from maquina_a import eixo as E
from maquina_a.parts import A02_bloco_tensor as T

ID = "A04"
NOME = "deslizador"
TITULO = "Deslizador da polia tensora"
QTD = {"B": 1, "A": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = "eixo_deslizador"
ESTRUTURAL = True
CONTATO_ESPERADO = ()
JUSTIFICATIVA = "deslizador novo: corre sobre a prateleira do A02 e e puxado por um M4 que vem de fora da lateral"

X_C = T.X_POLIA                       # CENA 178 (posicao nominal, lado +x antes do espelho)
Y0, Y1 = T.DESL_Y0, T.Y_TRAS
Z0, Z1 = T.DESL_Z
PORCA_M5_Y = 38.25                    # ESTIMADO topo da porca = ponta do M5x20 (cabeca apoiada em y=18,25)


def _local_mais_x():
    xa, xb = T.DESL_X
    d = caixa(xa, xb, Y0, Y1, Z0, Z1)
    d = d.edges("|Y").fillet(fab.R_EXTERNO).faces(">Y or <Y").edges().fillet(fab.R_DETALHE)
    # lingua de guia embaixo
    w = T.LINGUA[0] / 2
    d = d.union(caixa(xa, xb, T.Y_LINGUA - w, T.Y_LINGUA + w, Z0 - T.LINGUA[1], Z0 + 0.5))
    # M5 da tensora em z=0 + porca autotravante embutida por tras
    d = d.cut(cilindro(fab.FURO_PASSANTE["M5"], Y1 - Y0 + 2, (X_C, Y0 - 1, 0), (0, 1, 0)))
    s, h = fab.PORCA_NYLON_M5
    d = d.cut(cq.Workplane(cq.Plane(origin=(X_C, Y1 + 0.5, 0), xDir=(1, 0, 0), normal=(0, -1, 0)))
              .polygon(6, s / 0.8660254).extrude(Y1 + 0.5 - (PORCA_M5_Y - h)))
    # porca M3 da trava: assento 3 mm acima da base, entra por um canal na face da frente
    zp = Z0 + 3.0
    xt = T.X_TRAVA
    s3, h3 = fab.BOLSAO_PORCA["M3"]
    d = d.cut(cilindro(fab.FURO_PASSANTE["M3"], zp + h3 + 0.6 - (Z0 - T.LINGUA[1] - 1), (xt, T.Y_LINGUA, Z0 - T.LINGUA[1] - 1), (0, 0, 1)))
    d = d.cut(bolsao_porca("M3", (xt, T.Y_LINGUA, zp), (0, 0, 1), angulo=0.0))
    d = d.cut(caixa(xt - s3 / 2, xt + s3 / 2, Y0 - 1, T.Y_LINGUA, zp, zp + h3))
    # porca M4 do tensor: o M4 vem da parede (+x) e puxa; a porca apoia na parede do lado de fora
    s4, h4 = fab.BOLSAO_PORCA["M4"]
    xn = xb - 4.4 - h4
    d = d.cut(cilindro(fab.FURO_PASSANTE["M4"], xb - xn + 5 + 1, (xn - 5, T.Y_TENSOR, T.Z_TENSOR), (1, 0, 0)))
    d = d.cut(bolsao_porca("M4", (xn, T.Y_TENSOR, T.Z_TENSOR), (1, 0, 0), angulo=0.0))
    d = d.cut(caixa(xn, xn + h4, Y0 - 1, T.Y_TENSOR, T.Z_TENSOR - s4 / 2, T.Z_TENSOR + s4 / 2))
    return d


def local(eixo="B"):
    return cq.Workplane("XY").add(_local_mais_x().val().mirror("YZ"))


def build(p=None, eixo="B"):
    return E.para_maquina(local(eixo), eixo)


def impressao(eixo="B"):
    sh = _local_mais_x().val()
    sh = sh.rotate((0, 0, 0), (1, 0, 0), -90)      # face de tras (y=40,5) para baixo
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def fixadores(var="B"):
    return [dict(nome="tensora", tipo="ISO7380", bitola="M5", comp=20, ponto=(-X_C, Y0 - T.TENSORA_L - 2 * T.ARRUELA_M5, 0),
                 dir=(0, 1, 0), antes_de=("trilho", "perfil", "patim", "placa", "garra", "presilha", "boca", "berco"),
                 extra="2 arruelas M5 + porca M5 autotravante embutida")]


def pares_furos(var):
    from common import hardware as hw
    f = fixadores(var)[0]
    return [("eixo da tensora", (E.ponto_para_maquina(f["ponto"], var), E.dir_para_maquina(f["dir"], var)),
             (E.ponto_para_maquina((-L.X_POLIA, E.Y_TENSORA, 0), var), E.dir_para_maquina((0, 1, 0), var)))]


FICHA = dict(orientacao="deitada na face de tras", suporte="nao", perimetros=4, infill="40% gyroid (estrutural)", camada=0.20,
             montagem="porca M5 autotravante no bolsao de tras; porcas M3 e M4 pelos canais da frente; tensora no M5x20 com arruelas; vai no A02.")
