/* MODULO 4 — MAGAZINE: fila de bolas em 3 passes de tubo acrilico, escapement (SG90),
   comporta (JF-0530B) e a calha de carga que leva a bola ate o berco do eixo A.

   Referencial: o do eixo A instalado (trilho A centrado em z = 0, frente = -Y).
   O magazine fica ATRAS do eixo A: eixo dos tubos em y = 65. O limite de tras e o
   painel de MDF (y = 104); o da frente, a placa do bloco tensor do eixo A (y = 40,5).

   Alturas: inclinacao de 4 graus [H]. A 6 graus (modelo antigo) os passes reais de
   ~200 mm sobem tanto que o topo do elevador passaria do teto do gabinete. 4 graus ainda
   escoa com a resistencia de rolagem do modelo (tan 4 = 0,070 > 0,06) — valide na bancada
   com uma bola rolando no tubo inclinado antes de cortar o painel.

   Sequencia da bola: P1 (topo, entra pela direita) -> curva U esquerda -> P2 -> curva U
   direita -> P3 -> saida (escapement) -> curva -> travessia para a frente, por baixo do
   bloco tensor do eixo A -> comporta -> curva -> trilhos de carga dentro do berco. */
import { R, caixa, caixaC, cil, cilC, tubo, uniao, sextavado, FOLGA, extrudaPoli } from '../lib/base.mjs';
import { peca, inst } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';
import { PROJ } from '../lib/projeto.mjs';
import { TUBO, SG90, SOL } from '../pecas/comprados.mjs';
import { EX } from './eixo.mjs';
import { SO } from './soltura.mjs';

const RB = PROJ.bolaD / 2;
const th = 4 * Math.PI / 180, k = Math.tan(th);
const DCAN = 36.4;                         // canal das curvas: um pouco maior que o tubo (36)
const PAR = 3;                             // parede impressa
// canal aberto: parede 2,5. O raio da curva tem que passar da meia-largura externa (21,3) e a travessia
// tem que caber entre a parede do gabinete (-207) e o berco na carga (-161): por isso 21,6 e canto em -163
export const MG = { y: 65, xE: -110, xR: 40, xL: -162, xIn: 60, xCanto: -163, rCurva: 21.6, yPainel: 104 };
MG.xCruz = MG.xCanto - MG.rCurva;
const PARU = 2.5;
// comprimento do caminho dentro da saida+carga (reta, curva, travessia, curva, trilhos)
const LSAI = (MG.xE - MG.xCanto) + Math.PI * MG.rCurva / 2 + ((MG.y - MG.rCurva) - (SO.yb + MG.rCurva)) + Math.PI * MG.rCurva / 2 + 24;
MG.zE = SO.zb + LSAI * k;                                    // centro da bola na boca da saida
MG.zP3 = x => MG.zE + (x - MG.xE) * k;                       // P3 sobe para a direita
MG.zR = MG.zP3(MG.xR) + 21;                                  // centro da curva U direita
MG.zP2 = x => MG.zR + 21 + (MG.xR - x) * k;                  // P2 sobe para a esquerda
MG.zL = MG.zP2(MG.xL) + 21;
MG.zP1 = x => MG.zL + 21 + (x - MG.xL) * k;                  // P1 sobe para a direita
const IMP = { tipo: 'impresso', src: 'est', material: 'PETG' };

