"""Imagem do elevador inteiro com nomes (R2.2).  python render_elevador.py -> saida/imagens/e1_elevador.png"""
import layout as L
import render_m as R

ESCONDE = ("Gabinete", "Tela", "Bandeja", "Fila", "Perfil", "Trilho MGN12", "Patim", "Carro", "Esteira", "Bloco", "Prateleira",
           "Eletroima", "Arruela M10", "Correia A", "Correia B", "Polia GT2", "Polia tensora", "NEMA", "Fim de curso", "LED",
           "Ponta fixa", "Fixador de correia", "Anel", "Barreira", "Botao")


def main():
    R.IMG.mkdir(parents=True, exist_ok=True)
    R.IMPRESSAS = R.malhas_impressas()
    m = L.M()
    el = m.el
    zc = el.zc_min + 150
    k0, k1 = el.fix_z
    it = R.cena(m, zc, el.ang_baixa, -40.0, 0.0)
    bola_cab = (el.x_bola, el.y_bola, zc + L.R + 1.0)
    pc = el.z_polia_cima
    rot = [("1 Motor N20 (deitado no topo)", (191, 140, pc + 5)),
           ("2 Polia de CIMA = a sua polia de 16 mm. O motor gira ela", (el.x_polia, 192, pc + 8)),
           ("3 Sensor de cima: para a cabine no topo", (207, 196, 416)),
           ("4 Bolso: a bola sai da cabine e espera aqui", (196, 74, 352)),
           ("5 Correia (um laco so)", (el.x_volta, 192, 300)),
           ("6 Cabine (sobe e desce, leva 1 bola)", (191, 150, zc - 12)),
           ("7 Fixador: a correia prende na cabine aqui", (el.x_ida, 192, zc + k1 - 2)),
           ("8 Comporta (servo): solta 1 bola", (100, 102, 27)),
           ("9 Sensor de baixo: para a cabine embaixo", (207, 196, 14)),
           ("10 Polia de BAIXO (tensora antiga): so faz a correia voltar", (el.x_polia, 192, el.z_polia_baixo - 9))]
    R.foto("e1_elevador.png", it, (190, 150, 215), (0.55, 1.0, 0.22), 235, [bola_cab, tuple(m.bola_bolso)], rot,
           tam=(1500, 1900), vidro=("Cabine", "Rampa"), esconde=ESCONDE + ("Torre", "EVA"),
           titulo="ELEVADOR (visto de tras, sem a torre). Motor gira a polia de cima -> a correia puxa a cabine -> a bola sobe ate o bolso")
    print("ok")


if __name__ == "__main__":
    main()
