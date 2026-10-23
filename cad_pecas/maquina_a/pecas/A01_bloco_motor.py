"""A01 — Bloco de ponta do motor (eixos A e B).

Intencao:
- Funcao: pe aparafusado na lateral direita do gabinete que segura o NEMA 17, apoia a ponta do perfil 2020
  (berco em U) e o modulo de fim de curso de home.
- Cargas: tracao da correia GT2 (~30 N, no plano da placa), peso do motor e do eixo; estatico.
- Interfaces: parede x=207 (4x M4 + porca-garra), perfil 2020 (M5 na aba da frente + M5 no piso, porcas martelo), NEMA 17 (31x31, ressalto Ø22),
  modulo FC (2x M3 com porca embutida). Eixo A = mesma peca espelhada em z (STL proprio).
Impressao: deitada na face do pe (a que encosta na parede); placa do motor, berco e braco do FC sobem na vertical.
"""
import cadquery as cq

from common import fab
from common.features import caixa, cilindro, teardrop, bolsao_porca
from maquina_a import layout as L
from maquina_a import eixo as E

ID = "A01"
NOME = "bloco_motor"
TITULO = "Bloco de ponta do motor"
QTD = {"B": 1, "A": 1}
MATERIAL = "PETG"
IMPRESSORA = "220"
REF = "eixo_bloco_motor"
ESTRUTURAL = True
JUSTIFICATIVA = ("pe mais largo em y (-28..58 contra -14..40,5) para os 4 parafusos M4 ficarem fora da varredura da boca/berco "
                 "e da correia, e para apoiar as nervuras atras da placa do motor; placa do motor 2 mm mais baixa")

# ------------------------------------------------------------------ cotas (referencial local do eixo, B)
X_PAREDE = L.PAREDE_X                 # PARAMS 207 face interna da lateral
X_PE = L.X_PE                         # CENA 200 face interna do pe = ponta do perfil
PE_Y = (-28.0, 58.0)                  # ESTIMADO contorno do pe: cobre parafusos, berco e nervuras
PE_Z = (-32.0, 30.0)                  # ESTIMADO
R_PE = 6.0                            # FAB raio dos cantos do pe (familia: visivel=3, pe estrutural maior)

X_POLIA = L.X_POLIA                   # CENA 178 centro do motor
Y_PLACA = L.Y_FACE_PLACA_MOTOR        # CENA 35,5 face da frente da placa do motor
E_PLACA = fab.E_PLACA                 # FAB 6
PLACA_X0 = 155.0                      # ESTIMADO cobre o motor (42,3) com 2 mm de borda
PLACA_Z = 27.0                        # ESTIMADO meia-altura da placa
R_PLACA = 6.0                         # FAB
D_RESSALTO = 22.0 + 2 * fab.ENCAIXE_DESLIZANTE   # CATALOGO NEMA Ø22 + folga deslizante
NEMA_FUROS = 31.0                     # CATALOGO

NERV_Z = (23.0, 27.0)                 # ESTIMADO nervuras acima/abaixo do corpo do motor (±21,15)
NERV_Y1 = 58.0                        # ESTIMADO
NERV_X0 = 163.0                       # ESTIMADO

BERCO_X0 = 176.0                      # ESTIMADO comprimento de apoio do perfil (24 mm)
PERFIL_MEIA = 10.0 + fab.ENCAIXE_JUSTO   # CATALOGO 2020 + encaixe justo
E_ABA = fab.E_GROSSA                  # FAB 4
Z_PERFIL = L.PERFIL_Z                 # CENA -14
X_M5 = 183.0                          # ESTIMADO M5 da aba da frente (longe do furo de acesso)
X_M5_PISO = 188.0                     # ESTIMADO M5 do piso do berco na fenda de baixo (a aba de tras nao tem chave: motor atras)
D_ACESSO = 6.5                        # FAB furo para a chave allen 2,5 do parafuso de baixo do motor (atravessa as abas)

FUROS_PAREDE = [(-22.0, 8.0), (-22.0, -20.0), (29.0, 17.0), (29.0, -17.0)]   # ESTIMADO (y, z) fora da varredura da boca/berco e da correia

