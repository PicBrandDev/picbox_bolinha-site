# PICBOX compacta (R1)

Máquina A inteira dentro do gabinete de 420 × 420 × 200 (tela no fundo), bola de aço de 1" (25,4 mm, 67 g).

| Pasta | Para que serve |
|---|---|
| `imprimir/` | **Arquivos para imprimir.** Abra `impressao.html` (mesas por impressora, na ordem, com imagem) ou leia `ORDEM_DE_IMPRESSAO.txt`. |
| `imprimir/A_impressora_grande/` | Mesas da impressora boa, de 260 × 260: peças de precisão e as que ficam à vista. |
| `imprimir/B_creality_1/`, `imprimir/C_creality_2/` | Mesas das Creality, de 220 × 220: peças grandes e simples. |
| `imprimir/pecas_avulsas/` | Uma STL por peça, para reimprimir só uma. `__x2` no nome quer dizer imprimir 2 cópias. |
| `pagina/picbox_compacta.html` | Página com o 3D, a explicação de cada peça, a montagem passo a passo, os cabos e as checagens. Abra no navegador. |
| `imagens/` | Imagens da montagem feitas com as peças reais. |
| `step/` | Cada peça na posição de montagem, para abrir num CAD e editar. |
| `cad/` | Código que gera tudo. Só precisa abrir para mudar o projeto. |

## Como funciona

1. **Fila:** as bolas esperam numa calha no fundo, embaixo.
2. **Comporta:** um servo deixa passar uma bola por vez para a cabine do elevador.
3. **Elevador:** um motor N20 sobe a cabine. No topo, a bola rola por uma rampa até o bolso.
4. **Pega:** o carro A, no trilho de cima, para sobre o bolso e o eletroímã segura a bola. O sensor do bolso confirma a pega.
5. **Jogo:** o botão desliga o ímã e a bola cai 250 mm até o anel do carro B. A barreira infravermelha conta o acerto.
6. **Volta:** a bola cai na bandeja com EVA e rola até a fila.

## Para regerar tudo (se mudar o projeto)

Rode, de dentro de `cad/maquina/`, nesta ordem:

```
python checagem.py
python resistencia_m.py
python pecas.py
python teste_stl.py
python plano.py
python malhas.py
python render_m.py
python render_mesas.py
python impressao_html.py
python pagina_m.py
python publicar.py
```

`publicar.py` copia o resultado para `imprimir/`, `pagina/`, `imagens/` e `step/`.
