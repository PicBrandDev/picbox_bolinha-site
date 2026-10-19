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
const F4 = [[-17.5, 15.5], [17.5, 15.5], [-17.5, -15.5], [17.5, -15.5]];
export const LAYOUT = [
  ['esp32', 'esp32', -100, 45, [[-23.7, 11.9], [23.7, 11.9], [-23.7, -11.9], [23.7, -11.9]]],
  ['drv_a', 'base_driver', -30, 50, F4],
  ['drv_b', 'base_driver', 20, 50, F4],
  ['drv_e', 'base_driver', 70, 50, F4],                         // 3o motor: o NEMA do elevador
  ['buck', 'buck_lm2596', 122, 55, [[-17.5, 7.5], [17.5, -7.5]]],
  ['mos_sol', 'mosfet_logico', -110, -35, [[-14, 5.5], [-14, -5.5]]],
  ['mos_comp', 'mosfet_logico', -65, -35, [[-14, 5.5], [-14, -5.5]]],
  ['mos_led', 'irf520', -15, -35, [[-13, 9], [-13, -9]]],
  ['cmp_boca', 'lm393', 60, -30, [[-13, 0]]],
  ['cmp_nivel', 'lm393', 60, -65, [[-13, 0]]],
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
  ['drv_a', 'drv_b', 'drv_e'].forEach(d => { const l = LAYOUT.find(q => q[0] === d); add('tmc_' + d.slice(-1), 'tmc2209', r.t(l[2] - 2, l[3], H + 1.6 + 8.5 + 3)); });
  // fonte e botao, fora da placa (so para conhecer)
  add('fonte', 'fonte_12v', r.t(0, -190, -6));
  add('botao', 'botao_arcade', r.rx(90).t(0, -320, 60));
  return I;
}

