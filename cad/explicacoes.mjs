/* Explicacao completa de cada peca: e o que abre no pop-up quando se clica nela.
   Secoes: funcao (para que serve), como (como funciona), porque (por que e desse jeito),
   liga (ligacoes), ajuste (ajuste e teste), cuidado (cuidados e falhas comuns).
   Pode ser texto ou lista. HTML curto e permitido. */
export const EXPLICA = {

  /* ======================================================= SOLTURA */
  soltura_berco: {
    funcao: 'Segurar a bola parada, pendurada no carro do eixo A, e soltá-la no instante em que o jogador aperta o botão — sem dar nenhum empurrão para os lados.',
    como: ['A bola fica presa <b>pela lateral, na altura do equador</b>, entre duas coisas: atrás, a ponta do êmbolo do solenoide; na frente, um <b>V</b> fixo desta peça.',
      'Com o solenoide <b>desligado</b>, a mola dele empurra o êmbolo para a frente e aperta a bola contra o V. Ela fica presa por atrito: não tem nada embaixo dela.',
      'Quando o solenoide <b>liga</b>, o êmbolo recua 10 mm. A bola perde o apoio dos dois lados ao mesmo tempo e cai na vertical.',
      'Por cima da bola passa o "braço" desta peça: ele liga a parte de trás (onde fica o solenoide) à perna da frente (onde fica o V). Nada fica embaixo da bola.'],
    porque: ['<b>Por que não um pino por baixo (como no modelo antigo):</b> para uma bola de 35 mm cair, tudo que está embaixo dela tem que sair da frente uns 22 mm. O solenoide comprado só anda 10 mm. Segurando pela lateral, 10 mm sobram.',
      '<b>Por que um V e não uma parede reta:</b> as duas faces do V (a 45°) tocam a bola em dois pontos. A bola é empurrada para o fundo do V e fica centrada em X sozinha — e X é a direção que decide o jogo.',
      '<b>Por que na altura do equador:</b> é o único ponto em que a força horizontal do êmbolo não empurra a bola nem para cima nem para baixo. Mais alto ou mais baixo, ela escorregaria.',
      '<b>Por que o lado esquerdo é aberto:</b> é por ali que a bola entra, rolando da calha de carga, quando o carro está na ponta esquerda.',
      '<b>Por que imprimir de lado:</b> o desenho é um perfil (visto de lado) esticado em X; de lado na mesa, não tem nenhum balanço e não precisa de suporte.'],
    ajuste: 'Com uma bola no V e o solenoide desligado, deslize o solenoide pelos rasgos até a bola ficar presa com leve pressão (o êmbolo entra uns 0,5 mm "dentro" da bola). Vire o berço de cabeça para baixo: a bola não pode cair. Ligue 50 ms: ela tem que cair na hora.',
    cuidado: ['Pressão demais: o solenoide não consegue recuar rápido e a soltura atrasa (aumenta o jitter).', 'Pressão de menos: a bola cai sozinha com a vibração do carro na inversão.'],
  },
  soltura_batente: {
    funcao: 'Parar a bola que chega rolando da calha de carga exatamente no centro do berço.',
    como: 'A bola entra pelo lado esquerdo do berço, rolando sobre os trilhos de carga, e bate neste bloco. Ele fica a 0,25 mm de onde a bola tem que estar: quando a pinça fecha, a bola já está no lugar.',
    porque: ['Sem ele a bola passaria direto pelo berço (a pinça está aberta durante a carga).', 'É uma peça separada e azul (móvel/ajustável) porque é a cota mais sensível da carga: se a bola parar fora do centro, a pinça fecha torta. Dá para lixar ou reimprimir só ele.'],
  },
  sol_jf0826: {
    funcao: 'É o "dedo" que segura e solta a bola. É o elo final entre o botão do jogador e a bola caindo.',
    como: ['Uma bobina de fio de cobre em volta de um êmbolo de aço. Passando corrente (12 V, ~2 A), a bobina vira um ímã e puxa o êmbolo para dentro: a ponta grossa recua 10 mm.',
      'Sem corrente, a mola da ponta de trás empurra o êmbolo de volta para fora.',
      'Neste projeto a ponta grossa fica virada para a bola: desligado = segurando, ligado = soltando.'],
    porque: ['Solenoide e não servo: o catálogo do projeto mede 0,3 ms de jitter no solenoide contra 8 ms no servo. Como a bola voa 226 ms, cada ms de incerteza vira ~0,4 mm de erro no alvo.',
      'Desligado = segurando: se faltar energia, a bola fica presa (falha segura) e a bobina só esquenta no instante da soltura.'],
    liga: ['Os 2 fios vão no borne de saída do MOSFET da soltura (GPIO 18 comanda).', 'Diodo 1N4007 em paralelo nos terminais do solenoide, faixa no +12 V: na hora de desligar, a bobina gera um pico de tensão alto que queimaria o MOSFET; o diodo dá um caminho para essa energia.'],
    cuidado: ['Nunca deixe ligado mais que ~1 s: a 24 W ele esquenta rápido. O firmware liga por 50 ms e desliga.', 'Sem o diodo, o MOSFET morre em poucas centenas de disparos.'],
  },

  /* ======================================================= CARGA (magazine -> berco) */
  mag_carga: {
    funcao: 'Levar a bola da saída do magazine (atrás do eixo A) até dentro do berço (na frente), e segurá-la na comporta até a hora certa.',
    como: ['A bola vem da curva da saída andando para a frente (−Y), numa calha aberta inclinada 4°.',
      'No meio do caminho está a <b>comporta</b>: uma lâmina que sobe 9,5 mm acima do piso e segura a bola.',
      'Quando o carro A chega na ponta esquerda e o berço abre, o mini solenoide puxa a lâmina para baixo: a bola faz a curva de 90° e sai andando para a direita (+X).',
      'Na ponta da calha ela passa para <b>2 trilhos</b> que entram por baixo do berço. Rola sobre eles até bater no batente. A pinça fecha e o carro vai embora levando a bola; os trilhos ficam.'],
    porque: ['<b>Por que atravessa por baixo do bloco tensor do eixo A:</b> é o único caminho de trás para a frente que o carro A nunca ocupa. No meio do curso o carro passaria por cima; na ponta direita está o motor.',
      '<b>Por que a curva tem raio 21,6 mm:</b> menor que a meia-largura do canal (21,3) a parede de dentro se fecha sobre si mesma; maior, a travessia bateria na parede do gabinete (sobra 1,1 mm) ou o fim da calha entraria no caminho do berço (sobram 2 mm).',
      '<b>Por que 2 trilhos e não um piso:</b> o piso teria que ficar EMBAIXO da bola dentro do berço — e é por ali que a bola cai quando é solta. Dois trilhos finos, 20 mm afastados, seguram a bola só enquanto ela está ali e deixam o resto livre. Eles passam por baixo do V e do êmbolo sem encostar (3,5 mm de folga).',
      '<b>Por que a orelha na parede esquerda:</b> a calha fica em balanço do outro lado da junção com a saída; a orelha segura essa ponta.'],
    cuidado: ['O firmware NÃO pode soltar a bola com o carro A a menos de 112 mm do centro, pela esquerda: ali ela cairia em cima dos trilhos.'],
  },
  mag_comporta: {
    funcao: 'Segurar a próxima bola esperando, e soltar só quando o berço estiver pronto.',
    como: 'É uma lâmina vertical presa na ponta do êmbolo do mini solenoide (que fica embaixo da calha). Desligado, a mola empurra o êmbolo para cima e a lâmina fica 9,5 mm acima do piso. Ligado, o êmbolo desce 10 mm e a lâmina some dentro do rasgo do piso.',
    porque: ['<b>Por que DESCE em vez de girar:</b> uma lâmina que gira para abrir varre um arco; aberta, ela entraria no espaço por onde o berço passa. Descendo, ela nunca sai do rasgo.',
      '<b>Por que 9,5 mm:</b> uma bola de 35 mm parada contra um degrau de 9,5 mm não consegue subir nele (o ponto de contato fica bem abaixo do centro da bola). E 10 mm de curso do solenoide escondem 9,5 mm de lâmina com 0,5 de sobra.'],
  },
  sol_jf0530: {
    funcao: 'Abrir a comporta da calha de carga.',
    como: 'Igual ao solenoide da soltura, menor: bobina + êmbolo + mola. 12 V, ~300 mA, 10 mm de curso, ~5 N.',
    porque: 'A comporta só precisa vencer o peso da lâmina e o atrito: um solenoide pequeno basta e esquenta menos.',
    liga: ['Borne do MOSFET da comporta (GPIO 19).', 'Diodo 1N4007 em paralelo, faixa no +12 V.'],
  },
  mag_saida: {
    funcao: 'Receber a ponta do tubo P3, separar as bolas uma por vez (escapement) e virá-las 90° para a travessia.',
    como: 'Uma calha aberta que continua o tubo. No piso tem 2 rasgos: por eles sobem os dedos do balancim do escapement. Atrás, a chapa que segura o servo SG90.',
    porque: ['Calha ABERTA (e não tubo): imprime sem suporte e deixa ver/tirar uma bola presa com o dedo.', 'O tubo apoia numa meia-cana e é preso por abraçadeira de nylon: troca o tubo sem ferramenta.'],
  },
  mag_balancim: {
    funcao: 'Escapement: deixar passar UMA bola por vez da fila do magazine.',
    como: ['É uma gangorra presa no eixo do servo, com um dedo em cada ponta. Os dedos sobem pelos rasgos do piso da calha.',
      'Posição "segura": o dedo da frente está para cima e trava a primeira bola da fila; o de trás está escondido.',
      'O servo gira 24°: o dedo da frente desce (a 1ª bola vai embora) e, ao mesmo tempo, o de trás sobe ENTRE a 1ª e a 2ª bola, segurando a fila.',
      'O servo volta: o de trás desce e a fila anda uma posição até encostar no dedo da frente. Meia volta e volta = 1 bola.'],
    porque: 'Um dedo só não serve: no instante em que ele desce para soltar a 1ª bola, a fila inteira iria junto. Com dois dedos alternados, sempre tem um segurando.',
  },
  sg90: {
    funcao: 'Mexer o balancim do escapement.',
    como: 'Motor pequeno com redução e um potenciômetro no eixo: ele vai para o ângulo que o pulso de comando manda (pulso de 1 a 2 ms, 50 vezes por segundo).',
    porque: 'No escapement o tempo não importa (a bola espera na comporta), então o jitter de 8 ms do servo não atrapalha. Barato e já vem com o controle de posição.',
    liga: ['Marrom = GND', 'Vermelho = +5 V (do conversor LM2596, não do ESP32: na partida ele puxa até 0,5 A)', 'Laranja = sinal, GPIO 13'],
  },

  /* ======================================================= EIXO */
  mgn12_trilho_400: {
    funcao: 'Guia reta e rígida por onde o carro desliza.',
    como: 'O patim tem esferas que rolam em dois sulcos do trilho e voltam por dentro dele. Resultado: o carro anda sem folga de lado e quase sem atrito.',
    porque: 'A precisão do jogo depende de o carro estar exatamente onde o motor acha que está. Um trilho linear não deixa o carro balançar na inversão do movimento.',
    cuidado: ['Nunca tire o patim do trilho sem o trilho falso de plástico: as esferas caem.', 'Parafuso maior que M3×8 bate no fundo do perfil e entorta o trilho.'],
  },
  mgn12h_patim: {
    funcao: 'O carro que corre no trilho e leva tudo o que está em cima dele.',
    como: 'Bloco de aço com 4 roscas M3 em cima (20 × 20 mm). Dentro, duas carreiras de esferas recirculando.',
    cuidado: 'As roscas só têm 3,5 mm de fundo: parafuso comprido trava as esferas.',
  },
  eixo_placa_carro: {
    funcao: 'A "mesa" presa em cima do patim: liga o patim à correia (pela garra), à carga (berço ou boca) e aos fins de curso (pelas aletas).',
    como: '4 parafusos no patim. Na frente, 2 porcas embutidas onde a carga é parafusada. Atrás, a garra da correia. Nas pontas, as aletas que entram na fenda do sensor.',
    porque: ['As aletas cortam o feixe 4 mm ANTES do fim do curso: o carro passa pelo sensor a cada vai-e-volta, e é assim que o firmware confere se o motor perdeu passo.',
      'É azul (impresso que se move) porque é ela que leva a carga.'],
  },
  eixo_garra: {
    funcao: 'Prender as duas pontas da correia no carro.',
    como: 'A correia passa num canal aberto por baixo; duas presilhas dentadas apertam cada ponta contra o teto do canal.',
    porque: 'A correia do eixo é um laço ABERTO: as pontas presas no carro fazem dele o "elo" que fecha o laço. Assim, quando o motor gira, o carro anda exatamente 40 mm por volta.',
  },
  eixo_presilha: {
    funcao: 'Apertar a ponta da correia na garra.',
    porque: 'A nervura tem dentes no mesmo passo da correia (2 mm): eles encaixam nos dentes dela e a correia não escorrega mesmo com pouco aperto.',
  },
  eixo_bloco_motor: {
    funcao: 'Peça da ponta direita do eixo: segura o motor, prende o perfil e vai parafusada na lateral do gabinete.',
    porque: ['A placa do motor fica 35,5 mm atrás do trilho porque a polia (16 mm de largura) tem que alinhar com a correia, que passa atrás do patim.', 'Nada pode crescer para trás dela: 94 mm atrás começa a coluna do elevador.'],
  },
  eixo_bloco_tensor: {
    funcao: 'Ponta esquerda do eixo: segura a polia tensora e estica a correia.',
    como: 'A polia gira num parafuso M5 preso no deslizador. O parafuso tensor empurra o deslizador para fora (para a esquerda) e estica a correia; duas travas por trás seguram a posição.',
    porque: 'O tensor trabalha NA FRENTE da placa: no eixo A, atrás dela passa o magazine (a 43 mm do trilho).',
  },
  eixo_deslizador: { funcao: 'Carrinho que leva a polia tensora; anda no rasgo da placa quando a correia é esticada.' },
  polia_gt2_20t_5: {
    funcao: 'Transformar o giro do motor em movimento da correia.',
    como: '20 dentes de 2 mm = 40 mm de correia por volta. Com o motor de 200 passos e o driver em 1/8, cada pulso move o carro 0,025 mm.',
    cuidado: 'Aperte o parafusinho sobre a parte CHATA do eixo do motor; o outro, depois.',
  },
  polia_gt2_20t_tensora: { funcao: 'Polia do outro lado do laço: só guia a correia (gira solta no rolamento).' },
  correia_eixo: {
    funcao: 'Liga o motor ao carro.',
    como: 'Correia dentada GT2: os dentes encaixam na polia e não escorregam. 1 volta do motor = 40 mm de carro, sempre.',
    ajuste: 'Esticada até afundar ~3 mm com o dedo no meio e soar um "tum" grave (≈110 Hz).',
    cuidado: 'Frouxa, pula dente na inversão — é a folga que o PROJETO.md lista como risco.',
  },
  nema17: {
    funcao: 'Motor de passo: gira em passos exatos de 1,8° (200 por volta).',
    como: 'Duas bobinas acionadas em sequência pelo driver. A cada pulso de STEP o eixo anda um passo (ou 1/8 de passo com o TMC2209). Ele não precisa de sensor para saber onde está — desde que não perca passo.',
    porque: 'Precisão e repetição sem encoder. A conferência de "não perdeu passo" é feita pelo fim de curso, que o carro cruza a cada jogada.',
    liga: ['4 fios no borne da placa base do driver: uma bobina em A1/A2, a outra em B1/B2.', 'Ache os pares com o multímetro: entre os 2 fios de uma mesma bobina dá ~2 Ω; entre bobinas diferentes, aberto.'],
    cuidado: 'Nunca conecte ou desconecte o motor com o driver ligado.',
  },
  tcst2103: {
    funcao: 'Fim de curso óptico: avisa quando o carro passa por um ponto exato.',
    como: 'Um "U" com um LED infravermelho num braço e um fototransistor no outro, 3,1 mm de vão. Quando a aleta do carro entra no vão, corta o feixe e a saída muda de nível.',
    porque: ['Óptico e não chave mecânica: não tem desgaste e o ponto de corte repete em centésimos de mm.', 'Fica 4 mm DENTRO do curso de propósito: é cruzado a cada jogada e serve de régua para conferir os passos do motor.'],
    liga: ['VCC no 3,3 V do ESP32 (assim a saída já sai em 3,3 V)', 'GND', 'Sinal: GPIO 34 (eixo A), 35 e 39 (eixo B)'],
  },

  /* ======================================================= BOCA / DETECCAO */
  boca_alvo: {
    funcao: 'O alvo: chapa com o furo de 78 × 60 mm que anda no carro do eixo B, e a garganta onde a barreira IR confirma o acerto.',
    porque: ['Furo de 78 × 60 = geo.L × geo.depth do simulador: o modelo de acerto e a peça real usam o mesmo número.',
      'A borda tem só 13 mm de cada lado: no fim do curso a chapa chega a 3 mm da parede do gabinete.',
      'O feixe atravessa ao longo de X, no meio da profundidade: qualquer bola que passe corta o feixe, inclusive raspando nos cantos.'],
  },
  ir333c: {
    funcao: 'Emissor da barreira infravermelha.',
    como: 'LED que emite luz de 940 nm (invisível). Fica ligado o tempo todo.',
    liga: '+5 V → resistor de 150 Ω → perna LONGA (ânodo); perna curta no GND. ≈20 mA.',
    ajuste: 'A luz não aparece a olho nu: olhe pela câmera do celular, ela fica roxa.',
  },
  til78: {
    funcao: 'Receptor da barreira infravermelha.',
    como: 'Fototransistor: quanto mais luz IR chega nele, mais corrente ele deixa passar. A bola passando faz sombra e a corrente cai por alguns milissegundos.',
    liga: 'Coletor (perna curta, lado chanfrado) no IN do comparador LM393; emissor no GND.',
  },
  lm393: {
    funcao: 'Transformar o sinal "mais ou menos claro" do fototransistor em sinal digital limpo (0 ou 3,3 V) para o ESP32.',
    como: 'Comparador: compara a tensão do fototransistor com uma referência ajustada no trimpot. Passou do limite, a saída vira na hora — sem meio-termo.',
    porque: 'Ligado direto no ESP32, o fototransistor daria um sinal que muda devagar e depende da luz da sala. O comparador decide num ponto fixo e com histerese.',
    liga: ['VCC no 3,3 V, GND', 'IN: coletor do TIL78', 'OUT: GPIO 36 (boca) ou 21 (nível do magazine)'],
    ajuste: 'Feixe livre: gire o trimpot até o LED do módulo apagar e volte 1/4 de volta. Passe a mão: o LED tem que acender.',
  },

  /* ======================================================= MAGAZINE */
  mag_sensor_nivel: {
    funcao: 'Avisar quando o magazine está cheio, para o firmware parar o elevador.',
    como: 'LED IR de um lado do tubo, fototransistor do outro. Uma bola PARADA ali bloqueia a luz por muito tempo = fila chegou até aqui.',
    porque: 'A luz infravermelha atravessa o acrílico transparente: não precisa furar o tubo.',
  },
  mag_u_dir_f: { funcao: 'Curva em U da direita (liga P2 a P3).', como: 'Duas metades que fecham um canal de 36,4 mm em meia-volta de raio 21: a bola desce 42 mm e volta no sentido contrário.', porque: 'Canal 0,4 mm maior que o tubo para a bola não enganchar na borda do tubo ao entrar nele.' },
  tubo_p1: { funcao: 'Trecho de cima da fila de bolas.', porque: '4° de inclinação: a bola rola sozinha (precisa de mais que ~3,4° para vencer o atrito de rolagem do modelo) e a fila sobe o mínimo possível.' },

  /* ======================================================= ELEVADOR */
  elev_cacamba: {
    funcao: 'Copo que leva UMA bola do fundo até o topo.',
    como: 'Na subida (atrás), o fundo do copo fica embaixo da bola. No alto, o copo vira; a capa segura a bola até 45° depois do topo e ali ela cai na calha de entrega.',
    porque: ['Base de só 8 mm ao longo da correia: dobra em volta da polia de 28 mm sem forçar.', 'Presa com 2 parafusos M2 que passam RENTE às bordas da correia e uma arruela por dentro: a correia tem alma de aço e não pode ser furada.'],
  },
  elev_capa: {
    funcao: 'Segurar a bola no copo durante a curva de cima e decidir onde ela sai.',
    porque: 'Ela termina a 45° depois do alto: é ali que a bola deixa o copo. Se na bancada a bola não cair na calha, é esta peça que se ajusta.',
  },
  elev_concha: {
    funcao: 'Receber a bola que volta da bandeja e deixá-la esperando no fundo.',
    como: 'A bola entra pelo bico da frente, rola até o fundo da concha e para no ponto por onde todos os copos passam: o próximo copo a "varre" e leva.',
  },
  elev_polia_motora: { funcao: 'Polia de cima, direto no eixo do NEMA.', porque: '44 dentes = Ø primitivo 28,01 mm, o Ø28 do projeto. Só 6 mm de dentes: as arruelas das caçambas passam ao lado.' },
  elev_suporte_nema: { funcao: 'Prende o NEMA 17 do elevador na lateral da coluna.', porque: '6 mm: com a lateral de 6 mm, o eixo de 24 mm do motor ainda entra 11,5 mm no cubo da polia — sem acoplador nem eixo extra.' },
  correia_elev: { funcao: 'A esteira do elevador.', porque: 'Tem que ser FECHADA: uma emenda rígida não dobra em volta da polia de 28 mm.' },

  /* ======================================================= ELETRONICA */
  esp32: {
    funcao: 'O cérebro: lê o botão e os sensores, gera os pulsos dos 3 motores e liga os solenoides na hora certa.',
    como: 'Microcontrolador de 2 núcleos a 240 MHz. Um núcleo fica SÓ com o laço de tempo crítico (botão → solenoide); o outro cuida de motores, sensores e Wi-Fi (telemetria, atualização).',
    porque: ['Escolhido no ranking do ENGENHARIA.md § 5.2: o núcleo dedicado ataca o maior termo do erro de tempo da máquina.', 'Nenhum sensor ou saída está nos pinos de boot (0, 2, 5, 12, 15): com algo puxando um deles, o ESP32 não liga.'],
    liga: 'Alimentação: 5 V no VIN (do LM2596). Pinos: ver a tabela de ligações.',
    cuidado: 'Os GPIO são de 3,3 V: 5 V direto num GPIO queima o pino.',
  },
  tmc2209: {
    funcao: 'Driver do motor de passo: transforma os pulsos do ESP32 em corrente nas bobinas do motor.',
    como: 'A cada pulso em STEP, ele avança a corrente das bobinas um micropasso (1/8 de passo). DIR escolhe o sentido. EN liga/desliga o motor. Ele controla a corrente (não a tensão), por isso o motor não esquenta à toa.',
    porque: 'TMC2209: silencioso e com microsteps suaves; tem detecção de travamento (StallGuard) que pode ser usada depois como proteção extra.',
    ajuste: 'Vref ≈ 1,2 V (trimpot) para o 17HS4401: mede entre o trimpot e o GND com o motor DESLIGADO do driver.',
    cuidado: 'Nunca ligue/desligue o cabo do motor com o driver energizado.',
  },
  base_driver: { funcao: 'Placa onde o TMC2209 encaixa: traz borne de 12 V, capacitor de 100 µF e o conector do motor.', porque: 'Evita fio solto soldado no driver — o erro mais comum (e caro) de quem está começando.' },
  mosfet_logico: {
    funcao: 'Chave eletrônica que liga um solenoide (12 V, até 2 A) a partir de um pino do ESP32 (3,3 V, quase sem corrente).',
    como: 'O GPIO coloca 3,3 V no gate do MOSFET; ele conduz e fecha o circuito do solenoide. Gate em 0 V: abre o circuito.',
    porque: 'MOSFET "de nível lógico" conduz totalmente com 3,3 V. O IRF520 da planilha precisa de ~10 V: com 3,3 V ele fica meio ligado, esquenta e o solenoide fica fraco.',
    liga: ['+12 V e GND da fonte', 'Saída: solenoide (com o diodo em paralelo)', 'SIG: GPIO 18 (soltura) ou 19 (comporta)'],
  },
  irf520: { funcao: 'Liga o LED do botão do jogador (12 V, ~20 mA).', porque: 'Carga pequena: mesmo meio ligado com 3,3 V, o IRF520 dá conta. É o único lugar onde ele serve.', liga: 'SIG: GPIO 23.' },
  buck_lm2596: {
    funcao: 'Baixar os 12 V da fonte para 5 V (ESP32, servo e LEDs IR).',
    como: 'Conversor chaveado: liga e desliga muito rápido e filtra; perde pouco (esquenta pouco) mesmo convertendo 12 → 5 V.',
    ajuste: 'Ajuste o trimpot para 5,0 V na saída ANTES de ligar qualquer coisa nela.',
  },
  fonte_12v: {
    funcao: 'Toda a energia da máquina: 12 V, até 10 A.',
    porque: 'Picos: 2 A do solenoide de soltura + até 1,7 A por motor × 3 + o resto. 10 A deixam folga para os picos não derrubarem a tensão (o jitter do solenoide sobe se a fonte afundar).',
    cuidado: 'Há 220 V nos bornes de entrada: desligue da tomada antes de mexer. Ligue o terra (⏚) no gabinete.',
  },
  botao_arcade: {
    funcao: 'O único comando do jogador.',
    como: 'Ao apertar, a microchave embaixo fecha o contato NA com o COM. O ESP32 vê o pino ir de 3,3 V para 0 V e dispara a soltura.',
    liga: ['COM no GND, NA no GPIO 4 (com pull-up interno e filtro RC de 10 kΩ / 100 nF)', 'LED: + no 12 V, − na saída do IRF520'],
    porque: 'Interrupção dedicada no GPIO 4 + filtro por hardware: o caminho mais curto entre o dedo e o solenoide (ENGENHARIA.md § 5.1).',
  },
};
// as metades de tras repetem as da frente
EXPLICA.mag_u_dir_t = EXPLICA.mag_u_dir_f;
EXPLICA.mag_u_esq_f = Object.assign({}, EXPLICA.mag_u_dir_f, { funcao: 'Curva em U da esquerda (liga P1 a P2).' });
EXPLICA.mag_u_esq_t = EXPLICA.mag_u_esq_f;
EXPLICA.tubo_p2 = EXPLICA.tubo_p1; EXPLICA.tubo_p3 = EXPLICA.tubo_p1;
EXPLICA.eixo_bloco_tensor_semfc = EXPLICA.eixo_bloco_tensor;
EXPLICA.elev_polia_livre = { funcao: 'Polia de baixo: gira solta num rolamento 625, no eixo do tensor.', como: 'Descendo o eixo pelo rasgo das laterais, a correia estica.' };
