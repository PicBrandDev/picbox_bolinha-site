/* COMO FUNCIONA — animacoes didaticas dos mecanismos (nao entram na lista de compras).

   1) carga e soltura: magazine -> escapement -> comporta -> berco -> soltura
   Referencial: o do eixo A instalado (trilho A em z = 0, frente = -Y).
   As chaves das trilhas sao T no referencial do CAD; o build converte para o three. */
import { inst } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';
import { PROJ } from '../lib/projeto.mjs';
import { SO } from './soltura.mjs';
import { EX } from './eixo.mjs';
import { MG, zCruz, yComp, F1x, F2x, XPIV, zPiso, zEsc, REF_SAI, REF_CAR } from './magazine.mjs';
import { SOL } from '../pecas/comprados.mjs';

import { EL, posCacamba, C1, C2, CR, C3, C4, zC, LCAL, XF } from './elevador.mjs';
import { caixa, cil, cilC, tubo, uniao, FOLGA } from '../lib/base.mjs';
import { peca } from '../lib/registro.mjs';
import { R } from '../lib/base.mjs';

const RB = PROJ.bolaD / 2, k4 = Math.tan(4 * Math.PI / 180);
const r = T.of();

/* caminho da bola como polilinha 3D -> chaves com tempo proporcional a distancia */
function amostra(pts, passo) {
  const out = [pts[0]];
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1], b = pts[i], d = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
    const n = Math.max(1, Math.ceil(d / passo));
    for (let j = 1; j <= n; j++) out.push(a.map((v, q) => v + (b[q] - v) * j / n));
  }
  return out;
}
function arco(cx, cy, raio, a0, a1, z0, z1, n) {
  const p = [];
  for (let i = 0; i <= n; i++) { const a = (a0 + (a1 - a0) * i / n) * Math.PI / 180; p.push([cx + raio * Math.cos(a), cy + raio * Math.sin(a), z0 + (z1 - z0) * i / n]); }
  return p;
}
// chaves de uma bola rolando: posicao + giro (angulo = distancia / raio, em torno do eixo deitado)
function rolando(pts, t0, t1) {
  let L = 0; const acc = [0];
  for (let i = 1; i < pts.length; i++) { L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1], pts[i][2] - pts[i - 1][2]); acc.push(L); }
  let gx = 0, gy = 0;
  return pts.map((p, i) => {
    if (i > 0) {
      const dx = p[0] - pts[i - 1][0], dy = p[1] - pts[i - 1][1];
      gx += -dy / RB * 180 / Math.PI; gy += dx / RB * 180 / Math.PI;
    }
    return [t0 + (t1 - t0) * (L ? acc[i] / L : 0), r.rx(gx).ry(gy).t(...p)];
  });
}
const parado = (p, t) => [t, r.t(...p)];

/* ---------------------------------------------------------------- posicoes-chave */
const zTr = SO.zb;                                        // centro da bola nos trilhos/berco
const P_GATE = [MG.xCruz, yComp + 1.2 + RB, zCruz(yComp + 1.2 + RB)];          // esperando na comporta
const y1 = SO.yb + MG.rCurva;
const P_BERCO = [-140 + 0.25, SO.yb, zTr];
const caminhoCarga = amostra([P_GATE, [MG.xCruz, y1, zCruz(y1)],
  ...arco(MG.xCanto, y1, MG.rCurva, 180, 270, zCruz(y1), zCruz(y1) - 2.4, 8).slice(1),
  [MG.xCanto + 8, SO.yb, zTr + 0.5], P_BERCO], 6);
const P_F1 = [F1x + 1.5 + RB, MG.y, zEsc(F1x + 1.5 + RB)];                        // 1a da fila (no dedo da frente)
const P_F2 = [P_F1[0] + PROJ.bolaD, MG.y, zEsc(P_F1[0] + PROJ.bolaD)];             // 2a da fila
const zA = zEsc(MG.xCanto);
const caminhoEsc = amostra([P_F1, [MG.xCanto, MG.y, zA],
  ...arco(MG.xCanto, MG.y - MG.rCurva, MG.rCurva, 90, 180, zA, zA - 2.4, 8).slice(1),
  [MG.xCruz, MG.y - MG.rCurva, zCruz(MG.y - MG.rCurva)], P_GATE], 6);

/* ---------------------------------------------------------------- linha do tempo (s) */
const DUR = 16;
const XC = [[0, -60], [1.5, -140], [5.0, -140], [8.0, 60], [9.9, 60], [16, -60]];   // centro do carro A
const xc = t => { for (let i = 1; i < XC.length; i++) if (t <= XC[i][0]) { const [t0, a] = XC[i - 1], [t1, b] = XC[i]; const u = (t - t0) / (t1 - t0); return a + (b - a) * (u * u * (3 - 2 * u)); } return XC[XC.length - 1][1]; };
const TEMPOS = [0, 0.5, 1, 1.5, 5.0, 5.75, 6.5, 7.25, 8.0, 9.9, 11.5, 13, 14.5, 16];
// embolo: 0 = estendido (pinca fechada), 10 = recolhido
const EMB = [[0, 0], [1.5, 0], [2.0, 10], [4.6, 10], [5.0, 0], [8.6, 0], [8.65, 10], [8.95, 10], [9.1, 0], [16, 0]];
const emb = t => { for (let i = 1; i < EMB.length; i++) if (t <= EMB[i][0]) { const [t0, a] = EMB[i - 1], [t1, b] = EMB[i]; return a + (b - a) * (t - t0) / (t1 - t0); } return 0; };

