"""Testes na geometria REAL que vai para a impressora (STEP de cada peca, na posicao de montagem).

 1. pecas impressas nao entram umas nas outras (volume de intersecao das malhas)
 2. cada parafuso: o furo existe (o eixo do parafuso passa livre nas pecas que ele atravessa) e a rosca tem plastico
 3. bola no bolso da rampa e bola passando no anel, contra a malha real
 4. cada STL de impressao: assentada em Z 0, area de apoio na mesa, maior altura, um corpo, fechada
"""
import itertools
import json
import math
import re
from pathlib import Path

import numpy as np
import trimesh
import cadquery as cq
import manifold3d as mf

import layout as L
import pecas as PC

AQUI = Path(__file__).parent
S = AQUI / "saida"


def malha_step(arq):
    sh = cq.importers.importStep(str(arq)).val()
    vs, tr = sh.tessellate(0.05, 0.2)
    return trimesh.Trimesh(np.array([v.toTuple() for v in vs]), np.array(tr), process=True)


def man(me):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(me.vertices, np.float32), tri_verts=np.asarray(me.faces, np.uint32)))


def main():
    res = {}
    imp = json.loads((S / "impressao.json").read_text(encoding="utf8"))
    nomes = {l["arquivo"].split("__")[0].replace(".stl", ""): l["peca"] for l in imp if "arquivo" in l}
    malhas = {}
    for arq in sorted((S / "step").glob("*.step")):
        malhas[arq.stem] = malha_step(arq)
    print("STEPs", len(malhas))
    # ---- 1
    ruins = []
    mans = {k: man(v) for k, v in malhas.items()}
    for a, b in itertools.combinations(malhas, 2):
        la, ha = malhas[a].bounds
        lb, hb = malhas[b].bounds
        if np.any(ha < lb) or np.any(hb < la):
            continue
        inter = mans[a] ^ mans[b]
        v = inter.volume()
        if v > 0.5:                                   # mm3
            area = inter.surface_area()
            esp = 2 * v / area if area > 0 else 0     # espessura media da intersecao
            if esp > 0.1:                             # 0,02 mm de cada lado = faces encostadas (montagem), nao conta
                ruins.append(dict(a=a, b=b, mm3=round(v, 1), espessura=round(esp, 3)))
    res["intersecoes"] = dict(ruins=ruins, pecas=len(malhas), ok=not ruins)
    print("INTERSECOES", ruins)
    # ---- 2 furos
    m = L.M()
    el = m.el
    furo_ruim = []
    for f in L.fixadores(m):
        p0 = np.array(f["p0"], float)
        if f["corpo"] == "carro":
            p0[2] += el.zc_min
        d = np.array(f["dir"], float)
        b = PC.bitola(f["tipo"])
        for peca in {f["prende"], *f["atravessa"], f["rosca"]}:
            if L.PECAS.get(peca, ("?",))[0] != "impressa":
                continue
            if peca in PC.SO_EIXO_A and ("_B_" in f["nome"] or f["nome"].endswith("_B")):
                continue                              # o STL e o do eixo A (o do B e igual)
            chave = re.sub(r"[^a-z0-9]+", "_", peca.lower().translate(str.maketrans("áàãâéêíóôõúç", "aaaaeeiooouc"))).strip("_")
            cand = [k for k in malhas if k.startswith(chave)]
            if not cand:
                continue
            me = malhas[cand[0]] if len(cand) == 1 else trimesh.util.concatenate([malhas[k] for k in cand])
            ts = np.linspace(0.3, f["L"] - 0.3, 25)
            P = p0 + np.outer(ts, d)
            dentro = me.contains(P)
            porca = "porca" in f["tipo"] or "martelo" in f["tipo"] or f.get("insert") is False
            if peca == f["rosca"] and peca != f["prende"] and not porca:
                # rosca no PETG: o eixo fica livre (piloto) mas a 1,6 mm do eixo tem plastico
                u = np.cross(d, [0, 0, 1.0]) if abs(d[2]) < 0.9 else np.cross(d, [1.0, 0, 0])
                u /= np.linalg.norm(u)
                anel = P + 1.6 * u
                pega = me.contains(anel).sum() * (f["L"] - 0.6) / 25
                if pega < (3.5 if b == "M2" else 4.0) and b != "madeira":
                    furo_ruim.append(dict(f=f["nome"], peca=peca, problema=f"pouco plastico para rosca ({pega:.1f} mm)"))
            if dentro.any():
                furo_ruim.append(dict(f=f["nome"], peca=peca, problema=f"eixo do parafuso bate no plastico ({dentro.sum()}/25)"))
    res["furos"] = dict(ruins=furo_ruim, ok=not furo_ruim)
    print("FUROS", len(furo_ruim), furo_ruim[:15])
    # ---- 3 bola
    bola = trimesh.creation.icosphere(subdivisions=4, radius=L.R)
    out = {}
    r = malhas["rampa"]
    b1 = bola.copy()
    b1.apply_translation(m.bola_bolso)
    v = (man(b1) ^ mans["rampa"]).volume()
    q = trimesh.proximity.ProximityQuery(r)
    dmin = float(np.min(np.abs(q.signed_distance(b1.vertices))))
    out["bolso"] = dict(entra_mm3=round(v, 2), menor_dist=round(dmin, 2), ok=v < 2.0)
    a = malhas["carro_b"]
    for dlt in (0.0, 6.0):
        piores = []
        for z in np.arange(m.zb + 15, m.zb - m.h_anel - 15, -1.0):
            b2 = bola.copy()
            b2.apply_translation((dlt, m.y_bola, z))
            piores.append((man(b2) ^ mans["carro_b"]).volume())
        out[f"anel_{dlt}"] = dict(entra_mm3=round(max(piores), 2), ok=max(piores) < 0.01)
    res["bola"] = out
    print("BOLA", out)
    # ---- 4 stl na mesa
    mesa = []
    suporte = {l["arquivo"]: l["suporte"].startswith("sim") for l in imp if "arquivo" in l}
    for arq in sorted((S / "stl").glob("*.stl")):
        me = trimesh.load(str(arq), force="mesh")
        z0 = me.bounds[0][2]
        n, ar, c = me.face_normals, me.area_faces, me.triangles_center
        apoio = ar[(n[:, 2] < -0.99) & (c[:, 2] < z0 + 0.05)].sum()
        mesa.append(dict(stl=arq.name, z0=round(float(z0), 3), apoio_cm2=round(float(apoio) / 100, 1),
                         fechada=bool(me.is_watertight), corpos=len(me.split(only_watertight=False)),
                         ok=bool(abs(z0) < 0.01 and me.is_watertight and (
                             apoio > 0.3 * min(2000.0, float(np.prod(me.extents[:2]))) or (suporte.get(arq.name) and apoio > 100)
                             or (arq.name.startswith("bucha") and apoio > 30))),     # buchas: anel inteiro na mesa
                         nota="com suporte e aba (brim)" if suporte.get(arq.name) else
                         "pecas pequenas: aba (brim) de 5 mm" if arq.name.startswith("bucha") else ""))
    res["mesa"] = mesa
    for l in mesa:
        if not l["ok"]:
            print("MESA RUIM", l)
    print("MESA", sum(l["ok"] for l in mesa), "de", len(mesa))
    (AQUI / "teste_stl.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=float), encoding="utf8")


if __name__ == "__main__":
    main()
