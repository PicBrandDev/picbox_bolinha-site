/* MODULO 3 — BOCA DO BURACO + BARREIRA IR, em cima do carro do eixo B

   Referencial: o do eixo B (trilho centrado em z = 0, placa do carro de z = 9 a 14).
   Plano da boca: z = +45 (recuoInf do modelo: a boca fica 45 mm acima do eixo do trilho).
   Furo: geo.L x geo.depth = 78 x 60 mm, centrado no plano de jogo (y = -57).

   Largura da chapa NAO e livre: com o carro no fim de curso (x = 152) a chapa nao pode
   passar da parede (207). Sobram 13 mm de chapa de cada lado do furo — o modelo 3D
   antigo usava 26 mm e a chapa saia do gabinete.

   Barreira: feixe ao longo de X, no meio da profundidade do furo. Toda bola que passa
   corta o feixe (raio 17,5 > desvio maximo em Y de 12,5). Um feixe ao longo de Y perderia
   as bolas que passam de raspao em X. */
import { caixa, cil, cilC, uniao, FOLGA, R } from '../lib/base.mjs';
import { peca, inst } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';
import { EX } from './eixo.mjs';
import { PROJ } from '../lib/projeto.mjs';

export const BO = { zb: 45, yb: -57, L: PROJ.abertura, P: PROJ.profBoca, sobra: 13, parede: 3, chapa: 4,
  zGarg: 14, zFeixe: 30 };
const IMP = { tipo: 'impresso', src: 'est', material: 'PETG' };

function retArred(w, d, r, h, z0, yc) {
  return R.drawRoundedRectangle(w, d, r).sketchOnPlane('XY', z0).extrude(h).translate(0, yc, 0);
}
function boca() {
  const { zb, yb, L, P, sobra, parede: w, chapa } = BO;
  const xe = L / 2 + w + sobra, y0 = yb - P / 2 - w - sobra, y1 = -14;
  const chapaS = caixa(-xe, y0, zb - chapa, xe, y1, zb);
  const tuboExt = retArred(L + 2 * w, P + 2 * w, 8 + w, zb - BO.zGarg, BO.zGarg, yb);
  const aba = caixa(-22, yb + P / 2 + w - 1, BO.zGarg, 22, -8, BO.zGarg + 4);
  const reforcos = [-1, 1].map(s => caixa(s * 19, yb + P / 2 + w - 1, BO.zGarg + 4, s * 22, y1, zb - chapa));
  const buchas = [-1, 1].map(s => cil(10, 6, [s * (L / 2 + w - 0.5), yb, BO.zFeixe], s > 0 ? 'x' : '-x'));
  let b = uniao([chapaS, tuboExt, aba, ...reforcos, ...buchas]);
  b = b.cut(retArred(L, P, 8, 100, BO.zGarg - 10, yb));                 // o furo atravessa tudo
  [-15, 15].forEach(x => { b = b.cut(cilC(FOLGA.m3, 12, [x, -17, BO.zGarg + 2], 'z')); });
  [-1, 1].forEach(s => { b = b.cut(cilC(5.15, 20, [s * (L / 2 + 6), yb, BO.zFeixe], 'x')); });
  // anel em baixo-relevo em volta do furo: marca a area de acerto
  b = b.cut(retArred(L + 8, P + 8, 12, 1, zb - 0.6, yb).cut(retArred(L + 4, P + 4, 10, 2, zb - 1, yb)));
  return b;
}
peca('boca_alvo', Object.assign({}, IMP, { nome: 'Boca do buraco (chapa-alvo + garganta)', dims: '110 × 89 × 31 mm',
  imprimir: { rot: [['x', 180]] },
  impressao: { preenchimento: '30 %', paredes: 4, suportes: 'só sob a aba de fixação', tempo: '≈ 4 h' },
  notas: ['O furo é 78 × 60 mm (geo.L × geo.depth do simulador).',
    'Imprima com a chapa virada para a mesa: o furo e o anel saem perfeitos e as paredes da garganta sobem retas.',
    'A chapa tem 13 mm de borda de cada lado do furo: no fim de curso ela fica a 3 mm da parede do gabinete.'] }),
() => [{ forma: boca().translate(0, 57, -30), cor: 'impresso' }]);