function trilhasCarga(I) {
  const tr = [];
  const carro = (id, base) => tr.push({ id, k: TEMPOS.map(t => [t, base.em(r.t(xc(t), 0, 0))]) });
  const A = t => t.esp('z');
  carro('patim', A(r.t(0, 0, -4)));
  carro('placa', A(r.t(0, 0, 9)));
  carro('berco', r.t(0, -40, -40));
  carro('batente', r.t(19.75, -57, -50));
  carro('sol_corpo', r.rx(90).t(0, SO.ySol, SO.zb));
  const tEmb = [...new Set([...TEMPOS, ...EMB.map(e => e[0])])].sort((a, b) => a - b);
  tr.push({ id: 'sol_embolo', k: tEmb.map(t => [t, r.rx(90).t(0, SO.ySol + emb(t), SO.zb).em(r.t(xc(t), 0, 0))]) });
  // comporta: desce 10 mm de 2,0 a 2,4 s e sobe de 4,2 a 4,6 s
  const G0 = r.t(MG.xCruz, yComp, zCruz(yComp)), G1 = r.t(MG.xCruz, yComp, zCruz(yComp) - 10);
  tr.push({ id: 'comporta', k: [[0, G0], [2.0, G0], [2.4, G1], [4.2, G1], [4.6, G0], [16, G0]] });
  // balancim: -12 (segura) -> +12 (solta) de 5,0 a 5,4; volta de 6,0 a 6,4
  const zs = zPiso(XPIV) - 10, B0 = r.t(XPIV, MG.y, zs), B1 = r.ry(24).t(XPIV, MG.y, zs);
  tr.push({ id: 'balancim', k: [[0, B0], [5.0, B0], [5.4, B1], [6.0, B1], [6.4, B0], [16, B0]] });
  // bola 1: espera na comporta, rola ate o berco, vai com o carro, cai, volta para o fim da fila
  const k1 = [parado(P_GATE, 0), parado(P_GATE, 2.4), ...rolando(caminhoCarga, 2.4, 4.2)];
  [5.0, 5.75, 6.5, 7.25, 8.0, 8.6].forEach(t => k1.push([t, r.t(P_BERCO[0] + xc(t) + 140, P_BERCO[1], P_BERCO[2])]));
  for (let i = 1; i <= 8; i++) {                                    // queda livre (camera lenta: 1,3 s)
    const u = i / 8; k1.push([8.6 + 1.3 * u, r.t(P_BERCO[0] + 200, P_BERCO[1], P_BERCO[2] - PROJ.queda * u * u)]);
  }
  k1.push([15.9, r.t(P_BERCO[0] + 200, P_BERCO[1], P_BERCO[2] - PROJ.queda)], [15.95, r.t(...P_F2)], [16, r.t(...P_F2)]);
  tr.push({ id: 'bola1', k: k1 });
  // bola 2: espera no dedo da frente, sai no escapement e para na comporta
  tr.push({ id: 'bola2', k: [parado(P_F1, 0), parado(P_F1, 5.4), ...rolando(caminhoEsc, 5.4, 7.4), parado(P_GATE, 16)] });
  // bola 3: segunda da fila; anda para o dedo da frente quando o balancim volta
  tr.push({ id: 'bola3', k: [parado(P_F2, 0), parado(P_F2, 6.4), ...rolando(amostra([P_F2, P_F1], 6), 6.4, 6.9), parado(P_F1, 16)] });
  return tr;
}

const LEG = [
  [0, 1.5, '1 · O carro A anda até a ponta esquerda e PARA: o berço fica alinhado com o fim da calha de carga.'],
  [1.5, 2.0, '2 · O solenoide do berço LIGA: o êmbolo recua 10 mm e a pinça abre.'],
  [2.0, 2.4, '3 · O mini solenoide puxa a lâmina da comporta para baixo: o caminho fica livre.'],
  [2.4, 4.2, '4 · A bola faz a curva, sobe nos 2 trilhos que entram por baixo do berço e para no batente.'],
  [4.2, 4.6, '5 · A comporta sobe de novo (mola do mini solenoide).'],
  [4.6, 5.0, '6 · O solenoide do berço DESLIGA: a mola empurra o êmbolo e prende a bola contra o V.'],
  [5.0, 8.0, '7 · O carro sai levando a bola (os trilhos ficam). Ao mesmo tempo o escapement solta a PRÓXIMA bola, que rola até a comporta e espera.'],
  [8.0, 8.6, '8 · O jogador aperta o botão no momento certo.'],
  [8.6, 9.9, '9 · O êmbolo recua: a bola fica sem nada embaixo e cai reta. (Câmera lenta: na máquina são 0,23 s até a boca.)'],
  [9.9, 16, '10 · O carro volta para buscar a próxima. Na máquina o ciclo inteiro leva ~2,4 s.'],
];
const ANIM = I => ({ dur: DUR, trilhas: trilhasCarga(I), leg: LEG });

