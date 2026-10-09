/* MODULO 1 — EIXO LINEAR (monta 2: eixo A da bola e eixo B do buraco)

   Referencial do eixo (CAD, Z para cima, Y para o fundo), orientacao do eixo B:
     x = 0 no meio do trilho, z = 0 no CENTRO da altura do trilho, y = 0 no centro do trilho.
     O perfil 2020 fica embaixo do trilho; o patim em cima.
   O eixo A e o MESMO conjunto espelhado em z (patim pendurado embaixo do trilho): as
   pecas impressas do A saem espelhadas (STL "_A").

   Cotas que mandam (vem das pecas compradas, nao sao escolha):
     - correia no plano y = 23,5: o patim ocupa ate y = 13,5 e a garra tem que passar atras dele
     - polia de 16 mm com o cubo virado para o motor: cubo em y = 35, logo a placa do motor
       comeca em 35,5 e o flange do NEMA fica em 40,5 (eixo de 24 mm alcanca a polia toda)
     - paredes do gabinete em x = +-207 (450 - 2 x MDF 18; o geo.inner do simulador diz 415)
   O que NAO pode crescer para tras: no eixo A o magazine passa a 43 mm atras do trilho; na
   ponta do motor a coluna do elevador comeca a 94 mm. Por isso nada fica atras da placa de
   ponta do lado tensor, e o tensor trabalha na FRENTE dela. */
import { R, caixa, caixaC, cil, cilC, sextavado, uniao, corta, extrudaPoli, escareado, FOLGA } from '../lib/base.mjs';
import { peca, inst } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';
import { PROJ } from '../lib/projeto.mjs';
import { MGN, NEMA, GT2P, LINK } from '../pecas/comprados.mjs';
import { TC } from '../pecas/eletronicos.mjs';
import { correiaLaco } from '../pecas/correia.mjs';

export const EX = {
  // parede: a do gabinete REAL (450 - 2 x MDF 18 = 414), nao o geo.inner do simulador (415):
  // com 415 os pes dos blocos entrariam 0,5 mm na parede
  parede: Math.min(PROJ.interna, PROJ.lado - 2 * 18) / 2,   // 207
  xP: 178,                          // centro das polias (+motor, -tensor)
  yC: 23.5,                         // centro da largura da correia
  yCubo: 35,                        // face do cubo da polia motora
  yPl0: 35.5, yPl1: 40.5,           // placa de ponta (motor / tensor)
  xPe: 200,                         // face interna do pe (o perfil encosta aqui)
  zPerfil: -14,                     // centro do perfil 2020 (abaixo do trilho)
  zTrilho: -4,                      // base do trilho
  zPatim: 9,                        // topo do patim
  zPlaca: 14,                       // topo da placa do carro
  curso: PROJ.curso,                // 280
  zFC: 31.5,                        // altura da bandeira/fenda do fim de curso
};
/* o feixe e cortado DENTRO do curso (x = +-136, curso +-140): o carro passa pelo sensor a cada
   vai-e-volta e o firmware confere a contagem de passos toda vez — e isso que substitui o
   encoder. A aleta entra mais 4 mm (a fenda tem 7,4 de fundo). */
EX.xHome = EX.curso / 2 - 4;        // 136
EX.aleta = 31;                       // ponta da aleta, a partir do centro do patim
EX.xSensor = EX.xHome + EX.aleta - 2.6;          // face aberta do TCST2103 (eixo optico 2,6 para dentro)
EX.xPlacaFC = EX.xSensor + TC.alt + 1.6;         // costas da placa do sensor
EX.espFC = EX.xPe - EX.xPlacaFC;                 // espacador ate o pe
const IMP = { tipo: 'impresso', src: 'est', material: 'PETG' };
const YG = [EX.yC - 6.45, EX.yC + 6.45];   // furos da garra e das presilhas (simetricos)

/* ---------------------------------------------------------------- polia tensora */
peca('polia_gt2_20t_tensora', { nome: 'Polia tensora GT2 20 dentes, furo 5 mm (com rolamento)', tipo: 'falta', src: 'cat',
  dims: 'Ø18 × 8,5 mm, dentada, furo 5', link: 'https://lista.mercadolivre.com.br/polia-tensora-gt2-20-dentes-5mm',
  notas: ['Falta comprar 2 (uma por eixo). Já vem com rolamento: gira solta no parafuso M5.',
    'Não use a polia de furo 6,35 da planilha como tensora: ela não tem rolamento.'] },
() => {
  const f = (z) => cil(18, 1, [0, 0, z], 'z');
  let d = cil(12.2, 6.5, [0, 0, 1], 'z');
  for (let i = 0; i < 20; i++) {
    const a = i * Math.PI / 10;
    d = d.cut(cil(1.1, 7.5, [Math.cos(a) * 6.25, Math.sin(a) * 6.25, 0.5], 'z'));
  }
  const corpo = uniao([f(0), d, f(7.5)]).cut(cil(10.2, 9, [0, 0, -0.25], 'z'));
  const rol = cil(10, 8.5, [0, 0, 0], 'z').cut(cil(5, 9, [0, 0, -0.25], 'z'));
  return [{ forma: corpo, cor: 'aluminio' }, { forma: rol, cor: 'aco' }];
});

