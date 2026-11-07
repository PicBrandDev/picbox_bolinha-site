"""Imagens das novidades da R1.1 (presilha + fixador, fins de curso, arruela, barreira IR).

  python render_novo.py  ->  saida/imagens_novo/*.png
"""
import numpy as np

import layout as L
import render_m as R

NOVA = "#d6246e"      # comprada nova
ALT = "#f2a516"       # impressa alterada
BASE = "#c9d0d6"      # resto
COMPRADAS_NOVAS = ("Fixador de correia", "Arruela M10 de aco", "Fim de curso", "LED IR / fototransistor 5 mm")
ALTERADAS = ("Carro A", "Carro B", "Bloco esquerdo", "Anel")


def pinta(itens, fundo=0.35):
    out = []
    for me, cor, op, pc in itens:
        if pc in COMPRADAS_NOVAS:
            out.append((me, NOVA, 1.0, pc))
        elif pc in ALTERADAS:
            out.append((me, ALT, 1.0, pc))
        elif pc.startswith(("Correia", "Eletroima")):
            out.append((me, cor, 1.0, pc))
        else:
            out.append((me, BASE, fundo, pc))
    return out


def main():
    R.IMG = R.S / "imagens_novo"
    R.IMG.mkdir(parents=True, exist_ok=True)
    R.IMPRESSAS = R.malhas_impressas()
    m = L.M()
    el = m.el
    casa = m.c_casa
    zcA, zcB = m.zpA - 22, m.zpB - 22
    xe = casa + L.FIX[0] - 2
    yfix = 28.37 - 0.7 - 4.5

    # 1. geral
    cg = -20.0
    it = pinta(R.cena(m, el.zc_min + 160, el.ang_baixa, cg, cg + 40), 0.18)
    rot = [("Fixador de aluminio (carro A)", (cg - 6, yfix, zcA)),
           ("Fixador de aluminio (carro B)", (cg + 34, yfix, zcB)),
           ("Fim de curso eixo A", (xe - 7, 35, m.zpA - 20)), ("Fim de curso eixo B", (xe - 7, 35, m.zpB - 20)),
           ("Arruela M10 + copo no ima", (cg + m.dA, m.y_bola, m.face_ima)),
           ("Barreira IR no anel", (cg + 67.5, m.y_bola, m.zb - 14.5)),
           ("Fim de curso elevador (cima)", (205, 182, 404)), ("Fim de curso elevador (baixo)", (203, 186, 14))]
    R.foto("01_onde_fica.png", it, (0, 100, 210), (-0.75, -1.0, 0.62), 255, [], rot,
           titulo="R1.1: rosa = comprada nova, amarelo = impressa alterada")

    esc = ("Perfil 2020", "Prateleira", "Esteira", "Gancho", "Ponta fixa", "Bandeja", "EVA", "Tubo", "Fila")
    # 2. presilha + fixador (carro A, visto de baixo/frente, sem o perfil)
    it = pinta(R.cena(m, el.zc_min, el.ang_baixa, casa, 60.0), 0.25)
    rot = [("Fixador de aluminio 40x9x5", (casa - 6, yfix - 3, zcA - 1)),
           ("Correia presa entre fixador e parede", (casa - 20, 28.4, zcA + 3)),
           ("M3x12 + porca por baixo", (casa - 6, yfix, zcA - 8.5)),
           ("Carro A", (casa + 10, 40, zcA + 14))]
    R.foto("02_presilha.png", it, (casa - 6, 28, zcA + 2), (-0.3, -0.8, 1.0), 34, [], rot,
           titulo="Presilha do carro A: o fixador de aluminio prende a correia (o carro B e igual)",
           esconde=esc + ("Bloco esquerdo", "Fim de curso", "Trilho", "Patim", "Polia", "NEMA", "Suporte do NEMA"), vidro=("Carro A",))
    # 3. fim de curso (carro na casa, apertando a alavanca)
    rot = [("Fim de curso KW10", (xe - 7, 35, m.zpA - 14)), ("Braco do bloco esquerdo", (-200, 41, m.zpA - 12)),
           ("A presilha aperta a alavanca aqui (casa)", (xe + 1, 35, m.zpA - 22.5)),
           ("Carro A", (casa + 10, 40, zcA + 14))]
    R.foto("03_fim_de_curso.png", it, (xe, 36, m.zpA - 20), (0.25, -1.0, 0.55), 34, [], rot,
           titulo="Fim de curso do eixo A: na casa a presilha aperta a alavanca (eixo B igual, embaixo)",
           esconde=esc + ("Trilho", "Polia"))
    # 4. arruela + copo no ima
    it = pinta(R.cena(m, el.zc_max, el.ang_baixa, m.cA[1], 0.0), 0.25)
    bolso = tuple(m.bola_bolso)
    rot = [("Arruela M10 de aco (colada)", (m.x_pega, m.y_bola + 10, m.face_ima + 1)),
           ("Copo impresso em volta do ima", (m.x_pega - 12, m.y_bola, m.face_ima + 10)),
           ("Bola no bolso: o ima puxa e ela encaixa no furo", bolso)]
    R.foto("04_arruela.png", it, (m.x_pega, m.y_bola, m.face_ima), (-0.45, -1.0, 0.12), 28, [bolso], rot,
           titulo="Ima com arruela: a bola fica centrada no furo e nao escorrega",
           esconde=esc + ("Trilho MGN12 A", "Patim MGN12H A", "Bloco direito", "Correia A", "Rampa", "Fixador", "Fim de curso", "Sensor"), vidro=("Carro A",))
    # 5. barreira IR no anel
    it = pinta(R.cena(m, el.zc_min, el.ang_baixa, -60.0, 0.0), 0.25)
    rot = [("Emissor IR 5 mm", (-27.5, m.y_bola, m.zb - 14.5)), ("Receptor IR 5 mm", (27.5, m.y_bola, m.zb - 14.5)),
           ("Anel", (0, m.y_bola + 22, m.zb + 3))]
    R.foto("05_barreira_ir.png", it, (0, 70, m.zb - 8), (-0.5, -1.0, 0.7), 50, [], rot,
           titulo="Barreira infravermelha: par pronto emissor/receptor nos mesmos furos do anel",
           esconde=esc + ("Carro A", "Patim MGN12H A", "Eletroima", "Correia A", "Trilho MGN12 A", "Arruela"))
    print(sorted(x.name for x in R.IMG.glob("*.png")))


if __name__ == "__main__":
    main()