const PQ_CARGA = [
  { alvo: 'carga', em: [0, -10, 15], titulo: 'Por que a calha passa por baixo do bloco do eixo A',
    resumo: 'É o único caminho de trás para a frente que o carro A nunca ocupa.',
    texto: 'O magazine fica ATRÁS do eixo A e o berço na FRENTE. Para atravessar, a calha tem que cruzar o plano do trilho. No meio do curso o carro passaria por cima dela; na ponta direita estão o motor e a coluna do elevador. Na ponta esquerda, logo abaixo do bloco tensor, sobra o espaço — e é exatamente lá que o carro para para carregar.' },
  { alvo: 'comporta', titulo: 'Por que a comporta DESCE (e não gira)',
    resumo: 'Girando, ela abriria dentro do caminho do berço.',
    texto: 'Uma lâmina que gira varre um arco: aberta, ela invadiria o espaço por onde o berço passa quando o carro vai embora. Descendo, ela some dentro do piso da calha e nunca sai dali. Ela sobe 9,5 mm acima do piso: uma bola de 35 mm não sobe um degrau desse tamanho, e o solenoide de 10 mm de curso consegue esconder a lâmina inteira.' },
  { alvo: 'bola1', em: [0, 0, -22], titulo: 'Por que 2 trilhos dentro do berço',
    resumo: 'Seguram a bola só durante a carga e deixam o caminho de queda livre.',
    texto: 'Enquanto a pinça está aberta, alguma coisa tem que segurar a bola por baixo. Mas um piso dentro do berço impediria a bola de cair na hora da soltura. A solução: 2 trilhos finos, 20 mm afastados, que vêm da calha (fixos) e entram por baixo do berço só na posição de carga. A pinça fecha, o carro vai embora e leva a bola — os trilhos ficam para trás. Eles passam 3,5 mm abaixo do V e do êmbolo.' },
  { alvo: 'batente', titulo: 'Por que tem um batente',
    resumo: 'Para a bola exatamente no centro antes da pinça fechar.',
    texto: 'A pinça está aberta durante a carga: sem o batente a bola passaria direto. Ele fica a 0,25 mm de onde o centro da bola tem que estar. É uma peça separada para poder ser ajustada (lixada ou reimpressa) sem refazer o berço.' },
  { alvo: 'berco', em: [0, -30, -20], titulo: 'Por que a bola é presa pela LATERAL',
    resumo: 'Um pino por baixo precisaria de 22 mm de curso; o solenoide tem 10.',
    texto: 'Para uma bola de 35 mm cair, tudo que está embaixo dela tem que sair da frente uns 22 mm — o solenoide comprado anda 10. Segurando pelas laterais, na altura do equador, 10 mm sobram: o êmbolo recua, a bola fica sem nada encostado e cai na vertical. Não há empurrão em X (a direção que decide o jogo).' },
  { alvo: 'sol_embolo', titulo: 'Por que desligado = segurando',
    resumo: 'Falha segura e a bobina só esquenta na hora de soltar.',
    texto: 'A mola do solenoide empurra o êmbolo contra a bola o tempo todo. Ele só é ligado por 50 ms para soltar (e por ~3 s durante a carga). Se faltar energia, a bola fica presa — nunca cai sozinha.' },
  { alvo: 'balancim', titulo: 'Escapement: por que dois dedos',
    resumo: 'Sempre tem um dedo segurando a fila.',
    texto: 'Com um dedo só, no instante em que ele desce para soltar a 1ª bola, a fila inteira iria junto. O balancim é uma gangorra: quando o dedo da frente desce, o de trás sobe ENTRE a 1ª e a 2ª bola. Sai uma, a fila fica. Quando ele volta, a fila anda uma posição.' },
];
const PQ_SOLTA = [PQ_CARGA[4], PQ_CARGA[5],
  { alvo: 'berco', em: [0, -40, -28], titulo: 'Por que um V na frente',
    resumo: 'Dois pontos de contato a 45°: centra a bola em X sozinho.',
    texto: 'As duas faces do V tocam a bola em dois pontos. Quando o êmbolo empurra, a bola desliza para o fundo do V e fica centrada em X — a direção do jogo — sem ajuste nenhum. E o contato fica na altura do equador: a força do êmbolo não empurra a bola nem para cima nem para baixo.' },
  PQ_CARGA[3]];

