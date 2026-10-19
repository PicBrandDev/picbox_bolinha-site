/* Pecas compradas (planilha "PICBOX_Plano_de_Custos_links_ML2.xlsx", Plano 1) e as
   que a montagem exige mas nao estao na planilha (tipo 'falta').

   Cada geometria aqui segue o desenho do fabricante do MODELO que o anuncio vende.
   Anuncio generico (sem desenho) = src 'medir': a ficha diz o que conferir. */
import { R, caixa, caixaC, cil, cilC, tubo, sextavado, uniao, corta, extrudaPoli } from '../lib/base.mjs';
import { peca } from '../lib/registro.mjs';

export const LINK = {
  esp32: 'https://produto.mercadolivre.com.br/MLB-1409431047-placa-esp32-wifi-bluetooth-devkit-v1-30-pinos-_JM',
  solenoide: 'https://produto.mercadolivre.com.br/MLB-2020200039-solenoide-tipo-push-pull-12v-p-robotica-_JM',
  irf520: 'https://produto.mercadolivre.com.br/MLB-3689376795-5x-modulo-mosfet-irf520-pwm-driver-dc-arduino-12v-24v-_JM',
  sol0530: 'https://produto.mercadolivre.com.br/MLB-847770889-solenoide-0530-eletro-im-dc-12v-push-pull-arduino-robotica-_JM',
  sg90: 'https://produto.mercadolivre.com.br/MLB-1306049887-micro-servo-motor-9g-sg90-_JM',
  ir333c: 'https://produto.mercadolivre.com.br/MLB-1820025242-kit-50-pecas-led-emissor-infravermelho-ir333c-5mm-940nm-_JM',
  til78: 'https://www.mercadolivre.com.br/fototransistor-ir-receptor-infravermelho-til78-5mm/up/MLBU1965894181',
  nema17: 'https://lista.mercadolivre.com.br/motor-de-passo-nema-17-12v',
  as5600: 'https://www.mercadolivre.com.br/qccan-6-pecas-as5600-codificador-magnetico-alta-precisao/p/MLB2055223307',
  tmc2209: 'https://www.mercadolivre.com.br/driver-de-motor-de-passo-tmc2209-v20-de-4-conjuntos-adequad/p/MLB2069101300',
  mgn12: 'https://produto.mercadolivre.com.br/MLB-1835747600-eixo-guia-linear-mgn12h-12mm-x-400mm-com-patim-nf-_JM',
  gt2polia: 'https://produto.mercadolivre.com.br/MLB-894729913-kit-3-polias-gt2-20-dentes-p-correia-6mm-furo-635mm-cnc-3d-_JM',
  gt2kit: 'https://lista.mercadolivre.com.br/kit-polia-e-correia-gt2',
  botao: 'https://www.mercadolivre.com.br/botao-arcade-fliperama-iluminado-60mm--verde/up/MLBU2306114819',
  fonte: 'https://www.mercadolivre.com.br/fonte-colmeia-premium-chaveada-12v-10a-para-cmera-seguranca-bivolt/p/MLB27411633',
  jga25: 'https://produto.mercadolivre.com.br/MLB-3434269541-motor-eletrico-com-redutor-12v-15-rpm-modelo-jga25-370-_JM',
  gt2_10: 'https://produto.mercadolivre.com.br/MLB-1715503869-2-metros-correia-dentada-gt2-alma-de-aco-largura-10mm-preta-_JM',
  emenda: 'https://produto.mercadolivre.com.br/MLB-1121261926-fixador-emenda-aluminio-9x40-p-correia-gt2-impressora-3d-_JM',
  tubo: 'https://www.mercadolivre.com.br/tubo-cano-acrilico-40mm-ext-x-2mm-36mm-int-x-50cm-1-peca/up/MLBU734811564',
  lm393: 'https://www.mercadolivre.com.br/modulo-comparador-lm393-4-pcs/p/MLB2023094345',
  tcst2103: 'https://produto.mercadolivre.com.br/MLB-1920705102-6-sensor-optico-fim-de-curso-tcst2103-impressora-3d-endstop-_JM',
  bola: 'https://lista.mercadolivre.com.br/bola-de-sinuca-35mm',
  petg: 'https://lista.mercadolivre.com.br/filamento-petg-1kg',
};

