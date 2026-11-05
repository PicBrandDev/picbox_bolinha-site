/* PICBOX - motor de fisica.
   Uma unica engine serve os quatro modos (Jogar, Monte Carlo, Engenharia, Auditoria).
   Convencao de unidades:
     - interface e eixos em mm, mm/s, ms
     - integracao do voo em SI (m, s, kg), convertida nas bordas
     - y positivo para BAIXO, a partir do plano de soltura */
(function (PB) {
  'use strict';
  var U = PB.util;

  // ============================================================
  // 1. PERFIS DE MOVIMENTO DOS EIXOS
  // ============================================================
  // Todos os perfis percorrem o curso util S em meio periodo (T/2) e voltam
  // no meio periodo seguinte. Movimento continuo: nunca para no clique.

  function makeAxis(cfg) {
    var S = cfg.stroke, T = cfg.T, ph = (cfg.phaseDeg || 0) / 360;
    var prof = cfg.profile, meta = { profile: prof, S: S, T: T, warn: '' };
    var pos, vel;

    if (prof === 'senoidal') {
      // x(t) = S/2 * (1 - cos(2*pi*(t/T + fase)))
      var w = 2 * Math.PI / T;
      pos = function (t) { return S / 2 * (1 - Math.cos(w * t + 2 * Math.PI * ph)); };
      vel = function (t) { return S / 2 * w * Math.sin(w * t + 2 * Math.PI * ph); };
      meta.vPeak = Math.PI * S / T;
      meta.vMean = 2 * S / T;
      meta.aPeak = 2 * Math.PI * Math.PI * S / (T * T);
      meta.jerkPeak = 4 * Math.PI * Math.PI * Math.PI * S / (T * T * T);
      meta.formula = 'x(t) = S/2 · [1 − cos(2π(t/T + φ))]';

    } else if (prof === 'triangular') {
      // velocidade constante, inversao instantanea
      var vc = 2 * S / T;
      pos = function (t) {
        var u = U.frac(t / T + ph);
        return u < 0.5 ? 2 * S * u : 2 * S * (1 - u);
      };
      vel = function (t) {
        var u = U.frac(t / T + ph);
        return u < 0.5 ? vc : -vc;
      };
      meta.vPeak = vc; meta.vMean = vc;
      meta.aPeak = Infinity; meta.jerkPeak = Infinity;
      meta.warn = 'Perfil triangular exige inversao instantanea de velocidade: aceleracao e jerk infinitos. Fisicamente irrealizavel; use como limite superior teorico.';
      meta.formula = 'x(t) = onda triangular de amplitude S, |v| = 2S/T';

    } else if (prof === 'trapezoidal') {
      var th = T / 2;
      var aNeed = 4 * S / (th * th);   // aceleracao minima para fechar o curso
      var a = cfg.aPeak;
      if (!(a >= aNeed)) {
        meta.warn = 'Aceleracao de pico insuficiente (' + U.fmt(a, 0) + ' mm/s2) para cumprir ' +
          U.fmt(S, 0) + ' mm em ' + U.fmt(th, 3) + ' s. Minimo = ' + U.fmt(aNeed, 0) +
          ' mm/s2. O perfil foi degradado para triangular (a = a_min).';
        a = aNeed;
      }
      var disc = Math.max(0, 1 - 4 * S / (a * th * th));
      var r = (1 - Math.sqrt(disc)) / 2;          // fracao do meio-periodo acelerando
      var ta = r * th, vp = a * ta, tc = th - 2 * ta, xa = 0.5 * a * ta * ta;
      var half = function (tau) {                 // posicao dentro de meio periodo
        if (tau <= ta) return 0.5 * a * tau * tau;
        if (tau <= ta + tc) return xa + vp * (tau - ta);
        var t2 = tau - ta - tc;
        return xa + vp * tc + vp * t2 - 0.5 * a * t2 * t2;
      };
      var halfV = function (tau) {
        if (tau <= ta) return a * tau;
        if (tau <= ta + tc) return vp;
        return vp - a * (tau - ta - tc);
      };
      pos = function (t) {
        var u = U.frac(t / T + ph);
        return u < 0.5 ? half(u * T) : S - half((u - 0.5) * T);
      };
      vel = function (t) {
        var u = U.frac(t / T + ph);
        return u < 0.5 ? halfV(u * T) : -halfV((u - 0.5) * T);
      };
      meta.vPeak = vp; meta.vMean = 2 * S / T; meta.aPeak = a;
      meta.tAccel = ta; meta.tCruise = tc; meta.aUsed = a; meta.aMin = aNeed;
      meta.jerkPeak = Infinity;
      meta.jerkNote = 'Trapezio puro tem degrau de aceleracao (jerk infinito). Com jerk J = ' +
        U.fmt(cfg.jerk, 0) + ' mm/s3 a rampa de aceleracao leva ' + U.fmt(1000 * a / cfg.jerk, 1) +
        ' ms, ou ' + U.fmt(100 * (a / cfg.jerk) / Math.max(ta, 1e-9), 1) + ' % do trecho de aceleracao.';
      if (a / cfg.jerk > 0.5 * ta) meta.warn += (meta.warn ? ' ' : '') +
        'A rampa de jerk consome mais de metade do trecho de aceleracao: o perfil real ficara sensivelmente mais lento que o trapezio ideal.';
      meta.formula = 'trapezio: a const. em ' + U.fmt(ta, 3) + ' s, cruzeiro ' + U.fmt(tc, 3) + ' s, v_pico = ' + U.fmt(vp, 1) + ' mm/s';

    } else { // customizado por tabela
      var tab = (cfg.table && cfg.table.length > 1) ? cfg.table.slice() : [[0, 0], [0.5, 1], [1, 0]];
      tab.sort(function (p, q) { return p[0] - q[0]; });
      var interp = function (un) {
        un = U.frac(un);
        var i;
        for (i = 0; i < tab.length - 1; i++) {
          if (un >= tab[i][0] && un <= tab[i + 1][0]) {
            var f = (un - tab[i][0]) / Math.max(1e-12, tab[i + 1][0] - tab[i][0]);
            return U.lerp(tab[i][1], tab[i + 1][1], f);
          }
        }
        return tab[tab.length - 1][1];
      };
      pos = function (t) { return S * interp(t / T + ph); };
      var hdt = T / 4000;
      vel = function (t) { return (pos(t + hdt) - pos(t - hdt)) / (2 * hdt); };
      var vmax = 0, amax = 0, prev = vel(0), i2;
      for (i2 = 0; i2 <= 400; i2++) {
        var tt = i2 * T / 400, vv = vel(tt);
        vmax = Math.max(vmax, Math.abs(vv));
        amax = Math.max(amax, Math.abs((vv - prev) / (T / 400)));
        prev = vv;
      }
      meta.vPeak = vmax; meta.vMean = 2 * S / T; meta.aPeak = amax; meta.jerkPeak = NaN;
      meta.formula = 'tabela customizada com ' + tab.length + ' pontos, interpolacao linear';
      meta.warn = 'Perfil por tabela: velocidade obtida por diferenca finita. Verifique se a tabela e fisicamente executavel pelo acionamento.';
    }

    return { pos: pos, vel: vel, meta: meta, stroke: S, T: T, phaseDeg: cfg.phaseDeg || 0 };
  }

  // Inverso de makeAxis: qual periodo ida-e-volta entrega uma velocidade de pico
  // pedida, no perfil dado. Existe porque a interface do modelo 3D e em m/s e o
  // parametro do conjunto e o periodo T: a conversao tem que ter UMA implementacao.
  // vPeak e monotonicamente decrescente em T em todos os perfis, logo bissecao fecha.
  function periodForPeakSpeed(cfg, vPeakTarget, Tmin, Tmax) {
    var lo = Tmin || 0.05, hi = Tmax || 60, i, mid, v;
    var peak = function (T) { return makeAxis(Object.assign({}, cfg, { T: T })).meta.vPeak; };
    if (!(vPeakTarget > 0)) return hi;
    if (peak(lo) < vPeakTarget) return lo;   // pedido acima do que o perfil entrega
    if (peak(hi) > vPeakTarget) return hi;
    for (i = 0; i < 60; i++) {
      mid = 0.5 * (lo + hi); v = peak(mid);
      if (v > vPeakTarget) lo = mid; else hi = mid;
    }
    return 0.5 * (lo + hi);
  }

  // ============================================================
  // 2. VOO DA BOLA
  // ============================================================
  // Integracao RK4 de:
  //   dvx/dt = -k|v|vx  (+ Magnus)
  //   dvy/dt =  g - k|v|vy  (+ Magnus),  k = rho*Cd*A/(2m)
  // Sem arrasto e sem Magnus a solucao e a parabola classica.

  function flight(o) {
    var g = o.g, m = o.m, d = o.d, A = Math.PI * d * d / 4;
    var k = o.drag ? (0.5 * o.rho * o.cd * A / m) : 0;
    var useMag = !!o.magnus && Math.abs(o.spin) > 1e-9;
    var rBall = d / 2, sgn = o.spin >= 0 ? 1 : -1;
    var dt = o.dt, h = o.h;

    function acc(vx, vy) {
      var ax = 0, ay = g;
      var v = Math.hypot(vx, vy);
      if (k > 0 && v > 0) { ax -= k * v * vx; ay -= k * v * vy; }
      if (useMag && v > 1e-9) {
        var Cl = Math.min(0.35, Math.abs(o.spin) * rBall / v);   // aprox. grosseira
        var am = 0.5 * o.rho * A * Cl * v * v / m;
        ax += sgn * am * (-vy / v); ay += sgn * am * (vx / v);
      }
      return [ax, ay];
    }

    var x = 0, y = 0, vx = o.vx0, vy = o.vy0 || 0, t = 0;
    var path = [[0, 0, 0]], n = 0, maxV = Math.hypot(vx, vy), sample = Math.max(1, Math.round(0.004 / dt));
    var px, py, pvx, pvy, pt;
    while (y < h && n < 400000) {
      px = x; py = y; pvx = vx; pvy = vy; pt = t;
      var a1 = acc(vx, vy);
      var a2 = acc(vx + 0.5 * dt * a1[0], vy + 0.5 * dt * a1[1]);
      var a3 = acc(vx + 0.5 * dt * a2[0], vy + 0.5 * dt * a2[1]);
      var a4 = acc(vx + dt * a3[0], vy + dt * a3[1]);
      var kx1 = vx, kx2 = vx + 0.5 * dt * a1[0], kx3 = vx + 0.5 * dt * a2[0], kx4 = vx + dt * a3[0];
      var ky1 = vy, ky2 = vy + 0.5 * dt * a1[1], ky3 = vy + 0.5 * dt * a2[1], ky4 = vy + dt * a3[1];
      x += dt / 6 * (kx1 + 2 * kx2 + 2 * kx3 + kx4);
      y += dt / 6 * (ky1 + 2 * ky2 + 2 * ky3 + ky4);
      vx += dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0]);
      vy += dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1]);
      t += dt; n++;
      maxV = Math.max(maxV, Math.hypot(vx, vy));
      if (n % sample === 0) path.push([x, y, t]);
    }
    if (y > h && y !== py) {   // interpolacao linear no cruzamento do plano da boca
      var f = (h - py) / (y - py);
      x = px + f * (x - px); vx = pvx + f * (vx - pvx); vy = pvy + f * (vy - pvy);
      t = pt + f * (t - pt); y = h;
    }
    path.push([x, y, t]);
    return { t: t, dx: x, vx: vx, vy: vy, vImpact: Math.hypot(vx, vy), vMax: maxV, path: path, steps: n };
  }

  // Solucao analitica sem arrasto (a formula que aparece na tela)
  function freeFall(h, g, vy0) {
    vy0 = vy0 || 0;
    // h = vy0*t + g*t^2/2  ->  t = (-vy0 + sqrt(vy0^2 + 2gh))/g
    var t = (-vy0 + Math.sqrt(vy0 * vy0 + 2 * g * h)) / g;
    return { t: t, vy: vy0 + g * t };
  }

  // ============================================================
  // 3. PROVA DO ARRASTO
  // ============================================================
  // Nao assume nada: integra com e sem arrasto e mede a diferenca.
  function dragProof(o) {
    var withDrag = flight(Object.assign({}, o, { drag: true, magnus: false }));
    var noDrag = flight(Object.assign({}, o, { drag: false, magnus: false }));
    var ff = freeFall(o.h, o.g, o.vy0 || 0);
    var A = Math.PI * o.d * o.d / 4;
    var vImp = withDrag.vImpact;
    var Re = o.rho * vImp * o.d / o.mu;
    var Fd = 0.5 * o.rho * o.cd * A * vImp * vImp;
    var W = o.m * o.g;
    var v0 = Math.abs(o.vx0);
    var Re0 = o.rho * Math.max(v0, 1e-9) * o.d / o.mu;
    var Fd0 = 0.5 * o.rho * o.cd * A * v0 * v0;
    var res = {
      A: A, Re: Re, Re0: Re0, Fd: Fd, Fd0: Fd0, W: W,
      ratio: Fd / W, ratio0: Fd0 / W,
      tDrag: withDrag.t, tNoDrag: noDrag.t, tAnalytic: ff.t,
      dxDrag: withDrag.dx, dxNoDrag: noDrag.dx,
      dxAnalytic: o.vx0 * ff.t,
      ddx: withDrag.dx - noDrag.dx,
      dt: withDrag.t - noDrag.t,
      vImpact: vImp
    };
    res.regime = Re < 1 ? 'Stokes (laminar, Re < 1)' :
      Re < 1000 ? 'intermediario (1 < Re < 1e3)' :
        Re < 2e5 ? 'subcritico, Cd ~ 0,4-0,5 (1e3 < Re < 2e5)' :
          'supercritico, crise do arrasto (Re > 2e5): Cd cai para ~0,1-0,2 e o valor usado esta errado';
    return res;
  }

  // Magnus como percentual do peso, para dizer se o spin residual importa
  function magnusProof(o) {
    var A = Math.PI * o.d * o.d / 4, r = o.d / 2;
    var withM = flight(Object.assign({}, o, { drag: !!o.drag, magnus: true }));
    var noM = flight(Object.assign({}, o, { drag: !!o.drag, magnus: false }));
    var v = noM.vImpact;
    var Cl = Math.min(0.35, Math.abs(o.spin) * r / Math.max(v, 1e-9));
    var Fm = 0.5 * o.rho * A * Cl * v * v;
    return {
      Cl: Cl, Fm: Fm, W: o.m * o.g, ratio: Fm / (o.m * o.g),
      spinRatio: Math.abs(o.spin) * r / Math.max(v, 1e-9),
      ddx: withM.dx - noM.dx, I: o.ki * o.m * r * r,
      Erot: 0.5 * (o.ki * o.m * r * r) * o.spin * o.spin,
      Etrans: 0.5 * o.m * v * v
    };
  }

  PB.physics = {
    makeAxis: makeAxis, periodForPeakSpeed: periodForPeakSpeed,
    flight: flight, freeFall: freeFall,
    dragProof: dragProof, magnusProof: magnusProof
  };
})(window.PB);
