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
