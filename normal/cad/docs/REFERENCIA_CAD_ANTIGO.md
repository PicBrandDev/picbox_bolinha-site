# Especificação extraída do CAD antigo (JS/replicad) — Máquina A

Fonte: `cad/` (branch cad-pecas), `montagem/guia.json` (gerado pelo `cad/build.mjs`), `js/params.js`.
Objetivo: só a ESPECIFICAÇÃO funcional das 46 peças `tipo:'impresso'`; a forma atual será descartada.
Legenda de origem de cota: **[P]** = PROJ (cad/lib/projeto.mjs ← js/params.js), **[L]** = literal no código (CENA),
**[C]** = catálogo (cad/pecas/comprados.mjs, eletronicos.mjs, fixadores.mjs), **[D]** = derivada de outras cotas.
"(est.)" = estimativa minha.

---

## 0. Sistema de coordenadas, unidade, convenções

| item | valor |
|---|---|
| Unidade | **milímetro** (todas as cotas, STL, STEP) |
| CAD (`cad/lib/base.mjs`) | **Z-up**. X = direita do jogador, **Y = para o FUNDO** (frente da máquina = −Y), Z = altura |
| Origem da MÁQUINA | centro do piso do gabinete: x=0,y=0 no centro do quadrado 450×450 (externo), z=0 no chão |
| guia.json / GLB | **Y-up (three.js)**, +Z para o jogador. Matriz `m` 4×4 coluna-maior. Conversão: three(x,y,z) = CAD(x, z, −y) (`mat.mjs paraThree`) |
| Gabinete | 450×450×1700 externo, MDF 18 → interno 414 (paredes internas x=±207, y=±207). Piso z 0..18, teto 1682..1700 |
| Alturas-chave (CAD, z) | prat. fonte 162..180; prat. lógica 412..430; painel botão 1050..1100; divisória do campo 1082..1100; campo 1100..1550 (testeira 1550) |
| Eixo B (buraco) | referencial do eixo transladado **(0,0,1175)** — trilho B centrado em z=1175, patim/placa EM CIMA |
| Eixo A (bola) | mesmo conjunto **espelhado em z** e transladado **(0,0,1530)** — patim/placa EMBAIXO do trilho; peças impressas saem como STL `_A` (espelho real, não congruente) |
| Soltura, magazine | referencial "eixo A instalado" (já espelhado) transladado (0,0,1530) sem novo espelho |
| Boca | referencial do eixo B, +(0,0,1175) |
| Elevador, bandeja | já no referencial da máquina |
| Eletrônica | placa MDF local (face de cima z=0) transladada (0,20,436) |
| Referencial local do EIXO | x ao longo do trilho, x=0 meio do trilho; y=0 centro do trilho; z=0 centro da altura do trilho (trilho z −4..+4, base em −4); perfil 2020 centrado em z=−14; topo do patim z=9; placa do carro z 9..14 |
| Plano de jogo | y = **−57** (centro da bola e do furo da boca, 57 mm à frente do eixo dos trilhos) [L] |
| Bola na soltura | centro (0,−57,**1470**) = 1530 − 60 [L "recuoSup"] |
| Plano da boca | z = **1220** = 1175 + 45 [L "recuoInf"]; queda = 1470−1220 = **250** (= geo.h, mas por coincidência de literais, ver §3a) |
| Curso | ±140 (A.stroke=280 [P]); FC: toca em 141, clica em 143, fundo 144,2 [D de SW] |
| Folgas de impressão (`FOLGA`) | M3 furo 3,4; cabeça M3 Ø6,0×3,2; porca M3 5,8 entre faces ×2,6; M5 5,4; cab. M5 Ø9×5,2; porca M5 8,2×4,2; M2 2,3; madeira Ø4,0, cab. escareada Ø7,6 |
| Material | PETG em todas as impressas (laranja = fixa, azul = móvel) |
| Mesa considerada no build | 260×260×300 (Creality) [L em build.mjs]. Todas as STL atuais cabem também em 220×220 (maior: bj_guia 213,4 mm) |

Contagem por máquina (§1): contei as instâncias do módulo **`maquina`** do guia.json (ele junta eixo B + eixo A
espelhado uma vez cada, boca, soltura, magazine, elevador, bandeja e eletrônica, descartando instâncias
`contexto`/`oculta`). Ignorei os módulos `func_*`, `ligacoes`, `alt_pistao` (didáticos, `didatico:true`) e os
módulos individuais (eixo, boca, ...), que só repetem peças para visualização. O módulo `eixo` mostra 1 eixo;
a máquina usa 2 (B normal + A `_A`). Total impresso ativo por máquina = **94** peças (confere com a soma das
instâncias de `maquina`), + 3 gabaritos (ferramenta), + 4 da alternativa pistão (inativa).

---

## 1. Quantidades por módulo

| módulo | id | qtd/máq | obs. |
|---|---|---|---|
| eixo | eixo_placa_carro | 2 | 1 B + 1 `_A` |
| eixo | eixo_garra | 2 | 1 B + 1 `_A` |
| eixo | eixo_presilha | 4 | 2 B + 2 `_A` |
| eixo | eixo_bloco_motor | 2 | 1 B + 1 `_A` |
| eixo | eixo_bloco_tensor | 1 | só B |
| eixo | eixo_bloco_tensor_semfc | 1 | só A (`_A`) |
| eixo | eixo_deslizador | 2 | 1 B + 1 `_A` |
| eixo (ferramenta) | eixo_gabarito | 3 | não fica na máquina |
| boca | boca_alvo | 1 | |
| soltura | soltura_berco | 1 | |
| soltura | soltura_batente | 1 | |
| bandeja | bj_calco_0..3 | 4 (1 de cada) | alturas diferentes |
| bandeja | bj_borda_f1, f2, t1, t2, bj_guia, bj_borda_e | 6 (1 de cada) | |
| bandeja | bj_calha_retorno | 1 | |
| magazine | mag_u_dir_f/_t, mag_u_esq_f/_t | 4 (1 de cada) | |
| magazine | mag_saida, mag_balancim, mag_carga, mag_comporta, mag_entrada, mag_sensor_nivel | 6 (1 de cada) | |
| magazine | mag_presilha (sela) | 6 | |
| magazine | mag_espacador | 4 | |
| elevador | elev_suporte_nema, elev_polia_motora, elev_polia_livre, elev_capa, elev_concha, elev_calha_entrega | 6 (1 de cada) | |
| elevador | elev_espacador | 2 | |
| elevador | elev_cacamba | 12 | |
| eletronica | elet_espacador | 26 | ESP32 4, 3 bases driver 12, buck 2, 2 MOSFET 4, IRF520 2, 2 LM393 2 |
| alt_pistao (INATIVA) | alt_camara 1, alt_copo 1, alt_lingueta 2 | 0 | só no módulo didático `alt_pistao`, fora de `maquina` |

