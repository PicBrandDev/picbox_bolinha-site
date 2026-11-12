"""Pecas impressas da polia de cima do elevador (R2.2): adaptador reforcado N20 -> M5 e espacador da parede.

Polia GT2 20T de 16 mm (cubo 7,3 x Ø16 para a frente, dentes+abas 8,7) num parafuso M5 x 45 com 1 rolamento 625ZZ so
(o de tras, colado na sede, encostado no degrau). Da frente para tras (eixo Y da maquina):
  N20 | adaptador (e a "porca" do M5) | polia | espacador (atravessa o furo de 7 da parede) | rolamento | arruela | cabeca M5
O M5 aperta tudo num bloco: cabeca -> arruela -> pista de dentro do rolamento -> espacador -> polia -> adaptador.
A frente do eixo fica apoiada no proprio N20 (eixo dele dentro do adaptador).

  python polia_cima.py  ->  compacta/imprimir/polia_de_cima/*.stl + LEIA.txt  (rodar pelo PowerShell: CadQuery)
"""
from pathlib import Path

import cadquery as cq

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI.parents[1] / "imprimir" / "polia_de_cima"

# Y da maquina (frente -> tras)
Y_FACE_N20 = 154.5      # face do motor
Y_AD = (155.5, 180.35)  # adaptador
Y_FLANGE = 176.5        # dali para tras o adaptador esta dentro do furo de 16,8 do encaixe da frente: pode ser mais grosso
Y_POLIA = (180.35, 196.35)   # cubo 180,35..187,65 + dentes 187,65..196,35 (centro 192 = correia)
Y_DEGRAU = 203.15       # o rolamento de tras encosta aqui (sede de tras)
Y_ROL = (203.15, 208.15)
Y_ARR = (208.15, 209.15)
Y_CABECA = 209.15
M5 = 45.0               # ponta do M5 em Y 164,15
Y_M3 = 159.0            # parafuso sem cabeca M3 (radial, no chato do eixo do N20)

D_CORPO = 11.0          # na frente do encaixe o teto da torre fica 6 mm acima do eixo
D_FLANGE = 14.0         # dentro do furo de 16,8
FURO_M5 = 4.2           # rosca M5 direto no PETG
FURO_N20 = 3.2          # eixo de 3 do N20
CHATO_N20 = 1.1         # eixo do N20 em D: chato a 1,0 do centro (+0,1 de folga)
FURO_M3 = 2.7
FURO_PASSA = 5.3


def adaptador():
    """Em pe na mesa: face da polia (flange) para baixo. z 0 = Y 180,35 (encosta no cubo da polia)."""
    y0, y1 = Y_AD
    L = y1 - y0                                       # 24,85
    zf = y1 - Y_FLANGE                                # 3,85
    prof_m5 = y1 - (Y_CABECA - M5 - 0.25)             # 16,45: a ponta do M5 fica 0,25 antes do fundo
    prof_n20 = (Y_FACE_N20 + 1.0 + 7.15) - y0         # 7,15 de eixo dentro
    z_m3 = y1 - Y_M3                                  # 21,35
    c = cq.Workplane("XY").circle(D_FLANGE / 2).extrude(zf)
    c = c.union(cq.Workplane("XY").workplane(offset=zf).circle(D_CORPO / 2).extrude(L - zf))
    c = c.cut(cq.Workplane("XY").circle(FURO_M5 / 2).extrude(prof_m5))
    c = c.cut(cq.Workplane("XY").circle(FURO_M5 / 2 + 0.5).workplane(offset=0.5).circle(FURO_M5 / 2).loft())  # chanfro
    # furo em D do N20 (eixo em D: transmite o giro sem depender so do M3)
    d = cq.Workplane("XY").workplane(offset=L - prof_n20).circle(FURO_N20 / 2).extrude(prof_n20 + 0.1)
    corta_chato = cq.Workplane("XY").workplane(offset=L - prof_n20 - 0.1).center(CHATO_N20 + 2.0, 0).rect(4.0, 6.0) \
        .extrude(prof_n20 + 0.3)
    c = c.cut(d.cut(corta_chato))
    c = c.cut(cq.Workplane("XY").workplane(offset=L - 0.4).circle(FURO_N20 / 2 + 0.4).extrude(0.5))     # chanfro
    # M3 sem cabeca radial, entra pelo lado do chato (+X)
    c = c.cut(cq.Workplane("YZ").center(0, z_m3).circle(FURO_M3 / 2).extrude(D_CORPO))
    return c


