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
