/* MODULO 5 — ELEVADOR de cacambas (canto traseiro direito do gabinete)

   Referencial: o da MAQUINA — origem no centro do piso, z = altura do chao.
   A correia anda num plano YZ em x = 172: sobe pelo ramo de TRAS (y = 148 + R) e desce
   pela frente. No topo a capa segura a bola ate 45 graus depois do alto; ali ela sai do
   copo para a calha de entrega, que leva ate a entrada do magazine (y = 65, x = 95).

   Cotas que mandam:
     - motor: NEMA 17 direto na polia de cima (o JGA25 de 15 rpm era lento demais)
     - correia GT2 10 mm FECHADA de 1056 mm -> distancia entre polias 484 (polias 44 dentes,
       primitivo 28,01 — o mesmo Ø28 do modelo)
     - topo: a calha de entrega chega na entrada do magazine a 1612 mm, caindo 4 graus
     - fundo de tras: parede do gabinete em y = 207; a tampa de acrilico fica em 203..206
   Caçamba presa SEM furar a correia: 2 parafusos M2 passam rente as bordas da correia e
   duas arruelas M2 seguram a borda por dentro. A polia tem so 6 mm de dentes, entao as
   arruelas passam ao lado dela. */
import { R, caixa, caixaC, cil, cilC, uniao, sextavado, FOLGA } from '../lib/base.mjs';
import { peca, inst } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';
import { PROJ } from '../lib/projeto.mjs';
import { NEMA, LINK } from '../pecas/comprados.mjs';
import { correiaLaco } from '../pecas/correia.mjs';
import { retaU, arcoU, MG } from './magazine.mjs';

const RB = PROJ.bolaD / 2, k = Math.tan(4 * Math.PI / 180);
const A = 1530;                                   // altura do eixo do trilho A (referencial do magazine)
export const EL = {
  x: 172, y: 148, zb: 1125, C: 484, rp: 28.01 / 2, Ro: 14.5,
  placaE: 6, xPe: 144, xPd: 194,                   // faces internas das laterais: 150 e 194
  rCapa: 55, eCapa: 3, nCac: 12, yTampa: 53.5,     // tampa 1 mm alem da bola (200,0); a aba dela cabe antes da parede (207)
};
EL.zt = EL.zb + EL.C;
EL.L = 2 * EL.C + 2 * Math.PI * EL.Ro;
const IMP = { tipo: 'impresso', src: 'est', material: 'PETG' };

/* ---------------------------------------------------------------- polias 44 dentes */
function polia44(tipo) {
  // eixo em z, dentes de z = 0 a 6 (largura da faixa de dentes: 6 — as arruelas da cacamba passam ao lado)
  const de = 28.01 - 0.508;
  let p = cil(de, 6, [0, 0, 0], 'z');
  for (let i = 0; i < 44; i++) {
    const a = i * 2 * Math.PI / 44;
    p = p.cut(cil(1.15, 7, [Math.cos(a) * (de / 2 + 0.1), Math.sin(a) * (de / 2 + 0.1), -0.5], 'z'));
  }
  if (tipo === 'motora') {
    // cubo comprido: vai da polia ate perto da lateral e abraca a ponta do eixo do NEMA (11,5 mm)
    p = p.fuse(cil(14, 18.5, [0, 0, -18.5], 'z'));
    p = p.cut(cil(5.1, 30, [0, 0, -19.5], 'z'));
    p = p.cut(cil(FOLGA.m3, 8, [0, 0, -12], 'x'));                              // parafuso sem cabeca no chato do eixo
    p = p.cut(caixa(3, -FOLGA.m3PorcaAF / 2, -15.5, 5.6, FOLGA.m3PorcaAF / 2, -8.5)); // porca M3 encaixada
  } else {
    p = p.cut(cil(16.1, 6.5, [0, 0, -0.25], 'z'));                               // rolamento 625 dentro
  }
  return p;
}
peca('elev_polia_motora', Object.assign({}, IMP, { nome: 'Polia GT2 44 dentes motora (topo)', dims: 'Ø27,5 × 6 + cubo Ø14 × 18,5',
  imprimir: { rot: [] }, impressao: { preenchimento: '100 %', paredes: 4, suportes: 'não', tempo: '40 min' },
  notas: ['44 dentes: Ø primitivo 28,01 mm, o Ø28 do projeto. Imprima com camada 0,12 mm para os dentes saírem.',
    'Só 6 mm de dentes numa correia de 10: as bordas da correia ficam livres para as arruelas das caçambas.'] }),
() => [{ forma: polia44('motora'), cor: 'impresso2' }]);
peca('elev_polia_livre', Object.assign({}, IMP, { nome: 'Polia GT2 44 dentes livre (fundo)', dims: 'Ø27,5 × 6',
  imprimir: { rot: [] }, impressao: { preenchimento: '100 %', paredes: 4, suportes: 'não', tempo: '30 min' },
  notas: ['Leva um rolamento 625 prensado no centro e gira no parafuso M5 do tensor.'] }),
() => [{ forma: polia44('livre'), cor: 'impresso2' }]);

