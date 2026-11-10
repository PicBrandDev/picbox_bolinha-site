"""Plano para UMA impressora so (Creality SparkX i7, mesa 260 x 260 x 255): todas as pecas no menor numero de mesas.

  python plano_unica.py  ->  saida_unica/placas/*.stl, saida_unica/plano.json, saida_unica/mesas/*.png

Empacotamento MaxRects (melhor encaixe pelo lado curto), pecas da maior para a menor, giro de 90 graus permitido.
Cada peca ocupa a caixa dela + 8 mm (aba de 5 mm e folga). A mesa util e 250 x 250 (5 mm de margem).
"""
import json
import math
import shutil
from pathlib import Path

import numpy as np
import trimesh

AQUI = Path(__file__).parent
S = AQUI / "saida"
U = AQUI / "saida_unica"
LADO = 260.0
UTIL = 250.0
ALTURA = 255.0
GAP = 8.0
NOME_IMP = "Creality SparkX i7"


class Bin:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.livres = [(0.0, 0.0, w, h)]
        self.itens = []

    def melhor(self, w, h):
        best = None
        for (x, y, fw, fh) in self.livres:
            for rw, rh, gir in ((w, h, False), (h, w, True)):
                if rw <= fw + 1e-6 and rh <= fh + 1e-6:
                    curto = min(fw - rw, fh - rh)
                    longo = max(fw - rw, fh - rh)
                    cand = (curto, longo, x, y, rw, rh, gir)
                    if best is None or cand[:2] < best[:2]:
                        best = cand
        return best

    def coloca(self, x, y, w, h):
        novos = []
        for (fx, fy, fw, fh) in self.livres:
            if x >= fx + fw or x + w <= fx or y >= fy + fh or y + h <= fy:
                novos.append((fx, fy, fw, fh))
                continue
            if x > fx:
                novos.append((fx, fy, x - fx, fh))
            if x + w < fx + fw:
                novos.append((x + w, fy, fx + fw - x - w, fh))
            if y > fy:
                novos.append((fx, fy, fw, y - fy))
            if y + h < fy + fh:
                novos.append((fx, y + h, fw, fy + fh - y - h))
        # tira os retangulos contidos em outros
        lim = []
        for i, a in enumerate(novos):
            if a[2] <= 1e-6 or a[3] <= 1e-6:
                continue
            dentro = False
            for j, b in enumerate(novos):
                if i != j and a[0] >= b[0] - 1e-6 and a[1] >= b[1] - 1e-6 and a[0] + a[2] <= b[0] + b[2] + 1e-6 \
                        and a[1] + a[3] <= b[1] + b[3] + 1e-6 and (a != b or i > j):
                    dentro = True
                    break
            if not dentro:
                lim.append(a)
        self.livres = lim


def empacotar(itens):
    bins = []
    for it in itens:
        best = None
        for b in bins:
            c = b.melhor(it["w"], it["h"])
            if c and (best is None or c[:2] < best[1][:2]):
                best = (b, c)
        if best is None:
            b = Bin(UTIL + GAP, UTIL + GAP)        # o GAP da ultima peca pode sair da area util
            c = b.melhor(it["w"], it["h"])
            if not c:
                return None
            bins.append(b)
            best = (b, c)
        b, (_, _, x, y, rw, rh, gir) = best
        b.coloca(x, y, rw, rh)
        b.itens.append(dict(it, x=x, y=y, gir=gir))
    return bins


