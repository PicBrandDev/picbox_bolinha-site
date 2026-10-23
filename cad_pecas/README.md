# PICBOX — CAD das peças impressas (Máquina A)

CAD paramétrico em CadQuery (B-rep). Fluxo único: `js/params.js` → `maquina_a/params.json` → peças → STEP/STL →
montagem → relatórios → visualizador. A simulação (Three.js) e o CAD antigo em `../cad/` (replicad) **não são fonte
de geometria**: só de posição e interface.

## O que tem em `saidas/`

| Pasta / arquivo | Conteúdo |
|---|---|
| `visualizador.html` | Máquina montada com a lista de peças: clicar destaca; "peça a peça"; links de STL/STEP. Abre direto. |
| `stl_para_imprimir/<grupo>/` | Uma STL por peça, **já na orientação de impressão** (mm). |
| `step/<grupo>/` | Uma STEP por peça, **na posição de montagem** (coordenadas da máquina). |
| `montagem/maquina_a_montada.step` | Tudo junto, sem gabinete: impressas + compradas + bandeja. |
| `montagem/maquina_a.glb` | A mesma cena em malha (Y para cima), usada pelo visualizador. |
| `imagens/pecas/` | Por peça: vista, contexto, mesa da impressora, comparação com o CAD antigo. |
| `imagens/explicativas/` | Como as partes funcionam (caminho da bola, elevador, carga do berço, solenoide…). |
| `relatorios/` | As 13 verificações de cada peça (JSON). |

Nome dos arquivos: `ID_peça__posição[__xQuantidade]`, por exemplo
`A01_bloco-motor__eixoB-baixo_ponta-direita-motor.stl` ou `A07_presilha__eixoA-cima_carro-correia__x2.stl`.

Grupos: `1_eixos`, `2_boca_e_soltura`, `3_magazine_e_carga`, `4_bandeja`, `5_elevador`.

## Rodar

```bash
cd cad_pecas
../.venv/Scripts/python ferramentas/build_all.py          # tudo: params, 13 checagens, STEP/STL, montagem, relatórios, visualizador
../.venv/Scripts/python -m maquina_a.verifica A09         # uma peça (todas as variantes); A01:A = só a variante A
../.venv/Scripts/python ferramentas/checagem_global.py    # todos os corpos fixos entre si + os dois carros no curso inteiro
../.venv/Scripts/python ferramentas/pack.py               # zip com os entregáveis (fora do git)
```

Imagens explicativas: `ferramentas/render_*.py saidas/imagens/explicativas` e `ferramentas/mapa_pecas.py`.

## As 13 verificações (por peça)

B-rep válido · STL estanque · cabe na mesa · intenção vs. CAD antigo · espessura de parede · balanço e pontes ·
interferência com tudo o que é fixo · folga em movimento (carros no curso inteiro) · alinhamento de furos ·
caminho da bola · imagens · estimativa de tempo/massa · acesso de chave na ordem de montagem.
Tolerâncias justificadas (quando a medida é artefato) ficam escritas na própria peça e no relatório.

## Convenções

- Unidade mm. CAD: **Z para cima**, X = direita do jogador, **Y = para o fundo** (frente = −Y), origem no centro do piso.
  Three.js: Y para cima. `CAD(x, y, z) = three(x, −z, y)` (`common/coords.py`).
- Eixos lineares: peças desenhadas no referencial local do eixo (trilho em z=0); eixo B = translação z+1175,
  eixo A = espelho em z + translação z+1530 (`maquina_a/eixo.py`). As demais peças estão em coordenadas da máquina.
- Toda cota é constante nomeada com UMA tag: `PARAMS`, `CENA`, `CATALOGO`, `MEDIDO`, `FAB`, `ESTIMADO`.
- Folgas, raios, espessuras e regras de impressão: só em `common/fab.py`.
- `maquina_a/medidas.json`: valores informados pelo usuário (bola 38 mm/60 g, boca Ø50) por cima do `params.json`.
- Cada peça expõe `build(p, var)` (posição de montagem), `impressao(var)` (na mesa), `fixadores()`, `FICHA`.
- Registro das peças, grupos e posições: `maquina_a/montagem.py` (`PECAS`, `GRUPOS`, `POSICAO`).

## Estrutura

```
common/        fab, features, hardware (compradas, só checagem), coords, malha, checks, render, engrenagem, referencia
maquina_a/     layout, eixo, soltura, magazine, bandeja, elevador (+ elevador_bola.json), montagem, verifica, assembly
  pecas/       A01_bloco_motor.py … A27_cabeca_elevador.py (uma peça por arquivo)
ferramentas/   build_all, relatorio, visualizador, checagem_global, pack, render_*, mapa_pecas, tabela_bola,
               diagnostico, diag_peca, dump_scene, params_to_json.mjs, teste_ambiente
docs/          INVENTARIO, PENDENCIAS, VERIFICACAO, FILA_IMPRESSAO, BOM_FIXACAO, CHANGELOG, REFERENCIA_CAD_ANTIGO
saidas/        tudo o que é gerado (ver acima)
```
