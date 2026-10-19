/* Gera tudo o que a pagina /montagem usa:
     montagem/modelos/<peca>.glb      malha de cada peca (referencial do three.js)
     montagem/fabricar/<peca>.stl     pecas impressas, ja deitadas na posicao de imprimir
     montagem/fabricar/<peca>.step    o mesmo, em solido (para editar em qualquer CAD)
     montagem/guia.json               pecas, modulos, instancias e passos
   Uso: node build.mjs            (tudo)
        node build.mjs eixo       (so os modulos citados; o guia.json e sempre completo)
        node build.mjs --sem-colisao */
import fs from 'fs';
import path from 'path';
import { iniciaOC, R } from './lib/base.mjs';
import { PECAS } from './lib/registro.mjs';
import { malhaDeForma, escreveGLB, escreveSTL } from './lib/glb.mjs';
import { T } from './lib/mat.mjs';
import { RAIZ, PROJ } from './lib/projeto.mjs';
import { CONTEUDO } from './conteudo.mjs';
import { EXPLICA } from './explicacoes.mjs';

await iniciaOC();
await import('./pecas/fixadores.mjs');
await import('./pecas/comprados.mjs');
await import('./pecas/eletronicos.mjs');
const MODULOS = [];
for (const m of ['maquina', 'funcionamento', 'fimdecurso', 'gabinete', 'eixo', 'soltura', 'boca', 'bandeja', 'magazine', 'elevador', 'eletronica']) {
  const mod = await import('./montagens/' + m + '.mjs');
  Object.values(mod).filter(v => typeof v === 'function' && v.name.startsWith('modulo')).forEach(fn => MODULOS.push(fn()));
}

// ordem das abas: primeiro o que explica, depois a montagem na ordem em que se monta
const ORDEM = ['maquina', 'func_carga', 'func_elevador', 'func_fc', 'ligacoes', 'alt_pistao', 'gabinete', 'eletronica', 'eixo', 'boca', 'bandeja',
  'elevador', 'soltura', 'magazine'];
MODULOS.sort((a, b) => (ORDEM.indexOf(a.id) + 1 || 99) - (ORDEM.indexOf(b.id) + 1 || 99));
const args = process.argv.slice(2);
const so = args.filter(a => !a.startsWith('--'));
const semColisao = args.includes('--sem-colisao');
const MESA = [260, 260, 300];
const OUT = path.join(RAIZ, 'montagem');
const DIR_M = path.join(OUT, 'modelos'), DIR_F = path.join(OUT, 'fabricar');
[OUT, DIR_M, DIR_F].forEach(d => fs.mkdirSync(d, { recursive: true }));

const usadas = new Set();
MODULOS.forEach(m => m.instancias.forEach(i => usadas.add(i.peca)));
const alvo = so.length ? new Set(MODULOS.filter(m => so.includes(m.id)).flatMap(m => m.instancias.map(i => i.peca))) : usadas;

