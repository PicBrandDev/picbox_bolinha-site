"""Gera VERIFICACAO.md, FILA_IMPRESSAO.md e BOM_FIXACAO.md da Maquina A a partir dos relatorios JSON.
Uso: python ferramentas/relatorio.py"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from maquina_a import montagem as MT  # noqa: E402

BASE = Path(__file__).resolve().parents[1] / "docs"
REL = Path(__file__).resolve().parents[1] / "saidas" / "relatorios"
CHK = ["1_brep", "2_stl", "3_mesa", "4_intencao", "5_parede", "6_overhang", "7_interferencia", "8_movimento",
       "9_furos", "10_bola", "11_visual", "12_fatiamento", "13_montagem"]
IMPRESSORAS = ["260", "220 #1", "220 #2"]


def relatorios():
    out = []
    for pid in MT.PECAS:
        mod = MT.modulo(pid)
        for v in MT.variantes(mod):
            nome = MT.nome_arquivo(pid, v)
            f = REL / f"{nome}.json"
            if f.exists():
                out.append((mod, v, nome, json.loads(f.read_text(encoding="utf8"))))
    return out


def st(c):
    return "—" if c is None else ("ok" if c.get("ok") else ("ver" if c.get("ok") is None else "FALHOU"))


def main():
    rs = relatorios()
    # VERIFICACAO
    L = ["# Maquina A — verificacao (Fase 4)", "", "Gerado por `ferramentas/relatorio.py` a partir de `saidas/relatorios/*.json`.",
         "Checagem 11 (visual): avaliada abrindo as imagens em `saidas/imagens/pecas/` (ver CHANGELOG).", "",
         "| Peca | " + " | ".join(c.split("_", 1)[0] for c in CHK) + " | Resultado |",
         "|---|" + "---|" * (len(CHK) + 1)]
    for mod, v, nome, r in rs:
        L.append(f"| {nome} | " + " | ".join(st(r.get(c)) for c in CHK) + f" | {'APROVADA' if r['aprovada'] else 'REPROVADA'} |")
    L += ["", "## Detalhes que importam", ""]
    for mod, v, nome, r in rs:
        m = r.get("8_movimento", {})
        extra = []
        if m.get("menor"):
            extra.append(f"menor folga em movimento {m['menor'][1]} mm ({m['menor'][0]}, carro em {m['menor'][2]})")
        if m.get("fim_de_curso"):
            extra.append("FC tocado em " + ", ".join(f"{k}: {vv['toque_em']}" for k, vv in m["fim_de_curso"].items() if k != "ok"))
        b = r.get("10_bola", {})
        if "folga_radial_queda" in b:
            extra.append(f"bola: folga radial na queda {b['folga_radial_queda']} mm, bola rolando sob a garganta {b['folga_bola_rolando_mm']} mm")
        if "queda_aberta" in b:
            extra.append(f"bola: entra rolando e cai com as portinholas abertas sem tocar (curso do pino {b['curso_pino_mm']} mm)")
        p = r["5_parede"]
        extra.append(f"parede p1 {p['percentil1_mm']} mm (min {p['minimo']})")
        o = r["6_overhang"]
        extra.append(f"overhang {o['area_overhang_mm2']} mm2, ponte max {o['ponte_max_mm']} mm")
        if r["4_intencao"].get("justificativa"):
            extra.append(f"Δ intencao {r['4_intencao'].get('delta_abs_max', '-')} mm: {r['4_intencao']['justificativa']}")
        L.append(f"- **{nome}**: " + "; ".join(extra))
    (BASE / "VERIFICACAO.md").write_text("\n".join(L) + "\n", encoding="utf8")

    # FILA (P1): a mais longa primeiro, distribuida na impressora mais livre
    itens = []
    for mod, v, nome, r in rs:
        q = mod.QTD[v]
        for k in range(q):
            itens.append((r["12_fatiamento"]["horas"], r["12_fatiamento"]["gramas"], nome + (f" ({k + 1}/{q})" if q > 1 else "")))
    itens.sort(reverse=True)
    carga = {i: 0.0 for i in IMPRESSORAS}
    fila = {i: [] for i in IMPRESSORAS}
    for h, g, nome in itens:
        i = min(carga, key=carga.get)
        fila[i].append((nome, h, g))
        carga[i] += h
    total_h = sum(h for h, _, _ in itens)
    total_g = sum(g for _, g, _ in itens)
    F = ["# Maquina A — fila de impressao (P1)", "",
         f"Total: **{total_h:.1f} h** de impressora e **{total_g:.0f} g** de PETG em {len(itens)} pecas. "
         f"Com as 3 impressoras em paralelo: **{max(carga.values()):.1f} h** de relogio.",
         "Horas disponiveis: sem limite (usuario). Tempo/massa estimados por volume (sem slicer CLI); conferir no slicer.",
         "Todas as pecas cabem na mesa 220 x 220 x 250.", ""]
    for i in IMPRESSORAS:
        F += [f"## Impressora {i} — {carga[i]:.1f} h", "", "| # | Peca | Tempo (h) | Massa (g) |", "|---|---|---|---|"]
        F += [f"| {k + 1} | {n} | {h:.1f} | {g:.0f} |" for k, (n, h, g) in enumerate(fila[i])]
        F.append("")
    F += ["Pecas pequenas iguais (presilhas, garfo) podem ir juntas numa placa so.", ""]
    (BASE / "FILA_IMPRESSAO.md").write_text("\n".join(F), encoding="utf8")

    # BOM de fixacao
    c = Counter()
    por_peca = []
    for mod, v, nome, r in rs:
        q = mod.QTD[v]
        linhas = Counter()
        for f in r.get("fixadores", []):
            chave = f"{f['tipo']} {f['bitola']}x{f['comp']}"
            linhas[(chave, f.get("extra", ""))] += 1
            c[chave] += q
        if linhas:
            por_peca.append((nome, q, linhas))
    porcas = Counter()
    for chave, n in c.items():
        b = chave.split()[1].split("x")[0]
        porcas[b] += n
    B = ["# Maquina A — BOM de fixacao (P1)", "", "| Fixador | Qtd por maquina |", "|---|---|"]
    B += [f"| {k} | {n} |" for k, n in sorted(c.items())]
    B += ["", "Porcas (sextavadas comuns, 1 por parafuso salvo indicacao na peca): " +
          ", ".join(f"{b}: ~{n}" for b, n in sorted(porcas.items())) + ".",
          "Especiais: porca-garra M4 (4 por bloco de ponta = 16, cravada por fora da lateral); "
          "porca martelo M5 (2 por bloco = 8); porca M5 autotravante (2); arruela M5 (4); pino M2x12 (1, garfo).", "",
          "## Por peca", ""]
    for nome, q, linhas in por_peca:
        B.append(f"- **{nome}** (x{q}): " + "; ".join(f"{n}x {k}" + (f" — {e}" if e else "") for (k, e), n in linhas.items()))
    (BASE / "BOM_FIXACAO.md").write_text("\n".join(B) + "\n", encoding="utf8")
    print("ok:", len(rs), "relatorios;", f"{total_h:.1f} h total")


if __name__ == "__main__":
    main()
