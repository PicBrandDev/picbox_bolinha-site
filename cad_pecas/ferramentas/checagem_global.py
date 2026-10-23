"""Checagem global da Maquina A montada: todo corpo fixo contra todo corpo fixo (impressas, compradas, bandeja,
divisoria e paredes) e os dois carros varrendo o curso contra tudo. Contatos de projeto vem do CONTATO_ESPERADO.
Uso: python ferramentas/checagem_global.py"""
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402

from common.checks import c7_interferencia, c8_movimento  # noqa: E402
from common.malha import para_trimesh, _shape  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402
from maquina_a import verifica as V  # noqa: E402

corpos, esperado = {}, {}
for pid, v, obj in MT.pecas_fixas():
    k = f"{pid}.{v}"
    corpos[k] = obj
    esperado[k] = tuple(getattr(MT.modulo(pid), "CONTATO_ESPERADO", ()))
corpos.update(MT.hardware_fixo())
for e in ("A", "B"):
    corpos.update(V.hardware_eixo(e))
corpos.update(MT.corpos_bandeja())
corpos.update(V.gabinete())

# contatos de compradas entre si (montadas de proposito): trilho/perfil/fc/correia do mesmo eixo, tubo nas pecas etc.
def contato(a, b):
    for x, y in ((a, b), (b, a)):
        if any(s in y for s in esperado.get(x, ())):
            return True
    mesmo_eixo = a[:2] == b[:2] and a[:2] in ("A.", "B.")
    if mesmo_eixo:
        return True
    pares = [("lateral", "A."), ("lateral", "B."), ("divisoria", "bandeja"), ("elev_", "elev_"), ("lateral", "divisoria"),
             ("fundo", "divisoria"), ("bandeja", "elev_acrilico"), ("divisoria", "elev_acrilico"), ("lateral", "A01"),
             ("lateral", "A02"), ("lateral", "A15"), ("lateral", "A16"), ("lateral", "A26"), ("lateral", "A19"),
             ("lateral", "A22"), ("lateral", "sg90"), ("bandeja", "A12"), ("bandeja", "A13"), ("divisoria", "A12")]
    return any((p in a and q in b) or (p in b and q in a) for p, q in pares)

bbs = {k: _shape(v).BoundingBox() for k, v in corpos.items()}
ruins = []
for a, b in combinations(corpos, 2):
    if contato(a, b):
        continue
    A, B = bbs[a], bbs[b]
    if A.xmin > B.xmax or A.xmax < B.xmin or A.ymin > B.ymax or A.ymax < B.ymin or A.zmin > B.zmax or A.zmax < B.zmin:
        continue
    r = c7_interferencia(corpos[a], {b: corpos[b]})
    if not r["ok"]:
        ruins.append((a, b, r["colisoes"][b]))
print(f"corpos fixos: {len(corpos)}; pares com interferencia: {len(ruins)}")
for a, b, v in ruins:
    print(f"  {a} x {b}: {v} mm3")

fixos_m = {k: para_trimesh(v, 0.1, 0.3) for k, v in corpos.items() if not any(t in k for t in ("trilho", "correia"))}
for e in ("A", "B"):
    c0, c1 = MT.CURSO[e]
    xs = list(np.arange(c0, c1 + 1e-6, 5.0)) + [c1]
    proprios = {k: m for k, m in fixos_m.items() if not k.startswith(f"{e}.") or "fc" in k}
    r = c8_movimento({k: m for k, m in proprios.items() if ".fc" not in k}, lambda x, e=e: V.carro_em(e, x), xs)
    print(f"carro {e}: {'ok' if r['ok'] else 'FOLGA BAIXA'}; menor folga {r['menor']}; abaixo de 1 mm: {r['abaixo_da_folga']}")
