/* PICBOX - Monte Carlo.
   Cada partida e uma escada: erra, acabou. A UNICA fonte de aleatoriedade que
   decide o resultado e o erro humano de timing. O sorteio de qual oportunidade
   o jogador pega define o DESAFIO, nunca o vencedor.
   O jitter da maquina so entra se explicitamente ligado (sim.mcjit). */
(function (PB) {
  'use strict';
  var U = PB.util, M = PB.model;

  function prepare(horizon) {
    var lad = PB.params.getLadder();
    return lad.map(function (r) {
      var w = M.buildWorld(r);
      var opps = M.opportunities(w, horizon);
      return { round: r, w: w, opps: opps, horizon: opps.horizon };
    });
  }

  function run(opts, onProgress, onDone) {
    opts = opts || {};
    var P = PB.params;
    var N = opts.N || P.num('sim.mcN');
    var seed = opts.seed || P.num('sim.seed');
    var useMacJit = opts.machineJitter !== undefined ? opts.machineJitter : !!P.num('sim.mcjit');
    var bias = P.num('ply.bias') / 1000;
    var strat = P.get('ply.select');
    var stages = prepare(opts.horizon);
    var profs = M.profiles();
    var nR = stages.length;

    var out = {
      N: N, seed: seed, machineJitter: useMacJit, strategy: strat,
      rounds: nR, byProfile: {}, stages: stages,
      startedAt: U.nowStamp(), paramHash: P.hash()
    };
    profs.forEach(function (p) {
      out.byProfile[p.id] = {
        label: p.label, sigmaMs: p.sigma * 1000,
        attempts: new Array(nR).fill(0), hits: new Array(nR).fill(0),
        reached: new Array(nR).fill(0), cleared: new Array(nR).fill(0),
        finishHist: new Array(nR + 1).fill(0),
        deltas: [], meanRounds: 0, winAll: 0,
        rimOnly: new Array(nR).fill(0)
      };
    });

    var pi = 0, gi = 0;
    var rnd = U.rng(seed);

    function step(budgetMs) {
      var t0 = performance.now();
      while (pi < profs.length) {
        var prof = profs[pi], acc = out.byProfile[prof.id];
        while (gi < N) {
          playOne(prof, acc, rnd, stages, bias, strat, useMacJit);
          gi++;
          if ((gi & 63) === 0 && performance.now() - t0 > budgetMs) return false;
        }
        gi = 0; pi++;
      }
      return true;
    }

    function finish() {
      profs.forEach(function (p) {
        var a = out.byProfile[p.id], i, sum = 0;
        a.hitRate = a.attempts.map(function (n, i2) { return n ? a.hits[i2] / n : 0; });
        a.reachRate = a.reached.map(function (n) { return n / N; });
        a.clearRate = a.cleared.map(function (n) { return n / N; });
        a.winAll = a.cleared[nR - 1] / N;
        for (i = 0; i <= nR; i++) sum += i * a.finishHist[i];
        a.meanRounds = a.attempts.reduce(function (x, y) { return x + y; }, 0) / N;
        a.meanCleared = sum / N;
        var d = a.deltas;
        if (d.length) {
          var m = d.reduce(function (x, y) { return x + y; }, 0) / d.length;
          var v = d.reduce(function (x, y) { return x + (y - m) * (y - m); }, 0) / Math.max(1, d.length - 1);
          a.deltaMean = m; a.deltaSd = Math.sqrt(v);
        }
        a.deltas = null; // nao guardar amostra bruta
      });
      out.finishedAt = U.nowStamp();
      onDone(out);
    }

    function pump() {
      var done = step(30);
      var total = profs.length * N, cur = pi * N + gi;
      if (onProgress) onProgress(Math.min(1, cur / total));
      if (done) finish(); else setTimeout(pump, 0);
    }
    pump();
    return out;
  }

  function playOne(prof, acc, rnd, stages, bias, strat, useMacJit) {
    var lvl, cleared = 0;
    for (lvl = 0; lvl < stages.length; lvl++) {
      var st = stages[lvl];
      acc.reached[lvl]++;
      acc.attempts[lvl]++;
      if (!st.opps.length) break;      // rodada insoluvel: perde sempre

      var opp;
      if (strat === 'melhor oportunidade') {
        // jogador conhece a maquina: espera a janela mais larga do horizonte
        opp = st.opps.reduce(function (a, b) { return b.width > a.width ? b : a; });
      } else {
        // sorteio do DESAFIO: instante em que o jogador fica pronto -> proxima janela
        var tReady = rnd() * st.horizon;
        opp = st.opps.filter(function (o) { return o.t >= tReady; })[0] || st.opps[0];
      }
      var dTiming = rnd.normal(bias, prof.sigma);            // erro humano
      var jit = useMacJit ? rnd.normal(0, st.w.sigT) : 0;     // jitter da maquina (opcional)
      var ev = M.evalPress(st.w, opp.t + dTiming, jit);
      acc.deltas.push(ev.delta);
      if (!ev.hit) {
        if (ev.hitValid && !ev.hitClean) acc.rimOnly[lvl]++;
        break;
      }
      if (ev.hitValid && !ev.hitClean) acc.rimOnly[lvl]++;
      acc.hits[lvl]++; acc.cleared[lvl]++; cleared++;
    }
    acc.finishHist[cleared]++;
  }

  PB.mc = { run: run, prepare: prepare };
})(window.PB);
