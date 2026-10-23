# Máquina A — pendências

## Decisões registradas (default seguido)
- Máquina B fora do escopo.
- Horas de impressão sem limite; 3 impressoras: 1× mesa 260×260 (altura assumida 300) e 2× 220×220 (altura **assumida 250**, ESTIMADO).
- PETG, 4 perímetros, 20% gyroid (estruturais 40%), camada 0,20, bico 0,4. Fixação padrão: porca sextavada embutida; M3 no mecanismo, M4 no gabinete.
- O CAD antigo (`cad/`, `montagem/fabricar`) serve só como referência de posição e interface. Toda a forma é nova.
- CAD novo fica em `cad_py/` (`cad/` já existe e pertence à simulação).

## Respondido pelo usuário (2026-10-21)
- **Bola: Ø38 mm, 60 g, bola mini de sinuca.** O params diz 35 (est). Fica valendo 38 como MEDIDO, num arquivo de medidas de bancada lido por cima do params.json; o `js/params.js` só muda na Fase 6.
- Polias do elevador: comprar. A correia GT2 10 mm (já comprada) vai para o elevador.
- **Comprar correia GT2 6 mm para os dois eixos** (≈ 790 mm cada, ou seja 2 m no mínimo).
- **Boca: abertura redonda de no máximo Ø50**, reforçada para a bola de 60 g (o params tem geo.L 78 × 60 retangular, que é divergência). A bola chega a ~2,2 m/s (147 mJ) na boca e a ~2,6 m/s (200 mJ) na bandeja quando erra.
- Berço de soltura: redesenho com atenção à aparência.
- Fluxo da bola 100% livre: a checagem 10 é obrigatória em todo o caminho.
- Impacto da bola de 38: o tubo acrílico Ø40×36 **não passa**. Caçamba (36), canais (36,4) e largura do elevador (43,4) precisam crescer. A folga sob a boca antiga cai para 11,5 mm em x=−140.

## Segunda rodada de respostas (2026-10-21)
- **Elevador adiado.** Todo o resto tem que funcionar sem ele: a bola é recolocada à mão no magazine. A saída da bandeja termina num bolsão de coleta acessível pela porta, deixando a interface pronta para o retorno automático. Opções em aberto: correia com pás (opção A) ou pistão de curso longo.
- Envelope fixo de 450×450×1700: nada passa para cima. O piso e a divisória de madeira podem ser furados para passar coisas para baixo.
- Tubo do magazine: default acrílico Ø50×44 (sem resposta).
- 8 a 10 bolas em circulação.
- Boca: abertura redonda Ø50. A barreira IR fica.
- Cabos móveis dos dois carros têm que estar no 3D: esteira porta-cabo atrás do eixo, fora da vista do jogador.
- Queda de 250 fixa. Bandeja com forro de EVA de 3 mm. Jogador vê só pela frente. Altura útil das impressoras de 220: 250 mm.
- Soltura: o usuário perguntou qual conceito é melhor. Recomendado: alçapão duplo simétrico (aguarda confirmação).

## Aguardando resposta (com default)
1. Polias do elevador compradas: GT2 40T para correia de 10 mm, entre-centros 488. Default: sim.
2. Espaçadores da eletrônica e do elevador comprados. Default: sim.
3. Peças do eixo A: peça simétrica única quando der, e espelho explícito só nos blocos de ponta. Default: sim.
4. Bola Ø35 está como `est` no params e define todos os canais. Default: 35,0, com tudo paramétrico.
5. Fixação no MDF: M4 passante com porca-garra (T-nut) no lugar do parafuso de madeira, nos blocos dos eixos e nos suportes. Default: sim para peças com carga (blocos de ponta, cantoneiras da coluna); parafuso de madeira para o resto.
6. Cabos móveis: esteira porta-cabo comprada, com suportes impressos. Default: sim.
7. Temperatura do NEMA: PETG se a superfície ficar abaixo de 60 °C (corrente TMC2209 ≤ 0,8 A RMS). Default: PETG nos blocos de ponta e no suporte do NEMA; medir em bancada e trocar por ASA se passar.
8. Peça piloto: A01, bloco de ponta do motor (eixo B). Default: sim.

