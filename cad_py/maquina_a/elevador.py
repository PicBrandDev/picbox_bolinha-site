"""Elevador de fuso da Maquina A (coordenadas da maquina, Z up). Pecas: A20 base, A21 fuso, A22 topo, A23 calha, A24 suporte do motor.

Conceito (usuario, 2026-10-22): tubo acrilico em pe no canto frente-direita, fuso girando por dentro, motor embaixo.
- Entrada: a bola desce a bandeja ate o tubo e entra por um furo largo no pe (virado para o campo, 35..232 graus),
  cai num piso conico (sobe 4 mm para o centro) que a mantem encostada na parede.
- Subida: o fuso gira no sentido HORARIO visto de cima (helice a direita). O filete arrasta a bola ate o trilho-guia
  (barra Ø8 aparafusada na parede do tubo, a 250 graus); segura pelo trilho, a bola sobe 70 mm por volta. O topo do
  filete cai 10 graus para fora: a bola fica sempre apertada contra a parede.
- Transferencia e saida (revisao 2026-10-23): a bola sobe no canto (280 graus, trilho de aluminio a 250) e nunca
  fica solta. No topo o tubo vira a cabeca impressa A27: uma guia helicoidal continua o trilho e leva a bola, subindo,
  de 280 para 150 graus (lado do campo); dali um trilho vertical impresso (120 graus) a segura ate a janela de saida
  (126..175 graus). Quando a beira do filete passa da borda do piso da A25, a bola rola para fora pelo caimento do
  filete (10 graus), sem pular nada. A25 leva a calha A23 (3 graus) ate o funil do magazine (A18).
Angulos: em graus, a partir de +x, anti-horario visto de cima, em volta do eixo do tubo C.

Por que Ø100: a bola de 38 precisa caber entre o nucleo do fuso e a parede (num Ø44 sobram 3 mm).
Por que quase nesta posicao: inclinado pela parede direita, o tubo bate na boca no fim do curso do carro B.
"""
import math

from maquina_a import layout as L

R_B = L.BOLA_R                         # MEDIDO 19
TUBO_D, TUBO_DI = 100.0, 94.0          # CATALOGO tubo acrilico Ø100 x 3 (compra)
R_TI = TUBO_DI / 2
C = (L.PAREDE_X - TUBO_D / 2 - 2.0, -L.PAREDE_Y + TUBO_D / 2 + 2.0)   # (155, -155): 2 mm das paredes
Z_DIV_TOPO, Z_DIV_BAIXO = L.Z_DIVISORIA, L.Z_DIVISORIA - L.MDF_GAB    # 1100, 1082
FOLGA_TUBO = 0.3                       # FAB encaixe deslizante do tubo nas pecas
D_FURO_DIVISORIA = TUBO_D + 1.0        # FAB furo do tubo na divisoria e na bandeja

# ------------------------------------------------------------------ fuso (A21)
D_EIXO = 8.0                           # CATALOGO barra roscada M8 (passa por dentro do fuso)
D_FURO_EIXO = 8.4                      # FAB
R_NUCLEO = 7.0                         # ESTIMADO
R_FILETE = 37.0                        # ESTIMADO: 1,5 de folga para o trilho e para a soleira
PASSO = 70.0                           # ESTIMADO (CAD): com 62 a bola tocava o filete de cima; com 70 a folga e 2 mm (o nucleo limita)
BETA = math.radians(10.0)              # ESTIMADO caimento do topo do filete para fora
E_FILETE = 2.0                         # FAB espessura do filete na ponta
K_BAIXO = 1.3                          # FAB parte de baixo do filete: 52 graus (com a inclinacao da helice fica <= 45 da vertical)
LABIO = (2.0, 2.0)                     # FAB 2 mm junto da ponta a 63 graus (a varredura torce a superficie ali)
R_BOLA = R_TI - R_B                    # 28: centro da bola encostada na parede
R_APOIO = R_BOLA - R_B * math.sin(BETA)    # 24,7: onde a bola toca o filete
DZ_APOIO = 1.6                         # medido no CAD: a inclinacao da helice levanta a bola 1,6 mm
Z_REF = 0.0                            # fase da helice: altura de referencia (no nucleo) no angulo 0 do fuso
PINO = (3.0, 3.2, 8.0)                 # CATALOGO pino Ø3 (aco ou filamento 2,85) / FAB furo / profundidade por lado

