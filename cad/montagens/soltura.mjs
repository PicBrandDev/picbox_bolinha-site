/* MODULO 2 — SOLTURA (berco de pinca + solenoide), pendurado no carro do eixo A

   Referencial: o do eixo A JA INSTALADO (o eixo B espelhado em z): trilho centrado em
   z = 0, patim e placa do carro EMBAIXO (placa de z = -14 a -9). Centro da bola no
   instante da soltura: (0, -57, -60) — 60 mm abaixo do eixo do trilho (recuoSup do
   modelo) e no plano de jogo, 57 mm a frente dos trilhos (zJogo do modelo).

   Por que PINCA e nao pino por baixo: com 10 mm de curso, um pino sob uma bola de 35 mm
   continua no caminho dela quando ela cai (precisaria de ~22 mm). A pinca segura a bola
   na altura do equador: a mola do solenoide empurra o embolo contra a bola e a bola contra
   um V fixo. Energizado, o embolo recua; a bola fica sem nada embaixo e cai reta, sem
   empurrao no eixo X (o eixo do jogo). O V centra a bola em X sozinho. */
import { caixa, cil, cilC, uniao, extrudaPoli, FOLGA } from '../lib/base.mjs';
import { peca, inst } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';
import { EX, posFC } from './eixo.mjs';
import { PROJ } from '../lib/projeto.mjs';
import { SOL } from '../pecas/comprados.mjs';

const RB = PROJ.bolaD / 2;
export const SO = { yb: -57, zb: -60, ySol: -2, larg: 21, zBraco: -41, yFrente: -84 };
const s = SOL.jf0826;
const IMP = { tipo: 'impresso', src: 'est', material: 'PETG' };

// berco: perfil no plano YZ extrudado em X — imprime DE LADO, sem suporte
function berco() {
  const L = SO.larg, ztop = SO.zb + s.A / 2;                   // topo do solenoide: -47,5
  const blocos = [
    caixa(-L, -29, -18, L, -8, -14),                            // aba presa na placa do carro
    caixa(-L, -12, ztop + 4, L, -8, -18),                       // alma
    caixa(-L, -36, ztop, L, -8, ztop + 4),                      // mesa do solenoide
    caixa(-L, -36, ztop, L, -32, SO.zBraco + 4),                // degrau ate o braco
    caixa(-L, SO.yFrente, SO.zBraco, L, -32, SO.zBraco + 4),    // braco por cima da bola
    caixa(-L, SO.yFrente, SO.zb - 12, L, -72, SO.zBraco),       // perna da frente (o V)
  ];
  let b = uniao(blocos);
  // V de 90 graus: vertice a RB*sqrt(2) do centro da bola, encosta no equador
  const yv = SO.yb - RB * Math.SQRT2;
  const v = extrudaPoli([[0, yv], [40, yv + 40], [-40, yv + 40]], 60, SO.zb - 20);
  b = b.cut(v);
  // aba: 2 furos M3 (sobem para as porcas da placa do carro)
  [-15, 15].forEach(x => {
    b = b.cut(cilC(FOLGA.m3, 10, [x, -17, -16], 'z'));
    b = b.cut(cilC(6.5, 8, [x, -17, ztop + 2], 'z'));          // passagem da chave allen
  });
  // rasgos dos 2 parafusos da carcaca (posicao do furo varia entre lotes: +-2 mm)
  s.furos.forEach(zl => {
    const y = SO.ySol - zl;
    b = b.cut(caixa(-FOLGA.m3 / 2, y - 2 - FOLGA.m3 / 2, ztop - 1, FOLGA.m3 / 2, y + 2 + FOLGA.m3 / 2, ztop + 5));
  });
  // furo-guia do batente
  b = b.cut(cilC(FOLGA.m3, 10, [19.75, -57, SO.zBraco + 2], 'z'));
  return b.fillet(1, e => e.inDirection('X'));
}
function batente() {
  // a bola chega rolando por -X e para encostada aqui, com o centro em x = 0
  let t = caixa(RB + 0.25, -66, SO.zb - 3, RB + 4.25, -48, SO.zBraco);
  return t.cut(cilC(2.8, 12, [19.75, -57, SO.zBraco - 4], 'z'));
}
peca('soltura_berco', Object.assign({}, IMP, { nome: 'Berço da bola (pinça)', dims: '42 × 76 × 34 mm',
  ref: [0, -40, -40], imprimir: { rot: [['y', 90]] },
  impressao: { preenchimento: '40 %', paredes: 4, suportes: 'não (imprime de lado)', tempo: '≈ 2 h 30' },
  notas: ['O V da frente centra a bola sozinho; o êmbolo do solenoide empurra a bola contra ele.',
    'Imprima DE LADO (face lateral na mesa): o perfil inteiro fica sem balanço.'] }),
() => [{ forma: berco().translate(0, 40, 40), cor: 'impresso' }]);
peca('soltura_batente', Object.assign({}, IMP, { nome: 'Batente do berço', dims: '4 × 18 × 22 mm', cor: 'impresso2',
  ref: [19.75, -57, -50], imprimir: { rot: [['y', 90]] },
  impressao: { preenchimento: '100 %', paredes: 4, suportes: 'não', tempo: '10 min' },
  notas: ['A bola entra rolando pelo lado aberto (−X, lado da estação de carga) e para aqui com o centro exatamente sob o eixo do berço.'] }),
() => [{ forma: batente().translate(-19.75, 57, 50), cor: 'impresso2' }]);

