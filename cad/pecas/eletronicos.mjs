/* Modulos eletronicos e sensores. Origem de toda PCB: centro da placa, face de BAIXO
   em z=0, componentes para +z. Furos e conectores pelas cotas do fabricante/anuncio. */
import { R, caixa, caixaC, cil, cilC, tubo, uniao, corta } from '../lib/base.mjs';
import { peca } from '../lib/registro.mjs';
import { LINK } from './comprados.mjs';

const E = 1.6;   // espessura padrao de PCB
function pcb(w, d, furos, cor) {
  let p = caixa(-w / 2, -d / 2, 0, w / 2, d / 2, E);
  (furos || []).forEach(f => { p = p.cut(cilC(f[2], 4, [f[0], f[1], E / 2], 'z')); });
  return { forma: p, cor: cor || 'pcbAzul' };
}
// barra de pinos 2,54: n pinos ao longo de X, a partir do centro (x,y), para cima (ou para baixo)
function pinos(n, x, y, z, paraBaixo, eixo) {
  const passo = 2.54, l = [];
  const corpo = [];
  for (let i = 0; i < n; i++) {
    const px = eixo === 'y' ? x : x + (i - (n - 1) / 2) * passo;
    const py = eixo === 'y' ? y + (i - (n - 1) / 2) * passo : y;
    l.push(caixaC(px, py, paraBaixo ? z - 3 : z + 4, 0.64, 0.64, paraBaixo ? 6 : 8));
    corpo.push(caixaC(px, py, paraBaixo ? z - 1.25 : z + 1.25, 2.5, 2.5, 2.5));
  }
  return [{ forma: uniao(corpo), cor: 'preto' }, { forma: uniao(l), cor: 'latao' }];
}

/* ---------- AS5600: placa roxa quadrada vendida em pacote ---------- */
// 23 x 23, 2 furos a 17 mm entre centros na borda oposta ao conector, chip no centro
export const AS = { w: 23, d: 23, furo: 3.2, fx: 8.5, fy: 8.5, chipY: 0 };
peca('as5600', { nome: 'Encoder magnético AS5600 (módulo)', src: 'medir', dims: '23 × 23 × 1,6 mm, 2 furos a 17 mm',
  link: LINK.as5600, linha: 12,
  conferir: ['tamanho da placa e posição dos 2 furos', 'centro do chip em relação aos furos'],
  notas: ['O chip lê o ímã de frente, a 0,5–3 mm de distância. Centro do chip alinhado com o eixo: ±0,25 mm.',
    'Furos e tamanho variam entre fabricantes do mesmo anúncio — confira a sua placa antes de imprimir o suporte.'] },
() => {
  const placa = pcb(AS.w, AS.d, [[AS.fx, AS.fy, AS.furo], [-AS.fx, AS.fy, AS.furo]], 'pcbRoxo');
  const chip = { forma: caixaC(0, AS.chipY, E + 0.75, 5, 4, 1.5), cor: 'ic' };
  const cap = { forma: uniao([caixaC(-5, AS.chipY, E + 0.4, 1.6, 0.8, 0.8), caixaC(5, AS.chipY, E + 0.4, 1.6, 0.8, 0.8)]), cor: 'cobre' };
  return [placa, chip, cap, ...pinos(7, 0, -AS.d / 2 + 1.5, 0, true)];
});

/* ---------- fim de curso optico TCST2103 (placa de impressora 3D) ---------- */
export const TC = { w: 33, d: 10.5, furo: 3.2, fx: 9.5, fenda: 3.1, alt: 10.8, corpoC: 24.5, corpoL: 6.3 };
peca('tcst2103', { nome: 'Fim de curso óptico TCST2103 (placa)', src: 'medir', dims: '33 × 10,5 mm, fenda 3,1 mm, 3 pinos',
  link: LINK.tcst2103, linha: 27,
  conferir: ['tamanho da placa e distância entre furos', 'altura do sensor e largura da fenda'],
  notas: ['A bandeira do carro passa DENTRO da fenda sem encostar: 1 mm de folga para cada lado.'] },
() => {
  const placa = pcb(TC.w, TC.d, [[TC.fx, 0, TC.furo], [-TC.fx, 0, TC.furo]], 'pcbPreto');
  // Vishay doc 81147: bloco central de 11,9 com a fenda; abas de 3,1 com os furos a 19 mm
  let corpo = caixaC(0, 0, E + TC.alt / 2, 11.9, TC.corpoL, TC.alt);
  corpo = corpo.cut(caixaC(0, 0, E + TC.alt - 3.7, TC.fenda, TC.corpoL + 1, 7.5));
  let abas = caixaC(0, 0, E + 1.55, TC.corpoC, TC.corpoL, 3.1);
  [-1, 1].forEach(s => { abas = abas.cut(cilC(3.2, 5, [s * TC.fx, 0, E + 1.5], 'z')); });
  corpo = corpo.fuse(abas);
  const led = { forma: cilC(1.8, 1, [-13.5, 2.5, E + 0.5], 'z'), cor: 'vermelho' };
  return [placa, { forma: corpo, cor: 'ic' }, led, ...pinos(3, 14.2, 0, E, false, 'y')];
});

