# Contexto geral: PICBOX compacta (para continuar em outra sessão)

Atualizado em 23/11/2026 (R2.2). Branch `cad-pecas`. **Não fazer merge no `main`**: o site no Railway publica o `main`.

## O projeto
- Máquina A da PICBOX dentro de um gabinete de **440 × 430 × 230 mm livres** (R2), com a tela no fundo. O gabinete é de MDF/madeira e aceita parafuso de madeira.
- Bola de aço de 1" (Ø25,4 mm, 67 g).
- **Ciclo:**
  1. Fila (calha no fundo).
  2. Comporta com servo SG90.
  3. Elevador: cabine na torre impressa, N20 100 rpm, correia GT2 6 em laço, sensores de fenda embaixo e em cima.
  4. Rampa até o bolso.
  5. O carro A (trilho de cima) pega a bola com o eletroímã P20/15.
  6. O jogador aperta e a bola cai no anel do carro B (trilho de baixo), com barreira infravermelha.
  7. Bandeja com EVA 5 mm.
  8. Volta para a fila.
- **Eletrônica:** fora da caixa (fonte, ESP32, drivers). O firmware não está no repo.
- **Impressoras** (todas com 250 mm de altura):
  - **A**: 260 × 260, a melhor. Peças de precisão e as que ficam à vista vão nela.
  - **B e C**: Creality 220 × 220.
  - Plano alternativo: tudo numa SparkX i7 (260 × 260).
- **O usuário já tem:** 2 jogos de perfil 2020 + MGN12 + NEMA17 (com driver, polias e GT2 6), eletroímã P20/15, KW10, SG90, parafusos, filamento PETG, polia GT2 20T furo 5 de 16 mm. Ele quer sempre a opção mais barata e **não aceita peça comprada nova sem aprovar antes**.
- **Entrega da máquina:** semana de 23/11/2026.

## Como o usuário quer as respostas
- Português, extremamente conciso (ver `CLAUDE.md`).
- Entregar **só as peças alteradas**, numa mesa pronta, com LEIA-ME e o que comprar.
- Arquivos para enviar a outras pessoas: HTML de arquivo único, com tudo embutido.
- Imagens da máquina sem o gabinete (só o mecanismo e a bandeja).
- Commits na `cad-pecas`, com a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Não mexer em configurações de segurança do Windows (o MuJoCo foi bloqueado; as checagens usam numpy puro).
- CadQuery só roda pelo PowerShell.

## Estrutura
```
compacta/
  cad/maquina/   código da máquina inteira (o que importa)
  cad/elevador/  modelo antigo do elevador (importado por layout.py)
  imprimir/      mesas por impressora, SparkX_i7/, polia_de_cima/, pecas_avulsas/, LEIA-ME_R2.txt, zip
  pagina/        HTMLs: compacta_visualizacao, R2_visualizador_3D, elevador_3D, elevador_montagem, como_funciona, bucha
  imagens/, step/
normal/          versão antiga (só referência); normal/cad/ferramentas/visao_geral gera as imagens do LEIA-ME dela
```
A pasta `compacta/cad/maquina/saida/` é gerada e fica no `.gitignore`.

## Regerar tudo
De `compacta/cad/maquina/`, pelo PowerShell: `python regerar.py` (ou `python regerar.py <passo>` para continuar de um passo).
A ordem fica em `regerar.py`:
1. `checagem`, `resistencia_m`, `pecas`, `teste_stl`
2. `plano`, `plano_unica`, `malhas`
3. renders: `render_m`, `render_polias`, `render_sensores`, `render_elevador`, `render_mesas`
4. `impressao_html`, `explica_html`, `pagina_m`
5. `publicar`

- `publicar.py` **apaga e recria** `imprimir/`, `pagina/`, `imagens/` e `step/`. Por isso, tudo o que fica lá precisa ser gerado dentro dele:
  - `bucha_n20`, `polia_cima`, `impressao_unica`, `alteradas` (LEIA-ME_R2 + zip);
  - `visualizador`, `elevador3d`, `elevador_montagem`.
- **Patches grandes:** escrever o script de patch com Write e depois rodar. Um heredoc com `'''` no bash falha.

## Referencial e números-chave (layout.py / elevador2.py)
- **Eixos:** X para a direita (paredes em ±220), Y para a tela (tela em Y 230), Z para cima (teto em 430).
- **Eixos A e B:**
  - Perfil 2020 × 400, MGN12 na face de trás.
  - zpA = 410, zpB = 81.
  - Correia GT2 6 aberta. NEMA17 no bloco esquerdo, tensora no bloco direito (rasgo de 6 mm).
