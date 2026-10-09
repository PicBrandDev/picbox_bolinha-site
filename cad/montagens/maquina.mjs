/* MODULO 0 — A MAQUINA INTEIRA: todos os modulos nas posicoes reais, dentro do gabinete.

   Cada modulo foi desenhado no referencial dele; aqui cada um ganha o seu "lugar":
     eixo B, boca          -> trilho B a 1175 mm do chao (modelo 3D: yTrilhoB)
     eixo A, soltura,      -> trilho A a 1530 mm, eixo de cabeca para baixo (espelho em z)
       magazine
     elevador              -> ja esta no referencial da maquina
     eletronica            -> prateleira de logica a 430 mm; fonte a 180 mm
   E aqui que a verificacao de interferencia pega problema ENTRE modulos. */
import { caixa } from '../lib/base.mjs';
import { peca, inst, PECAS } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';
import { PROJ } from '../lib/projeto.mjs';
import { moduloEixo } from './eixo.mjs';
import { moduloSoltura } from './soltura.mjs';
import { moduloBoca } from './boca.mjs';
import { moduloMagazine } from './magazine.mjs';
import { moduloElevador } from './elevador.mjs';
import { moduloEletronica } from './eletronica.mjs';

const YB = 1175, YA = 1530;
const L = 450, H = 1700, P = 18, Y_PAINEL = 1050, Y_TESTEIRA = 1550;

/* gabinete (MDF 18): so referencia translucida, as cotas sao as do modelo 3D */
const GAB = {
  gab_piso: [-L / 2 + P, -L / 2 + P, 0, L / 2 - P, L / 2 - P, P],
  gab_lat_e: [-L / 2, -L / 2, 0, -L / 2 + P, L / 2, H],
  gab_lat_d: [L / 2 - P, -L / 2, 0, L / 2, L / 2, H],
  gab_fundo: [-L / 2 + P, L / 2 - P, 0, L / 2 - P, L / 2, H],
  gab_frente: [-L / 2 + P, -L / 2, 0, L / 2 - P, -L / 2 + P, Y_PAINEL],
  gab_testeira: [-L / 2 + P, -L / 2, Y_TESTEIRA + 50, L / 2 - P, -L / 2 + P, H],
  gab_teto: [-L / 2 + P, -L / 2 + P, H - P, L / 2 - P, L / 2 - P, H],
};
Object.entries(GAB).forEach(([id, b]) => peca(id, { nome: 'Gabinete (MDF 18 mm) — ' + id.slice(4), tipo: 'cortar', src: 'est',
  dims: `${(b[3] - b[0]).toFixed(0)} × ${(b[4] - b[1]).toFixed(0)} × ${(b[5] - b[2]).toFixed(0)} mm`,
  notas: ['Gabinete do modelo 3D (450 × 450 × 1700, MDF 18): aparece só como referência. Ainda está em aberto no PROJETO.md.'] },
() => [{ forma: caixa(...b), cor: 'mdf' }]));

function junta(mod, prefixo, quadro, filtro) {
  const ctx = new Set(mod.contexto || []);
  return mod.instancias
    .filter(i => !ctx.has(i.id) && !i.oculta && (!filtro || filtro(i)))
    .map(i => inst(prefixo + i.id, i.peca, i.T.em(quadro), { semColisao: i.semColisao }));
}

