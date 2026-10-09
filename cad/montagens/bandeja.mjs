/* MODULO — BANDEJA DE CAPTURA + CALHA DE RETORNO (referencial da MAQUINA: z = altura)

   Recebe a bola que passou pelo furo E a que bateu na chapa, e entrega no canto de tras
   a direita, ja andando na direcao do elevador.

   Dois caimentos (do modelo 3D): 4,5 graus para +X leva a bola ate a guia da direita;
   3 graus para tras a leva, encostada nessa guia, ate a saida. Ponto alto: canto da frente
   a esquerda, a 1150 mm (logo abaixo do perfil do eixo B, em 1151).

   A placa (390 x 225) nao cabe na impressora (260 x 260): e MDF 6 mm cortado, apoiado em
   4 calcos impressos sobre a divisoria do gabinete (1100 mm). Os calcos sao todos de
   alturas diferentes — sao eles que dao a inclinacao. As bordas sao impressas em pedacos. */
import { R, caixa, cil, cilC, uniao, FOLGA } from '../lib/base.mjs';
import { peca, inst } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';
import { PROJ } from '../lib/projeto.mjs';
import { EL } from './elevador.mjs';

const RB = PROJ.bolaD / 2;
const kx = Math.tan(4.5 * Math.PI / 180), ky = Math.tan(3 * Math.PI / 180);
export const BJ = {
  x0: -199, x1: 191.5,          // da frente do pe do bloco tensor B ate a guia que alinha com o elevador
  y0: -169.5, y1: 55.5,         // centrada no plano de jogo (y = -57), 225 de profundidade
  zAlto: 1150, e: 6, borda: 26, div: 1100,
  xSai0: EL.x - 21, xSai1: 191.5,
};
// superficie de cima da placa (onde a bola rola)
export const zSup = (x, y) => BJ.zAlto - kx * (x - BJ.x0) - ky * (y - BJ.y0);
const n = [kx, ky, 1].map(v => v / Math.hypot(kx, ky, 1));          // normal da placa
const IMP = { tipo: 'impresso', src: 'est', material: 'PETG' };

/* placa inclinada: caixa no plano XY levada para o plano da superficie (rotacao pelas duas
   inclinacoes, em torno do canto alto) */
function naPlaca(forma) {
  // forma desenhada com o canto alto (x0, y0) na origem e a face de cima em z = 0
  const ax = Math.atan(kx) * 180 / Math.PI, ay = Math.atan(ky) * 180 / Math.PI;
  return forma.rotate(ax, [0, 0, 0], [0, 1, 0]).rotate(-ay, [0, 0, 0], [1, 0, 0]).translate(BJ.x0, BJ.y0, BJ.zAlto);
}
const LX = (BJ.x1 - BJ.x0) / Math.cos(Math.atan(kx)), LY = (BJ.y1 - BJ.y0) / Math.cos(Math.atan(ky));

peca('bandeja_placa', { nome: 'Placa da bandeja (MDF 6 mm)', tipo: 'cortar', src: 'est', dims: `${LX.toFixed(0)} × ${LY.toFixed(0)} × 6 mm`,
  link: 'https://lista.mercadolivre.com.br/mdf-6mm-sob-medida',
  notas: ['Grande demais para a impressora: corte em MDF 6 mm. Passe verniz ou cole feltro fino: a bola cai nela o tempo todo e o MDF cru faz barulho e desgasta.',
    'Os 4 furos dos cantos vão sobre os calços.'] },
() => {
  let p = caixa(0, 0, -BJ.e, LX, LY, 0);
  [[20, 20], [LX - 20, 20], [20, LY - 20], [LX - 20, LY - 20]].forEach(([x, y]) => { p = p.cut(cilC(FOLGA.madeira, 20, [x, y, -3], 'z')); });
  return [{ forma: naPlaca(p), cor: 'mdf' }];
});