Subtotais ativos: eixo 14, soltura 2, boca 1, bandeja 11, magazine 20, elevador 20, eletrônica 26 = **94**.
Módulo `fimdecurso` (func_fc) não tem peça impressa própria (reusa bloco_motor/placa).

---

## 2. Fichas

Formato: **Função** / **Movimento-carga** / **Posição** (instância na máquina, CAD Z-up, mm; "local" = referencial
de onde a geometria foi desenhada; "ref" = ponto do local que vira a origem da peça) / **Envelope** (bbox local
CAD, de GLB; e da STL na posição de impressão) / **Interfaces** / **Fixação** / **Origem das cotas** / **Bola** / **Problemas**.

### 2.1 Eixo linear (cad/montagens/eixo.mjs) — solução principal

Comuns ao eixo: trilho MGN12 400 [C: W12, H8, passo 25, E 12,5, furos Ø3,5/Ø6×4,5]; patim MGN12H [C: 45,4×27×13
(base trilho→topo patim 13), 4×M3 em **20×20**, rosca 3,5 de prof.]; perfil 2020×400 V-slot (fenda 6,2) [C]; NEMA 17
17HS4401 [C/medir: 42,3, furação **31×31 M3**, ressalto **Ø22×2**, eixo Ø5×24]; polia GT2 20T furo 5 [C: Ø prim. 12,73,
flange Ø16, cubo Ø14×7, total 16]; polia tensora GT2 20T c/ rolamento furo 5 [C: Ø18×8,5]; correia GT2 6 mm,
790 mm. Cotas do eixo (`EX`) [L salvo indicado]: parede = min(geo.inner, geo.floor−36)/2 = **207** [P+L]; centro das
polias x=**±178**; plano da correia y=**23,5**; face do cubo da polia motora y=35; placa de ponta y **35,5..40,5**;
face interna do pé x=**±200**; perfil z=−14; trilho base z=−4; topo patim z=9; topo placa carro z=14; FC: placa em pé
centrada z=42, xLivre=141, xHome=143, xFim=144,2, batente a 29 do centro do patim, costas da placa FC x=181,5 [D de SW: placa
40×16, furos em x −16 e +2, pré-curso 2, sobrecurso 1,2, ponta alavanca 21,7, altura 11,5].

**eixo_placa_carro — Placa do carro** (2: B, A`_A`)
- Função: liga o patim MGN12H à carga (boca no B, berço no A) e à garra da correia; leva os 2 batentes que acionam os FC.
- Movimento: move com o carro, ±140 (jogo), até ±144,2 (referência). Massa de carro do simulador A 210 g / B 320 g [P].
- Posição: B (0,0,1184) local [0,0,9]; A (0,0,1521) espelhada (placa sob o trilho, z 1516..1521).
- Envelope: 58×63×13,2 (placa 50×63×5 com cantos R3, x −25..25, y −29..34, z 9..14; batentes até z 22,2). STL 58×63×13,2.
- Interfaces: patim — 4 furos Ø3,4 em 20×20 centrados em (0,0); carga — 2 furos Ø3,4 em x=±15, y=−17 com porca M3
  embutida por baixo (sext. 5,8, 2,8 de prof.); garra — 2 furos Ø3,4 em x=0, y=17,05 e 29,95 (=23,5±6,45);
  batentes x=±17..±29, y=±4, topo z=22,2 (= zFC − ponta + 1,9) — só tocam a ponta da alavanca do FC.
- Fixação: 4× DIN912 M3×8 no patim (rosca do patim só 3,5); 2× porca M3 cativas p/ carga (M3×10); 2× M3×12 da garra.
- Origem: 20×20 [C]; ±15/−17, batente 29, zBatente [L/D]; curso [P].
- Bola: não.
- Problemas: porca cativa por baixo e carga por cima: precisa montar porca antes do patim; batentes 12×8×8 em balanço sobre placa de 5 mm (ok). Peça A é espelho (não basta virar).

**eixo_garra — Garra da correia** (2)
- Função: bloco sob a traseira da placa que prende as 2 pontas da correia GT2 (canal aberto por baixo).
- Movimento: com o carro.
- Posição: B (0,23,5,1184); A (0,23,5,1521) espelhada. Local ref [0, 23,5, 9].
- Envelope: 28×19,5×7 (x ±14, y 14,5..34, z 2..9). Canal da correia y 20,3..26,7 (6,4 p/ correia 6), z 1..6,85.
- Interfaces: placa (2 furos-guia Ø2,8 em YG); presilhas (4 furos-guia Ø2,8 em x=±8, y=YG); correia no plano y=23,5,
  atrás do patim (patim vai até y=13,5).
- Fixação: 2× M3×12 de cima (rosqueiam no plástico); 4× M3×8 das presilhas por baixo (rosqueiam no plástico).
- Origem: yC 23,5 [L derivado de patim WR 27 [C]]; resto [L].
- Problemas: rosca direta em PETG com 6 parafusos; garra fina (z 2..9 = 7 mm) com canal de 5,85 → teto ~1,15 mm (est.) sobre o canal.