const cacheForma = {};
function formas(id) {
  if (!cacheForma[id]) cacheForma[id] = PECAS[id].gera();
  return cacheForma[id];
}
const t0 = Date.now();
let nGlb = 0, nStl = 0;
for (const id of usadas) {
  if (!alvo.has(id) && fs.existsSync(path.join(DIR_M, id + '.glb'))) continue;
  const corpos = formas(id).map(c => ({ malha: malhaDeForma(c.forma), cor: c.cor }));
  fs.writeFileSync(path.join(DIR_M, id + '.glb'), escreveGLB(corpos, id));
  nGlb++;
  const p = PECAS[id];
  if (p.tipo === 'impresso') {
    // STL/STEP na posicao de imprimir: gira, depois apoia na mesa (z minimo = 0) e centra
    const variantes = [['', false]];
    if (MODULOS.some(m => m.espelhoA && m.instancias.some(i => i.peca === id))) variantes.push(['_A', true]);
    for (const [suf, esp] of variantes) {
      let f = formas(id).map(c => c.forma.clone()).reduce((a, b) => a.fuse(b));
      if (esp) f = f.mirror('XY', [0, 0, 0]);
      ((p.imprimir && p.imprimir.rot) || []).forEach(([e, g]) => {
        f = f.rotate(g, [0, 0, 0], { x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1] }[e]);
      });
      const b = f.boundingBox.bounds;
      f = f.translate(-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]);
      const m = f.mesh({ tolerance: 0.01, angularTolerance: 0.1 });
      fs.writeFileSync(path.join(DIR_F, id + suf + '.stl'), escreveSTL([{ v: m.vertices, t: m.triangles }]));
      const step = Buffer.from(await f.blobSTEP().arrayBuffer());
      fs.writeFileSync(path.join(DIR_F, id + suf + '.step'), step);
      const bb = f.boundingBox.bounds;
      p.tamanhoMesa = [0, 1, 2].map(k => +(bb[1][k] - bb[0][k]).toFixed(1));
      // impressora do projeto: Creality, mesa 260 x 260, altura 300
      const t = p.tamanhoMesa, cabe = t[0] <= MESA[0] && t[1] <= MESA[1] && t[2] <= MESA[2];
      if (!cabe) { p.naoCabe = true; console.log('   NAO CABE NA MESA:', id + suf, t.join(' x ')); }
      nStl++;
    }
  }
}
console.log(`malhas: ${nGlb} glb, ${nStl} stl/step em ${((Date.now() - t0) / 1000).toFixed(1)} s`);

/* ---------- verificacao de interferencia ----------
   Entre pecas que NAO sao fixadores: volume em comum > 5 mm3 e erro (abaixo disso e lasca de
   tesselacao na quina de furo inclinado). Parafuso entrando em
   furo-guia ou rosca e de proposito, por isso fixador fica fora. */
const colisoes = {};
if (!semColisao) {
  for (const m of MODULOS) {
    if (so.length && !so.includes(m.id)) continue;
    if (m.didatico) continue;                 // animacao: pecas sobrepostas de proposito (posicoes iniciais)
    const t1 = Date.now();
    const lista = m.instancias.filter(i => PECAS[i.peca].tipo !== 'fixador' && !i.semColisao)
      .map(i => {
        const f = formas(i.peca).map(c => c.forma.clone()).reduce((a, b) => a.fuse(b));
        const s = i.T.aplica(f);
        return { i, s, b: s.boundingBox.bounds };
      });
    const achados = [];
    for (let a = 0; a < lista.length; a++) for (let b = a + 1; b < lista.length; b++) {
      const A = lista[a].b, B = lista[b].b;
      if ([0, 1, 2].some(k => A[1][k] < B[0][k] - 0.01 || B[1][k] < A[0][k] - 0.01)) continue;
      let v = 0;
      try {
        const x = lista[a].s.clone().intersect(lista[b].s.clone());
        v = x ? Math.abs(R.measureVolume(x)) : 0;
      } catch (e) { v = -1; }
      if (v > 5 || v < 0) achados.push({ a: lista[a].i.id, b: lista[b].i.id, mm3: +v.toFixed(1) });
    }
    // varredura: o conjunto movel deslocado ate cada extremo do curso, contra o que e fixo
    (m.varredura || []).forEach(v => {
      const moveis = lista.filter(o => v.ids.includes(o.i.id)), fixos = lista.filter(o => !v.ids.includes(o.i.id) && !(v.ignora || []).includes(o.i.id));
      v.desloc.forEach(d => moveis.forEach(mv => {
        const s = mv.s.clone().translate(...d), b = s.boundingBox.bounds;
        fixos.forEach(fx => {
          const B = fx.b;
          if ([0, 1, 2].some(k => b[1][k] < B[0][k] - 0.01 || B[1][k] < b[0][k] - 0.01)) return;
          let vol = 0;
          try { const x = s.clone().intersect(fx.s.clone()); vol = x ? Math.abs(R.measureVolume(x)) : 0; } catch (e) { vol = -1; }
          if (vol > 5 || vol < 0) achados.push({ a: mv.i.id + ' @x' + (d[0] >= 0 ? '+' : '') + d[0], b: fx.i.id, mm3: +vol.toFixed(1) });
        });
      }));
    });
    // trajetoria: uma peca levada por uma sequencia de posicoes (ex.: cacamba dando a volta no elevador)
    (m.trajetoria || []).forEach(tr => {
      const base = formas(tr.peca).map(c => c.forma.clone()).reduce((x, y) => x.fuse(y));
      const contra = lista.filter(o => tr.contra.includes(o.i.id));
      tr.Ts.forEach((t, n) => {
        const sh = t.aplica(base.clone()), b = sh.boundingBox.bounds;
        contra.forEach(fx => {
          const B = fx.b;
          if ([0, 1, 2].some(q => b[1][q] < B[0][q] - 0.01 || B[1][q] < b[0][q] - 0.01)) return;
          let vol = 0;
          try { const x = sh.clone().intersect(fx.s.clone()); vol = x ? Math.abs(R.measureVolume(x)) : 0; } catch (e) { vol = -1; }
          if (vol > 5 || vol < 0) achados.push({ a: tr.peca + ' @' + (tr.rotulos ? tr.rotulos[n] : n), b: fx.i.id, mm3: +vol.toFixed(1) });
        });
      });
    });
    colisoes[m.id] = achados;
    console.log(`colisao ${m.id}: ${lista.length} pecas, ${achados.length} interferencias (${((Date.now() - t1) / 1000).toFixed(1)} s)`);
    achados.forEach(c => console.log('   ', c.a, '×', c.b, c.mm3 < 0 ? 'ERRO NO CALCULO' : c.mm3 + ' mm³'));
  }
}

