/* PICBOX - relatorio de auditoria (Markdown + CSV).
   O relatorio e o produto: ele tem que permitir que outra pessoa refaca a conta. */
(function (PB) {
  'use strict';
  var U = PB.util, M = PB.model, P = PB.params, PH = PB.physics;

  var FORMULAS = [
    ['Tempo de queda livre (sem arrasto)', 't = raiz(2h/g)', 'h = altura de queda, g = gravidade local.'],
    ['Tempo de queda com velocidade vertical inicial', 't = [-v_y0 + raiz(v_y0^2 + 2gh)] / g', 'Reduz-se a raiz(2h/g) quando v_y0 = 0.'],
    ['Avanco horizontal no ar (sem arrasto)', 'dx = v_soltura · t', 'A bola herda a velocidade horizontal do eixo A no instante da soltura.'],
    ['Trajetoria com arrasto (integrada por RK4)', 'dv/dt = g_vetor - (rho·Cd·A / 2m) · |v| · v', 'A = pi·d^2/4. Resolvida numericamente; a comparacao com o caso sem arrasto e a prova.'],
    ['Numero de Reynolds', 'Re = rho · v · d / mu', 'Define se o Cd adotado e valido no regime de operacao.'],
    ['Forca de arrasto', 'F_d = 0,5 · rho · Cd · A · v^2', 'Reportada como PERCENTUAL do peso m·g.'],
    ['Forca de Magnus (estimativa)', 'F_m = 0,5 · rho · A · C_L · v^2, C_L ~ min(0,35 ; omega·r/v)', 'Modelo grosseiro de coeficiente de sustentacao; serve para dizer se o spin importa, nao para prever o desvio exato.'],
    ['Momento de inercia da bola', 'I = k · m · r^2', 'k = 0,4 para esfera macica homogenea.'],
    ['Velocidade relativa no cruzamento', 'v_rel = v_bola,x(t_pouso) - v_buraco(t_pouso)', 'Ambas medidas no plano da boca do buraco.'],
    ['Janela de acerto temporal (passagem limpa)', 'T = (L_abertura - d_bola) / |v_rel|', 'A bola inteira atravessa sem tocar a borda.'],
    ['Janela de acerto temporal (conformidade)', 'T = L_abertura / |v_rel|', 'Centro da bola dentro da boca; tocar a borda conta como execucao valida.'],
    ['Probabilidade de acerto por rodada', 'p = erf( T / (2·sigma·raiz2) )', 'sigma = desvio-padrao do erro de timing do jogador; erro suposto gaussiano de media zero.'],
    ['Probabilidade com janela assimetrica e vies', 'p = 1/2 · [ erf((w_dir - b)/(sigma·raiz2)) + erf((w_esq + b)/(sigma·raiz2)) ]', 'w_esq e w_dir sao as meias-janelas numericas medidas; b = vies sistematico.'],
    ['Probabilidade de vitoria da escada', 'P = produto de p_i, i = 1..N', 'Errar encerra a partida: os eventos sao encadeados.'],
    ['Erro posicional induzido pela maquina', 'sigma_maquina = v_soltura · jitter_total', 'jitter_total = raiz( jit_soltura^2 + jit_eletronico^2 + T_varredura^2/12 ).'],
    ['Erro posicional induzido pelo jogador', 'sigma_jogador = v_rel · sigma_timing', 'Mesma unidade (mm) do anterior, para comparacao direta.'],
    ['Criterio de habilidade', 'R = sigma_jogador / sigma_maquina', 'R < 4 significa que a dispersao da maquina e comparavel a do jogador: a maquina passa a decidir.'],
    ['Perfil senoidal do eixo', 'x(t) = S/2 · [1 - cos(2·pi·(t/T + fase))]', 'v_pico = pi·S/T, v_media = 2S/T, a_pico = 2·pi^2·S/T^2.'],
    ['Perfil trapezoidal', 'S = a·r·(T/2)^2·(1-r), r = fracao do meio-periodo em aceleracao', 'Exige a >= 4S/(T/2)^2, senao o curso nao fecha.'],
    ['Distancia percorrida pela correia', 'd/h = 2·S·3600/T', 'Duas travessias do curso por periodo.'],
    ['Ciclos de inversao', 'inv/h = 2·3600/T', 'Insumo direto para vida util de correia, polia e rolamento.'],
    ['Potencia mecanica estimada por eixo', 'P = m_carro · v_pico^2 / T', 'Energia cinetica injetada e dissipada a cada meia volta, sem regeneracao.'],
    ['Custo esperado de premio por jogada', 'C = soma( P_vitoria(nivel_i) · custo_i )', 'Calculado separadamente por perfil de jogador.']
  ];

  function paramRows() {
    return P.schema().map(function (d) {
      var v = P.get(d.k);
      return [d.g, d.k, d.l, (typeof v === 'number' ? U.fmt(v, 6) : v), d.u,
        d.s === 'def' ? 'definido' : (P.stat(d.k) === 'med' ? 'MEDIDO' : 'estimado'),
        d.n || ''];
    });
  }

  function csvParams() {
    return U.toCSV([['grupo', 'chave', 'parametro', 'valor', 'unidade', 'procedencia', 'nota']].concat(paramRows()));
  }

  function csvRounds(la) {
    var rows = [['rodada', 'mult_velocidade', 'L_abertura_mm', 'h_queda_mm', 'd_bola_mm',
      'oportunidades_por_min', 'v_rel_media_mm_s', 'v_soltura_media_mm_s',
      'T_analitica_ms', 'T_numerica_ms', 'erro_relativo_T',
      'sigma_jogador_treinado_mm', 'sigma_maquina_mm', 'razao_sigmas',
      'p_iniciante', 'p_medio', 'p_treinado',
      'P_acum_iniciante', 'P_acum_medio', 'P_acum_treinado', 'soluvel']];
    la.rows.forEach(function (r, i) {
      rows.push([r.round.n, U.fmt(r.round.speedMul, 4), U.fmt(r.L, 2), U.fmt(r.h, 1), U.fmt(r.d, 2),
        U.fmt(r.oppRate * 60, 2), U.fmt(r.vRelMean, 1), U.fmt(r.v0Mean, 1),
        U.fmt(r.T_used * 1000, 3), U.fmt(r.T_num * 1000, 3), U.fmt(r.T_err, 4),
        U.fmt(r.sig ? r.sig.pro.sPlayer : 0, 3), U.fmt(r.sig ? r.sig.pro.sMachine : 0, 4),
        U.fmt(r.sig ? r.sig.pro.ratio : 0, 2),
        U.fmt(r.probs.novice, 5), U.fmt(r.probs.mid, 5), U.fmt(r.probs.pro, 5),
        U.fmt(la.cum.novice[i], 6), U.fmt(la.cum.mid[i], 6), U.fmt(la.cum.pro[i], 6),
        r.solvable ? 'sim' : 'NAO']);
    });
    return U.toCSV(rows);
  }

  function csvLearning(lc) {
    var n = lc.length ? lc[0].perRound.length : 0, hdr = ['sigma_timing_ms', 'P_vitoria_escada'], i;
    for (i = 1; i <= n; i++) hdr.push('p_rodada_' + i);
    var rows = [hdr];
    lc.forEach(function (r) {
      rows.push([r.sigmaMs, U.fmt(r.win, 6)].concat(r.perRound.map(function (p) { return U.fmt(p, 5); })));
    });
    return U.toCSV(rows);
  }

  function csvMC(mc) {
    if (!mc) return '';
    var rows = [['perfil', 'sigma_ms', 'N', 'rodada', 'tentativas', 'acertos', 'taxa_acerto_condicional',
      'taxa_alcance', 'taxa_conclusao_acumulada', 'acertos_de_borda']];
    Object.keys(mc.byProfile).forEach(function (id) {
      var a = mc.byProfile[id], i;
      for (i = 0; i < mc.rounds; i++) {
        rows.push([a.label, U.fmt(a.sigmaMs, 1), mc.N, i + 1, a.attempts[i], a.hits[i],
          U.fmt(a.hitRate[i], 5), U.fmt(a.reachRate[i], 5), U.fmt(a.clearRate[i], 5), a.rimOnly[i]]);
      }
    });
    return U.toCSV(rows);
  }

  function csvSweep(sw) {
    if (!sw) return '';
    var hdr = [sw.xKey];
    if (sw.yKey) hdr.push(sw.yKey);
    hdr = hdr.concat(['soluvel', 'T_analitica_ms', 'T_numerica_ms', 'janela_min_ms', 'v_rel_mm_s',
      'oportunidades_por_min', 'sigma_jogador_mm', 'sigma_maquina_mm', 'razao_sigmas',
      'p_iniciante', 'p_medio', 'p_treinado', 'P_escada_iniciante', 'P_escada_medio', 'P_escada_treinado']);
    var rows = [hdr];
    sw.rows.forEach(function (r) {
      var line = [U.fmt(r.x, 5)];
      if (sw.yKey) line.push(U.fmt(r.y, 5));
      rows.push(line.concat([r.solvable ? 'sim' : 'NAO', U.fmt(r.T_ms, 3), U.fmt(r.Tnum_ms, 3),
        U.fmt(r.widthMin_ms, 3), U.fmt(r.vRel, 1), U.fmt(r.opps, 2),
        U.fmt(r.sigPlayer, 3), U.fmt(r.sigMachine, 4), U.fmt(r.ratio, 2),
        U.fmt(r.pNov, 5), U.fmt(r.pMid, 5), U.fmt(r.pPro, 5),
        U.fmt(r.winNov, 6), U.fmt(r.winMid, 6), U.fmt(r.winPro, 6)]));
    });
    return U.toCSV(rows);
  }

  // -------------------- MARKDOWN --------------------
  function markdown(ctx) {
    var la = ctx.la || M.cachedLadder();
    var op = ctx.op || M.opMetrics(ctx.mc);
    var eco = ctx.eco || PB.economy.compute(la, op);
    var lc = ctx.lc || M.learningCurve();
    var mc = ctx.mc;
    var w0 = la.rows[0].w;
    var drag = PH.dragProof(Object.assign({}, w0.flightBase, { vx0: la.rows[0].v0Mean / 1000, drag: true }));
    var mag = PH.magnusProof(Object.assign({}, w0.flightBase, { vx0: la.rows[0].v0Mean / 1000 }));
    var L = [];
    var pu = function (s) { L.push(s); };

    pu('# PICBOX — Relatório técnico de auditoria');
    pu('');
    pu('| campo | valor |');
    pu('|---|---|');
    pu('| Data/hora da emissão | ' + U.nowStamp() + ' |');
    pu('| Versão do conjunto de parâmetros | ' + P.VERSION + ' |');
    pu('| Hash do conjunto (FNV-1a 32 bits sobre a serialização canônica) | `' + P.hash() + '` |');
    pu('| Parâmetros ainda ESTIMADOS | ' + P.estimated().length + ' de ' + P.schema().length + ' |');
    pu('| Parâmetros marcados como MEDIDOS | ' + P.measured().length + ' |');
    pu('| Critério de vitória adotado | ' + P.get('sim.crit') + ' |');
    pu('| Estratégia de jogador modelada | ' + P.get('ply.select') + ' |');
    pu('');
    pu('> Este documento é gerado a partir do conjunto de parâmetros corrente. Alterar qualquer');
    pu('> parâmetro muda o hash acima. Dois relatórios com o mesmo hash descrevem exatamente a');
    pu('> mesma máquina.');
    pu('');

    // ---- veredito ----
    var rr = la.rows.map(function (r) { return r.solvable ? r.sig.pro.ratio : 0; });
    var rMin = Math.min.apply(null, rr);
    pu('## 1. Veredito de habilidade');
    pu('');
    pu('Razão **sigma_jogador / sigma_maquina** por rodada (perfil treinado, o mais exigente):');
    pu('');
    pu('| rodada | sigma_jogador (mm) | sigma_maquina (mm) | razão | veredito |');
    pu('|---:|---:|---:|---:|---|');
    la.rows.forEach(function (r) {
      if (!r.solvable) { pu('| ' + r.round.n + ' | — | — | — | RODADA INSOLÚVEL |'); return; }
      var s = r.sig.pro;
      pu('| ' + r.round.n + ' | ' + U.fmt(s.sPlayer, 2) + ' | ' + U.fmt(s.sMachine, 3) + ' | ' +
        U.fmt(s.ratio, 2) + ' | ' + (s.ratio < 4 ? '**REPROVADO (< 4)**' : 'aprovado') + ' |');
    });
    pu('');
    pu(rMin < 4
      ? '**REPROVADO.** A menor razão da escada é ' + U.fmt(rMin, 2) + ', abaixo de 4. Nas rodadas ' +
      'marcadas, a dispersão introduzida pela própria máquina é comparável à do jogador: o resultado ' +
      'deixa de ser determinado pela habilidade. Corrija a cadeia de soltura ou reduza a velocidade ' +
      'de soltura antes de operar.'
      : '**APROVADO.** A menor razão da escada é ' + U.fmt(rMin, 2) + ' (≥ 4). O erro do jogador domina ' +
      'o erro da máquina em todas as rodadas: o resultado é determinado pela habilidade.');
    pu('');

    // ---- parametros ----
    pu('## 2. Conjunto de parâmetros');
    pu('');
    pu('| grupo | parâmetro | valor | unidade | procedência |');
    pu('|---|---|---:|---|---|');
    paramRows().forEach(function (r) {
      pu('| ' + U.escMd(r[0]) + ' | ' + U.escMd(r[2]) + ' | ' + U.escMd(r[3]) + ' | ' + U.escMd(r[4]) + ' | ' +
        (r[5] === 'MEDIDO' ? '**medido**' : r[5]) + ' |');
    });
    pu('');
    pu('Escada configurada:');
    pu('');
    pu('| rodada | mult. velocidade | abertura L (mm) | altura h (mm) | prêmio liberado |');
    pu('|---:|---:|---:|---:|---|');
    P.getLadder().forEach(function (r) {
      pu('| ' + r.n + ' | ' + U.fmt(r.speedMul, 3) + ' | ' + U.fmt(r.L, 2) + ' | ' + U.fmt(r.h, 1) +
        ' | ' + (r.prize ? U.escMd(r.prize.name) + ' (R$ ' + U.fmt(r.prize.cost, 2) + ')' : '—') + ' |');
    });
    pu('');

    // ---- formulas ----
    pu('## 3. Fórmulas utilizadas');
    pu('');
    pu('| grandeza | fórmula | observação |');
    pu('|---|---|---|');
    FORMULAS.forEach(function (f) { pu('| ' + f[0] + ' | `' + f[1] + '` | ' + f[2] + ' |'); });
    pu('');
    pu('Perfil do eixo A: `' + w0.axA.meta.formula + '`  ');
    pu('Perfil do eixo B: `' + w0.axB.meta.formula + '`');
    if (w0.axA.meta.warn) pu('');
    if (w0.axA.meta.warn) pu('> Eixo A: ' + w0.axA.meta.warn);
    if (w0.axB.meta.warn) pu('> Eixo B: ' + w0.axB.meta.warn);
    pu('');

    // ---- arrasto ----
    pu('## 4. Prova do arrasto aerodinâmico');
    pu('');
    pu('Calculado na rodada 1, com velocidade de soltura média de ' + U.fmt(la.rows[0].v0Mean, 1) + ' mm/s.');
    pu('');
    pu('| grandeza | valor |');
    pu('|---|---:|');
    pu('| Área frontal A = pi·d²/4 | ' + U.fmt(drag.A * 1e6, 2) + ' mm² |');
    pu('| Velocidade no cruzamento do plano | ' + U.fmt(drag.vImpact, 3) + ' m/s |');
    pu('| Reynolds no cruzamento | ' + U.fmt(drag.Re, 0) + ' |');
    pu('| Regime | ' + drag.regime + ' |');
    pu('| Força de arrasto no cruzamento | ' + U.fmt(drag.Fd * 1000, 3) + ' mN |');
    pu('| Peso da bola m·g | ' + U.fmt(drag.W * 1000, 3) + ' mN |');
    pu('| **Arrasto / peso** | **' + U.pct(drag.ratio, 2) + '** |');
    pu('| Tempo de queda sem arrasto (analítico) | ' + U.fmt(drag.tAnalytic * 1000, 3) + ' ms |');
    pu('| Tempo de queda sem arrasto (RK4) | ' + U.fmt(drag.tNoDrag * 1000, 3) + ' ms |');
    pu('| Tempo de queda com arrasto (RK4) | ' + U.fmt(drag.tDrag * 1000, 3) + ' ms |');
    pu('| Avanço horizontal sem arrasto | ' + U.fmt(drag.dxNoDrag * 1000, 3) + ' mm |');
    pu('| Avanço horizontal com arrasto | ' + U.fmt(drag.dxDrag * 1000, 3) + ' mm |');
    pu('| **Diferença no ponto de pouso** | **' + U.fmt(drag.ddx * 1000, 3) + ' mm** |');
    pu('| Diferença como fração da abertura útil | ' + U.pct(Math.abs(drag.ddx * 1000) / Math.max(1e-9, la.rows[0].L - la.rows[0].d), 2) + ' |');
    pu('');
    var negl = Math.abs(drag.ddx * 1000) < 0.05 * Math.max(1e-9, (la.rows[0].L - la.rows[0].d));
    pu(negl
      ? '**Conclusão: o arrasto é desprezível nesta geometria.** O deslocamento do ponto de pouso ' +
      'causado pelo arrasto (' + U.fmt(Math.abs(drag.ddx * 1000), 3) + ' mm) é menor que 5 % da abertura ' +
      'útil. A parábola sem arrasto pode ser usada para projeto, com o erro acima registrado.'
      : '**Conclusão: o arrasto NÃO é desprezível.** O deslocamento do ponto de pouso é ' +
      U.fmt(Math.abs(drag.ddx * 1000), 3) + ' mm, ou ' +
      U.pct(Math.abs(drag.ddx * 1000) / Math.max(1e-9, la.rows[0].L - la.rows[0].d), 1) +
      ' da abertura útil. Projetar pela parábola simples introduz erro sistemático dessa ordem.');
    pu('');
    pu('Spin residual (' + U.fmt(P.num('rel.spin'), 1) + ' rad/s): força de Magnus estimada em ' +
      U.pct(mag.ratio, 2) + ' do peso, deslocamento de ' + U.fmt(mag.ddx * 1000, 3) + ' mm no pouso. ' +
      'Momento de inércia I = ' + U.fmt(mag.I * 1e7, 3) + '×10⁻⁷ kg·m²; energia de rotação = ' +
      U.pct(mag.Erot / Math.max(1e-12, mag.Etrans), 3) + ' da energia de translação.');
    pu('');

    // ---- janelas e probabilidades ----
    pu('## 5. Janela de acerto e probabilidade por rodada');
    pu('');
    pu('| rodada | L (mm) | v_rel (mm/s) | T analítica (ms) | T numérica (ms) | erro | oport./min | p iniciante | p médio | p treinado |');
    pu('|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
    la.rows.forEach(function (r) {
      if (!r.solvable) { pu('| ' + r.round.n + ' | ' + U.fmt(r.L, 1) + ' | — | — | — | — | 0 | 0 | 0 | 0 |'); return; }
      pu('| ' + r.round.n + ' | ' + U.fmt(r.L, 1) + ' | ' + U.fmt(r.vRelMean, 0) + ' | ' +
        U.fmt(r.T_used * 1000, 1) + ' | ' + U.fmt(r.T_num * 1000, 1) + ' | ' + U.pct(r.T_err, 1) + ' | ' +
        U.fmt(r.oppRate * 60, 1) + ' | ' + U.fmt(r.probs.novice, 4) + ' | ' + U.fmt(r.probs.mid, 4) +
        ' | ' + U.fmt(r.probs.pro, 4) + ' |');
    });
    pu('');
    pu('Probabilidade acumulada de completar a escada: iniciante = ' +
      U.pct(la.cum.novice[la.rows.length - 1], 4) + ', médio = ' + U.pct(la.cum.mid[la.rows.length - 1], 4) +
      ', treinado = ' + U.pct(la.cum.pro[la.rows.length - 1], 4) + '.');
    pu('');
    pu('A coluna "erro" compara a janela analítica `T = L_efetivo / |v_rel|` com a janela medida ' +
      'numericamente (varrendo o instante de soltura e verificando o pouso). Divergência grande ' +
      'indica que a velocidade relativa varia dentro da própria janela — a fórmula de primeira ordem ' +
      'perde validade.');
    pu('');

    // ---- curva de aprendizado ----
    pu('## 6. Curva de aprendizado');
    pu('');
    pu('Taxa de vitória da escada em função do desvio-padrão de timing do jogador.');
    pu('');
    pu('| sigma (ms) | P(vitória da escada) | p rodada 1 | p última rodada |');
    pu('|---:|---:|---:|---:|');
    lc.forEach(function (r) {
      pu('| ' + r.sigmaMs + ' | ' + U.pct(r.win, 4) + ' | ' + U.fmt(r.perRound[0], 4) + ' | ' +
        U.fmt(r.perRound[r.perRound.length - 1], 4) + ' |');
    });
    pu('');
    var lo = lc[0], hi = lc[lc.length - 1];
    pu('Reduzir o desvio de timing de ' + lo.sigmaMs + ' ms para ' + hi.sigmaMs + ' ms multiplica a ' +
      'probabilidade de vitória por ' + (lo.win > 0 ? U.fmt(hi.win / lo.win, 1) : '∞') +
      '. A curva é monotônica: **treino melhora desempenho**, que é a condição para a máquina ser ' +
      'classificada como de habilidade.');
    pu('');

    // ---- monte carlo ----
    pu('## 7. Monte Carlo');
    pu('');
    if (!mc) {
      pu('_Não executado nesta sessão. Rode a aba Monte Carlo antes de emitir o relatório final._');
    } else {
      pu('N = **' + mc.N + ' partidas por perfil**, semente = ' + mc.seed +
        ', jitter da máquina ' + (mc.machineJitter ? 'INCLUÍDO' : 'excluído') +
        ', estratégia = ' + mc.strategy + '.');
      pu('');
      pu('| perfil | sigma (ms) | rodadas médias | escada completa (MC) | escada completa (analítico) | divergência |');
      pu('|---|---:|---:|---:|---:|---:|');
      M.profiles().forEach(function (p) {
        var a = mc.byProfile[p.id], an = la.cum[p.id][la.rows.length - 1];
        pu('| ' + a.label + ' | ' + U.fmt(a.sigmaMs, 1) + ' | ' + U.fmt(a.meanRounds, 2) + ' | ' +
          U.pct(a.winAll, 4) + ' | ' + U.pct(an, 4) + ' | ' +
          U.fmt(Math.abs(a.winAll - an), 5) + ' |');
      });
      pu('');
      pu('| perfil | rodada | taxa de acerto condicional | alcance | conclusão acumulada |');
      pu('|---|---:|---:|---:|---:|');
      M.profiles().forEach(function (p) {
        var a = mc.byProfile[p.id], i;
        for (i = 0; i < mc.rounds; i++) {
          pu('| ' + a.label + ' | ' + (i + 1) + ' | ' + U.pct(a.hitRate[i], 2) + ' | ' +
            U.pct(a.reachRate[i], 2) + ' | ' + U.pct(a.clearRate[i], 3) + ' |');
        }
      });
      pu('');
      pu('A divergência entre Monte Carlo e o cálculo analítico é o teste de consistência dos dois ' +
        'caminhos: a fórmula com erf e a simulação partida a partida devem convergir dentro do erro ' +
        'estatístico de 1/raiz(N) ≈ ' + U.fmt(1 / Math.sqrt(mc.N), 4) + '. As duas contas usam a mesma ' +
        'ponderação das oportunidades (a chance de cair numa janela é proporcional ao intervalo que a ' +
        'precede, não 1/N); divergência sistemática acima do erro estatístico indicaria inconsistência ' +
        'de modelo, não ruído de amostragem.');
    }
    pu('');

    // ---- operacao ----
    pu('## 8. Métricas operacionais');
    pu('');
    pu('| grandeza | valor |');
    pu('|---|---:|');
    pu('| Distância percorrida pela correia — eixo A | ' + U.fmt(op.beltAperHour, 1) + ' m/h |');
    pu('| Distância percorrida pela correia — eixo B | ' + U.fmt(op.beltBperHour, 1) + ' m/h |');
    pu('| Distância total | ' + U.fmt(op.beltMperHour, 1) + ' m/h |');
    pu('| Ciclos de inversão — eixo A | ' + U.fmt(op.revAperHour, 0) + ' /h |');
    pu('| Ciclos de inversão — eixo B | ' + U.fmt(op.revBperHour, 0) + ' /h |');
    pu('| Potência mecânica estimada (2 eixos, com rendimento) | ' + U.fmt(op.pMech, 1) + ' W |');
    pu('| Potência total estimada | ' + U.fmt(op.pTotal, 1) + ' W |');
    pu('| Tempo de attract entre partidas | ' + U.fmt(op.attract, 0) + ' s |');
    pu('| Vazão estimada (perfil médio) | ' + U.fmt(op.throughputPerHour, 1) + ' partidas/h |');
    pu('');
    pu('| perfil | rodadas médias | duração média da partida (s) | energia por partida (Wh) | custo de energia (R$) |');
    pu('|---|---:|---:|---:|---:|');
    M.profiles().forEach(function (p) {
      var d = op.durations[p.id];
      pu('| ' + p.label + ' | ' + U.fmt(d.rounds, 2) + ' | ' + U.fmt(d.seconds, 1) + ' | ' +
        U.fmt(d.energyWh, 3) + ' | ' + U.fmt(d.cost, 4) + ' |');
    });
    pu('');
    pu('Distância e inversões são o insumo direto para vida útil: uma correia GT2 típica e os ' +
      'rolamentos do carro devem ser especificados contra esses números, não contra o tempo de ' +
      'operação em horas.');
    pu('');

    // ---- economia ----
    pu('## 9. Economia');
    pu('');
    pu('Preço da jogada: R$ ' + U.fmt(eco.price, 2) + ' · Jogadas/dia: ' + eco.plays +
      ' · Teto configurado: ' + U.pct(eco.cap, 0) + ' da receita (medido no perfil TREINADO).');
    pu('');
    pu('| prêmio | nível | custo (R$) | P(liberar) iniciante | P médio | P treinado | custo esperado treinado (R$) |');
    pu('|---|---:|---:|---:|---:|---:|---:|');
    eco.prizes.forEach(function (e) {
      pu('| ' + U.escMd(e.name) + ' | ' + e.level + ' | ' + U.fmt(e.cost, 2) + ' | ' + U.pct(e.p.novice, 4) +
        ' | ' + U.pct(e.p.mid, 4) + ' | ' + U.pct(e.p.pro, 4) + ' | ' + U.fmt(e.expected.pro, 4) + ' |');
    });
    pu('');
    pu('| perfil | custo esperado de prêmio (R$/jogada) | % da receita | margem (R$/jogada) |');
    pu('|---|---:|---:|---:|');
    M.profiles().forEach(function (p) {
      var b = eco.byProfile[p.id];
      pu('| ' + b.label + ' | ' + U.fmt(b.expectedPrizeCost, 4) + ' | ' + U.pct(b.costPctOfRevenue, 2) +
        ' | ' + U.fmt(b.margin, 4) + ' |');
    });
    pu('');
    pu('Mix de público adotado: iniciante ' + U.pct(eco.mix.novice, 0) + ', médio ' + U.pct(eco.mix.mid, 0) +
      ', treinado ' + U.pct(eco.mix.pro, 0) + '. Receita esperada por dia: R$ ' + U.fmt(eco.revenueDay, 2) +
      '; custo de prêmio no mix: R$ ' + U.fmt(eco.prizeCostDayBlended, 2) + '; margem: R$ ' +
      U.fmt(eco.marginDayBlended, 2) + '.');
    pu('');
    pu((eco.alert ? '**ALERTA.** ' : '') + eco.alertText);
    if (eco.alert) pu('');
    if (eco.alert) pu('Preço mínimo para respeitar o teto no perfil treinado: R$ ' + U.fmt(eco.minPrice, 2) + ' por jogada.');
    pu('');
    pu('O dimensionamento é feito pelo perfil treinado porque é ele quem repete a jogada. ' +
      'Um custo aceitável no jogador médio e inviável no treinado significa que a máquina é ' +
      'sustentável só enquanto ninguém aprende a jogá-la.');
    pu('');

    // ---- catalogo ----
    pu('## 10. Componentes selecionados');
    pu('');
    pu('| categoria | opção selecionada | jitter/erro típico | custo aprox. (R$) |');
    pu('|---|---|---|---:|');
    PB.catalog.CATALOG.forEach(function (cat) {
      var o = cat.options[PB.catalog.selected(cat.id)];
      pu('| ' + cat.label + ' | ' + U.escMd(o.name) + ' | ' + o.jitter + ' | ' + U.fmt(o.cost, 2) + ' |');
    });
    pu('');
    pu('Jitter total da cadeia input→soltura: ' + U.fmt(w0.sigT * 1000, 3) + ' ms (1 sigma). ' +
      'Latência média input→soltura: ' + U.fmt(w0.latMean * 1000, 2) + ' ms.');
    pu('');

    // ---- numerica ----
    pu('## 11. Verificação numérica');
    pu('');
    pu('| verificação | valor | tolerância |');
    pu('|---|---:|---:|');
    pu('| Erro da tabela de voo na posição de pouso | ' + U.fmt(w0.ft.interpErrMm, 5) + ' mm | < 0,01 mm |');
    pu('| Erro da tabela de voo no tempo de queda | ' + U.fmt(w0.ft.interpErrS * 1e6, 3) + ' µs | < 50 µs |');
    pu('| RK4 sem arrasto vs. solução analítica (tempo) | ' + U.fmt(Math.abs(drag.tNoDrag - drag.tAnalytic) * 1e6, 3) + ' µs | < 10 µs |');
    pu('| Passo de integração | ' + U.fmt(P.num('sim.dt'), 3) + ' ms | — |');
    pu('| Precisão da função erf (série de termos positivos) | ~1e-15 | — |');
    pu('');

    // ---- limitacoes ----
    pu('## 12. Limitações');
    pu('');
    var est = P.estimated();
    pu('Os resultados deste relatório dependem de medição em bancada. ' + est.length +
      ' parâmetros permanecem marcados como **estimados** e nenhuma conclusão quantitativa acima ' +
      'deve ser tratada como verificada enquanto eles não forem medidos no equipamento real:');
    pu('');
    pu('| grupo | parâmetro | valor estimado | unidade |');
    pu('|---|---|---:|---|');
    est.forEach(function (d) {
      var v = P.get(d.k);
      pu('| ' + d.g + ' | ' + d.l + ' | ' + (typeof v === 'number' ? U.fmt(v, 5) : U.escMd(v)) + ' | ' + d.u + ' |');
    });
    pu('');
    pu('Limitações de modelo, além dos parâmetros:');
    pu('');
    pu('- O erro de timing do jogador é modelado como gaussiano de média zero (mais um viés opcional). ' +
      'Erro humano real tem cauda pesada e assimetria; a probabilidade calculada tende a ser otimista nas rodadas difíceis.');
    pu('- O coeficiente de arrasto Cd é tratado como constante; ele varia com Reynolds e com a rugosidade da bola.');
    pu('- O coeficiente de sustentação de Magnus usa aproximação linear no parâmetro de spin, válida só em ordem de grandeza.');
    pu('- O ricochete na borda não é integrado: por regra de conformidade, tocar a borda já conta como execução válida, e o destino da bola depois disso não altera o resultado.');
    pu('- A potência mecânica supõe zero regeneração e atrito desprezível fora do rendimento global.');
    pu('- Os perfis de jogador (sigma de timing) são estimativas de literatura, não medição com sujeitos reais nesta máquina.');
    pu('- A escada supõe que o jogador escolhe a oportunidade segundo a estratégia "' + P.get('ply.select') +
      '"; um jogador que aprende a esperar a janela mais larga tem desempenho superior ao tabulado quando a estratégia usada é a "próxima oportunidade".');
    pu('');
    pu('---');
    pu('Relatório gerado por PICBOX — simulador de engenharia, versão ' + P.VERSION +
      ', hash do conjunto `' + P.hash() + '`.');
    return L.join('\n');
  }

  PB.report = {
    markdown: markdown, csvParams: csvParams, csvRounds: csvRounds,
    csvLearning: csvLearning, csvMC: csvMC, csvSweep: csvSweep, FORMULAS: FORMULAS
  };
})(window.PB);
