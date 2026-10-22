"""Montagem da Maquina A: pecas novas + compradas de referencia.

Uso: python -m maquina_a.assembly
Saida: out/assembly.step (pecas impressas, B-rep) e out/glb/assembly.glb (Y up, mm, para o simulador; inclui compradas).
"""
from pathlib import Path

import cadquery as cq
import trimesh

from common.coords import CAD_PARA_THREE
from common.malha import para_trimesh
from maquina_a import montagem as MT
from maquina_a import verifica as V

OUT = Path(__file__).resolve().parent / "out"


def pecas():
    """(nome, Workplane) de todas as pecas impressas na posicao de montagem (carros em x=0)."""
    for pid in MT.PECAS:
        mod = MT.modulo(pid)
        if getattr(mod, "FERRAMENTA", False):
            continue
        for v in MT.variantes(mod):
            yield f"{pid}_{mod.NOME}_{v}", mod.build(None, v)


def compradas():
    out = {}
    for e in ("A", "B"):
        out.update(V.hardware_eixo(e))
        out[f"{e}.patim"] = V.E.para_maquina(V.hw.patim(0.0), e)
        out.update(MT.hardware_carro(e))
    return out


def main():
    (OUT / "glb").mkdir(parents=True, exist_ok=True)
    asm = cq.Assembly(name="maquina_a")
    cena = trimesh.Scene()
    for nome, w in pecas():
        asm.add(w, name=nome, color=cq.Color(0.91, 0.54, 0.17))
        m = para_trimesh(w, 0.05, 0.2)
        m.apply_transform(CAD_PARA_THREE)
        m.visual.face_colors = [232, 137, 43, 255]
        cena.add_geometry(m, node_name=nome, geom_name=nome)
    for nome, w in compradas().items():
        m = para_trimesh(w, 0.1, 0.3)
        m.apply_transform(CAD_PARA_THREE)
        m.visual.face_colors = [150, 150, 150, 255]
        cena.add_geometry(m, node_name="hw_" + nome, geom_name="hw_" + nome)
    asm.save(str(OUT / "assembly.step"))
    cena.export(OUT / "glb" / "assembly.glb")
    print("assembly.step e assembly.glb:", len(cena.geometry), "corpos")


if __name__ == "__main__":
    main()