X_COSTAS_FC = E.X_COSTAS_FC           # ESTIMADO 185,7 (ver eixo.py)
Z_FC = E.Z_FC                         # ESTIMADO 34
PEZINHO = 3.0                         # CENA espaco atras da placa do FC (pinos soldados)
E_BRACO = fab.E_PLACA                 # FAB 6: placa do braco (bolsao de porca + 3,2 de fundo)
BRACO_Y = 9.0                         # ESTIMADO meia-largura do braco (placa FC tem 16)
BRACO_Z = (Z_FC - 8.0, Z_FC + 22.0)   # ESTIMADO cobre os furos do FC (z-2 e z+16)
FC_FUROS_Z = [Z_FC + 16.0, Z_FC - 2.0]   # ESTIMADO (modulo FC: furos a -16 e +2 do centro, ver hardware)

CIMA_IMPRESSAO = (-1.0, 0.0, 0.0)     # na mesa, -x local aponta para cima


def _arredonda(obj, sel, r):
    """Filete opcional: se o OCC recusar, mantem a aresta (a checagem visual acusa)."""
    try:
        return sel(obj).fillet(r)
    except Exception:
        return obj


def _pe(com_braco=True):
    sk = cq.Sketch().push([((PE_Y[0] + PE_Y[1]) / 2, (PE_Z[0] + PE_Z[1]) / 2)]).rect(PE_Y[1] - PE_Y[0], PE_Z[1] - PE_Z[0])
    if com_braco:
        sk = sk.push([(0, (PE_Z[1] - R_PE + BRACO_Z[1] + 2) / 2)]).rect(2 * BRACO_Y + 4, BRACO_Z[1] + 2 - PE_Z[1] + R_PE)
    sk = sk.clean().reset().vertices().fillet(R_PE)
    return cq.Workplane("YZ", origin=(X_PE, 0, 0)).placeSketch(sk).extrude(X_PAREDE - X_PE)


def _placa_motor():
    p = caixa(PLACA_X0, X_PE + 1, Y_PLACA, Y_PLACA + E_PLACA, -PLACA_Z, PLACA_Z)
    p = p.edges("|Y").edges("<X").fillet(R_PLACA)
    p = _arredonda(p, lambda q: q.faces("<Y").edges(), fab.R_EXTERNO)
    p = _arredonda(p, lambda q: q.faces(">Y").edges(), fab.R_DETALHE * 2)
    p = p.cut(teardrop(D_RESSALTO, E_PLACA + 2, (X_POLIA, Y_PLACA - 1, 0), (0, 1, 0), CIMA_IMPRESSAO))
    h = NEMA_FUROS / 2
    d_reb, p_reb = fab.REBAIXO_DIN912["M3"]
    for dx in (-h, h):
        for dz in (-h, h):
            c = (X_POLIA + dx, Y_PLACA - 1, dz)
            p = p.cut(cilindro(fab.FURO_PASSANTE["M3"], E_PLACA + 2, c, (0, 1, 0)))
            p = p.cut(teardrop(d_reb, p_reb + 1, c, (0, 1, 0), CIMA_IMPRESSAO))
    return p


def _nervuras():
    n = None
    for z0, z1 in ((NERV_Z[0], NERV_Z[1]), (-NERV_Z[1], -NERV_Z[0])):
        r = (cq.Workplane("XY", origin=(0, 0, z0))
             .polyline([(X_PE + 1, Y_PLACA + E_PLACA - 1), (X_PE + 1, NERV_Y1), (NERV_X0, Y_PLACA + E_PLACA - 1)])
             .close().extrude(z1 - z0))
        # arestas livres: a face inclinada e a ponta
        r = _arredonda(r, lambda q: q.edges(cq.selectors.BoxSelector((NERV_X0 - 1, Y_PLACA, z0 - 1), (X_PE - 1, NERV_Y1 + 1, z1 + 1))),
                       fab.R_EXTERNO)
        n = r if n is None else n.union(r)
    return n