/* ---------------------------------------------------------------- curvas U */
// bloco com meia-toroide (R 21) + dois encaixes de tubo; partido em y = 65 para imprimir
function curvaU(xc, zc, lado, zBaixo, zCima, incl) {
  // lado: +1 = curva para +X (direita), -1 = para -X. incl[0|1]: inclinacao dos tubos de baixo/cima,
  // em graus, positiva = o tubo SOBE no sentido +X
  const L = 15, re = DCAN / 2 + PAR;
  const x0 = xc - lado * L, x1 = xc + lado * (21 + re);
  let b = caixa(Math.min(x0, x1), MG.y - re - 1, zBaixo - re - 1, Math.max(x0, x1), MG.y + re + 1, zCima + re + 1);
  b = b.fillet(4, e => e.inDirection('Y'));
  // canal: meia-toroide no plano XZ
  const tor = R.drawCircle(DCAN / 2).translate(21, 0).sketchOnPlane('XY').revolve([0, 1, 0], { angle: 180 });
  // revolve em torno de Y parte de +X e gira para -Z; o semicirculo fica do lado escolhido
  let canal = tor.rotate(lado > 0 ? -90 : 90, [0, 0, 0], [0, 1, 0]).translate(xc, MG.y, zc);
  // encaixes: furo do tubo (40,4) com o eixo inclinado, saindo da curva para dentro do passe
  [[zBaixo, incl[0]], [zCima, incl[1]]].forEach(([z, a]) => {
    // o encaixe sai da curva para o lado do passe (-X na curva direita, +X na esquerda)
    let enc = lado > 0 ? cil(TUBO.de + 1.6, L + 1, [-(L + 1), 0, 0], 'x') : cil(TUBO.de + 1.6, L + 1, [0, 0, 0], 'x');
    enc = enc.rotate(-a, [0, 0, 0], [0, 1, 0]);
    canal = canal.fuse(enc.translate(xc, MG.y, z));
  });
  b = b.cut(canal);
  // 4 parafusos M3x40 atravessando as duas metades
  const xs = [Math.min(x0, x1) + 6, Math.max(x0, x1) - 6], zs = [zBaixo - re + 3, zCima + re - 3];
  xs.forEach(x => zs.forEach(z => {
    b = b.cut(cilC(FOLGA.m3, 60, [x, MG.y, z], 'y'));
    b = b.cut(sextavado(FOLGA.m3PorcaAF, 3, [x, MG.y + re + 1 - 1.4, z], 'y'));
  }));
  return b;
}
function metade(forma, tras) {
  const corte = tras ? caixa(-500, MG.y, -500, 500, 500, 500) : caixa(-500, -500, -500, 500, MG.y, 500);
  return forma.intersect(corte);
}
const curvaDir = () => curvaU(MG.xR, MG.zR, 1, MG.zP3(MG.xR), MG.zP2(MG.xR), [4, -4]);
const curvaEsq = () => curvaU(MG.xL, MG.zL, -1, MG.zP2(MG.xL), MG.zP1(MG.xL), [-4, 4]);
[['mag_u_dir', curvaDir, 'direita'], ['mag_u_esq', curvaEsq, 'esquerda']].forEach(([id, fn, nome]) => {
  [['_f', false, 'frente'], ['_t', true, 'trás']].forEach(([suf, tras, n2]) => {
    const ref = [id === 'mag_u_dir' ? MG.xR : MG.xL, MG.y, id === 'mag_u_dir' ? MG.zR : MG.zL];
    peca(id + suf, Object.assign({}, IMP, { nome: `Curva U ${nome} — metade de ${n2}`, dims: '≈ 57 × 22 × 128 mm',
      imprimir: { rot: [['x', tras ? 90 : -90]] },
      impressao: { preenchimento: '30 %', paredes: 4, suportes: 'não (face do corte na mesa)', tempo: '≈ 2 h' },
      notas: ['As duas metades fecham o canal da curva. 4 parafusos M3×40 com porca atravessam as duas.',
        'Canal de 36,4 mm: a bola de 35 passa folgada e não engancha na entrada do tubo (36).'] }),
    () => [{ forma: metade(fn(), tras).translate(-ref[0], -ref[1], -ref[2]), cor: 'impresso' }]);
  });
});

/* ---------------------------------------------------------------- canal aberto (U) */
// trecho reto: centro da bola de a ate b (pontos 3D). Parede 3, piso 3, abas ate 8,5 acima do centro.
export function retaU(a, b, interno) {
  const dx = b[0] - a[0], dy = b[1] - a[1], dz = b[2] - a[2];
  const L = Math.hypot(dx, dy), ang = Math.atan2(dy, dx) * 180 / Math.PI, inc = Math.atan2(dz, L) * 180 / Math.PI;
  const w = DCAN / 2 + 0.3;
  const s = interno ? caixa(-1, -w, -RB, L + 1, w, 30) : caixa(0, -w - PARU, -RB - PARU, L, w + PARU, 8.5);
  return s.rotate(-inc, [0, 0, 0], [0, 1, 0]).rotate(ang, [0, 0, 0], [0, 0, 1]).translate(...a);
}
// curva no plano: centro (cx,cy), raio r, de a0 a a1 graus, na altura z (centro da bola)
export function arcoU(cx, cy, r, a0, a1, z, interno) {
  const w = DCAN / 2 + 0.3;
  const perfil = interno ? R.drawRectangle(2 * w, RB + 30).translate(r, (30 - RB) / 2)
    : R.drawRectangle(2 * (w + PARU), RB + PARU + 8.5).translate(r, (8.5 - RB - PARU) / 2);
  let s = perfil.sketchOnPlane('XZ').revolve([0, 0, 1], { angle: a1 - a0 });
  return s.rotate(a0, [0, 0, 0], [0, 0, 1]).translate(cx, cy, z);
}

