"""Imagem de cada mesa de impressao (placa_XX.stl), vista de cima e em 3/4, com o contorno da mesa.

  python render_mesas.py  ->  saida/mesas/<placa>.png
"""
import json
from pathlib import Path

import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True
AQUI = Path(__file__).parent
S = AQUI / "saida"
CORES = ["#2f6fd6", "#e07a22", "#3f8f5f", "#b8457a", "#7a5cc7", "#c9a227", "#2b9aa6", "#a0522d"]


def main():
    plano = json.loads((S / "plano.json").read_text(encoding="utf8"))
    out = S / "mesas"
    out.mkdir(exist_ok=True)
    for k, lista in plano["placas"].items():
        lado = 260 if k == "A" else 220
        for p in lista:
            me = pv.read(str(S / "placas" / p["arquivo"]))
            partes = me.connectivity(extraction_mode="all").split_bodies()
            pl = pv.Plotter(off_screen=True, window_size=(900, 700))
            pl.set_background("#f4f6f4")
            mesa = pv.Box(bounds=(-lado / 2, lado / 2, -lado / 2, lado / 2, -2.0, 0.0))
            pl.add_mesh(mesa, color="#c9cfcb")
            pl.add_mesh(pv.Box(bounds=(-lado / 2 + 5, lado / 2 - 5, -lado / 2 + 5, lado / 2 - 5, -0.05, 0.0)),
                        style="wireframe", color="#7d8a83", line_width=1)
            for i, b in enumerate(partes):
                pl.add_mesh(b.extract_surface(algorithm="dataset_surface"), color=CORES[i % len(CORES)], smooth_shading=False, specular=0.15)
            pl.camera.focal_point = (0, 0, 15)
            pl.camera.position = (-lado * 0.9, -lado * 1.5, lado * 1.25)
            pl.camera.up = (0, 0, 1)
            pl.camera.parallel_projection = True
            pl.camera.parallel_scale = lado * 0.62
            pl.enable_anti_aliasing("ssaa")
            pl.screenshot(str(out / p["arquivo"].replace(".stl", ".png")))
            pl.close()
            print(p["arquivo"], len(partes), flush=True)


if __name__ == "__main__":
    main()