/* ---------- guia.json ---------- */
const pecasJson = {};
for (const id of usadas) {
  const p = PECAS[id];
  const o = {};
  for (const k of Object.keys(p)) if (!['gera', 'ref', 'imprimir', 'id'].includes(k)) o[k] = p[k];
  if (EXPLICA[id]) o.explica = EXPLICA[id];
  o.glb = 'modelos/' + id + '.glb';
  if (p.tipo === 'impresso') {
    o.stl = 'fabricar/' + id + '.stl'; o.step = 'fabricar/' + id + '.step';
    if (fs.existsSync(path.join(DIR_F, id + '_A.stl'))) o.stlA = 'fabricar/' + id + '_A.stl';
  }
  pecasJson[id] = o;
}
const guia = {
  gerado: new Date().toISOString(),
  projeto: Object.assign({ mesa: MESA }, PROJ),
  conteudo: CONTEUDO,
  pecas: pecasJson,
  modulos: MODULOS.map(m => Object.assign({}, m, {
    instancias: m.instancias.map(i => ({ id: i.id, peca: i.peca, m: i.T.paraThree(), esp: i.T.espelhado || undefined, oculta: i.oculta || undefined })),
    // animacoes: as chaves vem como T (referencial do CAD) e saem como matriz do three
    passos: m.passos.map(q => q.anim ? Object.assign({}, q, { anim: Object.assign({}, q.anim, {
      trilhas: q.anim.trilhas.map(tr => ({ id: tr.id, k: tr.k.map(([t, T]) => [+t.toFixed(3), T.paraThree()]) })) }) }) : q),
    varredura: undefined, trajetoria: undefined,
    colisoes: colisoes[m.id],
  })),
};
const anterior = fs.existsSync(path.join(OUT, 'guia.json')) ? JSON.parse(fs.readFileSync(path.join(OUT, 'guia.json'), 'utf8')) : null;
if (anterior && so.length) {
  // build parcial: mantem as colisoes ja calculadas dos outros modulos
  guia.modulos.forEach(m => { if (!so.includes(m.id)) { const a = anterior.modulos.find(x => x.id === m.id); if (a) m.colisoes = a.colisoes; } });
}
fs.writeFileSync(path.join(OUT, 'guia.json'), JSON.stringify(guia));
console.log('guia.json:', Object.keys(pecasJson).length, 'pecas,', MODULOS.length, 'modulos');
