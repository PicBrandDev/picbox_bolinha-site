"""Imagens das mudancas da R1.2 (elevador): degrau cabine -> rampa, bolso mais largo, suporte do motor reforcado.

  python render_r12.py  ->  saida/imagens_r12/*.png
"""
import numpy as np

import layout as L
import render_m as R

ALT = "#f2a516"
BASE = "#c9d0d6"
ALTERADAS = ("Cabine", "Rampa", "Suporte do motor")


def pinta(itens, fundo=0.3, alt=ALTERADAS):
    out = []
    for me, cor, op, pc in itens:
        if pc in alt:
            out.append((me, ALT, 1.0, pc))
        elif pc.startswith(("Correia", "EVA", "Motor N20", "Polia do motor", "Fim de curso")):
            out.append((me, cor, 1.0, pc))
        else:
            out.append((me, BASE, fundo, pc))
    return out


def main():
    R.IMG = R.S / "imagens_r12"
    R.IMG.mkdir(parents=True, exist_ok=True)
    R.IMPRESSAS = R.malhas_impressas()
    m = L.M()
    el = m.el
    xb = el.x_bola
    z_saida = el.zc_max + el.z_piso_berco(xb, 130.5)
    z_rampa = m.z_rampa(xb, 127.7)
    # 1. corte do elevador no topo, no plano da bola
    it = R.cena(m, el.zc_max, el.ang_baixa, -60.0, 0.0)
    cortado = [(me.clip(normal=(1, 0, 0), origin=(xb, 0, 0)), cor, op, pc) for me, cor, op, pc in pinta(it, 0.35)]
    cab = (xb, el.y_bola, el.zc_max + el.z_piso_berco(xb, el.y_bola) + L.R)
    rot = [(f"Saida da cabine Z {z_saida:.1f}", (xb, 133, z_saida - 3)), (f"Rampa Z {z_rampa:.1f}: degrau {z_saida - z_rampa:.1f} mm (era 3,5)", (xb, 104, m.z_rampa(xb, 104) + 0.5)),
           ("C direito 2,5 mm mais alto: aperta o fim de curso antes", (205, 182, el.zc_max + el.caixa_z[1] + el.batente_fdc)),
           ("Bola no bolso", tuple(m.bola_bolso))]
    R.foto("01_degrau_rampa.png", cortado, (xb, 125, 370), (-1, 0, 0.0001), 48, [cab, tuple(m.bola_bolso)], rot,
           titulo="Cabine no topo, cortada no plano da bola (visto da esquerda)",
           esconde=("Perfil 2020 A", "Trilho MGN12 A", "Patim MGN12H A", "Carro A", "Eletroima", "Arruela", "Prateleira",
                    "Esteira A", "Gancho", "Correia A", "Fixador"))
    # 2. bolso visto de cima
    it = pinta(R.cena(m, el.zc_max, el.ang_baixa, -60.0, 0.0), 0.25, ("Rampa",))
    rot = [("Piso do bolso: +3 mm para fora (X 186)", (L.X_BOLSO + 1, 75, m.z_rampa(L.X_BOLSO, 75))),
           ("Batente + EVA 20 mm", (L.X_BOLSO + 4, 56, m.z_rampa(190, 56) + 10))]
    R.foto("02_bolso.png", it, (196, 80, 350), (-0.25, -0.35, 1), 32, [tuple(m.bola_bolso)], rot,
           titulo="Bolso da rampa visto de cima: base mais larga do lado de fora",
           esconde=("Perfil 2020 A", "Trilho MGN12 A", "Patim MGN12H A", "Carro A", "Eletroima", "Arruela", "Prateleira",
                    "Esteira A", "Gancho", "Correia A", "Fixador", "Suporte do motor", "Motor N20", "Polia do motor",
                    "Tubo superior", "Bloco direito", "Gabinete"))
    # 3. suporte do motor visto de baixo
    it = pinta(R.cena(m, el.zc_min, el.ang_baixa, -60.0, 0.0), 0.2, ("Suporte do motor",))
    rot = [("Orelha: 2 parafusos na parede", (209, 116.5, 404)), ("Braco + 2 almas ate a placa", (203, 108, 405)),
           ("Faixa da frente 10 mm", (180, 133, 410)), ("Nervuras de 12 mm", (174, 165, 405)),
           ("Abraco do motor com paredes de 3 mm", (191, 135, 399))]
    R.foto("03_suporte_motor.png", it, (191, 150, 408), (-0.55, -0.8, -0.55), 52, [], rot,
           titulo="Suporte do motor N20 visto de baixo: placa reforcada e orelha travada",
           esconde=("Perfil 2020 A", "Trilho MGN12 A", "Patim MGN12H A", "Carro A", "Eletroima", "Arruela", "Prateleira",
                    "Esteira A", "Gancho", "Correia A", "Fixador", "Tubo superior", "Rampa", "EVA", "Guia impressa superior",
                    "Cabine", "Bloco direito", "Gabinete"))
    print(sorted(x.name for x in R.IMG.glob("*.png")))


if __name__ == "__main__":
    main()
