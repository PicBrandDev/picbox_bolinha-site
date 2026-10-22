# PICBOX — CAD das pecas impressas (Maquina A)

CAD parametrico em CadQuery (B-rep). Fluxo unico: `js/params.js` -> `params.json` -> pecas -> STEP/STL -> GLB.
A simulacao (Three.js) e o CAD antigo em `../cad/` (replicad) **nao sao fonte de geometria**: so de posicao e interface.

## Rodar
```
python -m venv .venv            (na raiz do repo; .venv fica fora do git)
.venv/Scripts/pip install cadquery trimesh numpy pyvista playwright manifold3d rtree scipy networkx
cd cad_py
../.venv/Scripts/python tools/build_all.py          # tudo: params, 13 checagens, STEP/STL/PNG, montagem, relatorios
../.venv/Scripts/python -m maquina_a.verifica A09   # uma peca (todas as variantes); A01:A = so a variante A
../.venv/Scripts/python tools/pack.py               # zip com os entregaveis
```
Coleta da pagina (Fase 1): `python -m http.server 8765` na raiz e `python tools/dump_scene.py`.

## Convencoes
- Unidade mm. CAD: **Z para cima**, X = direita do jogador, **Y = para o fundo** (frente = -Y), origem no centro do piso.
  Three.js: Y para cima. `CAD(x, y, z) = three(x, -z, y)` (`common/coords.py`).
- Eixos lineares: pecas desenhadas no referencial local do eixo (trilho em z=0); eixo B = translacao z+1175,
  eixo A = espelho em z + translacao z+1530 (`maquina_a/eixo.py`). Pecas da soltura estao em coordenadas da maquina.
- Toda cota e constante nomeada com UMA tag: `PARAMS`, `CENA`, `CATALOGO`, `MEDIDO`, `FAB`, `ESTIMADO`.
- Folgas, raios, espessuras e regras de impressao: so em `common/fab.py`.
- `medidas.json`: valores informados pelo usuario que valem por cima do `params.json` (bola 38 mm/60 g, boca Ø50).
- Cada peca expoe `build(p, var)` (posicao de montagem), `impressao(var)` (na mesa), `fixadores()`, `FICHA`.

## Estrutura
```
common/    fab, features, hardware (compradas, so checagem), coords, malha, checks, render, engrenagem, referencia
maquina_a/ layout.py, eixo.py, soltura.py, montagem.py (registro), verifica.py, assembly.py, parts/A*.py
           params.json, medidas.json, INVENTARIO/PENDENCIAS/VERIFICACAO/FILA_IMPRESSAO/BOM_FIXACAO/CHANGELOG.md
           out/{step,stl,png,glb,relatorios}
reference/A/  arquivos baixados da pagina /montagem e dump da cena (so referencia, nunca impressos)
tools/     params_to_json.mjs, dump_scene.py, build_all.py, relatorio.py, render_berco.py, diagnostico.py, pack.py
```
