"""Tracado do magazine e da calha de carga (coordenadas da MAQUINA, Z up). Tudo e definido pelo CENTRO DA BOLA.

Fluxo: entrada (carga manual; depois o elevador) em x=+130 -> tubo acrilico Ø50x44 ao longo de -x em y=70
(atras do eixo A) -> saida A15: reta + curva de 90 graus para -y -> escapamento A16: travessia em V ao longo
de -y em x=-184,5 (passa por baixo do pe do bloco do tensor A), servo SG90 com 2 dedos -> entrada do berco A26:
curva em V de 90 graus (R18,5, para +x) e linguas que entram no berco (carro A em x=-140).
Inclinacao de 3 graus em todo o caminho. Capacidade ~10 bolas (tubo 6 + saida e curva 1,9 + fila ate o dedo 0,5
+ canal da entrada 1,3 + funil 1).
"""
import math

from maquina_a import layout as L
from maquina_a import soltura as S

R_B = L.BOLA_R                         # MEDIDO 19
INCL = math.radians(3.0)               # ESTIMADO inclinacao do caminho (3 graus: rola com folga, sem velocidade demais)
TUBO_D, TUBO_DI = 50.0, 44.0           # CATALOGO tubo acrilico Ø50 x 44 (usuario: default aceito)
Y_MAG = 70.0                           # ESTIMADO eixo do tubo: atras do bloco do tensor A (y<=40,5) e longe do motor A01
X_TUBO = (-130.0, 100.0)               # ESTIMADO tubo cortado com 230 mm; a entrada A18 (x ate 150) fica longe do motor/nervuras do A01 (x>=157)
QUEDA_TUBO = TUBO_DI / 2 - R_B         # 3: centro da bola abaixo do eixo do tubo

# V de 120 graus (igual ao berco): centro da bola 21,94 acima do vertice, linhas de contato a 16,45 abaixo e +-9,5
ANG_V = S.ANG_CONTATO
H_VERTICE = R_B / math.sin(math.radians(90 - ANG_V))      # 21,94
GUARDA_IN = R_B + 1.5                  # FAB folga radial 1,5 nas guardas laterais
E_CALHA = 3.0                          # FAB parede/fundo da calha (E_FINA arredondada)

X_TRAV = -184.5                        # ESTIMADO travessia: guarda de 2 mm na parede; bola a 1,5 mm da bochecha do berco na carga
R_CURVA = 30.0                         # ESTIMADO linha de centro da curva de 90 graus
X_CURVA0 = X_TRAV + R_CURVA            # -155,5 inicio da curva (vindo em -x)
Y_CURVA1 = Y_MAG - R_CURVA             # 40 fim da curva (seguindo em -y)
X_CARGA = -140.0                       # CENA posicao de carga do carro A (extremo do curso de jogo, lado do tensor)
X_CARGA_MIN = -141.0                   # ESTIMADO limite do carro A do lado do tensor (1 mm alem da carga; sem FC desse lado)
X_LINGUA = X_CARGA_MIN + S.X_BOCH_E[0] - 1.0   # -166: fim do corpo da calha (1 mm da bochecha do berco no limite)
X_PONTA = X_CARGA - 1.0 + S.X_PORT[0] - 1.0   # -162,5: ponta da lingua (1 mm das portinholas com o carro em -141)
Y_CANTO = S.Y_C                        # -57 plano da bola no berco
QUEDA_CANTO = 2.0                      # referencia das alturas a montante (mantida: o magazine nao muda de altura)

# alturas do centro da bola (de tras para frente), a partir do berco
Z_BERCO = S.Z_C                                             # 1470
Z_FIM = Z_BERCO                                             # trecho final chega no nivel do berco (vertice continuo)
Z_CANTO_X = Z_FIM + (X_LINGUA - X_TRAV) * math.tan(INCL)    # trecho final no canto
Z_CANTO_Y = Z_CANTO_X + QUEDA_CANTO                         # referencia de z_trav (y=-57)
Z_CURVA1 = Z_CANTO_Y + (Y_CURVA1 - Y_CANTO) * math.tan(INCL)
Z_CURVA0 = Z_CURVA1 + (math.pi / 2 * R_CURVA) * math.tan(INCL)
Z_TUBO0 = Z_CURVA0 + (X_TUBO[0] - X_CURVA0) * math.tan(INCL)    # ponta esquerda do tubo (centro da bola)
Z_TUBO1 = Z_TUBO0 + (X_TUBO[1] - X_TUBO[0]) * math.tan(INCL)

