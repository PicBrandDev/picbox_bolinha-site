/* MODULO 6 — ELETRONICA: placa de montagem + ligacoes pino a pino

   Referencial: a placa de MDF deitada na mesa, face de cima em z = 0, x ao longo dos 300 mm.
   Na maquina ela vai na prateleira de logica do pedestal (430 mm do chao, modelo 3D).

   Escolha de pinos do ESP32 DevKit V1 (30 pinos):
     - nada nos pinos de boot (0, 2, 5, 12, 15): o ESP32 nao liga se um deles estiver puxado errado
     - sensores nos pinos so-de-entrada (34, 35, 36, 39): sobram os de saida para o resto
     - sensores alimentados em 3,3 V: a saida deles ja vem no nivel do ESP32, sem divisor */
import { caixa, cil, cilC, FOLGA } from '../lib/base.mjs';
import { peca, inst } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';

const IMP = { tipo: 'impresso', src: 'est', material: 'PETG' };
peca('elet_placa', { nome: 'Placa de montagem da eletrônica (MDF 6 mm)', tipo: 'cortar', src: 'est', dims: '300 × 200 × 6 mm',
  link: 'https://lista.mercadolivre.com.br/mdf-6mm-sob-medida',
  notas: ['Vai parafusada na prateleira de lógica do pedestal (430 mm do chão). Desenhe a posição de cada módulo com o gabarito impresso 1:1.'] },
() => [{ forma: caixa(-150, -100, -6, 150, 100, 0), cor: 'mdf' }]);
peca('elet_espacador', Object.assign({}, IMP, { nome: 'Espaçador de placa (8 mm)', dims: 'Ø7 × 8 mm', cor: 'impresso2', imprimir: { rot: [] },
  impressao: { preenchimento: '100 %', paredes: 3, suportes: 'não', tempo: '3 min cada' },
  notas: ['Um em cada furo de módulo: o módulo fica 8 mm acima do MDF, com os pinos de baixo livres.',
    'Parafuso M3×16 de cima: atravessa módulo + espaçador e morde no MDF (furo de 2,5 mm).'] }),
() => [{ forma: cil(7, 8, [0, 0, 0], 'z').cut(cil(FOLGA.m3, 10, [0, 0, -1], 'z')), cor: 'impresso2' }]);

// [id, peca, x, y, furos locais [[x,y],...]]
const LAYOUT = [
  ['esp32', 'esp32', -85, 45, [[-23.7, 11.9], [23.7, 11.9], [-23.7, -11.9], [23.7, -11.9]]],
  ['drv_a', 'base_driver', -10, 50, [[-17.5, 15.5], [17.5, 15.5], [-17.5, -15.5], [17.5, -15.5]]],
  ['drv_b', 'base_driver', 45, 50, [[-17.5, 15.5], [17.5, 15.5], [-17.5, -15.5], [17.5, -15.5]]],
  ['buck', 'buck_lm2596', 112, 55, [[-17.5, 7.5], [17.5, -7.5]]],
  ['mos_sol', 'mosfet_logico', -110, -35, [[-14, 5.5], [-14, -5.5]]],
  ['mos_comp', 'mosfet_logico', -65, -35, [[-14, 5.5], [-14, -5.5]]],
  ['mos_elev', 'mosfet_logico', -20, -35, [[-14, 5.5], [-14, -5.5]]],
  ['mos_led', 'irf520', 30, -35, [[-13, 9], [-13, -9]]],
  ['cmp_boca', 'lm393', 85, -30, [[-13, 0]]],
  ['cmp_nivel', 'lm393', 85, -65, [[-13, 0]]],
];
const H = 8;   // altura dos espacadores

function instancias() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  const r = T.of();
  add('placa', 'elet_placa', r);
  LAYOUT.forEach(([id, p, x, y, furos]) => {
    add(id, p, r.t(x, y, H));
    furos.forEach(([fx, fy], i) => {
      add(`esp_${id}_${i}`, 'elet_espacador', r.t(x + fx, y + fy, 0));
      add(`p_${id}_${i}`, p === 'esp32' ? 'din912_m2x10' : 'din912_m3x16', r.t(x + fx, y + fy, H + 1.6));
    });
  });
  // TMC2209 encaixado em cada base
  ['drv_a', 'drv_b'].forEach(d => { const l = LAYOUT.find(q => q[0] === d); add('tmc_' + d.slice(-1), 'tmc2209', r.t(l[2] - 2, l[3], H + 1.6 + 8.5 + 3)); });
  // fonte e botao, fora da placa (so para conhecer)
  add('fonte', 'fonte_12v', r.t(0, -190, -6));
  add('botao', 'botao_arcade', r.rx(90).t(0, -320, 60));
  return I;
}

