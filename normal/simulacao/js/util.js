/* PICBOX — utilitários numéricos, RNG determinístico, hash, formatação, export */
window.PB = window.PB || {};
(function (PB) {
  'use strict';

  // ---------- polifills ----------
  // A sintaxe deste projeto e toda ES5. So estas tres funcoes de biblioteca sao
  // mais novas; com elas cobertas, a ferramenta abre em qualquer navegador que
  // tenha canvas, inclusive maquina velha de operacao.
  if (!Object.assign) {
    Object.assign = function (t) {
      var i, k, src;
      for (i = 1; i < arguments.length; i++) {
        src = arguments[i]; if (!src) continue;
        for (k in src) if (Object.prototype.hasOwnProperty.call(src, k)) t[k] = src[k];
      }
      return t;
    };
  }
  if (!Array.prototype.fill) {
    Array.prototype.fill = function (v) {
      for (var i = 0; i < this.length; i++) this[i] = v;
      return this;
    };
  }
  if (!Math.hypot) {
    Math.hypot = function (a, b) { return Math.sqrt(a * a + b * b); };
  }

  // ---------- escape ----------
  // Nome de premio e modelo de motor sao digitados pelo usuario e entram em
  // innerHTML e em tabelas Markdown: sem escapar, um '<b>' quebra o layout da
  // tabela e um '|' quebra a tabela do relatorio.
  var ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  function esc(v) {
    return String(v === null || v === undefined ? '' : v).replace(/[&<>"']/g, function (c) { return ESC[c]; });
  }
  function escMd(v) {
    return String(v === null || v === undefined ? '' : v).replace(/\|/g, '\\|').replace(/[\r\n]+/g, ' ');
  }

  // ---------- erf ----------
  // Serie de termos POSITIVOS (sem cancelamento catastrofico):
  //   erf(x) = (2x/raiz(pi)) * e^(-x^2) * SOMA_n (2x^2)^n / (1*3*5*...*(2n+1))
  // Precisao ~1e-15 (limitada pelo epsilon do double), contra 1,5e-7 da
  // aproximacao racional de Abramowitz-Stegun. Acima de |x| = 6 o valor e 1
  // ate o ultimo bit do double (1 - erf(6) = 2,2e-17).
  var TWO_OVER_SQRT_PI = 2 / Math.sqrt(Math.PI);
  function erf(x) {
    if (x === 0) return 0;
    var s = x < 0 ? -1 : 1; x = Math.abs(x);
    if (x > 6) return s;
    var x2 = x * x, term = 1, sum = 1, n = 0;
    while (n < 400) {
      term *= 2 * x2 / (2 * n + 3);
      sum += term;
      if (term < sum * 1e-17) break;
      n++;
    }
    return s * TWO_OVER_SQRT_PI * x * Math.exp(-x2) * sum;
  }
  function erfinv(y) { // Newton sobre erf, para varreduras inversas
    if (y <= -1) return -Infinity; if (y >= 1) return Infinity;
    var x = 0, i;
    for (i = 0; i < 60; i++) {
      var e = erf(x) - y;
      var d = 2 / Math.sqrt(Math.PI) * Math.exp(-x * x);
      if (Math.abs(d) < 1e-14) break;
      var nx = x - e / d;
      if (!isFinite(nx)) break;
      if (Math.abs(nx - x) < 1e-12) { x = nx; break; }
      x = nx;
    }
    return x;
  }

  // ---------- RNG determinístico (mulberry32) ----------
  function rng(seed) {
    var a = (seed >>> 0) || 1;
    var f = function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    f.normal = function (mu, sigma) { // Box-Muller
      var u = 0, v = 0;
      while (u === 0) u = f();
      while (v === 0) v = f();
      return (mu || 0) + (sigma || 1) * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    };
    return f;
  }

  // ---------- hash FNV-1a 32 bits ----------
  function hash32(str) {
    var h = 0x811c9dc5, i;
    for (i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193); }
    return ('00000000' + (h >>> 0).toString(16)).slice(-8);
  }

  // ---------- formatação ----------
  function fmt(v, d) {
    if (v === null || v === undefined || (typeof v === 'number' && !isFinite(v))) return '—';
    if (typeof v !== 'number') return String(v);
    d = (d === undefined) ? 3 : d;
    if (v !== 0 && (Math.abs(v) < 1e-3 || Math.abs(v) >= 1e6)) return v.toExponential(Math.max(1, d - 1)).replace('.', ',');
    return v.toFixed(d).replace('.', ',');
  }
  function pct(v, d) { return fmt(100 * v, d === undefined ? 2 : d) + ' %'; }
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function frac(x) { return x - Math.floor(x); }

  // ---------- CSV ----------
  function csvCell(v) {
    var s = (v === null || v === undefined) ? '' : String(v);
    if (/[";\n]/.test(s)) s = '"' + s.replace(/"/g, '""') + '"';
    return s;
  }
  function toCSV(rows, sep) {
    sep = sep || ';';
    return rows.map(function (r) { return r.map(csvCell).join(sep); }).join('\n');
  }
  function parseCSV(text, sep) {
    sep = sep || ';';
    var out = [], lines = text.replace(/\r/g, '').split('\n'), i;
    for (i = 0; i < lines.length; i++) {
      var line = lines[i];
      if (line === '') continue;
      var row = [], cur = '', q = false, j;
      for (j = 0; j < line.length; j++) {
        var c = line[j];
        if (q) {
          if (c === '"' && line[j + 1] === '"') { cur += '"'; j++; }
          else if (c === '"') q = false;
          else cur += c;
        } else if (c === '"') q = true;
        else if (c === sep) { row.push(cur); cur = ''; }
        else cur += c;
      }
      row.push(cur); out.push(row);
    }
    return out;
  }

  // ---------- download (com fallback para file://) ----------
  function download(filename, text, mime) {
    try {
      var blob = new Blob([text], { type: (mime || 'text/plain') + ';charset=utf-8' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url; a.download = filename; a.style.display = 'none';
      document.body.appendChild(a); a.click();
      setTimeout(function () { document.body.removeChild(a); URL.revokeObjectURL(url); }, 1500);
      PB.ui && PB.ui.toast && PB.ui.toast('Arquivo gerado: ' + filename);
    } catch (e) {
      showText(filename, text);
    }
  }
  function showText(title, text) {
    var ov = document.getElementById('textOverlay');
    document.getElementById('textOverlayTitle').textContent = title;
    var ta = document.getElementById('textOverlayBody');
    ta.value = text; ov.classList.add('open'); ta.focus(); ta.select();
  }
  function legacyCopy(text) {
    try {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select(); document.execCommand('copy');
      document.body.removeChild(ta); return true;
    } catch (e) { return false; }
  }
  function copyText(text) {
    // navigator.clipboard existe mas REJEITA fora de contexto seguro. A promessa
    // rejeitada tem que cair no metodo antigo, senao o usuario acha que copiou.
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text)['catch'](function () { legacyCopy(text); });
        return true;
      }
    } catch (e) { }
    return legacyCopy(text);
  }

  function nowStamp() {
    var d = new Date(), p = function (n, w) { return ('0000' + n).slice(-(w || 2)); };
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' +
      p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
  }
  function fileStamp() { return nowStamp().replace(/[: ]/g, '-'); }

  // ---------- DOM helpers ----------
  function el(tag, attrs, kids) {
    var e = document.createElement(tag), k;
    if (attrs) for (k in attrs) {
      if (k === 'class') e.className = attrs[k];
      else if (k === 'html') e.innerHTML = attrs[k];
      else if (k === 'text') e.textContent = attrs[k];
      else if (k.slice(0, 2) === 'on') e.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== null && attrs[k] !== undefined) e.setAttribute(k, attrs[k]);
    }
    if (kids) kids.forEach(function (c) { if (c) e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return e;
  }
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function table(headers, rows, cls) {
    var t = el('table', { class: 'tbl ' + (cls || '') });
    var thead = el('thead'), tr = el('tr');
    headers.forEach(function (h) { tr.appendChild(el('th', { html: h })); });
    thead.appendChild(tr); t.appendChild(thead);
    var tb = el('tbody');
    rows.forEach(function (r) {
      var trr = el('tr');
      if (r.__cls) trr.className = r.__cls;
      (r.__cells || r).forEach(function (c) {
        if (c && typeof c === 'object' && c.html !== undefined) trr.appendChild(el('td', { html: c.html, class: c.cls || '' }));
        else trr.appendChild(el('td', { html: String(c) }));
      });
      tb.appendChild(trr);
    });
    t.appendChild(tb);
    return t;
  }

  PB.util = {
    erf: erf, erfinv: erfinv, rng: rng, hash32: hash32, fmt: fmt, pct: pct,
    clamp: clamp, lerp: lerp, frac: frac,
    toCSV: toCSV, parseCSV: parseCSV, csvCell: csvCell, esc: esc, escMd: escMd,
    download: download, showText: showText, copyText: copyText,
    nowStamp: nowStamp, fileStamp: fileStamp,
    el: el, $: $, $$: $$, table: table
  };
})(window.PB);