/* ---------------------------------------------------------------- saida + escapement */
const zEsc = x => MG.zP3(x);                              // a reta da saida continua o P3
const P_ESC = [MG.xCanto, MG.y, zEsc(MG.xCanto)];
const F1x = -158, F2x = -121.5, XPIV = (F1x + F2x) / 2;   // dedos do escapement e o pivo (eixo do servo)
const zPiso = x => zEsc(x) - RB - PARU;
function saida() {
  const a = [MG.xE, MG.y, MG.zE];
  const zc1 = zEsc(MG.xCanto), zc2 = zc1 - Math.PI * MG.rCurva / 2 * k;
  let s = uniao([retaU(a, P_ESC), arcoU(MG.xCanto, MG.y - MG.rCurva, MG.rCurva, 90, 180, (zc1 + zc2) / 2)]);
  // berco do tubo P3 (meia-cana) com 2 rasgos de abracadeira
  s = s.fuse(caixa(MG.xE, MG.y - 23, MG.zE - 23, MG.xE + 18, MG.y + 23, MG.zE));
  s = s.cut(cil(TUBO.de + 0.4, 20, [MG.xE - 1, MG.y, MG.zE], 'x'));
  s = s.cut(uniao([retaU(a, P_ESC, true), arcoU(MG.xCanto, MG.y - MG.rCurva, MG.rCurva, 90, 180, (zc1 + zc2) / 2, true)]));
  [MG.xE + 5, MG.xE + 13].forEach(x => { s = s.cut(caixa(x - 2, MG.y - 25, MG.zE - 26, x + 2, MG.y + 25, MG.zE - 20)); });
  // rasgos dos dedos no piso
  [F1x, F2x].forEach(x => { s = s.cut(caixa(x - 6, MG.y - 3, zPiso(x) - 5, x + 6, MG.y + 3, zPiso(x) + 4)); });
  // suporte do servo: chapa vertical atras do canal, com o rasgo do corpo e os 2 furos M2
  // a aba do servo apoia por tras desta chapa (aba a 16 mm da base, servo deitado com o eixo para -Y)
  const zs = zPiso(XPIV) - 10, ys = MG.y + 2.5 + SG90.topo - SG90.zAba;
  let sup = caixa(XPIV - 24, ys, zs - 14, XPIV + 24, ys + 3, zPiso(XPIV) + 3);
  sup = sup.cut(caixaC(XPIV - SG90.xEixo, ys + 1.5, zs, SG90.C + 0.6, 6, SG90.L + 0.6));
  [-1, 1].forEach(sx => { sup = sup.cut(cilC(1.8, 8, [XPIV - SG90.xEixo + sx * SG90.furos / 2, ys + 1.5, zs], 'y')); });
  s = s.fuse(sup);
  // pe de apoio no painel de MDF (2 parafusos de madeira)
  s = s.fuse(caixa(MG.xE + 2, MG.y + 20, MG.zE - 23, MG.xE + 16, MG.yPainel, MG.zE - 8));
  // aba de juncao com a calha de carga (2 x M3)
  const zf = zCruz(MG.y - MG.rCurva) - RB - PARU;
  let aba = caixa(MG.xCruz - 12, MG.y - MG.rCurva, zf - 10, MG.xCruz + 12, MG.y - MG.rCurva + 4, zf);
  [-7, 7].forEach(dx => { aba = aba.cut(cilC(FOLGA.m3, 10, [MG.xCruz + dx, MG.y - MG.rCurva + 2, zf - 5], 'y')); });
  s = s.fuse(aba);
  return s;
}
// balancim do escapement: preso no horn do SG90, dois dedos que sobem pelo piso alternadamente
function balancim() {
  const zs = zPiso(XPIV) - 10;
  const braco = caixa(F1x - 3, MG.y - 2.5, zs - 3, F2x + 3, MG.y + 2.5, zs + 3);
  const d1 = caixa(F1x - 1.5, MG.y - 2.5, zs, F1x + 1.5, MG.y + 2.5, zPiso(F1x) + 12);
  const d2 = caixa(F2x - 1.5, MG.y - 2.5, zs, F2x + 1.5, MG.y + 2.5, zPiso(F2x) + 4);
  let b = uniao([braco, d1, d2]).cut(cilC(4.9, 10, [XPIV, MG.y, zs], 'y'));
  return b.rotate(-12, [XPIV, MG.y, zs], [0, 1, 0]);        // posicao "segura a 1a bola"
}

