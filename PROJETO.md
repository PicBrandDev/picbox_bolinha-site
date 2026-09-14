# PICBOX — projeto

Documento-base de **produto, jogo e decisões**. O par técnico é [`ENGENHARIA.md`](ENGENHARIA.md).

Serve de contexto para Claude Chat, Claude Design e para as próximas decisões de engenharia.
Não descreve o que seria bom fazer: descreve o que **está no código**, o que é **hipótese** e o
que ainda **não tem dono nem resposta**.

**Convenção de marcação** — usada nas tabelas e no texto:

| marca | significado |
|---|---|
| `[D]` | decidido: está implementado e não se mexe sem motivo |
| `[H]` | hipótese: está implementado como valor de projeto, mas é palpite — precisa de validação |
| `[A]` | em aberto: ninguém decidiu ainda |

Estágio atual: **protótipo único**, operação comercial pretendida. Nenhuma cota física foi
validada em bancada; tudo o que é dimensão de máquina é `[H]` até existir peça cortada.

---

## 1. Conceito

Máquina de arcade de habilidade, do tipo *timing*, com prêmio físico.

Duas guias paralelas se movem continuamente, uma acima da outra:

- **Eixo A** carrega a **bola** (carro superior);
- **Eixo B** carrega o **buraco** (carro inferior, chapa com abertura).

O jogador tem **um botão**. Quando aperta, a bola é solta e cai. Ela nasce com a velocidade
horizontal que o carro A tinha no instante da soltura, voa ~226 ms e cruza o plano do buraco,
que também está andando. Acerta se, no cruzamento, bola e buraco estiverem alinhados.

O problema do jogador não é mira: é **antecipação**. Ele precisa apertar antes, porque entre o
dedo e a bola existe uma cadeia de atraso de ~29 ms, e porque a bola leva 226 ms no ar.

**O que torna o jogo honesto:** a máquina é determinística. Toda a incerteza que decide a partida
é o erro de *timing* humano. O jitter da própria máquina é ~1,46 ms — vinte vezes menor que o do
melhor jogador (26 ms). O simulador mede essa razão continuamente (`σ_jogador / σ_máquina`) e o
critério de projeto é **manter a razão acima de 4**: abaixo disso é a máquina que decide, não o
jogador, e o jogo vira loteria disfarçada. `[D]`

---

## 2. O ciclo de uma tentativa

1. A bola espera no **berço**, no carro A, presa por um pino.
2. O jogador aperta. Debounce, varredura do MCU, latência do solenoide — 29 ms em média.
3. O pino recolhe, a bola cai com a velocidade do carro.
4. Voo de 226 ms (queda de 250 mm), integrado com arrasto.
5. Cruza o plano da chapa-alvo: **acerto** se passar pelo furo, **erro** se bater na chapa.
6. Nos dois casos a bola termina na **bandeja**, que a conduz à calha de retorno.
7. Calha → concha do elevador → caçamba → topo → **magazine** (5,4 s medidos).
8. O magazine solta uma bola para a estação de carga, que recarrega o berço quando o carro A
   inverte o curso ao lado dela.

**Intervalo entre tentativas: ~2,4 s** — definido pelo carro A + comporta + berço, não pelo
elevador. Com 15 bolas em circulação e retorno de 5,4 s, o magazine não esvazia. `[D]`

---

## 3. Regras do jogo

### 3.1 O que já está implementado

| regra | valor | marca |
|---|---|---|
| Partida = **escada** de rodadas | 8 rodadas | `[H]` |
| Erro = **fim da partida** (morte súbita) | sim | `[H]` |
| Acerto = avança de rodada | sim | `[H]` |
| Vencer todas = vitória total | sim | `[H]` |
| Dificuldade por rodada | velocidade **+12 %** e abertura **−5 %** por rodada | `[H]` |
| Prêmio | amarrado a um **nível** da escada, não ao final | `[H]` |
| Prêmios de exemplo | pelúcia R$ 4,50 (nível 3) · fone R$ 22 (nível 6) · console R$ 180 (nível 8) | `[H]` |

Na rodada 8 a abertura caiu para 78 × 0,95⁷ ≈ **54,5 mm**, com bola de 35 mm.

### 3.2 O que ainda não foi decidido

Duas balizas travam todo o resto, e nenhuma é técnica:

1. **Unidade de pagamento** `[A]` — paga-se por *partida* (a escada inteira, morte súbita) ou por
   *tentativa* (N solturas avulsas)?
2. **Entrega do prêmio** `[A]` — sai da máquina, é voucher/código, ou vem de atendente?