**eixo_presilha — Presilha dentada** (4)
- Função: aperta cada ponta da correia contra o teto do canal da garra; nervura dentada (passo 2) encaixa nos dentes.
- Posição: B (±8, 23,5, 1175) (uma girada 180° em z); A idem em 1530 espelhada.
- Envelope: 11×17×5,2. Base 11×17×2, nervura 11×5,8 com 5 dentes 1×0,8.
- Fixação: 2× M3×8 (furos Ø3,4 em YG) por baixo na garra.
- Problemas: peça minúscula, 100% infill; dentes de 1 mm.

**eixo_bloco_motor — Bloco de ponta do motor** (2)
- Função: pé parafusado na lateral do gabinete + placa do NEMA + abas que prendem o perfil + braço do FC.
- Carga: estática; reação da correia (tração ~estimada dezenas de N) e torque do motor.
- Posição: B (200,0,1175); A (200,0,1530) espelhado. Local ref [200,0,0].
- Envelope local: 54×54,5×98 (x 153..207, y −14..40,5, z −34..64). STL (deitado no pé) 98×54,5×54.
- Geometria/Interfaces: pé x 200..207 (7 mm contra a parede MDF em x=207), y −14..40,5, z −34..24; braço do FC até
  z=64 (x 184,5..207, y ±9); abas do perfil y −14..−10 e 10..14, x 180..200, z −24..−4, furo M5 Ø5,4 em x=190 ao longo
  de Y, centro z=−14; placa do motor x 153..200, y 35,5..40,5 (5 mm), z ±24; furo ressalto Ø22,6 em (178, –, 0); 4 furos
  Ø3,4 em 31×31 centrados em x=178,z=0; 2 mãos-francesas triangulares (8 mm) em z 16..24 e −24..−16; 2 pezinhos Ø7×3
  para a placa do FC e 2 furos-guia Ø2,5×11 em x=181,5, z=58 e 40.
- Fixação: 4× M3×8 (NEMA, pela frente da placa); 2× ISO7380 M5×10 + porca martelo M5 no perfil; 4× parafuso
  madeira 3,5×20 escareado (cabeça do lado de dentro, face x=200) em (y,z)=(−7,17),(22,18),(−7,−29),(22,−29);
  FC: 2× M3×12 rosqueando em Ø2,5.
- Origem: NEMA 31/Ø22 [C]; parede 207 [P+L]; xP 178, placa 35,5..40,5 (polia 16 com cubo p/ motor) [L/D de C]; resto [L].
- Problemas: acesso aos parafusos de madeira só por dentro, ao longo de X, com o perfil/trilho montado (chave longa, est.);
  fixação só por parafusos de madeira em MDF (sem tarugo/insert); peça A é espelho real.

**eixo_bloco_tensor — Bloco de ponta do tensor, com FC** (1, só B)
- Função: idem motor, mas a placa guia o deslizador da polia tensora (tensor trabalha NA FRENTE da placa).
- Posição: (−200,0,1175). Local ref [−200,0,0]. Envelope 54×54,5×98 (x −207..−153).
- Interfaces: rasgo para a ponta do M5 da polia: x −178±6,8, z ±2,8; 2 rasgos M3 (x −178±5,7, z=±10) com rebaixo de cabeça
  6,2×3,2 atrás (y 37,3..40,5); orelha do parafuso tensor x −165..−160,5, y 28,75..35,5, z −17..−8, furo M3 ao longo de X
  em (y 32,1, z −12,5), porca M3 entra por baixo (rasgo 2,6×5,8). Demais = bloco motor espelhado em x.
- Fixação: 2× M3×8 travas (porcas no deslizador), 1× M3×16 tensor + porca, perfil 2× M5×10 + martelo, 4× madeira 3,5×20, FC 2× M3×12.
- Problemas: **orelha de 4,5 mm com porca M3 de 2,6 → paredes de ~0,8 e 1,1 mm** (frágil, recebe toda a tração da correia).

**eixo_bloco_tensor_semfc — Bloco do tensor sem FC** (1, só eixo A, `_A`)
- Função: igual ao tensor, sem braço do FC (por ali passa a calha de carga do magazine).
- Posição: A (−200,0,1530) espelhado. Envelope 54×54,5×58 (z −34..24). Nada atrás de y=40,5 (magazine passa ali).

**eixo_deslizador — Deslizador do tensor** (2)
- Função: carro da polia tensora; corre na frente da placa do bloco tensor, empurrado pelo M3×16.
- Movimento: ajuste ±4 mm em x (TENS.curso) [L].
- Posição: B (−178, 28,75, 1175); A espelhado. Envelope 14×6,7×28 (x −185..−171, y 28,75..35,4, z ±14).
- Interfaces: furo M5 Ø5,4 em (−178, z 0) + porca M5 autotravante cativa (8,2 AF × 6,4) do lado da placa; 2 furos M3
  (z=±10) + porcas M3 cativas (5,8×2,8). Polia tensora no eixo M5 entre arruelas, centro y=27,75; ISO7380 M5×20.
- Problemas: chão de ~1,25 mm atrás da porca M5 (est.); peça de 6,7 mm de espessura com 3 porcas cativas.

**eixo_gabarito — Gabarito de centragem** (3, FERRAMENTA, fora da máquina)
- Função: abraça perfil (20,3) e trilho (12,2) para centrar o trilho no perfil ao apertar.
- Envelope 12×26×29. Encaixes: perfil 20,3 de largura, trilho 12,2.

### 2.2 Boca (cad/montagens/boca.mjs) — principal