/* ============================================================== BOLA */
peca('bola35', { nome: 'Bola de jogo Ø35', src: 'est', dims: 'Ø35 mm, ~30 g', link: LINK.bola, linha: 28,
  notas: ['A planilha ainda deixa o material em aberto. O tubo do magazine (Ø36 interno) só aceita Ø35: a bola de 38 mm NÃO entra.'] },
() => [{ forma: R.makeSphere(17.5), cor: 'bola' }]);

/* ============================================================== GUIA LINEAR MGN12 */
// HIWIN MGN12: W 12, H 8, P 25, E 12,5 (trilho 400 = 16 furos), furo d3,5 / D6 / h4,5
export const MGN = { W: 12, H: 8, P: 25, E: 12.5, d: 3.5, D: 6, h: 4.5,
  // MGN12H: L 45,4, corpo de aco 32,4, W 27, H 13 (da base do trilho ao topo do patim), H1 3
  L: 45.4, L1: 32.4, WR: 27, HT: 13, H1: 3, B: 20, C: 20, M: 3, prof: 3.5 };
function trilhoMGN12(L) {
  // origem: centro do trilho no comprimento e na largura, base em z=0. Comprimento em X.
  let t = caixa(-L / 2, -MGN.W / 2, 0, L / 2, MGN.W / 2, MGN.H);
  // pistas das esferas (dois sulcos em arco, um de cada lado)
  [-1, 1].forEach(s => { t = t.cut(cilC(2.4, L + 2, [0, s * MGN.W / 2, 5.6], 'x')); });
  t = t.chamfer(0.4, e => e.inDirection('X').inPlane('XY', MGN.H));
  const n = Math.round((L - 2 * MGN.E) / MGN.P) + 1;
  for (let i = 0; i < n; i++) {
    const x = -L / 2 + MGN.E + i * MGN.P;
    t = t.cut(cilC(MGN.d, MGN.H + 2, [x, 0, MGN.H / 2], 'z'));
    t = t.cut(cil(MGN.D, MGN.h + 0.1, [x, 0, MGN.H - MGN.h], 'z'));
  }
  return [{ forma: t, cor: 'aco' }];
}
peca('mgn12_trilho_400', { nome: 'Trilho linear MGN12 400 mm', dims: '400 × 12 × 8 mm, 16 furos M3 a cada 25 mm',
  link: LINK.mgn12, linha: 14, src: 'cat',
  notas: ['Cota HIWIN MGN12 (clones seguem o mesmo desenho). Furo escareado Ø6 × 4,5 para parafuso M3.',
    'Nunca tire o patim do trilho sem o "trilho falso" de plástico que vem na caixa: as esferas caem.'] },
() => trilhoMGN12(400));