- **Carros:** casa em c = −146. cA de −146 a 165,8 (pega em x_pega 191,8); cB de −146 a 120.
- **Carro A (ímã):** dA = 26; arruela M10 de aço colada no ímã, dentro de um copo. Bola presa em zs = 366,16.
- **Bolso:** bola em (193,3, 72,7, 364,42).
- **Carro B / anel:** zb = 116,16. Barreira IR pronta, de 5 mm.
- **Fixador de correia:** alumínio comprado 40 × 9 × 5, dentado, em pé, com M3 e porca presa. O mesmo nos 2 carros e na cabine.
- **Fins de curso dos eixos:** KW10 da casa no bloco esquerdo e KW10 de segurança no bloco direito.
- **Elevador (R2.2):**
  - Torre em 2 peças: de baixo (Z 0–210) e de cima (Z 210–429, impressa de cabeça para baixo). Encaixam por 3 pinos e 4 M3x8.
  - Cabine em trilhos em T, com 1 mm de folga por lado. zc_min = 18,12; zc_max = zc_topo = 360,07; curso de 342 mm.
  - Eixo das polias em X 191. Polia de baixo em Z 10,5 (M5x30 em balanço, rasgo de 6 mm); polia de cima em Z 419.
  - **Polia de cima:** a polia de 16 mm num M5x45. Ordem (Y, da frente para trás): N20 | adaptador impresso (o M5 rosqueia nele) | polia (cubo para o motor) | espaçador 6,8 | parede | rolamento 625ZZ colado | arruela | cabeça do M5.
    - Na torre de cima já impressa: cortar a tira do teto Y 182–186,5 (4,5 mm, na largura da janela).
    - Detalhes em `polia_cima.py` e `imprimir/polia_de_cima/LEIA.txt`.
  - Sensores de fenda sem placa (tipo ITR9608) embaixo e em cima; a bandeira é um M2x25 rosqueado na cabine.

## Revisões
- **R1 (06/11):** máquina completa validada e impressa por mesas.
- **R1.1:** fixador de correia de alumínio, fins de curso nos eixos, arruela + copo no ímã, barreira IR pronta.
- **R1.2 (08/11):** cabine na altura da rampa, bolso mais largo, suporte do motor reforçado, bucha de furo redondo.
- **R2 (10/11):**
  - Gabinete de 440 × 430 × 230.
  - Peças juntadas: de 29 para 19 arquivos.
  - Elevador virou a torre em 2 peças, com sensores de fenda; correia presa na cabine com o fixador de alumínio.
  - Folgas maiores em tudo.
  - Detalhes em `imprimir/LEIA-ME_R2.txt`.
- **R2.1 (11/11):** polia de cima num parafuso M5x45, sem barra nem acoplamento comprado.
- **R2.2 (12/11):** polia de 16 mm (a que o usuário tem) com 1 rolamento só, adaptador N20-M5 reforçado impresso, e o corte da tira do teto na torre já impressa.
- **23/11:**
  - Imagem do elevador com nomes (`render_elevador.py`).
  - Elevador em 3D (`elevador3d.py`).
  - Montagem do elevador em 15 passos (`elevador_montagem.py`).
  - `regerar.py`.

## Estado das checagens (última rodada, 23/11)
Tudo ok:
- **Modelo:** 0 interferências (59 previstas); 128 de 128 parafusos; envelope dentro do gabinete.
- **Bola:** ok no bolso, na pega, levando, na queda (98 trajetórias), no anel, na bandeja e na fila.
- **Movimento:** varredura dos carros ok.
- **Polia de cima:** folga radial mínima de 0,3 mm (espaçador) e 0,4 mm (cubo).
- **Correia da cabine:** folga mínima de 2,81 mm.
- **Peças e impressão:** resistência ok (30 itens); STL: 18 STEPs, sem interseções, bola ok, 19 de 19 na mesa.

## Páginas publicadas (artifacts, privados)
Para atualizar, publicar o arquivo com o `url`:

| Página | Link | Arquivo |
|---|---|---|
| Montagem do elevador (15 passos) | https://claude.ai/artifact/CsDE6jch9xUdH1RAfmgCnn | `compacta/pagina/PICBOX_elevador_montagem.html` |
| Elevador 3D | https://claude.ai/artifact/B9c6qFFYNEjg8RGT3rd6Dy | `compacta/pagina/PICBOX_elevador_3D.html` |
| Visualizador 3D R2 | https://claude.ai/artifact/6WSaWDxGRZqrg7WT6ASbN9 | `compacta/pagina/PICBOX_R2_visualizador_3D.html` |
| Máquina completa (3D + montagem + checagens) | https://claude.ai/artifact/9DcfSq6gELSduMib1UJPYN | `compacta/pagina/PICBOX_compacta_visualizacao.html` |
| Como funciona (animado) | https://claude.ai/artifact/PRzhGNZ41kZTQf6w8VnnWW | `compacta/pagina/PICBOX_como_funciona.html` |

## Em aberto / não testado nas peças reais
- **Polia de cima R2.2:**
  - a frente do eixo apoia no próprio N20;
  - o cubo tem 0,4 mm de folga no encaixe;
  - a rosca do M5 no PETG pode espanar (vem 1 adaptador de reserva).
- Na montagem 3D, o motor entra no berço pela frente (deduzido da geometria da torre: o berço só é aberto na frente). Conferir na peça real.
- Aperto do fixador de alumínio na correia da cabine.
- Medidas de compradas que não foram medidas: orelhas do SG90, rosca do P20/15, esteira 7 × 7, sensores de fenda.
- Firmware:
  - casa dos eixos no mínimo de X, devagar;
  - elevador com PWM de 50% nos últimos 20 mm e corte em 1 s;
  - servo alimentado pelo buck de 5 V.