Enquanto não houver resposta, seguem as opções em ordem de preferência.

### 3.3 Proposta A — escada com morte súbita *(preferida)*

É o que está no código. Paga-se a partida; um erro encerra; o prêmio é o nível alcançado.

- **A favor:** o custo de prêmio é controlável analiticamente (a probabilidade de chegar ao nível
  *n* é o produto das anteriores, e o simulador já calcula isso por perfil de jogador); a tensão
  cresce sozinha; o jogador sempre sai com a sensação de ter chegado perto.
- **Contra:** partida curta para iniciante — com σ = 130 ms muita gente cai na rodada 1 ou 2, e a
  percepção pode ser de máquina injusta.
- **Mitigação:** rodada 1 com abertura folgada de propósito (é o tutorial), ou 1 vida extra.

### 3.4 Proposta B — N tentativas fixas, pontuação acumulada

Compra-se um crédito com, por exemplo, 5 solturas. Cada acerto pontua; prêmio por faixa de pontos.

- **A favor:** tempo de jogo previsível, receita por minuto previsível, mais fácil de explicar ao
  público, sem frustração de "perdi na primeira".
- **Contra:** dificuldade não cresce sozinha — precisa de um esquema de pontuação por precisão
  (|δ| pequeno vale mais) para não ficar plano; custo de prêmio mais difícil de dimensionar.

### 3.5 Proposta C — híbrido: escada com vidas

Escada como em A, com 2 ou 3 vidas por crédito, e a vida extra comprável.

- **A favor:** junta a curva de tensão da escada com a previsibilidade de B; a vida extra é um
  segundo ponto de receita.
- **Contra:** mais estados de máquina, mais UI, e o dimensionamento de prêmio fica sensível ao
  preço da vida extra. Só vale depois que A estiver medido com gente real.

### 3.6 Critério de acerto

Existem dois, e a escolha muda o jogo inteiro:

| critério | condição | janela hoje |
|---|---|---|
| **conformidade** (ativo) | centro da bola dentro da boca: \|δ\| ≤ L/2 | ± 39,0 mm |
| passagem limpa | a bola inteira passa: \|δ\| ≤ (L−d)/2 | ± 21,5 mm |

O critério ativo é `conformidade` `[H]`. **Ele é otimista**: aceita como acerto uma bola cujo centro
passa pela borda do furo e que, fisicamente, bateria na chapa. A janela real está entre os dois
valores. Decidir isto é decidir a dificuldade do jogo e o custo de prêmio — é a decisão de produto
com maior alavancagem em aberto. `[A]`

---

## 4. Economia

Modelo implementado em `js/economy.js`, dimensionado **pelo perfil treinado** — é ele que "farma" a
máquina. Dimensionar pelo jogador médio é o erro clássico que quebra a operação.

| parâmetro | valor | marca |
|---|---|---|
| Preço da jogada | R$ 5,00 | `[H]` |
| Jogadas por dia | 120 | `[H]` |
| Teto de custo de prêmio (perfil treinado) | 30 % da receita | `[H]` |
| Mix de público | 55 % iniciante · 40 % médio · 5 % treinado | `[H]` |
| Tarifa de energia | R$ 0,95/kWh | `[H]` |

Saída do modelo: probabilidade de liberar cada prêmio por perfil, custo esperado de prêmio, custo de
energia por jogada e margem por perfil.

**Em aberto:** custo de capital da máquina, manutenção, ponto/aluguel, impostos, meio de pagamento,
e se o preço é R$ 5,00 mesmo. `[A]`

---

## 5. Decisões, hipóteses e pontos em aberto

Sem donos: agrupado por categoria, para atribuir quando o time estiver definido.

### Mecânica
- `[H]` Envelope 450 × 450 × 1700 mm; campo de jogo a 1100 mm do chão.
- `[H]` Bola Ø 35 mm, 30 g, acrílico/ABS.
- `[H]` Curso útil dos dois eixos: 280 mm. Abertura da boca: 78 mm. Queda: 250 mm.
- `[H]` Magazine de 15 bolas em serpentina de 3 passes.
- `[D]` Elevador de esteira com caçambas, curso 542 mm, pé logo abaixo da bandeja.
- `[A]` O que ocupa o vão de ~450 × 450 × 930 mm sob a bandeja (fonte? eletrônica? lastro? nada?).
- `[A]` Material do gabinete (hoje modelado como MDF 18 mm) e acabamento.
- `[A]` Transporte: "cabe em todo lugar" exige passar por porta de 800 mm e caber em veículo —
  precisa virar requisito com número.

