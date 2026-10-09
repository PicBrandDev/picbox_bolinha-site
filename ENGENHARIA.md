# PICBOX — engenharia

Documento-base **técnico**. O par de produto é [`PROJETO.md`](PROJETO.md), que define a convenção
`[D]` decidido · `[H]` hipótese · `[A]` em aberto.

Tudo aqui é extraído do código, não de memória:

| arquivo | o que é |
|---|---|
| `modelo3d.html` | modelo 3D paramétrico da máquina inteira (183 peças) + verificações automáticas |
| `js/physics.js` | perfis de movimento dos eixos e integração do voo (RK4) |
| `js/model.js` | mundo, oportunidades de acerto, janelas, sigmas e probabilidades |
| `js/game.js` | modo Jogar: partida, escada, log de sessão, replay |
| `js/montecarlo.js` | N partidas por perfil de jogador |
| `js/sweep.js` | varredura de 1–2 parâmetros (modo Engenharia) |
| `js/economy.js` | custo esperado de prêmio e margem, por perfil |
| `js/catalog.js` | componentes: opções, custo, jitter, dimensões e o impacto de cada um |
| `js/params.js` | registro único de parâmetros, com **procedência** por cota |

**Procedência** é regra do projeto, não enfeite: cada cota é `cat` (dimensão publicada em catálogo
do fabricante) ou `est` (dimensão de projeto, estimada). No modelo 3D atual: **31 de catálogo, 152
estimadas**. Uma cota nunca mistura as duas.

---

## 1. Arquitetura física

Envelope externo **450 × 450 × 1700 mm**, largura interna útil 415 mm, parede de 18 mm. `[H]`

### Orçamento vertical (mm, do chão)

| y | o que acontece |
|---|---|
| 0 – 1050 | vão livre: pedestal. **Nada ocupa hoje** `[A]` |
| 1050 – 1100 | painel de botões |
| **1115,9** | **pé do elevador** (lábio da concha de captação) |
| 1107 – 1150 | bandeja de captura: cai 4,5° em +X e 3° em −Z, drenando no canto traseiro |
| 1150 – 1220 | banda do eixo B (trilho + carro + boca) |
| **1220** | plano da boca do buraco |
| 1220 – 1470 | **queda útil: 250 mm** |
| **1470** | plano de soltura (centro da bola no berço) |
| 1470 – 1550 | banda do eixo A (trilho + carro + soltura) |
| 1491 | saída do magazine (passe mais baixo) |
| 1530 / 1175 | eixos dos trilhos A e B — separação 355 mm |
| 1591 | topo do elevador |
| 1594 | entrada do magazine (passe mais alto) |

O que manda nessa pilha é a **altura de queda** (`geo.h`) e a relação construtiva
`geo.sep = geo.h + 60 + 45`. Mexer em `geo.h` reposiciona sozinho tudo o que está acima.

### Planos em profundidade (z, 0 = plano dos trilhos)

- `z = +57` — **plano de jogo**: por onde a bola cai. Fica à frente dos carros, porque nos trilhos
  estão os dois carros e ela bateria neles.
- `z = 0` — trilhos e carros.
- `z = −63` — tubo do magazine, espremido entre a coluna do elevador (atrás) e a correia do eixo A
  (à frente). As duas folgas são verificadas automaticamente.
- `z = −150,5` — coluna do elevador, no canto traseiro direito.

---

## 2. Fluxo da bola

Circuito fechado, 15 bolas. Estados (nomes do código) e tempos **medidos no modelo**, 200 s de
operação contínua:

```
mag ──► desce ──► retido ──► carga ──► assento ──► berco ──► voo ──► trem
 ▲                                                                    │
 └── descarga ◄── balde ◄── captura ◄── espera ◄── concha ◄── calha ◄─┘
```

