/* MODULO — GABINETE (referencial da MAQUINA: z = altura, frente = -Y)

   Envelope do PROJETO.md: 450 x 450 x 1700, MDF 18 mm. Por dentro sobram 414 mm — e por
   essa medida que os eixos foram desenhados.

   Ordem pensada para quem monta: caixa (piso, laterais, fundo) -> prateleiras e divisoria
   -> TODOS os modulos de dentro -> frente (porta do pedestal, painel do botao, frente
   transparente, testeira) -> teto. O fundo vai PARAFUSADO (nao colado): e a porta de
   manutencao do campo de jogo. */
import { caixa, cilC } from '../lib/base.mjs';
import { peca, inst } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';
import { PROJ } from '../lib/projeto.mjs';
import { EL } from './elevador.mjs';

const L = PROJ.lado, H = 1700, P = 18, I2 = L / 2 - P;          // 207: face de dentro
export const GB = { L, H, P, painel: 1050, campo: 1100, testeira: 1550, div: 1082, fonte: 162, logica: 412 };

// cada painel: [id, nome, caixa (x0,y0,z0,x1,y1,z1), notas, furos/recortes?]
const PAINEIS = [
  ['gab_piso', 'Piso', [-I2, -I2, 0, I2, I2, P], 'Entre as laterais. Pés de borracha embaixo, nos 4 cantos.'],
  ['gab_lat_e', 'Lateral esquerda', [-L / 2, -L / 2, 0, -I2, L / 2, H], 'Altura inteira. Os pés dos eixos A e B, a orelha da calha de carga e o painel do magazine são parafusados nela por dentro.'],
  ['gab_lat_d', 'Lateral direita', [I2, -L / 2, 0, L / 2, L / 2, H], 'Altura inteira. Pés dos eixos e coluna do elevador por dentro.'],
  ['gab_fundo', 'Fundo (porta de manutenção)', [-I2, I2, P, I2, L / 2, H - P], 'PARAFUSADO, não colado: tirando 10 parafusos, você alcança o campo de jogo por trás. Os espaçadores do magazine e as cantoneiras do elevador vão nele.'],
  ['gab_teto', 'Teto', [-I2, -I2, H - P, I2, I2, H], 'Por último, depois de tudo testado.'],
  ['gab_prat_fonte', 'Prateleira da fonte', [-I2, -I2, GB.fonte, I2, 150, GB.fonte + P], 'Fica 57 mm antes do fundo: passagem dos cabos.'],
  ['gab_prat_logica', 'Prateleira da eletrônica', [-I2, -I2, GB.logica, I2, 150, GB.logica + P], 'A placa de eletrônica vai em cima, a 430 mm do chão.'],
  ['gab_porta', 'Porta do pedestal', [-I2 + 1, -L / 2, P + 1, I2 - 1, -I2, GB.painel - 1], 'Com 2 dobradiças e fechadura: a eletrônica e o caixa (se houver) ficam aqui. 1 mm de folga em volta.'],
  ['gab_painel', 'Painel do botão', [-I2, -L / 2, GB.painel, I2, -I2, GB.campo], 'Furo de 25 mm (botão M24) no centro, a 15 mm da borda de baixo: mais alto, a porca do botão (Ø33) bate na divisória do campo.'],
  ['gab_testeira', 'Testeira', [-I2, -L / 2, GB.testeira, I2, -I2, H - P], 'Fecha a frente acima do campo. Espaço para a fita de LED / marca.'],
];
function divisoria() {
  // fecha o campo por baixo; recorte no canto de tras a direita, por onde passa a coluna do elevador,
  // e um furo para os cabos subirem
  let d = caixa(-I2, -I2, GB.div, I2, I2, GB.campo);
  d = d.cut(caixa(EL.xPe - 3, EL.y - 60, GB.div - 1, I2 + 1, I2 + 1, GB.campo + 1));
  d = d.cut(cilC(40, 40, [-170, 170, GB.div + 9], 'z'));
  return d;
}
PAINEIS.forEach(([id, nome, b, nota]) => peca(id, { nome: `Gabinete — ${nome} (MDF 18)`, tipo: 'comprado', src: 'est',
  dims: [b[3] - b[0], b[4] - b[1], b[5] - b[2]].map(v => v.toFixed(0)).sort((a, c) => c - a).join(' × ') + ' mm',
  link: 'https://lista.mercadolivre.com.br/mdf-18mm-sob-medida', notas: [nota] },
() => {
  let f = caixa(...b);
  if (id === 'gab_painel') f = f.cut(cilC(25, 60, [0, -L / 2 + 9, GB.painel + 15], 'y'));   // baixo: a microchave nao pode bater na divisoria (1082)
  return [{ forma: f, cor: 'mdf' }];
}));
peca('gab_divisoria', { nome: 'Gabinete — Divisória do campo (MDF 18)', tipo: 'comprado', src: 'est', dims: '414 × 414 × 18 mm (com recorte)',
  link: 'https://lista.mercadolivre.com.br/mdf-18mm-sob-medida',
  notas: ['Fecha o campo de jogo por baixo e apoia a bandeja (calços). Recorte de ' + (I2 - EL.xPe + 3).toFixed(0) + ' × ' + (I2 - EL.y + 60).toFixed(0) + ' mm no canto de trás à direita para a coluna do elevador; furo de 40 mm atrás à esquerda para os cabos.'] },
() => [{ forma: divisoria(), cor: 'mdf' }]);
peca('gab_frente', { nome: 'Frente do campo (acrílico/vidro — já têm)', tipo: 'comprado', src: 'est', dims: '412 × 448 × 4 mm',
  link: 'https://lista.mercadolivre.com.br/policarbonato-compacto-4mm',
  notas: ['Vocês já têm. Se for vidro, que seja temperado; se for acrílico, 4 mm ou mais (em local público, policarbonato é o mais seguro: não estilhaça).',
    'Encaixa num rebaixo de 5 mm nas laterais, preso por 4 presilhas impressas: sai para manutenção.'] },
() => [{ forma: caixa(-I2 + 1, -L / 2 + 8, GB.campo + 1, I2 - 1, -L / 2 + 12, GB.testeira - 1), cor: 'acrilico' }]);
peca('gab_dobradica', { nome: 'Dobradiça 3" (porta do pedestal)', tipo: 'comprado', src: 'cat', dims: '76 × 38 mm',
  link: 'https://lista.mercadolivre.com.br/dobradica-3-polegadas', notas: ['2 unidades.'] },
() => [{ forma: caixa(-1, -19, -38, 1, 19, 38), cor: 'zincado' }]);
peca('gab_fechadura', { nome: 'Fechadura de gaveta (porta do pedestal)', tipo: 'comprado', src: 'cat', dims: 'Ø19 × 22 mm',
  link: 'https://lista.mercadolivre.com.br/fechadura-gaveta-cilindro', notas: ['Máquina com prêmio: a eletrônica e o dinheiro ficam trancados.'] },
() => [{ forma: cilC(19, 22, [0, 0, 0], 'y'), cor: 'latao' }]);