/* ---------- LED IR e fototransistor 5 mm ---------- */
function led5(cor) {
  // Everlight: 8,6 mm da face de baixo da aba ate o topo da cupula
  const corpo = cil(5, 5.1, [0, 0, 1], 'z').fuse(R.makeSphere(2.5).translate(0, 0, 6.1));
  const aba = cil(5.8, 1, [0, 0, 0], 'z').cut(caixa(2.4, -4, -1, 4, 4, 2));
  const pernas = uniao([caixaC(-1.27, 0, -10, 0.5, 0.5, 20), caixaC(1.27, 0, -12, 0.5, 0.5, 24)]);
  return [{ forma: corpo.fuse(aba), cor }, { forma: pernas, cor: 'zincado' }];
}
peca('ir333c', { nome: 'LED emissor IR333C 5 mm (940 nm)', dims: 'Ø5 × 8,6 mm, aba Ø5,8', link: LINK.ir333c, linha: 10,
  notas: ['Perna longa = ânodo (+). Liga em 5 V com resistor de 150 Ω (≈20 mA).', 'A luz é invisível: teste olhando pela câmera do celular.'] },
() => led5('ledIR'));
peca('til78', { nome: 'Fototransistor TIL78 5 mm', dims: 'Ø5 × 8,6 mm, aba Ø5,8', link: LINK.til78, linha: 10,
  notas: ['Perna curta = coletor (do lado do chanfro). Vai para o LM393, que transforma em sinal digital limpo.'] },
() => led5('fotoT'));

/* ---------- comparador LM393 (modulo de 3 pinos com trimpot) ---------- */
peca('lm393', { nome: 'Módulo comparador LM393 com trimpot', src: 'medir', dims: '32 × 14 mm, furo Ø3',
  link: LINK.lm393, linha: 26, conferir: ['tamanho e furo de fixação'],
  notas: ['O trimpot ajusta o limiar: com o feixe livre, gire até o LED do módulo apagar e volte 1/4 de volta.'] },
() => {
  const placa = pcb(32, 14, [[-13, 0, 3]], 'pcbAzul');
  const pot = { forma: caixaC(-3, 0, E + 2.5, 6.5, 6.5, 5).fuse(cilC(2.5, 1.5, [-3, 0, E + 5.5], 'z')), cor: 'pcbAzul' };
  const ic = { forma: caixaC(5, 0, E + 0.9, 5, 4, 1.6), cor: 'ic' };
  return [placa, pot, ic, ...pinos(4, 15, 0, E, false, 'y')];
});

/* ---------- driver de MOSFET IRF520 ---------- */
peca('irf520', { nome: 'Módulo driver MOSFET IRF520', src: 'medir', dims: '33 × 24 mm, 2 furos Ø3',
  link: LINK.irf520, linha: 7, conferir: ['tamanho e furos'],
  notas: ['Ligue o diodo de roda livre (1N4007) em paralelo com o solenoide, faixa do diodo no +12 V. O módulo não traz.',
    'O IRF520 com 3,3 V do ESP32 no gate conduz pouco: ver "Eletrônica" — o certo é um MOSFET de nível lógico (IRLZ44N).'] },
() => {
  const placa = pcb(33, 24, [[-13, 9, 3], [-13, -9, 3]], 'pcbRoxo');
  const tr = { forma: caixaC(4, 6, E + 4.5, 10, 4.5, 9).fuse(caixaC(4, 7.7, E + 11, 10, 1.3, 6)), cor: 'ic' };
  const borne = { forma: caixaC(11, -5, E + 5, 7.5, 10, 10), cor: 'pcbAzul' };
  return [placa, tr, borne, ...pinos(3, -14, -1, E, false, 'y')];
});