def _berco(acesso=True):
    a = PERFIL_MEIA
    b = caixa(BERCO_X0, X_PE + 1, -a - E_ABA, a + E_ABA, Z_PERFIL - 10 - E_ABA, Z_PERFIL + 10)
    b = _arredonda(b, lambda q: q.edges("|X"), fab.R_EXTERNO)
    b = b.cut(caixa(BERCO_X0 - 1, X_PE + 2, -a, a, Z_PERFIL - 10, Z_PERFIL + 11))
    b = _arredonda(b, lambda q: q.faces("<X").edges(), fab.R_DETALHE * 2)
    b = b.edges("|X").edges(cq.selectors.BoxSelector((BERCO_X0 - 2, -a - 0.1, Z_PERFIL - 10.1),
                                                     (X_PE + 3, a + 0.1, Z_PERFIL - 9.9))).fillet(fab.R_INTERNO)
    b = b.cut(teardrop(fab.FURO_PASSANTE["M5"], E_ABA + 2, (X_M5, -(a + E_ABA + 1), Z_PERFIL), (0, 1, 0), CIMA_IMPRESSAO))
    b = b.cut(cilindro(fab.FURO_PASSANTE["M5"], E_ABA + 2, (X_M5_PISO, 0, Z_PERFIL - 10 - E_ABA - 1), (0, 0, 1)))
    # acesso da chave ao parafuso de baixo do motor que fica atras do berco (motor e montado antes do perfil)
    h = NEMA_FUROS / 2
    if acesso:
        b = b.cut(teardrop(D_ACESSO, 2 * (a + E_ABA) + 2, (X_POLIA + h, -(a + E_ABA + 1), -h), (0, 1, 0), CIMA_IMPRESSAO))
    return b


def _braco_fc():
    x0, x1 = X_COSTAS_FC + PEZINHO, X_COSTAS_FC + PEZINHO + E_BRACO
    z0, z1 = BRACO_Z
    w = BRACO_Y
    br = caixa(x0, X_PE + 1, -w, w, z0, z1)
    br = _arredonda(br, lambda q: q.edges("|X"), fab.R_VISIVEL)
    br = _arredonda(br, lambda q: q.faces("<X").edges(), fab.R_EXTERNO)
    br = br.cut(caixa(x1, X_PE + 0.01, -w + E_ABA + 0.5, w - E_ABA - 0.5, z0 - 1, z1 - E_ABA))   # vao (entrada das porcas por baixo)
    for z in FC_FUROS_Z:
        br = br.union(cilindro(7.0, PEZINHO + 0.01, (X_COSTAS_FC, 0, z), (1, 0, 0)))
        br = br.cut(cilindro(fab.FURO_PASSANTE["M3"], 30, (X_COSTAS_FC - 1, 0, z), (1, 0, 0)))
        br = br.cut(bolsao_porca("M3", (x1, 0, z), (-1, 0, 0), angulo=30.0, extra_saida=0.5))
    return br


def local(com_fc=True):
    """Peca no referencial local do eixo B."""
    peca = _pe().union(_placa_motor()).union(_nervuras()).union(_berco())
    if com_fc:
        peca = peca.union(_braco_fc())
    for y, z in FUROS_PAREDE:
        peca = peca.cut(cilindro(fab.FURO_PASSANTE["M4"], 20, (X_PE - 5, y, z), (1, 0, 0)))
    # chanfro de base na face que vai na mesa (x = 207)
    try:
        peca = peca.faces(">X").edges().chamfer(fab.CHANFRO_BASE)
    except Exception:
        pass
    return peca


def build(p=None, eixo="B"):
    return E.para_maquina(local(), eixo)


def impressao(eixo="B"):
    """Peca na mesa (z >= 0), deitada na face do pe."""
    sh = local().val()
    if eixo == "A":
        sh = sh.mirror("XY")
    # x local -> -z (mesa), y -> y, z -> x
    sh = sh.rotate((0, 0, 0), (0, 1, 0), 90)
    bb = sh.BoundingBox()
    sh = sh.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return cq.Workplane("XY").add(sh)


# ------------------------------------------------------------------ fixadores (referencial local; ponto = apoio da cabeca)
def fixadores(var=None):
    return _fix_base() + _fixadores_fc()