# escapamento na travessia: dedo de baixo (segura a fila) e dedo de cima a um passo de bola
Y_DEDO1 = -23.0                        # ESTIMADO (dedos entre y=-36,5 e o bloco da junta em y=30)
ANG_ESCAPE = 15.0                      # ESTIMADO +-15 graus no servo
DEDO_H = 18.0                          # ESTIMADO altura do dedo acima do pivo
DEDO_SEC = (3.0, 4.0)                  # ESTIMADO secao do dedo (x, y)
_INCL_DEDO = DEDO_H * math.sin(math.radians(ANG_ESCAPE))   # o dedo inclina junto com o balancim
Y_BOLA1 = Y_DEDO1 + _INCL_DEDO + DEDO_SEC[1] / 2 + R_B      # centro da 1a bola parada no dedo de baixo
PASSO_DEDOS = 2 * _INCL_DEDO + DEDO_SEC[1] / 2 + 2 * R_B   # o dedo de cima sobe entre a 1a e a 2a bola
Y_DEDO2 = Y_DEDO1 + PASSO_DEDOS
Y_PIVO = (Y_DEDO1 + Y_DEDO2) / 2
BRACO_DEDO = PASSO_DEDOS / 2


def z_trav(y):
    """Centro da bola na travessia (ao longo de -y em x=X_TRAV)."""
    return Z_CANTO_Y + (y - Y_CANTO) * math.tan(INCL)


def z_fim(x):
    """Centro da bola no trecho final (ao longo de +x em y=Y_CANTO)."""
    return Z_FIM + (X_LINGUA - x) * math.tan(INCL)


def z_tubo(x):
    return Z_TUBO0 + (x - X_TUBO[0]) * math.tan(INCL)


def pontos_bola(passo=4.0):
    """Centro da bola ao longo de todo o caminho, da entrada ao berco."""
    pts = []
    x = X_TUBO[1]
    while x > X_CURVA0:
        pts.append((x, Y_MAG, z_tubo(x) if x >= X_TUBO[0] else Z_CURVA0 + (x - X_CURVA0) * math.tan(INCL)))
        x -= passo
    n = int(math.pi / 2 * R_CURVA / passo) + 1
    for k in range(n + 1):
        a = math.pi / 2 * k / n
        cx, cy = X_TRAV + R_CURVA, Y_CURVA1
        pts.append((cx - R_CURVA * math.sin(a), cy + R_CURVA * math.cos(a), Z_CURVA0 - a * R_CURVA * math.tan(INCL)))
    y = Y_CURVA1
    while y > Y_CURVA_B0:
        pts.append((X_TRAV, y, z_trav(y)))
        y -= passo
    n = int(math.pi / 2 * R_CURVA_B / passo) + 1
    for k in range(n + 1):
        a = math.pi / 2 * k / n
        cx, cy = C_CURVA_B
        pts.append((cx - R_CURVA_B * math.cos(a), cy - R_CURVA_B * math.sin(a), Z_CURVA_B0 - (Z_CURVA_B0 - Z_FIM) * k / n))
    x = X_LINGUA + passo
    while x <= S.X_PORT[0] + X_CARGA:
        pts.append((x, Y_CANTO, Z_FIM))
        x += passo
    return pts


# ------------------------------------------------------------------ geometria do canal em V (secao no plano normal ao caminho)
V_ABERTO = 14.0                        # ESTIMADO meia-largura do V sem guarda (lado do berco): o V centra a bola sozinho


def perfil_v(neg="guarda", pos="guarda", guarda_alta=-2.0, u_neg=None, u_pos=None):
    """Pontos (u lateral, v para cima) da secao do canal, com o centro da bola em (0, 0).
    Cada lado: 'guarda' (parede a 1,5 mm da bola) ou 'v' (flanco aberto ate V_ABERTO). u_neg/u_pos cortam a largura."""
    t = math.tan(math.radians(ANG_V))
    gi, ge = GUARDA_IN, GUARDA_IN + E_CALHA
    vb = -H_VERTICE - E_CALHA
    def lado(tipo, s, ulim):
        if tipo == "guarda":
            e = min(ge, ulim) if ulim else ge
            return [(s * e, vb), (s * e, guarda_alta), (s * gi, guarda_alta), (s * gi, -H_VERTICE + gi * t)]
        e = V_ABERTO
        zt = -H_VERTICE + (e - 1.6) * t                 # patamar de 1,6 mm no topo do flanco (sem quina fina)
        return [(s * e, vb), (s * e, zt), (s * (e - 1.6), zt)]
    p = lado(pos, 1, u_pos)
    n = lado(neg, -1, u_neg)
    return p + [(0, -H_VERTICE)] + list(reversed(n))


def canal_reto(p0, p1, neg="guarda", pos="guarda", guarda_alta=-2.0, u_neg=None, u_pos=None, perfil=None):
    """Canal em V entre dois centros de bola p0 -> p1 (o vertice segue a reta, 'cima' = +z)."""
    import cadquery as cq
    a, b = cq.Vector(*p0), cq.Vector(*p1)
    d = b - a
    t = d.normalized()
    lat = cq.Vector(0, 0, 1).cross(t).normalized()
    up = lat.cross(t).normalized()
    pl = cq.Plane(origin=a.toTuple(), xDir=lat.toTuple(), normal=t.toTuple())
    # yDir do plano = normal x xDir = t x (z x t) = componente de +z normal ao caminho
    pts = perfil if perfil is not None else perfil_v(neg, pos, guarda_alta, u_neg, u_pos)
    return cq.Workplane(pl).polyline(pts).close().extrude(d.Length)