/* ---------------------------------------------------------------- cacamba */
// local: x atravessa a correia, y = para fora da correia, z = sentido de marcha
function cacamba() {
  const W = 20;                                                   // meia-largura externa (interna 36)
  let c = uniao([
    caixa(-10, 0, -4, 10, 2, 4),                                  // base na correia
    caixa(-W, 0, -4, W, 2, 14),                                   // costas
    caixa(-W, 2, -4, W, 38, -1),                                  // fundo (a bola apoia aqui na subida)
    caixa(-W, 2, -4, -W + 2, 38, 14), caixa(W - 2, 2, -4, W, 38, 14),   // laterais
    caixa(-W, 35.5, -1, W, 38, 12),                               // aba da ponta
  ]);
  [-6.5, 6.5].forEach(x => { c = c.cut(cilC(FOLGA.m2, 10, [x, 1, 0], 'y')); });
  [-6.5, 6.5].forEach(x => { c = c.cut(sextavado(4.3, 2, [x, 2.9, 0], 'y')); });   // porca M2 por dentro
  return c;
}
peca('elev_cacamba', Object.assign({}, IMP, { nome: 'Caçamba do elevador', dims: '40 × 38 × 18 mm',
  imprimir: { rot: [['x', -90]] }, impressao: { preenchimento: '40 %', paredes: 3, suportes: 'não', tempo: '35 min' },
  notas: ['12 unidades (a planilha previa 14). Base de só 8 mm ao longo da correia: ela dobra em volta da polia de 28 sem a caçamba atrapalhar.',
    'Presa por 2 parafusos M2×8 que passam rente às bordas da correia; por dentro, uma arruela M2 em cada um segura a borda.'] }),
() => [{ forma: cacamba(), cor: 'impresso' }]);

/* ---------------------------------------------------------------- laterais, mancal, motor */
const Z0 = EL.zb - EL.rCapa - EL.eCapa - 8, Z1 = EL.zt + EL.rCapa + EL.eCapa + 6;
function lateral(lado) {
  let p = caixa(0, 94, Z0, EL.placaE, 205, Z1);
  // furo do eixo de cima (so na esquerda) e rasgo do tensor de baixo
  if (lado < 0) p = p.cut(cilC(9, 20, [3, EL.y, EL.zt], 'x'));        // passagem do eixo do NEMA
  p = p.cut(caixa(-1, EL.y - 2.75, EL.zb - 10, 8, EL.y + 2.75, EL.zb + 10));
  return p;
}
peca('elev_lateral_d', { nome: 'Lateral DIREITA da coluna (MDF 6 mm)', tipo: 'cortar', src: 'est', dims: `111 × 6 × ${(Z1 - Z0).toFixed(0)} mm`,
  link: 'https://lista.mercadolivre.com.br/mdf-6mm-sob-medida', notas: ['Igual à esquerda, só sem o furo do eixo de cima.'] },
() => [{ forma: lateral(1), cor: 'mdf' }]);
peca('elev_lateral', { nome: 'Lateral ESQUERDA da coluna (MDF 6 mm)', tipo: 'cortar', src: 'est', dims: `111 × 6 × ${(Z1 - Z0).toFixed(0)} mm`,
  link: 'https://lista.mercadolivre.com.br/mdf-6mm-sob-medida',
  notas: ['2 peças. Na de baixo, um rasgo vertical de 5,5 × 20 mm (3 furos de 5,5 e lima): é por onde o eixo da polia de baixo desce para esticar a correia.',
    'Só a lateral ESQUERDA tem o furo de 5,6 mm do eixo de cima.'] },
() => [{ forma: lateral(-1), cor: 'mdf' }]);
/* NEMA 17 direto na polia de cima: o eixo de 24 mm atravessa a lateral e entra 11,5 mm no cubo
   da polia. Sem acoplador, sem eixo extra, sem mancal: o rolamento e o do proprio motor. */
