/* Le os parametros vivos do simulador (js/params.js, js/catalog.js) sem duplicar valor:
   a bola, o curso e a largura interna do gabinete vem de la. */
import fs from 'fs';
import vm from 'vm';
import path from 'path';
import { fileURLToPath } from 'url';

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const ctx = { window: {}, console, Math, JSON, Object, Array, Number, String, isFinite, parseFloat };
ctx.window.window = ctx.window;
vm.createContext(ctx);
['js/util.js', 'js/params.js', 'js/catalog.js'].forEach(f => {
  vm.runInContext(fs.readFileSync(path.join(raiz, f), 'utf8'), ctx, { filename: f });
});
const PB = ctx.window.PB;
export const num = k => PB.params.num(k);
export const RAIZ = raiz;
export const PROJ = {
  bolaD: num('ball.d'),
  curso: num('A.stroke'),
  interna: num('geo.inner'),
  lado: num('geo.floor'),
  abertura: num('geo.L'),
  profBoca: num('geo.depth'),
  queda: num('geo.h'),
};