/* ---------- driver TMC2209 (stepstick) ---------- */
peca('tmc2209', { nome: 'Driver de passo TMC2209 V2.0 (stepstick)', src: 'cat', dims: '20 × 15 mm, 2 × 8 pinos espaçados 12,7',
  link: LINK.tmc2209, linha: 13,
  notas: ['Ajuste a corrente pelo trimpot (Vref) ANTES de ligar o motor: para o 17HS4401 (1,7 A) use Vref ≈ 1,2 V.',
    'Nunca conecte/desconecte o motor com o driver ligado: queima o driver.'] },
() => {
  const placa = pcb(15.24, 20.32, [], 'pcbVerde');
  const dis = { forma: caixaC(0, 0, E + 6, 9, 9, 8), cor: 'aluminio' };
  return [placa, dis, ...pinos(8, -6.35, 0, 0, true, 'y'), ...pinos(8, 6.35, 0, 0, true, 'y')];
});

/* ---------- ESP32 DevKit V1 (30 pinos) ---------- */
peca('esp32', { nome: 'ESP32 DevKit V1 (30 pinos)', src: 'medir', dims: '51,8 × 28,2 mm, fileiras a 25,4 mm, 4 furos Ø2,8',
  link: LINK.esp32, linha: 6, conferir: ['comprimento/largura da placa', 'distância entre as fileiras de pinos'],
  notas: ['Alimentação: 5 V no pino VIN (ou USB). Os GPIO são de 3,3 V: NUNCA ligue 5 V direto num GPIO.'] },
() => {
  const placa = pcb(51.8, 28.2, [[-23.7, 11.9, 2.8], [-23.7, -11.9, 2.8], [23.7, 11.9, 2.8], [23.7, -11.9, 2.8]], 'pcbPreto');
  const mod = { forma: caixaC(8, 0, E + 0.4, 25.5, 18, 0.8).fuse(caixaC(4.5, 0, E + 1.6, 16, 16, 2.4)), cor: 'aluminio' };
  const ant = { forma: caixaC(18, 0, E + 0.5, 6, 18, 1), cor: 'pcbPreto' };
  const usb = { forma: caixaC(-24.5, 0, E + 1.5, 6, 8, 3), cor: 'aluminio' };
  const bot = { forma: uniao([caixaC(-21, 9, E + 1, 3, 5, 2), caixaC(-21, -9, E + 1, 3, 5, 2)]), cor: 'preto' };
  return [placa, mod, ant, usb, bot, ...pinos(15, 0, 12.7, 0, true), ...pinos(15, 0, -12.7, 0, true)];
});