# ------------------------------------------------------------------ trilho-guia
D_TRILHO = 8.0                         # CATALOGO barra Ø8 de aluminio (3 furos roscados M3)
R_TRILHO = R_TI - D_TRILHO / 2 - 0.5   # 42,5
ANG_TRILHO = 250.0                     # ESTIMADO trilho de aluminio (embaixo): fora do furo de entrada
ANG_BOLA = ANG_TRILHO + 30.0           # 280: bola parada no trilho (distancia de centros 23)
ANG_TRILHO_TOPO = 120.0                # ESTIMADO trilho vertical impresso no topo (A27): bola a 150, de frente para o campo
ANG_BOLA_TOPO = ANG_TRILHO_TOPO + 30.0
Z_TRILHO_SCREWS = (1200.0, 1400.0)     # ESTIMADO parafusos M3 pela parede do tubo (montagem na bancada)

# ------------------------------------------------------------------ alturas
Z_BASE0 = 1061.0                       # ESTIMADO fundo da A20
Z_TUBO0 = Z_BASE0 + 6.0                # 1067: ponta de baixo do tubo (apoiada no ressalto da A20)
Z_PISO = Z_DIV_TOPO                    # piso dentro do tubo, na parede
CONE_PISO = 4.0                        # ESTIMADO o piso sobe 4 mm ate o centro: a bola vai para a parede
Z_FUSO0 = Z_PISO + CONE_PISO + 0.5     # 1104,5: base plana do fuso
ARCO_FURO = (35.0, 232.0)              # ESTIMADO furo de entrada (cunhas da bola na bandeja: 63 e 207, +-23 graus)
Z_FURO = (Z_PISO + 12.0, 1170.0)       # soleira 1112 (abaixo do EVA na borda do tubo, 1118..1122) e topo
H_FIM = 1602.0                         # ESTIMADO topo do filete: a bola no fim dele fica 1,8 mm abaixo da tampa
Z_CABECA0 = 1467.0                     # ESTIMADO fim do acrilico / comeco da cabeca impressa A27
Z_TRANSF = (Z_CABECA0 + 3.0, 1580.0)   # ESTIMADO guia helicoidal (centro da bola): 280 -> 150 graus em 110 mm
Z_TRILHO = (1080.0, Z_TRANSF[0])       # trilho de aluminio: do fundo da A20 ate o encaixe na flange da A27 (3 mm)
Z_NUCLEO1 = H_FIM + 1.0                # topo do nucleo (porca + arruela por cima)
JUNTAS = (Z_FUSO0, 1272.0, 1440.0, Z_NUCLEO1)   # ESTIMADO 3 segmentos (<= 170 mm, cabem na 220)
ARCO_ENTALHE = (ANG_TRILHO_TOPO + 6.0, ANG_BOLA_TOPO + 25.0)   # 126..175: janela de saida na A27 (bola +-24 graus)
Z_SAIDA_FUNDO = 1582.0                 # ESTIMADO fundo plano da A25 = fundo da janela da A27 (a guia passa abaixo)
Z_ENTALHE0 = Z_SAIDA_FUNDO
R_BORDA_SAIDA = R_TI + 0.3             # 47,3: borda de dentro do piso da A25 na janela (faz de parede ate a bola sair)
Z_TUBO1 = 1640.0                       # topo da A27 (a tampa A22 apoia aqui)
E_TAMPA = 10.0                         # FAB placa da A22 sobre o tubo
D_ROLAMENTO = (22.0, 7.0, 8.0)         # CATALOGO 608ZZ (De, largura, di)
Z_REBAIXO = Z_FUSO0 - 10.0             # 1094,5: fundo do rebaixo do piso (arruela Ø14 + porca M8 embaixo do fuso)
Z_608_BAIXO = Z_REBAIXO - D_ROLAMENTO[1]   # o pacote do fuso apoia no anel interno do 608 de baixo

