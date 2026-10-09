/* Base do CAD da montagem guiada.

   Unidade: MILIMETRO. Referencial do CAD: Z para cima, X para a direita do jogador,
   Y para o FUNDO da maquina (frente = -Y). O visualizador (three.js) usa Y para cima
   e +Z para o jogador; a conversao acontece so na exportacao (glb.mjs).

   As operacoes do replicad CONSOMEM as formas de entrada. Toda funcao daqui devolve
   forma nova; quem precisar reaproveitar uma forma usa .clone(). */
import opencascade from 'replicad-opencascadejs';
import * as R from 'replicad';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
let pronto = false;
export async function iniciaOC() {
  if (pronto) return;
  const wasm = require.resolve('replicad-opencascadejs/wasm');
  R.setOC(await opencascade({ locateFile: () => wasm, print: () => {}, printErr: () => {} }));
  pronto = true;
}
export { R };

/* ---------- primitivas ---------- */
// caixa por dois cantos
export const caixa = (x0, y0, z0, x1, y1, z1) =>
  R.makeBox([Math.min(x0, x1), Math.min(y0, y1), Math.min(z0, z1)],
            [Math.max(x0, x1), Math.max(y0, y1), Math.max(z0, z1)]);
// caixa pelo centro e pelas medidas
export const caixaC = (cx, cy, cz, w, d, h) =>
  caixa(cx - w / 2, cy - d / 2, cz - h / 2, cx + w / 2, cy + d / 2, cz + h / 2);

const DIR = { x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1], '-x': [-1, 0, 0], '-y': [0, -1, 0], '-z': [0, 0, -1] };
// cilindro: base no ponto p, crescendo h na direcao dada
export const cil = (d, h, p, dir) => R.makeCylinder(d / 2, h, p || [0, 0, 0], DIR[dir || 'z'] || dir);
// cilindro centrado no ponto p, ao longo do eixo
export function cilC(d, h, p, eixo) {
  const v = DIR[eixo || 'z'];
  return cil(d, h, [p[0] - v[0] * h / 2, p[1] - v[1] * h / 2, p[2] - v[2] * h / 2], eixo || 'z');
}
// tubo (cilindro oco)
export const tubo = (dExt, dInt, h, p, dir) => cil(dExt, h, p, dir).cut(cil(dInt, h + 0.02, p, dir).translate(
  ...(DIR[dir || 'z'].map(c => -c * 0.01))));

// prisma sextavado: 'af' = medida entre faces (chave)
export function sextavado(af, h, p, eixo) {
  const raio = af / Math.sqrt(3);
  let s = R.drawPolysides(raio, 6).sketchOnPlane('XY').extrude(h);
  s = s.translate(0, 0, -h / 2);
  if (eixo === 'x') s = s.rotate(90, [0, 0, 0], [0, 1, 0]);
  if (eixo === 'y') s = s.rotate(90, [0, 0, 0], [1, 0, 0]);
  return s.translate(...(p || [0, 0, 0]));
}

// perfil 2D (pontos [x,y]) extrudado em Z a partir de z0
export function extrudaPoli(pts, h, z0) {
  let pen = R.draw(pts[0]);
  for (let i = 1; i < pts.length; i++) pen = pen.lineTo(pts[i]);
  return pen.close().sketchOnPlane('XY', z0 || 0).extrude(h);
}
// mesmo perfil, no plano XZ (pontos [x,z]), extrudado em +Y a partir de y0
export function extrudaPoliXZ(pts, h, y0) {
  // o plano XZ do replicad tem normal -Y; desenhar e girar e mais previsivel
  let s = extrudaPoli(pts.map(p => [p[0], p[1]]), h, 0);   // em XY, cresce em +Z
  s = s.rotate(90, [0, 0, 0], [1, 0, 0]);                   // XY->XZ: z vira -y
  return s.translate(0, (y0 || 0) + h, 0);
}

export const uniao = lista => lista.filter(Boolean).reduce((a, b) => (a ? a.fuse(b) : b), null);
export const corta = (base, lista) => lista.filter(Boolean).reduce((a, b) => a.cut(b), base);

/* furos de fixacao "para impressora": o furo impresso sai menor que o desenhado, por
   isso as folgas aqui ja vem compensadas (M3 passa em 3,4; porca M3 em 5,7 entre faces). */