/* ================================================================= PECAS IMPRESSAS */
// BLOCO DE PONTA: pe (parafusado na lateral do gabinete) + placa (motor ou tensor) +
// abas que prendem o perfil + braco do fim de curso. sx = +1 motor, -1 tensor.
function blocoPonta(sx, comFC) {
  const X = v => sx * v;
  const xa = EX.xPe, xb = EX.parede;
  // pe: 7,5 mm contra a parede. Sobe ate z=50 na faixa do fim de curso.
  let pe = caixa(X(xa), -14, -34, X(xb), EX.yPl1, 24);
  if (comFC !== false) pe = pe.fuse(caixa(X(xa), -9, 24, X(xb), 9, 50));
  // abas do perfil (frente e tras), cada uma com um furo M5
  const abaF = caixa(X(180), -14, -24, X(xa), -10, -4);
  const abaT = caixa(X(180), 10, -24, X(xa), 14, -4);
  // placa (motor ou tensor), atras da polia
  const placa = caixa(X(153), EX.yPl0, -24, X(xa), EX.yPl1, 24);
  // mãos-francesas entre o pe e a placa (acima e abaixo da polia)
  const mf = z0 => extrudaPoli([[X(xa), 26], [X(xa), EX.yPl0], [X(188), EX.yPl0]], 8, z0);
  let b = uniao([pe, abaF, abaT, placa, mf(16), mf(-24)]);
  // espacadores do fim de curso: a placa do TCST2103 fica 7,2 mm a frente do pe
  if (comFC !== false) [EX.zFC - TC.fx, EX.zFC + TC.fx].forEach(z => { b = b.fuse(cil(7, EX.espFC, [X(xa), 0, z], sx > 0 ? '-x' : 'x')); });
  // furos M5 das abas (eixo y)
  b = b.cut(cilC(FOLGA.m5, 40, [X(190), 0, EX.zPerfil], 'y'));
  // 4 parafusos de madeira para a parede, cabeca do lado de dentro (face x = 200)
  [[-7, 17], [22, 18], [-7, -29], [22, -29]].forEach(([y, z]) => {
    b = b.cut(escareado([X(xa), y, z], 'x', -sx, 20));
  });
  // espera do fim de curso: furo-guia de 2,8 no espacador (o parafuso M3 rosqueia no plastico)
  if (comFC !== false) [EX.zFC - TC.fx, EX.zFC + TC.fx].forEach(z => { b = b.cut(cilC(2.8, 28, [X(EX.xPlacaFC), 0, z], 'x')); });
  return b;
}
function blocoMotor() {
  let b = blocoPonta(1);
  b = b.cut(cilC(NEMA.boss + 0.6, 20, [EX.xP, 38, 0], 'y'));          // ressalto do motor
  [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([a, c]) => {
    b = b.cut(cilC(FOLGA.m3, 20, [EX.xP + a * NEMA.furo / 2, 38, c * NEMA.furo / 2], 'y'));
  });
  return b;
}
// o tensor trabalha na FRENTE da placa: deslizador entre a polia e a placa
const TENS = { x0: -185, x1: -171, y0: 28.75, y1: EX.yPl0 - 0.1, z: 14, curso: 4 };
function blocoTensor(comFC) {
  let b = blocoPonta(-1, comFC);
  const xc = -EX.xP;
  // rasgo para a ponta do parafuso M5 do eixo da polia
  b = b.cut(caixa(xc - TENS.curso - 2.8, EX.yPl0 - 1, -2.8, xc + TENS.curso + 2.8, EX.yPl1 + 1, 2.8));
  // 2 rasgos M3 das travas, com rebaixo da cabeca do lado de tras (nada sobra atras da placa)
  [-10, 10].forEach(z => {
    b = b.cut(caixa(xc - TENS.curso - 1.7, EX.yPl0 - 1, z - 1.7, xc + TENS.curso + 1.7, EX.yPl1 + 1, z + 1.7));
    b = b.cut(caixa(xc - TENS.curso - 3.1, EX.yPl1 - FOLGA.m3CabH, z - 3.1, xc + TENS.curso + 3.1, EX.yPl1 + 1, z + 3.1));
  });
  // orelha do parafuso tensor: na frente da placa, abaixo do ramo de baixo da correia
  let orelha = caixa(-165, TENS.y0, -17, -160.5, EX.yPl0, -8);
  orelha = orelha.cut(cilC(FOLGA.m3, 10, [-162.75, 32.1, -12.5], 'x'));
  orelha = orelha.cut(caixa(-164.2, 32.1 - 2.9, -18, -161.6, 32.1 + 2.9, -12.5));   // porca M3 entra por baixo
  return b.fuse(orelha);
}
function deslizador() {
  let s = caixa(TENS.x0, TENS.y0, -TENS.z, TENS.x1, TENS.y1, TENS.z).fillet(1, e => e.inDirection('Y'));
  const xc = -EX.xP;
  s = s.cut(cilC(FOLGA.m5, 20, [xc, 32, 0], 'y'));
  s = s.cut(sextavado(FOLGA.m5PorcaAF, 6.4, [xc, TENS.y1 - 2.2, 0], 'y'));            // porca M5 autotravante (5,2)
  [-10, 10].forEach(z => {
    s = s.cut(cilC(FOLGA.m3, 20, [xc, 32, z], 'y'));
    s = s.cut(sextavado(FOLGA.m3PorcaAF, 2.8, [xc, TENS.y1 - 1.3, z], 'y'));
  });
  return s;
}
// PLACA DO CARRO: 4 parafusos no patim, 2 esperas para a carga (berco ou boca), 2 para a garra,
// e as duas bandeiras do fim de curso
function placaCarro() {
  const z0 = EX.zPatim, z1 = EX.zPlaca;
  let p = caixa(-25, -29, z0, 25, 34, z1).fillet(3, e => e.inDirection('Z'));
  // bandeiras: torre na ponta + aleta horizontal que entra na fenda do TCST2103
  [-1, 1].forEach(s => {
    const torre = caixa(s * 14, -3, z1 - 0.5, s * 19, 3, EX.zFC + 0.8);
    const aleta = caixa(s * 18.5, -3, EX.zFC - 0.8, s * EX.aleta, 3, EX.zFC + 0.8);
    p = p.fuse(torre).fuse(aleta);
  });
  [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([a, c]) => {
    p = p.cut(cilC(FOLGA.m3, 20, [a * MGN.C / 2, c * MGN.B / 2, z0], 'z'));
  });
  [-15, 15].forEach(x => {                                     // esperas da carga: porca por baixo
    p = p.cut(cilC(FOLGA.m3, 20, [x, -17, z0], 'z'));
    p = p.cut(sextavado(FOLGA.m3PorcaAF, 2.8 * 2, [x, -17, z0], 'z'));
  });
  YG.forEach(y => { p = p.cut(cilC(FOLGA.m3, 20, [0, y, z0], 'z')); });   // garra
  return p;
}
// GARRA: bloco embaixo da traseira da placa, com o canal da correia aberto por baixo
function garra() {
  let g = caixa(-14, 14.5, 2, 14, 34, EX.zPatim).fillet(1, e => e.inDirection('X'));
  g = g.cut(caixa(-15, EX.yC - 3.2, 1, 15, EX.yC + 3.2, 6.85));
  YG.forEach(y => { g = g.cut(cilC(2.8, 10, [0, y, 6], 'z')); });
  [-8, 8].forEach(x => YG.forEach(y => { g = g.cut(cilC(2.8, 10, [x, y, 3], 'z')); }));
  return g;
}
// PRESILHA: aperta a ponta da correia contra o teto do canal; nervura dentada encaixa nos dentes
function presilha() {
  let p = caixa(2.5, EX.yC - 8.5, 0, 13.5, EX.yC + 8.5, 2);
  p = p.fuse(caixa(2.5, EX.yC - 2.9, 2, 13.5, EX.yC + 2.9, 4.4));
  for (let x = 4; x < 13; x += 2) p = p.fuse(caixa(x - 0.5, EX.yC - 2.9, 4.4, x + 0.5, EX.yC + 2.9, 5.2));
  YG.forEach(y => { p = p.cut(cilC(FOLGA.m3, 10, [8, y, 1], 'z')); });
  return p;
}
// GABARITO: encaixa no perfil e no trilho e deixa os dois centrados enquanto aperta
function gabarito() {
  let g = caixa(-6, -13, -26, 6, 13, 3);
  g = g.cut(caixa(-7, -10.15, -27, 7, 10.15, -4));             // perfil
  g = g.cut(caixa(-7, -6.1, -4.5, 7, 6.1, 4));                 // trilho
  return g;
}