/* ---------------------------------------------------------------- tabela de ligacoes */
export const LIGACOES = [
  ['Fonte V+ (12 V)', 'bornes 12 V das 2 bases de driver, + dos 3 MOSFET, + do LED do botão, entrada IN+ do LM2596', 'fio 1 mm² vermelho'],
  ['Fonte V− (GND)', 'GND de TUDO (bases, MOSFET, LM2596 IN−, ESP32 GND, sensores)', 'fio 1 mm² preto — um só ponto de terra'],
  ['LM2596 OUT+ (5,0 V)', 'ESP32 VIN, servo SG90 (vermelho), LEDs IR (via 150 Ω)', 'ajuste 5,0 V antes de ligar'],
  ['ESP32 3V3', 'VIO das 2 bases de driver, VCC dos 2 LM393, VCC dos fins de curso TCST2103', 'sensores em 3,3 V = saída já no nível do ESP32'],
  ['GPIO 25 / 26', 'STEP / DIR do eixo A (bola)', ''],
  ['GPIO 32 / 33', 'STEP / DIR do eixo B (buraco)', ''],
  ['GPIO 27', 'EN das 2 bases (liga/desliga os motores)', 'nível baixo = motores ligados'],
  ['GPIO 34', 'fim de curso do eixo A (direita)', 'entrada; o A cruza ele a cada jogada'],
  ['GPIO 35 / 39', 'fins de curso do eixo B (esquerda / direita)', 'entradas'],
  ['GPIO 36', 'LM393 da boca (OUT)', 'acerto: borda de descida'],
  ['GPIO 21', 'LM393 do nível do magazine (OUT)', 'magazine cheio'],
  ['GPIO 4', 'botão do jogador (NA da microchave; COM no GND)', 'INPUT_PULLUP + RC 10 kΩ/100 nF'],
  ['GPIO 18', 'MOSFET do solenoide de soltura (SIG)', 'pulso de 50 ms'],
  ['GPIO 19', 'MOSFET do solenoide da comporta (SIG)', ''],
  ['GPIO 22', 'MOSFET do motor do elevador (SIG)', ''],
  ['GPIO 23', 'IRF520 do LED do botão (SIG)', 'carga pequena: o IRF520 dá conta'],
  ['GPIO 13', 'servo SG90 do escapement (laranja)', 'PWM 50 Hz'],
  ['Base driver A → NEMA A', 'A1 A2 B1 B2', 'ache os pares com multímetro: bobina = ~2 Ω entre os fios'],
];