/* ---------------------------------------------------------------- instancias */
function instancias() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  const r = T.of();
  // contexto: o carro do eixo A (espelhado)
  const A = t => t.esp('z');
  add('ctx_perfil', 'perfil2020_400', A(r.t(0, 0, -14)), { contexto: true });
  add('ctx_trilho', 'mgn12_trilho_400', A(r.t(0, 0, -4)), { contexto: true });
  add('ctx_patim', 'mgn12h_patim', A(r.t(0, 0, -4)), { contexto: true });
  add('ctx_placa', 'eixo_placa_carro', A(r.t(0, 0, 9)), { contexto: true });
  // pecas FIXAS do eixo, invisiveis: so para a varredura do carro com a carga ate os extremos
  add('fx_motor', 'eixo_bloco_motor', A(r.t(EX.xPe, 0, 0)), { contexto: true, oculta: true });
  add('fx_tensor', 'eixo_bloco_tensor_semfc', A(r.t(-EX.xPe, 0, 0)), { contexto: true, oculta: true });
  add('fx_fc_m', 'fc_mecanico', A(posFC(1)), { contexto: true, oculta: true });
  // solenoide: embolo apontando para a bola (-y), furos para cima
  add('solenoide', 'sol_jf0826', r.rx(90).t(0, SO.ySol, SO.zb));
  add('berco', 'soltura_berco', r.t(0, -40, -40));
  s.furos.forEach((zl, k) => add('p_sol_' + k, 'din912_m3x6', r.t(0, SO.ySol - zl, SO.zb + s.A / 2 + 4)));
  add('batente', 'soltura_batente', r.t(19.75, -57, -50));
  add('p_batente', 'din912_m3x10', r.t(19.75, -57, SO.zBraco + 4));
  [-15, 15].forEach((x, k) => add('p_berco_' + k, 'din912_m3x10', r.rx(180).t(x, -17, -18)));
  add('bola', 'bola35', r.t(0, SO.yb, SO.zb), { semColisao: true });
  return I;
}