export function instanciasGabinete() {
  const r = T.of();
  const I = PAINEIS.map(([id]) => inst(id.replace('gab_', 'g_'), id, r));
  I.push(inst('g_divisoria', 'gab_divisoria', r));
  I.push(inst('g_frente', 'gab_frente', r));
  [300, 800].forEach((z, i) => I.push(inst('g_dob_' + i, 'gab_dobradica', r.t(-I2 + 1, -L / 2 + 1, z), { semColisao: true })));
  I.push(inst('g_fechadura', 'gab_fechadura', r.t(I2 - 40, -L / 2 + 9, 900), { semColisao: true }));
  return I;
}

/* plano de corte: tabela que aparece no passo */
const PLANO = PAINEIS.concat([['gab_divisoria', 'Divisória do campo', [-I2, -I2, 0, I2, I2, P]]]).map(([id, nome, b]) => {
  const d = [b[3] - b[0], b[4] - b[1], b[5] - b[2]].map(v => +v.toFixed(0)).sort((a, c) => c - a);
  return [nome, `${d[0]} × ${d[1]}`, id === 'gab_divisoria' ? 'recorte do elevador + furo de cabos' : ''];
});

export function moduloGabinete() {
  const I = instanciasGabinete();
  const ids = pre => I.filter(i => i.id.startsWith(pre)).map(i => i.id);
  return {
    id: 'gabinete', nome: 'Gabinete',
    subtitulo: 'Vocês já têm o gabinete: use esta aba para CONFERIR as medidas que o projeto assume (450 × 450 × 1700, MDF 18, 414 mm por dentro).',
    resumo: 'Plano de corte do MDF, ordem de montagem da caixa, prateleiras, divisória do campo, porta do pedestal, painel do botão e frente de policarbonato.',
    tempo: '≈ 1 dia (marcenaria) + acabamento',
    instancias: I,
    passos: [
      { titulo: 'Conheça as peças', mostra: 'tudo', explode: 0.25, vista: 'iso',
        texto: 'Uma torre de MDF 18 mm. O campo de jogo fica entre 1100 e 1550 mm, atrás de uma frente transparente; embaixo, o pedestal com a eletrônica, atrás de uma porta com chave.' },
      { titulo: 'Medidas que o projeto assume', mostra: 'tudo', vista: 'iso', tabela: PLANO, tabelaTitulo: 'Medidas do projeto (confira no seu gabinete)', tabelaCab: ['peça', 'medida (mm)', 'obs.'],
        texto: 'O gabinete de vocês já existe. Meça e compare com esta tabela — principalmente a <b>largura por dentro (414 mm)</b>, que é o comprimento dos eixos, e as alturas da divisória (1082–1100), do painel do botão (1050–1100) e da testeira (1550). Se alguma medida for diferente, passe para o projeto: as alturas e o comprimento dos eixos são parâmetros e o modelo se ajusta.',
        atencao: ['Confira 414 mm entre as laterais por dentro, em cima e embaixo, ANTES de parafusar o resto. 1 mm a mais e os pés dos eixos ficam soltos; 1 mm a menos e não entram.'] },
      { titulo: 'Caixa: piso, laterais e fundo', novos: ['g_piso', 'g_lat_e', 'g_lat_d', 'g_fundo'], vista: 'iso',
        texto: 'Piso entre as laterais, com cola + parafusos para MDF 4,0×45 (furo-guia de 3 mm, 4 por junta). O fundo vai só parafusado (sem cola): ele é a porta de manutenção do campo.',
        ferramentas: ['parafusadeira', 'broca 3 mm', 'esquadro', 'cola de madeira'],
        confira: ['Diagonais iguais (a caixa está no esquadro).'] },
      { titulo: 'Prateleiras e divisória', novos: ['g_prat_fonte', 'g_prat_logica', 'g_divisoria'], vista: 'iso',
        texto: 'Prateleira da fonte a 162 mm, da eletrônica a 412 mm, divisória do campo a 1082 mm (face de cima em 1100). As prateleiras param 57 mm antes do fundo: é por ali que os cabos sobem. A divisória tem o recorte da coluna do elevador e um furo de 40 mm para os cabos.',
        ferramentas: ['parafusadeira', 'nível de bolha'],
        confira: ['Divisória no nível nas duas direções: a bandeja apoia nela.'] },
      { titulo: 'Agora monte os módulos de dentro', vista: 'iso',
        texto: 'Com a caixa aberta na frente e em cima, instale na ordem da aba "Máquina completa": eletrônica, eixo B, bandeja, elevador, eixo A, berço e magazine. Só depois feche a frente.' },
      { titulo: 'Porta do pedestal e painel do botão', novos: ['g_porta', ...ids('g_dob_'), 'g_fechadura', 'g_painel'], vista: 'frente',
        texto: 'Porta com 2 dobradiças à esquerda e fechadura à direita. Painel do botão fixo, com o furo de 25 mm no centro.',
        ferramentas: ['serra-copo 25 mm', 'broca 19 mm (fechadura)'] },
      { titulo: 'Frente transparente, testeira e teto', novos: ['g_frente', 'g_testeira', 'g_teto'], vista: 'frente',
        texto: 'A frente de policarbonato 4 mm entra num rebaixo de 5 mm nas laterais e é presa por presilhas: sai sem desmontar nada. Testeira e teto por último, depois de testar a máquina inteira.',
        atencao: ['Policarbonato, não vidro nem acrílico: em local público alguém vai dar um soco. Ele não estilhaça.'] },
    ],
  };
}
