"""Imagens das polias: onde fica cada uma e como esta apoiada.

  python render_polias.py  ->  saida/imagens/p1..p3_*.png
"""
import layout as L
import elevador2 as E
import render_m as R

ROSA = "#d6246e"


def destaca(itens):
    return [(me, ROSA if pc.startswith(("Polia", "Rolamento", "Parafuso M5", "Acoplamento", "Arruela", "Espacador", "Parafuso sem")) else cor, op, pc) for me, cor, op, pc in itens]


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
    rot = [("Motor N20 (deitado no berco)", (191, 135, zt + 5)), ("Adaptador N20-M5 (o M5 rosqueia nele)", (191, 165, zt + 6)),
           ("Polia 16 mm (cubo para o motor)", (191, 184, zt + 8)), ("Espacador da parede (6,8)", (191, 199, zt + 3)),
           ("Rolamento 625ZZ (colado)", (191, 206, zt + 8)), ("Cabeca do M5x45", (191, 212, zt + 4))]
    R.foto("p2_polia_topo_elevador.png", it, (192, 182, 412), (0.75, -0.6, 0.45), 42, [], rot, vidro=("Torre superior", "Cabine"),
           titulo="Topo do elevador: a polia num parafuso M5, 1 rolamento atras e o eixo do N20 na frente",
           esconde=("Torre inferior", "Perfil 2020 A", "Trilho MGN12 A", "Patim MGN12H A", "Prateleira", "Esteira A", "Bloco direito",
                    "Correia A", "Carro A", "Eletroima", "Rampa"))
    it = destaca(R.cena(m, el.zc_min, el.ang_baixa, -60.0, 0.0))
    rot = [("Polia de baixo: eixo M5 preso na placa de tras", (el.x_polia, 192, el.z_polia_baixo + 9)),
           ("Porca de nylon na frente", (el.x_polia, 185.5, el.z_polia_baixo))]
    R.foto("p3_polia_baixo_elevador.png", it, (192, 190, 18), (0.75, -0.6, 0.5), 38, [], rot, vidro=("Torre inferior", "Cabine"),
           titulo="Pe do elevador: a polia de baixo fica num eixo M5 em balanco na placa de tras",
           esconde=("Torre superior", "Bandeja", "EVA", "Fila", "Perfil 2020 B", "Trilho MGN12 B", "Carro B", "Patim MGN12H B",
                    "Esteira B", "Bloco direito", "LED", "Correia B"))
    # laco inteiro da correia, visto de tras, cabine no meio do curso
    zm = (el.zc_min + el.zc_max) / 2
    it = destaca(R.cena(m, zm, el.ang_baixa, -60.0, 0.0))
    k0, k1 = el.fix_z
    rot = [("Polia do motor (topo)", (el.x_polia, 192, el.z_polia_cima + 9)), ("Polia de baixo", (el.x_polia, 192, el.z_polia_baixo - 9)),
           ("Ramo PRESO: as 2 pontas entram no fixador", (el.x_ida, 192, zm + k1 + 60)),
           ("Ramo LIVRE: passa ao lado da cabine", (el.x_volta, 192, zm - 60)),
           ("Fixador de aluminio (dentes na face dentada)", (el.x_ida - 3, 192, zm + (k0 + k1) / 2))]
    R.foto("p4_laco_correia.png", it, (191, 190, 215), (0.3, -1.0, 0.12), 250, [], rot, vidro=("Cabine",), tam=(1100, 1600),
           titulo="Correia do elevador vista de frente (cabine transparente): um laco, a cabine presa no ramo da direita",
           esconde=("Torre inferior", "Torre superior", "Gabinete", "Tela", "Bandeja", "EVA", "Fila", "Rampa", "Perfil", "Trilho MGN12",
                    "Patim", "Carro", "Esteira", "Bloco", "Prateleira", "Eletroima", "Arruela", "Correia A", "Correia B", "Polia GT2",
                    "Polia tensora", "NEMA", "Fim de curso", "Servo", "Braco", "LED", "Ponta fixa", "Fixador de correia", "Sensor do bolso"))
    # vista explodida da polia de cima (R2.2): as pecas na ordem do parafuso, afastadas ao longo do eixo
    import numpy as np
    import pyvista as pv
    pv.OFF_SCREEN = True
    ordem = [("Motor N20", "box", (E.Y_FACE_MOTOR - 32.5, E.Y_FACE_MOTOR), (6, 5), "#7d8790"),
             ("Adaptador N20-M5", "ad", E.PC_ACOPL, E.PC_ACOPL_R, "#2f9e8f"),
             ("Polia 16 mm (cubo para o motor)", "polia", (E.PC_CUBO[0], E.PC_POLIA[1]), E.PC_R_POLIA, "#d6246e"),
             ("Espacador da parede (6,8 mm)", "cil", E.PC_ESP_T, 3.2, "#2f9e8f"),
             ("Rolamento de tras (colado)", "cil", E.PC_ROL_T, 8.0, "#d6246e"),
             ("Arruela impressa", "cil", E.PC_ARR_T, 3.75, "#2f9e8f"),
             ("Parafuso M5x45", "m5", E.PC_CABECA, 4.25, "#c8a23c")]
    pl = pv.Plotter(off_screen=True, window_size=(2000, 560))
    pl.set_background("#f4f6f4")
    gap, desl, pts, txt = 14.0, 0.0, [], []
    for i, (nome, tp, (y0, y1), r, cor) in enumerate(ordem):
        d = i * gap + (E.PC_M5 + 6 if tp == "m5" else 0)
        if tp == "box":
            me = pv.Box(bounds=(-r[0], r[0], y0 + d, y1 + d, -r[1], r[1]))
        elif tp == "polia":
            me = pv.Cylinder(center=(0, (E.PC_CUBO[0] + E.PC_CUBO[1]) / 2 + d, 0), direction=(0, 1, 0), radius=r,
                             height=E.PC_CUBO[1] - E.PC_CUBO[0], resolution=48)
            yp0, yp1 = E.PC_POLIA
            for a0, a1, ra in ((yp0, yp0 + 0.85, r), (yp0 + 0.85, yp1 - 0.85, 6.1), (yp1 - 0.85, yp1, r)):
                me = me.merge(pv.Cylinder(center=(0, (a0 + a1) / 2 + d, 0), direction=(0, 1, 0), radius=ra, height=a1 - a0,
                                          resolution=48))
        elif tp == "ad":
            me = pv.Cylinder(center=(0, (y0 + E.PC_AD_FL[0]) / 2 + d, 0), direction=(0, 1, 0), radius=r,
                             height=E.PC_AD_FL[0] - y0, resolution=48)
            me = me.merge(pv.Cylinder(center=(0, (E.PC_AD_FL[0] + y1) / 2 + d, 0), direction=(0, 1, 0), radius=E.PC_AD_FL_R,
                                      height=y1 - E.PC_AD_FL[0], resolution=48))
        elif tp == "m5":
            me = pv.Cylinder(center=(0, (y0 + y1) / 2 + d, 0), direction=(0, 1, 0), radius=r, height=y1 - y0, resolution=48)
            me = me.merge(pv.Cylinder(center=(0, y0 - E.PC_M5 / 2 + d + 0.01, 0), direction=(0, 1, 0), radius=2.5,
                                      height=E.PC_M5, resolution=32))
        else:
            fora = pv.Cylinder(center=(0, (y0 + y1) / 2 + d, 0), direction=(0, 1, 0), radius=r, height=y1 - y0, resolution=48)
            me = fora
        pl.add_mesh(me, color=cor, smooth_shading=True)
        rr = (r[1] if tp == "box" else r) + 4
        pts.append((0, (y0 + y1) / 2 + d, rr if i % 2 else -rr - 5))
        txt.append(nome)
    # eixo do N20 (curto) e linha do parafuso
    pl.add_mesh(pv.Cylinder(center=(0, E.Y_FACE_MOTOR + 4, 0), direction=(0, 1, 0), radius=1.5, height=8), color="#7d8790")
    pl.add_point_labels(np.array(pts), txt, font_size=15, point_size=1, shape_opacity=0.85, always_visible=True, show_points=False,
                        text_color="#1d2328", shape_color="white")
    pl.add_text("Polia de cima R2.2, separada na ordem (verde = imprime, rosa = rolamento e polia, amarelo = M5x45 entra por tras)",
                font_size=11, color="#1d2328")
    pl.camera_position = [(-300, 262, 110), (0, 262, 0), (0, 0, 1)]
    pl.camera.zoom(1.75)
    pl.screenshot(str(R.IMG / "p5_montagem_polia_cima.png"))
    pl.close()
    print("ok")


if __name__ == "__main__":
    main()