export function moduloSoltura() {
  const I = instancias();
  const ids = pre => I.filter(i => i.id.startsWith(pre)).map(i => i.id);
  return {
    id: 'soltura', nome: 'Soltura (berço)',
    subtitulo: 'Pendurado no carro do eixo A. Segura a bola pelo equador e solta reto.',
    resumo: 'Berço de pinça impresso + solenoide JF-0826B: a mola do solenoide prende a bola contra um V; energizado, o êmbolo recua e a bola cai sem empurrão lateral.',
    tempo: '≈ 30 min',
    instancias: I,
    contexto: ids('ctx_').concat(ids('fx_')),
    varredura: [{ ids: ['berco', 'solenoide', 'batente', 'bola', 'ctx_patim', 'ctx_placa'], desloc: [[EX.curso / 2, 0, 0], [-EX.curso / 2, 0, 0]], ignora: ['ctx_trilho', 'ctx_perfil'] }],
    passos: [
      { titulo: 'Conheça as peças', mostra: 'tudo', explode: 1, vista: 'iso',
        texto: 'O berço fica pendurado embaixo da placa do carro do eixo A (o eixo de cima, montado de cabeça para baixo — em cinza claro, só como referência). A bola é presa pela lateral: atrás pelo êmbolo do solenoide, na frente por um V fixo.',
        atencao: ['Isto é diferente do "pino por baixo" do modelo 3D antigo: com 10 mm de curso, um pino sob a bola de 35 mm continua no caminho dela quando ela cai.'] },
      { titulo: 'Teste o solenoide antes', novos: ['solenoide'], vista: 'direita',
        texto: 'Antes de montar: ligue o solenoide em 12 V por 1 segundo (fonte da máquina, com o diodo 1N4007 em paralelo). A ponta GROSSA do êmbolo tem que RECOLHER. Desligado, a mola empurra essa ponta para fora uns 10 mm. É ela que vai encostar na bola.',
        atencao: ['Nunca deixe ligado mais que ~1 s: em 12 V ele puxa ~2 A e esquenta rápido.'],
        confira: ['Desligado: ponta para fora. Ligado: ponta para dentro.', 'Anote o curso medido (o desenho assume 10 mm).'] },
      { titulo: 'Solenoide no berço', novos: ['berco', ...ids('p_sol_')], vista: 'cima',
        texto: 'Encaixe o solenoide embaixo da mesa do berço, ponta grossa virada para a frente (para o V). Passe 2 parafusos M3×6 pelos rasgos da mesa até a rosca da carcaça. Antes de apertar, deslize o solenoide pelos rasgos até a ponta do êmbolo (solto, para fora) ficar 0,5 mm DENTRO de onde a bola vai estar: coloque uma bola no V e empurre o solenoide até a bola ficar presa com leve pressão.',
        ferramentas: ['chave allen 2,5 mm'],
        confira: ['Com o solenoide desligado, a bola fica presa e não cai mesmo virando o berço de cabeça para baixo.'] },
      { titulo: 'Batente', novos: ['batente', 'p_batente'], vista: 'esquerda',
        texto: 'Prenda o batente embaixo do braço com 1 parafuso M3×10 por cima (rosqueia no plástico). Ele fica do lado direito (+X): a bola chega rolando pela esquerda, vinda da estação de carga, e para encostada nele.',
        ferramentas: ['chave allen 2,5 mm'] },
      { titulo: 'Berço no carro A', novos: [...ids('p_berco_')], base: ['berco', 'solenoide', 'batente'], vista: 'baixo',
        texto: 'Encoste a aba do berço embaixo da placa do carro do eixo A, na frente (onde ficam as 2 porcas M3 encaixadas por cima). Passe 2 parafusos M3×10 por baixo — a chave entra pelos furos grandes da mesa do solenoide.',
        ferramentas: ['chave allen 2,5 mm'],
        confira: ['O berço fica alinhado com o carro (não torto).', 'Correndo o carro à mão, o berço não encosta em nada até os fins de curso.'] },
      { titulo: 'Teste de soltura', novos: ['bola'], vista: 'esquerda', zoom: ['bola', 'berco'],
        texto: 'Com o solenoide ENERGIZADO, encoste a bola no batente (ela entra pela esquerda) e desligue: a bola fica presa. Ligue por 50 ms: a bola cai reta. Repita 20 vezes sobre uma folha marcada 250 mm abaixo — o espalhamento das marcas é a dispersão da soltura (PROJETO.md, Fase 2).',
        confira: ['A bola nunca fica presa no êmbolo nem "pula" para o lado.', 'As 20 marcas cabem num círculo de poucos milímetros.'] },
    ],
  };
}