**boca_alvo — Chapa-alvo + garganta** (1)
- Função: furo-alvo 78×60 com garganta onde passa o feixe IR (barreira de acerto); vai no carro B.
- Movimento: com o carro B, ±140 (jogo) / ±144,2.
- Posição: (0,−57,1205) (local B (0,−57,30)). Plano de cima da chapa z=1220.
- Envelope: 110×95×31 (chapa 110×89×4: x ±55, y −103..−14; aba até y=−8). STL 110×95×31.
- Interfaces: furo **78×60 [P abertura×profBoca]**, R8, centro y=−57; chapa 4 mm em z 41..45 (local B), borda de 13 mm em
  volta do furo (limite: com carro em 144 a chapa vai até x=199, pé em 200) [L]; garganta (parede 3) de z 14 a 41;
  aba z 14..18, x ±22, y −24..−8 com 2 furos Ø3,4 em (±15, −17) sobre as porcas da placa do carro; 2 reforços laterais;
  buchas Ø10 com furos Ø5,15 em x=±45, y=−57, z=30 (feixe ao longo de X, 15 mm abaixo da face; LED IR333C à esquerda,
  TIL78 à direita); anel em baixo-relevo 0,6 mm em volta do furo.
- Fixação: 2× M3×10 de cima nas porcas da placa do carro; LED/fototransistor com cola quente.
- Origem: 78/60 [P]; 45 (recuoInf), 13, 3, 4, zFeixe 30, zGarg 14 [L]; Ø5 LED [C].
- Bola: a bola cai pelo furo; acerto = centro dentro do furo (|Δ|≤L/2, sim.crit); feixe corta toda bola (raio 17,5 > desvio Y 12,5).
- Problemas: impressa com a chapa na mesa; aba precisa de suporte; aba 4 mm é o único apoio de uma chapa de 110×89 em
  balanço (momento por impacto de bola, est.); fios do LED/TIL78 no carro móvel sem guia de cabo.

### 2.3 Soltura (cad/montagens/soltura.mjs) — principal

Referencial: eixo A instalado (placa do carro em z −14..−9 local, ou seja z 1516..1521 na máquina).
SO [L]: bola (0,−57,−60); solenoide ySol=−2; meia-largura do berço 21; braço z −41; frente y −84.
Solenoide JF-0826B [C/medir]: carcaça 27×22×25, êmbolo Ø7,4, curso 10, furos M3 a 8,5 e 18,5 da face.

**soltura_berco — Berço de pinça** (1)
- Função: segura a bola pelo equador (êmbolo do solenoide atrás empurra a bola contra um V 90° fixo na frente);
  energizado o êmbolo recua e a bola cai reta, sem empurrão em X.
- Movimento: com o carro A ±140; solenoide 10 mm em Y.
- Posição: (0,−40,1490) (local (0,−40,−40)).
- Envelope: 42×76×58 (x ±21, y −84..−8, z −76..−14 local da máquina). STL 58×76×42 (imprime de lado).
- Interfaces: aba z −18..−14, y −29..−8 encosta sob a placa do carro, 2 furos Ø3,4 em (±15,−17) + passagens Ø6,5 da chave
  na mesa; mesa do solenoide z −47,5..−43,5 (topo do solenoide = −60+12,5), y −36..−8, com 2 rasgos M3 em y −10,5 e
  −20,5 (±2 mm de ajuste); braço por cima da bola z −41..−37 (topo da bola −42,5 → 1,5 de folga); perna da frente
  y −84..−72, z −72..−41 com **V 90°** (vértice em y = −57 − 17,5·√2 = −81,75); furo Ø3,4 do batente em (19,75,−57).
- Fixação: 2× M3×10 de baixo para cima nas porcas cativas da placa do carro; 2× M3×6 no solenoide; 1× M3×10 do batente.
- Origem: bolaD [P]; −57, −60, 21, folgas [L]; solenoide [C].
- Bola: contato no V (2 linhas no equador) + ponta do êmbolo; centro da bola sob o eixo do berço.
- Problemas: só 2×M3 seguram tudo pendurado; alavanca de ~60 mm até a bola; ajuste do solenoide por rasgo.

**soltura_batente — Batente do berço** (1)
- Função: parada da bola que chega rolando de −X (estação de carga); centra a bola em x=0.
- Posição: (19,75,−57,1480). Envelope 4×18×22 (face de contato em x = 17,75 = RB+0,25).
- Fixação: 1× M3×10 de cima (furo-guia Ø2,8, rosca no plástico). Bola: contato pontual.
- Problemas: lâmina de 4 mm com furo Ø2,8 → paredes ~0,6 mm (est.).

### 2.4 Bandeja (cad/montagens/bandeja.mjs) — principal

BJ [L]: placa (MDF 6, cortada, não impressa) de x −199..191,5, y −169,5..55,5; ponto alto (−199,−169,5) a **z=1150**
(1 mm sob o perfil B em 1151); caimentos **4,5° para +X** e **3° para +Y (trás)**; divisória em z=1100; saída
x 151..191,5 no fundo-direita. Superfície: z = 1150 − tan4,5·(x+199) − tan3·(y+169,5); cantos 1150 / 1119,3 / 1138,2 / 1107,5.

**bj_calco_0..3 — Calços** (4, todos diferentes)
- Função: apoiam a placa sobre a divisória e definem os dois caimentos (topo inclinado).
- Posição: (−179,−149,5,1100), (171,5,−149,5), (−179,35,5), (171,5,35,5) (centros 20 mm para dentro dos cantos).
- Envelope 30×30× **43,3 / 15,7 / 33,6 / 6,0** (nome diz 41,4/13,8/31,7/4,1 = altura no centro).
- Fixação: furo Ø4 central; 1 parafuso madeira na divisória + 1× 3,5×16 da placa (instanciado).
- Problemas: calço_3 com 6 mm e furo Ø4; acesso ao parafuso de baixo depois de montado.

**bj_borda_f1, f2, t1, t2, bj_guia, bj_borda_e — Bordas** (6)
- Função: paredes da bandeja (perfil L: parede 3×26 + aba 10×3 apoiada na placa). bj_guia (direita) conduz a bola até a
  saída; bj_borda_e tem rebaixo sob o eixo B (y −18..+45), onde o perfil B faz de parede.