function instancias() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  const A = t => t.esp('z');
  add('ctx_perfil', 'perfil2020_400', A(r.t(0, 0, -14)), { contexto: true });
  add('ctx_trilho', 'mgn12_trilho_400', A(r.t(0, 0, -4)), { contexto: true });
  add('ctx_tensor', 'eixo_bloco_tensor_semfc', A(r.t(-EX.xPe, 0, 0)), { contexto: true });
  // carro A com o berco (posicoes iniciais; a animacao manda)
  add('patim', 'mgn12h_patim', A(r.t(-60, 0, -4)));
  add('placa', 'eixo_placa_carro', A(r.t(-60, 0, 9)));
  add('berco', 'soltura_berco', r.t(-60, -40, -40));
  add('batente', 'soltura_batente', r.t(-60 + 19.75, -57, -50));
  add('sol_corpo', 'sol_jf0826_corpo', r.rx(90).t(-60, SO.ySol, SO.zb));
  add('sol_embolo', 'sol_jf0826_embolo', r.rx(90).t(-60, SO.ySol, SO.zb));
  // magazine: saida, escapement, carga, comporta
  add('saida', 'mag_saida', r.t(...REF_SAI));
  add('servo', 'sg90', r.rx(90).t(XPIV + 5.2, MG.y + 2.5 + 31, zPiso(XPIV) - 10));
  add('balancim', 'mag_balancim', r.t(XPIV, MG.y, zPiso(XPIV) - 10));
  add('carga', 'mag_carga', r.t(...REF_CAR));
  add('comporta', 'mag_comporta', r.t(MG.xCruz, yComp, zCruz(yComp)));
  add('sol_comporta', 'sol_jf0530', r.t(MG.xCruz, yComp + 2.4, zCruz(yComp) - RB - 2.5 - 4 - 10 - SOL.jf0530.C));
  add('tubo_p3', 'tubo_p3', r.ry(-4).t(MG.xE, MG.y, MG.zE));
  ['bola1', 'bola2', 'bola3'].forEach(id => add(id, 'bola35', r.t(...P_GATE)));
  return I;
}

export function moduloFuncCarga() {
  const I = instancias();
  const anim = ANIM(I);
  const todos = I.filter(i => !i.id.startsWith('ctx_')).map(i => i.id);
  return {
    id: 'func_carga', nome: 'Como funciona: carga e soltura', didatico: true,
    subtitulo: 'Animação do caminho da bola: do magazine até cair no alvo.',
    resumo: 'O ciclo completo em câmera lenta: escapement, comporta, calha de carga, berço de pinça e soltura — com o "por que" de cada peça.',
    tempo: 'animação de 16 s (na máquina: ~2,4 s)',
    instancias: I,
    contexto: I.filter(i => i.id.startsWith('ctx_')).map(i => i.id),
    passos: [
      { titulo: 'O ciclo completo', base: todos, vista: 'iso', zoom: ['berco', 'carga', 'saida'], anim, porques: PQ_CARGA,
        transparentes: ['berco'],
        texto: 'Assista ao ciclo inteiro. O berço está translúcido para dar para ver a bola e o êmbolo dentro dele. Pause (espaço) e gire a câmera à vontade; clique numa etapa do roteiro para pular para ela, ou num círculo amarelo para ver por que aquela peça é daquele jeito.' },
      { titulo: 'Da comporta para o berço', base: todos, vista: 'esquerda', zoom: ['carga', 'comporta', 'bola1'], anim, porques: [PQ_CARGA[1], PQ_CARGA[2], PQ_CARGA[3], PQ_CARGA[0]],
        transparentes: ['berco'],
        texto: 'Olhando pela esquerda, de perto: a comporta desce, a bola faz a curva, sobe nos trilhos e para no batente. Depois a pinça fecha e o carro leva a bola embora — os trilhos ficam.' },
      { titulo: 'A soltura por dentro', base: todos, vista: 'frente', zoom: ['berco', 'sol_corpo'], anim, porques: PQ_SOLTA,
        transparentes: ['berco', 'placa', 'patim'],
        texto: 'Olhe o êmbolo (atrás da bola) e o V (na frente): desligado, a mola empurra o êmbolo e a bola fica espremida contra o V. Ligado, o êmbolo recua 10 mm — e só isso. A bola não tem nada embaixo: ela cai reta.' },
      { titulo: 'O escapement', base: todos, vista: 'tras', zoom: ['saida', 'balancim', 'servo'], anim, porques: [PQ_CARGA[6]],
        texto: 'A gangorra (balancim) no eixo do servo: um dedo sobe enquanto o outro desce. Sai exatamente uma bola por movimento.' },
    ],
  };
}


/* ================================================================ 2) ELEVADOR — como funciona
   Referencial da maquina. Animacao a METADE da velocidade real (NEMA a 50 rpm na tela). */