| trecho | como anda | tempo |
|---|---|---|
| fila do magazine → escapement | gravidade, 6° de caimento | fila |
| escapement (came, meia volta) | servo SG90 | 0,30 s |
| rampa de carga → comporta | gravidade, desnível de 16 mm | — |
| comporta → berço | gravidade, desnível de 5 mm, **só quando o carro A inverte ao lado** | 0,16 s |
| berço → voo | solenoide recolhe o pino | 29 ms de cadeia |
| voo | RK4 com arrasto | **225,9 ms** |
| bandeja → calha | atravessa até a guia de +X e desce por ela até o canto | ~0,16 s |
| calha → lábio da concha | trecho reto de 66 mm, queda de 22 mm (18°) | ~0,05 s |
| espera → caçamba | o copo **varre** a bola parada | ≤ 0,64 s |
| subida (475 mm a 131,9 mm/s) | esteira com 12 caçambas | **3,6 s** |
| despejo → magazine | o copo tomba a 45° depois do topo; calha de entrega | 0,2 s |
| **bandeja → magazine (total)** | | **4,85 s** |
| **intervalo entre tentativas** | carro A + comporta + berço | **~2,4 s** |

Regras de coerência que o modelo respeita e verifica:

1. **Nenhum teletransporte.** Toda troca de estado acontece no ponto em que os dois trechos
   coincidem. O verificador compara cada deslocamento com o que a velocidade da própria bola
   explica naquele quadro — hoje: **0 descontinuidades**.
2. **Nada de canto vivo.** Todo vértice de caminho vira arco tangente (`arredonda()`), com raio
   mínimo igual ao diâmetro da bola — abaixo de ~0,94·Ø duas bolas da fila se interpenetram na
   curva.
3. **Nenhum trecho sem apoio.** A bola sempre tem calha, chapa ou copo sob ela.
4. **Nenhum trecho que não escoa.** Ver § 6.

---

## 3. Mecanismos

| mecanismo | função | o que define a cota |
|---|---|---|
| **Magazine** | armazena 15 bolas em serpentina de 3 passes, escoando por gravidade a 6° | passo = Ø + folga = 37 mm; 5 bolas por passe; desnível entre passes 42 mm (menos que isso e as paredes de dois passes se cruzam) |
| **Escapement** | came de meia volta libera **uma** bola | servo SG90, 0,30 s |
| **Comporta de carga** | lâmina que segura a bola no fim da rampa. **Desce** para abrir — girando, a chapa aberta entraria no volume varrido pelo berço | 19 mm de curso, 0,16 s. Só abre com o carro A alinhado e praticamente parado (< 80 mm/s): por isso a máquina carrega **no fim do curso**, não em qualquer ponto |
| **Berço + pino** | copo aberto embaixo; quem segura a bola é o **pino lateral**, não o fundo | arco de abraço 150°; o pino recolhe e a bola cai livre |
| **Eixos A e B** | trilho linear MGN12 + carro, curso 280 mm, perfil senoidal, períodos 2,40 s e 3,10 s, defasagem 90° | velocidade de pico 367 mm/s (A) e 284 mm/s (B) |
| **Boca / chapa-alvo** | abertura de 78 mm numa chapa de 60 mm de profundidade, com portinhola e barreira óptica | a portinhola é a confirmação **mecânica e visível** de que a bola passou e não raspou |
| **Bandeja** | recebe a bola que entrou e a que errou e entrega no canto traseiro direito | dois caimentos: 4,5° em +X joga a bola contra a guia de saída, 3° em −Z a leva por essa guia até o canto. Ela sai **já andando na direção do elevador** |
| **Calha de retorno** | liga o canto da bandeja ao lábio da concha | trecho reto de 66 mm: como a bola já sai andando em −Z, não há curva fechada, queda livre nem trecho sem apoio. Só o último raio fica sem calha — ali quem sustenta a bola já é a chapa da concha |
| **Elevador** | esteira com 12 caçambas, curso 475 mm, 90 rpm em polia Ø28 = 131,9 mm/s | o pé é **derivado** do retorno; a profundidade do copo é o que a bola exige para caber encostada na tampa; o despejo é **geométrico** (a capa do topo acaba a 45° e a bola rola para fora), não temporizado |
| **Concha + fila** | recebe a bola e a guarda no ponto que o copo varre | só a **primeira** bola espera dentro do volume varrido; as demais param antes da boca, na própria calha |

