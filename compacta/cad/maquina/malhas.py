"""Malhas reais (dos STEPs gerados por pecas.py) na posicao de montagem, para o 3D da pagina.

Grava saida/malhas.json: por peca impressa, vertices (float32) e triangulos (uint32) em base64, o corpo que anda
e as copias (blocos do eixo B, ganchos).
"""
import base64
import json
from pathlib import Path

import numpy as np
import cadquery as cq

import layout as L

AQUI = Path(__file__).parent
S = AQUI / "saida"

CORPO = {"Cabine": "carro", "Braco da comporta": "alavanca", "Carro A": "carroA", "Carro B": "carroB"}


def main():
    m = L.M()
    imp = [l for l in json.loads((S / "impressao.json").read_text(encoding="utf8")) if "erro" not in l]
    out = []
    for l in imp:
        nome = l["arquivo"].split("__")[0].replace(".stl", "")
        arq = S / "step" / f"{nome}.step"
        sh = cq.importers.importStep(str(arq)).val()
        vs, tr = sh.tessellate(0.08, 0.3)
        V = np.array([v.toTuple() for v in vs], np.float32)
        T = np.array(tr, np.uint32)
        base = l["peca"]
        for suf in (" esquerda", " direita", " A (prateleira)", " B (piso)"):
            if base.endswith(suf) and base[:-len(suf)] in L.PECAS:
                base = base[:-len(suf)]
        copias = [[0, 0, 0]]
        if base == "Bloco direito":
            copias.append([0, 0, m.zpB - m.zpA])
        out.append(dict(peca=base, nome=l["peca"], arquivo=l["arquivo"], corpo=CORPO.get(base, "mundo"), copias=copias,
                        v=base64.b64encode(V.tobytes()).decode(), t=base64.b64encode(T.tobytes()).decode(),
                        nv=len(V), nt=len(T)))
        print(l["peca"], len(V), len(T), flush=True)
    (S / "malhas.json").write_text(json.dumps(out), encoding="utf8")
    print("total tri", sum(o["nt"] for o in out), "KB", (S / "malhas.json").stat().st_size // 1024)


if __name__ == "__main__":
    main()