const VEL = 73.5;                                   // mm/s na animacao (real: 147)
const DUR_E = +(EL.L / VEL).toFixed(2);             // uma volta da correia
function chavesCacamba(s0) {
  const k = [];
  for (let t = 0; t <= DUR_E + 1e-6; t += 0.12) {
    const p = posCacamba(s0 + VEL * t);
    k.push([Math.min(t, DUR_E), r.rx(p.phi).t(EL.x, p.y, p.z)]);
  }
  return k;
}
function chavesBolaElevador() {
  const sB = 2 * EL.C + Math.PI * EL.Ro * 1.5;       // fundo da volta de baixo
  const sD = EL.C + Math.PI * EL.Ro * 0.75;          // 45 graus depois do alto: onde a capa acaba
  const s0 = sB - VEL * 1.6;                          // a cacamba 0 passa no fundo em t = 1,6 s
  const naCac = s => { const p = posCacamba(s); return r.t(0, 20, 16.5).em(r.rx(p.phi).t(EL.x, p.y, p.z)); };
  const k = [];
  // entra pelo bico da concha e rola ate o fundo
  const ent = [EL.x, EL.y - 72, 1123.2], fundo = naCac(sB);
  k.push([0, r.t(...ent)], [0.9, fundo]);
  // a cacamba passa e leva
  const tSobe = (EL.L - sB + sD) / VEL;
  for (let u = 0; u <= 1.0001; u += 0.02) { const t = 1.6 + tSobe * u; k.push([t, naCac(sB + VEL * (t - 1.6))]); }
  const tD = 1.6 + tSobe;
  // cai na calha de entrega e rola ate o magazine
  const pts = [[C1[0], C1[1], zC(0)], [C2[0], C2[1], zC(C1[1] - C2[1])]];
  for (let i = 1; i <= 8; i++) { const a = -i / 8 * Math.PI / 2; pts.push([EL.x - CR + CR * Math.cos(a), C2[1] + CR * Math.sin(a), zC(C1[1] - C2[1] + CR * Math.PI / 2 * i / 8)]); }
  pts.push([C4[0], C4[1], zC(LCAL)]);
  pts.forEach((p, i) => k.push([tD + 0.4 + i * 0.18, r.t(...p)]));
  k.push([DUR_E - 0.05, r.t(...pts[pts.length - 1])], [DUR_E, r.t(...ent)]);
  return k;
}
export function moduloFuncElevador() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  add('ctx_entrada', 'mag_entrada', r.ry(-4).t(MG.xIn, MG.y, MG.zP1(MG.xIn)).t(0, 0, 1530), { contexto: true });
  add('ctx_p1', 'tubo_p1', r.ry(-4).t(MG.xL, MG.y, MG.zP1(MG.xL)).t(0, 0, 1530), { contexto: true });
  add('lat_e', 'elev_lateral', r.t(EL.xPe, 0, 0));
  add('lat_d', 'elev_lateral_d', r.t(EL.xPd, 0, 0));
  add('motor', 'nema17', r.ry(90).t(XF, EL.y, EL.zt));
  add('polia_cima', 'elev_polia_motora', r.ry(90).t(EL.x - 3, EL.y, EL.zt));
  add('polia_baixo', 'elev_polia_livre', r.ry(90).t(EL.x - 3, EL.y, EL.zb));
  add('correia', 'correia_elev', r.ry(-90).rz(90).t(EL.x, EL.y, EL.zb));
  add('capa', 'elev_capa', r.t(EL.x, EL.y, EL.zt));
  add('concha', 'elev_concha', r.t(EL.x, EL.y, EL.zb));
  add('tampa', 'elev_tampa', r.t(EL.x, EL.y + EL.yTampa, EL.zb + 0.5));
  add('calha', 'elev_calha_entrega', r.t(EL.x, 80, EL.zt));
  for (let i = 0; i < EL.nCac; i++) add('cac_' + i, 'elev_cacamba', r.t(EL.x, EL.y, EL.zb));
  add('bola', 'bola35', r.t(EL.x, EL.y, EL.zb));
  const sB = 2 * EL.C + Math.PI * EL.Ro * 1.5;
  const trilhas = [];
  for (let i = 0; i < EL.nCac; i++) trilhas.push({ id: 'cac_' + i, k: chavesCacamba(sB - VEL * 1.6 + i * EL.L / EL.nCac) });
  trilhas.push({ id: 'bola', k: chavesBolaElevador() });
  const anim = { dur: DUR_E, trilhas, leg: [
    [0, 0.9, '1 · A bola chega da bandeja pelo bico da concha e rola até o fundo.'],
    [0.9, 1.6, '2 · Ela espera parada no fundo, bem no caminho dos copos.'],
    [1.6, 3.0, '3 · O próximo copo passa por baixo, "varre" a bola e começa a subir com ela (pelo lado de trás).'],
    [3.0, 1.6 + (EL.L - sB + EL.C + Math.PI * EL.Ro * 0.75) / VEL - 0.8, '4 · Subida: a tampa de acrílico atrás impede a bola de sair do copo.'],
    [1.6 + (EL.L - sB + EL.C + Math.PI * EL.Ro * 0.75) / VEL - 0.8, 1.6 + (EL.L - sB + EL.C + Math.PI * EL.Ro * 0.75) / VEL + 0.4, '5 · No alto o copo vira; a capa segura a bola até 45° depois do topo — ali ela cai na calha.'],
    [1.6 + (EL.L - sB + EL.C + Math.PI * EL.Ro * 0.75) / VEL + 0.4, DUR_E, '6 · A calha leva a bola, descendo 4°, até a entrada do magazine.'],
  ] };
  const todos = I.filter(i => !i.id.startsWith('ctx_')).map(i => i.id);
  const PQ = [
    { alvo: 'concha', titulo: 'Por que a bola ESPERA no fundo', resumo: 'O copo varre a bola; não precisa acertar o tempo.',
      texto: 'A concha tem o fundo exatamente no caminho dos copos. A bola chega a qualquer hora, rola até lá e fica parada. O próximo copo que passa a empurra para dentro dele. Nenhum sensor ou sincronismo é necessário.' },
    { alvo: 'tampa', titulo: 'Por que uma tampa na subida', resumo: 'O copo é aberto para fora.',
      texto: 'O copo só tem fundo e laterais; para fora ele é aberto (é por ali que a bola sai no topo). Na subida, a tira de acrílico a 1 mm da bola fecha esse lado. Transparente para dar para ver.' },
    { alvo: 'capa', titulo: 'Por que a capa acaba a 45° depois do alto', resumo: 'É ali que a bola sai — o ponto de saída é geométrico.',
      texto: 'Na curva de cima o copo vira e a bola ficaria solta: a capa a segura. Onde a capa acaba, a bola sai, sempre no mesmo ponto, sem sensor nem tempo. Se na bancada a bola não cair certinho na calha, é a ponta desta peça que se ajusta.' },
    { alvo: 'cac_3', titulo: 'Por que o copo é preso pela borda da correia', resumo: 'A correia tem alma de aço e não pode ser furada.',
      texto: 'Dois parafusos M2 passam rente às bordas da correia e uma arruela por dentro segura cada borda. A polia tem só 6 mm de dentes no meio dos 10 mm da correia: as arruelas passam ao lado dela.' },
  ];
  return {
    id: 'func_elevador', nome: 'Como funciona: elevador', didatico: true,
    subtitulo: 'Animação da bola do fundo até o magazine (metade da velocidade real).',
    resumo: 'Correia com copos: a bola espera na concha, é varrida, sobe atrás da tampa e sai no ponto onde a capa acaba.',
    tempo: `animação de ${DUR_E.toFixed(1)} s (real: ${(EL.L / 147).toFixed(1)} s por volta)`,
    instancias: I,
    contexto: ['ctx_entrada', 'ctx_p1'],
    passos: [
      { titulo: 'O caminho da bola', base: todos, vista: 'direita', anim, porques: PQ, transparentes: ['lat_d', 'capa', 'tampa', 'concha'],
        texto: 'A lateral direita, a capa, a concha e a tampa estão translúcidas para ver os copos e a bola. Siga a bola: concha → copo → topo → calha → magazine.' },
      { titulo: 'O topo de perto', base: todos, vista: 'direita', zoom: ['capa', 'calha', 'polia_cima'], anim, porques: [PQ[2]], transparentes: ['lat_d', 'capa'],
        texto: 'Onde a capa acaba, a bola sai do copo e cai na calha de entrega.' },
      { titulo: 'O fundo de perto', base: todos, vista: 'direita', zoom: ['concha', 'polia_baixo'], anim, porques: [PQ[0], PQ[3]], transparentes: ['lat_d', 'concha'],
        texto: 'A bola chega pelo bico, para no fundo da concha e o copo a leva.' },
    ],
  };
}