function instancias() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  const r = T.of();
  add('ctx_perfil', 'perfil2020_400', r.t(0, 0, -14), { contexto: true });
  add('ctx_trilho', 'mgn12_trilho_400', r.t(0, 0, -4), { contexto: true });
  add('ctx_patim', 'mgn12h_patim', r.t(0, 0, -4), { contexto: true });
  add('ctx_placa', 'eixo_placa_carro', r.t(0, 0, 9), { contexto: true });
  // pecas FIXAS do eixo, invisiveis: so para a varredura do carro com a carga ate os extremos
  add('fx_motor', 'eixo_bloco_motor', (r.t(EX.xPe, 0, 0)), { contexto: true, oculta: true });
  add('fx_tensor', 'eixo_bloco_tensor', (r.t(-EX.xPe, 0, 0)), { contexto: true, oculta: true });
  add('fx_fc_m', 'tcst2103', (r.ry(-90).t(EX.xPlacaFC, 0, EX.zFC)), { contexto: true, oculta: true });
  add('fx_fc_t', 'tcst2103', r.ry(90).t(-EX.xPlacaFC, 0, EX.zFC), { contexto: true, oculta: true });
  add('boca', 'boca_alvo', r.t(0, -57, 30));
  [-15, 15].forEach((x, k) => add('p_boca_' + k, 'din912_m3x10', r.t(x, -17, BO.zGarg + 4)));
  const xL = BO.L / 2 + BO.parede + 6.5;     // aba do LED encostada por fora da bucha
  add('emissor', 'ir333c', r.ry(90).t(-xL, BO.yb, BO.zFeixe));
  add('receptor', 'til78', r.ry(-90).t(xL, BO.yb, BO.zFeixe));
  add('bola', 'bola35', r.t(6, BO.yb + 4, BO.zFeixe), { semColisao: true });
  return I;
}

export function moduloBoca() {
  const I = instancias();
  const ids = pre => I.filter(i => i.id.startsWith(pre)).map(i => i.id);
  return {
    id: 'boca', nome: 'Boca e detecção',
    subtitulo: 'Em cima do carro do eixo B. A bola que passa pelo furo corta o feixe infravermelho.',
    resumo: 'Chapa-alvo impressa com o furo de 78 × 60 mm, garganta e barreira IR (LED IR333C de um lado, fototransistor TIL78 do outro).',
    tempo: '≈ 40 min (com as soldas)',
    instancias: I,
    contexto: ids('ctx_').concat(ids('fx_')),
    varredura: [{ ids: ['boca', 'emissor', 'receptor', 'ctx_patim', 'ctx_placa'], desloc: [[EX.curso / 2, 0, 0], [-EX.curso / 2, 0, 0]], ignora: ['ctx_trilho', 'ctx_perfil'] }],
    passos: [
      { titulo: 'Conheça as peças', mostra: 'tudo', explode: 1, vista: 'iso',
        texto: 'A boca é uma peça só: a chapa com o furo, a garganta embaixo dela e a aba que prende no carro do eixo B (em cinza claro). O feixe infravermelho atravessa a garganta de um lado ao outro, no meio da profundidade do furo.' },
      { titulo: 'Fios no LED e no fototransistor', novos: ['emissor', 'receptor'], vista: 'frente', zoom: ['emissor', 'receptor'],
        texto: 'Solde 2 fios de ~60 cm em cada componente e isole com termorretrátil. LED IR333C (transparente-azulado): perna LONGA = + (ânodo). Fototransistor TIL78 (escuro): perna CURTA, do lado do chanfro da aba = coletor. Marque os fios (+/−, C/E) com fita.',
        ferramentas: ['ferro de solda', 'termorretrátil', 'alicate de corte'],
        atencao: ['A luz do LED IR é invisível. Para testar, ligue (5 V com resistor de 150 Ω) e olhe pela câmera do celular: ele aparece roxo.'] },
      { titulo: 'Encaixe nos dois lados da garganta', novos: ['boca'], base: ['emissor', 'receptor'], vista: 'frente',
        texto: 'Encaixe o LED no furo da ESQUERDA e o fototransistor no da DIREITA, por fora, até a aba encostar na bucha. A cúpula fica um pouco para dentro da parede: a bola não bate nela. Uma gota de cola quente por fora segura cada um.',
        ferramentas: ['cola quente'],
        confira: ['Olhando por um furo, você vê o outro alinhado.'] },
      { titulo: 'Boca no carro B', novos: ids('p_boca_'), vista: 'iso',
        texto: 'Apoie a aba da boca sobre a frente da placa do carro do eixo B, em cima das 2 porcas encaixadas. Prenda com 2 parafusos M3×10 de cima para baixo.',
        ferramentas: ['chave allen 2,5 mm'],
        confira: ['A chapa fica na horizontal (nível de bolha).', 'No fim de curso, a borda da chapa fica a uns 3 mm da parede do gabinete.'] },
      { titulo: 'Teste do feixe', novos: ['bola'], vista: 'frente', zoom: ['boca'],
        texto: 'Ligue o LED (5 V + 150 Ω) e o fototransistor no comparador LM393 (módulo Eletrônica). Gire o trimpot até o LED do módulo apagar com o feixe livre e volte 1/4 de volta. Solte uma bola pelo furo: o LED do módulo tem que piscar TODAS as vezes, inclusive passando de raspão nos cantos.',
        ferramentas: ['chave de fenda pequena (trimpot)'],
        confira: ['20 bolas, 20 piscadas.', 'Com a luz da sala acesa e apagada o resultado é o mesmo.'] },
    ],
  };
}