def canal_curva(u_neg=None, pos="v", perfil=None):
    """Curva de 90 graus: do fim do tubo (vindo em -x) para a travessia (seguindo em -y), descendo 3 graus."""
    import cadquery as cq
    cx, cy = X_TRAV + R_CURVA, Y_CURVA1
    h = Z_CURVA0 - Z_CURVA1
    hel = cq.Wire.makeHelix(pitch=4 * h, height=h, radius=R_CURVA, center=cq.Vector(cx, cy, Z_CURVA1), lefthand=True)
    hel = hel.rotate(cq.Vector(cx, cy, 0), cq.Vector(cx, cy, 1), 180)     # comeca em (cx - R, cy): fim da curva, embaixo
    p0 = hel.startPoint()
    t0 = hel.tangentAt(0).normalized()
    lat = cq.Vector(0, 0, 1).cross(t0).normalized()
    pl = cq.Plane(origin=p0.toTuple(), xDir=lat.toTuple(), normal=t0.toTuple())
    # a helice e varrida do fim da curva para o comeco (contra o fluxo): os lados u+/u- trocam
    pts = perfil if perfil is not None else perfil_v(neg=pos, pos="guarda", u_pos=u_neg)
    perfil = cq.Workplane(pl).polyline(pts).close()
    return perfil.sweep(cq.Workplane().add(hel), isFrenet=True)


X_PAREDE = -L.PAREDE_X                 # -207 face interna da lateral esquerda
U_PAREDE = X_TRAV - X_PAREDE - 0.0     # 21,5: lado da parede vai ate a lateral (a parede e a guarda de fora)

# curva em V da entrada do berco (A26): da travessia (-y) para o berco (+x), sem degrau nem batente
R_CURVA_B = X_LINGUA - X_TRAV          # 18,5: o maior raio que cabe entre a travessia e o berco
C_CURVA_B = (X_LINGUA, Y_CANTO + R_CURVA_B)   # (-166, -38,5)
Y_CURVA_B0 = C_CURVA_B[1]              # fim da travessia
Z_CURVA_B0 = Z_CANTO_Y + (Y_CURVA_B0 - Y_CANTO) * math.tan(INCL)   # 1473,9 (travessia na mesma altura de antes)
INCL_CURVA_B = math.degrees(math.atan((Z_CURVA_B0 - Z_FIM) / (math.pi / 2 * R_CURVA_B)))   # ~7,7 graus
Y_JUNTA_B = Y_CURVA_B0 + 4.5           # ESTIMADO junta A16/A26 na travessia (pinos)


def canal_curva_berco(neg="guarda", pos="v", perfil=None, extra=20.0):
    """Curva de 90 graus da travessia (vindo em -y) para o berco (seguindo em +x), descendo de Z_CURVA_B0 a Z_FIM.
    A varredura comeca 'extra' graus alem do fim (x>-166, fora da peca): no comeco dela o OCC perde material."""
    import cadquery as cq
    cx, cy = C_CURVA_B
    h = Z_CURVA_B0 - Z_FIM
    z0 = Z_FIM - h * extra / 90.0
    hel = cq.Wire.makeHelix(pitch=4 * h, height=h * (90.0 + extra) / 90.0, radius=R_CURVA_B, center=cq.Vector(cx, cy, z0),
                            lefthand=True)
    hel = hel.rotate(cq.Vector(cx, cy, 0), cq.Vector(cx, cy, 1), 270 + extra)
    p0 = hel.startPoint()
    t0 = hel.tangentAt(0).normalized()
    lat = cq.Vector(0, 0, 1).cross(t0).normalized()
    pl = cq.Plane(origin=p0.toTuple(), xDir=lat.toTuple(), normal=t0.toTuple())
    # varrida contra o fluxo: os lados u+/u- trocam
    pts = perfil if perfil is not None else perfil_v(neg=pos, pos=neg)
    return cq.Workplane(pl).polyline(pts).close().sweep(cq.Workplane().add(hel), isFrenet=True)

# escapamento: servo SG90 deitado contra a lateral, eixo para +x; dedos no plano do vertice da travessia
Z_PIVO = z_trav(Y_PIVO) - H_VERTICE - 14.0   # ponta sobe ~9,8 acima do vertice e desce ~3 abaixo
X_DEDO = X_TRAV                        # plano dos dedos = vertice da travessia
X_EIXO_SERVO = X_PAREDE + 22.7 + 4.0   # ponta do eixo do servo (corpo encostado na lateral)

# entrada (carga manual; depois o elevador): canal Ø44 continua o tubo ate x=150, funil por cima em x=120
X_ENTRADA = (85.0, 153.0)              # ESTIMADO corpo da A18 (encaixe 85..100, canal 100..150, tampa 150..153)
X_FUNIL = 112.0                        # ESTIMADO (funil a 8 mm do motor do A01 A, x>=156,9)
Z_FUNIL_TOPO = 1568.0                  # ESTIMADO acima do motor A01 A (1551) para o suporte passar por cima


def eixo_tubo(x):
    return (x, Y_MAG, z_tubo(x) + QUEDA_TUBO)