def main():
    plano = json.loads((S / "plano.json").read_text(encoding="utf8"))
    pecas = plano["pecas"]
    itens = []
    for p in pecas:
        me = trimesh.load(str(S / "stl" / p["arquivo"]), force="mesh")
        ext = me.extents
        assert ext[2] <= ALTURA - 5, p["peca"]
        for i in range(p["quantidade"]):
            itens.append(dict(p=p, w=float(ext[0]) + GAP, h=float(ext[1]) + GAP, alt=float(ext[2])))
    import random
    rnd = random.Random(7)
    ordens = [sorted(itens, key=lambda it: -(it["w"] * it["h"])), sorted(itens, key=lambda it: -max(it["w"], it["h"])),
              sorted(itens, key=lambda it: -(it["w"] + it["h"]))]
    for _ in range(3000):
        o = itens[:]
        rnd.shuffle(o)
        o.sort(key=lambda it: -(it["w"] * it["h"]) * rnd.uniform(0.6, 1.4))
        ordens.append(o)
    melhor = None
    for o in ordens:
        bs = empacotar(o)
        if bs is None:
            continue
        ocup = sorted(sum(i["w"] * i["h"] for i in b.itens) for b in bs)
        nota = (len(bs), -ocup[-1] if len(ocup) else 0)
        if melhor is None or nota < melhor[0]:
            melhor = (nota, bs)
    bins = melhor[1]
    # mesa com as pecas que precisam de suporte primeiro (teste de encaixe), depois pela altura
    sup = lambda b: any(i["p"]["suporte"].startswith(("sim", "so")) for i in b.itens)
    bins.sort(key=lambda b: (not sup(b), max(i["alt"] for i in b.itens)))
    if U.exists():
        shutil.rmtree(U)
    (U / "placas").mkdir(parents=True)
    placas = []
    for n, b in enumerate(bins, 1):
        ms = []
        for i in b.itens:
            me = trimesh.load(str(S / "stl" / i["p"]["arquivo"]), force="mesh")
            if i["gir"]:
                me.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, (0, 0, 1)))
            lo = me.bounds[0]
            me.apply_translation((5 + i["x"] + GAP / 2 - lo[0] - LADO / 2, 5 + i["y"] + GAP / 2 - lo[1] - LADO / 2, -lo[2]))
            ms.append(me)
        t = trimesh.util.concatenate(ms)
        assert t.bounds[0][0] >= -LADO / 2 and t.bounds[1][0] <= LADO / 2 and t.bounds[0][1] >= -LADO / 2 \
            and t.bounds[1][1] <= LADO / 2, f"mesa {n} fora"
        arq = f"mesa_{n:02d}.stl"
        t.export(str(U / "placas" / arq))
        horas = round(sum(i["p"]["horas"] / i["p"]["quantidade"] for i in b.itens) + 0.2, 1)
        area = sum((i["w"] - GAP) * (i["h"] - GAP) for i in b.itens) / (UTIL * UTIL)
        placas.append(dict(n=f"{n:02d}", arquivo=arq, horas=horas, pecas=[i["p"]["peca"] for i in b.itens],
                           suporte=sup(b), altura=round(max(i["alt"] for i in b.itens), 1), ocupacao=round(100 * area)))
        for i in b.itens:
            i["p"].setdefault("mesas", [])
            if f"{n:02d}" not in i["p"]["mesas"]:
                i["p"]["mesas"].append(f"{n:02d}")
    for p in pecas:
        p["placas"] = p.pop("mesas", [])
    tot = round(sum(p["horas"] for p in placas), 1)
    (U / "plano.json").write_text(json.dumps(dict(placas={"S": placas}, total={"S": tot}, pecas=pecas), ensure_ascii=False,
                                             indent=1), encoding="utf8")
    txt = [f"PICBOX compacta R2 - TUDO NUMA IMPRESSORA SO ({NOME_IMP}, mesa 260 x 260)", "",
           "Cada mesa_XX.stl ja tem as pecas arrumadas e na posicao certa: NAO use orientacao automatica.",
           "PETG, bico 0,4, camada 0,2, 4 perimetros, 25%. Aba (brim) de 5 mm em todas as mesas.",
           "Mesas COM SUPORTE: suporte em arvore so nas pecas marcadas (cabine, carro A, carro B).",
           "Se o fatiador juntar tudo num objeto so, use 'Dividir em objetos'.", "",
           f"TOTAL: {len(placas)} mesas, ~{tot} h", ""]
    for p in placas:
        txt.append(f"  mesa {p['n']}  {p['horas']:>5} h  altura {p['altura']:.0f} mm  ocupa {p['ocupacao']}% da mesa"
                   f"{'  COM SUPORTE' if p['suporte'] else ''}")
        q = {}
        for x in p["pecas"]:
            q[x] = q.get(x, 0) + 1
        for x, k in q.items():
            txt.append(f"         - {x}{f' x{k}' if k > 1 else ''}")
    (U / "placas" / "LEIA-ME.txt").write_text("\n".join(txt), encoding="utf8")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