/* registro das impressas (geometria no referencial do eixo; 'ref' vira a origem do STL) */
const reg = (id, meta, fn, ref, imprimir) => peca(id, Object.assign({}, IMP, meta, { ref, imprimir }),
  () => [{ forma: fn().translate(-ref[0], -ref[1], -ref[2]), cor: meta.cor || 'impresso' }]);

reg('eixo_bloco_motor', { nome: 'Bloco de ponta do MOTOR', dims: '54 × 55 × 84 mm',
  impressao: { preenchimento: '40 %', paredes: 4, suportes: 'não', tempo: '≈ 3 h' },
  notas: ['Prende o perfil (2 × M5), segura o motor (4 × M3×8) e vai parafusado na lateral do gabinete (4 parafusos de madeira).',
    'Imprima deitado sobre a face do pé (a que encosta na parede).'] }, blocoMotor, [EX.xPe, 0, 0], { rot: [['y', -90]] });
reg('eixo_bloco_tensor', { nome: 'Bloco de ponta do TENSOR', dims: '54 × 55 × 84 mm',
  impressao: { preenchimento: '40 %', paredes: 4, suportes: 'não', tempo: '≈ 3 h' },
  notas: ['A polia tensora fica num deslizador NA FRENTE desta placa: atrás dela não pode sobrar nada (no eixo A o magazine passa ali).'] },
blocoTensor, [-EX.xPe, 0, 0], { rot: [['y', 90]] });
reg('eixo_bloco_tensor_semfc', { nome: 'Bloco de ponta do TENSOR, sem fim de curso (só eixo A)', dims: '54 × 55 × 58 mm',
  impressao: { preenchimento: '40 %', paredes: 4, suportes: 'não', tempo: '≈ 2 h 30' },
  notas: ['No eixo A, à esquerda, passa a calha que leva a bola do magazine até o berço: ali não cabe o sensor.',
    'O eixo A confere os passos só pelo sensor da direita, que ele cruza a cada vai-e-volta.'] },
() => blocoTensor(false), [-EX.xPe, 0, 0], { rot: [['y', 90]] });
reg('eixo_deslizador', { nome: 'Deslizador do tensor', dims: '14 × 6,7 × 28 mm', cor: 'impresso2',
  impressao: { preenchimento: '60 %', paredes: 4, suportes: 'não', tempo: '20 min' },
  notas: ['Leva a porca M5 da polia e 2 porcas M3 das travas, todas viradas para a placa: não caem depois de montado.'] },
deslizador, [-EX.xP, TENS.y0, 0], { rot: [['x', 90]] });
reg('eixo_placa_carro', { nome: 'Placa do carro', dims: '50 × 63 × 5 mm + bandeiras', cor: 'impresso2',
  impressao: { preenchimento: '50 %', paredes: 4, suportes: 'não (bandeiras para cima)', tempo: '≈ 1 h 30' },
  notas: ['As duas aletas nas pontas são as BANDEIRAS dos fins de curso: entram na fenda do sensor quando o carro chega ao fim.',
    'Os 2 furos da frente (com porca por baixo) prendem o berço (eixo A) ou a boca (eixo B).'] },
placaCarro, [0, 0, EX.zPatim], null);
reg('eixo_garra', { nome: 'Garra da correia', dims: '28 × 19,5 × 7 mm', cor: 'impresso2',
  impressao: { preenchimento: '60 %', paredes: 4, suportes: 'não (canal para cima)', tempo: '30 min' } },
garra, [0, EX.yC, EX.zPatim], { rot: [['x', 180]] });
reg('eixo_presilha', { nome: 'Presilha dentada da correia', dims: '11 × 18,5 × 5,2 mm', cor: 'impresso2',
  impressao: { preenchimento: '100 %', paredes: 4, suportes: 'não', tempo: '10 min' },
  notas: ['A nervura dentada encaixa nos dentes da correia: ela não escorrega mesmo com aperto leve.'] },
presilha, [8, EX.yC, 0], null);
reg('eixo_gabarito', { nome: 'Gabarito de centragem do trilho', dims: '12 × 26 × 29 mm', cor: 'impresso2',
  impressao: { preenchimento: '20 %', paredes: 3, suportes: 'não', tempo: '15 min' },
  notas: ['Ferramenta: só serve durante a montagem. Imprima 3 e use os mesmos nos dois eixos.'] },
gabarito, [0, 0, 0], { rot: [['x', 180]] });