export const FOLGA = {
  m3: 3.4, m3Cab: 6.0, m3CabH: 3.2, m3PorcaAF: 5.8, m3PorcaH: 2.6,
  m5: 5.4, m5Cab: 9.0, m5CabH: 5.2, m5PorcaAF: 8.2, m5PorcaH: 4.2,
  m2: 2.3, madeira: 4.0, madeiraCab: 7.6,
};

// furo passante ao longo de um eixo, centrado em p, comprimento h
export const furo = (d, h, p, eixo) => cilC(d, h, p, eixo);
// escareado de parafuso de madeira (cabeca chata 90 graus), boca na face indicada
export function escareado(p, eixo, sentido, h) {
  // cone de 90 graus: do diametro da cabeca ate o do furo
  // v aponta para FORA da peca, pela face onde a cabeca fica
  const v = DIR[(sentido < 0 ? '-' : '') + eixo];
  const r1 = FOLGA.madeiraCab / 2 + 0.2, r0 = FOLGA.madeira / 2, prof = r1 - r0;
  const furoP = R.makeCylinder(r0, h || 40, p, v.map(c => -c));
  const perfil = R.draw([0, 0.01]).lineTo([r1, 0.01]).lineTo([r0, -prof]).lineTo([0, -prof]).close();
  const cone = orientaZ(perfil.sketchOnPlane('XZ').revolve([0, 0, 1]), v).translate(...p);
  return furoP.fuse(cone);
}
// gira uma forma construida "apontando +Z" para apontar na direcao v
export function orientaZ(s, v) {
  const [x, y, z] = v;
  if (z === 1) return s;
  if (z === -1) return s.rotate(180, [0, 0, 0], [1, 0, 0]);
  if (x === 1) return s.rotate(90, [0, 0, 0], [0, 1, 0]);
  if (x === -1) return s.rotate(-90, [0, 0, 0], [0, 1, 0]);
  if (y === 1) return s.rotate(-90, [0, 0, 0], [1, 0, 0]);
  return s.rotate(90, [0, 0, 0], [1, 0, 0]);
}

/* ---------- cores e materiais (nomes usados no visualizador) ---------- */
export const COR = {
  aluminio:  { c: '#b8c0c8', m: 0.85, r: 0.35 },
  aco:       { c: '#8a939b', m: 0.9,  r: 0.3 },
  acoEsc:    { c: '#3c4248', m: 0.8,  r: 0.4 },
  zincado:   { c: '#c9cdd2', m: 0.9,  r: 0.25 },
  latao:     { c: '#c9a25a', m: 0.9,  r: 0.3 },
  preto:     { c: '#1d2023', m: 0.1,  r: 0.6 },
  borracha:  { c: '#2a2a2a', m: 0.0,  r: 0.9 },
  vermelho:  { c: '#b8322c', m: 0.1,  r: 0.5 },
  pcbAzul:   { c: '#1f4fa8', m: 0.1,  r: 0.5 },
  pcbRoxo:   { c: '#5b2a86', m: 0.1,  r: 0.5 },
  pcbVerde:  { c: '#1f6b3a', m: 0.1,  r: 0.5 },
  pcbPreto:  { c: '#202428', m: 0.1,  r: 0.5 },
  ic:        { c: '#111111', m: 0.2,  r: 0.5 },
  cobre:     { c: '#c77a3a', m: 0.9,  r: 0.35 },
  branco:    { c: '#e8e8e2', m: 0.0,  r: 0.6 },
  ledIR:     { c: '#7a8aa0', m: 0.0,  r: 0.2, o: 0.75 },
  fotoT:     { c: '#202020', m: 0.0,  r: 0.2, o: 0.9 },
  acrilico:  { c: '#cfe6ee', m: 0.0,  r: 0.05, o: 0.35 },
  impresso:  { c: '#e0892b', m: 0.0,  r: 0.65 },   // PETG laranja: tudo que e IMPRESSO
  impresso2: { c: '#2b8fe0', m: 0.0,  r: 0.65 },   // PETG azul: pecas moveis impressas
  bola:      { c: '#f4f1e8', m: 0.0,  r: 0.25 },
  mdf:       { c: '#b89466', m: 0.0,  r: 0.85 },
  ima:       { c: '#9aa0a6', m: 0.6,  r: 0.4 },
  correia:   { c: '#222222', m: 0.0,  r: 0.8 },
  mola:      { c: '#a8acb0', m: 0.9,  r: 0.3 },
  fio:       { c: '#c0392b', m: 0.0,  r: 0.6 },
};