---

## 4. Física

### 4.1 Voo

RK4, passo de 0,25 ms, em SI. Arrasto ligado, Magnus desligado por padrão (o modelo de Cl é
grosseiro — serve como sensibilidade, não como verdade).

```
m·dv/dt = m·g − ½·ρ·Cd·A·|v|·v   (+ Magnus, se ligado)
```

Bola: Ø 35 mm, 30 g, Cd 0,47 (esfera lisa, regime subcrítico), k = 0,4 (esfera maciça).
Ar: ρ 1,184 kg/m³, μ 1,849·10⁻⁵ Pa·s.

A bola **herda a velocidade do carro A** no instante da soltura — é isso que faz o jogo: apertar
mais cedo não muda só o instante, muda também a velocidade de lançamento.

Para não integrar a cada quadro, o modelo monta uma **LUT de 121 pontos** em `vx0` e interpola;
o erro de interpolação é **medido** e exibido (hoje ~1,2·10⁻⁶ mm).

### 4.2 Transporte (rolagem)

Fora do voo, a bola não voa: ela rola dentro de calhas. A aceleração ao longo do caminho é

```
a = g·(sen θ − μ·cos θ) / (1 + k)      θ = inclinação local do caminho
a = g                                  em trecho quase vertical (não está apoiada em nada)
```

com `k = ball.ki = 0,4`. Tratar a bola como bloco deslizante a faz descer 40 % rápido demais.
A velocidade tem teto vindo da altura do gabinete (estabilidade da integração), e **não tem
piso**: se o caimento não vence a resistência de rolagem, a bola **para** — e o verificador acusa.

### 4.3 Cadeia de tempo botão → bola

```
latência média = debounce + varredura/2 + latência de entrada + latência de soltura = 29,0 ms
σ_máquina      = √( jitter_soltura² + jitter_entrada² + varredura²/12 ) = 1,46 ms
```

A varredura do MCU é quantização pura: `σ = passo/√12`. É por isso que trocar um laço de 100 Hz por
um de 1 kHz vale mais que quase qualquer outra otimização de firmware.

### 4.4 Critério de acerto

```
δ = x_bola(cruzamento) − x_buraco(cruzamento)
conformidade   : |δ| ≤ L/2       = ± 39,0 mm   (ativo)
passagem limpa : |δ| ≤ (L−d)/2   = ± 21,5 mm
```

**Limitação conhecida `[A]`:** `conformidade` ignora o raio da bola e a profundidade da boca não é
simulada — uma bola que raspa a borda é contada como acerto. A janela real está entre os dois
valores. Ver `PROJETO.md § 3.6`.

---

## 5. Hardware

O catálogo (`js/catalog.js`) carrega, por opção: custo, jitter imposto, dimensões (com procedência)
e o efeito no σ da máquina. Trocar a opção **reescreve os parâmetros e a malha 3D** — o modelo e o
número nunca divergem.

### 5.1 Ranking por categoria

Ordem = preferência. Custo em R$, unitário, estimado.

**Mecanismo de soltura** — domina o jitter: é o último elo antes da bola sair.
1. **Solenoide + driver dedicado (MOSFET, flyback)** — R$ 45 · jitter 0,3 ms. *Selecionado.* Curso
   curto e corrente de pico alta; exige fonte firme, o jitter cresce se a fonte afundar.
2. Came motorizada contínua — R$ 60 · 2,5 ms. Soltura em fase fixa; impõe spin residual alto.
3. Servo hobby (MG996R/SG90) — R$ 25 · 8 ms. O laço interno do servo é assíncrono ao MCU: uma
   ordem de grandeza pior.

**Motor dos eixos** — define o erro de posição repetível.
1. **Passo NEMA 17 + encoder de malha fechada** — R$ 180 · 0,05 mm. *Selecionado.* Perda de passo
   detectada e corrigida; melhor relação previsibilidade/custo.
