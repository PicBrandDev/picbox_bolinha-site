/* PICBOX - modo JOGAR: partida real, canvas, log de sessao e replay.
   O relogio da maquina NUNCA para. O clique nao trava os eixos. */
(function (PB) {
  'use strict';
  var U = PB.util, M = PB.model, PH = PB.physics, P = PB.params;

  var G = {
    canvas: null, ctx: null,
    tMachine: 0,          // relogio absoluto da maquina (s), continuo
    lastFrame: 0,
    state: 'attract',     // attract | ready | flight | result | over | won
    round: 0,             // indice 0-based
    roundT0: 0,           // instante absoluto do inicio da rodada
    w: null, opps: null,
    shot: null,           // solturas em andamento
    log: [], logging: true, lastSample: -1,
    result: null, resultUntil: 0,
    cleared: 0, prizeWon: null,
    showAids: true, showTrace: true,
    rnd: U.rng(P.num('sim.seed') ^ 0x5f3a),
    stats: { games: 0, wins: 0 },
    dirty: true
  };

  // ---------------- ciclo de vida ----------------
  function attach(canvas) {
    G.canvas = canvas; G.ctx = canvas.getContext('2d');
    canvas.addEventListener('mousedown', function (e) { e.preventDefault(); press(); });
    canvas.addEventListener('touchstart', function (e) { e.preventDefault(); press(); }, { passive: false });
    window.addEventListener('keydown', function (e) {
      if (e.code === 'Space' || e.code === 'Enter' || e.code === 'NumpadEnter') {
        var tag = (document.activeElement && document.activeElement.tagName) || '';
        if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
        e.preventDefault(); press();
      }
    });
    P.onChange(function () { G.dirty = true; });
    G.lastFrame = performance.now() / 1000;
    requestAnimationFrame(loop);
  }

  // reconfig = true quando a rodada e reconstruida no meio dela porque o operador
  // mexeu num parametro. O log registra isso com evento PROPRIO: duas linhas de
  // 'rodada_inicio' para a mesma rodada quebrariam o agrupamento do replay, e
  // esconder a mudanca quebraria a auditoria.
  function buildRound(reconfig) {
    var lad = P.getLadder();
    var r = lad[Math.min(G.round, lad.length - 1)];
    G.w = M.buildWorld(r);
    G.opps = M.opportunities(G.w, Math.min(12, Math.max(G.w.axA.T, G.w.axB.T) * 6));
    G.roundT0 = G.tMachine;
    G.dirty = false;
    logRow((reconfig ? 'rodada_reconfig#' : 'rodada_inicio#') + (G.round + 1),
      'L=' + G.w.L.toFixed(4) + ';h=' + G.w.h.toFixed(3) +
      ';vmul=' + r.speedMul.toFixed(6) + ';t0_ms=' + Math.round(G.tMachine * 1000));
  }

  function newGame() {
    G.log = []; G.cleared = 0; G.round = 0; G.prizeWon = null; G.shot = null; G.result = null;
    G.stats.games++;
    logRow('partida_inicio', 'hash=' + P.hash() + ';versao=' + P.VERSION + ';criterio=' + P.get('sim.crit'));
    buildRound();
    G.state = 'ready';
  }
  function toAttract() { G.state = 'attract'; G.shot = null; }

  function press() {
    if (G.state === 'attract' || G.state === 'over' || G.state === 'won') { newGame(); return; }
    if (G.state !== 'ready') return;
    var tau = G.tMachine - G.roundT0;
    var jit = P.num('sim.macjit') ? G.rnd.normal(0, G.w.sigT) : 0;
    var ev = M.evalPress(G.w, tau, jit);
    // trajetoria real para animacao
    var fl = PH.flight(Object.assign({}, G.w.flightBase, { vx0: ev.v0 / 1000 }));
    G.shot = {
      ev: ev, jit: jit, tauPress: tau,
      tRelAbs: G.roundT0 + ev.tRel, tLandAbs: G.roundT0 + ev.tRel + fl.t,
      path: fl.path, tf: fl.t, xRel: ev.xRel, logged: false
    };
    G.state = 'flight';
    logRow('botao', 'jitter_ms=' + (jit * 1000).toFixed(4) + ';latencia_ms=' + (G.w.latMean * 1000).toFixed(3) +
      ';t_press_ms=' + (tau * 1000).toFixed(3));
  }

  // Mantem a lista de oportunidades cobrindo o tempo que a faixa mostra.
  // Sem isso, uma rodada longa passaria do horizonte calculado no inicio dela.
  function ensureOpps(tau) {
    if (!G.w) return;
    if (!G.opps || tau + STRIP_SPAN + 0.5 > (G.opps.to || 0) || tau < (G.opps.from || 0)) {
      G.opps = M.opportunities(G.w, STRIP_SPAN * 2, 0.002, Math.max(0, tau - 0.25));
    }
  }
  var STRIP_SPAN = 6.0;

  function loop(nowMs) {
    var now = nowMs / 1000;
    var dt = Math.min(0.05, now - G.lastFrame);
    G.lastFrame = now;
    G.tMachine += dt;

    if (G.dirty && (G.state === 'ready' || G.state === 'attract')) buildRound(G.state === 'ready' && G.log.length > 0);

    if (G.state === 'flight' && G.shot) {
      if (!G.shot.logged && G.tMachine >= G.shot.tRelAbs) {
        G.shot.logged = true;
        logRow('soltura', 'v0_mm_s=' + G.shot.ev.v0.toFixed(4) + ';x_rel_mm=' + G.shot.xRel.toFixed(4) +
          ';tau_ms=' + (G.shot.ev.tRel * 1000).toFixed(4));
      }
      if (G.tMachine >= G.shot.tLandAbs) resolveShot();
    }
    if (G.state === 'result' && G.tMachine >= G.resultUntil) advance();

    ensureOpps(G.tMachine - G.roundT0);
    sampleLog();
    render();
    if (PB.ui && PB.ui.onFrame) PB.ui.onFrame(G);
    requestAnimationFrame(loop);
  }

  function resolveShot() {
    var ev = G.shot.ev;
    logRow('cruzamento', 'delta_mm=' + ev.delta.toFixed(4) + ';v_rel_mm_s=' + ev.vRel.toFixed(4) +
      ';barreira=1');
    var ok = ev.hit;
    var rim = ev.hitValid && !ev.hitClean;
    G.result = { ok: ok, rim: rim, delta: ev.delta, ev: ev };
    logRow(ok ? 'acerto' : 'erro', 'delta_mm=' + ev.delta.toFixed(4) + ';borda=' + (rim ? 1 : 0) +
      ';criterio=' + G.w.crit);
    if (ok) {
      G.cleared++;
      var lad = P.getLadder(), row = lad[G.round];
      if (row && row.prize) G.prizeWon = row.prize;
    }
    G.state = 'result';
    G.resultUntil = G.tMachine + 1.5;
  }

  function advance() {
    var lad = P.getLadder();
    if (!G.result.ok) {
      G.state = 'over';
      logRow('partida_fim', 'rodadas_vencidas=' + G.cleared + ';resultado=derrota');
      return;
    }
    G.round++;
    if (G.round >= lad.length) {
      G.state = 'won'; G.stats.wins++;
      logRow('partida_fim', 'rodadas_vencidas=' + G.cleared + ';resultado=vitoria_total');
      return;
    }
    G.shot = null; G.result = null;
    buildRound();
    G.state = 'ready';
  }

  // ---------------- log de sessao ----------------
  function logRow(evento, sensores) {
    if (!G.logging) return;
    var tau = G.tMachine - G.roundT0;
    var pa = G.w ? G.w.axA.pos(tau) : 0, pb = G.w ? G.w.axB.pos(tau) : 0;
    G.log.push([Math.round(G.tMachine * 1000), evento, +pa.toFixed(3), +pb.toFixed(3), sensores || '']);
  }
  function sampleLog() {
    if (!G.logging || G.state === 'attract' || !G.w) return;
    var ms = Math.floor(G.tMachine * 1000 / 20);
    if (ms === G.lastSample) return;
    G.lastSample = ms;
    var tau = G.tMachine - G.roundT0;
    var barreira = 0;
    if (G.shot && Math.abs(G.tMachine - G.shot.tLandAbs) < 0.01) barreira = 1;
    var s = 'encA=' + Math.round(G.w.axA.pos(tau) * P.num('enc.res')) +
      ';encB=' + Math.round(G.w.axB.pos(tau) * P.num('enc.res')) +
      ';barreira=' + barreira +
      ';estado=' + G.state;
    G.log.push([Math.round(G.tMachine * 1000), 'amostra', +G.w.axA.pos(tau).toFixed(3), +G.w.axB.pos(tau).toFixed(3), s]);
    if (G.log.length > 200000) G.log.splice(0, 50000);
  }
  function logCSV() {
    var rows = [['t_ms', 'evento', 'pos_eixo_A_mm', 'pos_eixo_B_mm', 'estado_sensores']];
    return U.toCSV(rows.concat(G.log));
  }

  // ---------------- replay ----------------
  // Reproduz a partida a partir do log e compara o resultado.
  // Duas reconstrucoes:
  //   (a) a partir do instante de SOLTURA registrado  -> deve bater bit a bit
  //   (b) a partir do instante do BOTAO               -> so bate a menos do jitter
  function replay(csvText) {
    var rows = U.parseCSV(csvText);
    if (!rows.length) throw new Error('Log vazio.');
    var hdr = rows[0].join(';').indexOf('t_ms') >= 0 ? rows.shift() : null;
    var cur = null, out = [], header = {};
    rows.forEach(function (r) {
      var t = +r[0], ev = r[1] || '', sens = r[4] || '';
      var kv = {}; sens.split(';').forEach(function (p2) { var q = p2.split('='); if (q.length === 2) kv[q[0]] = q[1]; });
      if (ev === 'partida_inicio') { header = kv; return; }
      if (ev.indexOf('rodada_inicio') === 0) {
        cur = {
          n: +(ev.split('#')[1] || 1), t0: +kv.t0_ms / 1000,
          L: +kv.L, h: +kv.h, vmul: +kv.vmul, reconfig: 0,
          press: null, rel: null, logged: null, delta: null
        };
        out.push(cur); return;
      }
      if (ev.indexOf('rodada_reconfig') === 0 && cur) {
        cur.t0 = +kv.t0_ms / 1000; cur.L = +kv.L; cur.h = +kv.h; cur.vmul = +kv.vmul;
        cur.reconfig++; cur.press = null; cur.rel = null;
        return;
      }
      if (!cur) return;
      if (ev === 'botao') {
        cur.press = (kv.t_press_ms !== undefined) ? +kv.t_press_ms / 1000 : (t / 1000 - cur.t0);
        cur.jit = (+kv.jitter_ms || 0) / 1000;
      }
      if (ev === 'soltura') { cur.rel = (+kv.tau_ms || 0) / 1000; cur.v0 = +kv.v0_mm_s; }
      if (ev === 'cruzamento') { cur.delta = +kv.delta_mm; }
      if (ev === 'acerto') { cur.logged = true; }
      if (ev === 'erro') { cur.logged = false; }
    });

    var lad = P.getLadder();
    return out.filter(function (r) { return r.press !== null; }).map(function (r) {
      var ladRow = lad[r.n - 1] || { n: r.n, speedMul: r.vmul, L: r.L, h: r.h };
      var w = M.buildWorld({ n: r.n, speedMul: r.vmul, L: r.L, h: r.h });
      var fromRelease = M.evalPress(w, r.rel - w.latMean, 0);   // usa a soltura medida
      var fromButton = M.evalPress(w, r.press, 0);              // ignora o jitter realizado
      return {
        n: r.n, loggedHit: r.logged, loggedDelta: r.delta, reconfig: r.reconfig || 0,
        replayDelta: fromRelease.delta, replayHit: fromRelease.hit,
        buttonDelta: fromButton.delta, buttonHit: fromButton.hit,
        err: Math.abs(fromRelease.delta - r.delta),
        match: (fromRelease.hit === r.logged) && Math.abs(fromRelease.delta - r.delta) < 0.05
      };
    });
  }

  // ---------------- render ----------------
  function render() {
    var c = G.canvas, ctx = G.ctx;
    if (!c) return;
    var dpr = window.devicePixelRatio || 1;
    var cw = c.clientWidth, ch = c.clientHeight;
    if (c.width !== Math.round(cw * dpr) || c.height !== Math.round(ch * dpr)) {
      c.width = Math.round(cw * dpr); c.height = Math.round(ch * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cw, ch);
    if (!G.w) return;

    var w = G.w, tau = G.tMachine - G.roundT0;
    var S = Math.max(w.axA.stroke, w.axB.stroke);
    var mmW = S + 140, mmH = w.h + 210;
    var padL = 14, padT = 10, stripH = 46;
    var s = Math.min((cw - 2 * padL) / mmW, (ch - 2 * padT - stripH) / mmH);
    var ox = Math.max(padL, (cw - mmW * s) / 2);          // centraliza o gabinete
    var oy = Math.max(padT, (ch - stripH - mmH * s) / 2);
    var X = function (xmm) { return ox + (xmm + 70) * s; };
    var Y = function (ymm) { return oy + (ymm + 95) * s; };

    // fundo e gabinete
    ctx.fillStyle = '#0d1117'; ctx.fillRect(0, 0, cw, ch);
    ctx.strokeStyle = '#1e2a38'; ctx.lineWidth = 1;
    var gx0 = X(-70), gx1 = X(S + 70), gy0 = Y(-95), gy1 = Y(w.h + 115);
    ctx.strokeRect(gx0, gy0, gx1 - gx0, gy1 - gy0);
    // grade de 50 mm
    ctx.strokeStyle = 'rgba(120,160,200,0.08)';
    for (var gx = 0; gx <= S; gx += 50) { ctx.beginPath(); ctx.moveTo(X(gx), gy0); ctx.lineTo(X(gx), gy1); ctx.stroke(); }
    for (var gy = 0; gy <= w.h; gy += 50) { ctx.beginPath(); ctx.moveTo(gx0, Y(gy)); ctx.lineTo(gx1, Y(gy)); ctx.stroke(); }

    var posA = w.axA.pos(tau), posB = w.axB.pos(tau);

    // trilhos
    ctx.strokeStyle = '#2b3a4d'; ctx.lineWidth = Math.max(2, 6 * s);
    ctx.beginPath(); ctx.moveTo(X(0), Y(-34)); ctx.lineTo(X(S), Y(-34)); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(X(0), Y(w.h + 30)); ctx.lineTo(X(S), Y(w.h + 30)); ctx.stroke();

    // ---- auxilios de mira (previsao) ----
    var pred = null;
    if (G.state === 'ready') {
      pred = M.evalPress(w, tau, 0);
      if (G.showAids) drawPrediction(ctx, X, Y, s, w, pred);
    }

    // ---- carro B (buraco) ----
    var barHalf = 130;
    ctx.fillStyle = '#31465e';
    var yB = Y(w.h), hB = Math.max(3, 16 * s);
    var lx0 = X(Math.max(-70, posB - barHalf)), lx1 = X(posB - w.L / 2);
    var rx0 = X(posB + w.L / 2), rx1 = X(Math.min(S + 70, posB + barHalf));
    ctx.fillRect(lx0, yB, Math.max(0, lx1 - lx0), hB);
    ctx.fillRect(rx0, yB, Math.max(0, rx1 - rx0), hB);
    // profundidade da boca
    ctx.strokeStyle = 'rgba(90,190,255,0.55)'; ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(X(posB - w.L / 2), yB); ctx.lineTo(X(posB - w.L / 2), Y(w.h + P.num('geo.depth')));
    ctx.moveTo(X(posB + w.L / 2), yB); ctx.lineTo(X(posB + w.L / 2), Y(w.h + P.num('geo.depth')));
    ctx.stroke();
    ctx.fillStyle = 'rgba(90,190,255,0.10)';
    ctx.fillRect(X(posB - w.L / 2), yB, (w.L) * s, P.num('geo.depth') * s);
    // plano da boca
    ctx.strokeStyle = 'rgba(90,190,255,0.30)'; ctx.setLineDash([4, 6]); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(gx0, yB); ctx.lineTo(gx1, yB); ctx.stroke(); ctx.setLineDash([]);

    // ---- carro A + bola ----
    var yA = Y(-34), cw2 = 62 * s;
    ctx.fillStyle = '#3d5675';
    ctx.fillRect(X(posA) - cw2 / 2, yA - Math.max(3, 14 * s), cw2, Math.max(3, 14 * s));
    var ballR = Math.max(3, (w.d / 2) * s);
    if (G.state === 'ready' || G.state === 'attract') {
      drawBall(ctx, X(posA), Y(w.d / 2), ballR);
    } else if (G.shot) {
      var tRel = G.shot.tRelAbs;
      if (G.tMachine < tRel) drawBall(ctx, X(posA), Y(w.d / 2), ballR);
      else {
        var tf = Math.min(G.shot.tf, G.tMachine - tRel);
        var p = samplePath(G.shot.path, tf);
        drawBall(ctx, X(G.shot.xRel + p[0] * 1000), Y(p[1] * 1000 + w.d / 2), ballR);
        if (G.showTrace) {
          ctx.strokeStyle = 'rgba(255,209,102,0.6)'; ctx.lineWidth = 1.5; ctx.beginPath();
          G.shot.path.forEach(function (q, i) {
            if (q[2] > tf) return;
            var px = X(G.shot.xRel + q[0] * 1000), py = Y(q[1] * 1000 + w.d / 2);
            if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
          });
          ctx.stroke();
        }
      }
    }

    // ---- resultado ----
    var midX = cw / 2, midY = (gy0 + gy1) / 2, stageH = ch - stripH;
    if (G.state === 'result' && G.result) {
      ctx.fillStyle = G.result.ok ? 'rgba(60,220,130,0.13)' : 'rgba(255,90,90,0.12)';
      ctx.fillRect(0, 0, cw, stageH);
      ctx.fillStyle = G.result.ok ? '#3cdc82' : '#ff6b6b';
      ctx.font = '600 ' + Math.round(Math.min(30, cw / 22)) + 'px system-ui,sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(G.result.ok ? (G.result.rim ? 'VÁLIDA (tocou a borda)' : 'ACERTO') : 'ERRO', midX, midY);
      ctx.font = '400 ' + Math.round(Math.min(15, cw / 45)) + 'px system-ui,sans-serif';
      ctx.fillStyle = '#c9d4e2';
      ctx.fillText('Δ = ' + U.fmt(G.result.delta, 2) + ' mm   (limite ' + U.fmt(w.tol, 2) + ' mm)', midX, midY + 26);
      ctx.textAlign = 'left';
    }
    if (G.state === 'attract' || G.state === 'over' || G.state === 'won') {
      ctx.fillStyle = 'rgba(8,12,18,0.74)'; ctx.fillRect(0, 0, cw, stageH);
      ctx.textAlign = 'center'; ctx.fillStyle = '#e8eef6';
      ctx.font = '600 ' + Math.round(Math.min(24, cw / 30)) + 'px system-ui,sans-serif';
      var msg = G.state === 'attract' ? 'PICBOX — pressione ESPAÇO ou clique para jogar'
        : (G.state === 'won' ? 'ESCADA COMPLETA — ' + G.cleared + ' rodadas' : 'FIM DE PARTIDA — ' + G.cleared + ' rodadas vencidas');
      ctx.fillText(msg, midX, midY);
      ctx.font = '400 13px system-ui,sans-serif'; ctx.fillStyle = '#93a4b8';
      ctx.fillText(G.state === 'attract' ? 'os eixos continuam em movimento durante toda a partida'
        : 'espaço/clique para nova partida', midX, midY + 26);
      ctx.textAlign = 'left';
    }

    // ---- faixa de oportunidades (janela de acerto no tempo) ----
    drawStrip(ctx, cw, ch - stripH + 6, cw - 28, stripH - 12, 14, tau);

    // ---- cotas ----
    ctx.fillStyle = '#7f8ea3'; ctx.font = '11px ui-monospace,Consolas,monospace';
    ctx.fillText('h = ' + U.fmt(w.h, 0) + ' mm', X(0) + 6, Y(w.h / 2));
    ctx.textAlign = 'center';
    ctx.fillText('L = ' + U.fmt(w.L, 1) + ' mm', X(posB), Y(w.h + P.num('geo.depth')) + 16);
    ctx.textAlign = 'left';
    ctx.strokeStyle = 'rgba(127,142,163,0.5)'; ctx.setLineDash([2, 4]);
    ctx.beginPath(); ctx.moveTo(X(0), Y(0)); ctx.lineTo(X(0), Y(w.h)); ctx.stroke(); ctx.setLineDash([]);
  }

  function drawBall(ctx, px, py, r) {
    var gr = ctx.createRadialGradient(px - r * 0.35, py - r * 0.35, r * 0.15, px, py, r);
    gr.addColorStop(0, '#fff3cf'); gr.addColorStop(1, '#f0a500');
    ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(px, py, r, 0, 6.2832); ctx.fill();
    ctx.strokeStyle = 'rgba(0,0,0,0.35)'; ctx.lineWidth = 1; ctx.stroke();
  }

  function drawPrediction(ctx, X, Y, s, w, pred) {
    // trajetoria prevista
    var fl = PH.flight(Object.assign({}, w.flightBase, { vx0: pred.v0 / 1000 }));
    ctx.strokeStyle = pred.hit ? 'rgba(60,220,130,0.75)' : 'rgba(120,170,255,0.5)';
    ctx.setLineDash([5, 5]); ctx.lineWidth = 1.5; ctx.beginPath();
    fl.path.forEach(function (q, i) {
      var px = X(pred.xRel + q[0] * 1000), py = Y(q[1] * 1000 + w.d / 2);
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    });
    ctx.stroke(); ctx.setLineDash([]);

    // buraco fantasma: onde ele ESTARA no instante do cruzamento
    var xg = pred.xHole, yB = Y(w.h);
    ctx.strokeStyle = 'rgba(90,190,255,0.85)'; ctx.setLineDash([3, 3]); ctx.lineWidth = 1.5;
    ctx.strokeRect(X(xg - w.L / 2), yB - 6, w.L * s, 12);
    ctx.setLineDash([]);
    // janela de acerto (tolerancia) ao redor do fantasma
    ctx.fillStyle = pred.hit ? 'rgba(60,220,130,0.22)' : 'rgba(255,120,120,0.16)';
    ctx.fillRect(X(xg - w.tol), yB - 5, 2 * w.tol * s, 10);

    // pouso projetado
    ctx.fillStyle = pred.hit ? '#3cdc82' : '#ff7b7b';
    var xl = X(pred.xBall);
    ctx.beginPath(); ctx.moveTo(xl, yB - 14); ctx.lineTo(xl - 6, yB - 26); ctx.lineTo(xl + 6, yB - 26); ctx.closePath(); ctx.fill();
    ctx.font = '10px ui-monospace,Consolas,monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Δ ' + U.fmt(pred.delta, 1) + ' mm', xl, yB - 30);
    ctx.textAlign = 'left';
  }

  // faixa temporal com as janelas de acerto das proximas oportunidades
  function drawStrip(ctx, cw, y, wpx, hpx, padL, tau) {
    if (!G.opps) return;
    var span = STRIP_SPAN;
    ctx.fillStyle = '#0a0f16'; ctx.fillRect(padL, y, wpx, hpx);
    ctx.strokeStyle = '#1e2a38'; ctx.strokeRect(padL, y, wpx, hpx);
    var px = function (t) { return padL + (t - tau) / span * wpx; };
    ctx.save();
    ctx.beginPath(); ctx.rect(padL, y, wpx, hpx); ctx.clip();
    G.opps.forEach(function (o) {
      if (o.t < tau - 0.3 || o.t > tau + span) return;
      var a = px(o.t - o.wLeft), b = px(o.t + o.wRight);
      ctx.fillStyle = 'rgba(60,220,130,0.35)';
      ctx.fillRect(a, y + 6, Math.max(1.5, b - a), hpx - 12);
      ctx.strokeStyle = '#3cdc82'; ctx.beginPath();
      ctx.moveTo(px(o.t), y + 3); ctx.lineTo(px(o.t), y + hpx - 3); ctx.stroke();
    });
    ctx.restore();
    ctx.strokeStyle = '#ffd166'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(padL, y + hpx); ctx.stroke(); ctx.lineWidth = 1;
    ctx.fillStyle = '#ffd166'; ctx.font = '10px ui-monospace,Consolas,monospace';
    ctx.fillText('agora', padL + 4, y + 12);
    ctx.fillStyle = '#7f8ea3';
    ctx.textAlign = 'right';
    ctx.fillText('faixa verde = janela de acerto  ·  horizonte +' + span.toFixed(0) + ' s', padL + wpx - 6, y + hpx - 5);
    ctx.textAlign = 'left';
  }

  function samplePath(path, t) {
    var i;
    for (i = 1; i < path.length; i++) {
      if (path[i][2] >= t) {
        var f = (t - path[i - 1][2]) / Math.max(1e-9, path[i][2] - path[i - 1][2]);
        return [U.lerp(path[i - 1][0], path[i][0], f), U.lerp(path[i - 1][1], path[i][1], f)];
      }
    }
    return path[path.length - 1];
  }

  PB.game = {
    G: G, attach: attach, newGame: newGame, press: press, toAttract: toAttract,
    logCSV: logCSV, replay: replay,
    setAids: function (v) { G.showAids = v; },
    setLogging: function (v) { G.logging = v; }
  };
})(window.PB);
