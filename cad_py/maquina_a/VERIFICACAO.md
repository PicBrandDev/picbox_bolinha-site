# Maquina A — verificacao (Fase 4)

Gerado por `tools/relatorio.py` a partir de `out/relatorios/*.json`.
Checagem 11 (visual): avaliada abrindo as imagens em `out/png/` (ver CHANGELOG).

| Peca | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | Resultado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A01_bloco_motor | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A01_bloco_motor_A | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A02_bloco_tensor | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A02_bloco_tensor_A | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A04_deslizador | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A04_deslizador_A | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A05_placa_carro | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A05_placa_carro_A | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A07_presilha | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A07_presilha_A | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A09_boca | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A10_berco | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A11_portinhola | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A11_portinhola_f | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A36_garfo | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A08_gabarito | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A15_saida_magazine | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A16_escapamento | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A26_entrada_berco | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A17_balancim | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A18_entrada_magazine | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A19_suporte_entrada | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A12_calco | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A12_calco_1 | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A12_calco_2 | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A12_calco_3 | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A12_calco_4 | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A12_calco_5 | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A13_rodape | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A13_rodape_d | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A20_base_elevador | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A24_suporte_motor_elevador | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A21_fuso | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A21_fuso_2 | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A21_fuso_3 | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A22_tampa_elevador | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A25_saida_elevador | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |
| A23_calha_elevador | ok | ok | ok | ok | ok | ok | ok | ok | ok | ok | ver | ok | ok | APROVADA |

## Detalhes que importam

