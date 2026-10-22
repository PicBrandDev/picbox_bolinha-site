# Máquina A — inventário de peças impressas (Fase 1)

Fontes: `reference/A/` (94 arquivos baixados de `/montagem`, 14 módulos com dump da cena), `params.json` (gerado de `js/params.js`, hash 401df891), ficha técnica `reference/A/spec_cad_antigo.md`.
Calibração: cena em **mm, Y-up**; máquina = 450 × 1700 × 468 (gabinete 450 + frente). CAD novo: Z-up, X = direita do jogador, Y = fundo, origem no centro do piso. Conversão: CAD (x, y, z) = three (x, −z, y).
Arquivos coletados: 43 STEP, **todos B-rep** (com superfícies cilíndricas), 51 STL (5 têm 2 corpos: eixo_gabarito, eixo_gabarito_A, mag_carga, mag_saida, soltura_berco). Por decisão sua, **servem só como referência de posição e interface**. A forma é refeita do zero.

Tempo e massa são estimados a partir do volume da referência × 1,3, em PETG com 4 perímetros, ~11 g/h e +12 min de preparo por placa. Depois de modelar, vou recalcular pelo slicer ou pelo volume real.
Origem das cotas: P = PARAMS · CN = CENA (posição/interface lida do código antigo) · CT = CATALOGO · E = ESTIMADO.

## Peças impressas (ativas)