/* correia de cada eixo: laco entre as polias, pontas presas na garra (carro no centro) */
const XC0 = 0;
peca('correia_eixo', { nome: 'Correia GT2 6 mm (laço do eixo)', tipo: 'comprado', src: 'cat', linha: 15, link: LINK.gt2kit,
  dims: '≈ 790 mm cortados de 1 m', notas: ['Corte com 790 mm: 752 mm do laço + 2 pontas de 19 mm dentro da garra.'] },
() => correiaLaco({ x1: -EX.xP, x2: EX.xP, rp: GT2P.dp / 2, larg: 6, y0: EX.yC - 3, xa: XC0 - 2.5, xb: XC0 + 2.5 })
  .map(f => ({ forma: f, cor: 'correia' })));

/* ================================================================= INSTANCIAS */
function instancias() {
  const I = [];
  const add = (id, p, t, extra) => I.push(inst(id, p, t, extra));
  const r = T.of();
  // perfil + trilho
  add('perfil', 'perfil2020_400', r.t(0, 0, EX.zPerfil));
  add('trilho', 'mgn12_trilho_400', r.t(0, 0, EX.zTrilho));
  const furosUsados = [0, 2, 4, 6, 8, 10, 12, 14];
  furosUsados.forEach((i, k) => {
    const x = -200 + MGN.E + i * MGN.P;
    add('pm3_trilho_' + k, 'porca_martelo_m3', r.t(x, 0, EX.zTrilho - 1.8));
    add('p_trilho_' + k, 'din912_m3x8', r.t(x, 0, EX.zTrilho + MGN.H - MGN.h));
  });
  [-140, -70, 70].forEach((x, k) => add('gab_' + k, 'eixo_gabarito', r.t(x, 0, 0)));
  // patim e placa
  add('patim', 'mgn12h_patim', r.t(XC0, 0, EX.zTrilho));
  add('placa', 'eixo_placa_carro', r.t(XC0, 0, EX.zPatim));
  [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([a, c], k) =>
    add('p_placa_' + k, 'din912_m3x8', r.t(XC0 + a * 10, c * 10, EX.zPlaca)));
  [-15, 15].forEach((x, k) => add('porca_carga_' + k, 'porca_m3', r.t(XC0 + x, -17, EX.zPatim + 0.2)));
  add('garra', 'eixo_garra', r.t(XC0, EX.yC, EX.zPatim));
  YG.forEach((y, k) => add('p_garra_' + k, 'din912_m3x12', r.t(XC0, y, EX.zPlaca)));
  [-1, 1].forEach((s, k) => {
    add('presilha_' + k, 'eixo_presilha', (s > 0 ? r : r.rz(180)).t(XC0 + s * 8, EX.yC, 0));
    YG.forEach((y, j) => add(`p_pres_${k}_${j}`, 'din912_m3x8', r.rx(180).t(XC0 + s * 8, y, 0)));
  });
  // bloco do motor
  add('bloco_motor', 'eixo_bloco_motor', r.t(EX.xPe, 0, 0));
  add('motor', 'nema17', r.rx(90).t(EX.xP, EX.yPl1, 0));
  [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([a, c], k) =>
    add('p_motor_' + k, 'din912_m3x8', r.rx(90).t(EX.xP + a * NEMA.furo / 2, EX.yPl0, c * NEMA.furo / 2)));
  add('polia_motor', 'polia_gt2_20t_5', r.rx(90).t(EX.xP, EX.yCubo, 0));
  // bloco do tensor
  add('bloco_tensor', 'eixo_bloco_tensor', r.t(-EX.xPe, 0, 0));
  add('deslizador', 'eixo_deslizador', r.t(-EX.xP, TENS.y0, 0));
  add('porca_m5_tensor', 'porca_nylon_m5', r.rx(-90).t(-EX.xP, TENS.y1 - 5.3, 0));
  [-10, 10].forEach((z, k) => {
    add('porca_trava_' + k, 'porca_m3', r.rx(-90).t(-EX.xP, TENS.y1 - 2.6, z));
    add('p_trava_' + k, 'din912_m3x8', r.rx(-90).t(-EX.xP, EX.yPl1 - FOLGA.m3CabH, z));
  });
  add('arruela_t0', 'arruela_m5', r.rx(90).t(-EX.xP, 19.25, 0));
  add('polia_tensora', 'polia_gt2_20t_tensora', r.rx(90).t(-EX.xP, 27.75, 0));
  add('arruela_t1', 'arruela_m5', r.rx(90).t(-EX.xP, 28.75, 0));
  add('p_m5_tensor', 'iso7380_m5x20', r.rx(90).t(-EX.xP, 18.25, 0));
  add('porca_tensor', 'porca_m3', r.ry(90).t(-164.0, 32.1, -12.5));
  // parafuso tensor desenhado na posicao de trabalho: 5,5 mm para fora, ponta encostada no deslizador
  add('p_tensor', 'din912_m3x16', r.ry(90).t(-155, 32.1, -12.5));
  // abas do perfil: 4 x M5 com porca martelo
  [1, -1].forEach(sx => [-1, 1].forEach(sy => {
    const k = (sx > 0 ? 'm' : 't') + (sy > 0 ? 'T' : 'F');
    add('pm5_' + k, 'porca_martelo_m5', r.rx(sy > 0 ? -90 : 90).t(sx * 190, sy * 8.2, EX.zPerfil));
    add('p_aba_' + k, 'iso7380_m5x10', r.rx(sy > 0 ? -90 : 90).t(sx * 190, sy * 14, EX.zPerfil));
  }));
  // correia
  add('correia', 'correia_eixo', r, { semColisao: true });   // dente com dente na polia: contato de proposito
  // fins de curso: placa de pe, sensor virado para o centro
  [1, -1].forEach(sx => {
    const k = sx > 0 ? 'm' : 't';
    add('fc_' + k, 'tcst2103', r.ry(-90 * sx).t(sx * EX.xPlacaFC, 0, EX.zFC));
    // o parafuso apoia na ABA do sensor (3,1 mm acima da placa)
    [-1, 1].forEach((s, j) => add(`p_fc_${k}_${j}`, 'din912_m3x16', r.ry(-90 * sx).t(sx * (EX.xPlacaFC - 1.6 - 3.1), 0, EX.zFC + s * TC.fx)));
  });
  // variante do eixo A, mostrada ao lado (so no ultimo passo)
  add('bloco_tensor_A', 'eixo_bloco_tensor_semfc', r.t(-EX.xPe, -150, 0), { semColisao: true, oculta: true });
  return I;
}