/* ---------------------------------------------------------------- carga + comporta */
const yComp = -25;
const zCruz = y => { const zc1 = zEsc(MG.xCanto) - Math.PI * MG.rCurva / 2 * k; return zc1 - ((MG.y - MG.rCurva) - y) * k; };
function carga() {
  const y0 = MG.y - MG.rCurva, y1 = SO.yb + MG.rCurva;
  const zc = zCruz(y1), zc2 = zc - Math.PI * MG.rCurva / 2 * k;
  const ext = uniao([retaU([MG.xCruz, y0 - 0.5, zCruz(y0)], [MG.xCruz, y1, zc]), arcoU(MG.xCanto, y1, MG.rCurva, 180, 270, (zc + zc2) / 2)]);
  const int = uniao([retaU([MG.xCruz, y0, zCruz(y0)], [MG.xCruz, y1, zc], true), arcoU(MG.xCanto, y1, MG.rCurva, 180, 270, (zc + zc2) / 2, true)]);
  let c = ext.cut(int);
  // aba de juncao (encosta na aba da saida) e orelha presa na parede esquerda do gabinete
  const zf = zCruz(y0) - RB - PARU;
  let aba = caixa(MG.xCruz - 12, y0 - 4.5, zf - 10, MG.xCruz + 12, y0 - 0.5, zf);
  [-7, 7].forEach(dx => { aba = aba.cut(cilC(FOLGA.m3, 10, [MG.xCruz + dx, y0 - 2.5, zf - 5], 'y')); });
  c = c.fuse(aba);
  const zo = zCruz(0) - RB - PARU;
  let orelha = caixa(-EX.parede, -20, zo - 22, MG.xCruz - DCAN / 2 - PARU + 0.3, 20, zo + 2);
  [-12, 12].forEach(dy => { orelha = orelha.cut(cilC(FOLGA.madeira, 20, [-EX.parede, dy, zo - 11], 'x')); });
  c = c.fuse(orelha);
  // trilhos de carga: entram no berco ate x = -128, com o topo onde a bola fica a -60
  const zt = SO.zb - Math.sqrt(RB * RB - 100);
  [SO.yb - 10, SO.yb + 10].forEach(y => {
    c = c.fuse(caixa(-170, y - 2, zt - 6, -128, y + 2, zt).fuse(caixa(-170, y - 2, zt - 14, -150, y + 2, zt - 6)));
  });
  // comporta: rasgo no piso e suporte do JF-0530B embaixo
  const zp = zCruz(yComp) - RB - PARU;
  c = c.cut(caixa(MG.xCruz - 20, yComp - 1.5, zp - 2, MG.xCruz + 20, yComp + 1.5, zp + PAR + 1));
  const s5 = SOL.jf0530, zSol = zp - 4 - 10 - s5.C;
  const yS = yComp + 2.4 + s5.A / 2;                          // face da carcaca com os furos
  let sup = caixa(MG.xCruz - 12, yS, zSol - 3, MG.xCruz + 12, yS + 3, zp);
  s5.furos.forEach(zl => { sup = sup.cut(cilC(FOLGA.m3, 8, [MG.xCruz, yS + 1.5, zSol + zl], 'y')); });
  // a reta inclinada passa um pouco do plano de juncao nas quinas: apara rente
  return c.fuse(sup).intersect(caixa(-300, -300, -300, 300, y0 - 0.4, 300));
}
function comporta() {
  const zp = zCruz(yComp) - RB - PARU;
  // lamina: fechada, sobe 9,5 mm acima do piso (a bola nao passa por cima de 9,5)
  let g = caixa(MG.xCruz - 18, yComp - 1.2, zp - 4, MG.xCruz + 18, yComp + 1.2, zp + PAR + 9.5);
  g = g.fuse(caixa(MG.xCruz - 5, yComp - 1.2, zp - 12, MG.xCruz + 5, yComp + 6, zp - 4));
  return g.cut(cilC(SOL.jf0530.emb + 0.4, 12, [MG.xCruz, yComp + 2.4, zp - 12], 'z'));
}