function patimMGN12H() {
  // origem: base do TRILHO em z=0, centro do patim em x=0
  const { L, L1, WR, HT, H1 } = MGN;
  void 0;
  const canal = (x0, x1) => caixa(x0, -6.25, H1 - 0.1, x1, 6.25, 8.6);
  let corpo = caixa(-L1 / 2, -WR / 2, H1, L1 / 2, WR / 2, HT).cut(canal(-L1, L1));
  corpo = corpo.chamfer(0.5, e => e.inDirection('X').inPlane('XY', HT));
  [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([sx, sy]) => {
    corpo = corpo.cut(cil(2.5, MGN.prof + 0.1, [sx * MGN.C / 2, sy * MGN.B / 2, HT - MGN.prof], 'z'));
  });
  const tampas = [-1, 1].map(s => {
    const x0 = s * L1 / 2, x1 = s * (L1 / 2 + 4.7);
    return caixa(x0, -WR / 2 + 0.4, H1 + 0.3, x1, WR / 2 - 0.4, HT - 0.5).cut(canal(-L, L));
  });
  const vedas = [-1, 1].map(s => {
    const x0 = s * (L1 / 2 + 4.7), x1 = s * L / 2;
    return caixa(x0, -WR / 2 + 0.8, H1 + 0.3, x1, WR / 2 - 0.8, HT - 0.8).cut(canal(-L, L));
  });
  // tamanho 12 nao tem graxeira: so um furo de lubrificacao de 2 mm na tampa
  const tampasF = uniao(tampas).cut(cil(2, 8, [L1 / 2 + 1, 0, 9], 'x'));
  return [{ forma: corpo, cor: 'aco' }, { forma: tampasF, cor: 'preto' }, { forma: uniao(vedas), cor: 'vermelho' }];
}
peca('mgn12h_patim', { nome: 'Patim (carro) MGN12H', dims: '45,4 × 27 × 13 mm, 4 furos M3 em 20 × 20', link: LINK.mgn12, linha: 14,
  notas: ['4 roscas M3 de 3,5 mm de profundidade: parafuso que passe disso trava as esferas.'] }, patimMGN12H);

/* ============================================================== PERFIL 2020 */
function perfil2020(L) {
  // secao no plano YZ, comprimento em X, centrado. Fenda serie 20: abertura 6,2
  const a = 10, ab = 3.1;
  let s = caixa(-L / 2, -a, -a, L / 2, a, a);
  const fenda = (rotY) => {
    // abertura 6,2 x 1,8 (aba) + camara trapezoidal ate 6,1 de profundidade
    const pen = R.draw([-ab, a + 0.1]).lineTo([-ab, a - 1.8]).lineTo([-5.6, a - 1.8]).lineTo([-5.6, a - 3.2])
      .lineTo([-2.6, a - 6.1]).lineTo([2.6, a - 6.1]).lineTo([5.6, a - 3.2]).lineTo([5.6, a - 1.8])
      .lineTo([ab, a - 1.8]).lineTo([ab, a + 0.1]).close();
    return pen.rotate(rotY).sketchOnPlane('YZ', -L / 2 - 1).extrude(L + 2);
  };
  [0, 90, 180, 270].forEach(g => { s = s.cut(fenda(g)); });
  s = s.cut(cilC(4.2, L + 2, [0, 0, 0], 'x'));
  return [{ forma: s, cor: 'aluminio' }];
}
peca('perfil2020_400', { nome: 'Perfil de alumínio 20×20 V-slot série 20, 400 mm', tipo: 'falta', src: 'cat',
  dims: '20 × 20 × 400 mm, canal 6 mm', link: 'https://lista.mercadolivre.com.br/perfil-aluminio-20x20',
  notas: ['NÃO está na planilha. É a viga reta e rígida onde o trilho é parafusado: sem ela o trilho não fica alinhado.',
    'Peça cortado em 400 mm (2 unidades, uma por eixo). Ponta em esquadro: é ela que encosta no bloco de ponta.'] },
() => perfil2020(400));

