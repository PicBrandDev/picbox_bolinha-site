/* PICBOX - economia.
   O custo esperado de premio e calculado SEPARADAMENTE por perfil de jogador.
   O dimensionamento e feito pelo perfil TREINADO: e ele que farma a maquina.
   Dimensionar pelo jogador medio e o erro classico que quebra a operacao. */
(function (PB) {
  'use strict';
  var U = PB.util, M = PB.model, P = PB.params;

  function compute(la, op) {
    la = la || M.cachedLadder();
    var prizes = P.getPrizes();
    var profs = M.profiles();
    var price = P.num('eco.price');
    var plays = P.num('eco.plays');
    var cap = P.num('eco.cap') / 100;

    var res = { price: price, plays: plays, cap: cap, prizes: [], byProfile: {}, nRounds: la.rows.length };

    // probabilidade de liberar cada premio, por perfil
    prizes.forEach(function (pz) {
      var lvl = Math.max(1, Math.min(la.rows.length, +pz.level));
      var e = { name: pz.name, cost: +pz.cost, level: lvl, p: {}, expected: {} };
      profs.forEach(function (pr) {
        var pw = la.cum[pr.id][lvl - 1];
        e.p[pr.id] = pw;
        e.expected[pr.id] = pw * (+pz.cost);
      });
      res.prizes.push(e);
    });

    var energyPerPlay = {};
    profs.forEach(function (pr) {
      var ec = (op && op.durations && op.durations[pr.id]) ? op.durations[pr.id].cost : 0;
      energyPerPlay[pr.id] = ec;
      var cost = res.prizes.reduce(function (a, e) { return a + e.expected[pr.id]; }, 0);
      res.byProfile[pr.id] = {
        label: pr.label,
        expectedPrizeCost: cost,
        energyCost: ec,
        margin: price - cost - ec,
        marginPct: price > 0 ? (price - cost - ec) / price : 0,
        costPctOfRevenue: price > 0 ? cost / price : Infinity,
        winAll: la.cum[pr.id][la.rows.length - 1]
      };
    });

    // mix de publico
    var mix = {
      novice: P.num('eco.mixNov'), mid: P.num('eco.mixMid'), pro: P.num('eco.mixPro')
    };
    var tot = mix.novice + mix.mid + mix.pro;
    res.mixSum = tot;
    res.mix = { novice: mix.novice / (tot || 1), mid: mix.mid / (tot || 1), pro: mix.pro / (tot || 1) };
    res.blendedPrizeCost = profs.reduce(function (a, pr) {
      return a + res.mix[pr.id] * res.byProfile[pr.id].expectedPrizeCost;
    }, 0);
    res.blendedEnergy = profs.reduce(function (a, pr) { return a + res.mix[pr.id] * energyPerPlay[pr.id]; }, 0);
    res.blendedMargin = price - res.blendedPrizeCost - res.blendedEnergy;

    res.revenueDay = price * plays;
    res.prizeCostDayBlended = res.blendedPrizeCost * plays;
    res.prizeCostDayPro = res.byProfile.pro.expectedPrizeCost * plays;
    res.marginDayBlended = res.blendedMargin * plays;
    res.energyDay = res.blendedEnergy * plays;

    // alerta: teto medido pelo perfil TREINADO
    res.proPct = res.byProfile.pro.costPctOfRevenue;
    res.alert = res.proPct > cap;
    res.alertText = res.alert
      ? 'CUSTO ESPERADO DE PREMIO NO PERFIL TREINADO = ' + U.pct(res.proPct, 1) +
      ' da receita, acima do teto de ' + U.pct(cap, 0) + '. Um jogador treinado extrai mais valor do que a maquina arrecada com ele.'
      : 'Custo esperado no perfil treinado = ' + U.pct(res.proPct, 1) + ' da receita, dentro do teto de ' + U.pct(cap, 0) + '.';

    // preco minimo para respeitar o teto no perfil treinado
    res.minPrice = res.byProfile.pro.expectedPrizeCost / (cap || 1e-9);
    // ponto de equilibrio: quantas jogadas do treinado ate zerar a margem do dia
    res.breakEvenPlays = res.blendedMargin > 0 ? null : Infinity;
    return res;
  }

  PB.economy = { compute: compute };
})(window.PB);