### Eletrônica
- `[A]` Controlador. Nenhuma opção está escolhida — ver ranking em `ENGENHARIA.md § 5.1`.
- `[D]` Soltura por solenoide + driver dedicado (jitter 0,3 ms) — é o item que domina a cadeia.
- `[D]` Detecção na boca por barreira óptica: não muda a trajetória, mas é o que **prova** o acerto.
- `[A]` Fonte, proteção, aterramento, chicote, botoeira, iluminação.

### Software
- `[D]` Simulador de engenharia completo (7 modos) — é o que existe hoje e é a fonte de verdade
  dos números deste documento.
- `[A]` **Firmware da máquina real não existe.** Nada do que está em `js/` roda no dispositivo.
- `[A]` Telemetria/log em operação, atualização, diagnóstico de campo.

### Jogo
- `[A]` Unidade de pagamento, entrega do prêmio, critério de acerto (§ 3.2, § 3.6).
- `[H]` Escada de 8 rodadas com +12 % / −5 %.

### Custo e operação
- `[A]` BOM fechada, fornecedores, câmbio, mão de obra, impostos — estrutura pronta em
  `ENGENHARIA.md § 7`, à espera dos números do time.
- `[A]` Local de operação e regime (evento itinerante? fixo?), que definem vandalismo,
  alimentação elétrica e logística de prêmio.

---

## 6. Riscos

| risco | por quê | como matar |
|---|---|---|
| **σ humano é palpite** | 130/65/26 ms são ordem de grandeza de literatura, sem sujeito real | medir com 10–20 pessoas num protótipo de bancada, antes de cortar chapa |
| **Critério otimista de acerto** | `conformidade` aceita bola que bateria na chapa; infla a taxa de vitória e o custo de prêmio | simular com `passagem limpa` e comparar; decidir com o custo na mão |
| **Jogador treinado farma a máquina** | com σ = 26 ms a janela de ±39 mm é larga | é o perfil pelo qual o prêmio é dimensionado — manter essa disciplina |
| **Folga mecânica na inversão** | correia GT2 alonga; a folga não aparece em bancada estática, só na inversão | medir folga na inversão, não em repouso; é item de manutenção |
| **Elevador/magazine travando com bola presa** | fila, comporta e escapement são pontos de encravamento | sensor de nível já previsto; falta rotina de destravamento |
| **Máquina esvaziar durante a partida** | 15 bolas, 2,4 s por tentativa | resolvido no modelo (retorno de 5,4 s), mas depende do elevador real não escorregar |
| **Segurança e vandalismo** | arcade com prêmio, público apertando botão com força | requisito ainda não escrito |

---

## 7. Roadmap

### Fase 0 — simulação *(concluída)*
Motor de física, modelo de acerto, Monte Carlo, economia, catálogo de componentes, log/replay,
auditoria. Modelo 3D paramétrico da máquina inteira com verificação automática de envelope,
interferência, coerência e escoamento.

### Fase 1 — validar as hipóteses humanas *(próxima, barata, destrava tudo)*
1. Bancada mínima: um eixo, um botão, um alvo fixo. Sem prêmio, sem gabinete.
2. Medir σ de timing com 10–20 pessoas reais → substitui `ply.novice/mid/pro`.
3. Medir latência e jitter reais da cadeia botão → soltura → substitui `in.*` e `rel.*`.
4. **Saída:** decidir o critério de acerto (§ 3.6) com dado medido.

### Fase 2 — mecânica do tiro
1. Um eixo real com o carro e o berço; medir folga na inversão e erro de posição repetível.
2. Medir dispersão da bola (mesmo comando, N solturas) — é o teste que valida ou mata o
   mecanismo de soltura escolhido.
3. Validar o critério de acerto contra a chapa real (bola que raspa: passa ou não?).

### Fase 3 — máquina completa
1. Cortar gabinete, montar dois eixos, magazine, elevador, bandeja.
2. Fechar o ciclo de bola sem intervenção por ≥ 500 tentativas seguidas.
3. Firmware de verdade, com log de campo no mesmo formato do simulador (permite replay).

### Fase 4 — produto
1. Regras finais + preço + prêmios, dimensionados pelo perfil treinado medido.
2. Acabamento, iluminação, som, atract mode.
3. Piloto em operação real: 2 semanas de log → recalibrar economia.

### Fase 5 — escala
Só depois do piloto: revisão de BOM para custo, fixtures de montagem, manual de manutenção.

**Ordem não é negociável:** Fase 1 antes de qualquer corte de chapa. Todo o dimensionamento de
prêmio e de dificuldade descansa em três números que hoje são palpite.
