"""Malhas de referencia da simulacao (somente para comparar intencao e posicao).

Le montagem/modelos/<peca>.glb e as matrizes de instancia do modulo 'maquina' do
guia.json e devolve trimesh no sistema CAD da maquina. Nunca usado como geometria."""
import json
from functools import lru_cache
from pathlib import Path

import trimesh

from .coords import instancia_para_cad

RAIZ = Path(__file__).resolve().parents[2]
GUIA = RAIZ / "montagem" / "guia.json"
MODELOS = RAIZ / "montagem" / "modelos"


@lru_cache(maxsize=1)
def guia():
    return json.loads(GUIA.read_text(encoding="utf8"))


def instancias(peca, modulo="maquina"):
    m = next(x for x in guia()["modulos"] if x["id"] == modulo)
    return [i for i in m["instancias"] if i["peca"] == peca and not i.get("oculta") and not i.get("contexto")]


@lru_cache(maxsize=None)
def _glb(peca):
    cena = trimesh.load(MODELOS / f"{peca}.glb", force="scene")
    # so as malhas trianguladas (o GLB tambem traz linhas de aresta)
    malhas = [g for g in cena.dump() if isinstance(g, trimesh.Trimesh) and len(g.faces)]
    return trimesh.util.concatenate(malhas)


def malha(peca, indice=0, modulo="maquina"):
    """Malha da peca na posicao da maquina (CAD). indice escolhe a instancia."""
    inst = instancias(peca, modulo)[indice]
    m = _glb(peca).copy()
    m.apply_transform(instancia_para_cad(inst["m"]))
    return m


def todas(peca, modulo="maquina"):
    return [malha(peca, k, modulo) for k in range(len(instancias(peca, modulo)))]