const XF = EL.xPe - 6;                                   // face do flange do motor (x = 138)
function suporteNema() {
  let s = caixa(XF, EL.y - 27, EL.zt - 27, EL.xPe, EL.y + 27, EL.zt + 27).fillet(3, e => e.inDirection('X'));
  s = s.cut(cilC(NEMA.boss + 0.6, 20, [XF, EL.y, EL.zt], 'x'));
  [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([a, b]) => {
    s = s.cut(cilC(FOLGA.m3, 20, [XF, EL.y + a * NEMA.furo / 2, EL.zt + b * NEMA.furo / 2], 'x'));
    // cabeca do M3 rebaixada do lado da lateral: o motor e preso no suporte ANTES de ir para a coluna
    s = s.cut(cil(FOLGA.m3Cab, FOLGA.m3CabH, [EL.xPe - FOLGA.m3CabH, EL.y + a * NEMA.furo / 2, EL.zt + b * NEMA.furo / 2], 'x'));
    // parafuso de madeira 3,5x12 nos cantos: 6 do suporte + 6 do MDF, a ponta morre rente por dentro
    s = s.cut(cilC(FOLGA.madeira, 20, [XF, EL.y + a * 22.5, EL.zt + b * 22.5], 'x'));
  });
  return s;
}
peca('elev_suporte_nema', Object.assign({}, IMP, { nome: 'Suporte do NEMA 17 do elevador', dims: '54 × 54 × 6 mm',
  imprimir: { rot: [['y', 90]] }, impressao: { preenchimento: '60 %', paredes: 4, suportes: 'não', tempo: '50 min' },
  notas: ['O motor é parafusado no suporte primeiro (4 × M3×6 com a cabeça rebaixada do lado da lateral); depois o conjunto vai na lateral com 4 parafusos de madeira 3,5×12.',
    'Por que 6 mm: com a lateral de 6 mm, o eixo de 24 mm do NEMA passa e ainda entra 11,5 mm no cubo da polia.'] }),
() => [{ forma: suporteNema(), cor: 'impresso' }]);