2. BLDC com encoder — R$ 260 · 0,08 mm. Silencioso e eficiente; controle mais complexo.
3. DC escovado com potenciômetro — R$ 70 · 0,60 mm. Realimentação ruidosa e não linear; costuma ser
   o item que derruba a razão de sigmas.

**Transmissão** — a folga não aparece em bancada estática, só na inversão.
1. **Correia GT2 + polia de 20 dentes** — R$ 40 · 0,10 mm. *Selecionada.* 40 mm/volta; alonga com o
   tempo — item de manutenção.
2. Pinhão e cremalheira — R$ 95 · 0,30 mm. Curso ilimitado, folga alta sem pré-carga.
3. Fuso trapezoidal T8 — R$ 120 · 0,20 mm. Rígido, mas lento e ruim para inversões frequentes.

**Detecção na boca** — não afeta a trajetória; afeta a capacidade de **provar** o que aconteceu.
1. **Barreira óptica (fototransistor + IR)** — R$ 35 · 0,2 ms. *Selecionada.* Exige alinhamento e
   proteção contra luz ambiente.
2. Chave mecânica — R$ 8 · 8 ms. Barata, com bounce; pode não registrar bola leve raspando.
3. Sensor indutivo — R$ 60 · 1,5 ms. Robusto a sujeira, **mas só funciona com bola metálica** — hoje
   a bola é acrílica, então está fora por incompatibilidade, não por desempenho.

**Cadeia de entrada (botão → MCU)**
1. **Interrupção externa dedicada + debounce por hardware** — R$ 12 · 0,06 ms. RC + Schmitt trigger;
   o caminho mais curto entre o dedo e o solenoide. *Preferida, ainda não selecionada.*
2. **Laço de varredura a 1 kHz** — R$ 0 · 0,34 ms. *Selecionado hoje.* Aceitável com soltura por
   solenoide.
3. Laço a 100 Hz — R$ 0 · 3,0 ms. Sozinho pode dominar todo o σ da máquina. Descartado.

### 5.2 Controlador `[A]`

Nenhuma opção foi escolhida e nenhuma está no catálogo ainda. Ranking proposto, pelo que a máquina
exige (2 eixos com encoder, 1 solenoide de pico alto, 2 servos, barreira óptica, fita de LED,
botoeira, log):

1. **ESP32 (dual core) + drivers de passo dedicados** — timer de hardware e núcleo dedicado ao laço
   crítico, Wi-Fi para telemetria e atualização, custo baixo, comunidade enorme. O laço de entrada
   fica num núcleo isolado, o que ataca direto o maior termo do σ.
2. **RP2040 + PIO** — o PIO faz geração de passo e leitura de encoder em hardware, jitter
   praticamente nulo; determinismo melhor que o do ESP32. Sem rádio nativo, exige mais firmware.
3. **STM32 (F4) + HAL** — mais periféricos de tempo real e o caminho natural se isto virar produto;
   custo de desenvolvimento maior.
4. **Arduino Mega / AVR** — só como bancada de Fase 1. Não tem fôlego para dois eixos com encoder e
   um laço de 1 kHz confiável.
5. **CLP industrial** — descartado: ciclo de varredura de dezenas de ms mata a cadeia de tempo, que
   é justamente o que precisa ser preciso nesta máquina.

Fora do controlador, ainda sem decisão: fonte e proteção, driver do solenoide de pico, aterramento,
chicote, botoeira do jogador, iluminação (WS2812B modelada), som e meio de pagamento.

---

## 6. Software

### 6.1 O que existe

Simulador de engenharia (`index.html`, ES5, sem dependências de runtime; servido por `serve`,
deploy em Railway) com 7 modos:
**Jogar** (partida real com log e replay) · **Monte Carlo** (N partidas por perfil) · **Engenharia**
(varredura de 1–2 parâmetros) · **Economia** · **Catálogo** · **Log & Replay** · **Auditoria**.

Uma única engine serve os quatro modos que calculam — não existe "física do jogo" separada da
"física do estudo". Convenção de unidades: interface e eixos em mm/mm/s/ms, integração do voo em SI,
conversão só nas bordas.

