/* PICBOX - varredura de parametros (modo ENGENHARIA).
   Dado um intervalo para uma ou duas grandezas, tabula janela de acerto,
   probabilidade por perfil, vitoria da escada e razao sigma_jogador/sigma_maquina.
   Executa em fatias para nao travar a interface. */
(function (PB) {
  'use strict';
  var U = PB.util, M = PB.model, P = PB.params;

  function axisValues(spec) {
    var out = [], i, n = Math.max(1, spec.steps | 0);
    if (n === 1) return [spec.from];
    for (i = 0; i < n; i++) out.push(spec.from + (spec.to - spec.from) * i / (n - 1));
    return out;
  }

  function run(cfg, onProgress, onDone) {
    var vx = axisValues(cfg.x);
    var vy = cfg.y && cfg.y.key ? axisValues(cfg.y) : [null];
    var saved = {};
    saved[cfg.x.key] = P.get(cfg.x.key);
    if (cfg.y && cfg.y.key) saved[cfg.y.key] = P.get(cfg.y.key);

    var results = [], ix = 0, iy = 0;
    var total = vx.length * vy.length;
    var targetRound = cfg.round || 1;

    function one(xv, yv) {
      P.set(cfg.x.key, xv, true);
      if (cfg.y && cfg.y.key) P.set(cfg.y.key, yv, true);
      P.rebuildLadder();
      var la = M.ladderAnalysis(cfg.horizon);
      var idx = Math.min(la.rows.length - 1, Math.max(0, targetRound - 1));
      var r = la.rows[idx];
      var row = {
        x: xv, y: yv,
        solvable: r.solvable,
        T_ms: r.solvable ? r.T_used * 1000 : 0,
        Tnum_ms: r.solvable ? r.T_num * 1000 : 0,
        vRel: r.solvable ? r.vRelMean : 0,
        opps: r.solvable ? r.oppRate * 60 : 0,
        widthMin_ms: r.solvable ? r.widthMin * 1000 : 0,
        sigPlayer: r.solvable ? r.sig.pro.sPlayer : 0,
        sigMachine: r.solvable ? r.sig.pro.sMachine : 0,
        ratio: r.solvable ? r.sig.pro.ratio : 0,
        pNov: r.probs.novice, pMid: r.probs.mid, pPro: r.probs.pro,
        winNov: la.cum.novice[la.rows.length - 1],
        winMid: la.cum.mid[la.rows.length - 1],
        winPro: la.cum.pro[la.rows.length - 1]
      };
      results.push(row);
    }

    function pump() {
      var t0 = performance.now();
      while (ix < vx.length) {
        while (iy < vy.length) {
          one(vx[ix], vy[iy]);
          iy++;
          if (performance.now() - t0 > 40) { report(); setTimeout(pump, 0); return; }
        }
        iy = 0; ix++;
      }
      // restaura
      Object.keys(saved).forEach(function (k) { P.set(k, saved[k], true); });
      P.rebuildLadder();
      if (onProgress) onProgress(1);
      onDone({
        cfg: cfg, rows: results, xs: vx, ys: vy,
        xKey: cfg.x.key, yKey: cfg.y && cfg.y.key ? cfg.y.key : null,
        round: targetRound, generated: U.nowStamp()
      });
    }
    function report() { if (onProgress) onProgress((ix * vy.length + iy) / total); }
    pump();
  }

  PB.sweep = { run: run, axisValues: axisValues };
})(window.PB);