def _fix_base():
    f = []
    for y, z in FUROS_PAREDE:
        f.append(dict(nome="parede", tipo="DIN912", bitola="M4", comp=25, ponto=(X_PE, y, z), dir=(1, 0, 0),
                      antes_de=("A13",), extra="porca-garra M4 cravada por fora da lateral"))
    f.append(dict(nome="perfil", tipo="ISO7380", bitola="M5", comp=10, ponto=(X_M5, -(PERFIL_MEIA + E_ABA), Z_PERFIL),
                  dir=(0, 1, 0), antes_de=("A13",), extra="porca martelo M5 na fenda lateral do perfil"))
    f.append(dict(nome="perfil", tipo="ISO7380", bitola="M5", comp=10, ponto=(X_M5_PISO, 0, Z_PERFIL - 10 - E_ABA),
                  dir=(0, 0, 1), chave=35, extra="porca martelo M5 na fenda de baixo do perfil"))
    h = NEMA_FUROS / 2
    for dx in (-h, h):
        for dz in (-h, h):
            f.append(dict(nome="motor", tipo="DIN912", bitola="M3", comp=6,
                          ponto=(X_POLIA + dx, Y_PLACA + fab.REBAIXO_DIN912["M3"][1], dz), dir=(0, 1, 0),
                          antes_de=("perfil", "trilho", "correia", "polia", "fc"), extra=""))
    return f


def _fixadores_fc():
    hw_placa = 1.6   # ESTIMADO espessura da placa do modulo FC
    return [dict(nome="fim de curso", tipo="DIN912", bitola="M3", comp=12,
                 ponto=(X_COSTAS_FC - hw_placa, 0, z), dir=(1, 0, 0), extra="porca M3 no bolsao do braco")
            for z in FC_FUROS_Z]


FICHA = dict(
    orientacao="deitada na face do pe (a que encosta na parede)", suporte="nao",
    perimetros=4, infill="40% gyroid (estrutural)", camada=0.20,
    montagem=("1) porcas M3 nos bolsoes do braco (por baixo); 2) motor na placa, 4x M3x6 pela frente; "
              "3) polia no eixo; 4) perfil+trilho entre os blocos (escorrega em x ate o pe), M5x10 + martelo na aba da frente e no piso; "
              "5) eixo montado na parede: 4x M4x25 nas porcas-garra; 6) modulo FC, 2x M3x12."),
)


def pares_furos(var):
    """Furos da peca x furos do par (referencial da maquina)."""
    from common import hardware as hw
    pares = []
    fx = fixadores(var)
    mot = [f for f in fx if f["nome"] == "motor"]
    alvo = hw.furos_nema17(X_POLIA, Y_PLACA + E_PLACA)
    for k, (f, (pa, da)) in enumerate(zip(sorted(mot, key=lambda f: (f["ponto"][0], f["ponto"][2])),
                                           sorted(alvo, key=lambda a: (a[0][0], a[0][2])))):
        pares.append((f"NEMA {k + 1}", (E.ponto_para_maquina(f["ponto"], var), E.dir_para_maquina(f["dir"], var)),
                      (E.ponto_para_maquina(pa, var), E.dir_para_maquina(da, var))))
    fc = [f for f in fx if f["nome"] == "fim de curso"]
    for k, (f, (pa, da)) in enumerate(zip(sorted(fc, key=lambda f: f["ponto"][2]),
                                           sorted(hw.furos_fim_de_curso(X_COSTAS_FC, Z_FC), key=lambda a: a[0][2]))):
        pares.append((f"FC {k + 1}", (E.ponto_para_maquina(f["ponto"], var), E.dir_para_maquina(f["dir"], var)),
                      (E.ponto_para_maquina(pa, var), E.dir_para_maquina(da, var))))
    for f in [f for f in fx if f["nome"] == "perfil"]:
        # parafuso M5 tem que cair no centro da fenda do perfil
        p, d = f["ponto"], f["dir"]
        alvo = (p[0], 0, L.PERFIL_Z)
        pares.append((f"perfil {'lateral' if d[1] else 'baixo'}", (E.ponto_para_maquina(p, var), E.dir_para_maquina(d, var)),
                      (E.ponto_para_maquina(alvo, var), E.dir_para_maquina(d, var))))
    return pares