/* ---------------------------------------------------------------- capa, concha, tampa, calha */
function arcoCasca(r0, r1, a0, a1, zc, larg) {
  // casca cilindrica em volta do eixo x da polia (angulo medido de +y para +z)
  const perfil = R.drawRectangle(r1 - r0, larg).translate((r0 + r1) / 2, 0);
  // em torno de -Y o giro vai de +X para +Z; depois x local -> y do mundo, largura -> x
  let s = perfil.sketchOnPlane('XY').revolve([0, -1, 0], { angle: a1 - a0 });
  s = s.rotate(-a0, [0, 0, 0], [0, 1, 0]);                         // inicio em a0 (de +X para +Z)
  s = s.rotate(90, [0, 0, 0], [0, 0, 1]);
  return s.translate(EL.x, EL.y, zc);
}
const LARG = EL.xPd - EL.xPe - EL.placaE - 0.6;                     // 43,4: entre as laterais
function capa() {
  let c = arcoCasca(EL.rCapa, EL.rCapa + EL.eCapa, 0, 135, EL.zt, LARG);
  // aba que prende a ponta de cima da tampa de acrilico
  c = c.fuse(caixa(EL.x - LARG / 2, EL.y + EL.yTampa, EL.zt - 12, EL.x + LARG / 2, EL.y + EL.yTampa + 5, EL.zt));
  c = c.cut(caixa(EL.x - LARG / 2 - 1, EL.y + EL.yTampa, EL.zt - 13, EL.x + LARG / 2 + 1, EL.y + EL.yTampa + 3.2, EL.zt - 0.5));
  // orelhas para parafusar nas laterais
  [-1, 1].forEach(s => { c = c.fuse(caixa(EL.x + s * LARG / 2, EL.y - 8, EL.zt + EL.rCapa - 10, EL.x + s * (LARG / 2 - 0.01), EL.y + 8, EL.zt + EL.rCapa + 3)); });
  return c;
}
function concha() {
  let c = arcoCasca(EL.rCapa, EL.rCapa + EL.eCapa, 200, 360, EL.zb, LARG);
  c = c.fuse(caixa(EL.x - LARG / 2, EL.y + EL.yTampa, EL.zb, EL.x + LARG / 2, EL.y + EL.yTampa + 5, EL.zb + 12));
  c = c.cut(caixa(EL.x - LARG / 2 - 1, EL.y + EL.yTampa, EL.zb + 0.5, EL.x + LARG / 2 + 1, EL.y + EL.yTampa + 3.2, EL.zb + 13));
  // bico de entrada: a calha de retorno da bandeja chega aqui pela frente
  const a = 200 * Math.PI / 180, ye = EL.y + (EL.rCapa + 1.5) * Math.cos(a), ze = EL.zb + (EL.rCapa + 1.5) * Math.sin(a);
  c = c.fuse(caixa(EL.x - LARG / 2, ye - 30, ze - 3, EL.x + LARG / 2, ye + 2, ze));
  return c;
}
peca('elev_capa', Object.assign({}, IMP, { nome: 'Capa do topo do elevador', dims: '43 × 116 × 58 mm',
  imprimir: { rot: [['y', 90]] }, impressao: { preenchimento: '30 %', paredes: 3, suportes: 'não (de lado)', tempo: '≈ 2 h' },
  notas: ['Segura a bola dentro da caçamba na curva de cima e ACABA 45° depois do alto: ali a bola cai para a calha de entrega.',
    'Se na bancada a bola não cair certinho na calha, é a ponta desta peça que se ajusta (lixar ou reimprimir mais curta).'] }),
() => [{ forma: capa().translate(-EL.x, -EL.y, -EL.zt), cor: 'impresso' }]);
peca('elev_concha', Object.assign({}, IMP, { nome: 'Concha do fundo do elevador', dims: '43 × 116 × 60 mm',
  imprimir: { rot: [['y', 90]] }, impressao: { preenchimento: '30 %', paredes: 3, suportes: 'não (de lado)', tempo: '≈ 2 h' },
  notas: ['A bola que volta da bandeja entra pelo bico da frente, rola até o fundo e espera ali: a próxima caçamba passa e a leva.'] }),
() => [{ forma: concha().translate(-EL.x, -EL.y, -EL.zb), cor: 'impresso' }]);
peca('elev_tampa', { nome: 'Tampa do ramo de subida (acrílico 3 mm)', tipo: 'cortar', src: 'est', dims: `${LARG.toFixed(0)} × 3 × 484 mm`,
  link: 'https://www.mercadolivre.com.br/chapa-placa-acrilico-sob-medida-3mm/up/MLBU729458147', linha: 25,
  notas: ['Tira de acrílico 3 mm (da mesma chapa da comporta). Encaixa na aba da capa em cima e na da concha embaixo.',
    'Transparente de propósito: dá para ver as bolas subindo.'] },
() => [{ forma: caixa(-LARG / 2 + 0.2, 0, 0, LARG / 2 - 0.2, 3, EL.C - 1), cor: 'acrilico' }]);