- Posição: geometria já em coordenadas da máquina (instância identidade). Comprimentos ~196, 196, 175, 175, 212, 199.
- Envelope (já inclinado): f1/f2 197,3×13,9×41,9; t1/t2 176,5×15,1×39,8; guia 15×213,4×37,2; e 13,2×199,1×37,3.
- Fixação: furos Ø3,4 na aba a cada 80 mm (a partir de 20): ~3/3/2/2/3/3 = 16 (est.) M3×12 + porca sob a placa (não instanciados).
- Bola: paredes laterais (bola rola encostada na guia).
- Problemas: **STL exportada inclinada** (rot de impressão vazia, geometria já girada 4,5°/3°) → base não plana;
  **borda_e: rebaixo deixa película de 0,3 mm** em ~63 mm; saída da bandeja sem borda.

**bj_calha_retorno — Calha de retorno** (1)
- Função: liga a saída da bandeja à aba (bico) da concha do elevador.
- Posição: (172, 55,5, 1126,6). Envelope real 42,6×9,3×28,4 (nome diz 47×30×32): canal de 37,6 (2×18,8) com paredes
  2,5, comprimento 9,3 em Y (y 55,5→64,8), cai 3,4 mm; termina em z=1123,2−17,5.
- Fixação: nenhuma feature (texto: cola quente ou 1 parafuso).
- Bola: piso + paredes, inclinação ~20° (est., 3,4 em 9,3).

### 2.5 Magazine (cad/montagens/magazine.mjs) — principal

Referencial = eixo A instalado (+1530 em z). MG [L]: eixo dos tubos **y=65**, painel MDF y=104..110; tubos acrílico
**Ø40×36** [C]; canal impresso **Ø36,4** (DCAN); inclinação **4°** [L, "H: validar"]; curvas U com linha de centro
**R21** (pitch vertical 42 entre passes); saída/travessia raio 21,6, canto x=−163; canal aberto: meia-largura 18,5,
parede e piso 2,5, abas até 8,5 acima do centro da bola. Cotas resultantes (centro da bola, máquina): saída P3
x=−110 z=1485,6; curva dir. x=40 z=1517,1; curva esq. x=−162 z=1573,3; entrada P1 x=60 z=1609,8. Passes: P3 −110→40,
P2 40→−162, P1 −162→60. Sequência: elevador → entrada → P1 → U esq → P2 → U dir → P3 → saída/escapement → curva →
travessia para a frente (por baixo do bloco tensor A) → comporta → curva → 2 trilhos dentro do berço (carro A em x=−140).

**mag_u_dir_f / mag_u_dir_t / mag_u_esq_f / mag_u_esq_t — Curvas U (metades)** (4)
- Função: meia-toroide Ø36,4 que liga dois passes; bipartida no plano y=65 para imprimir.
- Posição: dir (40,65,1517,1); esq (−162,65,1573,3).
- Envelope por metade 57,2×22,2×86,4. Encaixes do tubo Ø41,6 × 15 (eixo inclinado ±4°), bloco com raio 4 nas arestas.
- Fixação: 4× M3×40 atravessando as metades + porca cativa (5,8×3) na metade de trás (não instanciados).
- Bola: canal Ø36,4 (folga 0,7 de raio); R21 na linha de centro.
- Problemas: encaixe do tubo Ø41,6 para tubo Ø40 (folga 0,8 de raio, fixa só por aperto das metades); sem fixação ao painel.

**mag_saida — Saída + escapement** (1)
- Função: recebe a ponta do P3 (meia-cana + abraçadeira), canal até a curva da travessia, rasgos dos dedos do
  escapement, suporte do SG90, pé no painel, aba de junção com a calha de carga.
- Posição: (−110,65,1485,6). Envelope 113,6×62×54,6.
- Interfaces: meia-cana Ø40,4 de 18 mm; 2 rasgos 4×6 p/ abraçadeira; rasgos dos dedos 12×6 em x=−158 e −121,5; chapa do
  servo (48×3) com janela 22,8×12,4 e 2 furos Ø1,8 a 27,8 [C SG90]; pé até o painel (y 85..104) sem furos;
  aba 24×4×10 com 2 furos Ø3,4 a ±7 de x=−184,6.
- Fixação: abraçadeira nylon (P3); 2× parafusos do SG90 (M2 autoatarraxante); 2× M3×10 + porca com mag_carga; pé no painel
  "2 parafusos de madeira" (sem furo no modelo).
- Bola: canal aberto, 4°.

**mag_balancim — Balancim do escapement** (1, móvel)
- Função: preso ao eixo do SG90; 2 dedos (x=−158 e −121,5) sobem alternadamente pelo piso: ±12° = 1 bola.
- Movimento: rotação ±12° em torno de Y (eixo do servo em x=−139,75). Posição (−139,7,65,1453,6).
- Envelope 45×5×26,4. Furo Ø4,9 para o eixo estriado do servo. Dedos 3×5.
- Problemas: encaixe direto na estria Ø4,8 sem horn/parafuso (vai patinar, est.); dedos de 3 mm.

**mag_carga — Calha de carga + comporta** (1)
- Função: travessia da bola para a frente (de y=43,4 a y=−35,4 em x=−184,6), curva, 2 trilhos que entram no berço;
  suporte do solenoide JF-0530B; orelha na lateral esquerda do gabinete.
- Posição: (−184,6,0,1476,5). Envelope 79×121×80,3.
- Interfaces: trilhos de carga em y = −67 e −47 (20 entre si), x −170..−128, topo em z = −60 − √(17,5²−10²) = −74,4 (local)
  → bola fica com centro em −60 (mesmo do berço); rasgo da comporta 40×3 em y=−25; suporte do solenoide (furos Ø3,4 a
  9 e 21 [C JF-0530]); orelha x −207..−205,0 (**só 2 mm de espessura**), y ±20, z 24 mm, com 2 furos Ø4 (madeira) na parede x=−207; aba de junção.