/* ============================================================== NEMA 17 */
// 17HS4401: flange 42,3, furacao 31, rosca M3 x 4,5, ressalto Ø22 x 2, eixo Ø5 x 24 com chato 0,5
export const NEMA = { a: 42.3, L: 40, furo: 31, boss: 22, bossH: 2, eixo: 5, eixoL: 24, chato: 15 };
function nema17() {
  const { a, L } = NEMA;
  const sec = (z0, z1, ch) => caixa(-a / 2, -a / 2, z0, a / 2, a / 2, z1).chamfer(ch, e => e.inDirection('Z'));
  let frente = sec(-8, 0, 3.6), tras = sec(-L, -L + 8, 3.6);
  const meio = sec(-L + 8.3, -8.3, 4.2);
  [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([sx, sy]) => {
    frente = frente.cut(cil(2.5, 4.6, [sx * NEMA.furo / 2, sy * NEMA.furo / 2, -4.5], 'z'));
    tras = tras.cut(cil(2.5, 4.6, [sx * NEMA.furo / 2, sy * NEMA.furo / 2, -L - 0.1], 'z'));
  });
  const boss = cil(NEMA.boss, NEMA.bossH, [0, 0, 0], 'z');
  // eixo: 24 mm contados da face do flange, ja incluindo os 2 mm do ressalto
  let eixo = cil(NEMA.eixo, NEMA.eixoL, [0, 0, 0], 'z').chamfer(0.3, e => e.inPlane('XY', NEMA.eixoL));
  eixo = eixo.cut(caixa(-3, 2.0, NEMA.eixoL - NEMA.chato, 3, 3, NEMA.eixoL + 1));   // chato (D): 4,5 sobre o chato
  // conector JST-PH 6 vias na lateral, perto da tampa traseira
  const con = caixa(a / 2 - 0.5, -8, -L + 2, a / 2 + 3.2, 8, -L + 9.5).cut(caixa(a / 2 + 0.5, -7, -L + 3, a / 2 + 3.5, 7, -L + 8.5));
  return [{ forma: frente.fuse(tras), cor: 'preto' }, { forma: meio, cor: 'aco' }, { forma: boss.fuse(eixo), cor: 'aluminio' },
    { forma: con, cor: 'branco' }];
}
peca('nema17', { nome: 'Motor de passo NEMA 17 (17HS4401, 40 mm)', src: 'medir', dims: '42,3 × 42,3 × 40 mm, eixo Ø5 × 24 (da face do flange)',
  link: LINK.nema17, linha: 12,
  conferir: ['comprimento do corpo (40 ou 48 mm)', 'eixo: Ø5 com chato (D)? comprimento livre 24 mm?', 'posição do conector'],
  notas: ['O link da planilha é uma BUSCA: o modelo exato depende do anúncio comprado. O mais vendido é o 17HS4401 (40 mm).',
    'Furação frontal 31 × 31, rosca M3 com 4,5 mm de profundidade: parafuso M3×8 numa placa de 5 mm.'] }, nema17);