// calha de entrega: sai do topo pela frente e entra na entrada do magazine (x 95, y 65, ball center 1612)
const zEntradaMag = A + MG.zP1(MG.xIn + 35);
const C1 = [EL.x, 93], C2 = [EL.x, 87], CR = 22, C3 = [EL.x - CR, 65], C4 = [MG.xIn + 35.3, 65];
const LCAL = (C1[1] - C2[1]) + Math.PI * CR / 2 + (C3[0] - C4[0]);
const zC = s => zEntradaMag + (LCAL - s) * k;                          // centro da bola ao longo da calha
function calhaEntrega() {
  const s1 = C1[1] - C2[1], s2 = s1 + Math.PI * CR / 2;
  const partes = [retaU([C1[0], C1[1] + 20, zC(0)], [C2[0], C2[1], zC(s1)]),
    arcoU(EL.x - CR, C2[1], CR, 270, 360, (zC(s1) + zC(s2)) / 2), retaU([C3[0], C3[1], zC(s2)], [C4[0], C4[1], zC(LCAL)])];
  const int = [retaU([C1[0], C1[1] + 20, zC(0)], [C2[0], C2[1], zC(s1)], true),
    arcoU(EL.x - CR, C2[1], CR, 270, 360, (zC(s1) + zC(s2)) / 2, true), retaU([C3[0], C3[1], zC(s2)], [C4[0], C4[1], zC(LCAL)], true)];
  let c = uniao(partes).cut(uniao(int));
  // a ponta da calha nao pode entrar no volume varrido pelas cacambas da descida
  c = c.intersect(caixa(-500, -500, 0, 500, EL.y - EL.Ro - 38 - 1.5, 3000));
  return c;
}
peca('elev_calha_entrega', Object.assign({}, IMP, { nome: 'Calha de entrega (elevador → magazine)', dims: '≈ 120 × 70 × 60 mm',
  imprimir: { rot: [] }, impressao: { preenchimento: '30 %', paredes: 3, suportes: 'não (canal para cima)', tempo: '≈ 3 h' },
  notas: ['Recebe a bola que sai da caçamba no topo e leva até a entrada do magazine, caindo 4°.',
    'A ponta de recepção fica 1,5 mm fora do volume que as caçambas varrem na descida.'] }),
() => [{ forma: calhaEntrega().translate(-EL.x, -80, -EL.zt), cor: 'impresso' }]);

/* ---------------------------------------------------------------- correia (laco fechado) */
peca('correia_elev', { nome: 'Correia GT2 10 mm FECHADA (sem emenda), 1056 mm', tipo: 'falta', src: 'cat',
  dims: '10 mm de largura, 528 dentes (1056 mm)', link: 'https://lista.mercadolivre.com.br/correia-gt2-fechada-10mm',
  notas: ['Substitui a correia aberta + emenda da planilha: emenda rígida não passa na polia de 28 mm.',
    'Se só achar outro comprimento: distância entre polias = (comprimento − 88) / 2. O rasgo do tensor dá ±10 mm.'] },
() => correiaLaco({ x1: 0, x2: EL.C, rp: EL.rp, larg: 10, y0: -5, xa: EL.C / 2, xb: EL.C / 2 }).map(f => ({ forma: f, cor: 'correia' })));