Modelo 3D (`modelo3d.html`, Three.js): a máquina inteira, paramétrica. Cada peça carrega ficha
(função, de onde sai a cota, procedência) e a geometria é **derivada** — `derive()` recalcula tudo a
cada `rebuild()`, então mudar `ball.d` ou `geo.h` reconstrói a máquina coerente.

### 6.2 Verificações automáticas do modelo

Rodam a cada `rebuild()`; hoje **zero avisos** nas quatro:

| verificação | o que testa |
|---|---|
| **Envelope** | nenhuma peça fora de 450 × 450 × 1700 |
| **Interferência** | OBB/SAT entre todas as peças — nenhum volume comum |
| **Coerência** | as cotas que brigam entre si: tubo do magazine × coluna do elevador × correia do eixo A; ramo de carga entre o acrílico da tela e o mancal do trilho; curso e pé do elevador; estação de carga dentro da largura útil |
| **Escoamento** | integra a **mesma** física de rolagem ao longo de cada caminho e aponta onde `v` chegaria a zero. O critério **não** é geométrico de propósito: um trecho horizontal escoa se a bola chegar nele com energia sobrando |

### 6.3 O que não existe `[A]`

**Firmware.** Nada em `js/` roda na máquina. O simulador é a especificação executável do
comportamento — a portabilidade pretendida é o formato de log: se o firmware gravar os mesmos
eventos (`botao`, `soltura`, `cruzamento`, `acerto/erro`), o log de campo pode ser reproduzido no
replay do simulador e comparado com a previsão.

---

## 7. Custos

Estrutura pronta, números **à espera do time**. O que já tem preço vem do catálogo e é estimado.

| subsistema | itens | R$ | marca |
|---|---|---|---|
| Acionamento dos eixos | 2 × motor + 2 × transmissão | 2 × 180 + 2 × 40 = **440** | `[H]` |
| Soltura | solenoide + driver | **45** | `[H]` |
| Detecção | barreira óptica na boca | **35** | `[H]` |
| Entrada | debounce por hardware (se adotado) | **12** | `[H]` |
| Guias lineares | 2 × trilho MGN12 + carros + suportes | — | `[A]` |
| Elevador | motor DC 12 V, 2 polias, esteira 1179 mm, 14 caçambas | — | `[A]` |
| Magazine | tubo, came + servo SG90, comporta + solenoide, sensor de nível | — | `[A]` |
| Estrutura | MDF 18 mm, vidro 6 mm, acrílico da tela, ferragem | — | `[A]` |
| Eletrônica | controlador, fonte, chicote, botoeira, LED | — | `[A]` |
| Acabamento | pintura, adesivagem, iluminação, som | — | `[A]` |
| Mão de obra e impostos | — | — | `[A]` |
| **Prêmios (custo variável)** | pelúcia R$ 4,50 · fone R$ 22 · console R$ 180 | por partida, ver `js/economy.js` | `[H]` |

Duas perguntas precisam de resposta antes de fechar qualquer total: o custo é **só material** ou
inclui mão de obra e impostos? E é para **uma** unidade (protótipo) ou já com preço de lote?

---

## 8. Validações que faltam

Em ordem de impacto. As três primeiras invalidam números de projeto se derem diferente.

1. **σ de timing humano** — 130/65/26 ms são estimativa de literatura. Medir com 10–20 pessoas.
   É a entrada de maior alavancagem de todo o modelo: dimensiona prêmio, dificuldade e receita.
2. **Critério de acerto contra a chapa real** — a bola que raspa a borda passa? Define qual dos dois
   critérios é o verdadeiro.
3. **Latência e jitter reais da cadeia** — cronometrar botão → bola saindo, N vezes. Substitui
   `in.*` e `rel.*`, que hoje vêm de datasheet.
4. **Folga na inversão** — medir com o carro invertendo, não parado.
5. **Dispersão da bola** — mesmo comando, N solturas, medir o espalhamento no plano da boca. É o
   teste que aprova ou reprova o mecanismo de soltura.
6. **Coeficiente de arrasto e a hipótese de spin residual** — o simulador já mostra o arrasto como
   percentual do peso; confirmar em queda livre instrumentada.
