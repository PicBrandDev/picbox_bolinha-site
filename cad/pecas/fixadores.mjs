/* Ferragens. Referencial local de TODO fixador: a face de apoio da cabeca em z=0,
   cabeca para +z, haste para -z. Para instalar: aponte +z para fora da superficie
   onde a cabeca encosta. Porcas: centradas na origem, eixo z, face de baixo em z=0. */
import { R, cil, sextavado, caixa, uniao, corta, cilC } from '../lib/base.mjs';
import { peca } from '../lib/registro.mjs';

// DIN 912 (cabeca cilindrica sextavado interno) e ISO 7380 (cabeca abaulada)
const D912 = { 2: { dk: 3.8, k: 2, s: 1.5 }, 3: { dk: 5.5, k: 3, s: 2.5 }, 4: { dk: 7, k: 4, s: 3 }, 5: { dk: 8.5, k: 5, s: 4 } };
const I7380 = { 3: { dk: 5.7, k: 1.65, s: 2 }, 5: { dk: 9.5, k: 2.75, s: 3 } };
const PORCA = { 2: { s: 4, m: 1.6 }, 3: { s: 5.5, m: 2.4 }, 5: { s: 8, m: 4 } };

function haste(d, L) {
  // rosca nao e modelada: anel fino a cada passo so na ponta, para ler "parafuso"
  const h = cil(d, L, [0, 0, -L], 'z');
  return h.chamfer(Math.min(0.3, d * 0.1), e => e.inPlane('XY', -L));
}

function din912(M, L) {
  const p = D912[M];
  let cab = cil(p.dk, p.k, [0, 0, 0], 'z').fillet(p.k * 0.12, e => e.inPlane('XY', p.k));
  cab = cab.cut(sextavado(p.s, p.k * 1.2, [0, 0, p.k], 'z'));
  return [{ forma: cab.fuse(haste(M, L)), cor: 'acoEsc' }];
}
function iso7380(M, L) {
  const p = I7380[M];
  const perfil = R.draw([0, 0]).lineTo([p.dk / 2, 0]).lineTo([p.dk / 2, p.k * 0.25])
    .threePointsArcTo([0, p.k], [p.dk * 0.3, p.k * 0.86]).close();
  let cab = perfil.sketchOnPlane('XZ').revolve([0, 0, 1]);
  cab = cab.cut(sextavado(p.s, p.k * 1.4, [0, 0, p.k], 'z'));
  return [{ forma: cab.fuse(haste(M, L)), cor: 'acoEsc' }];
}
function porca(M, nylon) {
  const p = PORCA[M], h = nylon ? p.m * 1.3 : p.m;
  let n = sextavado(p.s, h, [0, 0, h / 2], 'z').chamfer(0.3);
  n = n.cut(cil(M, h + 1, [0, 0, -0.5], 'z'));
  const out = [{ forma: n, cor: 'zincado' }];
  if (nylon) out.push({ forma: cil(M * 1.7, p.m * 0.3, [0, 0, h - 0.01], 'z').cut(cil(M, 2, [0, 0, h - 0.5], 'z')), cor: 'branco' });
  return out;
}
function arruela(M) {
  const de = { 2: 5, 3: 7, 5: 10 }[M], e = { 2: 0.3, 3: 0.5, 5: 1 }[M];
  return [{ forma: cil(de, e, [0, 0, 0], 'z').cut(cil(M + 0.3, e + 1, [0, 0, -0.5], 'z')), cor: 'zincado' }];
}
/* porca martelo (T) para perfil 20x20 fenda 6: entra de lado na fenda e gira 90 graus.
   Local: eixo do furo em z, z=0 = face que encosta por dentro da aba do perfil. */
