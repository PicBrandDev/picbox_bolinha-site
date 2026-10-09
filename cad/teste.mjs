// gera cada peca registrada isoladamente e reporta erro / triangulos / tempo
import { iniciaOC } from './lib/base.mjs';
import { PECAS } from './lib/registro.mjs';
import { malhaDeForma } from './lib/glb.mjs';
await iniciaOC();
const mods = process.argv.slice(2);
for (const m of (mods.length ? mods : ['fixadores'])) await import('./pecas/' + m + '.mjs');
let erros = 0;
for (const id of Object.keys(PECAS)) {
  const t = Date.now();
  try {
    const corpos = PECAS[id].gera();
    let tri = 0;
    corpos.forEach(c => { tri += malhaDeForma(c.forma).t.length / 3; });
    console.log(id.padEnd(28), String(tri).padStart(7), 'tri', String(Date.now() - t).padStart(6), 'ms');
  } catch (e) { erros++; console.log(id.padEnd(28), 'ERRO', e.message || e); }
}
console.log('erros:', erros);
