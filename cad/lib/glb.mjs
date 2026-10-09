/* Escritor minimo de glTF binario (.glb).
   Uma peca = varios corpos (cada um com sua cor) + as arestas vivas como LINES.
   Converte do referencial do CAD (Z para cima, Y para o fundo) para o do three.js
   (Y para cima, +Z para o jogador): (x, y, z) -> (x, z, -y). */
import { COR } from './base.mjs';

export const cadParaThree = (x, y, z) => [x, z, -y];

function hexRGB(h) {
  const n = parseInt(h.slice(1), 16);
  // glTF quer cor linear; o three converte de volta para sRGB na saida
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map(c => Math.pow(c / 255, 2.2));
}

export function malhaDeForma(forma, tol) {
  const m = forma.mesh({ tolerance: tol || 0.04, angularTolerance: 0.25 });
  const a = forma.meshEdges({ tolerance: (tol || 0.04) * 2, angularTolerance: 0.35 });
  return { v: m.vertices, n: m.normals, t: m.triangles, e: a.lines };
}

// corpos: [{ malha:{v,n,t,e}, cor:'aluminio' }]
export function escreveGLB(corpos, nome) {
  const bufs = [], views = [], acc = [], prims = [], mats = [];
  let off = 0;
  const addBuf = (typed, target) => {
    const b = Buffer.from(typed.buffer, typed.byteOffset, typed.byteLength);
    const pad = (4 - (b.byteLength % 4)) % 4;
    bufs.push(b); if (pad) bufs.push(Buffer.alloc(pad));
    views.push({ buffer: 0, byteOffset: off, byteLength: b.byteLength, target });
    off += b.byteLength + pad;
    return views.length - 1;
  };
  const posAcc = v => {
    const f = new Float32Array(v.length);
    const mn = [Infinity, Infinity, Infinity], mx = [-Infinity, -Infinity, -Infinity];
    for (let i = 0; i < v.length; i += 3) {
      const p = cadParaThree(v[i], v[i + 1], v[i + 2]);
      for (let k = 0; k < 3; k++) { f[i + k] = p[k]; mn[k] = Math.min(mn[k], p[k]); mx[k] = Math.max(mx[k], p[k]); }
    }
    acc.push({ bufferView: addBuf(f, 34962), componentType: 5126, count: v.length / 3, type: 'VEC3', min: mn, max: mx });
    return acc.length - 1;
  };
  const nrmAcc = n => {
    const f = new Float32Array(n.length);
    for (let i = 0; i < n.length; i += 3) {
      const p = cadParaThree(n[i], n[i + 1], n[i + 2]);
      f[i] = p[0]; f[i + 1] = p[1]; f[i + 2] = p[2];
    }
    acc.push({ bufferView: addBuf(f, 34962), componentType: 5126, count: n.length / 3, type: 'VEC3' });
    return acc.length - 1;
  };
  const idxAcc = t => {
    const u = new Uint32Array(t);
    acc.push({ bufferView: addBuf(u, 34963), componentType: 5125, count: t.length, type: 'SCALAR' });
    return acc.length - 1;
  };
  const matIdx = {};
  const material = cor => {
    if (matIdx[cor] !== undefined) return matIdx[cor];
    const k = COR[cor] || COR.impresso;
    const base = hexRGB(k.c).concat([k.o || 1]);
    const m = { name: cor, pbrMetallicRoughness: { baseColorFactor: base, metallicFactor: k.m, roughnessFactor: k.r }, doubleSided: false };
    if (k.o && k.o < 1) m.alphaMode = 'BLEND';
    mats.push(m); matIdx[cor] = mats.length - 1; return matIdx[cor];
  };

  const linhas = [];
  corpos.forEach(c => {
    const g = c.malha;
    if (!g.t.length) return;
    prims.push({ attributes: { POSITION: posAcc(g.v), NORMAL: nrmAcc(g.n) }, indices: idxAcc(g.t), material: material(c.cor), mode: 4 });
    if (g.e && g.e.length) linhas.push(g.e);
  });
  if (linhas.length) {
    const tudo = [].concat(...linhas.map(l => Array.from(l)));
    mats.push({ name: '__aresta', pbrMetallicRoughness: { baseColorFactor: [0.02, 0.02, 0.02, 1], metallicFactor: 0, roughnessFactor: 1 } });
    prims.push({ attributes: { POSITION: posAcc(tudo) }, material: mats.length - 1, mode: 1 });
  }

  const gltf = {
    asset: { version: '2.0', generator: 'picbox cad/build.mjs' },
    scene: 0, scenes: [{ nodes: [0] }],
    nodes: [{ mesh: 0, name: nome }],
    meshes: [{ name: nome, primitives: prims }],
    materials: mats, accessors: acc, bufferViews: views,
    buffers: [{ byteLength: off }],
  };
  let json = Buffer.from(JSON.stringify(gltf));
  const jp = (4 - (json.length % 4)) % 4;
  json = Buffer.concat([json, Buffer.alloc(jp, 0x20)]);
  const bin = Buffer.concat(bufs);
  const head = Buffer.alloc(12), jh = Buffer.alloc(8), bh = Buffer.alloc(8);
  const total = 12 + 8 + json.length + 8 + bin.length;
  head.writeUInt32LE(0x46546c67, 0); head.writeUInt32LE(2, 4); head.writeUInt32LE(total, 8);
  jh.writeUInt32LE(json.length, 0); jh.writeUInt32LE(0x4e4f534a, 4);
  bh.writeUInt32LE(bin.length, 0); bh.writeUInt32LE(0x004e4942, 4);
  return Buffer.concat([head, jh, json, bh, bin]);
}

// STL binario de um conjunto de malhas (para impressao: referencial do CAD, Z para cima)
export function escreveSTL(malhas) {
  let n = 0; malhas.forEach(m => { n += m.t.length / 3; });
  const b = Buffer.alloc(84 + n * 50);
  b.write('picbox', 0);
  b.writeUInt32LE(n, 80);
  let o = 84;
  malhas.forEach(m => {
    const v = m.v, t = m.t;
    for (let i = 0; i < t.length; i += 3) {
      const a = t[i] * 3, c = t[i + 1] * 3, d = t[i + 2] * 3;
      const ux = v[c] - v[a], uy = v[c + 1] - v[a + 1], uz = v[c + 2] - v[a + 2];
      const wx = v[d] - v[a], wy = v[d + 1] - v[a + 1], wz = v[d + 2] - v[a + 2];
      let nx = uy * wz - uz * wy, ny = uz * wx - ux * wz, nz = ux * wy - uy * wx;
      const l = Math.hypot(nx, ny, nz) || 1; nx /= l; ny /= l; nz /= l;
      b.writeFloatLE(nx, o); b.writeFloatLE(ny, o + 4); b.writeFloatLE(nz, o + 8); o += 12;
      [a, c, d].forEach(k => { b.writeFloatLE(v[k], o); b.writeFloatLE(v[k + 1], o + 4); b.writeFloatLE(v[k + 2], o + 8); o += 12; });
      o += 2;
    }
  });
  return b;
}