function porcaMartelo(M) {
  const corpo = R.draw([-5, 0]).lineTo([5, 0]).lineTo([5, -2]).lineTo([3, -4]).lineTo([-3, -4])
    .lineTo([-5, -2]).close().sketchOnPlane('XZ').extrude(-10).translate(0, -5, 0);
  // o ressalto que entra na abertura de 6 mm da fenda
  const ressalto = caixa(-2.8, -5, 0, 2.8, 5, 1.6);
  let n = corpo.fillet(0.4, e => e.inDirection('Y')).fuse(ressalto);
  n = n.cut(cil(M, 8, [0, 0, -5], 'z'));
  return [{ forma: n, cor: 'zincado' }];
}
// parafuso de madeira cabeca chata Phillips 3,5 mm
function madeira(L) {
  const dk = 7, k = 2.2;
  const perfil = R.draw([0, 0]).lineTo([dk / 2, 0]).lineTo([1.75, -k]).lineTo([0, -k]).close();
  let cab = perfil.sketchOnPlane('XZ').revolve([0, 0, 1]);
  cab = cab.cut(caixa(-2, -0.4, -0.9, 2, 0.4, 0.1)).cut(caixa(-0.4, -2, -0.9, 0.4, 2, 0.1));
  const corpo = cil(2.4, L - k - 2.5, [0, 0, -L + 2.5], 'z');
  const ponta = R.draw([0, 0]).lineTo([1.2, 0]).lineTo([0, -2.5]).close().sketchOnPlane('XZ')
    .revolve([0, 0, 1]).translate(0, 0, -L + 2.5);
  // filetes de rosca de madeira (largos, visiveis): sao o que diferencia do M3
  const fios = [];
  for (let z = -k - 1.5; z > -L + 3; z -= 1.6) fios.push(cilC(3.5, 0.5, [0, 0, z], 'z'));
  return [{ forma: uniao([cab, corpo, ponta, ...fios]), cor: 'latao' }];
}

const FIX = { tipo: 'fixador', src: 'cat' };
[[3, 6], [3, 8], [3, 10], [3, 12], [3, 16], [3, 20], [3, 25], [3, 30], [3, 40], [5, 10], [5, 12], [5, 30], [5, 60], [2, 8], [2, 10]].forEach(([M, L]) =>
  peca(`din912_m${M}x${L}`, Object.assign({ nome: `Parafuso M${M}×${L} (DIN 912, cabeça cilíndrica allen)`,
    dims: `M${M} × ${L} mm, cabeça Ø${D912[M].dk} × ${D912[M].k}`, ferramenta: `chave allen ${D912[M].s} mm` }, FIX),
  () => din912(M, L)));
[[3, 8], [5, 8], [5, 10], [5, 20]].forEach(([M, L]) =>
  peca(`iso7380_m${M}x${L}`, Object.assign({ nome: `Parafuso M${M}×${L} (ISO 7380, cabeça abaulada allen)`,
    dims: `M${M} × ${L} mm, cabeça Ø${I7380[M].dk} × ${I7380[M].k}`, ferramenta: `chave allen ${I7380[M].s} mm` }, FIX),
  () => iso7380(M, L)));
[2, 3, 5].forEach(M => peca(`porca_m${M}`, Object.assign({ nome: `Porca sextavada M${M}`, dims: `chave ${PORCA[M].s} mm, altura ${PORCA[M].m} mm` }, FIX), () => porca(M)));
peca('porca_nylon_m5', Object.assign({ nome: 'Porca autotravante M5 (com anel de nylon)', dims: 'chave 8 mm' }, FIX), () => porca(5, true));
[2, 3, 5].forEach(M => peca(`arruela_m${M}`, Object.assign({ nome: `Arruela lisa M${M}`, dims: { 2: 'Ø5 × 0,3', 3: 'Ø7 × 0,5', 5: 'Ø10 × 1' }[M] }, FIX), () => arruela(M)));
[3, 5].forEach(M => peca(`porca_martelo_m${M}`, Object.assign({ nome: `Porca martelo M${M} para perfil 2020`,
  dims: 'perfil série 20, fenda 6 mm', notas: ['Entra de lado na fenda do perfil e gira 1/4 de volta ao apertar o parafuso.'] }, FIX),
  () => porcaMartelo(M)));
[16, 20, 25].forEach(L => peca(`madeira_3_5x${L}`, Object.assign({ nome: `Parafuso para madeira 3,5×${L} cabeça chata`,
  dims: `Ø3,5 × ${L} mm, Phillips`, ferramenta: 'chave Phillips nº 2' }, FIX), () => madeira(L)));
