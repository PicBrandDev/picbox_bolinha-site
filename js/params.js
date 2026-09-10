/* PICBOX - registro de parametros.
   Todo parametro tem: chave, grupo, rotulo, unidade explicita, valor,
   e flag de procedencia: 'est' (estimado) ou 'med' (medido em bancada).
   REGRA DO PROJETO: todo valor padrao nasce ESTIMADO. Nada aqui e medicao. */
(function (PB) {
  'use strict';
  var U = PB.util;

  // k=chave g=grupo l=rotulo u=unidade v=valor min max step
  // s=procedencia ('est'|'med'|'def' para constante definida) t=tipo o=opcoes n=nota
  var SCHEMA = [
    // ---------------- BOLA ----------------
    { k: 'ball.d', g: 'Bola', l: 'Diâmetro', u: 'mm', v: 38, min: 8, max: 120, step: 0.5, s: 'est' },
    { k: 'ball.m', g: 'Bola', l: 'Massa', u: 'g', v: 26, min: 1, max: 500, step: 0.5, s: 'est' },
    { k: 'ball.mat', g: 'Bola', l: 'Material', u: '—', v: 'ABS', t: 'sel', o: ['ABS', 'Poliuretano', 'Aço', 'Borracha', 'Madeira', 'Acrílico'], s: 'est' },
    { k: 'ball.e', g: 'Bola', l: 'Coef. de restituição', u: '—', v: 0.72, min: 0, max: 1, step: 0.01, s: 'est', n: 'Só afeta ricochete na borda; não afeta o critério de vitória.' },
    { k: 'ball.cd', g: 'Bola', l: 'Coef. de arrasto Cd', u: '—', v: 0.47, min: 0.05, max: 1.5, step: 0.01, s: 'est', n: 'Esfera lisa em regime subcrítico. Depende de Re — a seção de arrasto verifica.' },
    { k: 'ball.ki', g: 'Bola', l: 'Fator de inércia k (I = k·m·r²)', u: '—', v: 0.4, min: 0.1, max: 1, step: 0.01, s: 'est', n: '0,400 = esfera maciça homogênea; 0,667 = casca fina.' },

    // ---------------- EIXO A ----------------
    { k: 'A.stroke', g: 'Eixo A (bola)', l: 'Curso útil', u: 'mm', v: 320, min: 50, max: 1200, step: 5, s: 'est' },
    { k: 'A.mass', g: 'Eixo A (bola)', l: 'Massa do carro', u: 'g', v: 210, min: 10, max: 3000, step: 5, s: 'est' },
    { k: 'A.prof', g: 'Eixo A (bola)', l: 'Perfil de movimento', u: '—', v: 'senoidal', t: 'sel', o: ['senoidal', 'triangular', 'trapezoidal', 'customizado'], s: 'est' },
    { k: 'A.T', g: 'Eixo A (bola)', l: 'Período ida-e-volta', u: 's', v: 2.40, min: 0.3, max: 12, step: 0.02, s: 'est' },
    { k: 'A.phase', g: 'Eixo A (bola)', l: 'Defasagem', u: 'graus', v: 0, min: -180, max: 180, step: 1, s: 'def' },
    { k: 'A.aPeak', g: 'Eixo A (bola)', l: 'Aceleração de pico (perfil trapezoidal)', u: 'mm/s²', v: 4000, min: 100, max: 60000, step: 50, s: 'est' },
    { k: 'A.jerk', g: 'Eixo A (bola)', l: 'Jerk admitido', u: 'mm/s³', v: 60000, min: 500, max: 2000000, step: 500, s: 'est' },

    // ---------------- EIXO B ----------------
    { k: 'B.stroke', g: 'Eixo B (buraco)', l: 'Curso útil', u: 'mm', v: 320, min: 50, max: 1200, step: 5, s: 'est' },
    { k: 'B.mass', g: 'Eixo B (buraco)', l: 'Massa do carro', u: 'g', v: 320, min: 10, max: 3000, step: 5, s: 'est' },
    { k: 'B.prof', g: 'Eixo B (buraco)', l: 'Perfil de movimento', u: '—', v: 'senoidal', t: 'sel', o: ['senoidal', 'triangular', 'trapezoidal', 'customizado'], s: 'est' },
    { k: 'B.T', g: 'Eixo B (buraco)', l: 'Período ida-e-volta', u: 's', v: 3.10, min: 0.3, max: 12, step: 0.02, s: 'est' },
    { k: 'B.phase', g: 'Eixo B (buraco)', l: 'Defasagem em relação ao eixo A', u: 'graus', v: 90, min: -180, max: 180, step: 1, s: 'def' },
    { k: 'B.aPeak', g: 'Eixo B (buraco)', l: 'Aceleração de pico (perfil trapezoidal)', u: 'mm/s²', v: 3500, min: 100, max: 60000, step: 50, s: 'est' },
    { k: 'B.jerk', g: 'Eixo B (buraco)', l: 'Jerk admitido', u: 'mm/s³', v: 50000, min: 500, max: 2000000, step: 500, s: 'est' },

    // ---------------- GEOMETRIA ----------------
    { k: 'geo.h', g: 'Geometria', l: 'Altura de queda (plano de soltura -> boca do buraco)', u: 'mm', v: 420, min: 20, max: 2000, step: 1, s: 'est' },
    { k: 'geo.L', g: 'Geometria', l: 'Largura da abertura do buraco', u: 'mm', v: 78, min: 5, max: 400, step: 0.5, s: 'est' },
    { k: 'geo.depth', g: 'Geometria', l: 'Profundidade da boca', u: 'mm', v: 60, min: 5, max: 400, step: 1, s: 'est' },
    { k: 'geo.sep', g: 'Geometria', l: 'Separação entre planos dos eixos (mecânica)', u: 'mm', v: 445, min: 20, max: 2000, step: 1, s: 'est', n: 'Deve ser maior ou igual à altura de queda. A diferença é o recuo do plano de soltura dentro do carro A.' },
    { k: 'geo.floor', g: 'Geometria', l: 'Área de piso do gabinete (lado)', u: 'mm', v: 450, min: 200, max: 1200, step: 5, s: 'est' },

    // ---------------- SOLTURA ----------------
    { k: 'rel.type', g: 'Mecanismo de soltura', l: 'Tipo', u: '—', v: 'solenoide', t: 'sel', o: ['solenoide', 'servo', 'motor DC com came'], s: 'est' },
    { k: 'rel.lat', g: 'Mecanismo de soltura', l: 'Latência média de soltura', u: 'ms', v: 14, min: 0, max: 300, step: 0.1, s: 'est' },
    { k: 'rel.jit', g: 'Mecanismo de soltura', l: 'Jitter de soltura (1 sigma)', u: 'ms', v: 0.8, min: 0, max: 60, step: 0.05, s: 'est' },
    { k: 'rel.spin', g: 'Mecanismo de soltura', l: 'Spin residual imposto à bola', u: 'rad/s', v: 6, min: 0, max: 400, step: 0.5, s: 'est' },
    { k: 'rel.vy0', g: 'Mecanismo de soltura', l: 'Velocidade vertical inicial (para baixo)', u: 'mm/s', v: 0, min: -500, max: 500, step: 1, s: 'est', n: 'Ideal = 0. Valor não nulo indica que o mecanismo empurra a bola.' },

    // ---------------- CADEIA DE ENTRADA ----------------
    { k: 'in.deb', g: 'Cadeia de entrada', l: 'Debounce do botão', u: 'ms', v: 10, min: 0, max: 100, step: 0.5, s: 'est' },
    { k: 'in.scan', g: 'Cadeia de entrada', l: 'Período de varredura do MCU', u: 'ms', v: 4, min: 0.05, max: 50, step: 0.05, s: 'est', n: 'Quantização uniforme: contribui sigma = período / raiz(12).' },
    { k: 'in.lat', g: 'Cadeia de entrada', l: 'Latência eletrônica adicional (driver, ISR)', u: 'ms', v: 3, min: 0, max: 200, step: 0.1, s: 'est' },
    { k: 'in.jit', g: 'Cadeia de entrada', l: 'Jitter eletrônico (1 sigma)', u: 'ms', v: 0.4, min: 0, max: 40, step: 0.05, s: 'est' },

    // ---------------- SENSORIAMENTO E ACIONAMENTO ----------------
    { k: 'enc.res', g: 'Sensoriamento e acionamento', l: 'Encoder: resolução', u: 'pulsos/mm', v: 20, min: 0.1, max: 2000, step: 0.1, s: 'est' },
    { k: 'enc.err', g: 'Sensoriamento e acionamento', l: 'Encoder: erro de posição (1 sigma)', u: 'mm', v: 0.12, min: 0, max: 20, step: 0.01, s: 'est' },
    { k: 'mech.back', g: 'Sensoriamento e acionamento', l: 'Folga / backlash da transmissão (1 sigma equivalente)', u: 'mm', v: 0.10, min: 0, max: 20, step: 0.01, s: 'est' },
    { k: 'opt.fs', g: 'Sensoriamento e acionamento', l: 'Barreira óptica: taxa de amostragem', u: 'Hz', v: 2000, min: 10, max: 200000, step: 10, s: 'est' },
    { k: 'opt.lat', g: 'Sensoriamento e acionamento', l: 'Barreira óptica: latência de detecção', u: 'ms', v: 0.2, min: 0, max: 50, step: 0.01, s: 'est' },
    { k: 'mot.model', g: 'Sensoriamento e acionamento', l: 'Motor: modelo', u: '—', v: 'NEMA 17', t: 'txt', s: 'est' },
    { k: 'mot.torque', g: 'Sensoriamento e acionamento', l: 'Motor: torque de retenção', u: 'N·cm', v: 40, min: 1, max: 800, step: 1, s: 'est' },
    { k: 'mot.ustep', g: 'Sensoriamento e acionamento', l: 'Motor: micropasso', u: 'x', v: 16, t: 'sel', o: [1, 2, 4, 8, 16, 32, 64, 128, 256], s: 'est' },
    { k: 'mot.steps', g: 'Sensoriamento e acionamento', l: 'Motor: passos por volta (inteiro)', u: 'passos', v: 200, min: 4, max: 2000, step: 1, s: 'est' },
    { k: 'tr.type', g: 'Sensoriamento e acionamento', l: 'Transmissão', u: '—', v: 'correia GT2', t: 'sel', o: ['correia GT2', 'fuso trapezoidal', 'cremalheira'], s: 'est' },
    { k: 'tr.teeth', g: 'Sensoriamento e acionamento', l: 'Dentes da polia', u: 'dentes', v: 20, min: 6, max: 90, step: 1, s: 'est' },
    { k: 'tr.pitch', g: 'Sensoriamento e acionamento', l: 'Passo da correia', u: 'mm', v: 2, min: 0.5, max: 20, step: 0.1, s: 'est', n: 'GT2 = 2 mm. Avanço por volta = dentes x passo.' },
    { k: 'mot.eff', g: 'Sensoriamento e acionamento', l: 'Rendimento eletromecânico', u: '—', v: 0.45, min: 0.05, max: 1, step: 0.01, s: 'est' },
    { k: 'elec.base', g: 'Sensoriamento e acionamento', l: 'Consumo de base (eletrônica, luz, som)', u: 'W', v: 35, min: 0, max: 1000, step: 1, s: 'est' },

    // ---------------- AMBIENTE ----------------
    { k: 'env.g', g: 'Ambiente', l: 'Gravidade', u: 'm/s²', v: 9.80665, min: 0.5, max: 30, step: 0.00001, s: 'def', n: 'Valor padrão CGPM. Editável apenas para sanity check.' },
    { k: 'env.rho', g: 'Ambiente', l: 'Densidade do ar', u: 'kg/m³', v: 1.184, min: 0.001, max: 15, step: 0.001, s: 'est', n: 'Ar seco a 25 graus C, 101,325 kPa.' },
    { k: 'env.mu', g: 'Ambiente', l: 'Viscosidade dinâmica do ar', u: 'Pa·s', v: 1.849e-5, min: 1e-7, max: 1e-2, step: 1e-7, s: 'est' },

    // ---------------- MODELO DE JOGADOR ----------------
    { k: 'ply.novice', g: 'Modelo de jogador', l: 'sigma de timing - iniciante', u: 'ms', v: 130, min: 1, max: 800, step: 1, s: 'est', n: 'Ordem de grandeza de tarefa de antecipação não treinada. VALOR ESTIMADO, exige medição com sujeitos reais.' },
    { k: 'ply.mid', g: 'Modelo de jogador', l: 'sigma de timing - médio', u: 'ms', v: 65, min: 1, max: 800, step: 1, s: 'est' },
    { k: 'ply.pro', g: 'Modelo de jogador', l: 'sigma de timing - treinado', u: 'ms', v: 26, min: 1, max: 800, step: 1, s: 'est', n: 'Quem farma a máquina. É por este perfil que se dimensiona o prêmio.' },
    { k: 'ply.bias', g: 'Modelo de jogador', l: 'Viés sistemático de timing (todos os perfis)', u: 'ms', v: 0, min: -300, max: 300, step: 1, s: 'est', n: 'Erro médio, não aleatório. Jogador treinado tende a zerar isto.' },
    { k: 'ply.select', g: 'Modelo de jogador', l: 'Estratégia de escolha da oportunidade', u: '—', v: 'próxima oportunidade', t: 'sel', o: ['próxima oportunidade', 'melhor oportunidade'], s: 'def', n: 'Cada passagem do buraco tem uma janela diferente. "próxima" = solta na primeira que aparece. "melhor" = espera a janela mais larga do ciclo — é o que um jogador treinado faz. A diferença entre as duas é uma medida de quanto o conhecimento da máquina vale.' },

    // ---------------- ESCADA / PARTIDA ----------------
    { k: 'lad.n', g: 'Escada e partida', l: 'Número de rodadas', u: 'rodadas', v: 8, min: 1, max: 30, step: 1, s: 'def' },
    { k: 'lad.spd', g: 'Escada e partida', l: 'Incremento de velocidade por rodada', u: '%', v: 12, min: 0, max: 60, step: 1, s: 'def' },
    { k: 'lad.ap', g: 'Escada e partida', l: 'Redução de abertura por rodada', u: '%', v: 5, min: 0, max: 30, step: 0.5, s: 'def' },
    { k: 'game.tdec', g: 'Escada e partida', l: 'Tempo de observação do jogador por rodada', u: 's', v: 4.5, min: 0.2, max: 60, step: 0.1, s: 'est' },
    { k: 'game.treset', g: 'Escada e partida', l: 'Tempo de recolhimento / reset por rodada', u: 's', v: 2.2, min: 0, max: 30, step: 0.1, s: 'est' },
    { k: 'game.attract', g: 'Escada e partida', l: 'Tempo de attract entre partidas', u: 's', v: 20, min: 0, max: 600, step: 1, s: 'est' },

    // ---------------- ECONOMIA ----------------
    { k: 'eco.price', g: 'Economia', l: 'Preço da jogada', u: 'R$', v: 5.00, min: 0, max: 500, step: 0.25, s: 'def' },
    { k: 'eco.plays', g: 'Economia', l: 'Jogadas por dia', u: 'jogadas/dia', v: 120, min: 1, max: 20000, step: 1, s: 'est' },
    { k: 'eco.cap', g: 'Economia', l: 'Teto de custo de prêmio (perfil TREINADO)', u: '% da receita', v: 30, min: 1, max: 100, step: 1, s: 'def' },
    { k: 'eco.mixNov', g: 'Economia', l: 'Mix de público - iniciante', u: '%', v: 55, min: 0, max: 100, step: 1, s: 'est' },
    { k: 'eco.mixMid', g: 'Economia', l: 'Mix de público - médio', u: '%', v: 40, min: 0, max: 100, step: 1, s: 'est' },
    { k: 'eco.mixPro', g: 'Economia', l: 'Mix de público - treinado', u: '%', v: 5, min: 0, max: 100, step: 1, s: 'est' },
    { k: 'eco.kwh', g: 'Economia', l: 'Tarifa de energia', u: 'R$/kWh', v: 0.95, min: 0, max: 20, step: 0.01, s: 'est' },

    // ---------------- MODELO / NUMERICO ----------------
    { k: 'sim.dt', g: 'Modelo numérico', l: 'Passo de integração do voo (RK4)', u: 'ms', v: 0.25, min: 0.005, max: 5, step: 0.005, s: 'def' },
    { k: 'sim.drag', g: 'Modelo numérico', l: 'Incluir arrasto na trajetória', u: '—', v: 1, t: 'bool', s: 'def', n: 'Desligar só depois que a prova de arrasto mostrar que é desprezível.' },
    { k: 'sim.magnus', g: 'Modelo numérico', l: 'Incluir Magnus (spin residual) na trajetória', u: '—', v: 0, t: 'bool', s: 'def', n: 'Modelo de Cl grosseiro; use como sensibilidade, não como verdade.' },
    { k: 'sim.crit', g: 'Modelo numérico', l: 'Critério de vitória usado no jogo', u: '—', v: 'conformidade', t: 'sel', o: ['conformidade', 'passagem limpa'], s: 'def', n: 'conformidade = centro da bola dentro da boca (|delta| <= L/2). passagem limpa = a bola inteira passa (|delta| <= (L-d)/2).' },
    { k: 'sim.macjit', g: 'Modelo numérico', l: 'Aplicar jitter da máquina no modo Jogar', u: '—', v: 1, t: 'bool', s: 'def' },
    { k: 'sim.mcjit', g: 'Modelo numérico', l: 'Aplicar jitter da máquina no Monte Carlo', u: '—', v: 0, t: 'bool', s: 'def', n: 'Padrão desligado: o resultado do estudo deve depender só do erro humano de timing.' },
    { k: 'sim.seed', g: 'Modelo numérico', l: 'Semente do gerador aleatório', u: '—', v: 20260909, min: 1, max: 2147483647, step: 1, s: 'def' },
    { k: 'sim.mcN', g: 'Modelo numérico', l: 'Partidas por perfil no Monte Carlo', u: 'partidas', v: 4000, min: 50, max: 200000, step: 50, s: 'def' }
  ];

  var byKey = {}, values = {}, status = {}, listeners = [];
  SCHEMA.forEach(function (d) { byKey[d.k] = d; values[d.k] = d.v; status[d.k] = d.s; });

  // Tabela do perfil customizado: pares (t normalizado 0..1, x normalizado 0..1)
  var customTable = {
    A: [[0, 0], [0.12, 0.10], [0.25, 0.34], [0.38, 0.72], [0.5, 1], [0.62, 0.90], [0.75, 0.62], [0.88, 0.24], [1, 0]],
    B: [[0, 0], [0.15, 0.22], [0.3, 0.55], [0.45, 0.92], [0.5, 1], [0.6, 0.86], [0.75, 0.50], [0.9, 0.15], [1, 0]]
  };

  var ladder = null;
  function defaultLadder() {
    var n = get('lad.n'), i, out = [];
    for (i = 1; i <= n; i++) {
      out.push({
        n: i,
        speedMul: 1 + (get('lad.spd') / 100) * (i - 1),
        L: get('geo.L') * Math.pow(1 - get('lad.ap') / 100, i - 1),
        h: get('geo.h'),
        prize: null
      });
    }
    return out;
  }
  function getLadder() { if (!ladder) { ladder = defaultLadder(); syncPrizes(); } return ladder; }
  function rebuildLadder() { ladder = defaultLadder(); syncPrizes(); return ladder; }
  function setLadder(l) { ladder = l; syncPrizes(); }

  var prizes = [
    { name: 'Pelúcia pequena', cost: 4.50, level: 3, s: 'est' },
    { name: 'Fone bluetooth', cost: 22.00, level: 6, s: 'est' },
    { name: 'Console portátil', cost: 180.00, level: 8, s: 'est' }
  ];
  function getPrizes() { return prizes; }
  function setPrizes(p) { prizes = p; syncPrizes(); }
  function syncPrizes() {
    if (!ladder) return;
    ladder.forEach(function (r) { r.prize = null; });
    prizes.forEach(function (p) {
      var row = ladder.filter(function (r) { return r.n === +p.level; })[0];
      if (row) row.prize = p;
    });
  }

  function get(k) { return values[k]; }
  function num(k) { return +values[k]; }
  function set(k, v, silent) {
    var d = byKey[k]; if (!d) return;
    if (d.t === 'txt') values[k] = v;
    else if (d.t === 'sel') values[k] = (typeof d.o[0] === 'number') ? +v : v;
    else values[k] = +v;
    if (!silent) emit(k);
  }
  function stat(k) { return status[k]; }
  function setStat(k, s, silent) { status[k] = s; if (!silent) emit(k); }
  function schema() { return SCHEMA; }
  function def(k) { return byKey[k]; }
  function groups() {
    var g = [], seen = {};
    SCHEMA.forEach(function (d) { if (!seen[d.g]) { seen[d.g] = 1; g.push(d.g); } });
    return g;
  }
  function onChange(f) { listeners.push(f); }
  var emitTimer = null, dirty = {};
  function emit(k) {
    dirty[k] = 1;
    if (emitTimer) return;
    emitTimer = setTimeout(function () {
      var ks = Object.keys(dirty); dirty = {}; emitTimer = null;
      var rebuild = ks.some(function (x) {
        return x === 'lad.n' || x === 'lad.spd' || x === 'lad.ap' || x === 'geo.L' || x === 'geo.h' || x === '*';
      });
      if (rebuild) rebuildLadder();
      listeners.forEach(function (f) { f(ks); });
    }, 0);
  }
  function touch() { emit('*'); }

  function estimated() { return SCHEMA.filter(function (d) { return status[d.k] === 'est'; }); }
  function measured() { return SCHEMA.filter(function (d) { return status[d.k] === 'med'; }); }

  function canonical() {
    var parts = SCHEMA.map(function (d) { return d.k + '=' + values[d.k] + '@' + status[d.k]; });
    parts.push('customA=' + JSON.stringify(customTable.A));
    parts.push('customB=' + JSON.stringify(customTable.B));
    parts.push('ladder=' + JSON.stringify(getLadder().map(function (r) { return [r.n, +r.speedMul.toFixed(6), +r.L.toFixed(4), +r.h.toFixed(3)]; })));
    parts.push('prizes=' + JSON.stringify(prizes.map(function (p) { return [p.name, p.cost, p.level]; })));
    return parts.join('\n');
  }
  function hash() { return U.hash32(canonical()); }

  var VERSION = '1.0.0';
  function preset() {
    return {
      formato: 'picbox-preset', versao: VERSION, gerado: U.nowStamp(),
      hash: hash(), valores: JSON.parse(JSON.stringify(values)),
      procedencia: JSON.parse(JSON.stringify(status)),
      tabelaCustom: JSON.parse(JSON.stringify(customTable)),
      escada: getLadder().map(function (r) { return { n: r.n, speedMul: r.speedMul, L: r.L, h: r.h }; }),
      premios: JSON.parse(JSON.stringify(prizes))
    };
  }
  function loadPreset(obj) {
    if (!obj || obj.formato !== 'picbox-preset') throw new Error('Arquivo não é um preset PICBOX.');
    Object.keys(obj.valores || {}).forEach(function (k) { if (byKey[k]) values[k] = obj.valores[k]; });
    Object.keys(obj.procedencia || {}).forEach(function (k) { if (byKey[k]) status[k] = obj.procedencia[k]; });
    if (obj.tabelaCustom) customTable = obj.tabelaCustom;
    if (obj.premios) prizes = obj.premios;
    if (obj.escada) ladder = obj.escada.map(function (r) { return { n: r.n, speedMul: r.speedMul, L: r.L, h: r.h, prize: null }; });
    else ladder = null;
    syncPrizes();
    listeners.forEach(function (f) { f(['*']); });
  }
  function resetAll() {
    SCHEMA.forEach(function (d) { values[d.k] = d.v; status[d.k] = d.s; });
    ladder = null; getLadder();
    listeners.forEach(function (f) { f(['*']); });
  }

  PB.params = {
    get: get, num: num, set: set, stat: stat, setStat: setStat, def: def,
    schema: schema, groups: groups, onChange: onChange, touch: touch,
    estimated: estimated, measured: measured, canonical: canonical, hash: hash,
    preset: preset, loadPreset: loadPreset, resetAll: resetAll,
    customTable: function () { return customTable; },
    setCustomTable: function (ax, t) { customTable[ax] = t; touch(); },
    getLadder: getLadder, setLadder: setLadder, rebuildLadder: rebuildLadder,
    getPrizes: getPrizes, setPrizes: setPrizes, syncPrizes: syncPrizes,
    VERSION: VERSION
  };
})(window.PB);