## ESTIMADO / medir em bancada
- Diâmetro real da bola (`ball.d` = 35 est).
- Solenoides JF-0826B e JF-0530B: carcaça, furação e curso.
- Módulo FC mecânico: placa 40×16, posição dos furos e da alavanca.
- Temperatura do NEMA 17 em regime.
- Inclinação do magazine, 4° (marcada como "validar" no código antigo).
- Altura útil das impressoras 220.

## Divergências cena × params
- `geo.sep` = 355 não é lido; as alturas 1175/1530 são literais. A queda de 250 bate com `geo.h` por coincidência de literais.
- `geo.inner` = 415, mas o gabinete real tem 414.
- `B.stroke` não é usado; o CAD antigo usa `A.stroke` nos dois eixos.
- `geo.height` = 1700 é literal no gabinete antigo.
- Tubos do magazine: 221/201/149 (catálogo) contra 222/202/160 (passo de montagem).
- `enc.res` existe, mas não há encoder montado.

## Decisoes de modelagem da P1 (2026-10-22) — nao mudam interface com o que voce ja tem
- Tensor: M4x40 pela lateral esquerda do gabinete (furo Ø4,5 no MDF em y=34,6 / z=-7,9 do eixo; ver A02). Muda a furacao do MDF: marcar com o gabarito de furacao (pendente).
- Garra da correia integrada a placa do carro (A06 eliminado). Batentes do FC eliminados: a ponta da placa toca a alavanca.
- Fim de curso reposicionado (costas da placa x=186,1, centro z=34) para a alavanca tocar a ponta da placa.
- Boca: borda R1,5 (nao R3) para nao aumentar a abertura efetiva de 50 mm.
- Berco preso com 3 dos 4 furos da placa do carro.
- Espacadores da eletronica e do elevador: comprados (nylon/latao M3x8; bucha Ø5).

## A medir em bancada (afetam a P1)
- Solenoide JF-0826B: corpo (assumido 25 x 22 x 27), furos M3 a 8,5/18,5 da face do embolo, Ø do embolo 7,4 e como prender o garfo (assumido pino M2 transversal). Os furos do berco sao rasgos de +-1,5 mm para ajuste.
- Forca de retorno do solenoide: a bola tende a abrir as portinholas (~0,8 N no embolo). Se a mola do solenoide nao segurar, adicionar mola de tracao pequena entre o garfo e a bochecha (pendente de teste).
- Modulo de fim de curso: placa 40 x 16, furos a -16/+2 do centro, alavanca (posicao da ponta).
- Polia tensora GT2 20T com rolamento: Ø18 x 8,5 assumido.
- Bandeja antiga usada so para checar a folga da bola sob a boca (9,5 mm com EVA 3 mm); refazer junto com A12-A14 (P2).

## Interfaces que a P2 precisa respeitar
- Calha de carga do magazine -> berco: com o carro A em x=-140, a bola chega rolando em +X com centro em y=-57, z=1470; a calha termina em x=-165 (bochecha de entrada do berco em x=-140-24), apoiada em V de 120 graus (linhas de contato a y=-57+-9,5, z=1453,6).
- Magazine refeito para tubo Ø50x44 (bola 38), 8-10 bolas; o tubo Ø40x36 nao serve.
- Elevador: fuso em tubo acrilico Ø100 no canto frente-direita (A20-A25; ver CHANGELOG). Entrega no funil da A18.

## Decisoes da P2 (2026-10-22)
- (substituido) Sem elevador / bolsao: trocado pelo elevador de fuso em 2026-10-22.
- Magazine: tubo acrilico Ø50x44, comprimento 230 mm; o tubo Ø40x36 nao serve para a bola de 38.
- Comporta do magazine eliminada: o servo do escapamento so solta a bola com o carro A na carga (x=-140), e ela chega ao berco em menos de 1 s. Se quiser a comporta de volta (carga mais rapida), e uma peca a mais na A16.
- Carro A: limite do lado do tensor em -141 (firmware). A calha de carga fica a 1 mm da bochecha do berco nesse limite.
- Bandeja so na frente do eixo B. Bola que pular para tras do eixo B fica parada na divisoria (recolher pela porta de tras). Avaliar no teste se precisa de bandeja traseira.
- Inclinacao da bandeja: 3,5 graus em x e 3 graus em y. E o maximo: no canto alto, a bola fica 1,4 mm abaixo da placa do carro B.