/* parafusos de madeira so na instalacao (montagem final) */
function parafusosParede() {
  const I = [];
  [1, -1].forEach(sx => [[-7, 17], [22, 18], [-7, -29], [22, -29]].forEach(([y, z], k) =>
    I.push(inst(`mad_${sx > 0 ? 'm' : 't'}_${k}`, 'madeira_3_5x20', T.of().ry(-90 * sx).t(sx * EX.xPe, y, z)))));
  return I;
}

export function moduloEixo() {
  const I = instancias().concat(parafusosParede());
  const ids = pre => I.filter(i => i.id.startsWith(pre)).map(i => i.id);
  return {
    id: 'eixo',
    espelhoA: true,
    nome: 'Eixo linear',
    subtitulo: 'Monte 2 iguais: eixo A (bola, de cabeça para baixo) e eixo B (buraco)',
    resumo: 'Trilho MGN12 sobre perfil de alumínio, patim com placa impressa, motor NEMA 17 numa ponta e polia tensora na outra, correia GT2 presa na garra do carro e dois fins de curso ópticos.',
    tempo: '≈ 1 h 30 por eixo (sem contar a impressão)',
    instancias: I,
    // o carro inteiro nos dois extremos do curso, contra tudo o que e fixo
    varredura: [{ ids: ['patim', 'placa', 'garra', 'presilha_0', 'presilha_1'], desloc: [[EX.curso / 2, 0, 0], [-EX.curso / 2, 0, 0]],
      ignora: ['trilho', 'perfil', 'gab_0', 'gab_1', 'gab_2'] }],
    passos: [
      { titulo: 'Conheça as peças', vista: 'iso', mostra: 'tudo', explode: 1,
        texto: 'Este é o eixo B completo, com as peças afastadas. O eixo A é idêntico, só que montado de cabeça para baixo (o patim fica pendurado embaixo do trilho). Cores: <b>cinza</b> = comprado, <b>laranja</b> = impresso fixo, <b>azul</b> = impresso que se move.',
        atencao: ['Antes de começar, imprima todas as peças laranja e azuis da lista (botão "Imprimir").'] },
      { titulo: 'Porcas martelo no perfil', novos: [...ids('pm3_trilho')], base: ['perfil'], vista: 'cima',
        texto: 'Coloque o perfil 2020 deitado na mesa. Encaixe 8 porcas martelo M3 na fenda de CIMA, espaçadas a cada 50 mm (um furo sim, um não do trilho). Elas entram de lado e ficam soltas por enquanto.',
        ferramentas: [], confira: ['As 8 porcas estão na fenda de cima, não na lateral.'] },
      { titulo: 'Trilho no perfil, com os gabaritos', novos: ['trilho', ...ids('gab_')], vista: 'iso',
        texto: 'Apoie o trilho MGN12 sobre o perfil, pontas alinhadas com as pontas do perfil. Encaixe os 3 gabaritos impressos por cima: eles abraçam o perfil e o trilho e deixam o trilho exatamente no centro.',
        atencao: ['NÃO tire o patim do trilho. Se ele já veio montado, deixe — as esferas caem se ele sair sem o trilho falso.'] },
      { titulo: 'Parafusos do trilho', novos: ids('p_trilho_'), vista: 'cima', ferramentas: ['chave allen 2,5 mm'],
        texto: 'Passe um parafuso M3×8 em cada furo que tem porca embaixo (um sim, um não). Gire cada um até a porca martelo virar e travar na fenda. Aperte do CENTRO para as pontas, primeiro leve, depois firme.',
        confira: ['O trilho não mexe de lado.', 'Passe o dedo na emenda trilho/perfil: nenhum degrau nas pontas.'],
        atencao: ['M3×8 é o comprimento certo: um M3×10 bate no fundo do perfil e entorta o trilho.'] },
      { titulo: 'Placa do carro', novos: ['patim', 'placa', ...ids('p_placa_'), ...ids('porca_carga_')], remove: ids('gab_'), vista: 'iso',
        texto: 'Tire os 3 gabaritos (já cumpriram a função). Coloque as 2 porcas M3 nos encaixes sextavados de baixo da placa do carro (as da frente). Apoie a placa sobre o patim com as bandeiras para cima e prenda com 4 parafusos M3×8.',
        ferramentas: ['chave allen 2,5 mm'],
        atencao: ['O patim só tem 3,5 mm de rosca. Parafuso maior que M3×8 trava as esferas.'],
        confira: ['O carro corre de ponta a ponta sem ponto duro.'] },
      { titulo: 'Garra da correia', novos: ['garra', ...ids('p_garra_')], vista: 'tras',
        texto: 'Prenda a garra embaixo da traseira da placa com 2 parafusos M3×12, de cima para baixo. Eles rosqueiam direto no plástico da garra: aperte até encostar e mais 1/4 de volta.',
        ferramentas: ['chave allen 2,5 mm'] },
      { titulo: 'Motor no bloco de ponta', novos: ['bloco_motor', 'motor', ...ids('p_motor_')], vista: 'tras',
        texto: 'Encaixe o ressalto redondo do motor no furo grande da placa do bloco do motor, conector virado para BAIXO. Prenda com 4 parafusos M3×8 pela frente da placa.',
        ferramentas: ['chave allen 2,5 mm'], confira: ['O motor fica encostado na placa sem folga.'] },
      { titulo: 'Polia no motor', novos: ['polia_motor'], vista: 'frente', zoom: ['polia_motor'],
        texto: 'Encaixe a polia GT2 (furo de 5 mm) no eixo do motor com o CUBO (parte sem dentes) virado para o motor, deixando 0,5 mm de folga até a placa (uma folha de papel dobrada serve de calço). Gire até um parafusinho do cubo ficar sobre a parte chata do eixo e aperte esse primeiro.',
        ferramentas: ['chave allen 1,5 mm'],
        atencao: ['A polia da planilha tem furo 6,35 mm: no eixo de 5 mm ela fica torta. Use a de 5 mm (lista "falta comprar").'] },
      { titulo: 'Deslizador do tensor', novos: ['bloco_tensor', 'deslizador', 'porca_m5_tensor', ...ids('porca_trava_'), ...ids('p_trava_')], vista: 'tras',
        texto: 'Coloque a porca M5 autotravante e as 2 porcas M3 nos encaixes do deslizador (todas pelo lado que encosta na placa). Encoste o deslizador na FRENTE da placa do bloco tensor e passe os 2 parafusos M3×8 por trás, pelos rasgos. Deixe-os frouxos: o deslizador tem que correr no rasgo.',
        ferramentas: ['chave allen 2,5 mm'] },
      { titulo: 'Polia tensora', novos: ['arruela_t0', 'polia_tensora', 'arruela_t1', 'p_m5_tensor'], vista: 'frente', zoom: ['polia_tensora'],
        texto: 'Monte em ordem no parafuso M5: arruela, polia tensora, arruela. Rosqueie na porca M5 do deslizador até a polia ficar presa mas girando livre.',
        ferramentas: ['chave allen 4 mm'], confira: ['A polia gira solta com um peteleco.'] },
      { titulo: 'Parafuso tensor', novos: ['porca_tensor', 'p_tensor'], vista: 'baixo',
        texto: 'Coloque a porca M3 na orelha de baixo do bloco tensor (entra por baixo). Rosqueie o parafuso M3×16 pelo lado de dentro: a ponta dele empurra o deslizador para fora e é isso que estica a correia.',
        ferramentas: ['chave allen 2,5 mm'] },
      { titulo: 'Blocos nas pontas do perfil', novos: [...ids('pm5_'), ...ids('p_aba_')], vista: 'iso',
        texto: 'Encaixe as pontas do perfil nos dois blocos (motor à direita, tensor à esquerda), encostando o perfil no pé. Coloque as 4 porcas martelo M5 nas fendas da frente e de trás do perfil e prenda com os parafusos M5×10 pelas abas.',
        ferramentas: ['chave allen 3 mm'], confira: ['Perfil encostado no pé dos dois lados.', 'Os dois pés ficam paralelos (meça 414 mm por fora, em cima e embaixo).'] },
      { titulo: 'Correia', novos: ['correia', ...ids('presilha_'), ...ids('p_pres_')], vista: 'tras', zoom: ['garra'],
        texto: 'Corte 790 mm de correia GT2 6 mm. Prenda uma ponta na garra: dentes para CIMA encostando na nervura dentada da presilha, aperte os 2 parafusos M3×8 da presilha. Passe a correia pela polia do motor, pela polia tensora (dentes sempre para dentro) e prenda a outra ponta na outra presilha.',
        ferramentas: ['chave allen 2,5 mm', 'tesoura'],
        confira: ['A correia não torce em lugar nenhum.', 'Os dois ramos ficam na mesma altura das polias.'] },
      { titulo: 'Esticar a correia', vista: 'cima', zoom: ['deslizador'],
        texto: 'Aperte o parafuso tensor M3×16 aos poucos. Pare quando o ramo de cima, apertado no meio com um dedo, afundar uns 3 mm. Toque nele: tem que soar um "tum" grave (≈110 Hz — um app de afinador de violão mede). Então aperte as 2 travas M3 de trás.',
        ferramentas: ['chave allen 2,5 mm'],
        atencao: ['Correia esticada demais gasta o rolamento do motor; frouxa demais pula dente na inversão — é a folga que o PROJETO.md chama de risco.'] },
      { titulo: 'Fins de curso', novos: [...ids('fc_'), ...ids('p_fc_')], vista: 'frente',
        texto: 'Parafuse cada placa TCST2103 nos 2 espaçadores altos do bloco de ponta com parafusos M3×16 (rosqueiam no plástico), sensor virado para o centro, fenda na horizontal. Leve o carro devagar até a ponta: a aleta da placa do carro entra no meio da fenda e corta o feixe com o carro a 136 mm do centro — 4 mm ANTES do fim do curso (140). É de propósito: o carro cruza o sensor a cada vai-e-volta e o firmware confere ali se nenhum passo foi perdido.',
        ferramentas: ['chave allen 2,5 mm'],
        confira: ['Com a placa ligada, o LED do sensor muda quando a aleta entra.', 'No fim do curso (140 mm) a aleta ainda não encostou no fundo da fenda.'] },
      { titulo: 'Eixo A: o que muda', novos: ['bloco_tensor_A'], vista: 'iso', zoom: ['bloco_tensor_A', 'bloco_tensor'],
        texto: 'O eixo A é este mesmo conjunto montado de cabeça para baixo, com 2 diferenças: (1) as peças impressas são as do arquivo "STL A" (espelhadas); (2) na ESQUERDA use o bloco tensor SEM o braço do fim de curso (à frente, em destaque) e não instale o sensor da esquerda. Por ali passa a calha que leva a bola do magazine até o berço.',
        atencao: ['O eixo A confere os passos só pelo sensor da direita — ele o cruza a cada jogada.'] },
      { titulo: 'Instalação no gabinete', novos: [...ids('mad_')], vista: 'iso', mostra: 'tudo',
        texto: 'O eixo inteiro mede exatamente a largura interna do gabinete (414 mm). Entre com ele pela frente, encoste os pés nas laterais na altura marcada e prenda cada pé com 4 parafusos de madeira 3,5×20 por dentro. Eixo B: trilho em cima. Eixo A: o mesmo conjunto de cabeça para baixo (patim embaixo).',
        ferramentas: ['chave Phillips nº 2', 'nível de bolha'],
        confira: ['Nível de bolha sobre o perfil: horizontal.', 'Eixo A e eixo B paralelos entre si.'],
        alturas: [{ eixo: 'B', y: 1175, nota: 'centro do trilho B a 1175 mm do chão' }, { eixo: 'A', y: 1530, nota: 'centro do trilho A a 1530 mm do chão' }] },
    ],
  };
}