- Fixação: 2× madeira 3,5×16 na lateral; 2× M3×10+porca com a saída; 2× M3 no solenoide (não instanciados).
- Bola: canal aberto + 2 trilhos. Firmware: não soltar com carro A a < 112 mm à esquerda do centro.
- Problemas: maior peça complexa (≈4 h), trilhos em balanço precisam de suporte; a curva fica entre a parede (−207) e o berço (−161).

**mag_comporta — Lâmina da comporta** (1, móvel)
- Função: lâmina que fecha o canal (9,5 acima do piso); solenoide energizado puxa 10 mm e ela some no piso.
- Movimento: 10 mm em Z. Posição (−184,6,−25,1474,8). Envelope 36×7,2×24,5 (lâmina 36×2,4).
- Interface: furo Ø6,4 na ponta do êmbolo Ø6 [C]. Sem guia própria (só o rasgo de 3 mm do piso).

**mag_entrada — Entrada do magazine** (1)
- Função: encaixe da ponta direita do P1 + trecho de canal aberto onde apoia a calha de entrega do elevador.
- Posição: (60,65,1609,8), girada −4° em Y. Envelope 50×46×46. Encaixe Ø40,8×16; canal 35 mm.
- Fixação: nenhuma (só encaixe no tubo).

**mag_sensor_nivel — Abraçadeira do sensor de nível** (1)
- Função: abraça o P1 em x=20; LED IR na frente e TIL78 atrás atravessando o acrílico (magazine cheio).
- Posição: (20,65,1607), −4°. Envelope Ø52×14 (+ buchas Ø10 em y=±24, total 64). Furo Ø40,3; furos Ø5,15 ao longo de Y.
- Fixação: 1× M3 na fenda da abraçadeira (furo Ø3,4; porca não modelada).

**mag_presilha — Sela do tubo** (6)
- Função: apoia cada tubo no painel; tubo preso por abraçadeira nylon 3,6.
- Posições: (−60,65,1489,1), (10,65,1494) [P3]; (−110,65,1548,6), (−20,65,1542,3) [P2, +4°]; (−110,65,1597,9), (−30,65,1603,5) [P1].
- Envelope 16×39×44 (y 65..104). Berço Ø41,5; rasgo 4,4×5 da abraçadeira; 2 furos Ø4 (madeira) em z=±14.
- Fixação: 2× madeira no painel (não instanciados) + abraçadeira.

**mag_espacador — Espaçador do painel** (4)
- Função: afasta o painel MDF do magazine (y=104..110) da parede do fundo (y=207).
- Posições: (−190,110,1450), (−190,110,1610), (−20,110,1450), (−20,110,1610). Envelope 20×97×20.
- Fixação: furo Ø4 axial nas duas pontas (madeira 3,5 de cada lado).

### 2.6 Elevador (cad/montagens/elevador.mjs) — principal

EL [L]: plano da correia x=**172**; eixo das polias y=**148**; polia de baixo z=**1125**, de cima z=**1609** (C=484);
polias 44T Ø prim. 28,01; Ro=14,5; laterais MDF 6 (cortadas) em x 144..150 e 194..200, y 94..205, z 1059..1673;
largura interna 43,4; capa/concha raio interno 55, espessura 3; tampa acrílico em y=201,5; 12 caçambas a cada 88 mm;
correia GT2 10 mm fechada 1056 mm. Sobe pelo ramo de trás (y=162,5), desce pela frente (y=133,5).
NEMA 17 direto na polia de cima, flange em x=138.

**elev_suporte_nema — Suporte do NEMA 17** (1)
- Função: flange que prende o NEMA na lateral esquerda (por fora, x 138..144).
- Posição: geometria em coordenadas da máquina (instância identidade): x 138..144, y 121..175, z 1582..1636.
- Envelope 54×54×6. Furo Ø22,6 (ressalto); 4 Ø3,4 em 31×31 com cabeça rebaixada 6×3,2 do lado da lateral;
  4 Ø4 (madeira) em 45×45.
- Fixação: 4× M3×6 no motor (motor preso antes); 4× madeira 3,5×12 na lateral MDF.
- Origem: NEMA [C]; 6 mm = lateral 6 + eixo 24 → 11,5 mm dentro do cubo [D].
- Problemas: M3×6 com cabeça rebaixada 3,2 em 6 mm → ~3 mm de rosca no motor (est.); parafuso madeira 12 em MDF 6+6.

**elev_polia_motora — Polia GT2 44T motora** (1, gira)
- Função: polia de cima, no eixo do NEMA. Posição (169,148,1609), eixo ao longo de X.
- Envelope Ø27,5×24,5 (dentes 6 de largura + cubo Ø14×18,5). Furo Ø5,1; parafuso M3 radial no chato + porca cativa.
- Origem: 44T/28,01 [L], correia GT2 [C].
- Problemas: **dentes impressos** (camada 0,12), 6 mm de dente em correia de 10; parafuso em plástico. → comprar (§3d).

**elev_polia_livre — Polia GT2 44T livre** (1, gira)
- Posição (169,148,1125). Envelope Ø27,5×6. Rolamento 625ZZ prensado (furo Ø16,1×6,5). Eixo M5×60 nas laterais.
- Problemas: polia de 6 mm com rolamento de 5 → aro de ~5,7 mm radial (est.); idem dentes impressos.

**elev_espacador — Espaçador do eixo de baixo** (2)
- Posições (150,148,1125) e (174,5,148,1125). Envelope Ø10×19,4, furo Ø5,4. Centralizam a polia (tocam só o anel interno).

**elev_cacamba — Caçamba** (12, móvel)
- Função: copo que leva a bola na subida. Pitch 88 mm (44 dentes).
- Movimento: com a correia, laço de ~1059 mm; ~147 mm/s a 100 rpm [L].
- Posições: subida x=172, y=162,5, z 1165..1606 a cada 88,26; descida y=133,5 (girada 180° em X).
- Envelope 40×38×18 (largura interna 36, profundidade 36, base de 8 mm ao longo da correia).
- Fixação: 2× M2×8 rente às bordas da correia (x=±6,5), arruela M2 por dentro segura a borda, porca M2 cativa (4,3 AF). Sem furar a correia.
- Bola: fundo + laterais; bola Ø35 em canal de 36.