/* ============================================================== POLIA GT2 20T */
export const GT2P = { dp: 12.73, de: 12.22, flange: 16, cubo: 14, cuboL: 7, dentesL: 7.2, flangeE: 1, total: 16 };
function poliaGT2(furo) {
  // origem: face do CUBO em z=0, polia cresce em +z (cubo -> flange -> dentes -> flange)
  const p = GT2P;
  let cubo = cil(p.cubo, p.cuboL, [0, 0, 0], 'z');
  // 2 parafusos sem cabeca M3 no cubo, a 90 graus
  [0, 90].forEach(g => {
    const pr = cil(3, p.cubo / 2 + 1, [0, 0, p.cuboL / 2], 'x').rotate(g, [0, 0, 0], [0, 0, 1]);
    cubo = cubo.cut(pr);
  });
  const f1 = cil(p.flange, p.flangeE, [0, 0, p.cuboL], 'z');
  let dentes = cil(p.de, p.dentesL, [0, 0, p.cuboL + p.flangeE], 'z');
  for (let i = 0; i < 20; i++) {
    const a = i * 2 * Math.PI / 20;
    dentes = dentes.cut(cil(1.1, p.dentesL + 1, [Math.cos(a) * (p.de / 2 + 0.15), Math.sin(a) * (p.de / 2 + 0.15), p.cuboL + p.flangeE - 0.5], 'z'));
  }
  const f2 = cil(p.flange, p.flangeE, [0, 0, p.cuboL + p.flangeE + p.dentesL], 'z');
  let pol = uniao([cubo, f1, dentes, f2]).cut(cil(furo, p.total + 2, [0, 0, -1], 'z'));
  const grubs = [0, 90].map(g => cil(3, 2.5, [p.cubo / 2 - 3, 0, p.cuboL / 2], 'x').rotate(g, [0, 0, 0], [0, 0, 1]));
  return [{ forma: pol, cor: 'aluminio' }, { forma: uniao(grubs), cor: 'acoEsc' }];
}
peca('polia_gt2_20t_6_35', { nome: 'Polia GT2 20 dentes, furo 6,35 mm (comprada)', src: 'medir', link: LINK.gt2polia, linha: 15,
  dims: 'Ø primitivo 12,73, flange Ø16, largura total 16, furo 6,35',
  conferir: ['furo (6,35 mm, como diz o anúncio?)', 'largura total e posição do cubo'],
  notas: ['ATENÇÃO: o eixo do NEMA 17 tem 5 mm. Esta polia (furo 6,35) fica folgada no motor e bate fora de centro.',
    'Use-a só no eixo da polia tensora se o eixo for de 6,35 mm; no motor use a de furo 5 mm (linha "falta").'] },
() => poliaGT2(6.35));
peca('polia_gt2_20t_5', { nome: 'Polia GT2 20 dentes, furo 5 mm', src: 'cat',
  link: 'https://lista.mercadolivre.com.br/polia-gt2-20-dentes-5mm', dims: 'Ø primitivo 12,73, flange Ø16, largura total 16, furo 5',
  notas: ['Vocês já têm. 2 unidades, uma em cada motor dos eixos. Confira o furo: 5 mm (o eixo do NEMA 17).'] },
() => poliaGT2(5));

/* ============================================================== ROLAMENTO, EIXO, IMA */
function rolamento(d, D, B) {
  const ext = tubo(D, D - (D - d) * 0.45, B, [0, 0, 0], 'z');
  const int = tubo(d + (D - d) * 0.32, d, B, [0, 0, 0], 'z');
  const tampa = tubo(D - (D - d) * 0.42, d + (D - d) * 0.3, B - 0.4, [0, 0, 0.2], 'z');
  return [{ forma: ext.fuse(int), cor: 'aco' }, { forma: tampa, cor: 'acoEsc' }];
}
peca('rol_625zz', { nome: 'Rolamento 625ZZ (elevador)', tipo: 'falta', dims: 'Ø5 × Ø16 × 5 mm', link: 'https://lista.mercadolivre.com.br/rolamento-625zz',
  notas: ['Elevador: vai prensado na polia de baixo. Compre 2 (1 de reserva).'] }, () => rolamento(5, 16, 5));
peca('eixo_5x40', { nome: 'Eixo retificado Ø5 × 40 mm', tipo: 'falta', dims: 'Ø5 h6 × 40 mm',
  link: 'https://lista.mercadolivre.com.br/eixo-retificado-5mm',
  notas: ['Pode ser cortado de uma barra de eixo retificado de 5 mm com serra de arco. Lixe a ponta.'] },
() => [{ forma: cil(5, 40, [0, 0, 0], 'z').chamfer(0.3), cor: 'aco' }]);
peca('ima_6x2_5', { nome: 'Ímã diametral Ø6 × 2,5 (vem com o AS5600)', src: 'cat', dims: 'Ø6 × 2,5 mm, magnetização diametral',
  link: LINK.as5600, notas: ['Diametral: os polos N e S ficam nos LADOS, não nas faces. Ímã comum de geladeira não serve.'] },
() => [{ forma: caixa(-3.1, 0, 0, 3.1, 3.1, 2.5).intersect(cil(6, 2.5, [0, 0, 0], 'z')), cor: 'vermelho' },
  { forma: caixa(-3.1, -3.1, 0, 3.1, 0, 2.5).intersect(cil(6, 2.5, [0, 0, 0], 'z')), cor: 'ima' }]);

