"""Elevador em 3D (o mesmo da imagem e1_elevador.png: sem a torre, com os nomes), pagina HTML de arquivo unico.

  python elevador3d.py  ->  compacta/pagina/PICBOX_elevador_3D.html
A cabine anda: cada malha guarda os vertices na cabine embaixo (zc_min) e quanto cada vertice anda por mm de cabine
(a cabine e a correia presa sao lineares em zc).
"""
import base64
import json
from pathlib import Path

import numpy as np
import pyvista as pv

import layout as L
import render_m as R
from render_elevador import ESCONDE

AQUI = Path(__file__).resolve().parent
TPL = AQUI / "elevador3d_tpl.html"
SAIDA = AQUI.parents[1] / "pagina" / "PICBOX_elevador_3D.html"
VIDRO = ("Cabine", "Rampa")
CENTRO = np.array([190.0, 150.0, 215.0])


def b64(a, tp):
    return base64.b64encode(np.ascontiguousarray(a, tp).tobytes()).decode()


def filtra(itens):
    return [(me, cor, (0.3 if pc in VIDRO else op), pc) for me, cor, op, pc in itens
            if not any(pc.startswith(x) for x in ESCONDE + ("Torre", "EVA"))]


def tri(me):
    t = me.triangulate()
    f = t.faces.reshape(-1, 4)[:, 1:]
    return np.asarray(t.points, float), f


def main():
    R.IMPRESSAS = R.malhas_impressas()
    m = L.M()
    el = m.el
    z0, z1 = el.zc_min, el.zc_max
    A = filtra(R.cena(m, z0, el.ang_baixa, -40.0, 0.0))
    B = filtra(R.cena(m, z1, el.ang_baixa, -40.0, 0.0))
    assert len(A) == len(B)
    grupos = {}
    for (ma, cor, op, pc), (mb, *_r) in zip(A, B):
        pa, f = tri(ma)
        pb, _ = tri(mb)
        anda = pa.shape == pb.shape and np.abs(pb - pa).max() > 1e-6
        k = (pv.Color(cor).hex_rgb, round(op, 2), bool(anda))
        g = grupos.setdefault(k, dict(v=[], dv=[], t=[], n=0))
        g["v"].append(pa - CENTRO)
        g["dv"].append((pb - pa) / (z1 - z0) if anda else np.zeros_like(pa))
        g["t"].append(f + g["n"])
        g["n"] += len(pa)
    malhas = []
    for (cor, op, anda), g in grupos.items():
        d = dict(cor=cor, op=op, v=b64(np.vstack(g["v"]), np.float32), t=b64(np.vstack(g["t"]), np.uint32))
        if anda:
            d["dv"] = b64(np.vstack(g["dv"]), np.float32)
        malhas.append(d)
    k0, k1 = el.fix_z
    pc = el.z_polia_cima

    def p(x, y, z):
        return [round(v, 2) for v in (np.array([x, y, z]) - CENTRO)]
    # (texto, descricao, ponto, anda com a cabine, deslocamento do texto em px)
    rot = [("1 Motor N20", "no topo, deitado no berço", p(191, 140, pc + 5), False, -16),
           ("2 Polia de cima", "a sua polia de 16 mm; o motor gira ela", p(el.x_polia, 192, pc + 8), False),
           ("3 Sensor de cima", "para a cabine no topo", p(207, 196, 416), False, 14),
           ("4 Bolso", "a bola sai da cabine e espera aqui", p(196, 74, 352), False),
           ("5 Correia", "um laço só", p(el.x_volta, 192, 300), False),
           ("6 Cabine", "sobe e desce, leva 1 bola", p(191, 150, z0 - 12), True),
           ("7 Fixador", "a correia prende na cabine aqui", p(el.x_ida, 192, z0 + k1 - 2), True),
           ("8 Comporta (servo)", "solta 1 bola na cabine", p(100, 102, 27), False),
           ("9 Sensor de baixo", "para a cabine embaixo", p(207, 196, 14), False, -12),
           ("10 Polia de baixo", "a tensora antiga; só faz a correia voltar", p(el.x_polia, 192, el.z_polia_baixo - 9), False, 12)]
    dados = dict(malhas=malhas, rot=rot, z0=round(z0, 3), z1=round(z1, 3), r=L.R,
                 bola_cab=p(el.x_bola, el.y_bola, z0 + L.R + 1.0), bola_bolso=p(*m.bola_bolso),
                 cam=[0.55, 1.0, 0.22])
    html = TPL.read_text(encoding="utf8").replace("/*DADOS*/null", json.dumps(dados, separators=(",", ":")))
    SAIDA.write_text(html, encoding="utf8")
    print("ok", SAIDA, round(len(html) / 1e6, 2), "MB", sum(len(x["t"]) for x in malhas))


if __name__ == "__main__":
    main()
