"""A02 — Bloco de ponta do tensor (eixos A e B).

Intencao:
- Funcao: pe na lateral esquerda; apoia a ponta do perfil 2020 e guia o deslizador A04 da polia tensora.
  Eixo B leva o modulo FC de home do lado esquerdo; eixo A nao (a calha de carga passa ali).
- Cargas: tracao da correia (~30 N) no deslizador -> prateleira; estatico.
- Interfaces: parede x=-207 (4x M4 + porca-garra), perfil (M5 na aba da frente + M5 no piso), deslizador A04
  (lingua na canaleta da prateleira, M3 de trava por baixo); M4 tensor por fora da lateral do gabinete.
- Restricao de layout: nada atras de y=40,5 (no eixo A o magazine passa atras); nada acima de z=8 na regiao do carro.
Desenhada no lado +x (como o A01) e espelhada em x.
Impressao: deitada na face do pe.
"""
import cadquery as cq

from common import fab
from common.features import caixa, cilindro, teardrop, bolsao_porca
from maquina_a import layout as L
from maquina_a import eixo as E
from maquina_a.parts import A01_bloco_motor as A01

ID = "A02"
NOME = "bloco_tensor"
TITULO = "Bloco de ponta do tensor"
QTD = {"B": 1, "A": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = {"B": "eixo_bloco_tensor", "A": "eixo_bloco_tensor_semfc"}
ESTRUTURAL = True
JUSTIFICATIVA = ("pe mais largo (mesmo do A01); tensor redesenhado: deslizador corre numa prateleira abaixo do carro, "
                 "sem a orelha de parede fina da referencia; nada passa de y=40,5")

# ------------------------------------------------------------------ cotas (lado +x, referencial local do eixo B)
X_POLIA = L.X_POLIA                   # CENA 178 centro da tensora (espelhado: -178)
Y_CORREIA = L.Y_CORREIA               # CENA 23,5
Y_TRAS = L.Y_LIVRE_ATRAS_A            # CENA 40,5 limite de tras
TENSORA_L = 8.5                       # CATALOGO polia tensora 20T
ARRUELA_M5 = 1.0                      # CATALOGO arruela M5 fina

DESL_Y0 = Y_CORREIA + TENSORA_L / 2 + ARRUELA_M5     # 28,75 face da frente do deslizador
DESL_Z = (-12.0, 7.0)                 # ESTIMADO 2 mm abaixo do carro (z=9)
DESL_X = (X_POLIA - 13.0, A01.X_PE - 5.0)   # ESTIMADO 165..195 (lado +x)
CURSO_TENSOR = 4.0                    # ESTIMADO ajuste de +-4 mm
LINGUA = (6.0, 2.5)                   # FAB largura, altura da lingua de guia
Y_LINGUA = (DESL_Y0 + Y_TRAS) / 2     # centro da lingua

PRAT_Z = (DESL_Z[0] - fab.E_PLACA, DESL_Z[0])   # prateleira de 6 mm sob o deslizador
PRAT_Y = (DESL_Y0 - 0.5, Y_TRAS)      # ESTIMADO
PRAT_X0 = DESL_X[0] - CURSO_TENSOR - 1.0        # ESTIMADO
# tensor: M4 por fora da lateral do gabinete, atravessa o pe e puxa a porca embutida no deslizador
Y_TENSOR = Y_LINGUA                   # eixo do M4 tensor
Z_TENSOR = -7.9                       # ESTIMADO abaixo da porca do M5 da tensora
X_TRAVA = X_POLIA - 8.0               # ESTIMADO M3 de trava, por baixo, longe do M5 da tensora
FUROS_PAREDE = [(y, -26.0 if (y, z) == (29.0, -17.0) else z) for y, z in A01.FUROS_PAREDE]   # ESTIMADO o de baixo-tras desce: a prateleira passa ali
NERV_Y = Y_LINGUA                     # nervura sob a prateleira
MDF = L.MDF_GAB                       # CENA 18

CIMA_IMPRESSAO = A01.CIMA_IMPRESSAO


def _prateleira():
    x0, x1 = PRAT_X0, A01.X_PE + 1
    p = caixa(x0, x1, PRAT_Y[0], PRAT_Y[1], PRAT_Z[0], PRAT_Z[1])
    p = p.edges("|X").fillet(fab.R_DETALHE)
    p = p.faces("<X").edges().fillet(fab.R_DETALHE)
    # canaleta da lingua (encaixe deslizante)
    w = LINGUA[0] / 2 + fab.ENCAIXE_DESLIZANTE
    p = p.cut(caixa(x0 - 1, x1 + 1, Y_LINGUA - w, Y_LINGUA + w, PRAT_Z[1] - LINGUA[1] - fab.ENCAIXE_DESLIZANTE, PRAT_Z[1] + 1))
    # rasgo da trava (curso do tensor)
    d = fab.FURO_PASSANTE["M3"]
    p = p.cut(cq.Workplane("XY", origin=(X_TRAVA, Y_LINGUA, PRAT_Z[0] - 1)).slot2D(2 * CURSO_TENSOR + d, d).extrude(fab.E_PLACA + 2))
    # nervura sob a prateleira ate o pe
    n = (cq.Workplane("XZ", origin=(0, NERV_Y + 2, 0))
         .polyline([(A01.X_PE + 1, PRAT_Z[0] + 0.5), (A01.X_PE + 1, A01.PE_Z[0] + 2), (176.0, PRAT_Z[0] + 0.5)]).close()
         .extrude(4))
    return p.union(n)


def local(eixo="B"):
    """Referencial local do eixo B, lado -x (espelhado do lado +x)."""
    peca = A01._pe(com_braco=(eixo == "B")).union(A01._berco(acesso=False)).union(_prateleira())
    if eixo == "B":
        peca = peca.union(A01._braco_fc())
    for y, z in FUROS_PAREDE + [(Y_TENSOR, Z_TENSOR)]:
        peca = peca.cut(cilindro(fab.FURO_PASSANTE["M4"], 20, (A01.X_PE - 5, y, z), (1, 0, 0)))
    try:
        peca = peca.faces(">X").edges().chamfer(fab.CHANFRO_BASE)
    except Exception:
        pass
    return cq.Workplane("XY").add(peca.val().mirror("YZ"))


def build(p=None, eixo="B"):
    return E.para_maquina(local(eixo), eixo)


def impressao(eixo="B"):
    sh = local(eixo).val()
    if eixo == "A":
        sh = sh.mirror("XY")
    # x local (+ para dentro, pe em -207) -> mesa: pe embaixo
    sh = sh.rotate((0, 0, 0), (0, 1, 0), -90)
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


def _m(p):
    return (-p[0], p[1], p[2])


def fixadores(var="B"):
    f = []
    for d in A01._fix_base():
        if d["nome"] == "motor":
            continue
        if d["nome"] == "parede":
            d = dict(d, ponto=(d["ponto"][0], *FUROS_PAREDE[A01.FUROS_PAREDE.index(tuple(d["ponto"][1:]))]))
        f.append(dict(d, ponto=_m(d["ponto"]), dir=(-d["dir"][0], d["dir"][1], d["dir"][2])))
    if var == "B":
        for d in A01._fixadores_fc():
            f.append(dict(d, ponto=_m(d["ponto"]), dir=(-d["dir"][0], d["dir"][1], d["dir"][2])))
    f.append(dict(nome="tensor", tipo="DIN912", bitola="M4", comp=40, ponto=(-(A01.X_PAREDE + MDF), Y_TENSOR, Z_TENSOR),
                  dir=(1, 0, 0), extra="por fora da lateral esquerda (furo Ø4,5 no MDF); puxa a porca M4 embutida no A04"))
    f.append(dict(nome="trava", tipo="DIN912", bitola="M3", comp=12, ponto=(-X_TRAVA, Y_LINGUA, PRAT_Z[0]), dir=(0, 0, 1),
                  chave=15, extra="porca M3 no deslizador A04"))
    return f


def pares_furos(var):
    pares = []
    for f in [f for f in fixadores(var) if f["nome"] == "perfil"]:
        p, d = f["ponto"], f["dir"]
        pares.append((f"perfil {'lateral' if d[1] else 'baixo'}", (E.ponto_para_maquina(p, var), E.dir_para_maquina(d, var)),
                      (E.ponto_para_maquina((p[0], 0, L.PERFIL_Z), var), E.dir_para_maquina(d, var))))
    from common import hardware as hw
    fc = [f for f in fixadores(var) if f["nome"] == "fim de curso"]
    for k, (f, (pa, da)) in enumerate(zip(sorted(fc, key=lambda f: f["ponto"][2]),
                                           sorted(hw.furos_fim_de_curso(-E.X_COSTAS_FC, E.Z_FC), key=lambda a: a[0][2]))):
        pares.append((f"FC {k + 1}", (E.ponto_para_maquina(f["ponto"], var), E.dir_para_maquina(f["dir"], var)),
                      (E.ponto_para_maquina(pa, var), E.dir_para_maquina(da, var))))
    return pares


FICHA = dict(
    orientacao="deitada na face do pe", suporte="nao", perimetros=4, infill="40% gyroid (estrutural)", camada=0.20,
    montagem=("1) porcas M3 na orelha e no braco do FC; 2) deslizador A04 com a tensora na prateleira (lingua na canaleta); "
              "4) perfil+trilho (M5 na aba e no piso); 5) eixo na parede, 4x M4x25; "
              "6) correia: M4x40 por fora da lateral ate a porca do deslizador, apertar ate tensionar, travar com o M3x12 por baixo; "
              "7) FC (so eixo B)."),
)