/* ---------------------------------------------------------------- instancias */
function posCacamba(s) {
  const { C, Ro, y, zb, zt } = EL;
  s = ((s % EL.L) + EL.L) % EL.L;
  const arco = Math.PI * Ro;
  if (s < C) return { y: y + Ro, z: zb + s, phi: 0 };
  if (s < C + arco) { const a = (s - C) / Ro; return { y: y + Ro * Math.cos(a), z: zt + Ro * Math.sin(a), phi: a * 180 / Math.PI }; }
  if (s < 2 * C + arco) return { y: y - Ro, z: zt - (s - C - arco), phi: 180 };
  const a = Math.PI + (s - 2 * C - arco) / Ro; return { y: y + Ro * Math.cos(a), z: zb + Ro * Math.sin(a), phi: a * 180 / Math.PI };
}
function instancias() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  const r = T.of();
  // contexto: ponta do magazine (referencial do eixo A -> maquina: z + 1530)
  add('ctx_p1', 'tubo_p1', r.ry(-4).t(MG.xL, MG.y, MG.zP1(MG.xL)).t(0, 0, A), { contexto: true });
  add('ctx_entrada', 'mag_entrada', r.ry(-4).t(MG.xIn, MG.y, MG.zP1(MG.xIn)).t(0, 0, A), { contexto: true });
  // laterais
  add('lat_e', 'elev_lateral', r.t(EL.xPe, 0, 0));
  add('lat_d', 'elev_lateral_d', r.t(EL.xPd, 0, 0));
  // motor do topo: NEMA 17 no suporte, eixo direto na polia
  add('suporte_motor', 'elev_suporte_nema', r);
  add('motor', 'nema17', r.ry(90).t(XF, EL.y, EL.zt));
  [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([a, b], i) => {
    add('p_motor_' + i, 'din912_m3x6', r.ry(90).t(EL.xPe - FOLGA.m3CabH, EL.y + a * NEMA.furo / 2, EL.zt + b * NEMA.furo / 2));
    add('mad_motor_' + i, 'madeira_3_5x12', r.ry(-90).t(XF, EL.y + a * 22.5, EL.zt + b * 22.5));
  });
  add('polia_cima', 'elev_polia_motora', r.ry(90).t(EL.x - 3, EL.y, EL.zt));
  // eixo de baixo: parafuso M5x60 atravessando as laterais, polia livre com 625, espacadores
  add('polia_baixo', 'elev_polia_livre', r.ry(90).t(EL.x - 3, EL.y, EL.zb));
  add('rol_b', 'rol_625zz', r.ry(90).t(EL.x - 2.5, EL.y, EL.zb));
  add('p_m5_baixo', 'din912_m5x60', r.ry(-90).t(EL.xPe, EL.y, EL.zb));
  add('porca_baixo', 'porca_nylon_m5', r.ry(90).t(EL.xPd + EL.placaE, EL.y, EL.zb));
  [[EL.xPe + EL.placaE, EL.x - 2.5], [EL.x + 2.5, EL.xPd]].forEach(([a, b], i) =>
    add('esp_b' + i, 'elev_espacador', r.ry(90).t(a, EL.y, EL.zb), { comp: b - a }));
  // correia: laco do eixo x local (0 -> C) levado para a vertical no plano YZ
  add('correia', 'correia_elev', r.ry(-90).rz(90).t(EL.x, EL.y, EL.zb), { semColisao: true });
  // cacambas e seus parafusos/arruelas
  for (let i = 0; i < EL.nCac; i++) {
    const p = posCacamba(i * EL.L / EL.nCac + 40);
    const tc = r.rx(p.phi).t(EL.x, p.y, p.z);
    add('cac_' + i, 'elev_cacamba', tc);
    [-6.5, 6.5].forEach((x, j) => {
      // por dentro da correia: cabeca + arruela na borda; por fora: a porca no encaixe da cacamba
      add(`p_cac_${i}_${j}`, 'din912_m2x8', r.rx(90).t(x, -1.68, 0).em(tc));
      add(`arr_cac_${i}_${j}`, 'arruela_m2', r.rx(90).t(x, -1.38, 0).em(tc));
      add(`porca_cac_${i}_${j}`, 'porca_m2', r.rx(-90).t(x, 2, 0).em(tc));
    });
  }
  // capa, concha, tampa, calha de entrega
  add('capa', 'elev_capa', r.t(EL.x, EL.y, EL.zt));
  add('concha', 'elev_concha', r.t(EL.x, EL.y, EL.zb));
  add('tampa', 'elev_tampa', r.t(EL.x, EL.y + EL.yTampa, EL.zb + 0.5));
  add('calha', 'elev_calha_entrega', r.t(EL.x, 80, EL.zt));
  // bolas subindo em 3 cacambas
  [1, 2, 3].forEach(i => {
    const p = posCacamba(i * EL.L / EL.nCac + 40);
    if (p.phi === 0) add('bola_' + i, 'bola35', r.t(EL.x, p.y + 20, p.z + 16.5), { semColisao: true });
  });
  return I;
}
peca('elev_espacador', Object.assign({}, IMP, { nome: 'Espaçador do eixo de baixo', dims: 'Ø10 × 19,5 mm', cor: 'impresso2',
  imprimir: { rot: [] }, impressao: { preenchimento: '100 %', paredes: 4, suportes: 'não', tempo: '10 min' },
  notas: ['2 unidades: centralizam a polia de baixo entre as laterais, encostando só no anel de dentro do rolamento.'] }),
() => [{ forma: cil(10, 19.4, [0, 0, 0], 'z').cut(cil(FOLGA.m5, 21, [0, 0, -1], 'z')), cor: 'impresso2' }]);

