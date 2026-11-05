/* PICBOX - modelo de acerto: mundo, oportunidades, janelas, sigmas e probabilidades.
   Esta camada e a unica fonte de verdade para os quatro modos. */
(function (PB) {
  'use strict';
  var U = PB.util, PH = PB.physics;

  // ============================================================
  // MUNDO: instancia os dois eixos e pre-calcula a tabela de voo
  // ============================================================
  // A tabela de voo existe por desempenho: o tempo de queda e o avanco
  // horizontal dependem SO da velocidade de soltura (dados h, arrasto, ar).
  // Integrar RK4 dentro do laco de busca seria 4 ordens de grandeza mais caro.
  // O erro de interpolacao e medido e exposto em ft.interpErrMm.

  function buildWorld(round, over) {
    var P = PB.params;
    over = over || {};
    round = round || { n: 1, speedMul: 1, L: P.num('geo.L'), h: P.num('geo.h') };

    var sm = round.speedMul || 1;
    var axA = PH.makeAxis({
      stroke: P.num('A.stroke'), T: P.num('A.T') / sm, phaseDeg: P.num('A.phase'),
      profile: P.get('A.prof'), aPeak: P.num('A.aPeak'), jerk: P.num('A.jerk'),
      table: P.customTable().A
    });
    var axB = PH.makeAxis({
      stroke: P.num('B.stroke'), T: P.num('B.T') / sm, phaseDeg: P.num('A.phase') + P.num('B.phase'),
      profile: P.get('B.prof'), aPeak: P.num('B.aPeak'), jerk: P.num('B.jerk'),
      table: P.customTable().B
    });

    var d = over.d !== undefined ? over.d : P.num('ball.d');
    var L = over.L !== undefined ? over.L : round.L;
    var h = over.h !== undefined ? over.h : round.h;

    // cadeia input -> soltura
    var latMean = (P.num('in.deb') + P.num('in.scan') / 2 + P.num('in.lat') + P.num('rel.lat')) / 1000; // s
    var sigT = Math.sqrt(
      Math.pow(P.num('rel.jit') / 1000, 2) +
      Math.pow(P.num('in.jit') / 1000, 2) +
      Math.pow(P.num('in.scan') / 1000, 2) / 12
    ); // s  (varredura do MCU: quantizacao uniforme -> sigma = passo/raiz(12))

    var flightBase = {
      g: P.num('env.g'), m: P.num('ball.m') / 1000, d: d / 1000,
      cd: P.num('ball.cd'), rho: P.num('env.rho'), mu: P.num('env.mu'),
      spin: P.num('rel.spin'), ki: P.num('ball.ki'),
      drag: !!P.num('sim.drag'), magnus: !!P.num('sim.magnus'),
      dt: P.num('sim.dt') / 1000, h: h / 1000, vy0: P.num('rel.vy0') / 1000
    };

    // ---- tabela de voo ----
    var vMax = Math.max(axA.meta.vPeak, 1) * 1.05 / 1000;  // m/s
    var N = 121, vs = [], ts = [], dxs = [], i;
    for (i = 0; i < N; i++) {
      var v = -vMax + 2 * vMax * i / (N - 1);
      var f = PH.flight(Object.assign({}, flightBase, { vx0: v }));
      vs.push(v); ts.push(f.t); dxs.push(f.dx);
    }
    function lut(arr, v) {
      var f = (v + vMax) / (2 * vMax) * (N - 1);
      if (f <= 0) return arr[0];
      if (f >= N - 1) return arr[N - 1];
      var i0 = Math.floor(f), fr = f - i0;
      return arr[i0] + (arr[i0 + 1] - arr[i0]) * fr;
    }
    // erro de interpolacao, medido
    var errT = 0, errX = 0;
    for (i = 0; i < 17; i++) {
      var vt = -vMax + 2 * vMax * (i + 0.5) / 17;
      var ex = PH.flight(Object.assign({}, flightBase, { vx0: vt }));
      errT = Math.max(errT, Math.abs(ex.t - lut(ts, vt)));
      errX = Math.max(errX, Math.abs(ex.dx - lut(dxs, vt)) * 1000);
    }

    var w = {
      round: round, axA: axA, axB: axB, L: L, h: h, d: d,
      latMean: latMean, sigT: sigT, flightBase: flightBase,
      ft: { vMax: vMax, interpErrMm: errX, interpErrS: errT, tMid: ts[(N - 1) / 2 | 0] },
      tolClean: Math.max(0, (L - d) / 2),
      tolValid: L / 2,
      crit: P.get('sim.crit'),
      tFlight: function (vx0mmps) { return lut(ts, vx0mmps / 1000); },
      dxOf: function (vx0mmps) { return lut(dxs, vx0mmps / 1000) * 1000; }
    };
    w.tol = (w.crit === 'conformidade') ? w.tolValid : w.tolClean;
    return w;
  }

  // ============================================================
  // AVALIACAO DE UMA SOLTURA
  // ============================================================
  // tPress = instante em que o jogador aperta o botao (s, tempo da maquina)
  // jitS   = realizacao do jitter da cadeia (s), 0 no caso nominal
  function evalPress(w, tPress, jitS) {
    var tRel = tPress + w.latMean + (jitS || 0);
    var xRel = w.axA.pos(tRel);
    var v0 = w.axA.vel(tRel);              // mm/s - a bola herda esta velocidade
    var tf = w.tFlight(v0);
    var dx = w.dxOf(v0);
    var tLand = tRel + tf;
    var xBall = xRel + dx;
    var xHole = w.axB.pos(tLand);
    var vHole = w.axB.vel(tLand);
    // velocidade horizontal da bola no cruzamento: sem arrasto = v0; com arrasto, menor
    var vBallX = w.flightBase.drag ? estimateVxEnd(w, v0) : v0;
    var delta = xBall - xHole;
    return {
      tPress: tPress, tRel: tRel, xRel: xRel, v0: v0, tf: tf, dx: dx,
      tLand: tLand, xBall: xBall, xHole: xHole, vHole: vHole, vBallX: vBallX,
      vRel: vBallX - vHole, delta: delta,
      hitClean: Math.abs(delta) <= w.tolClean,
      hitValid: Math.abs(delta) <= w.tolValid,
      hit: Math.abs(delta) <= w.tol
    };
  }
  // vx no cruzamento, por diferenca finita da tabela (dx/dt medio nao serve)
  function estimateVxEnd(w, v0) {
    var e = 1.0; // mm/s
    var d1 = w.dxOf(v0 + e), d0 = w.dxOf(v0 - e);
    var t1 = w.tFlight(v0 + e), t0 = w.tFlight(v0 - e);
    // aproxima vx_final por d(dx)/d(t) ao longo da familia; fallback para media
    var num = (d1 - d0), den = (t1 - t0);
    var vAvg = w.dxOf(v0) / Math.max(w.tFlight(v0), 1e-9);
    if (Math.abs(den) < 1e-9) return vAvg;
    var v = num / den;
    if (!isFinite(v) || v * v0 < 0 || Math.abs(v) > Math.abs(v0) * 1.05) return vAvg;
    return v;
  }

  // ============================================================
  // OPORTUNIDADES: raizes de delta(t) = 0 e largura da janela
  // ============================================================
  // from = inicio da janela de busca (s). O padrao de oportunidades NAO e
  // periodico no horizonte quando os dois eixos tem periodos incomensuraveis,
  // entao extrapolar somando o horizonte seria errado: para tempos adiante,
  // busca-se de novo a partir de 'from'.
  function opportunities(w, horizon, coarse, from) {
    horizon = horizon || Math.min(30, Math.max(w.axA.T, w.axB.T) * 10);
    from = from || 0;
    var step = coarse || 0.002;
    var f = function (t) { return evalPress(w, t, 0).delta; };
    var roots = [], t, prev = f(from), prevT = from, cur;
    for (t = from + step; t <= from + horizon; t += step) {
      cur = f(t);
      if (prev === 0) roots.push(prevT);
      else if ((prev < 0) !== (cur < 0)) {
        var a = prevT, b = t, fa = prev, i;
        for (i = 0; i < 60; i++) {
          var mdl = 0.5 * (a + b), fm = f(mdl);
          if ((fa < 0) !== (fm < 0)) b = mdl; else { a = mdl; fa = fm; }
          if (b - a < 1e-7) break;
        }
        roots.push(0.5 * (a + b));
      }
      prev = cur; prevT = t;
    }
    // janelas
    var tol = w.tol, out = [];
    roots.forEach(function (r, idx) {
      var lim = 0.6;
      if (idx > 0) lim = Math.min(lim, (r - roots[idx - 1]) * 0.49);
      if (idx < roots.length - 1) lim = Math.min(lim, (roots[idx + 1] - r) * 0.49);
      var wl = edge(w, r, -1, tol, lim), wr = edge(w, r, +1, tol, lim);
      var ev = evalPress(w, r, 0);
      out.push({
        t: r, wLeft: wl, wRight: wr, width: wl + wr,
        vRel: ev.vRel, v0: ev.v0, xHole: ev.xHole, xBall: ev.xBall,
        tf: ev.tf, dx: ev.dx, tLand: ev.tLand,
        widthClean: edge(w, r, -1, w.tolClean, lim) + edge(w, r, 1, w.tolClean, lim),
        widthValid: edge(w, r, -1, w.tolValid, lim) + edge(w, r, 1, w.tolValid, lim)
      });
    });
    out.horizon = horizon;
    out.from = from;
    out.to = from + horizon;
    out.rate = out.length / horizon;   // oportunidades por segundo
    return out;
  }
  // Peso de cada oportunidade sob a estrategia "pega a proxima que aparecer".
  // O jogador fica pronto num instante uniforme no horizonte e usa a primeira
  // janela dali em diante; logo a chance de cair numa dada oportunidade e
  // proporcional ao INTERVALO que a precede, nao 1/N. Ignorar isso produz
  // divergencia sistematica entre o analitico e o Monte Carlo.
  function oppWeights(opps) {
    var n = opps.length, hor = opps.horizon || 1, from = opps.from || 0, i, wts = [], sum = 0;
    if (!n) return wts;
    for (i = 0; i < n; i++) {
      var g = (i === 0) ? ((opps[0].t - from) + (from + hor - opps[n - 1].t)) : (opps[i].t - opps[i - 1].t);
      g = Math.max(0, g); wts.push(g); sum += g;
    }
    if (sum <= 0) { for (i = 0; i < n; i++) wts[i] = 1 / n; return wts; }
    for (i = 0; i < n; i++) wts[i] /= sum;
    return wts;
  }
  function weightedProb(opps, sigma, bias) {
    var wts = oppWeights(opps), p = 0, i;
    for (i = 0; i < opps.length; i++) p += wts[i] * probWindow(opps[i].wLeft, opps[i].wRight, sigma, bias);
    return p;
  }

  function edge(w, root, dir, tol, lim) {
    var lo = 0, hi = lim, i;
    if (Math.abs(evalPress(w, root + dir * hi, 0).delta) <= tol) return hi;
    for (i = 0; i < 50; i++) {
      var m = 0.5 * (lo + hi);
      if (Math.abs(evalPress(w, root + dir * m, 0).delta) <= tol) lo = m; else hi = m;
      if (hi - lo < 1e-7) break;
    }
    return 0.5 * (lo + hi);
  }

  // ============================================================
  // PROBABILIDADE
  // ============================================================
  // delta_timing ~ N(bias, sigma). Acerta se -wLeft <= delta <= wRight.
  //   p = 1/2 [ erf((wRight - bias)/(sigma*raiz2)) + erf((wLeft + bias)/(sigma*raiz2)) ]
  // Janela simetrica e bias nulo reduzem a formula do briefing:
  //   p = erf( T / (2*sigma*raiz2) )
  function probWindow(wLeft, wRight, sigma, bias) {
    bias = bias || 0;
    if (sigma <= 0) return (bias >= -wLeft && bias <= wRight) ? 1 : 0;
    var s2 = sigma * Math.SQRT2;
    return 0.5 * (U.erf((wRight - bias) / s2) + U.erf((wLeft + bias) / s2));
  }
  function probSym(T, sigma) {
    if (sigma <= 0) return 1;
    return U.erf(T / (2 * sigma * Math.SQRT2));
  }

  // ============================================================
  // SIGMAS: quem manda no erro, a maquina ou o jogador
  // ============================================================
  function sigmas(w, opp, sigmaTimingS) {
    var P = PB.params;
    var vRel = Math.abs(opp.vRel), v0 = Math.abs(opp.v0);
    var sMachineSpec = v0 * w.sigT;                       // mm - formula do briefing
    var sMachineFull = Math.sqrt(
      Math.pow(vRel * w.sigT, 2) +
      Math.pow(P.num('enc.err'), 2) +
      Math.pow(P.num('mech.back'), 2)
    );
    var sPlayer = vRel * sigmaTimingS;                     // mm
    return {
      vRel: vRel, v0: v0, sigT: w.sigT,
      sMachine: sMachineSpec, sMachineFull: sMachineFull, sPlayer: sPlayer,
      ratio: sPlayer / Math.max(sMachineSpec, 1e-12),
      ratioFull: sPlayer / Math.max(sMachineFull, 1e-12)
    };
  }

  // ============================================================
  // PERFIS DE JOGADOR
  // ============================================================
  function profiles() {
    var P = PB.params;
    return [
      { id: 'novice', label: 'iniciante', sigma: P.num('ply.novice') / 1000 },
      { id: 'mid', label: 'médio', sigma: P.num('ply.mid') / 1000 },
      { id: 'pro', label: 'treinado', sigma: P.num('ply.pro') / 1000 }
    ];
  }

  // ============================================================
  // ANALISE DE UMA RODADA
  // ============================================================
  function roundAnalysis(round, horizon) {
    var P = PB.params;
    var w = buildWorld(round);
    var opps = opportunities(w, horizon);
    var bias = P.num('ply.bias') / 1000;
    var strat = P.get('ply.select');

    var rec = {
      round: round, w: w, opps: opps,
      L: w.L, h: w.h, d: w.d,
      solvable: opps.length > 0,
      nOpp: opps.length, oppRate: opps.rate,
      TA: w.axA.T, TB: w.axB.T,
      vPeakA: w.axA.meta.vPeak, vPeakB: w.axB.meta.vPeak,
      warnA: w.axA.meta.warn, warnB: w.axB.meta.warn
    };

    if (!opps.length) {
      rec.reason = 'Nenhum instante de soltura no horizonte de ' + U.fmt(opps.horizon, 1) +
        ' s leva a bola ao buraco. A rodada e INSOLUVEL com estes parametros: o resultado deixa de depender do jogador.';
      rec.probs = {}; profiles().forEach(function (p) { rec.probs[p.id] = 0; });
      return rec;
    }

    // estatistica das janelas entre oportunidades
    var widths = opps.map(function (o) { return o.width; }).sort(function (a, b) { return a - b; });
    rec.widthMin = widths[0];
    rec.widthMax = widths[widths.length - 1];
    rec.widthMed = widths[(widths.length / 2) | 0];
    rec.widthMean = widths.reduce(function (a, b) { return a + b; }, 0) / widths.length;

    var vrels = opps.map(function (o) { return Math.abs(o.vRel); });
    rec.vRelMean = vrels.reduce(function (a, b) { return a + b; }, 0) / vrels.length;
    rec.vRelMin = Math.min.apply(null, vrels);
    rec.vRelMax = Math.max.apply(null, vrels);
    rec.v0Mean = opps.reduce(function (a, o) { return a + Math.abs(o.v0); }, 0) / opps.length;

    // oportunidade representativa: a de janela mediana
    var repIdx = 0, best = 0, bi = 0, k;
    for (k = 0; k < opps.length; k++) {
      if (Math.abs(opps[k].width - rec.widthMed) < Math.abs(opps[repIdx].width - rec.widthMed)) repIdx = k;
      if (opps[k].width > best) { best = opps[k].width; bi = k; }
    }
    rec.rep = opps[repIdx]; rec.bestOpp = opps[bi];

    // janela analitica do briefing, na oportunidade representativa
    rec.T_clean = (w.L - w.d) / Math.abs(rec.rep.vRel);
    rec.T_valid = w.L / Math.abs(rec.rep.vRel);
    rec.T_used = (w.crit === 'conformidade') ? rec.T_valid : rec.T_clean;
    rec.T_num = rec.rep.width;
    rec.T_err = (rec.T_num - rec.T_used) / rec.T_used;

    // probabilidades por perfil, nas duas estrategias
    rec.probs = {}; rec.probsBest = {}; rec.probsNext = {}; rec.probsAnalytic = {};
    rec.sig = {};
    profiles().forEach(function (p) {
      var pn = weightedProb(opps, p.sigma, bias);          // pega a proxima oportunidade
      var pb = probWindow(rec.bestOpp.wLeft, rec.bestOpp.wRight, p.sigma, bias);
      rec.probsNext[p.id] = pn;
      rec.probsBest[p.id] = pb;
      rec.probsAnalytic[p.id] = probSym(rec.T_used, p.sigma);
      rec.probs[p.id] = (strat === 'melhor oportunidade') ? pb : pn;
      rec.sig[p.id] = sigmas(w, rec.rep, p.sigma);
    });
    rec.sigma = rec.sig.pro;   // o perfil que define se a maquina decide
    return rec;
  }

  // ============================================================
  // ANALISE DA ESCADA
  // ============================================================
  function ladderAnalysis(horizon) {
    var lad = PB.params.getLadder();
    var rows = lad.map(function (r) { return roundAnalysis(r, horizon); });
    var cum = {}, profs = profiles();
    profs.forEach(function (p) { cum[p.id] = []; });
    rows.forEach(function (rec, i) {
      profs.forEach(function (p) {
        var prev = i === 0 ? 1 : cum[p.id][i - 1];
        cum[p.id].push(prev * rec.probs[p.id]);
      });
    });
    return { rows: rows, cum: cum, profiles: profs };
  }

  // Cache da analise da escada, invalidado pelo hash do conjunto de parametros.
  var _ladCache = { key: null, val: null };
  function cachedLadder() {
    var k = PB.params.hash();
    if (_ladCache.key === k && _ladCache.val) return _ladCache.val;
    _ladCache.val = ladderAnalysis(); _ladCache.key = k;
    return _ladCache.val;
  }

  // ============================================================
  // CURVA DE APRENDIZADO: vitoria da escada em funcao do sigma
  // ============================================================
  function learningCurve(sigmasMs, horizon) {
    sigmasMs = sigmasMs || [200, 150, 120, 100, 80, 65, 50, 40, 30, 26, 20, 15, 10, 5];
    var lad = PB.params.getLadder();
    var bias = PB.params.num('ply.bias') / 1000;
    var strat = PB.params.get('ply.select');
    var cache = lad.map(function (r) {
      var w = buildWorld(r);
      return { w: w, opps: opportunities(w, horizon) };
    });
    return sigmasMs.map(function (ms) {
      var s = ms / 1000, prod = 1, per = [];
      cache.forEach(function (c) {
        var p;
        if (!c.opps.length) p = 0;
        else if (strat === 'melhor oportunidade') {
          var b = c.opps.reduce(function (x, y) { return y.width > x.width ? y : x; });
          p = probWindow(b.wLeft, b.wRight, s, bias);
        } else {
          p = weightedProb(c.opps, s, bias);
        }
        per.push(p); prod *= p;
      });
      return { sigmaMs: ms, perRound: per, win: prod };
    });
  }

  // ============================================================
  // METRICAS OPERACIONAIS
  // ============================================================
  function opMetrics(mc) {
    var P = PB.params, lad = PB.params.getLadder();
    var TA = P.num('A.T'), TB = P.num('B.T');
    var distA = 0, distB = 0, revA = 0, revB = 0, pMechA = 0, pMechB = 0;
    lad.forEach(function (r) {
      var w = buildWorld(r);
      var ta = w.axA.T, tb = w.axB.T;
      distA += 2 * w.axA.stroke / ta; distB += 2 * w.axB.stroke / tb;
      revA += 2 / ta; revB += 2 / tb;
      pMechA += (P.num('A.mass') / 1000) * Math.pow(w.axA.meta.vPeak / 1000, 2) / ta;
      pMechB += (P.num('B.mass') / 1000) * Math.pow(w.axB.meta.vPeak / 1000, 2) / tb;
    });
    var n = lad.length || 1;
    distA /= n; distB /= n; revA /= n; revB /= n; pMechA /= n; pMechB /= n;

    var pMech = (pMechA + pMechB) / P.num('mot.eff');
    var pTotal = pMech + P.num('elec.base');

    // duracao media: usa rodadas sobrevividas do Monte Carlo se houver
    var perRound = P.num('game.tdec') + P.num('game.treset');
    var res = {
      beltMperHour: (distA + distB) * 3600 / 1000,
      beltAperHour: distA * 3600 / 1000, beltBperHour: distB * 3600 / 1000,
      reversalsPerHour: (revA + revB) * 3600,
      revAperHour: revA * 3600, revBperHour: revB * 3600,
      pMech: pMech, pTotal: pTotal,
      perRoundTime: perRound,
      attract: P.num('game.attract'),
      cycleTime: null, durations: {}
    };
    var profs = profiles();
    profs.forEach(function (p) {
      var rounds = (mc && mc.byProfile && mc.byProfile[p.id]) ? mc.byProfile[p.id].meanRounds : null;
      if (rounds === null) {
        // rodadas jogadas = soma das probabilidades de ALCANCAR cada rodada
        var la = cachedLadder(), prod = 1, i;
        rounds = 0;
        for (i = 0; i < la.rows.length; i++) { rounds += prod; prod *= la.rows[i].probs[p.id]; }
      }
      var dur = rounds * perRound;
      res.durations[p.id] = { rounds: rounds, seconds: dur, energyWh: pTotal * dur / 3600, cost: pTotal * dur / 3600 / 1000 * P.num('eco.kwh') };
    });
    res.throughputPerHour = 3600 / (res.durations.mid.seconds + res.attract);
    return res;
  }

  PB.model = {
    buildWorld: buildWorld, evalPress: evalPress, opportunities: opportunities,
    probWindow: probWindow, probSym: probSym, sigmas: sigmas, profiles: profiles,
    oppWeights: oppWeights, weightedProb: weightedProb,
    roundAnalysis: roundAnalysis, ladderAnalysis: ladderAnalysis, cachedLadder: cachedLadder,
    learningCurve: learningCurve, opMetrics: opMetrics
  };
})(window.PB);
