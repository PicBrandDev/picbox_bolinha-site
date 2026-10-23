"""Montagem da Maquina A (sem gabinete): pecas impressas + compradas + bandeja, na posicao de montagem.

Uso (de dentro de cad_pecas/): python -m maquina_a.assembly
Saida (saidas/montagem/):
  maquina_a_montada.step  - tudo junto, coordenadas da maquina (mm, Z para cima), para abrir em CAD
  maquina_a.glb           - a mesma cena em malha (Y para cima, mm) para o visualizador; cada no tem o nome do arquivo
"""
from pathlib import Path

import cadquery as cq
import trimesh

from common.coords import CAD_PARA_THREE
from common.malha import para_trimesh
from maquina_a import montagem as MT
from maquina_a import verifica as V

OUT = Path(__file__).resolve().parents[1] / "saidas" / "montagem"
COR_PECA, COR_HW, COR_VIDRO = (0.91, 0.54, 0.17), (0.55, 0.55, 0.55), (0.62, 0.83, 0.91)


def pecas():
    """(pid, var, nome do arquivo, Workplane) de todas as pecas impressas na posicao de montagem (carros em x=0)."""
    for pid in MT.PECAS:
        mod = MT.modulo(pid)
        if getattr(mod, "FERRAMENTA", False):
            continue
        for v in MT.variantes(mod):
            yield pid, v, MT.nome_arquivo(pid, v), mod.build(None, v)


def compradas():
    out = {}
    for e in ("A", "B"):
        out.update(V.hardware_eixo(e))
        out[f"{e}.patim"] = V.E.para_maquina(V.hw.patim(0.0), e)
        out.update(MT.hardware_carro(e))
    out.update(MT.hardware_fixo())
    return out


def bandeja():
    return {k: v for k, v in MT.corpos_bandeja().items() if k != "divisoria"}   # sem gabinete


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    asm = cq.Assembly(name="maquina_a")
    cena = trimesh.Scene()

    def glb(nome, w, cor, tol=0.1):
        m = para_trimesh(w, tol, 0.3)
        m.apply_transform(CAD_PARA_THREE)
        m.visual.face_colors = [int(c * 255) for c in cor] + [255]
        cena.add_geometry(m, node_name=nome, geom_name=nome)

    for pid, v, nome, w in pecas():
        asm.add(w, name=nome, color=cq.Color(*COR_PECA))
        glb(nome, w, COR_PECA, 0.08)
    for nome, w in compradas().items():
        vidro = nome in ("tubo", "elev_acrilico")
        asm.add(w, name="comprada_" + nome.replace(".", "_"), color=cq.Color(*(COR_VIDRO if vidro else COR_HW), 0.5 if vidro else 1))
        glb("comprada_" + nome, w, COR_VIDRO if vidro else COR_HW)
    for nome, w in bandeja().items():
        cor = (0.2, 0.2, 0.2) if nome == "bandeja_eva" else (0.78, 0.66, 0.47)
        asm.add(w, name=nome, color=cq.Color(*cor))
        glb("bandeja_" + nome.split("_")[-1], w, cor, 0.5)
    asm.save(str(OUT / "maquina_a_montada.step"))
    cena.export(OUT / "maquina_a.glb")
    print("maquina_a_montada.step e maquina_a.glb:", len(cena.geometry), "corpos")


if __name__ == "__main__":
    main()
