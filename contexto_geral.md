# Contexto geral: PICBOX compacta (para continuar em outra sessão)

Atualizado em 09/11/2026. Branch `cad-pecas` (último commit 490ef9a). **Não fazer merge no `main`**: o site no Railway publica o `main`.

## O projeto
- Máquina A da PICBOX dentro de um gabinete de **420 × 420 × 200 mm livres**, com a tela no fundo. O gabinete é de MDF/madeira e aceita parafuso de madeira.
- Bola de aço de 1" (Ø25,4 mm, 67 g).
- **Ciclo:**
  1. Fila (calha no fundo).
  2. Comporta com servo SG90.
  3. Elevador de cabine com N20 e correia GT2 6 aberta.
  4. Rampa até o bolso.
  5. O carro A (trilho de cima) pega a bola com o eletroímã P20/15.
  6. O jogador aperta e a bola cai 250 mm no anel do carro B (trilho de baixo), com barreira infravermelha.
  7. Bandeja com EVA 5 mm.
  8. Volta para a fila.
- **Eletrônica:** fora da caixa (fonte, ESP32, drivers). O firmware não está no repo.
- **Impressoras** (todas com 250 mm de altura):
  - **A**: 260 × 260, a melhor. Peças de precisão e as que ficam à vista vão nela.
  - **B e C**: Creality 220 × 220.
- **O usuário já tem:** 2 jogos de perfil 2020 + MGN12 + NEMA17 (com driver, polias e GT2 6), eletroímã P20/15, KW10, SG90, parafusos, filamento PETG. Ele quer sempre a opção mais barata.

## Como o usuário quer as respostas
- Português, extremamente conciso (ver `CLAUDE.md`).
- Entregar **só as peças alteradas**, numa mesa pronta da impressora A, com LEIA-ME e o que comprar.
- Arquivos para enviar a outras pessoas: HTML de arquivo único, com tudo embutido.
- Commits só quando pedir. Os commits vão na `cad-pecas`, com a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Não mexer em configurações de segurança do Windows (o MuJoCo foi bloqueado; as checagens usam numpy puro).

## Estrutura
```
compacta/
  cad/maquina/   código da máquina inteira (o que importa)
  cad/elevador/  modelo do elevador (importado por layout.py)
  imprimir/      mesas por impressora, pecas_avulsas/, ALTERADAS_R1.1/, ALTERADAS_R1.2/ (+ .zip)
  pagina/        HTMLs: visualizacao (3D), novidades, como_funciona, bucha_polia_n20
  imagens/, step/
normal/          versão antiga (só referência)
```
A pasta `compacta/cad/maquina/saida/` é gerada e fica no `.gitignore`.

## Regerar tudo (de `compacta/cad/maquina/`, nesta ordem)
```
python checagem.py            # interferência SAT, parafusos, bola, varredura dos carros (--rapido pula a varredura)
python resistencia_m.py
python pecas.py               # CadQuery -> saida/stl, step
python teste_stl.py
python teste_paredes.py
python plano.py               # mesas por impressora
python malhas.py
python render_m.py
python render_mesas.py
python render_novo.py         # imagens R1.1
python render_r12.py          # imagens R1.2
python novidades_html.py
python impressao_html.py
python pagina_m.py
python explica_html.py
python publicar.py            # copia para imprimir/, pagina/, imagens/, step/; gera a bucha e os pacotes ALTERADAS
```
- `publicar.py` **apaga e recria** `imprimir/` e `pagina/`. Por isso, tudo o que fica lá precisa ser gerado pelo pipeline:
  - `bucha_n20.py`;
  - `alteradas.py` (função `pacote(rev, ...)`; para uma revisão nova, acrescentar um `pacote(...)` no `main`);
  - a lista de páginas extras dentro do `publicar.py`.
- **Patches grandes:** escrever o script de patch com Write e depois rodar. Um heredoc com `'''` no bash falha.

## Referencial e números-chave (layout.py / elevador/modelo.py)
- **Eixos:** X para a direita (paredes em ±210), Y para a tela (0 = frente, 200 = fundo), Z para cima (teto em 420).
- **Eixos A e B:**
  - Perfil 2020 × 400 na frente, em Y 8–28. MGN12 na face de trás. Patim MGN12H em Y 31–41.
  - zpA = 405, zpB = 81.
  - Correia GT2 6 aberta. Ramos em Y 15,63 e 28,37 (o ramo de trás tem os dentes para −Y). Plano da correia em zc = zp − 22.
  - NEMA17 em X −184, com o eixo para cima. Tensora no bloco direito em X 195, com rasgo de 6 mm.
- **Carros:**
  - Casa (home) em c = −146. Curso de jogo ±120.
  - cA vai de −146 a 166,3 (pega a bola em x_pega 192,3). cB vai de −146 a 120.