## A testar/medir (P2)
- **Bola rolando no EVA de 3 mm com 3 a 3,5 graus:** se parar, trocar por EVA de 1 mm, feltro fino ou borracha. A inclinacao nao tem margem para subir.
- **SG90:** dimensoes (corpo 22,8x12,2x22,7, orelhas a 15,9 da base, furos a 27,8) e o braco que vem no kit (o rebaixo do A17 assume Ø7,4 + braco de 5,4x17).
- Tubo acrilico: diametro externo real (o encaixe tem 0,3 mm de folga por lado).
- Furacao nova no MDF:
  - laterais: 2+3 furos M4 (A15/A16, lateral esquerda) e 2 M4 (A19) na lateral direita, com porca-garra por fora; 2 furos Ø4,5 (A22, tampa do elevador) na lateral direita, parafuso de fora e porca por dentro;
  - divisoria: furo Ø101 centrado em (155,-155) + recorte ate o canto frente-direita; 3 furos escareados para a A20;
  - placa da bandeja e EVA: mesmo furo Ø101 + recorte ate o canto.
- Placa da bandeja (MDF) e EVA: recorte de 6 x 9 mm nos dois cantos de tras (x>=|199|, y>=-29), onde ficam os pes dos blocos dos eixos.

## Elevador de fuso (2026-10-22)
### Comprar
- Tubo acrilico Ø100 x 94 (parede 3), 573 mm. Furo de entrada e entalhe de saida cortados no tubo (gabarito: imprimir a A25 e marcar).
- Barra roscada M8 x 620 mm, 4 porcas M8, 2 arruelas M8 pequenas (Ø14), 2 rolamentos 608ZZ, acoplamento flexivel 5x8 (Ø19 x 25).
- Barra Ø8 de aluminio x 516 mm (trilho-guia), com 3 furos roscados M3 (z=1200, 1400, 1575); 3 M3x8 pela parede do tubo.
- NEMA 17 (17HS4401 ou igual) + driver; 2 pinos Ø3x16 por junta do fuso (4).
### A testar (prioridade)
1. **Topo (saida):** imprimir A21-3 + A22 + A25 e testar so o ultimo segmento num pedaco de tubo: a bola tem que passar por cima do trilho e rolar para fora no entalhe em toda volta. Se ficar girando sem sair, aumentar o caimento do filete (10 -> 15 graus) ou alargar o entalhe.
2. **Pe (entrada):** bola parada nas duas cunhas (63 e 207 graus) tem que cair para dentro; o filete nao pode prender a bola na borda do furo.
3. Rotacao: 30-60 rpm (1 bola a cada 1-2 s). Sentido horario visto de cima.
### Riscos conhecidos
- O caminho da bola dentro do tubo depende de atrito (bola segura pelo trilho e arrastada pelo filete): a checagem do CAD so garante que ha espaco livre.
- A20 e pesada (~230 g, 21 h): se faltar tempo de impressora, ela pode ser oca (pedir).

## A16 + A26 (2026-10-22)
- Furacao da lateral esquerda: A16 agora com 2 M4 (y=-27 e 33) e A26 com 2 M4 (y=-74 e -50), todos com porca-garra por fora.
- Montagem: A16 e A26 se alinham por 2 pinos Ø4x16 em y=-34. Com o carro A parado na carga (x=-140), conferir que as
  linguas da A26 entram no furo do berco sem encostar (folga de 1,3 mm no raio).
- A testar: a bola passa a curva R18,5 sem parar (desce ~7,7 graus). Se bater forte no batente do berco, reduzir a descida.