| ID | Nome | Ref. coletada | Função | Qtd | Envelope ref. (mm) | Interfaces | Fixação | Origem | Prio | Tempo est. (total) | Risco |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A01 | Bloco de ponta — motor | eixo_bloco_motor(+_A) STEP/STL | pé na lateral do gabinete + placa do NEMA 17 + abas do perfil 2020 + braço do FC | 2 (B, A espelho) | 98×55×54 | parede x=±207; perfil 2020 (M5); NEMA 31×31/Ø22; FC mecânico; polia 20T alinhada à correia y=23,5 | 4×M3×8 motor, 2×M5×10+martelo, 4× na parede | P10 CN60 CT30 | P1 | 11,5 h | tração da correia; motor aquece (PETG?) |
| A02 | Bloco de ponta — tensor c/ FC | eixo_bloco_tensor | idem, com guia do deslizador do tensor | 1 (B) | 98×55×54 | idem A01 + deslizador | +M3×16 tensor | P10 CN60 CT30 | P1 | 6,0 h | porca do tensor com parede de 0,8 mm na ref. |
| A03 | Bloco de ponta — tensor s/ FC | eixo_bloco_tensor_semfc_A | idem, sem braço do FC (calha do magazine passa ali) | 1 (A) | 58×55×54 | idem A02; nada atrás de y=40,5 | idem | P10 CN60 CT30 | P1 | 4,5 h | idem |
| A04 | Deslizador do tensor | eixo_deslizador(+_A) | carro da polia tensora, ajuste ±4 mm | 2 | 14×28×7 | polia tensora M5; 2 travas M3 | porca M5 nylon, 2 porcas M3 | CN70 CT30 | P1 | 1,0 h | 3 porcas numa peça de 6,7 mm |
| A05 | Placa do carro | eixo_placa_carro(+_A) | liga patim MGN12H à carga (boca / berço) e à garra; batentes dos FC | 2 | 58×63×13 | patim 20×20 M3; carga 2×M3 em (±15,−17); garra; batentes FC | 4×M3×8 patim, 2 porcas M3 cativas | P10 CN50 CT40 | P1 | 4,8 h | — |
| A06 | Garra da correia | eixo_garra(+_A) | prende as 2 pontas da GT2 6 mm sob o carro | 2 | 28×20×7 | placa A05; correia y=23,5 | 2×M3×12 + 4×M3×8 (rosca no plástico na ref.) | CN70 CT30 | P1 | 1,2 h | rosca direta em PETG |
| A07 | Presilha dentada | eixo_presilha(+_A) | aperta a correia na garra | 4 | 11×17×5 | garra A06; dentes GT2 | 2×M3×8 | CN50 CT50 | P1 | 1,1 h | dentes de 1 mm |
| A08 | Gabarito do trilho (ferramenta) | eixo_gabarito | centra o MGN12 no perfil 2020 ao apertar | 1 (ref.: 3) | 12×26×29 | perfil 20,3 / trilho 12,2 | — | CT100 | P1 (antes de montar trilho) | 0,6 h | — |
| A09 | Boca do buraco | boca_alvo | chapa-alvo 78×60 + garganta com barreira IR | 1 | 110×95×31 | placa do carro B; furo **78×60 (P)**; LED IR333C/TIL78 Ø5 a 15 mm sob a face; plano z=1220 | 2×M3×10 nas porcas de A05 | P30 CN50 CT20 | P1 | 7,2 h | chapa em balanço; aba com suporte na ref. |
| A10 | Berço da bola (pinça) | soltura_berco | segura a bola no equador; solenoide JF-0826 recua e solta | 1 | 58×76×42 | placa do carro A; bola Ø35 (P) em (0,−57,1470); solenoide; V 90° | 2×M3×10, 2×M3×6, 1×M3 batente | P20 CN50 CT30 | P1 | 3,8 h | pendurado em 2×M3; 2 corpos na ref. |
| A11 | Batente do berço | soltura_batente | para e centra a bola que chega da carga | 1 | 22×18×4 | berço A10; bola | 1×M3×10 | P30 CN70 | P1 | 0,4 h | parede de 0,6 mm na ref. |
| A12 | Calços da bandeja (4 alturas) | bj_calco_0..3 | apoiam a placa MDF e dão os caimentos 4,5°/3° | 4 (diferentes) | 30×30×6..43 | divisória z=1100; placa MDF 6 | parafuso de madeira | CN100 | P2 | 7,7 h | — |
| A13 | Bordas da bandeja (6) | bj_borda_f1,f2,t1,t2,bj_guia,bj_borda_e | paredes da bandeja e guia até a saída | 6 (diferentes) | até 213 de comprimento | placa MDF; perfil B; saída x 151..191 | M3×12 + porca na placa (~16) | P10 CN90 | P2 | 18,9 h | STL da ref. saiu inclinado; película de 0,3 mm |
| A14 | Calha de retorno | bj_calha_retorno | saída da bandeja → bico da concha | 1 | 43×9×28 | A13; A21 | nenhuma na ref. → incluir | P20 CN80 | P2 | 0,6 h | sem fixação; degrau na junção |
| A15 | Curvas U do magazine (4 metades) | mag_u_dir_f/_t, mag_u_esq_f/_t | ligam os passes de tubo Ø40 (R21) | 4 | 57×86×22 | tubos acrílico Ø40×36; painel | 4×M3×40 + porca por curva | P20 CN50 CT30 | P2 | 23,4 h | sem fixação ao painel |
| A16 | Saída + escapement | mag_saida | ponta do P3, rasgos dos dedos, suporte SG90 | 1 | 114×62×55 | tubo P3; SG90; A17; A18; painel | abraçadeira, 2×M2 servo, 2×M3 c/ A18 | P20 CN50 CT30 | P2 | 5,2 h | 2 corpos na ref.; pé sem furo |
| A17 | Balancim do escapement | mag_balancim | libera 1 bola por ciclo (±12°) | 1 | 45×26×5 | eixo SG90 | ref.: só pressão na estria → usar horn | CN60 CT40 | P2 | 0,4 h | vai patinar sem horn |
| A18 | Calha de carga + comporta | mag_carga | travessia para a frente, curva, 2 trilhos até o berço; suporte JF-0530 | 1 | 79×121×80 | lateral x=−207; A16; berço A10 (carro em x=−140); solenoide | 2× madeira, 2×M3 c/ A16, 2×M3 solenoide | P20 CN50 CT30 | P2 | 5,5 h | orelha de 2 mm segura tudo; 2 corpos |
| A19 | Lâmina da comporta | mag_comporta | fecha o canal; solenoide puxa 10 mm | 1 | 36×24×7 | êmbolo Ø6; rasgo 3 mm | encaixe no êmbolo | CN60 CT40 | P2 | 0,5 h | sem guia |
| A20 | Entrada do magazine | mag_entrada | recebe o P1 e a calha de entrega | 1 | 50×46×46 | tubo P1; A24 | nenhuma na ref. → incluir | CN80 CT20 | P2 | 3,3 h | sem fixação |
| A21 | Abraçadeira do sensor de nível | mag_sensor_nivel | IR + TIL78 através do tubo (magazine cheio) | 1 | 58×64×14 | tubo P1 Ø40; LED Ø5 | 1×M3 | CN50 CT50 | P2 | 2,0 h | — |
| A22 | Sela do tubo | mag_presilha | apoia os tubos no painel | 6 | 16×44×39 | tubo Ø40; painel MDF | 2× madeira + abraçadeira | CN60 CT40 | P2 | 11,4 h | — |
| A23 | Espaçador do painel do magazine | mag_espacador | afasta o painel MDF da parede do fundo (97 mm) | 4 | 20×20×97 | painel; fundo | madeira nas 2 pontas | CN100 | P3 | 13,7 h | candidato a comprado (tubo + M4) |
| A24 | Calha de entrega | elev_calha_entrega | topo do elevador → entrada do magazine (4°) | 1 | 98×50×35 | A27; A20 | nenhuma na ref. → incluir | CN80 | P2 | 3,6 h | sem fixação |
| A25 | Suporte do NEMA 17 do elevador | elev_suporte_nema | flange do motor na lateral MDF | 1 | 54×54×6 | NEMA 31×31/Ø22; lateral MDF 6 | 4×M3×6, 4× madeira | CT60 CN40 | P2 | 2,1 h | pouca rosca no motor |
| A26 | Caçamba | elev_cacamba | leva a bola na subida | 12 | 40×38×18 | correia GT2 10 mm; bola | 2×M2×8 + arruela + porca | P20 CN50 CT30 | P2 | 18,7 h | ponte de 40 mm na orientação da ref. |
| A27 | Capa do topo | elev_capa | guia a bola na curva de cima | 1 | 70×100×43 | polia de cima; tampa acrílico; A24 | ref.: orelhas de 0,01 mm, sem furo → refazer | CN80 P20 | P2 | 3,0 h | bug de fixação |
| A28 | Concha do fundo | elev_concha | recebe a bola da bandeja; caçamba pega | 1 | 70×142×43 | polia de baixo; A14 | nenhuma na ref. → incluir | CN80 P20 | P2 | 4,0 h | sem fixação |
| **Soma** | | | | **69 peças** | | | | | | **≈ 166 h** (1 impressora) | |

