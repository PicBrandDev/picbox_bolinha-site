/* Textos da visao geral da /montagem. HTML curto: o visualizador so injeta. */
export const CONTEUDO = {
  intro: 'Duas partes. <b>Entender</b>: a máquina inteira, animações de como cada mecanismo funciona (com o "por que" de cada peça) e o mapa de ligações em 3D. ' +
    '<b>Montar</b>: cada módulo peça por peça, na ordem de montagem. Clique em qualquer peça ou cabo para abrir a explicação completa. ' +
    'Cada módulo da máquina usa as peças de verdade da planilha de compras. ' +
    'Toda peça impressa foi desenhada em cima das cotas do fabricante das peças compradas e passa por uma verificação ' +
    'automática de interferência (nenhuma peça invade outra). Clique em qualquer peça no 3D para ver a ficha: medidas, ' +
    'de onde vem a cota, o que conferir com o paquímetro e onde comprar ou baixar o arquivo para imprimir.',

  avisos: [
    { titulo: 'O que ainda falta comprar',
      texto: '<p>Gabinete, frente, motores NEMA (4), módulos e polias vocês já têm. Falta só o que aparece como <span class="chip falta">falta comprar</span> ' +
        'na <a href="#pecas">lista de peças</a>:</p><ul>' +
        '<li><b>Perfil de alumínio 20×20 V-slot, série 20 (canal 6 mm)</b>: 2 peças de 400 mm, corte em esquadro. É a viga reta onde o trilho é parafusado.</li>' +
        '<li><b>Elevador:</b> correia GT2 10 mm <b>fechada</b> de 1056 mm e rolamento 625ZZ (2, um de reserva).</li>' +
        '<li><b>Fim de curso mecânico de impressora 3D</b> (3): substitui os ópticos TCST2103.</li>' +
        '<li><b>Ferragens</b>: parafusos M2/M3/M5 e de madeira, porcas, porcas martelo M3 e M5 para perfil série 20 (quantidades na lista).</li>' +
        '<li>Confira se tem: tubo acrílico 40 × 36 suficiente para 571 mm (3 passes do magazine) e MDF 6 mm para o painel do magazine e as laterais do elevador.</li></ul>' },
    { titulo: 'Gabinete pronto: confira as medidas',
      texto: '<p>O projeto foi desenhado para 450 × 450 × 1700 em MDF 18 — <b>414 mm por dentro</b>, que é o comprimento exato dos eixos. ' +
        'Meça o gabinete de vocês (aba Gabinete) antes de imprimir os blocos de ponta dos eixos: se a medida for outra, os blocos e as alturas são ajustados no modelo.</p>' },
    { titulo: 'Elevador com NEMA 17 (não com o JGA25)',
      texto: '<p>O JGA25-370 de 15 rpm da planilha é a versão 1:377: a esteira andaria 19 mm/s e o magazine esvaziaria. O elevador usa um ' +
        '<b>NEMA 17 igual ao dos eixos</b> (vocês têm 4), direto na polia de cima, num 3º TMC2209.</p>' },
    { titulo: 'O módulo IRF520 não liga direito com o ESP32',
      texto: '<p>O IRF520 precisa de 10 V no gate para conduzir bem; o ESP32 entrega 3,3 V. O solenoide de soltura (≈2 A) fica fraco ' +
        'e o MOSFET esquenta. Use um módulo com MOSFET de nível lógico (<b>IRLZ44N</b> ou AO3400) e um diodo 1N4007 em paralelo com cada solenoide.</p>' },
    { titulo: 'Esteira do elevador: a emenda de alumínio não serve',
      texto: '<p>O fixador 9×40 é para correia de 6 mm (dente de 9 mm de largura) e, sendo rígido, não passa pela polia de Ø28. ' +
        'A esteira precisa ser uma <b>correia GT2 de 10 mm FECHADA</b> (sem emenda); a altura da coluna se ajusta ao comprimento dela.</p>' },
    { titulo: 'O encoder AS5600 não entra no eixo',
      texto: '<p>No eixo A, atrás da polia tensora passa o magazine (43 mm atrás do trilho); atrás do motor, a coluna do elevador (94 mm). ' +
        'O conjunto ímã + chip + placa precisa de ~25 mm a mais em qualquer um dos dois. A detecção de passo perdido passa a ser feita pelo ' +
        '<b>fim de curso mecânico</b>: ao ligar e uma vez por partida, cada carro encosta devagar na chave (clica a 143 mm do centro, 3 mm além do curso de jogo) ' +
        'e o firmware compara a contagem de passos naquele instante com a esperada. Os AS5600 ficam guardados.</p>' },
    { titulo: 'Bola: só Ø35',
      texto: '<p>O tubo do magazine tem 36 mm por dentro. A bola de 38 mm (conjunto de bilhar da planilha) não entra; a de 35 mm passa com 0,5 mm de folga por lado. ' +
        'Antes de comprar 15 bolas, passe UMA pelo tubo inteiro, inclusive pelas curvas impressas.</p>' },
  ],

  antes: '<p><b>Ferramentas:</b> jogo de chaves allen (1,5 / 2 / 2,5 / 3 / 4 mm), chave Phillips nº 2, paquímetro, alicate de bico, ' +
    'tesoura, nível de bolha, régua metálica. Opcional: torquímetro pequeno.</p>' +
    '<p><b>Antes de imprimir:</b> imprima primeiro o <i>gabarito de centragem</i> e confira: o trilho tem que entrar justo e o perfil deslizar ' +
    'sem forçar. Se ficar apertado, aumente a compensação de furos/XY do fatiador (0,1–0,2 mm) e reimprima — todas as outras peças usam a mesma folga.</p>' +
    '<p><b>Peças com <span class="chip medir">medir</span></b> vêm de anúncio genérico: meça a sua antes de imprimir a peça que encaixa nela. A ficha diz quais cotas medir.</p>',

  cores: '<p><span class="chip comprado">cinza</span> metal comprado · <span class="chip impresso">laranja</span> impresso fixo · ' +
    '<span class="chip" style="color:#06232a;background:#2b8fe0;border-color:#2b8fe0">azul</span> impresso que se move · preto: motor, correia, PCB. ' +
    'Em cada passo, as peças novas entram voando do lugar de onde você as coloca (parafuso sai do furo pelo eixo dele) e piscam em ciano.</p>' +
    '<p>Teclado: ← → passos · R repete · E explode · F destaca o passo · V câmera do passo.</p>',

  impressao: '<p>Todas em <b>PETG</b>, camada 0,2 mm, bico 0,4. Os STL já estão deitados na posição certa de imprimir. ' +
    'Peças do eixo A são as do eixo B espelhadas: use o arquivo "STL A". STEP para quem quiser editar.</p>',

  proximos: [],
};