/* ============================================================== SOLENOIDES */
/* Referencial: eixo do embolo em z. Carcaca de z=0 a z=C. Ponta de PUXAR em +z: em
   repouso (sem energia) a mola deixa o embolo 'curso' mm para fora; energizado ele recolhe.
   Ponta de EMPURRAR em -z, com a mola e a trava. Furos M3 na face de cima (+y). */
export const SOL = {
  jf0826: { C: 27, L: 22, A: 25, emb: 7.4, curso: 10, tras: 16, furos: [8.5, 18.5] },
  jf0530: { C: 30, L: 15.5, A: 13, emb: 6, curso: 10, tras: 18, furos: [9, 21] },
};
function solenoide(s) {
  const { C, L, A, emb, curso, tras } = s;
  // carcaca em U de chapa (1,2 mm) envolvendo a bobina
  const e = 1.2;
  let car = caixa(-L / 2, -A / 2, 0, L / 2, A / 2, C).cut(caixa(-L / 2 - 1, -A / 2 + e, e, L / 2 + 1, A / 2 - e, C - e));
  s.furos.forEach(z => { car = car.cut(cilC(2.5, 4, [0, A / 2 - e / 2, z], 'y')); car = car.cut(cilC(2.5, 4, [0, -A / 2 + e / 2, z], 'y')); });
  const bob = cil(Math.min(L, A) - 3.5, C - 2 * e - 0.4, [0, 0, e + 0.2], 'z');
  const puxa = cil(emb, curso + 2, [0, 0, C - 2], 'z').fuse(cil(emb + 2.6, 2.4, [0, 0, C + curso - 2.4], 'z'));
  const empurra = cil(emb * 0.5, tras, [0, 0, -tras], 'z');
  const trava = cil(emb * 0.5 + 3, 0.8, [0, 0, -tras + 1.5], 'z');
  const mola = cil(emb * 0.5 + 2.4, tras - 3, [0, 0, -tras + 2.4], 'z').cut(cil(emb * 0.5 + 1.2, tras, [0, 0, -tras], 'z'));
  return [{ forma: car, cor: 'zincado' }, { forma: bob, cor: 'cobre' }, { forma: puxa, cor: 'aco' },
    { forma: empurra.fuse(trava), cor: 'aco' }, { forma: mola, cor: 'mola' },
    // fios saem pela lateral aberta da carcaca (a face de cima e a de baixo ficam livres para os furos)
    { forma: caixaC(L / 2 + 2, 3, C / 2, 4, 1.2, 1.2).fuse(caixaC(L / 2 + 2, -3, C / 2, 4, 1.2, 1.2)), cor: 'fio' }];
}
peca('sol_jf0826', { nome: 'Solenoide push-pull 12 V (JF-0826B) — soltura', src: 'medir', link: LINK.solenoide, linha: 7,
  dims: 'carcaça 27 × 22 × 25 mm, êmbolo Ø7,4, curso 10 mm',
  conferir: ['tamanho da carcaça', 'posição dos 2 furos M3 na carcaça', 'com o solenoide desligado, quanto o êmbolo fica para fora (curso)'],
  notas: ['≈2 A em 12 V: só pode ficar ligado por pulsos curtos (até ~1 s). Diodo 1N4007 em paralelo, faixa no +12 V.',
    'O modelo exato do anúncio não traz desenho: a peça impressa tem rasgos para ajustar a posição dos furos.'] },
() => solenoide(SOL.jf0826));
peca('sol_jf0530', { nome: 'Mini solenoide 12 V (JF-0530B) — comporta', src: 'medir', link: LINK.sol0530, linha: 8,
  dims: 'carcaça 30 × 15,5 × 13 mm, êmbolo Ø6, curso 10 mm',
  conferir: ['tamanho da carcaça', 'posição dos furos (anúncio: Ø2,5 roscado M3)'],
  notas: ['≈300 mA, força ≈5 N. Diodo 1N4007 em paralelo.'] },
() => solenoide(SOL.jf0530));

