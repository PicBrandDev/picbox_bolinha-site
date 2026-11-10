"""Imagens dos sensores: onde fica cada um, para que lado olha e o que aciona.

  python render_sensores.py  ->  saida/imagens/s1..s5_*.png
"""
import numpy as np
import pyvista as pv

import layout as L
import elevador2 as E
import render_m as R

SENS = "#d6246e"
SETA = "#c8601e"


def seta(itens, p0, d, comp=18.0, cor=SETA):
    d = np.array(d, float)
    d /= np.linalg.norm(d)
    a = pv.Arrow(start=p0, direction=d, scale=comp, tip_length=0.3, tip_radius=0.12, shaft_radius=0.045)
    itens.append((a, cor, 1.0, "seta"))


def destaca(itens):
    out = []
    for me, cor, op, pc in itens:
        if pc in ("Fim de curso", "Sensor de fenda", "Sensor do bolso", "LED IR / fototransistor 5 mm", "Bandeira"):
            cor = SENS
        out.append((me, cor, op, pc))
    return out


def main():
    R.IMG.mkdir(parents=True, exist_ok=True)
    R.IMPRESSAS = R.malhas_impressas()
    m = L.M()
    el = m.el
    zfb, zft = E.P.Z_FEIXE_BAIXO, E.P.Z_FEIXE_CIMA
    xb, yb = E.X_BANDEIRA, E.Y_BANDEIRA

    # 1. visao geral: os 9 sensores
    it = destaca(R.cena(m, el.zc_min + 150, el.ang_baixa, m.cA[0] + 40, 0.0))
    rot = [("1 KW10 casa A", (-181, 35, m.zpA - 20)), ("2 KW10 seguranca A", (190, 35, m.zpA - 25)),
           ("3 KW10 casa B", (-181, 35, m.zpB - 20)), ("4 KW10 seguranca B", (190, 35, m.zpB - 25)),
           ("5 Fenda de baixo (elevador)", (xb, yb, 14)), ("6 Fenda de cima (elevador)", (xb, yb, 416)),
           ("7 TCRT5000 do bolso", L.SENSOR_BOLSO + (347,)), ("8 Barreira IR do anel", (0, m.y_bola, m.zb - 14.5))]
    R.foto("s1_sensores_geral.png", it, (0, 115, 215), (-0.75, -1.0, 0.62), 300, [], rot,
           titulo="Os 8 sensores (rosa): 4 fins de curso nos eixos, 2 opticos no elevador, 1 no bolso, 1 barreira no anel")

    # 2. elevador embaixo: fenda de baixo, bandeira descendo
    it = destaca(R.cena(m, el.zc_min, el.ang_baixa, -60.0, 0.0))
    seta(it, (xb, yb - 9, zfb), (0, 1, 0), 18)                 # feixe ao longo de Y
    seta(it, (xb + 6, yb, zfb + 22), (0, 0, -1), 14)           # bandeira desce
    rot = [("Sensor de fenda de baixo: orelhas presas no pe com 2 M3, fenda para CIMA", (xb, yb + 14, 7)),
           ("Feixe infravermelho (ao longo de Y, de frente para tras)", (xb, yb - 9, zfb)),
           ("Bandeira M2x25 da cabine: desce e corta o feixe", (xb + 6, yb, zfb + 22)),
           ("Fios: furo no pe e canal por baixo ate a canaleta", (xb, 214, 2))]
    R.foto("s2_sensor_elevador_baixo.png", it, (200, 195, 22), (0.75, -0.55, 0.55), 38, [], rot, vidro=("Cabine",),
           titulo="Elevador embaixo (torres escondidas): a bandeira entra na fenda e a cabine para",
           esconde=("Torre inferior", "Torre superior", "Bandeja", "EVA", "Fila", "Perfil 2020 B", "Trilho MGN12 B", "Carro B",
                    "Patim MGN12H B", "Esteira B", "Bloco direito", "LED", "Correia B"))

    # 3. elevador em cima
    it = destaca(R.cena(m, el.zc_max, el.ang_baixa, -60.0, 0.0))
    seta(it, (xb, yb - 9, zft), (0, 1, 0), 18)
    seta(it, (xb + 6, yb, zft - 22), (0, 0, 1), 14)
    rot = [("Sensor de fenda de cima: orelhas presas no teto com 2 M3, fenda para BAIXO", (xb, yb + 14, 423)),
           ("Feixe (ao longo de Y)", (xb, yb - 9, zft)),
           ("Bandeira M2x25: sobe e corta o feixe na entrega", (xb + 6, yb, zft - 22)),
           ("Motor N20", (191, 160, el.z_polia_cima))]
    R.foto("s3_sensor_elevador_cima.png", it, (200, 190, 405), (0.75, -0.55, 0.35), 40, [], rot, vidro=("Cabine",),
           titulo="Elevador no topo (torres escondidas): a bandeira sobe na fenda e a cabine para com a bola na altura da rampa",
           esconde=("Torre inferior", "Torre superior", "Perfil 2020 A", "Trilho MGN12 A", "Patim MGN12H A", "Prateleira",
                    "Esteira A", "Bloco direito", "Correia A", "Carro A", "Eletroima", "Rampa"))

    # 4. eixo A: casa (esquerda) e seguranca (direita)
    for nome, ca, foco, txt in (("s4_fim_de_curso_casa.png", m.cA[0], (-178, 44, m.zpA - 4),
                                 "Casa do eixo A: o batedor da placa do carro aperta a alavanca, atras do trilho, longe da polia e da correia"),
                                ("s5_fim_de_curso_seguranca.png", m.cA[1], (186, 33, m.zpA - 40),
                                 "Seguranca do eixo A: abaixo da tensora; o batedor que desce do carro fica 0,8 mm da alavanca na pega")):
        it = destaca(R.cena(m, el.zc_max, el.ang_baixa, ca, 0.0))
        if "casa" in nome:
            seta(it, (-150, 30, m.zpA - 22), (-1, 0, 0), 18)
            rot = [("KW10 da casa (atras do trilho)", (-181, 46, m.zpA + 4)), ("Carro A indo para a esquerda", (-150, 30, m.zpA - 22))]
        else:
            seta(it, (160, 30, m.zpA - 26), (1, 0, 0), 18)
            rot = [("KW10 de seguranca (abaixo da tensora)", (190, 35, m.zpA - 36)), ("Carro A na pega", (160, 30, m.zpA - 26))]
        R.foto(nome, it, foco, (0.35, -1.0, 0.35) if "casa" in nome else (0.35, -1.0, -0.45), 45, [], rot, titulo=txt,
               esconde=("Perfil 2020 A", "Prateleira", "Esteira A", "Eletroima", "Rampa", "Torre"))

    # 6. bolso e anel
    it = destaca(R.cena(m, el.zc_max, el.ang_baixa, m.cA[1], 0.0))
    seta(it, (L.SENSOR_BOLSO[0], L.SENSOR_BOLSO[1], 338), (0, 0, 1), 14)
    rot = [("TCRT5000: embaixo do piso do bolso, olhando para CIMA pela janela", (L.SENSOR_BOLSO[0], L.SENSOR_BOLSO[1], 345)),
           ("Bola no bolso", tuple(m.bola_bolso))]
    R.foto("s6_sensor_bolso.png", it, (196, 72, 352), (0.45, -1.0, -0.35), 32, [tuple(m.bola_bolso)], rot, vidro=("Rampa",),
           titulo="Sensor do bolso: ve a bola chegar e ve a bola ir embora presa no ima",
           esconde=("Perfil 2020 A", "Trilho MGN12 A", "Patim MGN12H A", "Prateleira", "Esteira A", "Bloco direito", "Correia A",
                    "Carro A", "Eletroima", "Torre superior"))
    it = destaca(R.cena(m, el.zc_min, el.ang_baixa, m.cA[0], 0.0))
    seta(it, (-24, m.y_bola, m.zb - 14.5), (1, 0, 0), 48)
    rot = [("LED IR (emissor)", (-27.5, m.y_bola, m.zb - 14.5)), ("Receptor", (27.5, m.y_bola, m.zb - 14.5)),
           ("Feixe atravessa o furo do anel (ao longo de X)", (0, m.y_bola, m.zb - 14.5))]
    R.foto("s7_barreira_anel.png", it, (0, m.y_bola, m.zb - 8), (-0.4, -1.0, 0.75), 45, [], rot, vidro=("Carro B",),
           titulo="Barreira do anel: a bola que passa pelo furo corta o feixe 14,5 mm abaixo da borda",
           esconde=("Bandeja", "EVA", "Perfil 2020 A", "Trilho MGN12 A", "Carro A", "Prateleira", "Esteira A"))
    print("ok")


if __name__ == "__main__":
    main()