**elev_capa — Capa do topo** (1)
- Função: casca R55..58 de 0° a 135° em volta da polia de cima: segura a bola na curva; termina 45° depois do topo
  (ali a bola sai para a calha de entrega); aba que prende a ponta de cima da tampa de acrílico.
- Posição (172,148,1609). Envelope 43,4×99,5×70.
- Problemas: **orelhas de fixação com 0,01 mm de espessura e sem furo** (bug); ajuste do ponto de saída por lixa.

**elev_concha — Concha do fundo** (1)
- Função: casca de 200° a 360° em volta da polia de baixo + bico de entrada (frente) onde chega a calha de retorno; a bola
  espera no fundo e a caçamba a pega. Posição (172,148,1125). Envelope 43,4×141,6×70.
- Fixação: **nenhuma feature** (texto: "parafuse a concha").

**elev_calha_entrega — Calha de entrega** (1)
- Função: canal aberto do topo do elevador até a mag_entrada (4°): reta (172,113→87), curva R22, reta até x=95,3, y=65;
  centro da bola de z≈1618,9 a 1612,2. Ponta de recepção cortada em y≤94 (1,5 mm fora do volume das caçambas).
- Posição (172,80,1609). Envelope 98,2×50×34,8. Fixação: nenhuma feature.

### 2.7 Eletrônica (cad/montagens/eletronica.mjs) — principal

**elet_espacador — Espaçador de placa 8 mm** (26)
- Função: eleva cada módulo 8 mm sobre o MDF 6 (300×200) da prateleira de lógica (z placa = 436 na máquina).
- Envelope Ø7×8, furo Ø3,4 (parede 1,8). Fixação: M3×16 atravessa módulo+espaçador e morde no MDF (Ø2,5); no ESP32, M2×10.
- Furações (locais da placa): ESP32 47,4×23,8; base driver 35×31; LM2596 diagonal (±17,5, ±7,5); MOSFET lógico 2 furos a 11;
  IRF520 2 a 18; LM393 1 furo. Todas [C/medir].
- → comprar espaçador nylon/latão M3×8 (§3d).

### 2.8 Alternativa pistão (cad/montagens/funcionamento.mjs, módulo `alt_pistao`, `didatico:true`) — **INATIVA**

Não entra em `maquina`, nem na lista de compras. Mesmo canto do elevador (x=172, y=148). Coluna de 13 bolas em tubo
Ø40×36 (~520 mm), pistão linear 12 V (falta) empurra 37 mm por ciclo. O texto conclui que o elevador fica como principal.

| id | qtd (no módulo) | função | envelope | cotas |
|---|---|---|---|---|
| alt_camara | 1 | câmara: entrada lateral pela frente, furo Ø37, encaixe do tubo Ø40,4×12, janelas das linguetas | 60×60×90 | bola Ø35 em Ø37 |
| alt_copo | 1 | copo na haste do pistão, assento esférico R17,5 | Ø34×12 | |
| alt_lingueta | 2 | catraca de mão única (gira 35°) | 14×8×16 | sem eixo/pivô modelado |

---

## 3. Listas

### (a) Divergências código × js/params.js

| tema | params.js | CAD | comentário |
|---|---|---|---|
| Separação dos eixos | geo.sep = 355 | YB=1175, YA=1530 literais em maquina.mjs (dif. 355) | geo.sep NÃO é lido (PROJ não o exporta) |
| Queda | geo.h = 250 | 1530−60 (recuoSup, soltura SO.zb) − (1175+45) (recuoInf, BO.zb) = 250 | coincide por literais; PROJ.queda só é usado na animação didática. Mudar geo.h não move nada no CAD. Relação do params: sep = h + 60 + 45 |
| Largura interna | geo.inner = 415 | parede = min(415, 450−36)/2 = 207 → 414 | CAD usa o gabinete real (414); com 415 os pés entrariam 0,5 mm na parede |
| Altura do gabinete | geo.height = 1700 | H=1700 literal em gabinete.mjs | não lido |
| Curso B | B.stroke = 280 | usa só A.stroke para os dois eixos | se B mudar, CAD não acompanha |
| Encoder | enc.res = 20 p/mm (AS5600) | nenhum encoder montado; peça `as5600` existe no catálogo mas não é instanciada | FC mecânico faz referência + contagem de passos |
| Transmissão | tr.teeth=20, GT2 | polia 20T furo 5 nos eixos | consistente |
| Plano de jogo / boca | (não existe em params) | y=−57, boca 45 acima do trilho B, bola 60 abaixo do trilho A | literais (vêm do "modelo 3D" antigo) |
| Tubos do magazine | — | comprados.mjs corta 221/201/149 (571) mas o passo do guia manda 222/202/160 (584) | divergência interna |
| Mesa de impressão | — | build MESA 260×260×300; usuário fala em 220×220 | todas as STL atuais cabem em 220 |
| Inclinação do magazine | — | 4° (modelo antigo 6°) | marcado [H] validar |
| geo.L/geo.depth | 78 / 60 | furo da boca 78×60 | consistente; a escada reduz L 5%/rodada (lad.ap) mas o furo físico é fixo |

Como o código posiciona: o eixo é desenhado uma vez (local, trilho em z=0). B = translação z+1175 (patim em cima,
boca sobre a placa, chapa em z 1216..1220). A = espelho em z + translação z+1530 (patim embaixo, placa 1516..1521,
berço pendurado com a bola em 1470). Soltura/magazine são desenhados direto no referencial do A já espelhado, por isso
entram só com translação. Bandeja logo abaixo do B (ponto alto 1150 vs perfil B em 1151); elevador de 1125 a 1609;
entrada do magazine a 1612.

### (b) Itens `tipo:'falta'` no guia.json (5)

