/* Correia GT2 aberta em laco entre duas polias, no plano XZ, largura em Y.
   Dentes para DENTRO (encostam na polia). Passo 2 mm, altura do dente 0,75,
   espessura total 1,38 (largura 6) / 1,52 (largura 10). A linha primitiva fica a
   0,254 mm para dentro do dorso. */
import { R, uniao, caixa } from '../lib/base.mjs';

const P = 2, HD = 0.75;
// trecho reto com dentes, comprimento L ao longo de +X a partir de x=0, dorso em z=+eDorso,
// dentes para -z. Desenhado no plano XZ e extrudado na largura (Y, de y0 a y0+larg)
function trechoReto(L, larg, eDorso, y0) {
  const pts = [[0, eDorso]];
  pts.push([L, eDorso], [L, 0]);
  const n = Math.floor(L / P);
  const sobra = (L - n * P) / 2;
  for (let i = n - 1; i >= 0; i--) {
    const x0 = sobra + i * P;                    // cada passo: dente trapezoidal de 1,1 mm
    pts.push([x0 + 1.55, 0], [x0 + 1.35, -HD], [x0 + 0.65, -HD], [x0 + 0.45, 0]);
  }
  pts.push([0, 0]);
  let pen = R.draw(pts[0]);
  for (let i = 1; i < pts.length; i++) pen = pen.lineTo(pts[i]);
  // desenha em XY (y = espessura) e gira para XZ
  let s = pen.close().sketchOnPlane('XY').extrude(larg);
  s = s.rotate(90, [0, 0, 0], [1, 0, 0]);          // (x,y,z) -> (x,-z,y): espessura vai para z
  return s.translate(0, y0 + larg, 0);
}
// arco: anel do raio rI (dentes, sem detalhe) ao raio rE (dorso), angulos em graus no plano XZ
function arco(cx, cz, rI, rE, a0, a1, larg, y0) {
  const perfil = R.draw([rI, 0]).lineTo([rE, 0]).lineTo([rE, larg]).lineTo([rI, larg]).close();
  // revolucao em torno de Y: desenhar no plano XY (x = raio, y = largura) e girar em torno de Y
  let s = perfil.sketchOnPlane('XY').revolve([0, 1, 0], { angle: a1 - a0 });
  // revolve em torno de Y parte do eixo +X e gira no sentido de +X para -Z
  s = s.rotate(-a0, [0, 0, 0], [0, 1, 0]);
  return s.translate(cx, y0, cz);
}

/* laco: polias em x1 < x2 na altura z=0, raio primitivo rp. O ramo de CIMA e cortado
   entre xa e xb (onde a garra prende as duas pontas). */
export function correiaLaco({ x1, x2, rp, larg, y0, xa, xb }) {
  const eD = larg >= 10 ? 0.77 : 0.63;           // dorso acima da raiz do dente
  const rRaiz = rp - 0.254 + 0.0;                 // raiz dos dentes (face interna lisa)
  const partes = [];
  // ramo de cima: dorso para +z. Dente para -z (para dentro).
  const zc = rRaiz;
  const cima = (a, b) => { if (b - a > 0.5) partes.push(trechoReto(b - a, larg, eD, y0).translate(a, 0, zc)); };
  cima(x1, xa); cima(xb, x2);
  // ramo de baixo: espelho (dorso para -z)
  partes.push(trechoReto(x2 - x1, larg, eD, y0).mirror('XY').translate(x1, 0, -zc));
  // abracos nas polias: meia volta cada
  partes.push(arco(x2, 0, rRaiz - HD * 0.4, rRaiz + eD, 90, 270, larg, y0));   // o revolve gira de +X para +Z
  partes.push(arco(x1, 0, rRaiz - HD * 0.4, rRaiz + eD, -90, 90, larg, y0));
  return partes;   // sem fundir: a uniao de trechos dentados custa minutos e nao muda a malha
}