/* bordas: perfil L (parede 3 x 26 + aba 10 x 3 apoiada na placa), cortadas em pedacos que cabem na mesa */
function borda(x0, y0, x1, y1, dentro) {
  // segmento reto no referencial da placa; 'dentro' = lado da aba (+1/-1) na direcao perpendicular
  const L = Math.hypot(x1 - x0, y1 - y0), ang = Math.atan2(y1 - y0, x1 - x0) * 180 / Math.PI;
  let b = caixa(0, -1.5, 0, L, 1.5, BJ.borda).fuse(caixa(0, dentro > 0 ? 1.5 : -11.5, 0, L, dentro > 0 ? 11.5 : -1.5, 3));
  for (let x = 20; x < L - 10; x += 80) b = b.cut(cilC(FOLGA.m3, 10, [x, dentro * 7, 1.5], 'z'));
  return naPlaca(b.rotate(ang, [0, 0, 0], [0, 0, 1]).translate(x0, y0, 0));
}
const BORDAS = [
  ['bj_borda_f1', 'Borda da frente (esquerda)', 0, 1.5, LX / 2, 1.5, 1],
  ['bj_borda_f2', 'Borda da frente (direita)', LX / 2, 1.5, LX, 1.5, 1],
  ['bj_borda_t1', 'Borda de trás (esquerda)', 0, LY - 1.5, (BJ.xSai0 - BJ.x0) / 2, LY - 1.5, -1],
  ['bj_borda_t2', 'Borda de trás (até a saída)', (BJ.xSai0 - BJ.x0) / 2, LY - 1.5, BJ.xSai0 - BJ.x0, LY - 1.5, -1],
  ['bj_guia', 'Guia de saída (direita)', LX - 1.5, 13, LX - 1.5, LY, 1],     // girada 90: aba +y local = -x (para dentro)
];
BORDAS.forEach(([id, nome, a, b, c, d, s]) => peca(id, Object.assign({}, IMP, { nome, dims: `${Math.hypot(c - a, d - b).toFixed(0)} × 13 × 26 mm`,
  imprimir: { rot: [] }, impressao: { preenchimento: '20 %', paredes: 3, suportes: 'não', tempo: '≈ 1 h 30' },
  notas: id === 'bj_guia' ? ['A guia da direita é a mais importante: o caimento de 4,5° joga a bola contra ela, e ela leva a bola pelo caimento de 3° até a saída, no canto de trás.']
    : ['Presa na placa por parafusos M3×12 com porca por baixo, a cada 80 mm.'] }),
() => [{ forma: borda(a, b, c, d, s), cor: 'impresso' }]));
// borda da esquerda: rebaixada no meio, onde o perfil do eixo B passa 1 mm acima da placa
peca('bj_borda_e', Object.assign({}, IMP, { nome: 'Borda da esquerda (com rebaixo sob o eixo B)', dims: `${LY.toFixed(0)} × 13 × 26 mm`,
  imprimir: { rot: [] }, impressao: { preenchimento: '20 %', paredes: 3, suportes: 'não', tempo: '≈ 1 h 30' },
  notas: ['No meio ela é rebaixada até a placa: ali o perfil do eixo B passa 1 mm acima — ele mesmo faz de parede, a bola não passa por baixo dele.'] }),
() => {
  let b = borda(1.5, 13, 1.5, LY - 13, -1);           // os cantos ficam com as bordas da frente e de tras
  const yc = -BJ.y0;                                          // y = 0 da maquina no referencial da placa
  // de y = -18 (aba da frente do bloco) a y = +45 (placa do tensor, 40,5): tudo isso do eixo B fica 1 mm acima
  const corte = naPlaca(caixa(-20, yc - 18, 0.3, 20, yc + 45, 40));
  return [{ forma: b.cut(corte), cor: 'impresso' }];
});