/* ============================================================== SERVO SG90 */
// TowerPro: corpo 22,2 x 11,8; aba de 32,2 a 16 mm da base; topo ate 31 mm na saida.
// Origem: base do corpo em z=0, centro do corpo em x,y. Eixo de saida em x = -5,2.
export const SG90 = { C: 22.2, L: 11.8, A: 22.7, abas: 32.2, zAba: 16, eAba: 2.5, furos: 27.8, xEixo: -5.2, topo: 31 };
peca('sg90', { nome: 'Micro servo SG90', src: 'medir', link: LINK.sg90, linha: 9,
  dims: '22,2 × 11,8 × 31 mm, abas 32,2 com furos Ø2 a 27,8',
  conferir: ['distância entre os furos das abas (27,5–28 conforme o lote)', 'altura da aba até a base (16 mm)'],
  notas: ['Fio marrom = GND, vermelho = +5 V, laranja = sinal (GPIO do ESP32).',
    'Os parafusos que vêm no saquinho são autoatarraxantes M2: rosqueiam direto no plástico.'] },
() => {
  const S = SG90;
  const corpo = caixaC(0, 0, S.A / 2, S.C, S.L, S.A);
  let abas = caixaC(0, 0, S.zAba + S.eAba / 2, S.abas, S.L, S.eAba);
  [-1, 1].forEach(s => { abas = abas.cut(cilC(2, 6, [s * S.furos / 2, 0, S.zAba], 'z')); });
  const domo = cil(11.8, S.topo - S.A - 4, [S.xEixo, 0, S.A], 'z').fuse(cil(7, 2, [S.xEixo + 7, 0, S.A], 'z'));
  const eixo = cil(4.8, 4, [S.xEixo, 0, S.topo - 4], 'z');
  const fios = caixaC(S.C / 2 + 3, 0, 4, 6, 3.6, 1.2);
  return [{ forma: corpo.fuse(abas).fuse(domo), cor: 'pcbAzul' }, { forma: eixo, cor: 'branco' }, { forma: fios, cor: 'fio' }];
});

/* ============================================================== TUBO ACRILICO */
export const TUBO = { de: 40, di: 36 };
[['tubo_p1', 221], ['tubo_p2', 201], ['tubo_p3', 149]].forEach(([id, L]) =>
  peca(id, { nome: `Tubo acrílico Ø40 × 36, cortado com ${L} mm`, tipo: 'cortar', src: 'cat', link: LINK.tubo, linha: 24,
    dims: `Ø40 externo, Ø36 interno, ${L} mm`,
    notas: ['Corte com serra de dentes finos e fita crepe em volta (não lasca). Lixe a rebarba de dentro: a bola não pode enganchar.',
      'Os 3 trechos somam 571 mm: a planilha tem 1 tubo de 500 mm — falta comprar mais 1.'] },
  () => [{ forma: tubo(TUBO.de, TUBO.di, L, [0, 0, 0], 'x'), cor: 'acrilico' }]));