| id | o que é | onde |
|---|---|---|
| perfil2020_400 | perfil alumínio 20×20 V-slot série 20 × 400 (2) — viga do trilho | eixos A/B |
| fc_mecanico | módulo fim de curso de impressora 3D (microchave KW10 + alavanca, placa 40×16, 3 pinos) ×3 (2 no B, 1 no A dir.) — substitui TCST2103 ópticos da planilha | braço dos blocos de ponta |
| rol_625zz | rolamento 625ZZ (5×16×5) — polia livre do elevador | elevador |
| correia_elev | correia GT2 10 mm FECHADA 1056 mm (528 dentes) — substitui correia aberta + emenda | elevador |
| alt_atuador | atuador linear 12 V curso 50 (só alternativa inativa) | alt_pistao |

Também registrados como `falta` no código mas não usados na montagem atual (não aparecem no guia): acoplador 4×5,
eixo Ø5×70, eixo Ø5×40 (do elevador antigo com JGA25). Notas de compra fora do `falta`: polia GT2 20T furo 5 (a da
planilha é 6,35), MOSFET de nível lógico e LM2596 (eletrônica), 2º tubo acrílico.

### (c) Peças que a montagem real exige e NÃO existem

- **Fixação da coluna do elevador ao gabinete** (cantoneiras/suportes): as laterais MDF do elevador não têm nenhuma
  ligação ao gabinete (nota do gab_fundo cita "cantoneiras do elevador" inexistentes).
- **Features de fixação faltando** em peças existentes: orelhas da elev_capa (0,01 mm, sem furo), elev_concha (nada),
  elev_calha_entrega (nada), bj_calha_retorno (nada), mag_entrada (nada), pé da mag_saida (sem furos), curvas U sem
  fixação ao painel.
- **Gestão de cabos móveis**: carro A leva o solenoide (2 fios) e carro B leva LED IR + TIL78 (4 fios), ±140 mm —
  falta esteira porta-cabo / guia de cabo flexível e alívio de tensão. Também falta guia/canaleta dos cabos dos 3 NEMA,
  3 FC, servo, comporta, sensor de nível até o pedestal (há só furo Ø40 na divisória e vão de 57 mm nas prateleiras).
- **Presilhas da frente de policarbonato** (4, citadas em gab_frente) — não existem.
- **Suporte de PCB**: só espaçadores sobre MDF; não há tampa/proteção dos bornes 220 V da fonte nem caixa da eletrônica (est.).
- **Guia/proteção da correia dos eixos** e **batentes mecânicos rígidos** de fim de curso (só existe a microchave) — não existem.
- **Horn/cubo do servo** para o balancim (encaixe direto na estria).
- **Guia da lâmina da comporta** (só o rasgo do piso).
- **Suporte de encoder AS5600** se o encoder do simulador for mantido.
- **Borda/guia na saída da bandeja** e fechamento entre bandeja e concha (calha de 9 mm sem fixação).
- Tensor do elevador é só rasgo no MDF (sem peça de ajuste).
- Arquivo órfão `montagem/fabricar/elev_mancal_motor.stl/.step` (não está no guia — sobra do projeto antigo).

### (d) Peças impressas que deveriam ser compradas

| peça | motivo | sugestão |
|---|---|---|
| elev_polia_motora (GT2 44T) | dentes GT2 impressos (precisão de perfil, camada 0,12), só 6 mm de dente em correia de 10, parafuso-trava em plástico, desgaste contínuo | polia GT2 alumínio p/ correia 10 mm, furo 5 (ex. 40T/36T — muda C: entre-centros = (L − N·2)/2) |
| elev_polia_livre (GT2 44T + 625) | idem; rolamento prensado em PETG afrouxa | polia/idler GT2 10 mm com rolamento furo 5 (dentada, mesmo N) |
| elet_espacador (26×) | 26 impressões minúsculas com parede 1,8 | espaçador nylon/latão M3×8 (ou hex M3 F-F) |
| elev_espacador (2×) | trivial | bucha/espaçador Ø5 ou arruelas empilhadas |
| eixo_deslizador + orelha do tensor | porca em parede de 0,8 mm recebendo tração da correia | opcional: tensor GT2 comercial de alumínio, ou redesenhar |
| mag_presilha (6×) | opcional | abraçadeira/clip para tubo Ø40 (eletroduto) |
| mag_balancim (interface) | estria do SG90 em furo Ø4,9 | manter impresso, mas parafusado no horn do kit SG90 |

---

## 4. Problemas de impressão/montagem (resumo transversal)

1. bj_borda_* exportadas inclinadas (STL sem base plana); bj_borda_e com película de 0,3 mm no rebaixo.
2. Rótulos `dims` desatualizados: bj_calha_retorno (real 42,6×9,3×28,4), calços (altura real maior que o nome), soltura_berco/boca (STL maior).
3. Paredes finas: orelha da mag_carga na parede (2 mm, segura a calha inteira), orelha do tensor (0,8/1,1 mm ao redor da porca), soltura_batente (~0,6 mm), espaçadores elet (1,8), polia livre (aro ~5,7 com rolamento), teto do canal da garra (~1,15, est.).
4. Overhang/suporte: boca (aba), mag_carga (trilhos), caçamba (costas em ponte de 40 mm na orientação atual), bordas inclinadas.
5. Rosca direta em PETG: garra (6 parafusos), batente, braço do FC (Ø2,5), polia motora (porca cativa radial).
6. Acesso de chave: parafusos de madeira dos pés dos eixos só por dentro ao longo de X com perfil montado; porcas cativas da placa do carro precisam ser postas antes do patim; parafusos do berço por baixo através de Ø6,5 na mesa do solenoide.
7. Peças A espelhadas (6 ids com STL `_A`): placa, garra, presilha, bloco motor, bloco tensor sem FC, deslizador (+ gabarito) — a remodelagem deve decidir entre peças simétricas ou espelho explícito.
8. Todas as STL cabem em 220×220 (maior 213,4 mm, bj_guia; blocos 98 mm de altura deitados).
9. Verificação de interferência do build: 0 colisões em todos os módulos (guia.json `colisoes`).
