# Maquina A — CHANGELOG

## 2026-10-22 — P1 (eixos, boca, soltura)
- **A01 bloco do motor** (piloto): pe com 4x M4 + porca-garra fora da varredura da boca/berco; berco em U do perfil
  (M5 na aba da frente + M5 no piso: a aba de tras nao tem chave por causa do motor); furo de acesso da chave ao
  parafuso de baixo do motor; nervuras atras da placa; braco do FC em caixa com porcas embutidas. Eixo A = espelho.
- **A02 bloco do tensor** + **A04 deslizador**: tensor redesenhado. O deslizador corre numa prateleira abaixo do carro
  (lingua na canaleta) e e **puxado por um M4x40 que vem de fora da lateral do gabinete** (ajuste sem abrir a maquina;
  1 furo Ø4,5 na lateral esquerda por eixo). Nada passa de y=40,5 (magazine atras no eixo A). Mesma peca A/B espelhada;
  o B leva o braco do FC.
- **A05 placa do carro**: garra da correia integrada (o antigo A06 deixa de existir); placa +-32 para as porcas da
  carga ficarem fora do patim; a ponta da placa aciona o FC direto (sem batente). FC reposicionado: costas da placa em
  x=186,1, centro z=34 -> toque em 141,0 (clique 143, fundo 144,2 como na cena).
- **A07 presilha**: 4 por maquina, A e B iguais.
- **A09 boca**: abertura redonda Ø50 (usuario), garganta de 4 mm com costelas, aba Ø76 com cone de 50 graus por baixo,
  borda R1,5 (R3 aumentaria a abertura efetiva). Barreira IR 15 mm abaixo da face. Impressa em pe.
- **A10 berco + A11 portinholas + A36 garfo**: soltura nova (usuario: alcapao duplo simetrico). Duas portinholas em V
  de 120 graus, articuladas a +-25,5 mm, acopladas por setores de engrenagem m1,5 z34: abrem exatamente iguais. O
  solenoide puxa 9,5 mm uma alavanca de 9,5 mm = 60 graus. Entrada da bola pelo lado -X (calha de carga, carro em
  x=-140), batente no +X. 3x M3 na placa (o 4o furo cai na bochecha). O antigo A11 (batente) foi incorporado ao A10.
- Checagens: overhang medido por face B-rep (furos <=Ø5 aceitos sem gota), interferencia ignora contatos de projeto,
  folga em movimento com manifold3d `min_gap`, checagem propria de acionamento do FC, peca do carro x carro,
  acesso de chave respeitando a ordem de montagem.

## 2026-10-21 — Fases 0 e 1
- Ambiente, branch `cad-pecas`, coleta da pagina `/montagem` (94 arquivos, 14 modulos), `params.json`, inventario.

## 2026-10-22 — P2 sem elevador (magazine, calha de carga, bandeja)
- **Magazine Ø50:** tubo acrilico Ø50x44 de 230 mm ao longo de -x em y=70 (atras do eixo A), inclinacao de 3 graus
  em todo o caminho, ~10 bolas.
  - **A18 entrada:** canal Ø44 + funil de carga manual (depois, o elevador entrega ali).
  - **A19 suporte:** pela lateral direita, por BAIXO da entrada e do motor do eixo A.
  - **A15 saida:** encaixe do tubo + curva de 90 graus encostada na lateral esquerda; impressa em pe, com um pe varrido ate a sola.
- **A16 calha de carga:**
  - travessia em V de 120 graus em x=-184,5, que passa 1,9 mm abaixo do pe do bloco do tensor A;
  - escapamento com servo SG90 deitado contra a lateral + **A17 balancim** (+-15 graus; passo dos dedos 49,3 mm, calculado pela inclinacao dos dedos);
  - canto contra o batente da frente; trecho em V ao longo de +x;
  - trilhos-lingua que entram no furo do berco (A10: furo de entrada passou para R23).
  - Caminho da bola checado do funil ao berco, nas duas fases do escapamento.
- O carro A agora para em -141 do lado do tensor (sem FC desse lado); a carga e em -140.
- A02 do eixo A sem a aba do braco do FC (invadia a travessia).
- **Bandeja:**
  - MDF 6 + EVA 3 com 3,5 graus para +x e 3 graus para a frente, na frente de um **A13 rodape** em y=-20 (a bola de 38 nao passa sob o perfil B);
  - **A12 calcos** (6 alturas);
  - **A14 saida** no canto frente-direita (tubo rente ao EVA, sem degrau) ate o **A38 bolsao** atras da porta do pedestal.
  - Bola checada em toda a bandeja com a boca passando por cima.