/* ================================================================ 3) ALTERNATIVA: BOMBA DE COLUNA COM PISTAO
   Um tubo vertical cheio de bolas; embaixo, um pistao empurra a coluna inteira UMA bola
   para cima por ciclo. Linguetas de mao unica seguram a coluna quando o pistao desce.
   A bola de cima transborda para a calha do magazine. Mesmo canto do elevador. */
const PB = { x: EL.x, y: EL.y, d: 37, n: 13, curso: 40 };
// a bola de cima (pos(N)) tem que ficar 10 mm acima do comeco da calha de entrega: dai sai a altura da camara
PB.z0 = zC(0) + 10 + 38 - (PB.n + 1) * PB.d;
PB.tubo = (PB.n + 1) * PB.d - 38 - 19 - 10;          // o tubo acaba logo abaixo da bola que transborda
const ALT = { tipo: 'impresso', src: 'est', material: 'PETG', didatico: true };
peca('alt_tubo', { nome: 'Tubo da coluna (acrílico Ø40 × 36, ~520 mm)', tipo: 'cortar', src: 'est', didatico: true, dims: 'Ø40 × 520 mm',
  notas: ['Alternativa ao elevador: a coluna de bolas sobe por dentro dele.'] },
() => [{ forma: tubo(40, 36, PB.tubo, [0, 0, 0], 'z'), cor: 'acrilico' }]);
peca('alt_camara', Object.assign({}, ALT, { nome: 'Câmara da bomba (entrada lateral + linguetas)', dims: '60 × 60 × 90 mm', imprimir: { rot: [] },
  impressao: { preenchimento: '40 %', paredes: 4, suportes: 'não', tempo: '≈ 3 h' } }),
() => {
  let c = caixa(-30, -30, -60, 30, 30, 30).cut(cil(37, 100, [0, 0, -70], 'z'));
  c = c.cut(caixa(-19, -60, -58, 19, 0, -18));                     // entrada lateral (vem da bandeja, pela frente)
  c = c.cut(cil(40.4, 12, [0, 0, 19], 'z'));                      // encaixe do tubo
  [-1, 1].forEach(s => { c = c.cut(caixa(s * 15, -4, -14, s * 31, 4, 2)); });   // janelas das linguetas
  return [{ forma: c, cor: 'impresso' }];
});
peca('alt_lingueta', Object.assign({}, ALT, { nome: 'Lingueta de mão única', cor: 'impresso2', dims: '14 × 8 × 16 mm', imprimir: { rot: [] },
  impressao: { preenchimento: '100 %', paredes: 4, suportes: 'não', tempo: '10 min' } }),
() => [{ forma: caixa(-7, -4, 0, 7, 4, 3).fuse(caixa(-7, -4, 0, -4, 4, 16)), cor: 'impresso2' }]);
peca('alt_atuador', { nome: 'Pistão elétrico (atuador linear 12 V, curso 50 mm)', tipo: 'falta', src: 'est', didatico: true,
  dims: '≈ 30 × 50 × 150 mm, haste Ø8', link: 'https://lista.mercadolivre.com.br/atuador-linear-12v-50mm',
  notas: ['Precisa de ~40 mm/s ou mais para dar conta de 1 bola a cada 2,4 s.', 'Durabilidade: atuadores baratos são feitos para dezenas de milhares de ciclos — aqui seriam ~1000 por dia.'] },
() => [{ forma: caixa(-15, -25, -150, 15, 25, -20).fuse(cil(18, 20, [0, 0, -20], 'z')), cor: 'acoEsc' },
  { forma: cil(8, 60, [0, 0, -20], 'z'), cor: 'aco' }]);
