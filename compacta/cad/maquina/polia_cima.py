"""Pecas impressas pequenas da polia de cima do elevador (R2.1): acoplamento N20 -> M5, arruelas e espacadores.

A polia de cima gira num parafuso M5 x 45 (o eixo) apoiado em 2 rolamentos 625ZZ. Tudo fica apertado num bloco so
entre a cabeca do M5 (atras) e o acoplamento (na frente), que e a "porca": o M5 rosqueia nele por tras.
Medidas (eixo Y da maquina) em elevador2.py (PC_*).

  python polia_cima.py  ->  compacta/imprimir/polia_de_cima/*.stl + LEIA.txt  (rodar pelo PowerShell: CadQuery)
"""
from pathlib import Path

import cadquery as cq

import elevador2 as E

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI.parents[1] / "imprimir" / "polia_de_cima"

FURO_M5 = 4.2        # rosca M5 direto no PETG (o parafuso abre a rosca)
FURO_N20 = 3.2       # eixo de 3 do N20 entra sem forcar
FURO_M3 = 2.7        # parafuso sem cabeca M3 abre a rosca
FURO_PASSA = 5.3     # arruelas e espacadores: passam no M5


def acoplamento():
    """Em pe na mesa, lado do M5 para baixo (z 0 = ponta de tras, Y 175,5)."""
    y0, y1 = E.PC_ACOPL
    comp = y1 - y0                                   # 20
    prof_m5 = y1 - E.PC_FURO_M5                      # 11,85
    prof_n20 = E.PC_FURO_N20 - y0                    # 7,15
    z_m3 = y1 - E.PC_M3_Y                            # 16,5
    c = cq.Workplane("XY").circle(E.PC_ACOPL_R).extrude(comp)
    c = c.cut(cq.Workplane("XY").circle(FURO_M5 / 2).extrude(prof_m5))
    c = c.cut(cq.Workplane("XY").circle(FURO_M5 / 2 + 0.4).extrude(0.4))          # chanfro de entrada da rosca
    c = c.cut(cq.Workplane("XY").workplane(offset=comp - prof_n20).circle(FURO_N20 / 2).extrude(prof_n20))
    c = c.cut(cq.Workplane("YZ").workplane(offset=0).center(0, z_m3).circle(FURO_M3 / 2).extrude(E.PC_ACOPL_R + 1))
    return c


def anel(d_fora, comp):
    return cq.Workplane("XY").circle(d_fora / 2).circle(FURO_PASSA / 2).extrude(comp)


def arruela():
    return anel(7.5, E.PC_ARR_F[1] - E.PC_ARR_F[0])


def espacador_frente():
    return anel(7.5, E.PC_ESP_F[1] - E.PC_ESP_F[0])


def espacador_tras():
    # passa no furo de 7 mm do degrau da torre: parede fina, furo um pouco menor (o fatiador fecha um pouco o furo)
    return cq.Workplane("XY").circle(3.2).circle(2.6).extrude(E.PC_ESP_T[1] - E.PC_ESP_T[0])


PECAS = [  # (arquivo, funcao, quantidade a imprimir: 1 de reserva em cada)
    ("acoplamento_n20_m5__x2.stl", acoplamento, 2),
    ("arruela_7.5x1__x4.stl", arruela, 4),
    ("espacador_da_frente_2mm__x2.stl", espacador_frente, 2),
    ("espacador_de_tras_7.65mm__x2.stl", espacador_tras, 2),
]

LEIA = """PICBOX COMPACTA R2.1 - POLIA DE CIMA DO ELEVADOR (parafuso M5 como eixo)

IMPRIMIR (qualquer impressora, uns 20 min, ja vem 1 de reserva de cada):
  polia_de_cima__mesa.stl  = tudo junto numa mesa so
  (ou os arquivos separados, a quantidade esta no nome: __x2 = 2 copias)
  PETG, camada 0,12 a 0,16, 100% de preenchimento, SEM suporte, como esta no arquivo (em pe).

COMPRAR
  2  rolamentos 625ZZ (5 x 16 x 5 mm)
  1  parafuso Allen M5 x 45 (DIN 912, cabeca cilindrica) - de preferencia rosca parcial
     (tem que ser 45: com 50 bate no eixo do motor, com 40 pega pouca rosca)
  1  parafuso Allen sem cabeca M3 x 3 (ou M3 x 4)
  NAO precisa de porca: o acoplamento impresso e a porca do M5.
  Ja tem: polia GT2 20T furo 5, motor N20. Separar: cola instantanea (super bonder), fita crepe.

A ORDEM NO PARAFUSO (de tras para a frente)
  cabeca M5 | arruela | rolamento de tras | espacador de tras (7,65) | polia (cubo para a frente) |
  espacador da frente (2) | rolamento da frente | arruela | acoplamento | eixo do N20

MONTAGEM (torre de cima sozinha, na bancada)
 0. Se ficou uma pelicula fina tampando os furos dos rolamentos, corte com estilete
    (as 2 faces do furo da frente e a face de tras do furo de tras).
 1. Na bancada: eixo do N20 no acoplamento (furo pequeno) ate o fundo; aperte o M3 sem cabeca
    (se o eixo for redondo, lixe um chatinho nele onde o M3 encosta).
 2. Motor com o acoplamento pela frente, no encaixe do motor: o acoplamento passa pelo encaixe e o motor deita no berco.
 3. Rolamento de tras: por tras da torre, ate encostar no degrau. Uma gota de cola na pista de FORA
    (nao deixe a cola chegar na tampinha do meio). E ele que segura tudo no lugar.
 4. Rolamento da frente: se ficar frouxo na sede, 1 volta de fita crepe na pista de fora.
 5. Torre de cabeca para baixo, apoiada em 2 livros, com a janela do teto livre por baixo.
    Arruela na cabeca do M5 e o M5 por tras, atravessando o rolamento de tras.
    Pelo vao aberto da torre (agora em cima) solte uma peca de cada vez e encaixe na ponta do M5 com o dedo
    pela janela do teto, empurrando o M5 um pouco a cada peca:
      espacador de tras -> polia (cubo virado para o motor) -> espacador da frente -> rolamento da frente -> arruela
    O rolamento da frente entra na sede da frente.
 6. Gire o M5 por tras com a chave Allen: ele rosqueia no acoplamento (o motor no berco nao deixa o acoplamento
    girar). Aperte firme: tudo vira um bloco so. Uma gota de trava-rosca (ou cola) na ponta do M5 antes.
 7. Centralize os dentes da polia na janela do teto e aperte o parafusinho da polia pela janela.
 8. Gire com a mao: tem que girar liso.
"""


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    mesa, x = None, 0.0
    for arq, f, n in PECAS:
        w = f()
        bb = w.val().BoundingBox()
        uma = None
        for i in range(n):
            c = w.translate((i * (bb.xlen + 4.0), 0, 0))
            uma = c if uma is None else uma.union(c)
        cq.exporters.export(uma, str(SAIDA / arq), tolerance=0.01, angularTolerance=0.1)
        lin = uma.translate((0, x, 0))
        mesa = lin if mesa is None else mesa.union(lin)
        x += bb.ylen + 5.0
    cq.exporters.export(mesa, str(SAIDA / "polia_de_cima__mesa.stl"), tolerance=0.01, angularTolerance=0.1)
    (SAIDA / "LEIA.txt").write_text(LEIA, encoding="utf8")
    print("ok", SAIDA)


if __name__ == "__main__":
    main()