export function moduloElevador() {
  const I = instancias();
  const ids = pre => I.filter(i => i.id.startsWith(pre)).map(i => i.id);
  const fx = ['p_cac_', 'arr_cac_', 'porca_cac_'];
  return {
    id: 'elevador', nome: 'Elevador',
    subtitulo: 'Canto traseiro direito. Leva a bola do fundo (1125 mm) até a entrada do magazine (1612 mm).',
    resumo: 'Correia GT2 10 mm fechada com 12 caçambas impressas, polias de 44 dentes impressas, NEMA 17 direto na polia de cima, capa, concha e calha de entrega.',
    tempo: '≈ 2 h 30',
    instancias: I,
    contexto: ids('ctx_'),
    // uma cacamba dando a volta inteira, de 15 em 15 mm, contra tudo o que e fixo
    trajetoria: [{ peca: 'elev_cacamba', contra: ['lat_e', 'lat_d', 'capa', 'concha', 'tampa', 'calha', 'suporte_motor', 'ctx_entrada', 'ctx_p1'],
      Ts: Array.from({ length: Math.ceil(EL.L / 15) }, (_, n) => { const p = posCacamba(n * 15); return T.of().rx(p.phi).t(EL.x, p.y, p.z); }),
      rotulos: Array.from({ length: Math.ceil(EL.L / 15) }, (_, n) => 's=' + n * 15) }],
    passos: [
      { titulo: 'Conheça as peças', mostra: 'tudo', explode: 0.5, vista: 'iso',
        texto: 'A coluna são duas laterais de MDF. A correia sobe por trás (com as bolas nas caçambas), passa por cima da polia motora e desce pela frente vazia. No alto, a bola sai da caçamba e cai na calha que leva ao magazine (em cinza claro).',
        atencao: ['Motor: NEMA 17 (o mesmo dos eixos) num 3º TMC2209 do kit de 4 — a velocidade sai do firmware. A 100 rpm a esteira anda 147 mm/s.',
          'A correia precisa ser FECHADA (sem emenda), 1056 mm. A da planilha (aberta + emenda de alumínio) não passa na polia.'] },
      { titulo: 'Laterais de MDF', novos: ['lat_e', 'lat_d'], vista: 'iso',
        texto: `Corte 2 laterais de MDF 6 mm com 111 × ${(Z1 - Z0).toFixed(0)} mm. Na esquerda, faça o furo de 5,6 mm do eixo de cima (centro a ${(EL.y - 94).toFixed(0)} mm da frente e ${(EL.zt - Z0).toFixed(0)} mm da base). Nas duas, um rasgo vertical de 5,5 × 20 mm para o eixo de baixo (centro a ${(EL.y - 94).toFixed(0)} mm da frente e ${(EL.zb - Z0).toFixed(0)} mm da base). A base das laterais fica a ${Z0.toFixed(0)} mm do chão.`,
        ferramentas: ['serra', 'furadeira', 'broca 5,5 mm', 'lima'] },
      { titulo: 'Motor no topo', novos: ['suporte_motor', 'motor', ...ids('p_motor_'), ...ids('mad_motor_')], vista: 'esquerda',
        texto: 'Prenda o NEMA 17 no suporte impresso com 4 parafusos M3×6 — as cabeças ficam rebaixadas do lado que encosta na lateral. Depois passe o eixo do motor pelo furo de 9 mm da lateral esquerda e parafuse o suporte nela com 4 parafusos de madeira 3,5×12.',
        ferramentas: ['chave allen 2,5 mm', 'chave Phillips nº 2'],
        atencao: ['Parafuso de madeira maior que 12 mm fura a lateral por dentro e as caçambas batem nele.'],
        confira: ['O eixo do motor aparece 12 mm para dentro da coluna.'] },
      { titulo: 'Polias', novos: ['polia_cima', 'polia_baixo', 'rol_b', 'p_m5_baixo', 'porca_baixo', ...ids('esp_b')], vista: 'esquerda', zoom: ['polia_cima', 'polia_baixo'],
        texto: 'Polia motora direto no eixo do NEMA: o cubo comprido abraça os 11,5 mm de eixo que passam da lateral; aperte o parafusinho M3 sobre a parte chata do eixo. Na de baixo, prense um rolamento 625 e passe o parafuso M5×60 pelo rasgo da lateral esquerda, espaçador, polia, espaçador, rasgo da lateral direita, porca autotravante — sem apertar ainda.',
        ferramentas: ['chave allen 2,5 e 4 mm', 'chave 8 mm'] },
      { titulo: 'Caçambas na correia', novos: ['correia', ...ids('cac_'), ...I.filter(i => fx.some(f => i.id.startsWith(f))).map(i => i.id)], vista: 'iso',
        texto: 'Com a correia FORA da máquina, prenda as 12 caçambas a cada 44 dentes (88 mm). Cada caçamba: base encostada no dorso da correia (lado liso), 2 parafusos M2×8 passando rente às bordas, por dentro uma arruela M2 que segura a borda da correia e a porca. Fundo de cada caçamba para o mesmo lado.',
        ferramentas: ['chave Phillips pequena', 'alicate de bico'],
        atencao: ['Não fure a correia: ela tem alma de aço; o furo corta os cabos e ela rompe.'],
        confira: ['Contando dentes: 44 entre caçambas, todas iguais.'] },
      { titulo: 'Correia nas polias e tensão', vista: 'esquerda', zoom: ['polia_baixo'],
        texto: 'Passe o laço pelas duas polias (caçambas para fora, subindo por TRÁS). Puxe o eixo de baixo para baixo no rasgo até a correia ficar firme (afunda ~5 mm com o dedo no meio) e aperte a porca do M5.',
        ferramentas: ['chave allen 4 mm', 'chave 8 mm'],
        confira: ['Girando o eixo de cima à mão, as caçambas passam pelas polias sem encostar nas laterais.'] },
      { titulo: 'Concha, tampa e capa', novos: ['concha', 'tampa', 'capa'], vista: 'tras',
        texto: 'Parafuse a concha embaixo, encaixe a tira de acrílico na aba da concha, apoie a capa em cima com a aba dela abraçando a ponta de cima da tampa e parafuse as orelhas da capa nas laterais.',
        ferramentas: ['chave Phillips nº 2'] },
      { titulo: 'Calha de entrega e teste', novos: ['calha', ...ids('bola_')], vista: 'iso', zoom: ['calha', 'capa'],
        texto: 'Parafuse a calha de entrega na frente do topo, com a ponta apoiada na entrada do magazine. Ligue o motor e jogue bolas na concha, uma por vez: cada uma tem que subir, sair no alto e rolar até o tubo P1.',
        confira: ['50 bolas seguidas sem nenhuma presa.', 'Volta completa da correia em ~7 s (NEMA a 100 rpm).'],
        atencao: ['Se a bola não cair na calha no topo, ajuste a ponta da capa (é ela que decide onde a bola sai) — isto é [H]: validar na bancada.'] },
    ],
  };
}