export function moduloMaquina() {
  const r = T.of();
  const B = r.t(0, 0, YB), A = r.esp('z').t(0, 0, YA), Ac = r.t(0, 0, YA);
  const eixo = moduloEixo();
  // no eixo A: bloco tensor sem fim de curso e sem o sensor/parafusos da esquerda
  const eixoA = Object.assign({}, eixo, {
    instancias: eixo.instancias.map(i => i.id === 'bloco_tensor' ? Object.assign({}, i, { peca: 'eixo_bloco_tensor_semfc' }) : i)
      .filter(i => !/^fc_t$|^p_fc_t_/.test(i.id) && !/^gab_/.test(i.id) && !/^mad_/.test(i.id)),
  });
  const eixoB = Object.assign({}, eixo, { instancias: eixo.instancias.filter(i => !/^gab_/.test(i.id) && !/^mad_/.test(i.id)) });
  const ele = moduloEletronica();
  const I = [
    ...Object.keys(GAB).map(id => inst(id, id, r, { contexto: true })),
    ...junta(eixoB, 'B.', B),
    ...junta(eixoA, 'A.', A),
    ...junta(moduloBoca(), 'boca.', B),
    ...junta(moduloSoltura(), 'sol.', Ac),
    ...junta(moduloMagazine(), 'mag.', Ac),
    ...junta(moduloElevador(), 'elev.', r),
    ...junta(ele, 'ele.', r.t(0, 20, 430 + 6), i => i.id !== 'fonte' && i.id !== 'botao'),
    inst('ele.fonte', 'fonte_12v', r.t(0, 40, 180)),
    inst('ele.botao', 'botao_arcade', r.rx(90).t(0, -L / 2, Y_PAINEL + 25)),
  ];
  const grupo = pre => I.filter(i => i.id.startsWith(pre)).map(i => i.id);
  return {
    id: 'maquina', nome: 'Máquina completa',
    subtitulo: 'Todos os módulos no lugar, dentro do gabinete. A verificação daqui pega o que um módulo faz no outro.',
    resumo: 'Os 6 módulos nas alturas reais: eixo B a 1175 mm, eixo A a 1530 mm, magazine atrás do A, elevador no canto de trás à direita, eletrônica no pedestal.',
    tempo: 'ordem de montagem sugerida',
    instancias: I,
    contexto: Object.keys(GAB),
    // os dois carros com a carga indo de ponta a ponta, contra a maquina inteira
    varredura: [
      { ids: [...['patim', 'placa', 'garra', 'presilha_0', 'presilha_1'].map(i => 'B.' + i), ...grupo('boca.')],
        desloc: [-140, -100, -50, 50, 100, 140].map(x => [x, 0, 0]), ignora: ['B.trilho', 'B.perfil', 'B.correia'] },
      { ids: [...['patim', 'placa', 'garra', 'presilha_0', 'presilha_1'].map(i => 'A.' + i), ...grupo('sol.')],
        desloc: [-140, -100, -50, 50, 100, 140].map(x => [x, 0, 0]), ignora: ['A.trilho', 'A.perfil', 'A.correia'] },
    ],
    passos: [
      { titulo: 'A máquina inteira', mostra: 'tudo', vista: 'iso',
        texto: 'Todos os módulos desta página, nas posições reais. O gabinete aparece transparente (ele ainda está em aberto no PROJETO.md). Clique em qualquer peça para ver a ficha.' },
      { titulo: '1. Eletrônica no pedestal', novos: grupo('ele.'), vista: 'frente',
        texto: 'Comece por baixo: fonte a 180 mm e placa de eletrônica a 430 mm do chão. Assim a fiação dos módulos de cima já desce até ela.' },
      { titulo: '2. Eixo B e boca', novos: [...grupo('B.'), ...grupo('boca.')], vista: 'frente',
        texto: 'Eixo B com o trilho a 1175 mm do chão (trilho em cima, patim em cima). A boca vai no carro dele.' },
      { titulo: '3. Elevador', novos: grupo('elev.'), vista: 'tras',
        texto: 'A coluna do elevador no canto de trás, à direita. Monte antes do eixo A: depois ele fica difícil de alcançar.' },
      { titulo: '4. Eixo A, berço e magazine', novos: [...grupo('A.'), ...grupo('sol.'), ...grupo('mag.')], vista: 'iso',
        texto: 'Eixo A de cabeça para baixo com o trilho a 1530 mm, berço no carro dele, e o magazine atrás, ligado ao elevador pela calha de entrega.',
        confira: ['Correndo o carro A à mão, o berço passa por cima dos trilhos de carga sem encostar.'] },
    ],
  };
}