/* ---------------------------------------------------------------- entrada, sensor, presilhas */
function entrada() {
  // encaixe da ponta do P1 + um trecho de canal aberto onde a calha de entrega do elevador apoia
  const z = MG.zP1(MG.xIn), w = DCAN / 2 + 0.3;
  let e = caixa(MG.xIn - 15, MG.y - 23, z - 23, MG.xIn + 1, MG.y + 23, z + 23);
  e = e.fuse(caixa(MG.xIn, MG.y - w - PARU, z - RB - PARU, MG.xIn + 35, MG.y + w + PARU, z + 8.5));
  e = e.cut(cil(TUBO.de + 0.8, 16, [MG.xIn - 16, MG.y, z], 'x'));
  e = e.cut(caixa(MG.xIn - 0.5, MG.y - w, z - RB, MG.xIn + 36, MG.y + w, z + 30));
  e = e.cut(cil(DCAN, 3, [MG.xIn - 1.5, MG.y, z], 'x'));
  return e;
}
function sensorNivel() {
  const x = 20, z = MG.zP1(x);
  let s = cil(52, 14, [x - 7, MG.y, z], 'x').cut(cil(TUBO.de + 0.3, 16, [x - 8, MG.y, z], 'x'));
  [-1, 1].forEach(sy => { s = s.fuse(cil(10, 8, [x, MG.y + sy * 24, z], sy > 0 ? 'y' : '-y')); });
  s = s.cut(cilC(5.15, 120, [x, MG.y, z], 'y'));
  s = s.cut(caixa(x - 8, MG.y - 1, z + 18, x + 8, MG.y + 1, z + 27));                   // fenda da abracadeira
  s = s.fuse(caixa(x - 7, MG.y - 7, z + 25, x + 7, MG.y - 1, z + 32)).fuse(caixa(x - 7, MG.y + 1, z + 25, x + 7, MG.y + 7, z + 32));
  return s.cut(cilC(FOLGA.m3, 20, [x, MG.y, z + 28.5], 'y'));
}
function presilha(x, z) {
  // sela atras do tubo + base ate o painel; o tubo e preso por uma abracadeira de nylon
  let p = caixa(x - 8, MG.y, z - 22, x + 8, MG.yPainel, z + 22);
  p = p.cut(cil(TUBO.de + 1.5, 20, [x - 10, MG.y, z], 'x'));
  p = p.cut(caixa(x - 2.2, MG.y + 18, z - 30, x + 2.2, MG.y + 23, z + 30));
  [-14, 14].forEach(dz => { p = p.cut(cilC(FOLGA.madeira, 40, [x, MG.yPainel - 10, z + dz], 'y')); });
  return p;
}
const PRES = [[-60, 'P3'], [10, 'P3'], [-110, 'P2'], [-20, 'P2'], [-110, 'P1'], [-30, 'P1']];
const zPres = (x, p) => p === 'P3' ? MG.zP3(x) : p === 'P2' ? MG.zP2(x) : MG.zP1(x);

const regImp = (id, meta, fn, ref, rot) => peca(id, Object.assign({}, IMP, meta, { imprimir: { rot: rot || [] } }),
  () => [{ forma: fn().translate(-ref[0], -ref[1], -ref[2]), cor: meta.cor || 'impresso' }]);
const REF_SAI = [MG.xE, MG.y, MG.zE], REF_CAR = [MG.xCruz, 0, zCruz(0)], REF_ENT = [MG.xIn, MG.y, MG.zP1(MG.xIn)];
regImp('mag_saida', { nome: 'Saída do magazine + escapement', dims: '≈ 80 × 70 × 60 mm',
  impressao: { preenchimento: '30 %', paredes: 4, suportes: 'não (canal aberto para cima)', tempo: '≈ 3 h' },
  notas: ['Recebe o fim do tubo P3 numa meia-cana (presa com abraçadeira de nylon) e leva a bola até a curva da travessia.',
    'Os 2 rasgos do piso são onde os dedos do balancim do servo sobem.'] }, saida, REF_SAI);
regImp('mag_balancim', { nome: 'Balancim do escapement', cor: 'impresso2', dims: '42 × 5 × 26 mm',
  impressao: { preenchimento: '100 %', paredes: 4, suportes: 'não', tempo: '15 min' },
  notas: ['Gira ±12° com o servo: um dedo sobe e segura a bola da frente; o outro desce e solta. Meia volta = 1 bola.'] },
balancim, [XPIV, MG.y, zPiso(XPIV) - 10], [['x', 90]]);
regImp('mag_carga', { nome: 'Calha de carga + comporta', dims: '≈ 75 × 140 × 55 mm',
  impressao: { preenchimento: '30 %', paredes: 4, suportes: 'só sob os trilhos', tempo: '≈ 4 h' },
  notas: ['Atravessa por baixo do bloco tensor do eixo A e entrega a bola ao berço sobre 2 trilhos.',
    'A bola só fica nos trilhos até o berço fechar a pinça: quando o carro sai, ela sai junto.',
    'Firmware: não soltar com o carro A a menos de 112 mm do centro pela esquerda — ali a bola cairia nos trilhos.'] }, carga, REF_CAR);
regImp('mag_comporta', { nome: 'Lâmina da comporta', cor: 'impresso2', dims: '36 × 7 × 26 mm',
  impressao: { preenchimento: '100 %', paredes: 4, suportes: 'não', tempo: '15 min' },
  notas: ['Fechada (solenoide desligado), sobe 9,5 mm acima do piso: a bola não passa. Ligado, o solenoide puxa 10 mm e ela some no piso.'] },
comporta, [MG.xCruz, yComp, zCruz(yComp)], [['x', 90]]);
regImp('mag_entrada', { nome: 'Entrada do magazine', dims: '50 × 46 × 46 mm',
  impressao: { preenchimento: '30 %', paredes: 4, suportes: 'não', tempo: '≈ 2 h' },
  notas: ['A calha de entrega do elevador apoia neste trecho de canal aberto e a bola entra rolando no tubo P1.'] }, entrada, REF_ENT);