Reduzi de 94 para 69 peças porque retirei os 26 espaçadores da eletrônica e os 2 do elevador (passam a ser comprados) e contei só 1 gabarito.

## Fora da impressão (cena tem, mas não imprimir)

| Ref. | Motivo | Proposta |
|---|---|---|
| elev_polia_motora / elev_polia_livre (GT2 44T) | dente GT2 impresso, só 6 mm de dente para correia de 10, rolamento prensado em PETG, desgaste contínuo | comprar polia GT2 **40T** de alumínio para correia de 10 mm, furo 5, mais idler 40T com rolamento. Com a mesma correia fechada de 1056 mm, a distância entre centros vai de 484 para **488 mm** |
| elet_espacador (26) | peça trivial, parede de 1,8 mm | espaçador de nylon/latão M3×8 |
| elev_espacador (2) | trivial | bucha Ø5 ou arruelas |
| alt_camara, alt_copo, alt_lingueta | alternativa com pistão, inativa | fora |
| Polias GT2 20T, tensora, MGN12H, NEMA, solenoides, FC | já são compradas | — |

## Peças que faltam (a montagem real exige)

| ID | Peça | Prio | Obs. |
|---|---|---|---|
| A29 | Cantoneiras da coluna do elevador (laterais MDF → gabinete) | P2 | hoje a coluna não está presa a nada |
| A30 | Suportes de esteira porta-cabo, nas 2 pontas × 2 carros | P2 | carro A leva solenoide, carro B leva IR + TIL78; esteira comprada |
| A31 | Horn adaptador do balancim (ou balancim parafusado no horn do kit SG90) | P2 | entra no A17 |
| A32 | Guia da lâmina da comporta | P2 | entra no A18/A19 |
| A33 | Presilhas da frente de policarbonato | P3 | 4 peças, citadas no gabinete |
| A34 | Guias/canaletas de cabo até o pedestal + tampa dos bornes da fonte | P3 | |
| A35 | Batentes rígidos de fim de curso | P3 | hoje só há a microchave |
| — | Furos e orelhas de fixação | — | entram como feature em A14, A16, A20, A24, A27, A28 (não são peças novas) |