7. **Ciclo do elevador com bola real** — escorregamento da esteira, encravamento na concha, fila.
8. **Vida útil e travamento** — 500 tentativas seguidas sem intervenção humana.

---

## 9. Como mexer

- **Parâmetro vivo:** tudo em `js/params.js` tem faixa, unidade, procedência e nota. Mudar ali
  propaga para os quatro modos e para o modelo 3D.
- **Cota derivada:** no modelo 3D, `derive()` é a única fonte. Se uma cota pode ser **calculada** a
  partir da bola, do gabinete ou de outra cota, ela **não** é parâmetro — duplicar fórmula em duas
  funções foi a causa de metade dos erros de geometria já corrigidos.
- **Peça nova:** registre com `reg()` (nome, subsistema, procedência, dimensões) e escreva a ficha.
  Peça sem ficha entra na lista, mas ninguém sabe por que ela existe.
- **Antes de aceitar qualquer mudança de geometria:** as quatro verificações do § 6.2 têm que voltar
  zeradas. Elas são baratas e pegam o que o olho não pega.

---

## 10. Montagem guiada (`/montagem`)

Passo a passo visual de cada módulo, com as peças **compradas** (planilha do Plano 1) e as
**impressas** desenhadas sobre as cotas do fabricante delas. Fonte: `cad/` (replicad =
OpenCascade em WebAssembly, roda em Node sem instalar nada nativo).

```
cd cad && npm install && node build.mjs        # ~15 s: GLB, STL/STEP e montagem/guia.json
```

O build roda 3 verificações por módulo e para a máquina inteira — hoje **zero** nas três:
interferência entre peças (> 5 mm³), **varredura** dos carros carregados até ±140 mm e
**trajetória** de uma caçamba dando a volta no elevador.

### Decisões que a peça real impôs `[H]`

| item | decisão | por quê |
|---|---|---|
| largura interna | 414 mm (não 415) | 450 − 2 × MDF 18; com 415 os pés dos eixos entram na parede |
| soltura | berço de **pinça** (solenoide empurra a bola contra um V) | pino por baixo precisaria de ~22 mm de curso; o JF-0826B tem 10 |
| fim de curso | dispara a ±136 mm, dentro do curso (±140) | o carro cruza a cada jogada e o firmware confere os passos ali — o AS5600 não cabe atrás de nenhuma polia |
| eixo A | sem o sensor da esquerda | ali passa a calha do magazine para o berço |
| boca | 13 mm de borda (não 26) | no fim de curso a chapa sairia do gabinete |
| magazine | tubo Ø40 a **4°** (não 6°), 571 mm de tubo | a 6° o topo do elevador passaria do teto |
| elevador | correia GT2 10 mm **fechada** 1056 mm, polias 44 dentes impressas | emenda rígida não passa na polia de 28 |
| firmware | não soltar com o carro A a menos de 112 mm do centro pela esquerda | ali a bola cairia nos trilhos de carga |
| elevador | NEMA 17 direto na polia de cima, num 3º TMC2209 | o JGA25 de 15 rpm (1:377) daria 19 mm/s e o magazine esvaziaria |
| bandeja | MDF 6 mm sobre 4 calços impressos de alturas diferentes | 390 × 225 não cabe na impressora (260 × 260 × 300); os calços dão os dois caimentos |
| bandeja | borda esquerda rebaixada sob o eixo B | o ponto alto (1150) fica 1 mm abaixo do perfil do B (1151) |
| botão | centro a 1065 mm | mais alto, a porca (Ø33) bate na divisória do campo (1082) |
| frente | policarbonato 4 mm | local público: não estilhaça |

**Alternativa estudada — bomba de coluna com pistão** (aba "alt.: pistão"): mais compacta, mas prende 13 bolas
no tubo (a máquina precisaria de ~28), trava com uma bola ruim e, com atuador linear barato, não aguenta
~1000 ciclos/dia. Se for testada, que seja com NEMA + manivela.

A lista do que **falta comprar** está na própria página (lista de peças → "falta comprar").