export function moduloEletronica() {
  const I = instancias();
  const ids = pre => I.filter(i => i.id.startsWith(pre)).map(i => i.id);
  const de = id => [id, ...ids('esp_' + id + '_'), ...ids('p_' + id + '_')];
  return {
    id: 'eletronica', nome: 'Eletrônica',
    subtitulo: 'Placa de montagem com ESP32, drivers, MOSFETs e comparadores. Ligações pino a pino.',
    resumo: 'ESP32 DevKit, 2 TMC2209 em placas base, 3 MOSFETs de nível lógico + 1 IRF520, 2 comparadores LM393, conversor 12→5 V, fonte e botão.',
    tempo: '≈ 3 h (com a fiação)',
    instancias: I,
    passos: [
      { titulo: 'Conheça as peças', mostra: 'tudo', explode: 0.4, vista: 'iso',
        texto: 'Tudo numa placa de MDF de 300 × 200 que vai na prateleira de lógica do pedestal. Embaixo dela (aqui à frente), a fonte de 12 V; o botão do jogador vai no painel da frente.',
        atencao: ['Os módulos IRF520 da planilha não ligam direito com os 3,3 V do ESP32: use os MOSFETs de nível lógico ("falta comprar") nos 2 solenoides e no motor. O IRF520 fica só para o LED do botão.',
          'O ESP32 precisa de 5 V: falta o conversor LM2596 (12 → 5 V).'] },
      { titulo: 'Fonte e terra', novos: ['fonte'], vista: 'iso',
        texto: 'Prenda a fonte no piso do pedestal pelos furos de baixo. Ligue a tomada em L e N, e o fio verde/amarelo no ⏚ — e o mesmo terra numa parte metálica do gabinete.',
        atencao: ['Fonte DESLIGADA da tomada enquanto mexe nos bornes: há 220 V expostos.'] },
      { titulo: 'Espaçadores e conversor 5 V', novos: [...de('buck')], base: ['placa'], vista: 'cima',
        texto: 'Marque e fure (2,5 mm) a placa de MDF onde vão os módulos. Monte o LM2596 sobre 2 espaçadores com M3×16. Ligue SÓ ele na fonte e gire o trimpot até o multímetro marcar 5,0 V na saída.',
        ferramentas: ['furadeira + broca 2,5 mm', 'chave allen 2,5 mm', 'multímetro'],
        confira: ['5,0 V na saída do LM2596 com a fonte ligada.'] },
      { titulo: 'ESP32', novos: de('esp32'), vista: 'cima',
        texto: 'ESP32 sobre 4 espaçadores, parafusos M2×10 nos furos dos cantos. Deixe o conector USB virado para a borda da placa: é por ele que você grava o firmware.',
        ferramentas: ['chave Phillips pequena'] },
      { titulo: 'Drivers dos motores', novos: [...de('drv_a'), ...de('drv_b'), 'tmc_a', 'tmc_b'], vista: 'iso',
        texto: 'Monte as 2 placas base (eixo A à esquerda, eixo B à direita). Microchaves todas DESLIGADAS. Encaixe o TMC2209 com o trimpot virado para o lado oposto ao borne do motor. Com 12 V ligado e motor DESCONECTADO, gire o trimpot até medir 1,2 V entre ele e o GND (corrente ≈1,7 A do 17HS4401).',
        ferramentas: ['multímetro', 'chave de fenda cerâmica ou pequena'],
        atencao: ['Nunca ligue/desligue o cabo do motor com o driver energizado: queima o TMC2209.'] },
      { titulo: 'MOSFETs', novos: [...de('mos_sol'), ...de('mos_comp'), ...de('mos_elev'), ...de('mos_led')], vista: 'cima',
        texto: 'Da esquerda para a direita: soltura, comporta, motor do elevador (os 3 de nível lógico) e o IRF520 do LED do botão. Em cada solenoide e no motor, solde um diodo 1N4007 em paralelo nos terminais DA CARGA, com a faixa do lado do +12 V.',
        ferramentas: ['ferro de solda', 'chave allen 2,5 mm'],
        atencao: ['Diodo ao contrário = curto na hora de ligar. A faixa vai no +.'] },
      { titulo: 'Comparadores dos sensores', novos: [...de('cmp_boca'), ...de('cmp_nivel')], vista: 'cima',
        texto: 'Os 2 LM393: um para a barreira da boca, outro para o nível do magazine. Alimente em 3,3 V. Fototransistor TIL78: coletor no IN do módulo, emissor no GND. LED IR333C: + no 5 V por um resistor de 150 Ω, − no GND.',
        ferramentas: ['ferro de solda'] },
      { titulo: 'Ligações pino a pino', vista: 'cima', tabela: LIGACOES,
        texto: 'Faça uma ligação de cada vez, conferindo com a tabela, e marque com fita cada fio nas duas pontas. Use fio de 1 mm² nos 12 V de potência e jumper Dupont no resto.',
        confira: ['Antes de ligar a fonte: multímetro em continuidade entre 12 V e GND — NÃO pode apitar.'] },
      { titulo: 'Botão do jogador', novos: ['botao'], vista: 'frente',
        texto: 'Furo de 25 mm no painel da frente (confira se a rosca do seu botão é M24 ou Ø28). Aperte a porca por trás. Microchave: COM no GND, NA no GPIO 4. LED do botão: + no 12 V, − na saída do IRF520.',
        ferramentas: ['serra-copo 25 mm'] },
    ],
  };
}
