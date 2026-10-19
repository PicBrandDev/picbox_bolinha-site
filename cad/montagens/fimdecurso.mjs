/* COMO FUNCIONA — FIM DE CURSO MECANICO (didatico, referencial do eixo B, ponta do motor)

   Em jogo o carro vai ate 140 e para com o batente 1 mm antes da alavanca. Na referencia o
   firmware encosta devagar: 141 toca, 143 clica, para, recua. A alavanca gira na dobra. */
import { inst } from '../lib/registro.mjs';
import { T } from '../lib/mat.mjs';
import { EX, posFC } from './eixo.mjs';
import { SW } from '../pecas/eletronicos.mjs';

const r = T.of();
const DUR = 14;
const ss = u => u * u * (3 - 2 * u);
// [t, x do carro]
const XC = [[0, 60], [1.2, 140], [2.0, 140], [3.0, 60], [4.2, 140], [5.0, 140], [5.6, 134], [8.0, EX.xLivre], [8.7, EX.xHome],
  [10.6, EX.xHome], [11.6, 136], [14, 60]];
const xc = t => {
  for (let i = 1; i < XC.length; i++) if (t <= XC[i][0] + 1e-9) {
    const [t0, a] = XC[i - 1], [t1, b] = XC[i];
    // aproximacao lenta da referencia: velocidade constante (e assim que o firmware faz)
    const u = (t - t0) / (t1 - t0);
    return a + (b - a) * (i === 7 || i === 8 ? u : ss(u));
  }
  return XC[XC.length - 1][1];
};
// alavanca: compressao d na ponta -> giro na dobra
const giro = x => Math.max(0, x - EX.xLivre) / SW.alav * 180 / Math.PI;
const alav = g => T.of().t(-SW.dobra[0], 0, -SW.dobra[1]).ry(g).t(SW.dobra[0], 0, SW.dobra[1]).em(posFC(1));

function trilhas() {
  const ts = [];
  for (let t = 0; t <= DUR + 1e-9; t += 0.1) ts.push(+t.toFixed(2));
  XC.forEach(([t]) => ts.includes(t) || ts.push(t));
  ts.sort((a, b) => a - b);
  return [
    { id: 'patim', k: ts.map(t => [t, r.t(xc(t), 0, EX.zTrilho)]) },
    { id: 'placa', k: ts.map(t => [t, r.t(xc(t), 0, EX.zPatim)]) },
    { id: 'fc_alav', k: ts.map(t => [t, alav(giro(xc(t)))]) },
  ];
}
const LEG = [
  [0, 2.0, '1 · EM JOGO: o carro vai até a ponta do curso (140 mm do centro) e para. O batente fica 1 mm antes da alavanca — não encosta.'],
  [2.0, 5.0, '2 · Vai e volta em velocidade de jogo. A chave nunca é tocada assim: ela só aguenta ~1 mm depois do clique.'],
  [5.0, 8.0, '3 · REFERÊNCIA (ao ligar e uma vez por partida): o firmware leva o carro devagar, em velocidade constante, até encostar na alavanca (141 mm).'],
  [8.0, 8.7, '4 · O batente empurra a PONTA da alavanca. Com 2 mm de curso, a microchave clica (143 mm): a saída S muda de nível e o LED da placa acende.'],
  [8.7, 10.6, '5 · No clique o firmware para o motor na hora e confere: o número de passos contado até ali bate com 143 mm? Se não bater, perdeu passo — corrige e anota no log.'],
  [10.6, 14, '6 · Recua alguns milímetros (a alavanca volta sozinha, é uma mola) e retoma o jogo.'],
];
const PQ = [
  { alvo: 'fc_alav', em: [0, -20, -6], titulo: 'Por que a chave fica FORA do curso de jogo',
    resumo: 'Depois do clique a alavanca só anda ~1,2 mm até bater no corpo da chave.',
    texto: 'Uma microchave clica com ~2 mm de curso na ponta da alavanca e só aguenta mais ~1,2 mm depois disso. Em velocidade de jogo o carro precisa de vários milímetros para frear: passaria do limite e entortaria a alavanca na primeira jogada. Por isso, em jogo, o carro para em 140 mm, com o batente a 1 mm da alavanca, e a chave só é tocada devagar, em velocidade constante, na referência. (O sensor óptico antigo podia ficar dentro do curso porque nada encostava nele.)' },
  { alvo: 'placa', em: [EX.batente - 4, -10, 2], titulo: 'Por que o batente é baixo',
    resumo: 'Ele só alcança a ponta da alavanca, nunca o corpo da chave.',
    texto: 'O batente sobe só ' + (EX.zBatente - EX.zPlaca).toFixed(0) + ' mm acima da placa do carro: alcança a ponta da alavanca (a parte que mais anda) e passa por baixo do corpo preto da microchave. Mesmo que o firmware erre e o carro passe do clique, ele empurra uma lâmina de aço flexível — não uma caixa de plástico rígida. E empurrar na ponta dá o curso maior e o clique mais repetível.' },
  { alvo: 'fc_base', em: [0, -16, 4], titulo: 'Por que 3,3 V e não 5 V',
    resumo: 'Os GPIO 34, 35 e 39 do ESP32 aceitam no máximo 3,3 V e não têm pull-up interno.',
    texto: 'A placa do fim de curso tem um resistor que puxa a saída S para o + quando a chave está solta. Ligando o + no 3,3 V do ESP32, o sinal nunca passa de 3,3 V. No 5 V, a entrada do ESP32 queima com o tempo. Por isso use o módulo com placa: uma microchave solta, sem resistor, deixaria a entrada flutuando (34/35/39 não têm pull-up interno).' },
  { alvo: 'bloco', em: [-8, -20, 50], titulo: 'Por que um braço maciço no bloco',
    resumo: 'A furação varia entre fabricantes: a placa vira gabarito.',
    texto: 'O braço é maciço e a placa da chave fica em 2 pezinhos de 3 mm (a solda dos pinos fica no vão). Os 2 furos-guia de 2,5 mm são para a placa mais comum. Se a sua tiver outra furação, encoste a placa no braço, marque pelos furos dela e fure com broca de 2,5 mm: o parafuso M3×12 rosqueia direto no plástico.' },
];

