/* PICBOX - interface. Painel de parametros, abas e renderizacao dos resultados. */
(function (PB) {
  'use strict';
  var U = PB.util, P = PB.params, M = PB.model, PH = PB.physics;
  var el = U.el, $ = U.$, $$ = U.$$;

  var state = { mc: null, sweep: null, lastCalc: 0, pane: 'jogar', recalcTimer: null };

  // =====================================================================
  // PAINEL DE PARAMETROS
  // =====================================================================
  function buildPanel() {
    var host = $('#paramPanel'); host.innerHTML = '';
    P.groups().forEach(function (g, gi) {
      var items = P.schema().filter(function (d) { return d.g === g; });
      var nEst = items.filter(function (d) { return P.stat(d.k) === 'est'; }).length;
      var body = el('div', { class: 'grpBody' });
      var head = el('div', { class: 'grpHead' }, [
        el('span', { class: 'caret', text: '▸' }),
        el('span', { text: g }),
        el('span', { class: 'cnt', text: nEst + ' est/' + items.length })
      ]);
      var box = el('div', { class: 'grp' + (gi < 2 ? ' open' : '') }, [head, body]);
      head.querySelector('.caret').textContent = gi < 2 ? '▾' : '▸';
      head.addEventListener('click', function () {
        box.classList.toggle('open');
        head.querySelector('.caret').textContent = box.classList.contains('open') ? '▾' : '▸';
      });
      items.forEach(function (d) { body.appendChild(paramRow(d)); });
      host.appendChild(box);
    });
  }

  function paramRow(d) {
    var wrap = el('div', { class: 'p' });
    var flag = el('button', { class: 'flag ' + P.stat(d.k), text: flagText(d.k) });
    if (d.s !== 'def') {
      flag.title = 'Clique para alternar entre estimado e medido em bancada';
      flag.addEventListener('click', function () {
        P.setStat(d.k, P.stat(d.k) === 'med' ? 'est' : 'med');
        flag.className = 'flag ' + P.stat(d.k); flag.textContent = flagText(d.k);
        buildPanelCounts(); scheduleRecalc();
      });
    } else flag.title = 'Valor definido pelo projeto (não é medição)';

    wrap.appendChild(el('div', { class: 'pTop' }, [
      el('span', { class: 'pLbl', text: d.l }),
      el('span', { class: 'pUnit', text: d.u }),
      flag
    ]));

    var row = el('div', { class: 'pRow' });
    if (d.t === 'sel') {
      var sel = el('select');
      d.o.forEach(function (o) {
        var op = el('option', { value: o, text: String(o) });
        if (String(P.get(d.k)) === String(o)) op.selected = true;
        sel.appendChild(op);
      });
      sel.addEventListener('change', function () { P.set(d.k, sel.value); scheduleRecalc(); });
      row.appendChild(sel);
    } else if (d.t === 'txt') {
      var tx = el('input', { type: 'text', value: P.get(d.k) });
      tx.addEventListener('input', function () { P.set(d.k, tx.value); scheduleRecalc(); });
      row.appendChild(tx);
    } else if (d.t === 'bool') {
      var lbl = el('label', { class: 'flexline mini' });
      var cb = el('input', { type: 'checkbox' }); cb.checked = !!P.num(d.k);
      cb.addEventListener('change', function () { P.set(d.k, cb.checked ? 1 : 0); scheduleRecalc(); });
      lbl.appendChild(cb); lbl.appendChild(document.createTextNode(cb.checked ? ' ativado' : ' desativado'));
      cb.addEventListener('change', function () { lbl.lastChild.textContent = cb.checked ? ' ativado' : ' desativado'; });
      row.appendChild(lbl);
    } else {
      var rng = el('input', { type: 'range', min: d.min, max: d.max, step: d.step, value: P.num(d.k) });
      var num = el('input', { type: 'number', min: d.min, max: d.max, step: d.step, value: P.num(d.k) });
      rng.addEventListener('input', function () { num.value = rng.value; P.set(d.k, rng.value); scheduleRecalc(); });
      num.addEventListener('input', function () { rng.value = num.value; P.set(d.k, num.value); scheduleRecalc(); });
      row.appendChild(rng); row.appendChild(num);
      wrap.__sync = function () { rng.value = P.num(d.k); num.value = P.num(d.k); };
    }
    wrap.appendChild(row);
    if (d.n) wrap.appendChild(el('div', { class: 'pNote', text: d.n }));
    wrap.__flag = function () { flag.className = 'flag ' + P.stat(d.k); flag.textContent = flagText(d.k); };
    return wrap;
  }
  function flagText(k) {
    var s = P.stat(k);
    return s === 'med' ? 'MEDIDO' : (s === 'def' ? 'definido' : 'estimado');
  }
  function buildPanelCounts() {
    $$('.grp').forEach(function (box, i) {
      var g = P.groups()[i];
      var items = P.schema().filter(function (d) { return d.g === g; });
      var nEst = items.filter(function (d) { return P.stat(d.k) === 'est'; }).length;
      box.querySelector('.cnt').textContent = nEst + ' est/' + items.length;
    });
  }

  function scheduleRecalc() {
    clearTimeout(state.recalcTimer);
    state.recalcTimer = setTimeout(function () { refreshAll(); }, 180);
  }

  // =====================================================================
  // BADGES
  // =====================================================================
  function refreshBadges(la) {
    var r = la.rows[0];
    var bw = $('#badgeWindow'), bd = $('#badgeDrag'), br = $('#badgeRatio'), bh = $('#badgeHash');
    bh.querySelector('b').textContent = P.hash();
    if (!r.solvable) {
      bw.className = 'badge bad'; bw.querySelector('b').textContent = 'INSOLÚVEL';
      br.className = 'badge bad'; br.querySelector('b').textContent = '—';
      return;
    }
    bw.className = 'badge';
    bw.querySelector('b').textContent = U.fmt(r.T_used * 1000, 1) + ' ms';

    var drag = PH.dragProof(Object.assign({}, r.w.flightBase, { vx0: r.v0Mean / 1000, drag: true }));
    var negl = Math.abs(drag.ddx * 1000) < 0.05 * Math.max(1e-9, r.L - r.d);
    bd.className = 'badge ' + (negl ? 'ok' : 'warn');
    bd.querySelector('b').textContent = U.pct(drag.ratio, 1) + (negl ? ' (desprezível)' : ' (relevante)');
    state.drag = drag;

    var worst = la.rows.reduce(function (a, x) {
      if (!x.solvable) return 0;
      return Math.min(a, x.sig.pro.ratio);
    }, Infinity);
    br.className = 'badge ' + (worst < 4 ? 'bad' : (worst < 6 ? 'warn' : 'ok'));
    br.querySelector('b').textContent = U.fmt(worst, 2) + (worst < 4 ? '  A MÁQUINA DECIDE' : '');
    br.title = 'Menor razão da escada (perfil treinado). Abaixo de 4 a dispersão da máquina é ' +
      'comparável à do jogador e o resultado deixa de medir habilidade.';
  }

  // =====================================================================
  // ABA JOGAR
  // =====================================================================
  var frameCount = 0, fpsT = 0;
  function onFrame(G) {
    frameCount++;
    var now = performance.now();
    if (now - fpsT > 1000) { $('#fpsLbl').textContent = frameCount + ' fps'; frameCount = 0; fpsT = now; }
    if (state.pane !== 'jogar') return;
    if (now - state.lastCalc < 120) return;
    state.lastCalc = now;
    renderHud(G);
  }

  function renderHud(G) {
    if (!G.w) return;
    var w = G.w, tau = G.tMachine - G.roundT0;
    var pred = M.evalPress(w, tau, 0);
    var lad = P.getLadder();

    var st = { attract: 'attract', ready: 'aguardando soltura', flight: 'bola em voo', result: 'resultado', over: 'fim de partida', won: 'escada completa' }[G.state];
    $('#hudGame').innerHTML = kv([
      ['estado', st],
      ['rodada', (G.round + 1) + ' / ' + lad.length],
      ['rodadas vencidas', G.cleared],
      ['relógio da máquina', U.fmt(G.tMachine, 2) + ' s'],
      ['partidas nesta sessão', G.stats.games + ' (vitórias: ' + G.stats.wins + ')'],
      ['prêmio liberado', G.prizeWon ? U.esc(G.prizeWon.name) : '—']
    ]);

    var opp = G.opps && G.opps.length ? G.opps.filter(function (o) { return o.t >= tau; })[0] || G.opps[0] : null;
    var sig = opp ? M.sigmas(w, opp, P.num('ply.mid') / 1000) : null;
    $('#hudRound').innerHTML = kv([
      ['abertura L', U.fmt(w.L, 2) + ' mm'],
      ['altura de queda h', U.fmt(w.h, 1) + ' mm'],
      ['posição eixo A', U.fmt(w.axA.pos(tau), 1) + ' mm'],
      ['velocidade eixo A', U.fmt(w.axA.vel(tau), 1) + ' mm/s'],
      ['posição eixo B', U.fmt(w.axB.pos(tau), 1) + ' mm'],
      ['velocidade eixo B', U.fmt(w.axB.vel(tau), 1) + ' mm/s'],
      ['SEP'],
      ['se soltar agora: Δ', spanC(U.fmt(pred.delta, 2) + ' mm', pred.hit ? 'ok' : 'bad')],
      ['tempo de queda', U.fmt(pred.tf * 1000, 1) + ' ms'],
      ['avanço horizontal', U.fmt(pred.dx, 1) + ' mm'],
      ['v relativa no cruzamento', U.fmt(pred.vRel, 1) + ' mm/s'],
      ['SEP'],
      ['próxima janela em', opp ? U.fmt(Math.max(0, opp.t - tau), 2) + ' s' : '—'],
      ['largura da janela', opp ? U.fmt(opp.width * 1000, 1) + ' ms' : '—'],
      ['σ jogador / σ máquina', sig ? spanC(U.fmt(sig.ratio, 2), sig.ratio < 4 ? 'bad' : 'ok') : '—']
    ]);

    var la = M.cachedLadder();
    var rows = lad.map(function (r, i) {
      var rec = la.rows[i];
      var cls = i === G.round ? 'style="background:rgba(78,163,255,.10)"' : '';
      return '<tr ' + cls + '><td>' + r.n + '</td><td>' + U.fmt(r.L, 1) + '</td><td>' +
        U.fmt(r.speedMul, 2) + '</td><td>' + (rec.solvable ? U.fmt(rec.T_used * 1000, 1) : '—') + '</td><td>' +
        U.fmt(rec.probs.mid, 3) + '</td><td>' + (r.prize ? U.esc(r.prize.name) : '—') + '</td></tr>';
    }).join('');
    $('#hudLadder').innerHTML = '<table class="tbl"><thead><tr><th>#</th><th>L mm</th><th>vel×</th><th>T ms</th><th>p médio</th><th>prêmio</th></tr></thead><tbody>' + rows + '</tbody></table>';

    renderLiveCalc(w, pred, opp);
    $('#logCount').textContent = G.log.length + ' linhas no log';
  }

  function renderLiveCalc(w, pred, opp) {
    var g = P.num('env.g'), h = w.h / 1000;
    var tAn = Math.sqrt(2 * h / g);
    var sigMid = P.num('ply.mid') / 1000;
    var T = w.L / Math.abs(pred.vRel || 1e-9);
    var Tc = Math.max(0, w.L - w.d) / Math.abs(pred.vRel || 1e-9);
    var Tu = w.crit === 'conformidade' ? T : Tc;
    var p = M.probSym(Tu, sigMid);
    var sigT = w.sigT;
    var out = [
      f('Tempo de queda livre', 't = √(2h/g) = √(2 · ' + U.fmt(h, 4) + ' m / ' + U.fmt(g, 5) + ' m/s²) = ' +
        U.fmt(tAn * 1000, 2) + ' ms', 'com arrasto e v_y0, integrado: ' + U.fmt(pred.tf * 1000, 2) + ' ms'),
      f('Avanço horizontal no ar', 'dx = v_soltura · t = ' + U.fmt(pred.v0, 1) + ' mm/s · ' +
        U.fmt(pred.tf, 4) + ' s = ' + U.fmt(pred.v0 * pred.tf, 1) + ' mm',
        'integrado com arrasto: ' + U.fmt(pred.dx, 1) + ' mm  (diferença ' + U.fmt(pred.dx - pred.v0 * pred.tf, 2) + ' mm)'),
      f('Velocidade relativa no cruzamento', 'v_rel = v_bola,x − v_buraco = ' + U.fmt(pred.vBallX, 1) +
        ' − (' + U.fmt(pred.vHole, 1) + ') = ' + U.fmt(pred.vRel, 1) + ' mm/s', ''),
      f('Janela de acerto temporal', 'T = (L − d)/|v_rel| = (' + U.fmt(w.L, 1) + ' − ' + U.fmt(w.d, 1) +
        ')/' + U.fmt(Math.abs(pred.vRel), 1) + ' = ' + U.fmt(Tc * 1000, 2) + ' ms   [passagem limpa]',
        'conformidade (centro na boca): T = L/|v_rel| = ' + U.fmt(T * 1000, 2) + ' ms · ' +
        'janela numérica medida: ' + (opp ? U.fmt(opp.width * 1000, 2) + ' ms' : '—')),
      f('Probabilidade de acerto (jogador médio)', 'p = erf( T / (2σ√2) ) = erf( ' + U.fmt(Tu, 5) +
        ' / (2 · ' + U.fmt(sigMid, 4) + ' · √2) ) = ' + U.fmt(p, 4), ''),
      f('Erro posicional da MÁQUINA', 'σ_máquina = v_soltura · jitter_total = ' + U.fmt(Math.abs(pred.v0), 1) +
        ' mm/s · ' + U.fmt(sigT * 1000, 3) + ' ms = ' + U.fmt(Math.abs(pred.v0) * sigT, 3) + ' mm',
        'jitter_total = √(jit_soltura² + jit_eletrônico² + T_varredura²/12)'),
      f('Erro posicional do JOGADOR', 'σ_jogador = v_rel · σ_timing = ' + U.fmt(Math.abs(pred.vRel), 1) +
        ' mm/s · ' + U.fmt(sigMid * 1000, 1) + ' ms = ' + U.fmt(Math.abs(pred.vRel) * sigMid, 2) + ' mm', ''),
      f('Razão de habilidade', 'R = σ_jogador / σ_máquina = ' +
        U.fmt((Math.abs(pred.vRel) * sigMid) / Math.max(1e-12, Math.abs(pred.v0) * sigT), 2),
        'R < 4 → a máquina decide. Este número é o critério que separa jogo de habilidade de sorteio.')
    ];
    $('#liveCalc').innerHTML = out.join('');
  }
  function f(title, formula, note) {
    return '<div style="margin-bottom:8px"><div class="mini" style="color:var(--fg2)">' + title +
      '</div><div class="formula">' + formula + '</div>' +
      (note ? '<div class="mini">' + note + '</div>' : '') + '</div>';
  }
  function kv(pairs) {
    return '<div class="kv">' + pairs.map(function (p) {
      if (p[0] === 'SEP') return '<div class="sep"></div>';
      return '<div class="k">' + p[0] + '</div><div class="v">' + p[1] + '</div>';
    }).join('') + '</div>';
  }
  function spanC(txt, cls) { return '<span class="' + cls + '" style="color:var(--' + (cls === 'ok' ? 'ok' : 'bad') + ')">' + txt + '</span>'; }

  // =====================================================================
  // ABA MONTE CARLO
  // =====================================================================
  function runMC() {
    var N = +$('#mcN').value, seed = +$('#mcSeed').value, jit = $('#mcJit').checked;
    $('#btnRunMC').disabled = true;
    $('#mcProg').textContent = 'executando…';
    PB.mc.run({ N: N, seed: seed, machineJitter: jit },
      function (p) { $('#mcProg').textContent = 'executando… ' + U.pct(p, 0); },
      function (res) {
        state.mc = res; $('#btnRunMC').disabled = false;
        $('#mcProg').textContent = 'concluído — ' + res.N + ' partidas/perfil';
        renderMC();
      });
  }

  function renderMC() {
    var host = $('#mcOut'); host.innerHTML = '';
    var mc = state.mc;
    if (!mc) { host.innerHTML = '<div class="card"><div class="note">Nenhuma execução ainda.</div></div>'; return; }
    var la = M.cachedLadder();

    var head = ['perfil', 'σ (ms)', 'rodadas médias', 'escada completa (MC)', 'analítico', 'divergência', 'erro estat. 1/√N'];
    var rows = M.profiles().map(function (p) {
      var a = mc.byProfile[p.id], an = la.cum[p.id][la.rows.length - 1];
      var dv = Math.abs(a.winAll - an);
      return [a.label, U.fmt(a.sigmaMs, 1), U.fmt(a.meanRounds, 2), U.pct(a.winAll, 3), U.pct(an, 3),
        { html: U.fmt(dv, 5), cls: dv > 3 / Math.sqrt(mc.N) ? 'warnc' : 'ok' }, U.fmt(1 / Math.sqrt(mc.N), 4)];
    });
    var c1 = el('div', { class: 'card' }, [
      el('h3', { html: 'Resultado <span class="sub">N = ' + mc.N + ' por perfil, semente ' + mc.seed +
        ', jitter da máquina ' + (mc.machineJitter ? 'incluído' : 'excluído') + '</span>' }),
      U.table(head, rows)
    ]);
    host.appendChild(c1);

    // por rodada
    var hdr = ['rodada'], body = [];
    M.profiles().forEach(function (p) { hdr.push('acerto ' + p.label, 'alcance ' + p.label, 'acum. ' + p.label); });
    var i;
    for (i = 0; i < mc.rounds; i++) {
      var line = [i + 1];
      M.profiles().forEach(function (p) {
        var a = mc.byProfile[p.id];
        line.push(U.pct(a.hitRate[i], 1), U.pct(a.reachRate[i], 1), U.pct(a.clearRate[i], 2));
      });
      body.push(line);
    }
    host.appendChild(el('div', { class: 'card' }, [
      el('h3', { html: 'Taxas por nível da escada' }),
      el('div', { class: 'scroll' }, [U.table(hdr, body)]),
      el('div', { class: 'note', text: 'Acerto = taxa condicional de vencer a rodada dado que chegou nela. Alcance = fração das partidas que chegaram na rodada. Acumulada = fração das partidas que venceram até essa rodada.' })
    ]));

    // distribuicao final
    var dh = ['perfil'], dr = [];
    for (i = 0; i <= mc.rounds; i++) dh.push(i + ' rod.');
    M.profiles().forEach(function (p) {
      var a = mc.byProfile[p.id], line = [a.label];
      for (i = 0; i <= mc.rounds; i++) line.push(U.pct(a.finishHist[i] / mc.N, 1));
      dr.push(line);
    });
    host.appendChild(el('div', { class: 'card' }, [
      el('h3', { html: 'Distribuição de rodadas vencidas' }),
      el('div', { class: 'scroll' }, [U.table(dh, dr)])
    ]));

    // curva de aprendizado
    var lc = M.learningCurve();
    host.appendChild(el('div', { class: 'card' }, [
      el('h3', { html: 'Curva de aprendizado <span class="sub">vitória da escada em função do σ de timing</span>' }),
      curveSVG(lc),
      U.table(['σ (ms)', 'P(vitória)', 'p rodada 1', 'p última'],
        lc.map(function (r) {
          return [r.sigmaMs, U.pct(r.win, 4), U.fmt(r.perRound[0], 4), U.fmt(r.perRound[r.perRound.length - 1], 4)];
        })),
      el('div', { class: 'note', text: 'A curva é monotônica decrescente em σ: reduzir o desvio de timing sempre aumenta a taxa de vitória. É essa monotonicidade que caracteriza a máquina como de habilidade.' })
    ]));
  }

  function curveSVG(lc) {
    var W = 560, H = 180, pad = 34;
    var xs = lc.map(function (r) { return r.sigmaMs; });
    var xmin = Math.min.apply(null, xs), xmax = Math.max.apply(null, xs);
    var ymax = Math.max.apply(null, lc.map(function (r) { return r.win; })) || 1;
    var X = function (v) { return pad + (Math.log(v) - Math.log(xmin)) / (Math.log(xmax) - Math.log(xmin) || 1) * (W - pad - 10); };
    var Y = function (v) { return H - pad - (v / ymax) * (H - pad - 12); };
    var pts = lc.slice().sort(function (a, b) { return a.sigmaMs - b.sigmaMs; })
      .map(function (r) { return X(r.sigmaMs) + ',' + Y(r.win); }).join(' ');
    var marks = [P.num('ply.novice'), P.num('ply.mid'), P.num('ply.pro')];
    var names = ['inic.', 'médio', 'trein.'];
    var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" style="width:100%;height:190px">';
    s += '<rect x="0" y="0" width="' + W + '" height="' + H + '" fill="#0a0f16" stroke="#223143"/>';
    s += '<polyline points="' + pts + '" fill="none" stroke="#4ea3ff" stroke-width="2"/>';
    marks.forEach(function (m, i) {
      if (m < xmin || m > xmax) return;
      s += '<line x1="' + X(m) + '" y1="12" x2="' + X(m) + '" y2="' + (H - pad) + '" stroke="#ffc857" stroke-dasharray="3 3" opacity=".7"/>';
      s += '<text x="' + (X(m) + 3) + '" y="22" fill="#ffc857" font-size="10">' + names[i] + ' ' + m + 'ms</text>';
    });
    s += '<line x1="' + pad + '" y1="' + (H - pad) + '" x2="' + (W - 10) + '" y2="' + (H - pad) + '" stroke="#2d3f56"/>';
    s += '<line x1="' + pad + '" y1="12" x2="' + pad + '" y2="' + (H - pad) + '" stroke="#2d3f56"/>';
    s += '<text x="' + pad + '" y="' + (H - 12) + '" fill="#6c7f95" font-size="10">σ = ' + xmin + ' ms</text>';
    s += '<text x="' + (W - 90) + '" y="' + (H - 12) + '" fill="#6c7f95" font-size="10">σ = ' + xmax + ' ms</text>';
    s += '<text x="4" y="20" fill="#6c7f95" font-size="10">' + U.pct(ymax, 1) + '</text>';
    s += '</svg>';
    var d = el('div'); d.innerHTML = s; return d;
  }

  // =====================================================================
  // ABA ENGENHARIA
  // =====================================================================
  function fillSweepSelects() {
    var nums = P.schema().filter(function (d) { return !d.t || d.t === undefined; });
    var xs = $('#swXKey'), ys = $('#swYKey');
    xs.innerHTML = ''; ys.innerHTML = '<option value="">— nenhum —</option>';
    nums.forEach(function (d) {
      var t = d.g + ' · ' + d.l + ' (' + d.u + ')';
      xs.appendChild(el('option', { value: d.k, text: t }));
      ys.appendChild(el('option', { value: d.k, text: t }));
    });
    xs.value = 'geo.h'; ys.value = 'geo.L';
    syncSweepRange('x'); syncSweepRange('y');
    xs.addEventListener('change', function () { syncSweepRange('x'); });
    ys.addEventListener('change', function () { syncSweepRange('y'); });
  }
  function syncSweepRange(ax) {
    var k = $('#sw' + ax.toUpperCase() + 'Key').value;
    if (!k) { $('#sw' + ax.toUpperCase() + 'From').value = ''; $('#sw' + ax.toUpperCase() + 'To').value = ''; return; }
    var d = P.def(k), v = P.num(k);
    $('#sw' + ax.toUpperCase() + 'From').value = +Math.max(d.min, v * 0.6).toFixed(4);
    $('#sw' + ax.toUpperCase() + 'To').value = +Math.min(d.max, v * 1.6).toFixed(4);
  }
  function runSweep() {
    var cfg = {
      x: { key: $('#swXKey').value, from: +$('#swXFrom').value, to: +$('#swXTo').value, steps: +$('#swXN').value },
      round: +$('#swRound').value
    };
    if ($('#swYKey').value) cfg.y = { key: $('#swYKey').value, from: +$('#swYFrom').value, to: +$('#swYTo').value, steps: +$('#swYN').value };
    $('#btnRunSweep').disabled = true;
    PB.sweep.run(cfg, function (p) { $('#swProg').textContent = 'varrendo… ' + U.pct(p, 0); },
      function (res) {
        state.sweep = res; $('#btnRunSweep').disabled = false;
        $('#swProg').textContent = res.rows.length + ' combinações';
        renderSweep(); refreshAll();
      });
  }
  function renderSweep() {
    var host = $('#swOut'); host.innerHTML = '';
    var sw = state.sweep;
    if (!sw) { host.innerHTML = '<div class="card"><div class="note">Nenhuma varredura executada.</div></div>'; return; }
    var metric = $('#swMetric').value;
    var dx = P.def(sw.xKey), dy = sw.yKey ? P.def(sw.yKey) : null;

    if (sw.yKey) {
      var vals = sw.rows.map(function (r) { return r[metric]; });
      var mn = Math.min.apply(null, vals), mx = Math.max.apply(null, vals);
      var hdr = [dx.l + ' \\ ' + dy.l].concat(sw.ys.map(function (y) { return U.fmt(y, 3); }));
      var body = sw.xs.map(function (x) {
        var line = [U.fmt(x, 3)];
        sw.ys.forEach(function (y) {
          var r = sw.rows.filter(function (q) { return q.x === x && q.y === y; })[0];
          if (!r) { line.push(''); return; }
          var v = r[metric];
          var f2 = (mx - mn) > 0 ? (v - mn) / (mx - mn) : 0.5;
          var col = heat(f2);
          var flagBad = !r.solvable || (metric === 'ratio' && v < 4);
          line.push({
            html: '<span style="display:block;background:' + col + ';color:#04070b;font-weight:600;padding:1px 3px;border-radius:2px">' +
              (r.solvable ? U.fmt(v, metric.indexOf('p') === 0 || metric.indexOf('win') === 0 ? 4 : 2) : 'INSOL') + '</span>',
            cls: flagBad ? 'bad' : ''
          });
        });
        return line;
      });
      host.appendChild(el('div', { class: 'card' }, [
        el('h3', { html: 'Mapa: ' + $('#swMetric').selectedOptions[0].textContent + ' <span class="sub">linhas = ' + dx.l + ' (' + dx.u + '), colunas = ' + dy.l + ' (' + dy.u + ')</span>' }),
        el('div', { class: 'scroll' }, [U.table(hdr, body)]),
        el('div', { class: 'note', text: 'Faixa: ' + U.fmt(mn, 4) + ' a ' + U.fmt(mx, 4) + '. Células marcadas INSOL são combinações em que a rodada analisada não tem nenhum instante de soltura que acerte.' })
      ]));
    }

    var hdr2 = [dx.l + ' (' + dx.u + ')'];
    if (dy) hdr2.push(dy.l + ' (' + dy.u + ')');
    hdr2 = hdr2.concat(['solúvel', 'T anal. (ms)', 'T num. (ms)', 'janela mín (ms)', 'v_rel (mm/s)', 'oport./min',
      'σ jog (mm)', 'σ máq (mm)', 'razão', 'p inic.', 'p médio', 'p trein.', 'P escada trein.']);
    var body2 = sw.rows.map(function (r) {
      var line = [U.fmt(r.x, 4)];
      if (dy) line.push(U.fmt(r.y, 4));
      return line.concat([
        { html: r.solvable ? 'sim' : 'NÃO', cls: r.solvable ? '' : 'bad' },
        U.fmt(r.T_ms, 2), U.fmt(r.Tnum_ms, 2), U.fmt(r.widthMin_ms, 2), U.fmt(r.vRel, 0), U.fmt(r.opps, 1),
        U.fmt(r.sigPlayer, 2), U.fmt(r.sigMachine, 3),
        { html: U.fmt(r.ratio, 2), cls: r.ratio < 4 ? 'bad' : 'ok' },
        U.fmt(r.pNov, 4), U.fmt(r.pMid, 4), U.fmt(r.pPro, 4), U.fmt(r.winPro, 5)
      ]);
    });
    host.appendChild(el('div', { class: 'card' }, [
      el('h3', { html: 'Tabela completa <span class="sub">rodada ' + sw.round + ' · ' + sw.generated + '</span>' }),
      el('div', { class: 'scroll' }, [U.table(hdr2, body2)])
    ]));
  }
  function heat(f) {
    var r = Math.round(255 * Math.min(1, 2 * f)), g = Math.round(255 * Math.min(1, 2 * (1 - f)));
    return 'rgb(' + Math.round(60 + 0.6 * (255 - r)) + ',' + Math.round(60 + 0.7 * g) + ',' + Math.round(120 - 60 * f) + ')';
  }

  function renderEng(la) {
    // arrasto
    var r = la.rows[0];
    var d = state.drag || PH.dragProof(Object.assign({}, r.w.flightBase, { vx0: r.v0Mean / 1000, drag: true }));
    var mag = PH.magnusProof(Object.assign({}, r.w.flightBase, { vx0: r.v0Mean / 1000 }));
    var negl = Math.abs(d.ddx * 1000) < 0.05 * Math.max(1e-9, r.L - r.d);
    $('#dragOut').innerHTML =
      '<div class="formula">Re = ρ·v·d/μ = ' + U.fmt(P.num('env.rho'), 3) + ' · ' + U.fmt(d.vImpact, 3) +
      ' · ' + U.fmt(r.d / 1000, 4) + ' / ' + U.fmt(P.num('env.mu'), 8) + ' = ' + U.fmt(d.Re, 0) + '</div>' +
      '<div class="formula">F_d = ½·ρ·Cd·A·v² = ' + U.fmt(d.Fd * 1000, 4) + ' mN     peso m·g = ' +
      U.fmt(d.W * 1000, 4) + ' mN     F_d/W = ' + U.pct(d.ratio, 3) + '</div>' +
      kv([
        ['regime', d.regime],
        ['área frontal A = πd²/4', U.fmt(d.A * 1e6, 2) + ' mm²'],
        ['velocidade no cruzamento', U.fmt(d.vImpact, 3) + ' m/s'],
        ['SEP'],
        ['t sem arrasto (analítico √(2h/g))', U.fmt(d.tAnalytic * 1000, 4) + ' ms'],
        ['t sem arrasto (RK4)', U.fmt(d.tNoDrag * 1000, 4) + ' ms'],
        ['t com arrasto (RK4)', U.fmt(d.tDrag * 1000, 4) + ' ms'],
        ['dx sem arrasto', U.fmt(d.dxNoDrag * 1000, 3) + ' mm'],
        ['dx com arrasto', U.fmt(d.dxDrag * 1000, 3) + ' mm'],
        ['diferença no pouso', U.fmt(d.ddx * 1000, 3) + ' mm'],
        ['diferença / abertura útil', U.pct(Math.abs(d.ddx * 1000) / Math.max(1e-9, r.L - r.d), 2)]
      ]) +
      '<div class="alert ' + (negl ? 'ok' : 'warn') + '">' + (negl
        ? 'Arrasto DESPREZÍVEL nesta geometria: desloca o pouso em ' + U.fmt(Math.abs(d.ddx * 1000), 3) +
        ' mm, menos de 5 % da abertura útil (' + U.fmt(r.L - r.d, 1) + ' mm). A parábola simples serve para projeto — com este erro registrado.'
        : 'Arrasto NÃO desprezível: desloca o pouso em ' + U.fmt(Math.abs(d.ddx * 1000), 3) + ' mm, ' +
        U.pct(Math.abs(d.ddx * 1000) / Math.max(1e-9, r.L - r.d), 1) + ' da abertura útil. Usar a parábola simples introduz erro sistemático dessa ordem.') +
      '</div>' +
      '<div class="note">Magnus com spin de ' + U.fmt(P.num('rel.spin'), 1) + ' rad/s: C_L ≈ ' + U.fmt(mag.Cl, 3) +
      ', força = ' + U.pct(mag.ratio, 3) + ' do peso, desloca o pouso em ' + U.fmt(mag.ddx * 1000, 3) +
      ' mm. Momento de inércia I = k·m·r² = ' + U.fmt(mag.I * 1e7, 3) + '×10⁻⁷ kg·m²; energia de rotação = ' +
      U.pct(mag.Erot / Math.max(1e-12, mag.Etrans), 3) + ' da energia de translação.</div>';

    // perfis
    var ax = [['A', r.w.axA], ['B', r.w.axB]];
    $('#axisOut').innerHTML = ax.map(function (a) {
      var m = a[1].meta;
      return '<div style="margin-bottom:10px"><b>Eixo ' + a[0] + '</b> — perfil ' + m.profile +
        '<div class="formula">' + m.formula + '</div>' +
        kv([
          ['curso útil S', U.fmt(m.S, 1) + ' mm'],
          ['período (rodada 1)', U.fmt(m.T, 3) + ' s'],
          ['velocidade média = 2S/T', U.fmt(m.vMean, 1) + ' mm/s'],
          ['velocidade de pico', U.fmt(m.vPeak, 1) + ' mm/s'],
          ['aceleração de pico', isFinite(m.aPeak) ? U.fmt(m.aPeak, 0) + ' mm/s²' : 'infinita'],
          ['jerk de pico', isFinite(m.jerkPeak) ? U.fmt(m.jerkPeak, 0) + ' mm/s³' : (isNaN(m.jerkPeak) ? 'não definido (tabela)' : 'infinito')]
        ]) +
        (m.jerkNote ? '<div class="note">' + m.jerkNote + '</div>' : '') +
        (m.warn ? '<div class="alert warn">' + m.warn + '</div>' : '') + '</div>';
    }).join('');

    // operacional
    var op = M.opMetrics(state.mc);
    state.op = op;
    $('#opOut').innerHTML = kv([
      ['correia — eixo A', U.fmt(op.beltAperHour, 1) + ' m/h'],
      ['correia — eixo B', U.fmt(op.beltBperHour, 1) + ' m/h'],
      ['correia — total', U.fmt(op.beltMperHour, 1) + ' m/h'],
      ['inversões — eixo A', U.fmt(op.revAperHour, 0) + ' /h'],
      ['inversões — eixo B', U.fmt(op.revBperHour, 0) + ' /h'],
      ['SEP'],
      ['potência mecânica (2 eixos, c/ rendimento)', U.fmt(op.pMech, 1) + ' W'],
      ['potência total estimada', U.fmt(op.pTotal, 1) + ' W'],
      ['tempo de attract', U.fmt(op.attract, 0) + ' s'],
      ['vazão (perfil médio)', U.fmt(op.throughputPerHour, 1) + ' partidas/h'],
      ['SEP']
    ].concat(M.profiles().map(function (p) {
      var dd = op.durations[p.id];
      return ['duração média — ' + p.label, U.fmt(dd.seconds, 1) + ' s (' + U.fmt(dd.rounds, 2) + ' rodadas, ' +
        U.fmt(dd.energyWh, 3) + ' Wh, R$ ' + U.fmt(dd.cost, 4) + ')'];
    }))) +
      '<div class="note">Distância e inversões dimensionam correia, polia e rolamento. ' +
      'Uma correia GT2 a ' + U.fmt(op.beltMperHour, 0) + ' m/h acumula ' +
      U.fmt(op.beltMperHour * 10 * 30 / 1000, 1) + ' km por mês em operação de 10 h/dia.</div>';
  }

  // =====================================================================
  // TESTES DE SANIDADE
  // =====================================================================
  function selfTest() {
    var out = [], la = M.cachedLadder();
    function t(name, ok, detail) { out.push({ name: name, ok: ok, detail: detail }); }

    // 1. erf
    t('erf(0,5) = 0,5204999 (referência)', Math.abs(U.erf(0.5) - 0.5204998778) < 2e-7,
      'obtido ' + U.fmt(U.erf(0.5), 9));
    t('erf(0) = 0 e erf(4) ≈ 1', Math.abs(U.erf(0)) < 1e-12 && Math.abs(U.erf(4) - 1) < 1e-6, '');

    // 2. RK4 sem arrasto = analitico
    var w = la.rows[0].w;
    var noDrag = PH.flight(Object.assign({}, w.flightBase, { vx0: 0.3, drag: false, magnus: false, vy0: 0 }));
    var an = PH.freeFall(w.h / 1000, P.num('env.g'), 0);
    t('RK4 sem arrasto reproduz t = √(2h/g)', Math.abs(noDrag.t - an.t) < 1e-5,
      'Δt = ' + U.fmt(Math.abs(noDrag.t - an.t) * 1e6, 3) + ' µs');
    t('RK4 sem arrasto reproduz dx = v·t', Math.abs(noDrag.dx - 0.3 * an.t) * 1000 < 0.01,
      'Δdx = ' + U.fmt(Math.abs(noDrag.dx - 0.3 * an.t) * 1e6, 3) + ' µm');

    // 3. tabela de voo
    t('Erro da tabela de voo < 0,01 mm', w.ft.interpErrMm < 0.01, U.fmt(w.ft.interpErrMm, 5) + ' mm');

    // 4. jogador perfeito vence sempre
    var perfect = la.rows.every(function (r) {
      if (!r.solvable) return false;
      return r.opps.every(function (o) { return M.evalPress(r.w, o.t, 0).hit; });
    });
    t('Jogador perfeito (σ = 0) acerta em TODAS as oportunidades de TODAS as rodadas', perfect,
      perfect ? 'nenhuma rodada depende de sorte' : 'há rodada insolúvel ou janela inconsistente');

    // 5. eixos dentro do curso
    var okAx = true, i;
    for (i = 0; i <= 500; i++) {
      var tt = i * w.axA.T / 500;
      var pa = w.axA.pos(tt), pb = w.axB.pos(tt * w.axB.T / w.axA.T);
      if (pa < -1e-6 || pa > w.axA.stroke + 1e-6 || pb < -1e-6 || pb > w.axB.stroke + 1e-6) okAx = false;
    }
    t('Posição dos eixos permanece dentro do curso útil', okAx, '');

    // 6. determinismo do RNG
    var a1 = U.rng(1234), a2 = U.rng(1234), same = true;
    for (i = 0; i < 500; i++) if (a1() !== a2()) same = false;
    t('RNG determinístico com a mesma semente', same, 'mesma semente → mesma sequência');

    // 7. monotonicidade da curva de aprendizado
    var lc = M.learningCurve([200, 120, 65, 26, 10]);
    var mono = true;
    for (i = 1; i < lc.length; i++) if (lc[i].win < lc[i - 1].win - 1e-12) mono = false;
    t('Curva de aprendizado monotônica (menor σ → mais vitória)', mono,
      lc.map(function (r) { return r.sigmaMs + 'ms:' + U.fmt(r.win, 4); }).join('  '));

    // 8. probabilidade coerente
    var pr = M.probSym(0.05, 0.05 / 2 / Math.SQRT2 / 1);
    t('p = erf(T/(2σ√2)) em [0,1] e crescente em T',
      M.probSym(0.02, 0.05) < M.probSym(0.06, 0.05) && M.probSym(1e9, 0.05) <= 1, '');

    // 9. replay determinístico (log corrente, se houver)
    var lg = PB.game.G.log;
    if (lg.length > 20) {
      try {
        var rep = PB.game.replay(PB.game.logCSV());
        var okR = rep.length > 0 && rep.every(function (x) { return x.match; });
        t('Replay do log reproduz o resultado da partida', okR,
          rep.length + ' rodadas verificadas, erro máx = ' +
          U.fmt(Math.max.apply(null, rep.map(function (x) { return x.err; })), 5) + ' mm');
      } catch (e) { t('Replay do log', false, e.message); }
    } else {
      out.push({ name: 'Replay do log', ok: null, detail: 'jogue uma partida para habilitar este teste' });
    }

    // 10. hash estável
    var h1 = P.hash(), h2 = P.hash();
    t('Hash do conjunto é estável e reprodutível', h1 === h2, h1);

    $('#testOut').innerHTML = '<table class="tbl"><thead><tr><th>verificação</th><th>resultado</th><th>detalhe</th></tr></thead><tbody>' +
      out.map(function (o) {
        return '<tr><td>' + o.name + '</td><td class="' + (o.ok === null ? 'warnc' : (o.ok ? 'ok' : 'bad')) + '">' +
          (o.ok === null ? 'n/d' : (o.ok ? 'PASSOU' : 'FALHOU')) + '</td><td>' + (o.detail || '') + '</td></tr>';
      }).join('') + '</tbody></table>';
  }

  // =====================================================================
  // ABA ECONOMIA
  // =====================================================================
  function renderPrizes() {
    var host = $('#prizeTable'); host.innerHTML = '';
    var prizes = P.getPrizes(), lad = P.getLadder();
    var t = el('table', { class: 'tbl' });
    t.innerHTML = '<thead><tr><th>prêmio</th><th>custo unitário (R$)</th><th>nível que libera</th><th>procedência</th><th></th></tr></thead>';
    var tb = el('tbody');
    prizes.forEach(function (pz, i) {
      var tr = el('tr');
      var nm = el('input', { type: 'text', value: pz.name, style: 'width:100%;background:var(--bg);border:1px solid var(--line2);border-radius:3px;padding:2px 4px' });
      var ct = el('input', { type: 'number', step: '0.01', min: '0', value: pz.cost, style: 'width:90px;background:var(--bg);border:1px solid var(--line2);border-radius:3px;padding:2px 4px' });
      var lv = el('input', { type: 'number', step: '1', min: '1', max: String(lad.length), value: pz.level, style: 'width:60px;background:var(--bg);border:1px solid var(--line2);border-radius:3px;padding:2px 4px' });
      var fl = el('button', { class: 'flag ' + (pz.s === 'med' ? 'med' : 'est'), text: pz.s === 'med' ? 'MEDIDO' : 'estimado' });
      var rm = el('button', { class: 'btn sm', text: '×' });
      nm.addEventListener('input', function () { pz.name = nm.value; P.syncPrizes(); scheduleRecalc(); });
      ct.addEventListener('input', function () { pz.cost = +ct.value; P.syncPrizes(); scheduleRecalc(); });
      lv.addEventListener('input', function () { pz.level = +lv.value; P.syncPrizes(); scheduleRecalc(); });
      fl.addEventListener('click', function () {
        pz.s = pz.s === 'med' ? 'est' : 'med';
        fl.className = 'flag ' + (pz.s === 'med' ? 'med' : 'est');
        fl.textContent = pz.s === 'med' ? 'MEDIDO' : 'estimado'; scheduleRecalc();
      });
      rm.addEventListener('click', function () { prizes.splice(i, 1); P.setPrizes(prizes); renderPrizes(); refreshAll(); });
      [nm, ct, lv, fl, rm].forEach(function (x) { tr.appendChild(el('td', {}, [x])); });
      tb.appendChild(tr);
    });
    t.appendChild(tb); host.appendChild(t);
  }

  function renderEco(la) {
    var op = state.op || M.opMetrics(state.mc);
    var eco = PB.economy.compute(la, op);
    state.eco = eco;
    var host = $('#ecoOut'); host.innerHTML = '';

    host.appendChild(el('div', { class: 'card' }, [
      el('h3', { html: 'Probabilidade de liberar cada prêmio' }),
      U.table(['prêmio', 'nível', 'custo R$', 'P iniciante', 'P médio', 'P treinado', 'custo esp. trein. R$'],
        eco.prizes.map(function (e) {
          return [U.esc(e.name), e.level, U.fmt(e.cost, 2), U.pct(e.p.novice, 4), U.pct(e.p.mid, 4),
          { html: U.pct(e.p.pro, 4), cls: 'warnc' }, U.fmt(e.expected.pro, 4)];
        })),
      el('div', { class: 'note', text: 'P(liberar) = produto das probabilidades de vencer todas as rodadas até o nível do prêmio.' })
    ]));

    var alertCls = eco.alert ? 'bad' : 'ok';
    host.appendChild(el('div', { class: 'card' }, [
      el('h3', { html: 'Custo esperado por jogada, por perfil' }),
      U.table(['perfil', 'custo esperado R$', '% da receita', 'energia R$', 'margem R$', 'margem %'],
        M.profiles().map(function (p) {
          var b = eco.byProfile[p.id];
          var isPro = p.id === 'pro';
          return [b.label + (isPro ? '  ← dimensiona' : ''), U.fmt(b.expectedPrizeCost, 4),
          { html: U.pct(b.costPctOfRevenue, 2), cls: (isPro && eco.alert) ? 'bad' : '' },
          U.fmt(b.energyCost, 4),
          { html: U.fmt(b.margin, 3), cls: b.margin < 0 ? 'bad' : 'ok' },
          U.pct(b.marginPct, 1)];
        })),
      el('div', { class: 'alert ' + alertCls, html: (eco.alert ? '<b>ALERTA:</b> ' : '') + eco.alertText }),
      eco.alert ? el('div', { class: 'note', text: 'Preço mínimo da jogada para respeitar o teto no perfil treinado: R$ ' + U.fmt(eco.minPrice, 2) + '. Alternativas: reduzir o custo do prêmio do nível mais alto, ou alongar a escada acima do nível que libera o prêmio caro.' }) : null,
      el('div', { class: 'note', text: 'O perfil treinado é quem farma a máquina. Dimensionar pelo jogador médio é o erro clássico: funciona até alguém aprender a jogar.' })
    ]));

    host.appendChild(el('div', { class: 'card' }, [
      el('h3', { html: 'Operação diária <span class="sub">mix de público: ' + U.pct(eco.mix.novice, 0) + ' / ' + U.pct(eco.mix.mid, 0) + ' / ' + U.pct(eco.mix.pro, 0) + '</span>' }),
      el('div', { html: kv([
        ['receita bruta por dia', 'R$ ' + U.fmt(eco.revenueDay, 2)],
        ['custo de prêmio (mix)', 'R$ ' + U.fmt(eco.prizeCostDayBlended, 2)],
        ['custo de prêmio (só treinados)', 'R$ ' + U.fmt(eco.prizeCostDayPro, 2)],
        ['custo de energia', 'R$ ' + U.fmt(eco.energyDay, 2)],
        ['SEP'],
        ['margem por jogada (mix)', 'R$ ' + U.fmt(eco.blendedMargin, 3)],
        ['margem por dia (mix)', 'R$ ' + U.fmt(eco.marginDayBlended, 2)]
      ]) }),
      eco.mixSum !== 100 ? el('div', { class: 'alert warn', text: 'O mix de público soma ' + eco.mixSum + ' %, não 100 %. Os pesos foram normalizados para o cálculo.' }) : null
    ]));
  }

  // =====================================================================
  // ABA CATALOGO
  // =====================================================================
  function renderCat(la) {
    var r = la.rows[0];
    var v0 = r.solvable ? r.v0Mean : 500, vRel = r.solvable ? r.vRelMean : 500;
    var tbls = PB.catalog.impactTable(v0, vRel);
    var host = $('#catOut'); host.innerHTML = '';
    var cur = PB.catalog.sigPosFor(null, v0, vRel);
    tbls.forEach(function (t) {
      var rows = t.rows.map(function (o) {
        var btn = '<button class="btn sm ' + (o.selected ? 'pri' : '') + '" data-cat="' + t.cat.id + '" data-idx="' + o.idx + '">' +
          (o.selected ? 'selecionado' : 'selecionar') + '</button>';
        var delta = o.spec - cur.spec;
        return [U.esc(o.opt.name), o.opt.jitter, U.fmt(o.opt.cost, 2),
          U.fmt(o.sigT * 1000, 3),
          { html: U.fmt(o.spec, 3), cls: o.spec > cur.spec ? 'bad' : 'ok' },
          { html: (delta >= 0 ? '+' : '') + U.fmt(delta, 3), cls: delta > 0 ? 'bad' : (delta < 0 ? 'ok' : '') },
          { html: btn }, U.esc(o.opt.obs)];
      });
      var card = el('div', { class: 'card' }, [
        el('h3', { html: t.cat.label + ' <span class="sub">' + t.cat.note + '</span>' }),
        U.table(['opção', 'jitter/erro típico', 'custo R$', 'σ_t cadeia (ms)', 'σ_máquina (mm)', 'Δ vs atual', '', 'observação'], rows)
      ]);
      host.appendChild(card);
    });
    host.appendChild(el('div', { class: 'card' }, [
      el('h3', { html: 'Cadeia resultante' }),
      el('div', { html: kv([
        ['jitter total da cadeia (1σ)', U.fmt(cur.sigT * 1000, 3) + ' ms'],
        ['latência média input→soltura', U.fmt(r.w.latMean * 1000, 2) + ' ms'],
        ['σ_máquina (fórmula do briefing: v_soltura · jitter)', U.fmt(cur.spec, 3) + ' mm'],
        ['σ_máquina (completo: + encoder + folga)', U.fmt(cur.full, 3) + ' mm'],
        ['σ_jogador (treinado)', U.fmt(vRel * P.num('ply.pro') / 1000, 2) + ' mm'],
        ['razão', U.fmt((vRel * P.num('ply.pro') / 1000) / Math.max(1e-9, cur.spec), 2)]
      ]) }),
      el('div', { class: 'note', text: 'A coluna σ_máquina mostra o efeito da opção mantendo o resto do conjunto. Trocar o mecanismo de soltura costuma ser a intervenção de maior impacto por real investido.' })
    ]));
    $$('#catOut button[data-cat]').forEach(function (b) {
      b.addEventListener('click', function () {
        PB.catalog.select(b.getAttribute('data-cat'), +b.getAttribute('data-idx'));
        buildPanel(); refreshAll();
        toast('Componente aplicado ao conjunto de parâmetros.');
      });
    });
  }

  // =====================================================================
  // ABA LOG / REPLAY
  // =====================================================================
  function doReplay(csv) {
    try {
      var rep = PB.game.replay(csv);
      var host = $('#replayOut'); host.innerHTML = '';
      if (!rep.length) { host.innerHTML = '<div class="card"><div class="note">Nenhuma soltura encontrada no log.</div></div>'; return; }
      var allOk = rep.every(function (r) { return r.match; });
      host.appendChild(el('div', { class: 'card' }, [
        el('h3', { html: 'Replay <span class="sub">' + rep.length + ' rodadas reconstruídas</span>' }),
        U.table(['rodada', 'Δ no log (mm)', 'Δ do replay pela soltura (mm)', 'erro (mm)', 'resultado log', 'resultado replay',
          'Δ reconstruído só pelo botão (mm)', 'confere'],
          rep.map(function (r) {
            return [r.n, U.fmt(r.loggedDelta, 3), U.fmt(r.replayDelta, 3), U.fmt(r.err, 5),
              r.loggedHit ? 'acerto' : 'erro', r.replayHit ? 'acerto' : 'erro',
              U.fmt(r.buttonDelta, 3),
            { html: r.match ? 'SIM' : 'NÃO', cls: r.match ? 'ok' : 'bad' }];
          })),
        el('div', { class: 'alert ' + (allOk ? 'ok' : 'bad'), html: allOk
          ? 'Todas as rodadas foram reproduzidas a partir do log com erro abaixo de 0,05 mm. A partida é auditável: o log basta para refazer o resultado.'
          : 'Alguma rodada não reproduziu. Isso indica que o log não contém informação suficiente ou que houve mudança de parâmetros entre a partida e o replay.' }),
        el('div', { class: 'note', text: 'A coluna "reconstruído só pelo botão" ignora o jitter realizado da cadeia. A diferença entre ela e a coluna do replay pela soltura é exatamente o quanto a máquina moveu o resultado sem o jogador participar.' })
      ]));
    } catch (e) {
      $('#replayOut').innerHTML = '<div class="card"><div class="alert bad">Falha no replay: ' + e.message + '</div></div>';
    }
  }

  // =====================================================================
  // ABA AUDITORIA
  // =====================================================================
  function renderAud(la) {
    var est = P.estimated(), med = P.measured();
    var worst = la.rows.reduce(function (a, x) { return Math.min(a, x.solvable ? x.sig.pro.ratio : 0); }, Infinity);
    $('#audSummary').innerHTML = kv([
      ['data/hora', U.nowStamp()],
      ['versão do conjunto', P.VERSION],
      ['hash do conjunto', P.hash()],
      ['parâmetros estimados', est.length + ' de ' + P.schema().length],
      ['parâmetros medidos', med.length],
      ['menor razão σ_jogador/σ_máquina', U.fmt(worst, 2) + (worst < 4 ? '  ← REPROVADO' : '')],
      ['Monte Carlo disponível', state.mc ? (state.mc.N + ' partidas/perfil') : 'não executado'],
      ['P(escada) treinado', U.pct(la.cum.pro[la.rows.length - 1], 4)]
    ]) + (state.mc ? '' : '<div class="alert warn">Rode o Monte Carlo antes de emitir o relatório final: sem ele a seção 7 sai vazia.</div>');

    $('#formulaOut').innerHTML = PB.report.FORMULAS.map(function (f2) {
      return '<div style="margin-bottom:6px"><div class="mini" style="color:var(--fg2)">' + f2[0] +
        '</div><div class="formula">' + f2[1] + '</div><div class="mini">' + f2[2] + '</div></div>';
    }).join('');

    $('#limitOut').innerHTML =
      '<div class="alert warn">Os resultados desta ferramenta dependem de medição em bancada. ' +
      est.length + ' parâmetros permanecem estimados.</div>' +
      '<div class="scroll" style="max-height:320px"><table class="tbl"><thead><tr><th>grupo</th><th>parâmetro</th><th>valor</th><th>unidade</th></tr></thead><tbody>' +
      est.map(function (d) {
        var v = P.get(d.k);
        return '<tr><td>' + d.g + '</td><td>' + d.l + '</td><td>' + (typeof v === 'number' ? U.fmt(v, 5) : U.esc(v)) + '</td><td>' + d.u + '</td></tr>';
      }).join('') + '</tbody></table></div>';
  }

  // =====================================================================
  // REFRESH GERAL
  // =====================================================================
  function refreshAll() {
    var la = M.cachedLadder();
    refreshBadges(la);
    buildPanelCounts();
    if (state.pane === 'eng') { renderEng(la); }
    if (state.pane === 'eco') { renderPrizes(); renderEco(la); }
    if (state.pane === 'cat') { renderCat(la); }
    if (state.pane === 'aud') { renderAud(la); }
    if (state.pane === 'mc') { renderMC(); }
  }

  // Exportacao com saida garantida: se o navegador bloquear o download iniciado
  // de file:// (comportamento comum), o conteudo ainda tem que chegar ao usuario.
  // O relatorio e o produto da ferramenta; nao pode depender de um download passar.
  function emitFile(filename, text, mime) {
    var forcarTexto = $('#chkShowText') && $('#chkShowText').checked;
    if (forcarTexto) { U.showText(filename, text); return; }
    U.download(filename, text, mime);
  }

  function toast(msg) {
    var t = $('#toast'); t.textContent = msg; t.classList.add('on');
    clearTimeout(toast._t); toast._t = setTimeout(function () { t.classList.remove('on'); }, 2600);
  }

  // =====================================================================
  // INIT
  // =====================================================================
  function init() {
    buildPanel();
    fillSweepSelects();
    PB.game.attach($('#gameCanvas'));

    $$('.tab').forEach(function (b) {
      b.addEventListener('click', function () {
        $$('.tab').forEach(function (x) { x.classList.remove('on'); });
        b.classList.add('on');
        $$('.pane').forEach(function (p) { p.classList.remove('on'); });
        state.pane = b.getAttribute('data-pane');
        $('#pane-' + state.pane).classList.add('on');
        refreshAll();
      });
    });

    // painel
    $('#btnExportPreset').addEventListener('click', function () {
      emitFile('picbox-preset-' + P.hash() + '-' + U.fileStamp() + '.json',
        JSON.stringify(P.preset(), null, 2), 'application/json');
    });
    $('#btnImportPreset').addEventListener('click', function () { $('#filePreset').click(); });
    $('#filePreset').addEventListener('change', function (e) {
      var f = e.target.files[0]; if (!f) return;
      var fr = new FileReader();
      fr.onload = function () {
        try { P.loadPreset(JSON.parse(fr.result)); buildPanel(); refreshAll(); toast('Preset carregado.'); }
        catch (err) { toast('Falha ao carregar: ' + err.message); }
      };
      fr.readAsText(f); e.target.value = '';
    });
    $('#btnResetParams').addEventListener('click', function () {
      P.resetAll(); buildPanel(); refreshAll(); toast('Parâmetros restaurados ao padrão (todos estimados).');
    });
    $('#btnExpandAll').addEventListener('click', function () {
      var anyClosed = $$('.grp').some(function (g) { return !g.classList.contains('open'); });
      $$('.grp').forEach(function (g) {
        g.classList.toggle('open', anyClosed);
        g.querySelector('.caret').textContent = anyClosed ? '▾' : '▸';
      });
    });

    // jogar
    $('#btnNewGame').addEventListener('click', function () { PB.game.newGame(); });
    $('#btnDrop').addEventListener('click', function () { PB.game.press(); });
    $('#chkAids').addEventListener('change', function () { PB.game.setAids(this.checked); });
    $('#chkLog').addEventListener('change', function () { PB.game.setLogging(this.checked); });

    // monte carlo
    // limites e valor vem do conjunto de parametros, nunca do HTML
    ['sim.mcN:#mcN', 'sim.seed:#mcSeed'].forEach(function (pair) {
      var k = pair.split(':')[0], d = P.def(k), el = $(pair.split(':')[1]);
      if (d.min !== undefined) el.min = d.min;
      if (d.max !== undefined) el.max = d.max;
      if (d.step !== undefined) el.step = d.step;
      el.value = P.num(k);
    });
    $('#mcJit').checked = !!P.num('sim.mcjit');
    $('#btnRunMC').addEventListener('click', runMC);
    $('#btnMcCSV').addEventListener('click', function () {
      if (!state.mc) return toast('Rode o Monte Carlo primeiro.');
      emitFile('picbox-montecarlo-' + P.hash() + '.csv', PB.report.csvMC(state.mc), 'text/csv');
    });

    // engenharia
    $('#btnRunSweep').addEventListener('click', runSweep);
    $('#swMetric').addEventListener('change', renderSweep);
    $('#btnSweepCSV').addEventListener('click', function () {
      if (!state.sweep) return toast('Rode a varredura primeiro.');
      emitFile('picbox-varredura-' + P.hash() + '.csv', PB.report.csvSweep(state.sweep), 'text/csv');
    });
    $('#btnSelfTest').addEventListener('click', selfTest);

    // economia
    $('#btnAddPrize').addEventListener('click', function () {
      var ps = P.getPrizes();
      ps.push({ name: 'Novo prêmio', cost: 10, level: Math.min(P.getLadder().length, ps.length + 1), s: 'est' });
      P.setPrizes(ps); renderPrizes(); refreshAll();
    });

    // log
    $('#btnLogCSV').addEventListener('click', function () {
      emitFile('picbox-log-' + U.fileStamp() + '.csv', PB.game.logCSV(), 'text/csv');
    });
    $('#btnLogView').addEventListener('click', function () {
      U.showText('log de sessão (' + PB.game.G.log.length + ' linhas)', PB.game.logCSV());
    });
    $('#btnReplay').addEventListener('click', function () { doReplay(PB.game.logCSV()); });
    $('#btnReplayFile').addEventListener('click', function () { $('#fileLog').click(); });
    $('#fileLog').addEventListener('change', function (e) {
      var f = e.target.files[0]; if (!f) return;
      var fr = new FileReader();
      fr.onload = function () { doReplay(fr.result); };
      fr.readAsText(f); e.target.value = '';
    });
    $('#btnClearLog').addEventListener('click', function () { PB.game.G.log = []; toast('Log limpo.'); });

    // auditoria
    $('#btnRepMD').addEventListener('click', function () {
      var md = PB.report.markdown({ la: M.cachedLadder(), mc: state.mc, op: state.op, eco: state.eco });
      if (!($('#chkShowText') && $('#chkShowText').checked)) {
        U.download('picbox-auditoria-' + P.hash() + '-' + U.fileStamp() + '.md', md, 'text/markdown');
      }
      U.showText('relatório de auditoria (Markdown)', md);
    });
    $('#btnRepCSVparams').addEventListener('click', function () {
      emitFile('picbox-parametros-' + P.hash() + '.csv', PB.report.csvParams(), 'text/csv');
    });
    $('#btnRepCSVrounds').addEventListener('click', function () {
      emitFile('picbox-rodadas-' + P.hash() + '.csv', PB.report.csvRounds(M.cachedLadder()), 'text/csv');
    });
    $('#btnRepCSVlearn').addEventListener('click', function () {
      emitFile('picbox-curva-aprendizado-' + P.hash() + '.csv', PB.report.csvLearning(M.learningCurve()), 'text/csv');
    });
    $('#btnRepCSVmc').addEventListener('click', function () {
      if (!state.mc) return toast('Rode o Monte Carlo primeiro.');
      emitFile('picbox-montecarlo-' + P.hash() + '.csv', PB.report.csvMC(state.mc), 'text/csv');
    });
    $('#btnRepAll').addEventListener('click', function () {
      var h = P.hash(), st = U.fileStamp();
      var md = PB.report.markdown({ la: M.cachedLadder(), mc: state.mc, op: state.op, eco: state.eco });
      if ($('#chkShowText') && $('#chkShowText').checked) {
        // um unico documento com tudo dentro, para copiar de uma vez
        var tudo = md + '\n\n---\n\n## Anexo A - parametros (CSV)\n\n' + PB.report.csvParams() +
          '\n\n## Anexo B - rodadas (CSV)\n\n' + PB.report.csvRounds(M.cachedLadder()) +
          '\n\n## Anexo C - curva de aprendizado (CSV)\n\n' + PB.report.csvLearning(M.learningCurve()) +
          (state.mc ? '\n\n## Anexo D - Monte Carlo (CSV)\n\n' + PB.report.csvMC(state.mc) : '') +
          (state.sweep ? '\n\n## Anexo E - varredura (CSV)\n\n' + PB.report.csvSweep(state.sweep) : '');
        U.showText('auditoria completa - ' + h, tudo);
        return;
      }
      U.download('picbox-auditoria-' + h + '-' + st + '.md', md, 'text/markdown');
      setTimeout(function () { U.download('picbox-parametros-' + h + '.csv', PB.report.csvParams(), 'text/csv'); }, 250);
      setTimeout(function () { U.download('picbox-rodadas-' + h + '.csv', PB.report.csvRounds(M.cachedLadder()), 'text/csv'); }, 500);
      setTimeout(function () { U.download('picbox-curva-aprendizado-' + h + '.csv', PB.report.csvLearning(M.learningCurve()), 'text/csv'); }, 750);
      if (state.mc) setTimeout(function () { U.download('picbox-montecarlo-' + h + '.csv', PB.report.csvMC(state.mc), 'text/csv'); }, 1000);
      toast('Relatório e CSVs gerados.');
    });

    // overlay
    $('#btnCloseText').addEventListener('click', function () { $('#textOverlay').classList.remove('open'); });
    $('#btnCopyText').addEventListener('click', function () {
      U.copyText($('#textOverlayBody').value); toast('Copiado para a área de transferência.');
    });
    window.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') $('#textOverlay').classList.remove('open');
    });

    if (location.protocol === 'file:') {
      $('#chkShowText').checked = true;
      $('#protoNote').innerHTML = 'aberto via <code>file://</code> — o download pode ser bloqueado pelo navegador, ' +
        'então a saída em texto vem marcada por padrão';
    } else {
      $('#protoNote').textContent = 'servido por http — download direto disponível';
    }

    P.onChange(function () { buildPanelCounts(); });
    refreshAll();
    selfTest();
  }

  PB.ui = { init: init, onFrame: onFrame, toast: toast, refreshAll: refreshAll };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})(window.PB);
