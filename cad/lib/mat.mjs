/* Transformacoes de instancia, no referencial do CAD (Z para cima).
   T().rz(90).t(10,0,0): primeiro gira, depois translada (ordem de leitura).
   paraThree() devolve a matriz 4x4 coluna-maior que o three.js le com fromArray. */
const I = () => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
// a e b em linha-maior (r*4+c); devolve a*b
function mul(a, b) {
  const o = new Array(16).fill(0);
  for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) for (let k = 0; k < 4; k++) o[r * 4 + c] += a[r * 4 + k] * b[k * 4 + c];
  return o;
}
function rot(eixo, graus) {
  const a = graus * Math.PI / 180, c = Math.cos(a), s = Math.sin(a), m = I();
  if (eixo === 'x') { m[5] = c; m[6] = -s; m[9] = s; m[10] = c; }
  if (eixo === 'y') { m[0] = c; m[2] = s; m[8] = -s; m[10] = c; }
  if (eixo === 'z') { m[0] = c; m[1] = -s; m[4] = s; m[5] = c; }
  return m;
}
export class T {
  // ops: a mesma sequencia, para reaplicar numa forma do replicad (verificacao de interferencia)
  constructor(m, ops) { this.m = m || I(); this.ops = ops || []; }
  static of() { return new T(); }
  ap(n, op) { return new T(mul(n, this.m), this.ops.concat([op])); }
  rx(g) { return this.ap(rot('x', g), ['r', 'x', g]); }
  ry(g) { return this.ap(rot('y', g), ['r', 'y', g]); }
  rz(g) { return this.ap(rot('z', g), ['r', 'z', g]); }
  t(x, y, z) { const n = I(); n[3] = x || 0; n[7] = y || 0; n[11] = z || 0; return this.ap(n, ['t', x || 0, y || 0, z || 0]); }
  esp(eixo) { const n = I(); n[{ x: 0, y: 5, z: 10 }[eixo]] = -1; return this.ap(n, ['e', eixo]); }
  // compoe: primeiro this, depois o outro (o outro e o "pai")
  em(pai) { return new T(mul(pai.m, this.m), this.ops.concat(pai.ops)); }
  get espelhado() { return this.ops.filter(o => o[0] === 'e').length % 2 === 1; }
  aplica(forma) {
    const EIXO = { x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1] };
    const PLANO = { x: 'YZ', y: 'XZ', z: 'XY' };
    return this.ops.reduce((f, o) => o[0] === 'r' ? f.rotate(o[2], [0, 0, 0], EIXO[o[1]])
      : o[0] === 't' ? f.translate(o[1], o[2], o[3]) : f.mirror(PLANO[o[1]], [0, 0, 0]), forma);
  }
  ponto(p) {
    const m = this.m;
    return [0, 1, 2].map(r => m[r * 4] * p[0] + m[r * 4 + 1] * p[1] + m[r * 4 + 2] * p[2] + m[r * 4 + 3]);
  }
  vetor(v) {
    const m = this.m;
    return [0, 1, 2].map(r => m[r * 4] * v[0] + m[r * 4 + 1] * v[1] + m[r * 4 + 2] * v[2]);
  }
  paraThree() {
    // C: (x,y,z)cad -> (x,z,-y)three. M3 = C * M * C^-1
    const C = [1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1];
    const Ci = [1, 0, 0, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 1];
    const m = mul(mul(C, this.m), Ci);
    const col = [];
    for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) col.push(+m[r * 4 + c].toFixed(5));
    return col;
  }
}
export const vParaThree = v => [v[0], v[2], -v[1]];