/* calcos: base plana na divisoria (1100), topo na face de baixo da placa */
const CANTOS = [[BJ.x0 + 20, BJ.y0 + 20], [BJ.x1 - 20, BJ.y0 + 20], [BJ.x0 + 20, BJ.y1 - 20], [BJ.x1 - 20, BJ.y1 - 20]];
CANTOS.forEach(([x, y], i) => {
  const h = zSup(x, y) - BJ.e - BJ.div;
  peca('bj_calco_' + i, Object.assign({}, IMP, { nome: `Calço da bandeja ${['frente esq.', 'frente dir.', 'trás esq.', 'trás dir.'][i]} (${h.toFixed(1)} mm)`,
    dims: `30 × 30 × ${h.toFixed(1)} mm`, imprimir: { rot: [] },
    impressao: { preenchimento: '40 %', paredes: 4, suportes: 'não', tempo: '≈ 30 min' },
    notas: ['Os 4 calços têm alturas diferentes e o topo inclinado: são eles que dão os dois caimentos da bandeja. Imprima cada um com o seu arquivo e marque o canto.'] }),
  () => {
    let c = caixa(x - 15, y - 15, BJ.div, x + 15, y + 15, BJ.div + h + 15);
    c = c.cut(naPlaca(caixa(-200, -200, -BJ.e, 600, 400, 60)));     // topo = face de baixo da placa
    c = c.cut(cilC(FOLGA.madeira, 200, [x, y, BJ.div], 'z'));
    return [{ forma: c.translate(-x, -y, -BJ.div), cor: 'impresso2' }];
  });
});

/* calha de retorno: saida da bandeja -> aba da concha do elevador */
const zSai = zSup(EL.x, BJ.y1) + RB / n[2];
peca('bj_calha_retorno', Object.assign({}, IMP, { nome: 'Calha de retorno (bandeja → elevador)', dims: '47 × 30 × 32 mm',
  imprimir: { rot: [] }, impressao: { preenchimento: '30 %', paredes: 3, suportes: 'não', tempo: '40 min' },
  notas: ['Trecho curto de propósito: a bola já sai da bandeja andando para trás (−Y), na linha da concha. Nada de curva fechada nem queda livre.'] }),
() => {
  const w = 18.8, ya = BJ.y1, yb = 64.8, za = zSai - RB, zb = 1123.2 - RB;   // termina rente na aba da concha
  const piso = R.draw([ya, za]).lineTo([yb, zb]).lineTo([yb, zb - 3]).lineTo([ya, za - 3]).close();
  let c = piso.sketchOnPlane('YZ').extrude(2 * w + 5).translate(EL.x - w - 2.5, 0, 0);
  [-1, 1].forEach(s => { c = c.fuse(caixa(EL.x + s * (w + 1.25) - 1.25, ya, zb - 3, EL.x + s * (w + 1.25) + 1.25, yb, za + 22)); });
  return [{ forma: c.translate(-EL.x, -BJ.y1, -zSai), cor: 'impresso' }];
});

/* ---------------------------------------------------------------- instancias */
export function instanciasBandeja() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  const r = T.of();
  add('placa', 'bandeja_placa', r);
  CANTOS.forEach(([x, y], i) => {
    add('calco_' + i, 'bj_calco_' + i, r.t(x, y, BJ.div));
    add('mad_calco_' + i, 'madeira_3_5x16', r.t(x, y, zSup(x, y)));
  });
  ['bj_borda_f1', 'bj_borda_f2', 'bj_borda_t1', 'bj_borda_t2', 'bj_guia', 'bj_borda_e'].forEach(id => add(id.replace('bj_', ''), id, r));
  add('calha', 'bj_calha_retorno', r.t(EL.x, BJ.y1, zSai));
  return I;
}