/* ---------------------------------------------------------------- tabela de ligacoes */
export const LIGACOES = [
  ['Fonte V+ (12 V)', 'bornes 12 V das 3 bases de driver, + dos 3 MOSFET, + do LED do botão, entrada IN+ do LM2596', 'fio 1 mm² vermelho'],
  ['Fonte V− (GND)', 'GND de TUDO (bases, MOSFET, LM2596 IN−, ESP32 GND, sensores)', 'fio 1 mm² preto — um só ponto de terra'],
  ['LM2596 OUT+ (5,0 V)', 'ESP32 VIN, servo SG90 (vermelho), LEDs IR (via 150 Ω)', 'ajuste 5,0 V antes de ligar'],
  ['ESP32 3V3', 'VIO das 3 bases de driver, VCC dos 2 LM393, + dos 3 fins de curso mecânicos', 'NUNCA 5 V: os GPIO 34/35/39 não aguentam'],
  ['GPIO 25 / 26', 'STEP / DIR do eixo A (bola)', ''],
  ['GPIO 32 / 33', 'STEP / DIR do eixo B (buraco)', ''],
  ['GPIO 14 / 17', 'STEP / DIR do motor do elevador', 'EN no 27 também: na partida o 14 pisca, mas os motores estão desligados'],
  ['GPIO 27', 'EN das 3 bases (liga/desliga os motores)', 'nível baixo = motores ligados'],
  ['GPIO 34', 'fim de curso do eixo A (direita)', 'entrada sem pull-up interno: o resistor da placa do fim de curso faz esse papel'],
  ['GPIO 35 / 39', 'fins de curso do eixo B (esquerda / direita)', 'idem: só com a placa (microchave solta precisa de 10 kΩ para 3,3 V)'],
  ['GPIO 36', 'LM393 da boca (OUT)', 'acerto: borda de descida'],
  ['GPIO 21', 'LM393 do nível do magazine (OUT)', 'magazine cheio'],
  ['GPIO 4', 'botão do jogador (NA da microchave; COM no GND)', 'INPUT_PULLUP + RC 10 kΩ/100 nF'],
  ['GPIO 18', 'MOSFET do solenoide de soltura (SIG)', 'pulso de 50 ms'],
  ['GPIO 19', 'MOSFET do solenoide da comporta (SIG)', ''],
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
    resumo: 'ESP32 DevKit, 3 TMC2209 em placas base (eixos A, B e elevador), 2 MOSFETs de nível lógico + 1 IRF520, 2 comparadores LM393, conversor 12→5 V, fonte e botão.',
    tempo: '≈ 3 h (com a fiação)',
    instancias: I,
    passos: [
      { titulo: 'Conheça as peças', mostra: 'tudo', explode: 0.4, vista: 'iso',
        texto: 'Tudo numa placa de MDF de 300 × 200 que vai na prateleira de lógica do pedestal. Embaixo dela (aqui à frente), a fonte de 12 V; o botão do jogador vai no painel da frente.',
        atencao: ['Os módulos IRF520 da planilha não ligam direito com os 3,3 V do ESP32: use os MOSFETs de nível lógico ("falta comprar") nos 2 solenoides. O IRF520 fica só para o LED do botão.',
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
      { titulo: 'Drivers dos motores', novos: [...de('drv_a'), ...de('drv_b'), ...de('drv_e'), 'tmc_a', 'tmc_b', 'tmc_e'], vista: 'iso',
        texto: 'Monte as 3 placas base (da esquerda para a direita: eixo A, eixo B, elevador). Microchaves todas DESLIGADAS. Encaixe o TMC2209 com o trimpot virado para o lado oposto ao borne do motor. Com 12 V ligado e motor DESCONECTADO, gire o trimpot até medir 1,2 V entre ele e o GND (corrente ≈1,7 A do 17HS4401).',
        ferramentas: ['multímetro', 'chave de fenda cerâmica ou pequena'],
        atencao: ['Nunca ligue/desligue o cabo do motor com o driver energizado: queima o TMC2209.'] },
      { titulo: 'MOSFETs', novos: [...de('mos_sol'), ...de('mos_comp'), ...de('mos_led')], vista: 'cima',
        texto: 'Da esquerda para a direita: soltura, comporta (os 2 de nível lógico) e o IRF520 do LED do botão. Em cada solenoide, solde um diodo 1N4007 em paralelo nos terminais DO SOLENOIDE, com a faixa do lado do +12 V.',
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

/* ================================================================ LIGACOES EM 3D
   A placa de eletronica no centro e cada componente da maquina em volta, ligados por
   cabos coloridos pela funcao. Clicar num cabo abre os fios um a um; num modulo, a
   explicacao completa dele. As posicoes sao de bancada (didaticas), nao as da maquina. */
const COR_C = { v12: '#d9342b', v5: '#ff8c1a', v33: '#e8c81a', sinal: '#2b8fe0', motor: '#2fa84f', sensor: '#9b59d0', gnd: '#333333' };
const L_ = id => LAYOUT.find(l => l[0] === id);
const at_ = (id, dx, dy, dz) => { const l = L_(id); return [l[2] + dx, l[3] + dy, dz === undefined ? 14 : dz]; };
// pinos do ESP32 DevKit V1 (30 pinos), na ordem da placa, da antena (+x) para o USB (-x)
const ESQ = ['EN', 36, 39, 34, 35, 32, 33, 25, 26, 27, 14, 12, 13, 'GND', 'VIN'];
const DIR = [23, 22, 'TX0', 'RX0', 21, 19, 18, 5, 17, 16, 4, 2, 15, 'GND2', '3V3'];
function pino(g) {
  const l = L_('esp32'); let i = ESQ.indexOf(g), y = l[3] - 12.7;
  if (i < 0) { i = DIR.indexOf(g); y = l[3] + 12.7; }
  return [l[2] + 17.78 - i * 2.54, y, 13];
}
const SAT = {
  nema_a: [-300, 125], nema_b: [-300, 30], nema_e: [-300, -65],
  sol_solt: [-210, -200], sol_comp: [-130, -200], servo: [-50, -195], botao: [30, -210],
  fonte: [190, -230], ir_boca_led: [240, -95], ir_boca_foto: [240, -35], ir_nivel_led: [310, -95], ir_nivel_foto: [310, -35],
  fc_a: [-130, 210], fc_b1: [-50, 210], fc_b2: [30, 210],
};
function rota(a, b, h, meio) {
  const m = meio || [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  return [a, [a[0], a[1], h * 0.7], [m[0], m[1], h], [b[0], b[1], h * 0.7], b];
}
const S_ = (id, dz) => [SAT[id][0], SAT[id][1], dz === undefined ? 10 : dz];

function cabos() {
  const C = [];
  const cb = o => C.push(Object.assign({ raio: 2.2 }, o));
  const FONTE = [SAT.fonte[0] - 96, SAT.fonte[1], 22];
  // ---------------- 12 V
  [['drv_a', 'eixo A'], ['drv_b', 'eixo B'], ['drv_e', 'elevador']].forEach(([d, n], i) => cb({
    id: 'c12_' + d, grupo: '12v', nome: `12 V → driver do ${n}`, rotulo: '12 V', cor: COR_C.v12, rotuloEm: 0.75,
    de: 'Fonte (V+ / V−)', para: `Placa base do driver do ${n} (borne VM / GND)`, bitola: '1 mm² (AWG 18), par vermelho + preto',
    funcao: 'Alimenta o motor de passo. O TMC2209 pega esses 12 V e controla a corrente que vai para as bobinas.',
    como: 'Corrente contínua. O motor puxa até ~1,7 A nos picos; o capacitor de 100 µF da placa base segura os picos curtos.',
    cuidado: 'Inverter + e − queima o driver na hora. Confira com o multímetro antes de encaixar o TMC2209.',
    fios: [['#d9342b', 'vermelho', 'Fonte V+', 'borne VM da base', '+12 V'], ['#222', 'preto', 'Fonte V−', 'borne GND da base', 'terra comum']],
    pts: rota(FONTE, at_(d, 15, -12, 16), 70 + i * 6, [60, -140 + i * 8]) }));
  [['mos_sol', 'MOSFET da soltura'], ['mos_comp', 'MOSFET da comporta'], ['mos_led', 'IRF520 do LED']].forEach(([d, n], i) => cb({
    id: 'c12_' + d, grupo: '12v', nome: `12 V → ${n}`, rotulo: '12 V', cor: COR_C.v12, rotuloEm: 0.7,
    de: 'Fonte (V+ / V−)', para: `${n} (borne de entrada)`, bitola: '1 mm² (AWG 18)',
    funcao: 'A energia que o MOSFET entrega para a carga (solenoide ou LED) quando o ESP32 manda.',
    fios: [['#d9342b', 'vermelho', 'Fonte V+', 'borne + do módulo', '+12 V'], ['#222', 'preto', 'Fonte V−', 'borne − do módulo', 'terra']],
    pts: rota(FONTE, at_(d, 11, 0, 16), 55 + i * 5, [20 - i * 30, -150]) }));
  cb({ id: 'c12_buck', grupo: '12v', nome: '12 V → conversor LM2596', rotulo: '12 V', cor: COR_C.v12, rotuloEm: 0.6,
    de: 'Fonte (V+ / V−)', para: 'LM2596 (IN+ / IN−)', bitola: '0,5 mm²',
    funcao: 'Entrada do conversor que gera os 5 V da lógica.',
    fios: [['#d9342b', 'vermelho', 'Fonte V+', 'IN+', '+12 V'], ['#222', 'preto', 'Fonte V−', 'IN−', 'terra']],
    pts: rota(FONTE, at_('buck', -20, 0), 50, [150, -60]) });
  // ---------------- 5 V e 3,3 V
  cb({ id: 'c5_esp', grupo: 'logica', nome: '5 V → ESP32', rotulo: '5 V', cor: COR_C.v5,
    de: 'LM2596 (OUT+ / OUT−)', para: 'ESP32 (VIN / GND)', bitola: 'jumper Dupont',
    funcao: 'Alimenta o ESP32. O regulador da própria placa baixa para 3,3 V.',
    cuidado: 'Ajuste o LM2596 para 5,0 V ANTES de ligar este fio. Com 12 V aqui, o ESP32 queima.',
    fios: [['#ff8c1a', 'laranja', 'LM2596 OUT+', 'ESP32 VIN', '+5 V'], ['#222', 'preto', 'LM2596 OUT−', 'ESP32 GND', 'terra']],
    pts: rota(at_('buck', 20, 0), pino('VIN'), 45, [10, 90]) });
  ['drv_a', 'drv_b', 'drv_e'].forEach((d, i) => cb({
    id: 'c33_' + d, grupo: 'logica', nome: `3,3 V → lógica do driver ${['A', 'B', 'do elevador'][i]}`, rotulo: '3,3 V', cor: COR_C.v33, raio: 1.1, rotuloEm: 0.8,
    de: 'ESP32 3V3', para: 'VIO da placa base', bitola: 'jumper Dupont',
    funcao: 'Diz ao TMC2209 em que tensão estão os sinais STEP/DIR/EN (3,3 V do ESP32).',
    fios: [['#e8c81a', 'amarelo', 'ESP32 3V3', 'VIO', '+3,3 V'], ['#222', 'preto', 'ESP32 GND', 'GND', 'terra']],
    pts: rota(pino('3V3'), at_(d, -18, -12, 12), 30 + i * 4) }));
  // ---------------- controle dos motores
  [['drv_a', 25, 26, 'eixo A (bola)'], ['drv_b', 32, 33, 'eixo B (buraco)'], ['drv_e', 14, 17, 'elevador']].forEach(([d, st, dr, n], i) => cb({
    id: 'cs_' + d, grupo: 'motor', nome: `STEP / DIR / EN → driver do ${n}`, rotulo: `GPIO ${st}/${dr}/27`, cor: COR_C.sinal, raio: 1.2, rotuloEm: 0.55,
    de: `ESP32 GPIO ${st}, ${dr} e 27`, para: 'STEP, DIR e EN da placa base', bitola: 'jumper Dupont (3 fios)',
    funcao: `Comando do motor do ${n}: cada pulso em STEP anda 1/8 de passo; DIR escolhe o sentido; EN liga/desliga.`,
    como: 'O ESP32 gera os pulsos num timer de hardware (não no laço do programa): a velocidade fica exata mesmo com o resto do código rodando.',
    fios: [['#2b8fe0', 'azul', `GPIO ${st}`, 'STEP', 'pulsos (até ~20 kHz)'], ['#7fb3e6', 'azul claro', `GPIO ${dr}`, 'DIR', 'nível: sentido'], ['#5b6670', 'cinza', 'GPIO 27', 'EN', 'baixo = motor ligado (comum aos 3)']],
    pts: rota(pino(st), at_(d, -12, -18, 12), 22 + i * 4) }));
  [['drv_a', 'nema_a', 'eixo A'], ['drv_b', 'nema_b', 'eixo B'], ['drv_e', 'nema_e', 'elevador']].forEach(([d, m, n], i) => cb({
    id: 'cm_' + d, grupo: 'motor', nome: `Motor do ${n}`, rotulo: `NEMA ${n}`, cor: COR_C.motor, raio: 2,
    de: 'Placa base (A1 A2 B1 B2)', para: `NEMA 17 do ${n}`, bitola: 'cabo do motor (6 vias JST-PH, 4 usadas)',
    funcao: 'Leva a corrente para as duas bobinas do motor de passo.',
    como: 'O driver alterna a corrente nas bobinas A e B em degraus: o campo magnético gira e o rotor acompanha, passo a passo.',
    cuidado: 'Ache os pares com o multímetro (~2 Ω na mesma bobina). Par trocado: o motor só vibra. Nunca desconecte com o driver ligado.',
    fios: [['#111', 'preto', 'A1 (A+)', 'bobina A', 'corrente da bobina A'], ['#2fa84f', 'verde', 'A2 (A−)', 'bobina A', ''],
      ['#d9342b', 'vermelho', 'B1 (B+)', 'bobina B', 'corrente da bobina B'], ['#2b6fe0', 'azul', 'B2 (B−)', 'bobina B', '']],
    pts: rota(at_(d, 15, 5, 16), [SAT[m][0] + 24, SAT[m][1], 8], 60 - i * 6, [-200, SAT[m][1] + 20]) }));
  // ---------------- solenoides
  [['mos_sol', 18, 'sol_solt', 'soltura (JF-0826B)', '50 ms por jogada'], ['mos_comp', 19, 'sol_comp', 'comporta (JF-0530B)', '~3 s por carga']].forEach(([d, g, s, n, tempo]) => {
    cb({ id: 'cg_' + d, grupo: 'sol', nome: `Comando do MOSFET da ${n.split(' ')[0]}`, rotulo: `GPIO ${g}`, cor: COR_C.sinal, raio: 1.1,
      de: `ESP32 GPIO ${g}`, para: 'SIG do MOSFET', bitola: 'jumper Dupont',
      funcao: `Quando o GPIO ${g} vai a 3,3 V, o MOSFET conduz e o solenoide liga (${tempo}).`,
      fios: [['#2b8fe0', 'azul', `GPIO ${g}`, 'SIG', '3,3 V = ligado'], ['#222', 'preto', 'GND', 'GND', 'referência']],
      pts: rota(pino(g), at_(d, -9, 0, 12), 26) });
    cb({ id: 'cl_' + d, grupo: 'sol', nome: `Solenoide da ${n}`, rotulo: n.split(' ')[0], cor: COR_C.v12, raio: 1.6,
      de: 'saída do MOSFET', para: `solenoide da ${n}`, bitola: '0,5 mm² + diodo 1N4007 no solenoide',
      funcao: 'Liga a bobina do solenoide.',
      como: 'Na hora de desligar, a bobina gera um pico de tensão; o diodo 1N4007, soldado nos terminais do solenoide com a faixa no +, dá caminho a essa energia e protege o MOSFET.',
      cuidado: 'Diodo invertido = curto-circuito na hora de ligar.',
      fios: [['#d9342b', 'vermelho', 'OUT+ do módulo', 'terminal + do solenoide', '+12 V'], ['#222', 'preto', 'OUT− do módulo', 'terminal − do solenoide', 'chaveado pelo MOSFET']],
      pts: rota(at_(d, 11, 0, 16), S_(s, 26), 40) });
  });
  // ---------------- servo e botao
  cb({ id: 'c_servo', grupo: 'outros', nome: 'Servo SG90 do escapement', rotulo: 'servo', cor: COR_C.v5, raio: 1.3,
    de: 'ESP32 GPIO 13 + LM2596 5 V', para: 'SG90', bitola: 'cabo do servo (3 vias)',
    funcao: 'Comanda o ângulo do balancim do escapement.',
    como: 'Pulso de 1 a 2 ms, 50 vezes por segundo: 1,5 ms = centro; ±0,13 ms ≈ ±12°.',
    cuidado: 'O + do servo vai no LM2596 (5 V), não no 3V3 do ESP32: na partida ele puxa até 0,5 A.',
    fios: [['#ff8c1a', 'laranja', 'GPIO 13', 'sinal', 'PWM 50 Hz'], ['#d9342b', 'vermelho', 'LM2596 5 V', '+', '+5 V'], ['#6b3a1e', 'marrom', 'GND', '−', 'terra']],
    pts: rota(pino(13), S_('servo', 6), 35) });
  cb({ id: 'c_botao', grupo: 'outros', nome: 'Botão do jogador', rotulo: 'GPIO 4', cor: COR_C.sinal, raio: 1.3,
    de: 'ESP32 GPIO 4 / GND', para: 'microchave do botão (NA / COM)', bitola: 'par trançado (fica longe da fonte)',
    funcao: 'O comando do jogador: dispara a soltura.',
    como: 'GPIO 4 com pull-up: solto = 3,3 V; apertado, a chave liga ao GND = 0 V. A borda de descida gera uma interrupção que liga o solenoide em microssegundos. Filtro RC (10 kΩ + 100 nF) tira o repique da chave.',
    fios: [['#2b8fe0', 'azul', 'GPIO 4', 'NA da microchave', 'apertado = 0 V'], ['#222', 'preto', 'GND', 'COM da microchave', 'terra']],
    pts: rota(pino(4), S_('botao', 12), 48, [0, -80]) });
  cb({ id: 'c_led', grupo: 'outros', nome: 'LED do botão', rotulo: 'LED', cor: COR_C.v12, raio: 1.2,
    de: 'IRF520 (saída) / Fonte 12 V', para: 'LED do botão', bitola: '0,5 mm²',
    funcao: 'Acende o botão (atração e "pode jogar").', fios: [['#d9342b', 'vermelho', 'Fonte 12 V', 'LED +', '+12 V'], ['#222', 'preto', 'OUT− do IRF520', 'LED −', 'chaveado (GPIO 23)']],
    pts: rota(at_('mos_led', 11, -5, 16), S_('botao', 20), 30) });
  // ---------------- sensores
  [['boca', 'cmp_boca', 36, 'barreira da boca (acerto)'], ['nivel', 'cmp_nivel', 21, 'nível do magazine (cheio)']].forEach(([n, c, g, desc]) => {
    cb({ id: 'ci_' + n, grupo: 'sensores', nome: `Barreira IR — ${desc}`, rotulo: `IR ${n}`, cor: COR_C.sensor, raio: 1.3,
      de: `LED IR333C + fototransistor TIL78 (${n})`, para: `comparador LM393 (${n})`, bitola: '4 fios finos, blindado se passar perto dos motores',
      funcao: `Feixe infravermelho atravessando o caminho da bola: ${desc}.`,
      como: 'O LED fica sempre aceso. O TIL78 conduz enquanto recebe luz; a bola faz sombra, ele para de conduzir e a tensão no IN do LM393 sobe. O LM393 compara com o trimpot e vira a saída — sinal digital limpo.',
      fios: [['#ff8c1a', 'laranja', 'LM2596 5 V', '150 Ω → LED +', 'LED ~20 mA'], ['#222', 'preto', 'GND', 'LED − e emissor do TIL78', 'terra'],
        ['#9b59d0', 'roxo', 'coletor do TIL78', 'IN do LM393', 'cai quando a bola corta o feixe']],
      pts: rota(S_('ir_' + n + '_foto', 10), at_(c, 15, 0, 12), 28) });
    cb({ id: 'co_' + n, grupo: 'sensores', nome: `Saída do LM393 (${n}) → ESP32`, rotulo: `GPIO ${g}`, cor: COR_C.sensor, raio: 1.1,
      de: `LM393 (${n}) OUT`, para: `ESP32 GPIO ${g}`, bitola: 'jumper Dupont',
      funcao: `Leva o evento "${desc}" para o ESP32.`, fios: [['#9b59d0', 'roxo', 'OUT', `GPIO ${g}`, 'digital 3,3 V'], ['#e8c81a', 'amarelo', 'ESP32 3V3', 'VCC', '+3,3 V'], ['#222', 'preto', 'GND', 'GND', 'terra']],
      pts: rota(at_(c, 15, 0, 12), pino(g), 20) });
  });
  [['fc_a', 34, 'eixo A (direita)'], ['fc_b1', 35, 'eixo B (esquerda)'], ['fc_b2', 39, 'eixo B (direita)']].forEach(([f, g, n]) => cb({
    id: 'cf_' + f, grupo: 'sensores', nome: `Fim de curso ${n}`, rotulo: `GPIO ${g}`, cor: COR_C.sensor, raio: 1.2,
    de: `fim de curso mecânico ${n}`, para: `ESP32 GPIO ${g}`, bitola: 'cabo de 3 vias com conector (vem com o módulo; emende se não chegar)',
    funcao: 'Avisa quando o batente do carro aperta a alavanca da microchave — a 143 mm do centro, 3 mm além do curso de jogo.',
    como: 'Ao ligar, cada carro vai devagar até o clique: ali é o zero. Depois, na volta para a posição de espera, o carro encosta de novo devagar e o firmware compara a contagem de passos com a esperada. Diferença = passo perdido: ele corrige e registra no log.',
    cuidado: 'Ligue o + no 3,3 V, nunca no 5 V. Confira com o multímetro qual nível o S dá apertado e solto antes de escrever o firmware (varia entre placas).',
    fios: [['#e8c81a', 'amarelo', 'ESP32 3V3', '+', '+3,3 V (saída já no nível do ESP32)'], ['#222', 'preto', 'GND', '−', 'terra'], ['#9b59d0', 'roxo', `GPIO ${g}`, 'S', 'muda quando a alavanca clica']],
    pts: rota(S_(f, 6), pino(g), 26) }));
  return C;
}

function satelites() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  const r = T.of();
  ['nema_a', 'nema_b', 'nema_e'].forEach(m => add(m, 'nema17', r.t(SAT[m][0], SAT[m][1], 40)));
  add('sol_solt', 'sol_jf0826', r.ry(90).t(SAT.sol_solt[0] - 13, SAT.sol_solt[1], 13));
  add('sol_comp', 'sol_jf0530', r.ry(90).t(SAT.sol_comp[0] - 15, SAT.sol_comp[1], 7));
  add('servo', 'sg90', r.t(SAT.servo[0], SAT.servo[1], 0));
  add('botao', 'botao_arcade', r.t(SAT.botao[0], SAT.botao[1], 52.4));
  add('fonte', 'fonte_12v', r.t(SAT.fonte[0], SAT.fonte[1], 0));
  ['boca', 'nivel'].forEach(n => {
    add('ir_' + n + '_led', 'ir333c', r.rx(-90).t(SAT['ir_' + n + '_led'][0], SAT['ir_' + n + '_led'][1], 10));
    add('ir_' + n + '_foto', 'til78', r.rx(90).t(SAT['ir_' + n + '_foto'][0], SAT['ir_' + n + '_foto'][1], 10));
  });
  ['fc_a', 'fc_b1', 'fc_b2'].forEach(f => add(f, 'fc_mecanico', r.t(SAT[f][0], SAT[f][1], 0)));
  return I;
}

export function moduloLigacoes() {
  const placa = instancias().filter(i => i.id !== 'fonte' && i.id !== 'botao' && !i.id.startsWith('p_'));
  const I = placa.concat(satelites());
  const C = cabos();
  const grupo = g => C.filter(c => c.grupo === g).map(c => c.id);
  return {
    id: 'ligacoes', nome: 'Ligações e cabos', didatico: true,
    subtitulo: 'Cada cabo da máquina, colorido pela função. Clique num cabo ou num módulo.',
    resumo: 'Mapa 3D das ligações: energia, lógica, motores, solenoides e sensores — com a explicação de cada fio e de cada módulo.',
    tempo: 'mapa de bancada',
    instancias: I,
    cabos: C,
    passos: [
      { titulo: 'O mapa completo', mostra: 'tudo', cabos: true, vista: 'cima',
        texto: 'A placa de eletrônica no meio e tudo o que ela comanda em volta (posições de bancada, não as da máquina). Cores: <b style="color:#d9342b">vermelho</b> 12 V, <b style="color:#ff8c1a">laranja</b> 5 V, <b style="color:#e8c81a">amarelo</b> 3,3 V, <b style="color:#2b8fe0">azul</b> comandos, <b style="color:#2fa84f">verde</b> motores, <b style="color:#9b59d0">roxo</b> sensores. <b>Clique em qualquer cabo</b> para ver os fios, um a um; em qualquer módulo para ver como ele funciona.' },
      { titulo: '1. Energia: 12 V', mostra: 'tudo', cabos: grupo('12v'), vista: 'iso', zoom: ['fonte', 'placa'],
        texto: 'A fonte alimenta direto o que precisa de força: os 3 drivers de motor, os 2 MOSFETs dos solenoides, o LED do botão e o conversor de 5 V. Todos os GND (−) se encontram num ponto só.' },
      { titulo: '2. Lógica: 5 V e 3,3 V', mostra: 'tudo', cabos: grupo('logica'), vista: 'cima', zoom: ['placa'],
        texto: 'O LM2596 baixa para 5 V e alimenta o ESP32. Do ESP32 sai 3,3 V para a lógica dos drivers e para os sensores: assim todo sinal que volta para o ESP32 já vem em 3,3 V.' },
      { titulo: '3. Motores', mostra: 'tudo', cabos: grupo('motor'), vista: 'iso', zoom: ['placa', 'nema_a', 'nema_e'],
        texto: 'Para cada motor, 3 fios de comando (STEP, DIR, EN) do ESP32 até o driver, e o cabo de 4 fios do driver até o motor.' },
      { titulo: '4. Solenoides', mostra: 'tudo', cabos: grupo('sol'), vista: 'iso', zoom: ['mos_sol', 'sol_solt', 'sol_comp'],
        texto: 'O ESP32 não aguenta 2 A: ele só "avisa" o MOSFET (fio azul), e o MOSFET liga os 12 V no solenoide (fio vermelho). O diodo fica soldado no próprio solenoide.' },
      { titulo: '5. Sensores', mostra: 'tudo', cabos: grupo('sensores'), vista: 'iso', zoom: ['cmp_boca', 'ir_nivel_led', 'fc_a', 'fc_b2'],
        texto: 'Barreiras infravermelhas (boca e nível do magazine) passam por um comparador LM393 antes do ESP32. Os fins de curso mecânicos já saem digitais e vão direto.' },
      { titulo: '6. Botão e servo', mostra: 'tudo', cabos: grupo('outros'), vista: 'iso', zoom: ['botao', 'servo', 'esp32'],
        texto: 'O botão vai num pino com interrupção (GPIO 4): é o caminho mais curto entre o dedo e o solenoide. O servo do escapement recebe 5 V do conversor e o sinal do GPIO 13.' },
    ],
  };
}