def espacador_parede():
    """Atravessa o furo de 7 mm da parede de tras: encosta na polia e na pista de dentro do rolamento (nunca na parede)."""
    return cq.Workplane("XY").circle(3.2).circle(2.6).extrude(Y_DEGRAU - Y_POLIA[1])          # 6,8


def arruela():
    return cq.Workplane("XY").circle(3.75).circle(FURO_PASSA / 2).extrude(Y_ARR[1] - Y_ARR[0])


PECAS = [  # (arquivo, funcao, quantidade: 1 de reserva em cada)
    ("adaptador_n20_m5_reforcado__x2.stl", adaptador, 2),
    ("espacador_da_parede_6.8mm__x2.stl", espacador_parede, 2),
    ("arruela_7.5x1__x2.stl", arruela, 2),
]

LEIA = """PICBOX COMPACTA R2.2 - POLIA DE CIMA DO ELEVADOR (polia de 16 mm, 1 rolamento so)

IMPRIMIR (uns 25 min, ja vem 1 de reserva de cada):
  polia_de_cima__mesa.stl  = tudo junto (ou os separados: __x2 = 2 copias)
  PETG, camada 0,12, 100% de preenchimento, SEM suporte, em pe como esta no arquivo
  (adaptador com a parte grossa na mesa).

COMPRAR: 1 rolamento 625ZZ, 1 parafuso Allen M5 x 45 (DIN 912), 1 parafuso sem cabeca M3 x 3 (ou x 4). Sem porca.

A ORDEM (da frente para tras)
  N20 | adaptador | polia (cubo virado para o motor) | espacador 6,8 (atravessa o furo de 7 da parede) |
  rolamento (colado na sede, encostado no degrau) | arruela | cabeca do M5

IMAGENS: montagem_r2.2.png (montado + ordem) e adaptador_corte.png.

CORTE NA TORRE (obrigatorio)
  Teto: tirar a tira entre o encaixe do rolamento da frente e a janela (4,5 mm de largura, a largura da janela).
  O cubo de 16 da polia bate ali. O encaixe da frente nao precisa cortar (o cubo passa no furo de 16,8),
  mas pode, se quiser folga.

MONTAGEM
 1. Bancada: eixo do N20 no furo em D do adaptador ate o fundo; aperte o M3 sem cabeca no chato do eixo.
 2. Motor no berco com o adaptador para tras.
 3. Rolamento de tras na sede, encostado no degrau, gota de cola na pista de FORA.
 4. Polia (cubo para a frente) e espacador pela janela; M5 com a arruela por tras, atravessando rolamento,
    espacador e polia, e rosqueie no adaptador (o berco segura o motor). Aperte firme.
 5. Confira os dentes no meio da correia e aperte o parafusinho da polia no M5.
 6. Gire com a mao: liso, sem raspar no teto.
"""


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    for f in list(SAIDA.glob("*.stl")) + list(SAIDA.glob("*.png")):
        f.unlink()
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
    import polia_cima_imagens as I
    I.corte_adaptador(SAIDA / PECAS[0][0], SAIDA / "adaptador_corte.png")
    I.montagem(SAIDA / "montagem_r2.2.png")
    print("ok", SAIDA)


if __name__ == "__main__":
    main()