export function moduloBandeja() {
  const I = instanciasBandeja();
  const r = T.of();
  // contexto: eixo B por cima (perfil, blocos) e a concha do elevador, para ver as folgas
  I.push(inst('ctx_perfilB', 'perfil2020_400', r.t(0, 0, 1175 - 14), { contexto: true }));
  I.push(inst('ctx_tensorB', 'eixo_bloco_tensor', r.t(-200, 0, 1175), { contexto: true }));
  I.push(inst('ctx_motorB', 'eixo_bloco_motor', r.t(200, 0, 1175), { contexto: true }));
  I.push(inst('ctx_concha', 'elev_concha', r.t(EL.x, EL.y, EL.zb), { contexto: true }));
  I.push(inst('ctx_lat_e', 'elev_lateral', r.t(EL.xPe, 0, 0), { contexto: true }));
  I.push(inst('bola_a', 'bola35', r.t(-60, -80, zSup(-60, -80) + RB / n[2]), { semColisao: true }));
  I.push(inst('bola_b', 'bola35', r.t(EL.x, 20, zSup(EL.x, 20) + RB / n[2]), { semColisao: true }));
  const ids = pre => I.filter(i => i.id.startsWith(pre)).map(i => i.id);
  return {
    id: 'bandeja', nome: 'Bandeja e retorno',
    subtitulo: 'Logo abaixo do eixo B. Junta toda bola que cai e entrega no pé do elevador.',
    resumo: 'Placa de MDF com dois caimentos sobre 4 calços impressos, bordas impressas em partes e a calha curta até a concha do elevador.',
    tempo: '≈ 1 h',
    instancias: I,
    contexto: ids('ctx_'),
    passos: [
      { titulo: 'Conheça as peças', mostra: 'tudo', explode: 0.4, vista: 'iso',
        texto: 'A bandeja fica sobre a divisória do gabinete (1100 mm), logo abaixo do eixo B (em cinza claro). Ela cai em DUAS direções: para a direita e para trás. Qualquer bola que cair nela — acerto ou erro — rola até a guia da direita e desce encostada nela até o canto de trás, onde está a calha de retorno.',
        porques: [
          { alvo: 'guia', titulo: 'Por que dois caimentos', resumo: 'A bola sai da bandeja já andando na direção do elevador.',
            texto: 'Com um caimento só (para a direita), a bola chegaria no canto e teria que fazer uma curva fechada para ir para trás, até o elevador — e ali ela pararia ou bateria. Com o segundo caimento (3° para trás), ela desce encostada na guia da direita e sai do canto JÁ andando para trás, na linha da concha. Por isso a calha de retorno é um trechinho reto de 12 mm.' },
          { alvo: 'borda_e', titulo: 'Por que a borda da esquerda tem um rebaixo', resumo: 'Ali o eixo B passa 1 mm acima da placa.',
            texto: 'O ponto mais alto da bandeja (1150 mm) fica 1 mm abaixo do perfil do eixo B (1151). Uma borda de 26 mm bateria no perfil e no bloco tensor. Nesse trecho ela é rebaixada: o próprio eixo B faz de parede — 1 mm de fresta, a bola não passa.' },
          { alvo: 'calco_0', titulo: 'Por que calços de alturas diferentes', resumo: 'São eles que inclinam a placa.',
            texto: 'A placa é plana; a divisória embaixo é plana e horizontal. Os 4 calços têm alturas diferentes e o topo já inclinado — a placa apoiada neles fica exatamente nos dois caimentos. Cada calço tem o seu arquivo: não troque de canto.' },
        ] },
      { titulo: 'Calços na divisória', novos: ids('calco_'), vista: 'iso',
        texto: 'Marque os 4 cantos na divisória (20 mm para dentro da placa) e parafuse cada calço no seu canto com um parafuso de madeira por dentro do furo central. Confira pela altura gravada no nome: o mais alto vai na frente à esquerda.',
        ferramentas: ['chave Phillips nº 2', 'esquadro'] },
      { titulo: 'Placa', novos: ['placa', ...ids('mad_calco_')], vista: 'iso',
        texto: 'Apoie a placa de MDF sobre os calços e parafuse nos 4 cantos (3,5×16, cabeça escareada rente: a bola não pode bater numa cabeça de parafuso).',
        ferramentas: ['chave Phillips nº 2', 'escareador'],
        confira: ['Uma bola solta em qualquer ponto rola até a guia da direita e desce até o canto de trás.'] },
      { titulo: 'Bordas', novos: ['borda_f1', 'borda_f2', 'borda_t1', 'borda_t2', 'guia', 'borda_e'], vista: 'iso',
        texto: 'Parafuse as bordas em volta (M3×12 com porca por baixo da placa). Na de trás fica a abertura da saída, no canto da direita.',
        ferramentas: ['chave allen 2,5 mm', 'furadeira 3,5 mm'] },
      { titulo: 'Calha de retorno', novos: ['calha', 'bola_a', 'bola_b'], vista: 'tras', zoom: ['calha', 'ctx_concha'],
        texto: 'A calha liga a saída da bandeja à aba da concha do elevador (desce 3,4 mm em 12 mm). Encoste e cole com cola quente ou 1 parafuso na placa.',
        confira: ['10 bolas soltas em lugares diferentes: todas chegam na concha sem parar no caminho.'] },
    ],
  };
}