/* ============================================================== MOTOR DO ELEVADOR */
// JGA25-370: caixa Ø25 (comprimento depende da reducao: 27 na 1:377, 23 na 1:46,8), motor Ø24,4 x 30,8,
// ressalto Ø7 x 2,5, eixo Ø4 com chato (3,5) saindo 12,1 da face, 2 x M3 a 17 mm na face
export const JGA = { cx: 25, cxL: 27, mot: 24.4, motL: 30.8, boss: 7, bossH: 2.5, eixo: 4, eixoL: 12.1, furos: 17 };
peca('jga25', { nome: 'Motor JGA25-370 12 V com redução', src: 'medir', link: LINK.jga25, linha: 19,
  dims: 'Ø25 × 58 mm + eixo Ø4 × 12 (D)',
  conferir: ['comprimento da caixa de redução (varia com a redução)', 'eixo: Ø4 com chato?'],
  notas: ['O comprado (15 rpm, 1:377) é lento demais: troque pelo de 128 rpm (1:46,8) — mesma carcaça e furos, caixa 4 mm mais curta.',
    'Origem: face da caixa em z=0, eixo para +z.'] },
() => {
  const J = JGA;
  let cx = cil(J.cx, J.cxL, [0, 0, -J.cxL], 'z');
  [-1, 1].forEach(s => { cx = cx.cut(cil(2.5, 4.6, [s * J.furos / 2, 0, -4.5], 'z')); });
  const mot = cil(J.mot, J.motL, [0, 0, -J.cxL - J.motL], 'z');
  const tampa = cil(J.mot - 4, 2, [0, 0, -J.cxL - J.motL - 2], 'z');
  const term = uniao([caixaC(5, 0, -J.cxL - J.motL - 4, 1, 3, 4), caixaC(-5, 0, -J.cxL - J.motL - 4, 1, 3, 4)]);
  let eixo = cil(J.boss, J.bossH, [0, 0, 0], 'z').fuse(cil(J.eixo, J.eixoL, [0, 0, 0], 'z'));
  eixo = eixo.cut(caixa(-3, 1.5, J.bossH + 1, 3, 3, J.eixoL + 1));
  return [{ forma: cx, cor: 'zincado' }, { forma: mot.fuse(tampa), cor: 'aco' }, { forma: term, cor: 'latao' }, { forma: eixo, cor: 'aco' }];
});
peca('acoplador_4x5', { nome: 'Acoplador rígido 4 × 5 mm', tipo: 'falta', src: 'cat', dims: 'Ø12 × 20 mm, furos 4 e 5',
  link: 'https://lista.mercadolivre.com.br/acoplador-rigido-4mm-5mm',
  notas: ['Liga o eixo de 4 mm do motor ao eixo de 5 mm da polia de cima. 4 parafusinhos sem cabeça M3.'] },
() => {
  let a = cil(12, 20, [0, 0, 0], 'z').cut(cil(4, 10.5, [0, 0, -0.5], 'z')).cut(cil(5, 10.5, [0, 0, 10], 'z'));
  [5, 15].forEach(z => [0, 90].forEach(g => { a = a.cut(cil(2.5, 7, [0, 0, z], 'x').rotate(g, [0, 0, 0], [0, 0, 1])); }));
  return [{ forma: a, cor: 'aluminio' }];
});
peca('eixo_5x70', { nome: 'Eixo retificado Ø5 × 70 mm', tipo: 'falta', dims: 'Ø5 h6 × 70 mm', link: 'https://lista.mercadolivre.com.br/eixo-retificado-5mm',
  notas: ['Eixo da polia de cima do elevador. Corte de uma barra de 5 mm e lixe as pontas.'] },
() => [{ forma: cil(5, 70, [0, 0, 0], 'z').chamfer(0.3), cor: 'aco' }]);

/* corpo e embolo separados: so para as animacoes de funcionamento (o embolo anda) */
peca('sol_jf0826_corpo', { nome: 'Solenoide JF-0826B (carcaça e bobina)', src: 'medir', link: LINK.solenoide, linha: 7, didatico: true,
  dims: 'carcaça 27 × 22 × 25 mm' }, () => solenoide(SOL.jf0826).filter((c, i) => i < 2 || i === 5));
peca('sol_jf0826_embolo', { nome: 'Solenoide JF-0826B (êmbolo e mola)', src: 'medir', link: LINK.solenoide, linha: 7, didatico: true,
  dims: 'êmbolo Ø7,4, curso 10 mm' }, () => solenoide(SOL.jf0826).filter((c, i) => i >= 2 && i <= 4));
