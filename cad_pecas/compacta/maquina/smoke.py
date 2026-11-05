import layout as L

m = L.M()
g = L.geometria(m)
print(len(g), "bola bolso", m.bola_bolso.round(2), "face", round(m.face_ima, 2), "zs", round(m.zs, 2), "zb", round(m.zb, 2))
print("S", [round(m.s_bandeja(x, y), 1) for x, y in ((-207, 47.5), (-207, 127.5), (-30, 127.5), (144, 52.3), (207, 47.5))])
print("labio", [round(m.z_labio(x), 1) for x in (-207, -30, 40)], "fila", [round(m.f_fila(x), 1) for x in (-207, -30, 174)])
print(len(L.fixadores(m)), "fix")
print(L.esteira_caixas(m, "A", 0)[1], L.esteira_caixas(m, "B", 0)[1])