regImp('mag_sensor_nivel', { nome: 'Abraçadeira do sensor de nível', cor: 'impresso2', dims: 'Ø52 × 14 mm',
  impressao: { preenchimento: '40 %', paredes: 4, suportes: 'não', tempo: '40 min' },
  notas: ['LED na frente, fototransistor atrás: o infravermelho atravessa o acrílico sem furar o tubo.',
    'Bola parada aqui = magazine cheio: o firmware desliga o elevador.'] }, sensorNivel, [20, MG.y, MG.zP1(20)], [['y', 90]]);
peca('mag_presilha', Object.assign({}, IMP, { nome: 'Sela do tubo', dims: '16 × 39 × 44 mm', imprimir: { rot: [['x', -90]] },
  impressao: { preenchimento: '30 %', paredes: 3, suportes: 'não', tempo: '40 min' },
  notas: ['Parafusada no painel por 2 parafusos de madeira; o tubo fica preso por uma abraçadeira de nylon de 3,6 mm.'] }),
() => [{ forma: presilha(0, 0).translate(0, -MG.y, 0), cor: 'impresso' }]);
peca('mag_painel', { nome: 'Painel do magazine (MDF 6 mm)', tipo: 'falta', src: 'est', dims: '338 × 6 × 200 mm',
  link: 'https://lista.mercadolivre.com.br/mdf-6mm-sob-medida',
  notas: ['Peça cortada. Fica 104 mm atrás do trilho A, preso na parede do fundo por 4 espaçadores impressos.'] },
() => [{ forma: caixa(-205, 0, -100, 133, 6, 100), cor: 'mdf' }]);
peca('mag_espacador', Object.assign({}, IMP, { nome: 'Espaçador do painel', dims: '20 × 97 × 20 mm', imprimir: { rot: [['x', 90]] },
  impressao: { preenchimento: '30 %', paredes: 4, suportes: 'não', tempo: '1 h' },
  notas: ['Liga o painel do magazine à parede do fundo do gabinete.'] }),
() => {
  let e = caixa(-10, 0, -10, 10, 97, 10);
  e = e.cut(cilC(FOLGA.madeira, 20, [0, 5, 0], 'y')).cut(cilC(FOLGA.madeira, 20, [0, 92, 0], 'y'));
  return [{ forma: e, cor: 'impresso' }];
});