function instancias() {
  const I = [], add = (id, p, t, x) => I.push(inst(id, p, t, x));
  add('ctx_perfil', 'perfil2020_400', r.t(0, 0, EX.zPerfil), { contexto: true });
  add('ctx_trilho', 'mgn12_trilho_400', r.t(0, 0, EX.zTrilho), { contexto: true });
  add('ctx_motor', 'nema17', r.rx(90).t(EX.xP, EX.yPl1, 0), { contexto: true });
  add('bloco', 'eixo_bloco_motor', r.t(EX.xPe, 0, 0));
  add('patim', 'mgn12h_patim', r.t(60, 0, EX.zTrilho));
  add('placa', 'eixo_placa_carro', r.t(60, 0, EX.zPatim));
  add('fc_base', 'fc_mecanico_base', posFC(1));
  add('fc_alav', 'fc_mecanico_alav', alav(0));
  SW.furos.forEach((x, j) => add('p_fc_' + j, 'din912_m3x12', r.ry(-90).t(EX.xPlacaFC - 1.6, 0, EX.zFC - x)));
  return I;
}

export function moduloFuncFimDeCurso() {
  const I = instancias();
  const anim = { dur: DUR, trilhas: trilhas(), leg: LEG };
  const todos = I.filter(i => !i.id.startsWith('ctx_')).map(i => i.id);
  return {
    id: 'func_fc', nome: 'Como funciona: fim de curso', didatico: true,
    subtitulo: 'Microchave com alavanca (a mesma das impressoras 3D), na ponta de cada eixo.',
    resumo: 'Em jogo o carro nunca toca a chave; na referência ele encosta devagar, a alavanca clica e o firmware confere se o motor perdeu passo.',
    tempo: 'animação de 14 s',
    instancias: I,
    contexto: I.filter(i => i.id.startsWith('ctx_')).map(i => i.id),
    passos: [
      { titulo: 'Jogo × referência', base: todos, vista: 'frente', zoom: ['fc_base', 'fc_alav', 'placa'], anim, porques: PQ,
        texto: 'Ponta direita do eixo B, vista de frente. Veja o carro em jogo parar 1 mm antes da alavanca e, depois, encostar devagar até o clique. Pause (espaço) e clique nos círculos amarelos.' },
      { titulo: 'A alavanca de perto', base: todos, vista: 'frente', zoom: ['fc_alav'], anim, porques: [PQ[0], PQ[1]],
        texto: 'O batente azul empurra só a ponta da lâmina de aço. 2 mm até o clique, mais ~1,2 mm até a lâmina deitar no corpo preto — por isso o firmware para no clique.' },
      { titulo: 'Fixação e ligação', base: todos, vista: 'iso', zoom: ['fc_base', 'bloco'], porques: [PQ[3], PQ[2]],
        texto: 'Placa em pé no braço do bloco de ponta, 2 parafusos M3×12. Cabo de 3 vias: <b>+</b> no 3,3 V do ESP32, <b>−</b> no GND, <b>S</b> no GPIO (34 = eixo A direita, 35 = eixo B esquerda, 39 = eixo B direita).',
        tabelaTitulo: 'Onde vai cada fim de curso', tabelaCab: ['eixo / ponta', 'GPIO', 'obs.'],
        tabela: [['A, direita', '34', 'único do eixo A (à esquerda passa a calha de carga)'], ['B, esquerda', '35', ''], ['B, direita', '39', '']] },
    ],
  };
}