peca('alt_copo', Object.assign({}, ALT, { nome: 'Copo do pistão', cor: 'impresso2', dims: 'Ø35 × 12 mm', imprimir: { rot: [] },
  impressao: { preenchimento: '100 %', paredes: 4, suportes: 'não', tempo: '15 min' } }),
() => [{ forma: cil(34, 12, [0, 0, -12], 'z').cut(R.makeSphere(17.5).translate(0, 0, 13.5)), cor: 'impresso2' }]);

export function moduloAltPistao() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  const zEnt = PB.z0 - 38;                        // centro da bola na posicao de entrada (no copo, embaixo)
  add('camara', 'alt_camara', r.t(PB.x, PB.y, PB.z0));
  add('tubo', 'alt_tubo', r.t(PB.x, PB.y, PB.z0 + 19));
  add('atuador', 'alt_atuador', r.t(PB.x, PB.y, zEnt - 17.5 - 12 - 40));
  add('copo', 'alt_copo', r.t(PB.x, PB.y, zEnt - 17.5));
  add('ling_e', 'alt_lingueta', r.t(PB.x - 23, PB.y, PB.z0 - 12));
  add('ling_d', 'alt_lingueta', r.rz(180).t(PB.x + 23, PB.y, PB.z0 - 12));
  add('ctx_calha', 'elev_calha_entrega', r.t(EL.x, 80, EL.zt), { contexto: true });
  /* posicoes: 0 = entrada lateral; 1 = no copo; j >= 1 -> zEnt + (j-1)*d. No inicio do ciclo a coluna
     (b1..b_{N-1}) esta apoiada nas linguetas, de pos(2) a pos(N). Cada bola termina o ciclo onde a
     seguinte comecou: como as bolas sao iguais, o laco da animacao nao tem salto. */
  const N = PB.n + 2;
  for (let i = 0; i < N; i++) add('b' + i, 'bola35', r.t(PB.x, PB.y, PB.z0));
  const D = 2.4, d = PB.d;
  const pos = j => j === 0 ? [PB.x, PB.y - 45, zEnt + 4] : [PB.x, PB.y, zEnt + (j - 1) * d];
  const trilhas = [{ id: 'b0', k: [[0, r.t(...pos(0))], [0.6, r.t(...pos(1))], [1.4, r.t(...pos(2))], [D, r.t(...pos(2))]] }];
  for (let i = 1; i < N - 1; i++)
    trilhas.push({ id: 'b' + i, k: [[0, r.t(...pos(i + 1))], [0.6, r.t(...pos(i + 1))], [1.4, r.t(...pos(i + 2))], [D, r.t(...pos(i + 2))]] });
  const topo = pos(N), sai = [C1[0], C1[1] - 4, zC(0)];
  trilhas.push({ id: 'b' + (N - 1), k: [[0, r.t(...topo)], [0.6, r.t(...topo)], [1.4, r.t(topo[0], topo[1] - 20, topo[2] + 14)], [2.0, r.t(...sai)], [D, r.t(...sai)]] });
  const Cu0 = r.t(PB.x, PB.y, zEnt - 17.5), Cu1 = r.t(PB.x, PB.y, zEnt - 17.5 + d);
  trilhas.push({ id: 'copo', k: [[0, Cu0], [0.6, Cu0], [1.4, Cu1], [1.6, Cu1], [D, Cu0]] });
  const Le0 = r.t(PB.x - 23, PB.y, PB.z0 - 12), Le1 = r.ry(-35).t(PB.x - 23, PB.y, PB.z0 - 12);
  const Ld0 = r.rz(180).t(PB.x + 23, PB.y, PB.z0 - 12), Ld1 = r.rz(180).ry(-35).t(PB.x + 23, PB.y, PB.z0 - 12);
  trilhas.push({ id: 'ling_e', k: [[0, Le0], [0.8, Le0], [1.0, Le1], [1.3, Le1], [1.5, Le0], [D, Le0]] });
  trilhas.push({ id: 'ling_d', k: [[0, Ld0], [0.8, Ld0], [1.0, Ld1], [1.3, Ld1], [1.5, Ld0], [D, Ld0]] });
  const anim = { dur: D, trilhas, leg: [
    [0, 0.6, '1 · Pistão embaixo: a bola que volta da bandeja entra pela lateral e cai no copo.'],
    [0.6, 1.4, '2 · O pistão sobe 37 mm e empurra a COLUNA INTEIRA uma bola para cima; as linguetas abrem para deixar passar.'],
    [1.4, 1.6, '3 · As linguetas fecham por baixo da bola nova: agora são elas que seguram a coluna.'],
    [1.6, 2.4, '4 · O pistão desce para buscar a próxima. Lá em cima, a bola do topo transbordou para a calha do magazine.'],
  ] };
  const todos = I.filter(i => !i.id.startsWith('ctx_')).map(i => i.id);
  return {
    id: 'alt_pistao', nome: 'Alternativa: pistão', didatico: true,
    subtitulo: 'No lugar do elevador de caçambas: uma coluna de bolas empurrada por um pistão elétrico.',
    resumo: 'Bomba de coluna: tubo vertical cheio de bolas, pistão embaixo e linguetas de mão única. Comparação com o elevador de caçambas.',
    tempo: 'animação de 1 ciclo (2,4 s)',
    instancias: I,
    contexto: ['ctx_calha'],
    passos: [
      { titulo: 'Como funciona', base: todos, vista: 'direita', anim, transparentes: ['camara', 'tubo'], zoom: ['camara', 'atuador', 'b3'],
        texto: 'É uma "bomba de bolas": a cada ciclo o pistão empurra a fila inteira uma bola para cima, e a bola do topo transborda para a calha do magazine. Duas linguetas de mão única, na câmara, deixam a fila subir mas não descer.',
        porques: [
          { alvo: 'ling_e', titulo: 'Por que as linguetas', resumo: 'Seguram a coluna enquanto o pistão desce.',
            texto: 'Sem elas, quando o pistão desce a coluna inteira desceria junto. Elas giram para fora quando a bola sobe (a bola as empurra) e voltam por baixo dela por gravidade ou mola. É a mesma ideia de uma catraca.' },
          { alvo: 'atuador', titulo: 'O ponto fraco: durabilidade do atuador', resumo: '~1000 ciclos por dia; atuador barato aguenta dezenas de milhares.',
            texto: 'Cada bola que volta é um ciclo do pistão. Com 120 partidas por dia de até 8 rodadas, são ~1000 ciclos/dia. Atuadores lineares de 12 V baratos são feitos para abrir e fechar coisas algumas vezes por dia (vida de 10–50 mil ciclos): durariam semanas. Se for por esse caminho, o "pistão" deve ser um NEMA 17 com manivela ou came — a mesma bomba, com vida praticamente infinita.' },
        ] },
      { titulo: 'Comparação com o elevador de caçambas', base: todos, vista: 'iso', anim, transparentes: ['camara', 'tubo'],
        tabela: [
          ['Bolas presas no transporte', 'caçambas: 0–6 (só as que estão subindo)', 'pistão: 13 SEMPRE dentro do tubo → a máquina precisa de ~28 bolas, não 15'],
          ['Ritmo', 'caçambas: 1 bola a cada 0,6 s (com o NEMA a 100 rpm)', 'pistão: 1 por ciclo; precisa de ≥ 40 mm/s para 2,4 s'],
          ['Travamento', 'caçambas: uma bola ruim fica no copo e passa', 'pistão: uma bola ovalada ou suja trava a coluna inteira'],
          ['Durabilidade', 'caçambas: NEMA + correia, anos', 'pistão: atuador barato, semanas (NEMA + manivela resolve)'],
          ['Espaço', 'caçambas: 56 × 111 mm de coluna', 'pistão: Ø40 de tubo + câmara 60 × 60 — bem menor'],
          ['Barulho', 'caçambas: baixo', 'pistão: um "toc" por ciclo'],
          ['Peças', 'caçambas: 12 copos, 2 polias, correia fechada', 'pistão: tubo, câmara, 2 linguetas, atuador'],
        ],
        texto: 'Resumo honesto: o pistão é mais compacto e tem menos peças, mas prende 13 bolas no tubo, trava com uma bola ruim e, com atuador barato, não aguenta o ritmo de uma máquina comercial. O elevador de caçambas fica como principal; vale testar a bomba na bancada com um NEMA + manivela se o espaço do canto for problema.' },
    ],
  };
}