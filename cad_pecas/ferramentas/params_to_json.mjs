/* js/params.js (+ util.js, catalog.js) -> cad_pecas/maquina_a/params.json
   Executa o registro de parametros do simulador num contexto isolado e grava
   valor, unidade, procedencia (est/med/def) e rotulo de cada chave. Nunca editar o JSON a mao.
   Uso: node cad_pecas/ferramentas/params_to_json.mjs */
import fs from 'fs';
import vm from 'vm';
import path from 'path';
import { fileURLToPath } from 'url';

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const ctx = { window: {}, console, Math, JSON, Object, Array, Number, String, isFinite, parseFloat, Date };
ctx.window.window = ctx.window;
vm.createContext(ctx);
for (const f of ['js/util.js', 'js/params.js', 'js/catalog.js']) {
  vm.runInContext(fs.readFileSync(path.join(raiz, f), 'utf8'), ctx, { filename: f });
}
const P = ctx.window.PB.params;
const out = { _fonte: 'js/params.js', _hash: P.hash(), valores: {} };
for (const d of P.schema()) {
  out.valores[d.k] = { v: P.get(d.k), u: d.u, s: P.stat(d.k), g: d.g, l: d.l };
}
const dest = path.join(raiz, 'cad_pecas', 'maquina_a', 'params.json');
fs.mkdirSync(path.dirname(dest), { recursive: true });
fs.writeFileSync(dest, JSON.stringify(out, null, 2));
console.log('params.json:', Object.keys(out.valores).length, 'chaves, hash', out._hash);