/* ---------- itens da eletronica que a planilha nao tem ---------- */
peca('buck_lm2596', { nome: 'Conversor DC-DC LM2596 (12 V → 5 V)', tipo: 'falta', src: 'medir', dims: '43 × 21 × 14 mm, 2 furos Ø3',
  link: 'https://lista.mercadolivre.com.br/regulador-tensao-lm2596',
  conferir: ['posição dos 2 furos (variam entre fabricantes)'],
  notas: ['Ajuste a saída para 5,0 V com o multímetro ANTES de ligar o ESP32 (trimpot azul).', 'Alimenta ESP32 (VIN), servo e LEDs IR.'] },
() => {
  const placa = pcb(43, 21, [[-17.5, 7.5, 3], [17.5, -7.5, 3]], 'pcbAzul');
  const indutor = { forma: caixaC(4, 0, E + 4, 12, 12, 8), cor: 'ic' };
  const caps = { forma: cil(8, 11, [-12, 3, E], 'z').fuse(cil(8, 11, [13, 3, E], 'z')), cor: 'ic' };
  const pot = { forma: caixaC(-5, -7, E + 5, 9.5, 4.8, 10), cor: 'pcbAzul' };
  return [placa, indutor, caps, pot];
});
peca('mosfet_logico', { nome: 'Módulo MOSFET de nível lógico (IRLZ44N ou AOD4184)', tipo: 'falta', src: 'medir', dims: '34 × 17 mm, 2 furos Ø3',
  link: 'https://lista.mercadolivre.com.br/modulo-mosfet-d4184',
  conferir: ['tamanho e furos'],
  notas: ['Conduz totalmente com 3,3 V no gate (o IRF520 da planilha precisa de ~10 V). Use para os 2 solenoides e o motor do elevador.',
    'Diodo 1N4007 em paralelo com cada carga, faixa no +12 V — protege o MOSFET do pico na hora de desligar.'] },
() => {
  const placa = pcb(34, 17, [[-14, 5.5, 3], [-14, -5.5, 3]], 'pcbVerde');
  const tr = { forma: caixaC(2, 0, E + 1.2, 6.5, 6, 2.4), cor: 'ic' };
  const borne = { forma: caixaC(11, 0, E + 5, 7.5, 15, 10), cor: 'pcbAzul' };
  return [placa, tr, borne, ...pinos(3, -9, 0, E, false, 'y')];
});
peca('base_driver', { nome: 'Placa base para driver de passo (com bornes e microchaves)', tipo: 'falta', src: 'medir', dims: '41 × 37 mm, 4 furos Ø3',
  link: 'https://lista.mercadolivre.com.br/placa-expansao-driver-a4988-drv8825',
  conferir: ['tamanho e furos'],
  notas: ['O TMC2209 encaixa nela; ela traz borne de 12 V, capacitor de 100 µF e conector do motor. Evita fiação solta no driver.',
    'Microchaves de passo: deixe todas DESLIGADAS (o TMC2209 fica em 1/8 de passo).'] },
() => {
  const placa = pcb(41, 37, [[-17.5, 15.5, 3], [17.5, 15.5, 3], [-17.5, -15.5, 3], [17.5, -15.5, 3]], 'pcbVerde');
  const soquete = { forma: caixaC(-2, 0, E + 4.25, 17.5, 20.5, 8.5).cut(caixaC(-2, 0, E + 6, 15, 18, 8)), cor: 'preto' };
  const borne = { forma: caixaC(15, -5, E + 5, 7.5, 20, 10), cor: 'pcbAzul' };
  const cap = { forma: cil(8, 11, [13, 11, E], 'z'), cor: 'ic' };
  return [placa, soquete, borne, cap];
});
peca('fonte_12v', { nome: 'Fonte chaveada 12 V 10 A (colmeia)', src: 'medir', link: LINK.fonte, linha: 17,
  dims: '199 × 98 × 38 mm (há versões de 160 e 130 mm)',
  conferir: ['comprimento (199, 160 ou 130 mm)', 'posição dos furos de baixo'],
  notas: ['Borne: L e N na tomada, ⏚ no terra do gabinete; V+ e V− saem os 12 V.', 'Desligue da tomada antes de mexer nos bornes: há 220 V expostos.'] },
() => {
  let corpo = caixa(-99.5, -49, 0, 99.5, 49, 38);
  for (let x = -75; x <= 75; x += 15) for (let y = -30; y <= 30; y += 15) corpo = corpo.cut(cilC(5, 3, [x, y, 37.5], "z"));
  const borne = caixa(-99.5, -45, 2, -88, 45, 20);
  return [{ forma: corpo, cor: 'aluminio' }, { forma: borne, cor: 'preto' }];
});
peca('botao_arcade', { nome: 'Botão arcade 60 mm iluminado', src: 'medir', link: LINK.botao, linha: 16,
  dims: 'aro Ø60,8, rosca M24 (furo de 24–25 mm no painel), 52 mm de profundidade',
  conferir: ['diâmetro da rosca: M24 (furo 25) ou Ø28 (furo 30)?', 'espessura máxima de painel que a porca aperta'],
  notas: ['Microchave: COM no GND, NA no GPIO do botão. LED: 12 V direto (já tem resistor) pelo MOSFET do LED.'] },
() => {
  const aro = cil(60.8, 4.4, [0, 0, 0], 'z');
  const capa = cil(51.9, 5.6, [0, 0, 4.4], 'z').fuse(R.makeSphere(26).translate(0, 0, -16).intersect(cil(52, 10, [0, 0, 9], 'z')));
  const rosca = cil(24, 30.5, [0, 0, -30.5], 'z');
  const porca = cil(33, 6, [0, 0, -12], 'z').cut(cil(24.2, 8, [0, 0, -13], 'z'));
  const chave = caixaC(0, 0, -30.5 - 11, 20, 10, 22);
  return [{ forma: aro, cor: 'preto' }, { forma: capa, cor: 'acrilico' }, { forma: rosca, cor: 'branco' }, { forma: porca, cor: 'branco' }, { forma: chave, cor: 'preto' }];
});
