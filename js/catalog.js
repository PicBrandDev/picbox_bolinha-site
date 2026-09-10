/* PICBOX - catalogo de componentes.
   TODOS os numeros abaixo sao ESTIMADOS (ordem de grandeza de datasheet e de
   pratica corrente). Nenhum e medicao de bancada. Ao selecionar uma opcao, os
   parametros correspondentes sao escritos no conjunto e marcados como estimados. */
(function (PB) {
  'use strict';
  var U = PB.util, P = PB.params;

  var CATALOG = [
    {
      id: 'soltura', label: 'Mecanismo de soltura',
      note: 'Domina o jitter total da cadeia: e o ultimo elo antes da bola sair.',
      options: [
        { name: 'Solenoide + driver dedicado (MOSFET, flyback)', cost: 45, set: { 'rel.type': 'solenoide', 'rel.jit': 0.3, 'rel.lat': 8, 'rel.spin': 4 }, jitter: '0,3 ms', obs: 'Curso curto, corrente de pico alta. Precisa de fonte firme; jitter cresce se a fonte afundar.' },
        { name: 'Servo hobby (MG996R / SG90)', cost: 25, set: { 'rel.type': 'servo', 'rel.jit': 8, 'rel.lat': 45, 'rel.spin': 12 }, jitter: '8 ms', obs: 'Barato, mas o laco interno do servo e assincrono ao MCU: jitter de uma ordem de grandeza acima do solenoide.' },
        { name: 'Came motorizada continua', cost: 60, set: { 'rel.type': 'motor DC com came', 'rel.jit': 2.5, 'rel.lat': 20, 'rel.spin': 25 }, jitter: '2,5 ms', obs: 'Soltura em fase fixa da came. Impoe spin residual alto; verifique a prova de Magnus.' }
      ]
    },
    {
      id: 'motor', label: 'Motor dos eixos',
      note: 'Define o erro de posicao repetivel do carro.',
      options: [
        { name: 'Passo NEMA 17 + encoder de malha fechada', cost: 180, set: { 'enc.err': 0.05, 'mot.model': 'NEMA 17 + encoder', 'mot.torque': 40, 'mot.ustep': 16, 'enc.res': 40 }, jitter: '0,05 mm', obs: 'Perda de passo detectada e corrigida. Melhor relacao previsibilidade/custo.' },
        { name: 'BLDC com encoder', cost: 260, set: { 'enc.err': 0.08, 'mot.model': 'BLDC 42mm + encoder', 'mot.torque': 55, 'mot.ustep': 1, 'enc.res': 60 }, jitter: '0,08 mm', obs: 'Silencioso e eficiente. Controle mais complexo; ripple de comutacao aparece no perfil.' },
        { name: 'DC escovado com potenciometro', cost: 70, set: { 'enc.err': 0.60, 'mot.model': 'DC 12V + pot linear', 'mot.torque': 20, 'mot.ustep': 1, 'enc.res': 2 }, jitter: '0,60 mm', obs: 'Realimentacao analogica ruidosa e nao linear. Costuma ser o item que derruba a razao de sigmas.' }
      ]
    },
    {
      id: 'transmissao', label: 'Transmissao',
      note: 'Folga e o erro que nao aparece em bancada estatica: so na inversao.',
      options: [
        { name: 'Correia GT2 + polia 20 dentes', cost: 40, set: { 'tr.type': 'correia GT2', 'tr.teeth': 20, 'tr.pitch': 2, 'mech.back': 0.10 }, jitter: '0,10 mm', obs: 'Avanco 40 mm/volta. Folga baixa se tensionada; alonga com o tempo — item de manutencao.' },
        { name: 'Fuso trapezoidal T8 + castanha', cost: 120, set: { 'tr.type': 'fuso trapezoidal', 'tr.teeth': 1, 'tr.pitch': 8, 'mech.back': 0.20 }, jitter: '0,20 mm', obs: 'Rigido, mas lento e com folga axial na castanha. Ruim para inversoes frequentes.' },
        { name: 'Pinhao e cremalheira', cost: 95, set: { 'tr.type': 'cremalheira', 'tr.teeth': 20, 'tr.pitch': 3.14, 'mech.back': 0.30 }, jitter: '0,30 mm', obs: 'Curso ilimitado, folga entre dentes alta sem pre-carga.' }
      ]
    },
    {
      id: 'deteccao', label: 'Deteccao na boca',
      note: 'Nao afeta a trajetoria: afeta a capacidade de PROVAR o que aconteceu.',
      options: [
        { name: 'Barreira optica (fototransistor + IR)', cost: 35, set: { 'opt.lat': 0.2, 'opt.fs': 2000 }, jitter: '0,2 ms', obs: 'Resolve a passagem da bola com folga. Exige alinhamento e protecao contra luz ambiente.' },
        { name: 'Sensor indutivo', cost: 60, set: { 'opt.lat': 1.5, 'opt.fs': 500 }, jitter: '1,5 ms', obs: 'So funciona com bola metalica. Robusto a sujeira.' },
        { name: 'Chave mecanica (microswitch)', cost: 8, set: { 'opt.lat': 8, 'opt.fs': 100 }, jitter: '8 ms', obs: 'Barato e sujeito a bounce. Pode nao registrar bola leve que passa raspando.' }
      ]
    },
    {
      id: 'entrada', label: 'Cadeia de entrada (botao -> MCU)',
      note: 'A varredura do MCU vira quantizacao pura: sigma = passo / raiz(12).',
      options: [
        { name: 'Interrupcao externa dedicada + debounce por hardware', cost: 12, set: { 'in.scan': 0.2, 'in.jit': 0.05, 'in.deb': 2, 'in.lat': 1 }, jitter: '0,06 ms', obs: 'RC + Schmitt trigger. O caminho mais curto entre o dedo e o solenoide.' },
        { name: 'Laco de varredura a 1 kHz', cost: 0, set: { 'in.scan': 1, 'in.jit': 0.2, 'in.deb': 8, 'in.lat': 2 }, jitter: '0,34 ms', obs: 'Padrao de firmware simples. Aceitavel se a soltura for solenoide.' },
        { name: 'Laco de varredura a 100 Hz (loop principal)', cost: 0, set: { 'in.scan': 10, 'in.jit': 1.0, 'in.deb': 20, 'in.lat': 5 }, jitter: '3,0 ms', obs: 'Comum em firmware feito as pressas. Sozinho pode dominar todo o sigma da maquina.' }
      ]
    }
  ];

  // Selecao corrente: inferida dos parametros (a opcao cujo conjunto mais se aproxima)
  var selection = { soltura: 0, motor: 0, transmissao: 0, deteccao: 0, entrada: 1 };

  function select(catId, idx) {
    var cat = CATALOG.filter(function (c) { return c.id === catId; })[0];
    if (!cat || !cat.options[idx]) return;
    selection[catId] = idx;
    var s = cat.options[idx].set, k;
    for (k in s) { P.set(k, s[k], true); P.setStat(k, 'est', true); }
    P.touch();
  }
  function selected(catId) { return selection[catId]; }

  // sigma da cadeia (s) para um conjunto hipotetico de parametros
  function sigTimeFor(over) {
    var g = function (k) { return over && over[k] !== undefined ? +over[k] : P.num(k); };
    return Math.sqrt(
      Math.pow(g('rel.jit') / 1000, 2) +
      Math.pow(g('in.jit') / 1000, 2) +
      Math.pow(g('in.scan') / 1000, 2) / 12
    );
  }
  function sigPosFor(over, v0mmps, vRelmmps) {
    var g = function (k) { return over && over[k] !== undefined ? +over[k] : P.num(k); };
    var st = sigTimeFor(over);
    return {
      sigT: st,
      spec: Math.abs(v0mmps) * st,
      full: Math.sqrt(Math.pow(Math.abs(vRelmmps) * st, 2) + Math.pow(g('enc.err'), 2) + Math.pow(g('mech.back'), 2))
    };
  }

  // impacto de cada opcao no sigma_maquina, mantendo o resto do conjunto
  function impactTable(v0, vRel) {
    return CATALOG.map(function (cat) {
      return {
        cat: cat,
        rows: cat.options.map(function (o, i) {
          var s = sigPosFor(o.set, v0, vRel);
          return { opt: o, idx: i, sigT: s.sigT, spec: s.spec, full: s.full, selected: selection[cat.id] === i };
        })
      };
    });
  }

  PB.catalog = {
    CATALOG: CATALOG, select: select, selected: selected,
    impactTable: impactTable, sigTimeFor: sigTimeFor, sigPosFor: sigPosFor,
    selection: function () { return selection; }
  };
})(window.PB);