- **A01_bloco_motor**: menor folga em movimento 1.0 mm (A05.B x A01, carro em 144.2); parede p1 2.7 mm (min 1.6); overhang 16.5 mm2, ponte max 9.0 mm; Δ intencao 17.5 mm: pe mais largo em y (-28..58 contra -14..40,5) para os 4 parafusos M4 ficarem fora da varredura da boca/berco e da correia, e para apoiar as nervuras atras da placa do motor; placa do motor 2 mm mais baixa
- **A01_bloco_motor_A**: menor folga em movimento 1.0 mm (A05.A x A01, carro em 144.0); parede p1 2.7 mm (min 1.6); overhang 16.5 mm2, ponte max 9.0 mm; Δ intencao 17.5 mm: pe mais largo em y (-28..58 contra -14..40,5) para os 4 parafusos M4 ficarem fora da varredura da boca/berco e da correia, e para apoiar as nervuras atras da placa do motor; placa do motor 2 mm mais baixa
- **A02_bloco_tensor**: menor folga em movimento inf mm (B.patim x A02, carro em -144.2); parede p1 2.57 mm (min 1.6); overhang 16.5 mm2, ponte max 9.0 mm; Δ intencao 17.5 mm: pe mais largo (mesmo do A01); tensor redesenhado: deslizador corre numa prateleira abaixo do carro, sem a orelha de parede fina da referencia; nada passa de y=40,5
- **A02_bloco_tensor_A**: menor folga em movimento inf mm (A.patim x A02, carro em -141.0); parede p1 2.57 mm (min 1.6); overhang 16.5 mm2, ponte max 0.1 mm; Δ intencao 17.5 mm: pe mais largo (mesmo do A01); tensor redesenhado: deslizador corre numa prateleira abaixo do carro, sem a orelha de parede fina da referencia; nada passa de y=40,5
- **A04_deslizador**: menor folga em movimento 5.07 mm (A05.B x A04, carro em -144.2); parede p1 1.51 mm (min 1.6); overhang 1.2 mm2, ponte max 8.4 mm; Δ intencao 10.0 mm: deslizador novo: corre sobre a prateleira do A02 e e puxado por um M4 que vem de fora da lateral
- **A04_deslizador_A**: menor folga em movimento inf mm (A.patim x A04, carro em -141.0); parede p1 1.51 mm (min 1.6); overhang 1.2 mm2, ponte max 8.4 mm; Δ intencao 10.0 mm: deslizador novo: corre sobre a prateleira do A02 e e puxado por um M4 que vem de fora da lateral
- **A05_placa_carro**: menor folga em movimento 1.0 mm (A05.B x A01.B, carro em 144.2); FC tocado em B.fc+: 141.0, B.fc-: 141.0; parede p1 2.15 mm (min 1.6); overhang 0.0 mm2, ponte max 6.2 mm; Δ intencao 7.2 mm: placa mais larga (+-32) para as porcas da carga ficarem fora do patim e mais robusta para a boca com bola de 60 g; garra da correia integrada (antes A06); lingua de tras estreita para nao alcancar as polias
- **A05_placa_carro_A**: menor folga em movimento 1.0 mm (A05.A x A01.A, carro em 144.0); FC tocado em A.fc+: 141.0; parede p1 2.1 mm (min 1.6); overhang 0.0 mm2, ponte max 6.2 mm; Δ intencao 7.2 mm: placa mais larga (+-32) para as porcas da carga ficarem fora do patim e mais robusta para a boca com bola de 60 g; garra da correia integrada (antes A06); lingua de tras estreita para nao alcancar as polias
- **A07_presilha**: menor folga em movimento 1.0 mm (A05.B x A01.B, carro em 144.2); parede p1 0.8 mm (min 0.7); overhang 0.0 mm2, ponte max 0.0 mm; Δ intencao 17.5 mm: presilha mais longa (12) e larga
- **A07_presilha_A**: menor folga em movimento 1.0 mm (A05.A x A01.A, carro em 144.0); parede p1 0.8 mm (min 0.7); overhang 0.0 mm2, ponte max 0.0 mm; Δ intencao 17.5 mm: presilha mais longa (12) e larga
- **A09_boca**: menor folga em movimento 1.0 mm (A05.B x A01.B, carro em 144.2); bola: folga radial na queda 6.0 mm, bola rolando sob a garganta 9.5 mm; parede p1 2.79 mm (min 1.6); overhang 0.0 mm2, ponte max 2.0 mm; Δ intencao 17.0 mm: abertura redonda Ø50 (usuario) no lugar de 78x60; garganta e costelas para a bola de 60 g; borda redonda
- **A10_berco**: menor folga em movimento 1.0 mm (A05.A x A01.A, carro em 144.0); bola: entra rolando e cai com as portinholas abertas sem tocar (curso do pino 9.5 mm); parede p1 3.0 mm (min 1.6); overhang 0.0 mm2, ponte max 3.2 mm; Δ intencao 12.0 mm: conceito novo (usuario): alcapao duplo simetrico no lugar da pinca lateral
- **A11_portinhola**: menor folga em movimento 1.0 mm (A05.A x A01.A, carro em 144.0); parede p1 1.24 mm (min 1.0); overhang 0.0 mm2, ponte max 5.9 mm
- **A11_portinhola_f**: menor folga em movimento 1.0 mm (A05.A x A01.A, carro em 144.0); parede p1 1.76 mm (min 1.0); overhang 0.0 mm2, ponte max 0.0 mm
- **A36_garfo**: menor folga em movimento 1.0 mm (A05.A x A01.A, carro em 144.0); parede p1 1.81 mm (min 1.6); overhang 0.0 mm2, ponte max 3.2 mm
- **A08_gabarito**: parede p1 4.0 mm (min 1.6); overhang 0.0 mm2, ponte max 0.0 mm
- **A15_saida_magazine**: menor folga em movimento inf mm (A.patim x A15, carro em -141.0); parede p1 1.56 mm (min 1.6); overhang 0.0 mm2, ponte max 0.1 mm
- **A16_escapamento**: menor folga em movimento 5.5 mm (A10.A x A16, carro em -141.0); parede p1 2.0 mm (min 1.6); overhang 0.0 mm2, ponte max 9.9 mm
- **A26_entrada_berco**: menor folga em movimento 1.0 mm (A10.A x A26, carro em -141.0); parede p1 2.0 mm (min 1.6); overhang 6.3 mm2, ponte max 0.2 mm
- **A17_balancim**: menor folga em movimento inf mm (A.patim x A17, carro em -141.0); parede p1 1.91 mm (min 1.5); overhang 0.0 mm2, ponte max 9.7 mm
- **A18_entrada_magazine**: menor folga em movimento 3.38 mm (ref:A.garra x A18, carro em 99.0); parede p1 1.59 mm (min 1.6); overhang 0.0 mm2, ponte max 5.9 mm
- **A19_suporte_entrada**: menor folga em movimento inf mm (A.patim x A19, carro em -141.0); parede p1 5.4 mm (min 1.6); overhang 0.0 mm2, ponte max 0.1 mm
- **A12_calco**: menor folga em movimento inf mm (B.patim x A12, carro em -144.2); parede p1 9.54 mm (min 1.6); overhang 0.0 mm2, ponte max 0.0 mm
- **A12_calco_1**: menor folga em movimento inf mm (B.patim x A12, carro em -144.2); parede p1 11.31 mm (min 1.6); overhang 0.0 mm2, ponte max 0.0 mm
- **A12_calco_2**: menor folga em movimento inf mm (B.patim x A12, carro em -144.2); parede p1 7.15 mm (min 1.6); overhang 0.0 mm2, ponte max 0.0 mm
- **A12_calco_3**: menor folga em movimento inf mm (B.patim x A12, carro em -144.2); parede p1 9.18 mm (min 1.6); overhang 0.0 mm2, ponte max 0.0 mm
- **A12_calco_4**: menor folga em movimento inf mm (B.patim x A12, carro em -144.2); parede p1 5.22 mm (min 1.6); overhang 0.0 mm2, ponte max 0.0 mm
- **A12_calco_5**: menor folga em movimento inf mm (B.patim x A12, carro em -144.2); parede p1 6.73 mm (min 1.6); overhang 0.0 mm2, ponte max 0.0 mm
- **A13_rodape**: menor folga em movimento inf mm (B.patim x A13, carro em -144.2); parede p1 3.0 mm (min 1.6); overhang 0.0 mm2, ponte max 0.2 mm
- **A13_rodape_d**: menor folga em movimento inf mm (B.patim x A13, carro em -144.2); parede p1 3.0 mm (min 1.6); overhang 0.0 mm2, ponte max 0.2 mm
- **A20_base_elevador**: parede p1 4.41 mm (min 1.6); overhang 0.0 mm2, ponte max 2.6 mm
- **A24_suporte_motor_elevador**: parede p1 2.32 mm (min 1.6); overhang 0.0 mm2, ponte max 6.2 mm
- **A21_fuso**: menor folga em movimento inf mm (B.patim x A21, carro em -144.2); parede p1 1.67 mm (min 1.0); overhang 20.5 mm2, ponte max 0.0 mm
- **A21_fuso_2**: menor folga em movimento inf mm (B.patim x A21, carro em -144.2); parede p1 0.95 mm (min 1.0); overhang 36.8 mm2, ponte max 3.2 mm
- **A21_fuso_3**: menor folga em movimento inf mm (B.patim x A21, carro em -144.2); parede p1 2.79 mm (min 1.0); overhang 8.3 mm2, ponte max 3.2 mm
- **A22_tampa_elevador**: menor folga em movimento inf mm (A.patim x A22, carro em -141.0); parede p1 2.99 mm (min 1.6); overhang 0.0 mm2, ponte max 3.6 mm
- **A25_saida_elevador**: menor folga em movimento inf mm (A.patim x A25, carro em -141.0); parede p1 2.05 mm (min 1.6); overhang 0.0 mm2, ponte max 5.9 mm
- **A23_calha_elevador**: menor folga em movimento inf mm (A.patim x A23, carro em -141.0); parede p1 2.58 mm (min 1.6); overhang 0.0 mm2, ponte max 5.9 mm