/* ---------------------------------------------------------------- instancias */
function instancias() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  const r = T.of(), A = t => t.esp('z');
  // contexto: o eixo A e o berco, na posicao de carga (carro em x = -140)
  add('ctx_perfil', 'perfil2020_400', A(r.t(0, 0, -14)), { contexto: true });
  add('ctx_trilho', 'mgn12_trilho_400', A(r.t(0, 0, -4)), { contexto: true });
  add('ctx_tensor', 'eixo_bloco_tensor_semfc', A(r.t(-EX.xPe, 0, 0)), { contexto: true });
  add('ctx_motor', 'eixo_bloco_motor', A(r.t(EX.xPe, 0, 0)), { contexto: true });
  add('ctx_nema', 'nema17', A(r.rx(90).t(EX.xP, EX.yPl1, 0)), { contexto: true });
  add('ctx_patim', 'mgn12h_patim', A(r.t(-140, 0, -4)), { contexto: true });
  add('ctx_placa', 'eixo_placa_carro', A(r.t(-140, 0, 9)), { contexto: true });
  add('ctx_berco', 'soltura_berco', r.t(-140, -40, -40), { contexto: true });
  add('ctx_sol', 'sol_jf0826', r.rx(90).t(-140, SO.ySol, SO.zb), { contexto: true });
  // tubos
  add('tubo_p3', 'tubo_p3', r.ry(-4).t(MG.xE, MG.y, MG.zE));
  add('tubo_p2', 'tubo_p2', r.ry(4).t(MG.xL, MG.y, MG.zP2(MG.xL)));
  add('tubo_p1', 'tubo_p1', r.ry(-4).t(MG.xL, MG.y, MG.zP1(MG.xL)));
  // curvas
  ['f', 't'].forEach(m => {
    add('u_dir_' + m, 'mag_u_dir_' + m, r.t(MG.xR, MG.y, MG.zR));
    add('u_esq_' + m, 'mag_u_esq_' + m, r.t(MG.xL, MG.y, MG.zL));
  });
  // saida, servo, balancim, carga, comporta, solenoide
  add('saida', 'mag_saida', r.t(...REF_SAI));
  const zs = zPiso(XPIV) - 10;
  // servo deitado: eixo para -Y (para o canal), corpo para tras; o balancim fica no eixo
  add('servo', 'sg90', r.rx(90).t(XPIV - SG90.xEixo, MG.y + 2.5 + SG90.topo, zs));
  add('balancim', 'mag_balancim', r.t(XPIV, MG.y, zs));
  add('carga', 'mag_carga', r.t(...REF_CAR));
  add('comporta', 'mag_comporta', r.t(MG.xCruz, yComp, zCruz(yComp)));
  const zp = zCruz(yComp) - RB - PARU;
  // ponta de puxar para CIMA, encaixada na lamina: ligado, recolhe 10 mm e abre
  add('sol_comporta', 'sol_jf0530', r.t(MG.xCruz, yComp + 2.4, zp - 4 - 10 - SOL.jf0530.C), { semColisao: true });
  // entrada, sensor de nivel
  add('entrada', 'mag_entrada', r.ry(-4).t(...REF_ENT));
  add('nivel', 'mag_sensor_nivel', r.ry(-4).t(20, MG.y, MG.zP1(20)));
  add('nivel_led', 'ir333c', r.rx(-90).t(20, MG.y - 33, MG.zP1(20)), { semColisao: true });
  add('nivel_foto', 'til78', r.rx(90).t(20, MG.y + 33, MG.zP1(20)), { semColisao: true });
  // presilhas, painel, espacadores
  PRES.forEach(([x, p], i) => add('sela_' + i, 'mag_presilha', r.ry(p === 'P2' ? 4 : -4).t(x, MG.y, zPres(x, p))));
  [-7, 7].forEach((dx, i) => {
    add('p_junta_' + i, 'din912_m3x10', r.rx(90).t(MG.xCruz + dx, MG.y - MG.rCurva - 4.5, zCruz(MG.y - MG.rCurva) - RB - PARU - 5));
    add('porca_junta_' + i, 'porca_m3', r.rx(-90).t(MG.xCruz + dx, MG.y - MG.rCurva + 4, zCruz(MG.y - MG.rCurva) - RB - PARU - 5));
  });
  [-12, 12].forEach((dy, i) => add('mad_carga_' + i, 'madeira_3_5x16', r.ry(-90).t(-EX.parede + (MG.xCruz - DCAN / 2 - PARU + 0.3 + EX.parede), dy, zCruz(0) - RB - PARU - 11)));
  add('painel', 'mag_painel', r.t(0, MG.yPainel, 0));
  [[-190, -80], [-190, 80], [-20, -80], [-20, 80]].forEach(([x, z], i) => add('esp_' + i, 'mag_espacador', r.t(x, MG.yPainel + 6, z)));
  // bolas na fila
  const fila = [];
  for (let i = 0; i < 3; i++) fila.push([MG.xE + 1 + RB + i * 36, MG.zP3(MG.xE + 1 + RB + i * 36)]);
  fila.forEach(([x, z], i) => add('bola_' + i, 'bola35', r.t(x, MG.y, z), { semColisao: true }));
  return I;
}