# motor embaixo (eixo vertical, fora do campo: dentro do pedestal)
ACOPL = (19.0, 25.0)                   # CATALOGO acoplamento flexivel 5x8 (D, L)
Z_ACOPL1 = Z_BASE0 - 6.0               # 1055: topo do acoplamento (1 mm abaixo do fundo da A20 menos folga)
Z_MOTOR_FACE = Z_ACOPL1 - ACOPL[1] + 12.0 - 24.0   # 1016: eixo de 24 entra 12 no acoplamento

# ------------------------------------------------------------------ saida e calha (A22, A23)
INCL_SAIDA = math.radians(6.0)         # ESTIMADO piso da saida (para +y)
X_RAIA = 100.0                         # ESTIMADO linha da bola na calha (ao longo de +y)
Y_RAIA0 = -90.0                        # inicio da A23 (fim da A25)
GUARDA = (20.5, 23.5)                  # FAB guarda lateral da saida e da calha (bola + 1,5; parede 3)
POSTES = ((131.0, -105.0), (100.0, -166.0))   # ESTIMADO postes da A25 presos por baixo da tampa A22 (M3)
ORELHAS = ((62.0, 76.5), (123.5, 140.0))     # ESTIMADO orelhas da A23 por baixo da A25 (x), y Y_RAIA0-14..Y_RAIA0
FUROS_ORELHA = ((69.0, -97.0), (133.0, -97.0))
INCL_CALHA = math.radians(3.0)         # ESTIMADO igual ao magazine
Y_RAIA1 = 66.0                         # ESTIMADO furo de queda sobre o funil da A18 (a 12,6 do eixo do funil)


def p(r, ang, z=0.0):
    """Ponto (maquina) em coordenadas polares em volta do eixo do tubo."""
    a = math.radians(ang)
    return (C[0] + r * math.cos(a), C[1] + r * math.sin(a), z)


def z_piso(r):
    return Z_PISO + CONE_PISO * (1.0 - r / R_TI)


def zc_apoio(ref):
    """Centro da bola encostada na parede, apoiada no filete cuja referencia (no nucleo) esta em 'ref'."""
    return ref + DZ_APOIO + R_B * math.cos(BETA) - (R_APOIO - R_NUCLEO) * math.tan(BETA)


ZC_MAX = zc_apoio(H_FIM)               # bola mais alta possivel (no fim do filete)
ZC_SAI = ZC_MAX - 8.0                  # centro da bola quando a beira do filete passa da borda do piso (8 mm de sobra)
BEIRA_FILETE = ZC_MAX - (H_FIM - (R_FILETE - R_NUCLEO) * math.tan(BETA))   # centro da bola - beira do filete (r=37)
Z_BORDA_SAIDA = ZC_SAI - BEIRA_FILETE  # topo da borda do piso da A25 no angulo da bola (150)
Z_TRILHO_TOPO1 = ZC_SAI - 11.0         # fim do trilho de cima: na saida a bola ja nao encosta nele (senao ele a empurra para dentro)


def z_saida(y):
    """Topo do piso da saida (A25), descendo 6 graus para +y; na borda (r=47,3, 150 graus) vale Z_BORDA_SAIDA."""
    y0 = p(R_BORDA_SAIDA, ANG_BOLA_TOPO)[1]
    return Z_BORDA_SAIDA - (y - y0) * math.tan(INCL_SAIDA)


def ang_guia(z):
    """Angulo do centro do perfil da guia/trilho na altura z (250 embaixo, gira 130 graus horario, 120 em cima)."""
    z0, z1 = Z_TRANSF
    t = min(1.0, max(0.0, (z - z0) / (z1 - z0)))
    return ANG_TRILHO + (ANG_TRILHO_TOPO - ANG_TRILHO) * t


def _tabela_bola():
    import json
    from pathlib import Path
    f = Path(__file__).resolve().parent / "elevador_bola.json"
    return json.loads(f.read_text(encoding="utf8")) if f.exists() else None


_TAB = _tabela_bola()