- **Carro A (ímã):**
  - Ímã em dA = 26 do centro do patim, y_bola 73,7.
  - Arruela M10 de aço colada embaixo do ímã, dentro de um copo impresso. A bola assenta 1,14 mm no furo.
  - Bola presa: zs = 360,66. Aproximação de 0,6 mm (gap_pega).
- **Bolso:** a bola fica em (193,3, 72,7, 358,92). Rampa inclina 1,5° para a parede da direita. Piso do bolso a partir de X 186 (`X_BOLSO`). Sensor TCRT5000 embaixo.
- **Carro B / anel:**
  - Anel com furo de 38. zb = 110,66.
  - O anel prende atrás com 4 M3x12 + porca.
  - Barreira IR pronta, de 5 mm, nos furos laterais, em Z zb − 14,5.
- **Fixador de correia (R1.1):**
  - Alumínio comprado, 40 × 9 × 5, com a face 40 × 9 dentada. Fica em pé, com os dentes direto na face dentada da correia.
  - As costas lisas da correia encostam na parede da presilha.
  - Um M3x16 entra de frente pelo furo do meio. A porca M3 fica presa numa fenda da presilha (entra por baixo).
  - Aperta com a tensora solta.
- **Fins de curso dos eixos:** KW10 no braço do bloco esquerdo, em X −174, apertado pela face esquerda da presilha na casa.
- **Elevador:**
  - Cabine em trilhos em T impressos. N20 com polia GT2 20T furo 5 + bucha impressa (furo redondo de 3,2 mm, rasgo para o parafuso).
  - KW10 embaixo e em cima.
  - zc_min = 18,82, zc_topo = 354,21 (entrega na rampa).
  - **zc_max = zc_topo + 0,5** (onde a cabine para). **zc_max_guia = zc_topo + 3**: usado só para desenhar a guia de cima e o rebaixo do fim de curso, que não mudaram.
  - O C direito da cabine fica 2,5 mm mais alto (`batente_fdc`) para apertar o KW10 de cima mais cedo.
  - Degrau da cabine para a rampa: 1 mm.

## Revisões
- **R1 (06/11):** máquina completa validada e impressa por mesas.
- **R1.1:**
  - fixador de correia de alumínio (primeiro deitado, o que estava errado; corrigido para em pé);
  - fins de curso nos eixos;
  - arruela + copo no ímã (eletroímã mais forte só depois);
  - barreira IR pronta.
  - Peças: Carro A, Carro B, Anel, Bloco esquerdo ×2. Pasta `ALTERADAS_R1.1`.
- **R1.2 (elevador, 08/11), a partir do que o usuário viu montando:**
  - Cabine: para na altura da rampa (o degrau era de 3,5 mm).
  - Rampa: bolso 3 mm mais largo (a bola estava no limite de cair).
  - Suporte do motor: reforçado (torcia ao apertar). Faixa de 10 mm na frente, travessa, nervuras de 12 mm, abraço com paredes de 3 mm, orelha com braço + 2 almas e **2** parafusos de madeira.
  - Bucha: furo redondo.
  - Peças: Cabine, Rampa, Suporte do motor, 4 buchas. Pasta `ALTERADAS_R1.2`, uma mesa da impressora A, ~6 h, camada de 0,16 mm.

## Estado das checagens (última rodada)
- 0 interferências; 129 de 129 parafusos ok; varredura dos carros ok.
- Bola ok: bolso, pega, levando, queda, anel, bandeja, fila.
- Resistência ok; 29 de 29 STLs ok.

## Páginas publicadas (artifacts, privados)
- Visualizador 3D (abre com "O que mudou" destacado e com botões de câmera): https://claude.ai/artifact/9DcfSq6gELSduMib1UJPYN
  - Publicar com `url` e o arquivo `compacta/pagina/PICBOX_compacta_visualizacao.html`.
- Novidades R1.2 + R1.1: https://claude.ai/artifact/5rbkAGhWgXMCw13sq35bWj (arquivo `compacta/pagina/PICBOX_novidades_R1.1.html`).
- Como funciona (animado): https://claude.ai/artifact/PRzhGNZ41kZTQf6w8VnnWW
- Ficha de impressão: https://claude.ai/artifact/NjVMRuLSQzLVFdekHecZbo **(desatualizada: ainda é a R1)**

## Em aberto / não testado nas peças reais
- Encaixe da bucha no eixo e na polia (medidas de catálogo).
- Degrau de 1 mm da cabine para a rampa: se sobrar, dobrar a alavanca do KW10 de cima.
- Aperto do fixador de alumínio na correia.
- Medidas de compradas que não foram medidas: furos do KW10, orelhas do SG90, rosca do P20/15, esteira 7 × 7, TCRT5000.
- A ficha de impressão publicada ainda não foi atualizada para R1.1/R1.2.
- Firmware: fazer a casa dos eixos no mínimo de X, devagar. Elevador: PWM de 50% nos últimos 20 mm e corte em 1 s. Servo alimentado pelo buck de 5 V.
