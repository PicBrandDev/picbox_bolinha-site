# PICBOX – Máquina A (bolinha)

Duas versões da mesma máquina, cada uma na sua pasta.

| Pasta | O que é |
|---|---|
| [`compacta/`](compacta/LEIA-ME.md) | **Versão atual.** Cabe no gabinete de 420 × 420 × 200 com a tela no fundo, bola de aço de 1". É a que está sendo impressa. |
| [`normal/`](normal/LEIA-ME.md) | Versão original: gabinete de 450 × 450 × 1700, bola de 38 mm. CAD das peças, documentos de projeto e o simulador do site. |

## Para imprimir a compacta

Abra `compacta/imprimir/ORDEM_DE_IMPRESSAO.txt`. Cada impressora tem a sua pasta, com as mesas numeradas na ordem:

- `compacta/imprimir/A_impressora_grande/`
- `compacta/imprimir/B_creality_1/`
- `compacta/imprimir/C_creality_2/`

## Observações

- O site no ar (Railway) é publicado do ramo `main`, que não mudou. Neste ramo (`cad-pecas`), o site fica em `normal/simulacao/`. Não junte este ramo no `main` sem antes ajustar o `railway.json`.
- `CLAUDE.md` traz as instruções para o assistente.