export function moduloMagazine() {
  const I = instancias();
  const ids = pre => I.filter(i => i.id.startsWith(pre)).map(i => i.id);
  return {
    id: 'magazine', nome: 'Magazine',
    subtitulo: 'Atrás do eixo A. Guarda a fila de bolas e entrega uma por vez ao berço.',
    resumo: 'Três passes de tubo acrílico Ø40 com curvas em U impressas, escapement com servo SG90, comporta com o mini solenoide e a calha de carga até o berço.',
    tempo: '≈ 2 h',
    instancias: I,
    contexto: ids('ctx_'),
    // o carro A com o berco saindo da posicao de carga e indo ate o outro extremo: nada do magazine no caminho
    varredura: [{ ids: ['ctx_patim', 'ctx_placa', 'ctx_berco', 'ctx_sol'], desloc: [[8, 0, 0], [20, 0, 0], [40, 0, 0], [140, 0, 0], [280, 0, 0]],
      ignora: ['ctx_trilho', 'ctx_perfil', 'ctx_tensor', 'ctx_motor', 'ctx_nema'] }],
    passos: [
      { titulo: 'Conheça as peças', mostra: 'tudo', explode: 0.8, vista: 'iso',
        texto: 'O magazine fica atrás do eixo A (em cinza claro, com o berço parado na posição de carga, à esquerda). A bola chega do elevador pela direita, desce em zigue-zague pelos 3 tubos, passa pelo escapement, atravessa para a frente por baixo do bloco tensor do eixo A e cai nos trilhos dentro do berço.',
        atencao: ['Inclinação de 4° em vez dos 6° do modelo antigo, para o elevador caber embaixo do teto. Antes de cortar o painel, teste: tubo inclinado 4° com uma bola — ela tem que rolar sozinha de ponta a ponta.'] },
      { titulo: 'Painel e espaçadores', novos: ['painel', ...ids('esp_')], vista: 'tras',
        texto: 'Corte o painel de MDF 6 mm (338 × 200). Parafuse os 4 espaçadores impressos na parede do fundo do gabinete e o painel na frente deles, com parafusos de madeira 3,5×16. O painel fica a 104 mm do trilho A.',
        ferramentas: ['serra', 'furadeira 3 mm', 'chave Phillips nº 2'] },
      { titulo: 'Corte os tubos', novos: ['tubo_p1', 'tubo_p2', 'tubo_p3'], vista: 'iso',
        texto: 'Do tubo de acrílico Ø40, corte: P1 = 222 mm, P2 = 202 mm, P3 = 160 mm. Fita crepe em volta do corte, serra de dentes finos, depois lixe a rebarba de DENTRO com lixa enrolada num lápis.',
        atencao: ['São 584 mm: o tubo de 500 mm da planilha não basta — falta comprar mais 1.'],
        confira: ['Passe uma bola por dentro de cada trecho: ela tem que escorregar sem prender.'] },
      { titulo: 'Curvas em U', novos: ids('u_'), vista: 'iso',
        texto: 'Feche cada curva em U juntando as duas metades com 4 parafusos M3×40 e porca, com as pontas dos tubos encaixadas. Curva da ESQUERDA: liga P1 (em cima) a P2. Curva da DIREITA: liga P2 a P3 (embaixo).',
        ferramentas: ['chave allen 2,5 mm', 'alicate'] },
      { titulo: 'Selas dos tubos', novos: ids('sela_'), vista: 'iso',
        texto: 'Parafuse as 6 selas no painel (2 por tubo) e prenda cada tubo na sua sela com uma abraçadeira de nylon. Confira a inclinação com um nível digital ou app de celular: 4° em cada tubo, descendo no sentido da bola.',
        ferramentas: ['chave Phillips nº 2', 'abraçadeiras de nylon 3,6 mm', 'nível (app de celular)'] },
      { titulo: 'Entrada e sensor de nível', novos: ['entrada', 'nivel', 'nivel_led', 'nivel_foto'], vista: 'iso',
        texto: 'Encaixe a entrada na ponta direita do P1 (é onde a calha do elevador vai apoiar). Feche a abraçadeira do sensor de nível em volta do P1, perto da entrada, com 1 parafuso M3. LED na frente, fototransistor atrás: a luz infravermelha atravessa o acrílico.',
        ferramentas: ['chave allen 2,5 mm'] },
      { titulo: 'Saída e escapement', novos: ['saida', 'servo', 'balancim', ...ids('bola_')], vista: 'iso', zoom: ['saida', 'balancim'],
        texto: 'Apoie a ponta esquerda do P3 na meia-cana da saída e prenda com abraçadeira. Antes de montar o balancim, ligue o servo no ESP32 e mande para 90° (centro). Encaixe o balancim no eixo do servo com os dois dedos na mesma altura e prenda o servo no suporte com os 2 parafusinhos que vêm com ele.',
        ferramentas: ['chave Phillips pequena'],
        confira: ['Servo a 78°: o dedo da esquerda fica para cima (segura a bola da frente).', 'Servo a 102°: troca — sai UMA bola.'] },
      { titulo: 'Calha de carga e comporta', novos: ['carga', 'comporta', 'sol_comporta', ...ids('p_junta_'), ...ids('porca_junta_'), ...ids('mad_carga_')], vista: 'esquerda', zoom: ['carga'],
        texto: 'Prenda o mini solenoide JF-0530B embaixo da calha de carga (2 parafusos M3, ponta grossa para CIMA) e encaixe a lâmina da comporta na ponta do êmbolo, pelo rasgo do piso. Encaixe a calha na curva da saída. Una a calha à saída pelas 2 abas de baixo (2 parafusos M3×10 com porca) e prenda a orelha na parede esquerda do gabinete com 2 parafusos de madeira. Os 2 trilhos da ponta entram por baixo do berço quando o carro A está na esquerda.',
        ferramentas: ['chave allen 2,5 mm'],
        atencao: ['Com o carro A a menos de 112 mm do centro pela esquerda, uma bola solta cairia nos trilhos. O firmware não pode soltar ali.'],
        confira: ['Desligado: a lâmina fica 9,5 mm acima do piso. Ligado: some no piso.', 'Correndo o carro A à mão até a esquerda, o berço passa por cima dos trilhos sem encostar.'] },
    ],
  };
}