def ang_bola(zc):
    """Angulo da bola encostada na guia, pela altura do centro. Na guia inclinada a bola encosta abaixo do centro e fica
    mais para o lado anti-horario que 30 graus: tabela calculada no CAD (tools/tabela_bola.py, esfera tangente a guia)."""
    if _TAB:
        zs, angs = _TAB["z"], _TAB["ang"]
        if zc <= zs[0]:
            return angs[0]
        if zc >= zs[-1]:
            return angs[-1]
        for k in range(len(zs) - 1):
            if zs[k] <= zc <= zs[k + 1]:
                t = (zc - zs[k]) / (zs[k + 1] - zs[k])
                return angs[k] + (angs[k + 1] - angs[k]) * t
    return ang_guia(zc) + 30.0


Z_RAIA0 = z_saida(Y_RAIA0) + R_B - 1.0  # centro da bola no inicio da A23 (desce 1 mm do piso plano para o V)


def z_raia(y):
    return Z_RAIA0 - (y - Y_RAIA0) * math.tan(INCL_CALHA)


# ------------------------------------------------------------------ geometria do fuso
def h_helice(ang_fuso):
    """Altura de referencia (no nucleo) do topo do filete no angulo do fuso (helice a direita), na volta de Z_REF."""
    return Z_REF + PASSO * ang_fuso / 360.0


def _perfil_filete():
    t = math.tan(BETA)
    top = lambda r: -(r - R_NUCLEO) * t
    r0 = D_FURO_EIXO / 2 + 0.6           # o filete entra no nucleo ate perto do furo (sem faces internas)
    rl, zl = R_FILETE - LABIO[0], top(R_FILETE) - E_FILETE - LABIO[0] * LABIO[1]
    return [(r0, top(r0)), (R_FILETE, top(R_FILETE)), (R_FILETE, top(R_FILETE) - E_FILETE), (rl, zl),
            (r0, zl - K_BAIXO * (rl - r0))]


def filete(z0, z1):
    """Filete (helice a direita) com a referencia indo de z0 a z1 (eixo local em (0,0), z da maquina)."""
    import cadquery as cq
    ang0 = 360.0 * (z0 - Z_REF) / PASSO
    hel = cq.Wire.makeHelix(PASSO, z1 - z0, 21.0, center=cq.Vector(0, 0, z0), lefthand=False)
    hel = hel.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), ang0)
    a = math.radians(ang0)
    pl = cq.Plane(origin=(0, 0, z0), xDir=(math.cos(a), math.sin(a), 0), normal=(math.sin(a), -math.cos(a), 0))
    return cq.Workplane(pl).polyline(_perfil_filete()).close().sweep(cq.Workplane().add(hel), isFrenet=True)


def segmento_fuso(k):
    """Segmento k (0..2) do fuso no eixo local (x=y=0), z da maquina, fase de referencia."""
    import cadquery as cq
    from common.features import caixa, cilindro
    z0, z1 = JUNTAS[k], JUNTAS[k + 1]
    zh1 = min(z1 + 45.0, H_FIM)
    f = filete(z0 - 5.0, zh1)
    nuc = cilindro(2 * R_NUCLEO, z1 - z0, (0, 0, z0), (0, 0, 1))
    s = f.union(nuc).intersect(caixa(-60, 60, -60, 60, z0, z1))
    s = s.cut(cilindro(D_FURO_EIXO, z1 - z0 + 2, (0, 0, z0 - 1), (0, 0, 1)))
    for zj in (z0, z1):
        if zj in (JUNTAS[0], JUNTAS[-1]):
            continue
        for x, y in pinos(zj):
            s = s.cut(cilindro(PINO[1], 2 * PINO[2], (x, y, zj - PINO[2]), (0, 0, 1)))
    return s


def pinos(zj):
    """2 pinos de alinhamento na junta zj: no angulo em que o filete tem a referencia 15 mm acima da junta."""
    ang = 360.0 * (zj + 15.0 - Z_REF) / PASSO
    a = math.radians(ang)
    return [(r * math.cos(a), r * math.sin(a)) for r in (12.0, 20.0)]


def fuso_maquina(k, giro=0.0):
    """Segmento k na maquina, girado 'giro' graus (anti-horario visto de cima) em volta do eixo."""
    import cadquery as cq
    sh = segmento_fuso(k).val().rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), giro).translate((C[0], C[1], 0))
    return cq.Workplane("XY").add(sh)