## Divergências cena × params (o params vence; detalhes em PENDENCIAS.md)
- `geo.sep` = 355 não é lido. As alturas dos eixos (1175 e 1530) são literais. No CAD novo elas saem de `geo.h` + recuos, com uma checagem de que a diferença é 355.
- `geo.inner` = 415, mas o gabinete real tem 414 (MDF 18). O CAD novo usa 450 − 2×18 = 414 e marca 415 como divergência.
- `B.stroke` não é lido (os dois eixos usam `A.stroke`). O CAD novo lê cada um.
- Tubos do magazine: 221/201/149 no catálogo contra 222/202/160 no passo de montagem. Vão ser recalculados pela geometria nova.
- Arquivo órfão `elev_mancal_motor` em `montagem/fabricar` (não está no guia).

## Fila de impressão proposta (3 impressoras)

Critério: P1 primeiro; dentro da mesma prioridade, a mais longa antes. Peças pequenas iguais saem juntas numa placa só. A **mesa 260** recebe só o que não cabe nas de 220. Hoje tudo cabe em 220, porque a maior peça (bj_guia) mede 213 mm.

| Ordem | Impressora 260 | Impressora 220 #1 | Impressora 220 #2 |
|---|---|---|---|
| 1 | **A01 bloco motor B (piloto)** | A09 boca | A10 berço + A11 batente |
| 2 | A01 bloco motor A | A02 tensor c/ FC | A03 tensor s/ FC |
| 3 | A05 placa ×2 + A06 garra ×2 | A04 deslizador ×2 + A07 presilha ×4 + A08 gabarito | — |
| 4+ | A15 curvas U (4 metades) | A26 caçambas (12, em 2–3 placas) | bandeja A12–A14 |
| … | A18, A16, A20, A24 | A27, A28, A25 | A22 selas, A21, A17, A19, A23 |

**Horas:** P1 ≈ 42 h e P2/P3 ≈ 124 h, total **≈ 166 h** numa impressora só. Com as 3 em paralelo dá **≈ 55–60 h de relógio**. Como você disse que não há limite de horas, nada foi cortado.

## Atualizacao 2026-10-22 (P1 modelada) — mudancas de ID
- A03 (tensor sem FC) virou a variante A do A02. A06 (garra) foi integrada ao A05.
- A11 deixou de ser o batente (incorporado ao A10) e passou a ser o par de portinholas do alcapao.
- A36 (novo): garfo do embolo do solenoide.
- A08 (gabarito) feito: 2 por montagem, ferramenta.
- Estado atual, tempos e massas: ver VERIFICACAO.md e FILA_IMPRESSAO.md.

## Atualizacao 2026-10-22 (P2 sem elevador)
- A12 calcos (6), A13 rodape (2), A14 saida da bandeja, A38 bolsao (novo).
- A15 saida do magazine, A16 calha de carga, A17 balancim, A18 entrada, A19 suporte da entrada.
- Eliminados: A19 comporta e A32 guia da comporta (sem comporta; ver PENDENCIAS), A22 selas e A23 espacadores (o tubo fica so nas duas pontas), A20/A21 (entrada e sensor de nivel substituidos por A18; sensor de nivel adiado).
- Elevador (A24 a A29) adiado.
