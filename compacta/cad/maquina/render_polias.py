"""Imagens das polias: onde fica cada uma e como esta apoiada.

  python render_polias.py  ->  saida/imagens/p1..p3_*.png
"""
import layout as L
import elevador2 as E
import render_m as R

ROSA = "#d6246e"


def destaca(itens):
    return [(me, ROSA if pc.startswith(("Polia", "Rolamento", "Eixo da polia", "Acoplamento")) else cor, op, pc) for me, cor, op, pc in itens]


def main():
    R.IMG.mkdir(parents=True, exist_ok=True)
    R.IMPRESSAS = R.malhas_impressas()
    m = L.M()
    el = m.el
    zcA, zcB = m.zpA + m.dz_correia, m.zpB + m.dz_correia
    it = destaca(R.cena(m, el.zc_min + 150, el.ang_baixa, -40.0, 0.0))
    rot = [("1 Polia do motor do elevador (N20, no topo)", (el.x_polia, 192, el.z_polia_cima)),
           ("2 Polia de baixo do elevador (eixo M5)", (el.x_polia, 192, el.z_polia_baixo)),
           ("3 Polia do NEMA do eixo A", (m.x_motor, m.y_correia, zcA)), ("4 Tensora do eixo A", (m.x_tensora, m.y_correia, zcA)),
           ("5 Polia do NEMA do eixo B", (m.x_motor, m.y_correia, zcB)), ("6 Tensora do eixo B", (m.x_tensora, m.y_correia, zcB))]
    R.foto("p1_polias_geral.png", it, (0, 115, 215), (-0.75, -1.0, 0.62), 300, [], rot, vidro=("Torre inferior", "Torre superior"),
           titulo="As 6 polias (rosa). Torres do elevador transparentes")
    it = destaca(R.cena(m, el.zc_max, el.ang_baixa, -60.0, 0.0))
    zt = el.z_polia_cima
    rot = [("Motor N20 (solto no berco, so gira)", (191, 135, zt + 5)), ("Acoplamento rigido 3 x 5", (191, E.Y_FACE_MOTOR + 10.5, zt + 6)),
           ("Rolamento 625ZZ da frente", (191, 179, zt + 8)), ("Polia (no eixo de 5 mm)", (191, 192, zt + 9)),
           ("Rolamento 625ZZ de tras", (191, 206, zt + 8)), ("Sensor de fenda de cima", (E.X_BANDEIRA, E.Y_BANDEIRA, 418))]
    R.foto("p2_polia_topo_elevador.png", it, (192, 182, 412), (0.75, -0.6, 0.45), 42, [], rot, vidro=("Torre superior", "Cabine"),
           titulo="Topo do elevador: a polia num eixo de 5 mm apoiado nos 2 lados por rolamentos 625ZZ",
           esconde=("Torre inferior", "Perfil 2020 A", "Trilho MGN12 A", "Patim MGN12H A", "Prateleira", "Esteira A", "Bloco direito",
                    "Correia A", "Carro A", "Eletroima", "Rampa"))
    it = destaca(R.cena(m, el.zc_min, el.ang_baixa, -60.0, 0.0))
    rot = [("Polia de baixo: eixo M5 preso na placa de tras", (el.x_polia, 192, el.z_polia_baixo + 9)),
           ("Porca de nylon na frente", (el.x_polia, 185.5, el.z_polia_baixo))]
    R.foto("p3_polia_baixo_elevador.png", it, (192, 190, 18), (0.75, -0.6, 0.5), 38, [], rot, vidro=("Torre inferior", "Cabine"),
           titulo="Pe do elevador: a polia de baixo fica num eixo M5 em balanco na placa de tras",
           esconde=("Torre superior", "Bandeja", "EVA", "Fila", "Perfil 2020 B", "Trilho MGN12 B", "Carro B", "Patim MGN12H B",
                    "Esteira B", "Bloco direito", "LED", "Correia B"))
    print("ok")


if __name__ == "__main__":
    main()