def giro_para_bola(z_centro, ang=None):
    """Giro do fuso que poe o filete embaixo da bola (centro em z_centro, encostada na parede no angulo 'ang';
    sem 'ang', o angulo da guia naquela altura)."""
    ang = ang_bola(z_centro) if ang is None else ang
    h = z_centro - DZ_APOIO - R_B * math.cos(BETA) + (R_APOIO - R_NUCLEO) * math.tan(BETA)   # referencia no ponto de apoio
    ang_fuso = 360.0 * (h - Z_REF) / PASSO
    return (ang - ang_fuso) % 360.0


# ------------------------------------------------------------------ compradas (referencia)
def tubo_acrilico():
    import cadquery as cq
    from common.features import caixa, cilindro
    t = cilindro(TUBO_D, Z_CABECA0 - Z_TUBO0, (C[0], C[1], Z_TUBO0), (0, 0, 1))
    t = t.cut(cilindro(TUBO_DI, Z_CABECA0 - Z_TUBO0 + 2, (C[0], C[1], Z_TUBO0 - 1), (0, 0, 1)))
    t = t.cut(setor(R_TI - 1, TUBO_D / 2 + 1, *ARCO_FURO, *Z_FURO))
    for z in Z_TRILHO_SCREWS:
        t = t.cut(cilindro(3.4, 10, p(R_TI - 2, ANG_TRILHO, z), (math.cos(math.radians(ANG_TRILHO)), math.sin(math.radians(ANG_TRILHO)), 0)))
    return t


def setor(r0, r1, a0, a1, z0, z1):
    """Setor anelar (maquina) entre os angulos a0..a1 (graus, anti-horario)."""
    import cadquery as cq
    n = max(4, int(abs(a1 - a0) / 5))
    pts = [p(r1, a0 + (a1 - a0) * k / n)[:2] for k in range(n + 1)]
    pts += [p(r0, a1 - (a1 - a0) * k / n)[:2] for k in range(n + 1)] if r0 > 0 else [C]
    return cq.Workplane("XY", origin=(0, 0, z0)).polyline(pts).close().extrude(z1 - z0)


def hardware():
    """Compradas do elevador (maquina)."""
    import cadquery as cq
    from common.features import caixa, cilindro
    x, y = C
    out = {"elev_acrilico": tubo_acrilico(),
           "elev_trilho": cilindro(D_TRILHO, Z_TRILHO[1] - Z_TRILHO[0], p(R_TRILHO, ANG_TRILHO, Z_TRILHO[0]), (0, 0, 1)),
           "elev_barra_m8": cilindro(D_EIXO, (Z_TUBO1 + E_TAMPA + 10.0) - (Z_ACOPL1 - 12.0), (x, y, Z_ACOPL1 - 12.0), (0, 0, 1)),
           "elev_acoplamento": cilindro(ACOPL[0], ACOPL[1], (x, y, Z_ACOPL1 - ACOPL[1]), (0, 0, 1)),
           "elev_608_baixo": cilindro(D_ROLAMENTO[0], D_ROLAMENTO[1], (x, y, Z_608_BAIXO), (0, 0, 1)),
           "elev_608_cima": cilindro(D_ROLAMENTO[0], D_ROLAMENTO[1], (x, y, Z_TUBO1), (0, 0, 1))}
    a = 42.3 / 2
    motor = caixa(x - a, x + a, y - a, y + a, Z_MOTOR_FACE - 40.0, Z_MOTOR_FACE).edges("|Z").chamfer(3.6)
    motor = motor.union(cilindro(22.0, 2.0, (x, y, Z_MOTOR_FACE), (0, 0, 1)))
    motor = motor.union(cilindro(5.0, 24.0, (x, y, Z_MOTOR_FACE), (0, 0, 1)))
    out["elev_nema17"] = motor
    return out


def furos_motor():
    """Furos M3 do NEMA (quadrado 31, nas diagonais)."""
    h = 31.0 / 2
    return [(C[0] + sx * h, C[1] + sy * h) for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
