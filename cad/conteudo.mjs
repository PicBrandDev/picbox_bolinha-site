/* Textos da visao geral da /montagem. HTML curto: o visualizador so injeta. */
export const CONTEUDO = {
  intro: 'Cada módulo da máquina, montado peça por peça, com as peças de verdade da planilha de compras. ' +
    'Toda peça impressa foi desenhada em cima das cotas do fabricante das peças compradas e passa por uma verificação ' +
    'automática de interferência (nenhuma peça invade outra). Clique em qualquer peça no 3D para ver a ficha: medidas, ' +
    'de onde vem a cota, o que conferir com o paquímetro e onde comprar ou baixar o arquivo para imprimir.',

  avisos: [
    { titulo: 'Compre antes de montar: a planilha não fecha a máquina',
      texto: '<p>Itens que a montagem exige e que não estão na planilha aparecem como <span class="chip falta">falta comprar</span> ' +
        'na <a href="#pecas">lista de peças</a>. Os principais:</p><ul>' +
        '<li><b>Perfil de alumínio 20×20 de 400 mm</b> (2 unid.): é a viga reta onde o trilho é parafusado.</li>' +
        '<li><b>Polia GT2 20 dentes com furo de 5 mm</b> (2 unid.): a da planilha tem furo de 6,35 mm e fica torta no eixo de 5 mm do NEMA 17.</li>' +
        '<li><b>Polia tensora GT2 20 dentes com rolamento</b> (2 unid.).</li>' +
        '<li><b>Mais 1 tubo acrílico 40 × 36 de 50 cm</b>: os 3 passes do magazine somam 571 mm.</li>' +
        '<li><b>MDF 6 mm</b> para o painel do magazine (338 × 200) e as 2 laterais do elevador (111 × 614).</li>' +
        '<li><b>Elevador:</b> correia GT2 10 mm <b>fechada</b> de 1056 mm, acoplador rígido 4 × 5 mm, eixo retificado Ø5 × 70, 3 rolamentos 625ZZ.</li>' +
        '<li><b>Kit de ferragens</b>: parafusos M3, M5 e de madeira, porcas M3/M5, porcas martelo para perfil 2020 (quantidades exatas na lista).</li></ul>' },
    { titulo: 'Motor do elevador: 15 rpm é lento demais',
      texto: '<p>O JGA25-370 de 15 rpm é a versão 1:377 (≈13 rpm com carga). Com a polia de Ø28 a esteira anda 19 mm/s: ' +
        'a bola leva 25 s para subir e sai uma caçamba a cada 4,4 s. A máquina dispara uma bola a cada 2,4 s, então o magazine ' +
        'esvazia. Troque pela versão de <b>128 rpm (1:46,8)</b> — mesma carcaça, mesmos furos; dá ≈100 rpm com carga, perto dos 90 rpm do projeto.</p>' },
    { titulo: 'O módulo IRF520 não liga direito com o ESP32',
      texto: '<p>O IRF520 precisa de 10 V no gate para conduzir bem; o ESP32 entrega 3,3 V. O solenoide de soltura (≈2 A) fica fraco ' +
        'e o MOSFET esquenta. Use um módulo com MOSFET de nível lógico (<b>IRLZ44N</b> ou AO3400) e um diodo 1N4007 em paralelo com cada solenoide.</p>' },
    { titulo: 'Esteira do elevador: a emenda de alumínio não serve',
      texto: '<p>O fixador 9×40 é para correia de 6 mm (dente de 9 mm de largura) e, sendo rígido, não passa pela polia de Ø28. ' +
        'A esteira precisa ser uma <b>correia GT2 de 10 mm FECHADA</b> (sem emenda); a altura da coluna se ajusta ao comprimento dela.</p>' },
    { titulo: 'O encoder AS5600 não entra no eixo',
      texto: '<p>No eixo A, atrás da polia tensora passa o magazine (43 mm atrás do trilho); atrás do motor, a coluna do elevador (94 mm). ' +
        'O conjunto ímã + chip + placa precisa de ~25 mm a mais em qualquer um dos dois. A detecção de passo perdido passa a ser feita pelo ' +
        '<b>fim de curso óptico</b>: o sensor foi colocado 4 mm para DENTRO do curso (corta o feixe a 136 mm do centro, o curso vai a 140), então ' +
        'cada eixo cruza o feixe a cada vai-e-volta e o firmware compara a contagem de passos naquele instante com a esperada. Os AS5600 ficam guardados.</p>' },
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

  proximos: [
    { nome: 'Eletrônica e fiação', resumo: 'ESP32, 2× TMC2209, drivers dos solenoides, comparadores, fonte e botão.' },
  ],
};
